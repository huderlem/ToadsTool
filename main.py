import argparse
import csv
import json
import os
import shutil
import struct
import sys

import compression
import tt_config
import files
import freespace
from util import *


def setup_dol(input_dir, work_dir):
    """
    Extracts the main .dol file into the working directory.
    """
    original_filepath = files.get_original_filepath(tt_config.dol_file)
    input_filepath = os.path.join(input_dir, original_filepath)
    work_filepath = os.path.join(work_dir, tt_config.dol_file)
    os.makedirs(os.path.dirname(work_filepath), exist_ok=True)
    shutil.copy(input_filepath, work_filepath)
    print_info("Setup '%s'" % work_filepath)


def stage_dol(work_dir, stage_dir, free_space):
    """
    Injects modifications into the game's free space by adding
    custom Data section(s) into the .dol file.
    """
    # We won't get too clever for now, so we'll make some assumptions
    # about the .dol--namely, that it's a vanilla .dol from MGTT.

    # Read the existing .dol file contents.
    work_filepath = os.path.join(work_dir, tt_config.dol_file)
    with open(work_filepath, mode="rb") as f:
        dol = bytearray(f.read())

    # Append the injected data to the end of the .dol file.
    # Calculate the total size of the injected data along the way.
    data_size = 0
    for alloc in free_space["allocs"]:
        data_size += len(alloc["data"])
        dol.extend(alloc["data"])

    # Write the DOL header attributes for the new data section that
    # we just appended to the file.
    struct.pack_into(">I", dol, 0x20, 0x15E7C0) # address in .dol
    struct.pack_into(">I", dol, 0x68, free_space["sector"]["address"]) # in-game memory address
    struct.pack_into(">I", dol, 0xB0, data_size) # section size

    # Update the pointers in the .dol to the injected data so the game
    # knows to look for our injected data, rather than the original data.
    for alloc in free_space["allocs"]:
        pointer_type = alloc["pointer_type"]
        if pointer_type == freespace.POINTER_TYPE_TEXT_TABLE:
            # 0x801431CC is the start of the in-memory string table. The string table
            # first lists the offsets of all string ids from the start of
            # this table. For example, if an entry is the value 0x100, then
            # the contents of the string lives at 0x801431CC + 0x100.
            text_offset = (alloc["address"]) - 0x801431CC
            struct.pack_into(">i", dol, alloc["pointer"], text_offset)
        else:
            fatal_error("Unhandled free-space pointer type '%s'" % pointer_type)

    # Write the .dol file to the staging directory.
    original_filepath = files.get_original_filepath(tt_config.dol_file)
    stage_filepath = os.path.join(stage_dir, original_filepath)
    os.makedirs(os.path.dirname(stage_filepath), exist_ok=True)
    with open(stage_filepath, "wb") as f:
        f.write(dol)

    print_info("Staged '%s' as '%s'" % (work_filepath, stage_filepath))


def setup_overlays(input_dir, work_dir):
    """
    Extracts the code overlay files into the working directory.
    Also extracts any relevant data that resides in the overlay files.
    """
    for overlay in tt_config.overlay_files:
        original_filepath = files.get_original_filepath(overlay)
        input_filepath = os.path.join(input_dir, original_filepath)
        work_filepath = os.path.join(work_dir, overlay)
        os.makedirs(os.path.dirname(work_filepath), exist_ok=True)
        with open(input_filepath, "rb") as f:
            decompressed_overlay = compression.decompress(bytearray(f.read()))
        with open(work_filepath, "wb") as f:
            f.write(decompressed_overlay)

        print_info("Setup '%s'" % work_filepath)

    # Extract the character stats into JSON files.
    overlay_work_filepath = os.path.join(work_dir, tt_config.character_stats["golf_overlay_file"]["overlay_file"])
    with open(overlay_work_filepath, "rb") as f:
        data = f.read()

    base_offset = tt_config.character_stats["golf_overlay_file"]["offset"]
    id_order = tt_config.character_stats["character_id_stats_order"]
    character_stats = []
    for i in range(len(id_order)):
        character_id = id_order[i]
        offset = base_offset + i * 0x1C
        stats = {}
        stats["_label"] = tt_config.character_stats["character_labels"][character_id]
        stats["drive_distance"] = struct.unpack_from(">I", data, offset)[0]
        stats["shot_loft"] = struct.unpack_from(">i", data, offset + 0x4)[0]
        if struct.unpack_from(">I", data, offset + 0x8)[0] == 0:
            stats["shot_curve_direction"] = "draw"
        else:
            stats["shot_curve_direction"] = "fade"
        stats["shot_curve_amount"] = struct.unpack_from(">I", data, offset + 0xC)[0]
        stats["impact"] = struct.unpack_from(">i", data, offset + 0x10)[0]
        stats["control"] = struct.unpack_from(">i", data, offset + 0x14)[0]
        stats["spin"] = struct.unpack_from(">i", data, offset + 0x18)[0]
        character_stats.append(stats)

    work_stats_filepath = os.path.join(work_dir, tt_config.character_stats["work_file"])
    os.makedirs(os.path.dirname(work_stats_filepath), exist_ok=True)
    with open(work_stats_filepath, "w") as f:
        json.dump(character_stats, f, indent=2)

    print_info("Setup '%s'" % work_stats_filepath)


