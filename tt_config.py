# This file contains generic settings for various aspects of data that
# ToadsTool covers.

dol_file = "core/main.dol"

# List of code overlay files. These files contain code and data, similar to DOL files, 
# but they are dynamically loaded into a static location in RAM during gameplay.
overlay_files = [
    "core/overlay_menu.bin",
    "core/overlay_golf.bin",
]

# Character golf stats file metadata.
character_stats = {
    "character_select": {
        "overlay_file": "core/overlay_menu.bin",
        "offset": 0x45b50,
    },
    "golf_overlay_file": {
        "overlay_file": "core/overlay_golf.bin",
        "offset": 0xd2980,
    },
    "work_file": "characters/stats.json",
    "character_labels": {
        0x0: "Mario",
        0x1: "Luigi",
        0x2: "Peach",
        0x3: "Daisy",
        0x4: "Yoshi",
        0x5: "Koopa",
        0x6: "Donkey Kong",
        0x7: "Diddy Kong",
        0x8: "Wario",
        0x9: "Waluigi",
        0xa: "Birdo",
        0xb: "Bowser",
        0xc: "Bowser Jr.",
        0xd: "Boo",
        0xe: "Shadow Mario",
        0xf: "Petey Piranha",
        0x10: "Mario (Star)",
        0x11: "Luigi (Star)",
        0x12: "Peach (Star)",
        0x13: "Daisy (Star)",
        0x14: "Yoshi (Star)",
        0x15: "Koopa (Star)",
        0x16: "Donkey Kong (Star)",
        0x17: "Diddy Kong (Star)",
        0x18: "Wario (Star)",
        0x19: "Waluigi (Star)",
        0x1a: "Birdo (Star)",
        0x1b: "Bowser (Star)",
        0x1c: "Bowser Jr. (Star)",
        0x1d: "Boo (Star)",
        0x1e: "Shadow Mario (Star)",
        0x1f: "Petey Piranha (Star)",
    },
    "character_id_stats_order": [
        0x5, 0x15,
        0x2, 0x12,
        0x1, 0x11,
        0x7, 0x17,
        0x4, 0x14,
        0xd, 0x1d,
        0xa, 0x1a,
        0x9, 0x19,
        0x8, 0x18,
        0xc, 0x1c,
        0x3, 0x13,
        0xe, 0x1e,
        0x0, 0x10,
        0x6, 0x16,
        0xb, 0x1b,
        0xf, 0x1f,
    ]
}

# List of hole data for Ring Attack that contain Ring Attack ring definitions.
# 801431CC, 1401CC
ring_attack_holes = [
    {
        "file": "lakitu_valley/ring_attack_0.json",
        "dolTitlePointer": 0x142098,
    },
    {
        "file": "lakitu_valley/ring_attack_1.json",
        "dolTitlePointer": 0x14205C,
    },
    {
        "file": "lakitu_valley/ring_attack_2.json",
        "dolTitlePointer": 0x142064,
    },
    {
        "file": "lakitu_valley/ring_attack_3.json",
        "dolTitlePointer": 0x142058,
    },
    {
        "file": "lakitu_valley/ring_attack_4.json",
        "dolTitlePointer": 0x14208C,
    },
    {
        "file": "lakitu_valley/ring_attack_5.json",
        "dolTitlePointer": 0x142068,
    },
    {
        "file": "cheep_cheep_falls/ring_attack_0.json",
        "dolTitlePointer": 0x14209C,
    },
    {
        "file": "cheep_cheep_falls/ring_attack_1.json",
        "dolTitlePointer": 0x1420A0,
    },
    {
        "file": "cheep_cheep_falls/ring_attack_2.json",
        "dolTitlePointer": 0x1420CC,
    },
    {
        "file": "cheep_cheep_falls/ring_attack_3.json",
        "dolTitlePointer": 0x1420B8,
    },
    {
        "file": "cheep_cheep_falls/ring_attack_4.json",
        "dolTitlePointer": 0x1420D4,
    },
    {
        "file": "cheep_cheep_falls/ring_attack_5.json",
        "dolTitlePointer": 0x1420D8,
    },
    {
        "file": "shifting_sands/ring_attack_0.json",
        "dolTitlePointer": 0x1420E4,
    },
    {
        "file": "shifting_sands/ring_attack_1.json",
        "dolTitlePointer": 0x142100,
    },
    {
        "file": "shifting_sands/ring_attack_2.json",
        "dolTitlePointer": 0x142104,
    },
    {
        "file": "shifting_sands/ring_attack_3.json",
        "dolTitlePointer": 0x142108,
    },
    {
        "file": "shifting_sands/ring_attack_4.json",
        "dolTitlePointer": 0x142114,
    },
    {
        "file": "shifting_sands/ring_attack_5.json",
        "dolTitlePointer": 0x142128,
    },
    {
        "file": "blooper_bay/ring_attack_0.json",
        "dolTitlePointer": 0x142130,
    },
    {
        "file": "blooper_bay/ring_attack_1.json",
        "dolTitlePointer": 0x142138,
    },
    {
        "file": "blooper_bay/ring_attack_2.json",
        "dolTitlePointer": 0x14213C,
    },
    {
        "file": "blooper_bay/ring_attack_3.json",
        "dolTitlePointer": 0x142148,
    },
    {
        "file": "blooper_bay/ring_attack_4.json",
        "dolTitlePointer": 0x142150,
    },
    {
        "file": "blooper_bay/ring_attack_5.json",
        "dolTitlePointer": 0x14216C,
    },
    {
        "file": "peach_castle_grounds/ring_attack_0.json",
        "dolTitlePointer": 0x142174,
    },
    {
        "file": "peach_castle_grounds/ring_attack_1.json",
        "dolTitlePointer": 0x142178,
    },
    {
        "file": "peach_castle_grounds/ring_attack_2.json",
        "dolTitlePointer": 0x142190,
    },
    {
        "file": "peach_castle_grounds/ring_attack_3.json",
        "dolTitlePointer": 0x14219C,
    },
    {
        "file": "peach_castle_grounds/ring_attack_4.json",
        "dolTitlePointer": 0x1421B0,
    },
    {
        "file": "peach_castle_grounds/ring_attack_5.json",
        "dolTitlePointer": 0x1421B8,
    },
    {
        "file": "bowser_badlands/ring_attack_0.json",
        "dolTitlePointer": 0x1421C0,
    },
    {
        "file": "bowser_badlands/ring_attack_1.json",
        "dolTitlePointer": 0x1421D4,
    },
    {
        "file": "bowser_badlands/ring_attack_2.json",
        "dolTitlePointer": 0x1421E8,
    },
    {
        "file": "bowser_badlands/ring_attack_3.json",
        "dolTitlePointer": 0x1421F4,
    },
    {
        "file": "bowser_badlands/ring_attack_4.json",
        "dolTitlePointer": 0x1421E0,
    },
    {
        "file": "bowser_badlands/ring_attack_5.json",
        "dolTitlePointer": 0x1421D8,
    },
]
