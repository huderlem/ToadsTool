import argparse
import csv
import json
import os
import shutil
import struct
import sys

import tt_config
import files


quiet = False

def print_info(message):
    """
    Prints informational content to the console.
    """
    if not quiet:
        print(message)


def fatal_error(message):
    """
    Exits the program with the given error message.
    """
    sys.exit("ERROR: %s" % message)


def assert_dir_exists(directory):
    """
    Checks if the given directory exists. If it doesn't,
    then the program is terminated.
    """
    if not os.path.isdir(directory):
        fatal_error("Directory '%s' doesn't exist." % directory)


def assert_dirs_exist(*directories):
    """
    Checks if the given directories exist. If any doesn't,
    then the program is terminated.
    """
    for directory in directories:
        assert_dir_exists(directory)


def setup_ring_attack(input_dir, work_dir):
    """
    Extracts all the Ring Attack files into the working directory.
    They are transformed into JSON files for easier editing.
    """
    for toadstool_filepath in tt_config.ring_attack_files:
        ring_attack_data = {
            "rings": [],
        }

        # Read the rings definition file.
        original_filepath = files.get_original_filepath(toadstool_filepath)
        filepath = os.path.join(input_dir, original_filepath)
        with open(filepath, mode="rb") as f:
            data = f.read()

        # Parse the ring data from the file.
        num_rings = struct.unpack_from(">i", data, 0)[0]
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

        # Write the parsed ring definition file as JSON.
        work_filepath = os.path.join(work_dir, toadstool_filepath)
        os.makedirs(os.path.dirname(work_filepath), exist_ok=True)
        with open(work_filepath, "w") as f:
            json.dump(ring_attack_data, f, indent=2)

        print_info("Setup '%s'" % work_filepath)


def stage_ring_attack(work_dir, stage_dir):
    """
    Converts the Ring Attack files into their original file formats
    and saves them into the staging directory.
    """
    for toadstool_filepath in tt_config.ring_attack_files:
        # Read the ring attack JSON file.
        work_filepath = os.path.join(work_dir, toadstool_filepath)
        with open(work_filepath) as f:
            ring_attack_data = json.load(f)

        # Convert to the original binary data format.
        num_rings = len(ring_attack_data["rings"])
        file_length = 4 + num_rings * 0x1C
        data = bytearray(file_length)
        struct.pack_into(">i", data, 0, num_rings)
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
    setup_ring_attack(input_dir, work_dir)
    print_info("Setup successfully completed! Wahoo!")


def command_stage(work_dir, stage_dir):
    """
    Processes the working directory files into the game's original
    file formats and writes them to the staging directory.
    """
    assert_dir_exists(work_dir)
    os.makedirs(stage_dir, exist_ok=True)
    stage_ring_attack(work_dir, stage_dir)
    print_info("Stage successfully completed! Wahoo!")


def command_apply(stage_dir, input_dir):
    """
    Copies files from the staging directory into the game's extracted
    filesystem. If a file is missing from the staging directory, it is
    silently ignored.
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
    argparser.add_argument("-q", "--quiet", help="Don't print any output to the console", action='store_true', default=False)
    args = argparser.parse_args()

    if args.quiet:
        quiet = True
    
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
