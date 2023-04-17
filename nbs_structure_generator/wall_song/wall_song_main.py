import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common_blocks import INSTRUMENTS, InstrumentBlock
from generate_wall_song import generate_wall_song_nbt_structure
from process_song import process_song


def generate_wall_sequencer(
    nbs_file_path: str,
    save_to_path: str,
    instruments: list[InstrumentBlock],
    max_height: int = 380,
) -> None:
    if max_height < 32:
        raise ValueError("Max height must be 32 or more.")
    channels, tickchannels = process_song(nbs_file_path)
    nbtStructure = generate_wall_song_nbt_structure(
        instruments, channels, tickchannels, max_height
    )
    nbt_file = nbtStructure.get_nbt(pressurize=False)
    nbt_file.write_file(filename=save_to_path)


if __name__ == "__main__":
    main_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # get two directories above this file
    nbs_file_path = "songs/test3.nbs"
    full_path = os.path.join(main_dir, nbs_file_path)
    save_to_path = "D:\\GameRelatedData\\Minecraft\\CurseForge\\Instances\\Fabric Vanilla\\saves\\New World\\generated\\minecraft\\structures\\test2.nbt"
    max_height = 52
    generate_wall_sequencer(full_path, save_to_path, INSTRUMENTS, max_height)