def stage_overlays(work_dir, stage_dir):
    """
    Injects modifications into the game's overlay files.
    """
    # We will write the character stats data into the two overlay files that
    # contain the data.
    golf_overlay_file = tt_config.character_stats["golf_overlay_file"]["overlay_file"]
    golf_work_filepath = os.path.join(work_dir, golf_overlay_file)
    with open(golf_work_filepath, mode="rb") as f:
        golf_overlay = bytearray(f.read())

    menu_overlay_file = tt_config.character_stats["character_select"]["overlay_file"]
    menu_work_filepath = os.path.join(work_dir, menu_overlay_file)
    with open(menu_work_filepath, mode="rb") as f:
        menu_overlay = bytearray(f.read())

    work_stats_filepath = os.path.join(work_dir, tt_config.character_stats["work_file"])
    with open(work_stats_filepath) as f:
        character_stats = json.load(f)

    id_order = tt_config.character_stats["character_id_stats_order"]
    golf_base_offset = tt_config.character_stats["golf_overlay_file"]["offset"]
    menu_base_offset = tt_config.character_stats["character_select"]["offset"]
    for i, stats in enumerate(character_stats):
        character_id = id_order[i]
        # Write the golf overlay character stats data.
        offset = golf_base_offset + i * 0x1C
        struct.pack_into(">I", golf_overlay, offset, stats["drive_distance"])
        struct.pack_into(">i", golf_overlay, offset + 0x4, stats["shot_loft"])
        if stats["shot_curve_direction"] == "draw":
            struct.pack_into(">I", golf_overlay, offset + 0x8, 0x0)
        else:
            struct.pack_into(">I", golf_overlay, offset + 0x8, 0x1)
        struct.pack_into(">I", golf_overlay, offset + 0xC, stats["shot_curve_amount"])
        struct.pack_into(">i", golf_overlay, offset + 0x10, stats["impact"])
        struct.pack_into(">i", golf_overlay, offset + 0x14, stats["control"])
        struct.pack_into(">i", golf_overlay, offset + 0x18, stats["spin"])

        # Write the menu overlay character stats data.
        offset = menu_base_offset + i * 0xA
        struct.pack_into(">B", menu_overlay, offset, i)
        struct.pack_into(">B", menu_overlay, offset + 0x1, character_id)
        struct.pack_into(">H", menu_overlay, offset + 0x2, stats["drive_distance"])
        struct.pack_into(">b", menu_overlay, offset + 0x4, stats["shot_loft"])
        if stats["shot_curve_direction"] == "draw":
            struct.pack_into(">B", menu_overlay, offset + 0x5, 0)
        else:
            struct.pack_into(">B", menu_overlay, offset + 0x5, 1)
        struct.pack_into(">B", menu_overlay, offset + 0x6, stats["shot_curve_amount"])
        struct.pack_into(">b", menu_overlay, offset + 0x7, stats["impact"])
        struct.pack_into(">b", menu_overlay, offset + 0x8, stats["control"])
        struct.pack_into(">b", menu_overlay, offset + 0x9, stats["spin"])

    with open(golf_work_filepath, "wb") as f:
        f.write(golf_overlay)

    with open(menu_work_filepath, "wb") as f:
        f.write(menu_overlay)

    for overlay in tt_config.overlay_files:
        work_filepath = os.path.join(work_dir, overlay)
        original_filepath = files.get_original_filepath(overlay)
        stage_filepath = os.path.join(stage_dir, original_filepath)
        os.makedirs(os.path.dirname(stage_filepath), exist_ok=True)
        shutil.copy(work_filepath, stage_filepath)
        print_info("Staged '%s' as '%s'" % (work_filepath, stage_filepath))


