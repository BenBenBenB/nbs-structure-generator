import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from common_blocks import INSTRUMENTS, InstrumentBlock
from generate_simple_walkway import generate_simple_walkway_nbt_structure


def generate_simple_walkway(
    nbs_file_path: str,
    save_to_path: str,
    instruments: list[InstrumentBlock],
    song_tps: int = 10,
    max_height: int = 60,
    tileable_width: int = 7,
    walkway_option: str = None,
) -> None:
    nbtStructure = generate_simple_walkway_nbt_structure(
        nbs_file_path,
        instruments,
        song_tps,
        max_height,
        tileable_width,
        walkway_option,
    )
    nbt_file = nbtStructure.get_nbt(pressurize=False)
    nbt_file.write_file(filename=save_to_path)


if __name__ == "__main__":
    main_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )  # get two directories above this file
    nbs_file_path = "songs/vengabus.nbs"
    full_path = os.path.join(main_dir, nbs_file_path)
    save_to_path = os.path.join(main_dir, "output/vengabus_simple.nbt")
    generate_simple_walkway(full_path, save_to_path, INSTRUMENTS, 10, 29, 5)
