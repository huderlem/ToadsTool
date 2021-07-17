# This file contains logic for compressing and decompressing binary
# game files. Mario Golf: Toadstool Tour uses a simple LZ-style
# compression method, where data is either copied direclty, or copied
# from a previous position from the decompression buffer.
#
# This file's compression and decompression functionality probably needs
# to be rewritten in C or C++ because the game's files are large enough
# that Python's slowness is getting in the way.  (One file can take
# 5-10 seconds to compress, for example.)

import struct

from util import fatal_error


def bits(b):
    """
    Returns a tuple of the individual bits in a byte, in order
    of most-significant to least-significant.
    """
    return ((b >> 7) & 1,
            (b >> 6) & 1,
            (b >> 5) & 1,
            (b >> 4) & 1,
            (b >> 3) & 1,
            (b >> 2) & 1,
            (b >> 1) & 1,
            (b) & 1)


def decompress(data):
    """
    Decompresses the given input bytearray.
    TODO: Add error handling.
    """
    # Skip the first 4 header bytes.
    index = 4

    def read_byte():
        nonlocal index
        b = data[index]
        index += 1
        return b

    output = bytearray()
    while True:
        command = read_byte()
        if command == 0:
            # Copy 8 immediate bytes.
            for i in range(8):
                output.append(read_byte())
        else:
            # Take different action depending on each bit in the command.
            for bit in bits(command):
                if bit == 0:
                    # Copy an immediate byte
                    output.append(read_byte())
                else:
                    # We will be copying a string of bytes from the previously-decompressed data.
                    p0 = read_byte()
                    p1 = read_byte()
                    if p0 == 0 and p1 == 0:
                        return output

                    # Calculate the offset in the decompression buffer, from which we
                    # will copy data.
                    offset = (p0 & 0xF0) * 0x10 + p1

                    copy_ctrl = p0 & 0xF
                    if copy_ctrl == 0:
                        # Copy at least 17 bytes
                        num_bytes = read_byte() + 17
                    else:
                        # Copy somewhere between 1 and 16 bytes.
                        num_bytes = copy_ctrl + 1

                    # Perform the copy from the previously-decompressed data.
                    for i in range(num_bytes):
                        output.append(output[-offset])

# LZ_WINDOW_SIZE can be freely tweaked to control
# the processing speed, with a compression quality tradeoff.
# A larger LZ_WINDOW_SIZE will result in better compression, but
# it will take longer to run.  LZ_WINDOW_SIZE has a maximum of 4096.
# I've found that LZ_WINDOW_SIZE=512 will result in slightly smaller
# file sizes than the original game's files.
LZ_WINDOW_SIZE = 128

# Don't tweak these values--they are constants baked into the
# game's decompression code.
LZ_PREFIX_MIN_LENGTH = 3
LZ_PREFIX_MAX_LENGTH = 272

def get_longest_prefix(data, cur_index):
    """
    Performs an LZ prefix search in a sliding window of the input data.
    """
    data_len = len(data)
    longest_prefix_index = cur_index
    longest_prefix_length = 0
    start_index = max(0, cur_index - LZ_WINDOW_SIZE)
    for start_index in range(max(0, cur_index - LZ_WINDOW_SIZE), cur_index):
        if data[start_index] == data[cur_index]:
            prefix_length = 1
            i = start_index + 1
            j = cur_index + 1
            while i < data_len and j < data_len and prefix_length < LZ_PREFIX_MAX_LENGTH and data[i] == data[j]:
                i += 1
                j += 1
                prefix_length += 1

            if prefix_length > longest_prefix_length:
                longest_prefix_length = prefix_length
                longest_prefix_index = start_index

    return longest_prefix_index, longest_prefix_length


def compress(data):
    """
    Compresses the given input bytearray.
    """
    data_len = len(data)
    if data_len > 0xFFFFFF:
        fatal_error("Data is too large (%s bytes) to compress! Must be <= 0xFFFFFF bytes" % hex(data_len))

    output = bytearray(4)
    struct.pack_into(">I", output, 0, data_len)
    # The uncompressed data length is only three bytes large, and we
    # overwrite the first byte in the header with the compression type
    output[0] = 0x2

    # Build up the list of LZ commands for copying immediate or pre-existing data.
    commands = []
    i = 0
    while i < data_len:
        longest_prefix_index, longest_prefix_length = get_longest_prefix(data, i)
        if longest_prefix_length > LZ_PREFIX_MIN_LENGTH:
            # Emit command for copying previous data.
            offset = i - longest_prefix_index
            commands.append({'type': 'prefix', 'offset': offset, 'length': longest_prefix_length})
            i += longest_prefix_length
        else:
            # Emit command for copying immediate data.
            commands.append({'type': 'copy', 'value': data[i]})
            i += 1

    # Add the terminating command.
    commands.append({'type': 'prefix', 'offset': 0, 'length': 1})

    # Build the raw compressed stream from the LZ commands.
    ctrl = 0x0
    ctrl_bit = 7
    buff = []
    for command in commands:
        if command['type'] == 'copy':
            buff.append(command['value'])
        else:
            ctrl |= (1 << ctrl_bit)
            p0 = ((command['offset'] >> 8) & 0xFF) << 4
            p1 = command['offset'] & 0xFF
            if command['length'] <= 16:
                p0 |= (command['length'] - 1)

            buff.append(p0)
            buff.append(p1)
            if command['length'] > 16:
                if command['length'] - 17 > 255:
                    fatal_error("Unexpected prefix length %s" % command['length'])
                buff.append(command['length'] - 17)

        ctrl_bit -= 1
        if ctrl_bit < 0:
            output.append(ctrl)
            output.extend(buff)
            ctrl = 0x0
            ctrl_bit = 7
            buff = []

    if ctrl_bit != 7:
        output.append(ctrl)
        output.extend(buff)

    # The original game always has 8 0xFF bytes at the end, for some reason.
    output.extend([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    return output
