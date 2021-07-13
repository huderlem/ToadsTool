# ToadsTool
Tool which can edit Mario Golf: Toadstool Tour files. This README is still under construction.

# Get Started

1. Install Python 3.
2. Obtain a Mario Golf: Toadstool Tour (USA) ISO
3. Extract the ISO's filesystem. (The Dolphin emulator can do this for you.)
4. Run `python toadstool.py -i <extracted-ISO-filesystem> setup`.  This will extract various files from the game and place them by default in a `work/` directory in the same directory as `toadstool.py`.
5. Modify any desired file in the `work/` directory.
6. Run `python toadstool.py -i <extracted-ISO-filesystem> build`.  This will process files from `work/` into a directory called `stage/` by default.  Then, it will copy files from `stage/` into the ISO's extracted filesystem.
7. Load the game in Dolphipn and see your changes in action.
