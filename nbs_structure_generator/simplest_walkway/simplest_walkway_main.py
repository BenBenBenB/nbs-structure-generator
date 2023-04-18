import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common_blocks import INSTRUMENTS, InstrumentBlock
from generate_simplest_walkway import generate_simplest_walkway_nbt_structure


def generate_simplest_walkway(
    nbs_file_path: str,
    save_to_path: str,
    instruments: list[InstrumentBlock],
    walkway_option: str = None,
) -> None:
    nbtStructure = generate_simplest_walkway_nbt_structure(
        nbs_file_path, instruments, walkway_option
    )
    nbt_file = nbtStructure.get_nbt(pressurize=True)
    nbt_file.write_file(filename=save_to_path)


if __name__ == "__main__":
    main_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # get two directories above this file
    nbs_file_path = "songs/vengabus.nbs"
    full_path = os.path.join(main_dir, nbs_file_path)
    save_to_path = "D:/GameRelatedData/Minecraft/CurseForge/Instances/Fabric Vanilla/saves/New World/generated/minecraft/structures/test2.nbt"
    generate_simplest_walkway(full_path, save_to_path, INSTRUMENTS, "horse")
