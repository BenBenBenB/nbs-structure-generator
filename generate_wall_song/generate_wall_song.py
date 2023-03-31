import os

from generate_wall_song_nbt_structure import (
    InstrumentBlock,
    generate_wall_song_nbt_structure,
)
from nbt_helper.nbt_structure_helper import BlockData
from process_song import process_song


def generate_wall_sequencer(
    nbs_file_path: str,
    save_to_path: str,
    instruments: list[InstrumentBlock],
    max_height: int = 380,
) -> None:
    channels, tickchannels = process_song(nbs_file_path)
    generate_wall_song_nbt_structure(
        save_to_path, filename, instruments, channels, tickchannels, max_height
    )


BLOCKS = [
    (InstrumentBlock(0, "harp", BlockData("minecraft:dirt"), False, True)),
    (InstrumentBlock(1, "bass", BlockData("minecraft:oak_planks"), False, True)),
    (InstrumentBlock(2, "basedrum", BlockData("minecraft:stone"), False, True)),
    (InstrumentBlock(3, "snare", BlockData("minecraft:sand"), True, True)),
    (InstrumentBlock(4, "hat", BlockData("minecraft:glass"), False, False)),
    (InstrumentBlock(5, "guitar", BlockData("minecraft:brown_wool"), False, True)),
    (InstrumentBlock(6, "flute", BlockData("minecraft:clay"), False, True)),
    (InstrumentBlock(7, "bell", BlockData("minecraft:gold_block"), False, True)),
    (InstrumentBlock(8, "chime", BlockData("minecraft:packed_ice"), False, True)),
    (InstrumentBlock(9, "xylophone", BlockData("minecraft:bone_block"), False, True)),
    (
        InstrumentBlock(
            10, "iron_xylophone", BlockData("minecraft:iron_block"), False, True
        )
    ),
    (InstrumentBlock(11, "cow_bell", BlockData("minecraft:soul_sand"), False, True)),
    (InstrumentBlock(12, "didgeridoo", BlockData("minecraft:pumpkin"), False, True)),
    (InstrumentBlock(13, "bit", BlockData("minecraft:emerald_block"), False, True)),
    (InstrumentBlock(14, "banjo", BlockData("minecraft:hay_block"), False, True)),
    (InstrumentBlock(15, "pling", BlockData("minecraft:glowstone"), False, False)),
]

if __name__ == "__main__":
    main_dir = os.path.dirname(os.path.dirname(__file__)) # get two directories above this file
    nbs_file_path = "songs/test.nbs"
    full_path = os.path.join(main_dir, nbs_file_path)
    save_to_path = "./output/"
    filename = "wall.nbt"
    max_height = 384
    generate_wall_sequencer(full_path, save_to_path, BLOCKS, max_height)