def setup_ring_attack(input_dir, work_dir):
    """
    Extracts all the Ring Attack files into the working directory.
    They are transformed into JSON files for easier editing.
    """
    # Read the game .dol file contents.
    dol_filepath = os.path.join(work_dir, tt_config.dol_file)
    with open(dol_filepath, mode="rb") as f:
        dol = f.read()

    for hole in tt_config.ring_attack_holes:
        ring_attack_data = {
            "rings": [],
        }

        # Read the rings definition file.
        toadstool_filepath = hole["file"]
        original_filepath = files.get_original_filepath(toadstool_filepath)
        filepath = os.path.join(input_dir, original_filepath)
        with open(filepath, mode="rb") as f:
            data = f.read()

        # Parse the ring data from the file.
        num_rings = struct.unpack_from(">I", data, 0)[0]
        for i in range(num_rings):
            offset = (i * 7 * 4) + 4
            ring_attack_data["rings"].append({
                "x": struct.unpack_from(">f", data, offset)[0],
                "y": struct.unpack_from(">f", data, offset + 0x04)[0],
                "z": struct.unpack_from(">f", data, offset + 0x08)[0],
                "rotationX": struct.unpack_from(">f", data, offset + 0x0C)[0],
                "rotationY": struct.unpack_from(">f", data, offset + 0x10)[0],
                "scaleX": struct.unpack_from(">f", data, offset + 0x14)[0],
                "scaleY": struct.unpack_from(">f", data, offset + 0x18)[0],
            })

        # Read the hole's title.
        # 0x1401CC is the start of the string table. The string table
        # first lists the offsets of all string ids from the start of
        # this table. For example, if an entry is the value 0x100, then
        # the contents of the string lives at 0x1401CC + 0x100.
        offset = struct.unpack_from(">I", dol, hole["dolTitlePointer"])[0]
        title_address = 0x1401CC + offset
        ring_attack_data["title"] = read_c_ascii_string(dol, title_address)

        # Write the parsed ring definition file as JSON.
        work_filepath = os.path.join(work_dir, toadstool_filepath)
        os.makedirs(os.path.dirname(work_filepath), exist_ok=True)
        with open(work_filepath, "w") as f:
            json.dump(ring_attack_data, f, indent=2)

        print_info("Setup '%s'" % work_filepath)


def stage_ring_attack(work_dir, stage_dir, free_space):
    """
    Converts the Ring Attack files into their original file formats
    and saves them into the staging directory.
    """
    for hole in tt_config.ring_attack_holes:
        # Read the ring attack JSON file.
        toadstool_filepath = hole["file"]
        work_filepath = os.path.join(work_dir, toadstool_filepath)
        with open(work_filepath) as f:
            ring_attack_data = json.load(f)

        # Convert to the original binary data format.
        num_rings = len(ring_attack_data["rings"])
        file_length = 4 + num_rings * 0x1C
        data = bytearray(file_length)
        struct.pack_into(">I", data, 0, num_rings)
        for i, ring in enumerate(ring_attack_data["rings"]):
            offset = 4 + i * 0x1C
            struct.pack_into(">fffffff", data, offset,
                ring["x"],
                ring["y"],
                ring["z"],
                ring["rotationX"],
                ring["rotationY"],
                ring["scaleX"],
                ring["scaleY"])

        # Write the binary data file to the staging directory.
        original_filepath = files.get_original_filepath(toadstool_filepath)
        stage_filepath = os.path.join(stage_dir, original_filepath)
        os.makedirs(os.path.dirname(stage_filepath), exist_ok=True)
        with open(stage_filepath, "wb") as f:
            f.write(data)

        # Write the data to free space.
        title_string = to_c_ascii_string(ring_attack_data["title"])
        freespace.alloc(free_space, title_string, hole["dolTitlePointer"], pointer_type=freespace.POINTER_TYPE_TEXT_TABLE)

        print_info("Staged '%s' as '%s'" % (work_filepath, stage_filepath))


