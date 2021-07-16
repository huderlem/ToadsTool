# This file contains logic for compressing and decompressing binary
# game files. Mario Golf: Toadstool Tour uses a simple LZ-style
# compression method, where data is either copied direclty, or copied
# from a previous position from the decompression buffer.

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
    index = 0

    def read_byte():
        nonlocal index
        b = data[index]
        index += 1
        return b

    output = bytearray()
    while True:
        command = read_byte()
        # print("Command: %s" % hex(command))
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

                    ctrl = p0 & 0xF
                    if ctrl == 0:
                        # Copy at least 17 bytes
                        num_bytes = read_byte() + 17
                    else:
                        # Copy somewhere between 1 and 16 bytes.
                        num_bytes = ctrl + 1

                    # Perform the copy from the previously-decompressed data.
                    for i in range(num_bytes):
                        output.append(output[-offset])
