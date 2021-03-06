# This file contains logic for managing known free space in the game's
# memory layout.

from util import fatal_error

# We'll just handle one chunk of free space for now.
sector_0 = {
    "address": 0x80530000,
    "size": 0x20000,
}

POINTER_TYPE_NORMAL = "normal"
POINTER_TYPE_TEXT_TABLE = "text_table"

def init():
    """
    Gets an initial free space object.
    """
    # sector contains info about the destination for in-game memory.
    # allocs is an array of allocated data of shape:
    #    {
    #        "offset": int,
    #        "pointer": int,
    #        "pointer_type": string,
    #        "data": byte[],
    #    }
    return {
        "sector": sector_0,
        "allocs": [],
    }


def alloc(space, data, pointer, pointer_type=POINTER_TYPE_NORMAL):
    """
    Allocates the given data array to known free space. We don't free
    data from this space, so data can be alloc'd contiguously.
    """
    if len(space["allocs"]) == 0:
        offset = 0
    else:
        last_alloc = space["allocs"][-1]
        offset = last_alloc["offset"] + len(last_alloc["data"])

    if offset + len(data) > space["sector"]["size"]:
        fatal_error("Failed to allocate %s bytes of data to free space." % len(data))

    space["allocs"].append({
        "address": space["sector"]["address"] + offset,
        "offset": offset,
        "pointer": pointer,
        "pointer_type": pointer_type,
        "data": data,
    })

    return space