def command_setup(input_dir, work_dir):
    """
    Runs the ToadsTool 'setup' command.
    This setup a working directory and extract files from the game's
    filesystem. In some cases, the files will be transformed into
    a more friendly data format.
    """
    assert_dir_exists(input_dir)
    os.makedirs(work_dir, exist_ok=True)
    setup_dol(input_dir, work_dir)
    setup_overlays(input_dir, work_dir)
    setup_ring_attack(input_dir, work_dir)
    print_info("Setup successfully completed! Wahoo!")


def command_stage(work_dir, stage_dir):
    """
    Processes the working directory files into the game's original
    file formats and writes them to the staging directory.
    """
    assert_dir_exists(work_dir)
    os.makedirs(stage_dir, exist_ok=True)
    free_space = freespace.init()
    stage_ring_attack(work_dir, stage_dir, free_space)
    stage_overlays(work_dir, stage_dir)
    stage_dol(work_dir, stage_dir, free_space)
    print_info("Stage successfully completed! Wahoo!")


def command_apply(stage_dir, input_dir):
    """
    Copies files from the staging directory into the game's extracted
    filesystem. If a file is missing from the staging directory, it is
    silently ignored. Also applies compression to the file, if necessary.
    """
    assert_dirs_exist(stage_dir, input_dir)
    
    # Simply copy all the files we're aware of.
    for original_filepath in files.get_original_filepaths():
        stage_filepath = os.path.join(stage_dir, original_filepath)
        if not os.path.exists(stage_filepath):
            print(stage_filepath)
            # Silently ignore files that don't exist in the staging directory.
            continue

        output_filepath = os.path.join(input_dir, original_filepath)
        if files.is_compressed(original_filepath):
            print_info("Compressing '%s'" % stage_filepath)
            with open(stage_filepath, "rb") as f:
                compressed_data = compression.compress(bytearray(f.read()))
            with open(output_filepath, "wb") as f:
                f.write(compressed_data)
        else:
            shutil.copy(stage_filepath, output_filepath)

        print_info("Applied '%s' to '%s" % (stage_filepath, output_filepath))

    print_info("Apply successfully completed! Wahoo!")


def command_build(work_dir, stage_dir, input_dir):
    """
    Simply runs the "stage" command followed by the "apply" command.
    """
    assert_dirs_exist(work_dir, stage_dir, input_dir)
    command_stage(work_dir, stage_dir)
    command_apply(stage_dir, input_dir)
    print_info("Build successfully completed! Wahoo!")


if __name__ == "__main__":
    default_work_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "work")
    default_stage_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stage")

    argparser = argparse.ArgumentParser("ToadsTool - Mario Golf Toadstool Tour Editor")
    argparser.add_argument("command", help="The ToadsTool command to run ('setup', 'stage', 'apply', 'build')")
    argparser.add_argument("-i", "--input-dir", help="Directory of the MGTT ISO's extracted filesystem", required=True)
    argparser.add_argument("-w", "--work-dir", help="Working directory of the ToadsTool data files. Defaults to \"%s\"" % default_work_dir, default=default_work_dir)
    argparser.add_argument("-s", "--stage-dir", help="Staging directory of the ToadsTool data files. Defaults to \"%s\"" % default_stage_dir, default=default_stage_dir)
    args = argparser.parse_args()
    
    if args.command == "setup":
        command_setup(args.input_dir, args.work_dir)
    elif args.command == "stage":
        command_stage(args.work_dir, args.stage_dir)
    elif args.command == "apply":
        command_apply(args.stage_dir, args.input_dir)
    elif args.command == "build":
        command_build(args.work_dir, args.stage_dir, args.input_dir)
    else:
        fatal_error("Invalid command '%s'. Valid commands are 'setup', 'stage', 'apply', and 'build'." % args.command)
