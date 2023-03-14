from process_song import process_song
from generate_wall_song_nbt_structure import (
    generate_wall_song_nbt_structure,
    InstrumentBlockPhysics,
)


def generate_wall_sequencer(
    nbs_file_path: str,
    save_to_path: str,
    instruments: list[InstrumentBlockPhysics],
    max_height: int = 380,
) -> None:
    channels, tickchannels = process_song(nbs_file_path)
    generate_wall_song_nbt_structure(
        save_to_path, filename, instruments, channels, tickchannels, max_height
    )


BLOCKS = []
BLOCKS.append(InstrumentBlockPhysics(0, "minecraft:dirt", False, True))
BLOCKS.append(InstrumentBlockPhysics(1, "minecraft:oak_planks", False, True))
BLOCKS.append(InstrumentBlockPhysics(2, "minecraft:stone", False, True))
BLOCKS.append(InstrumentBlockPhysics(3, "minecraft:sand", True, True))
BLOCKS.append(InstrumentBlockPhysics(4, "minecraft:glass", False, False))
BLOCKS.append(InstrumentBlockPhysics(5, "minecraft:brown_wool", False, True))
BLOCKS.append(InstrumentBlockPhysics(6, "minecraft:clay", False, True))
BLOCKS.append(InstrumentBlockPhysics(7, "minecraft:gold_block", False, True))
BLOCKS.append(InstrumentBlockPhysics(8, "minecraft:packed_ice", False, True))
BLOCKS.append(InstrumentBlockPhysics(9, "minecraft:bone_block", False, True))
BLOCKS.append(InstrumentBlockPhysics(10, "minecraft:iron_block", False, True))
BLOCKS.append(InstrumentBlockPhysics(11, "minecraft:soul_sand", False, True))
BLOCKS.append(InstrumentBlockPhysics(12, "minecraft:pumpkin", False, True))
BLOCKS.append(InstrumentBlockPhysics(13, "minecraft:emerald_block", False, True))
BLOCKS.append(InstrumentBlockPhysics(14, "minecraft:hay_block", False, True))
BLOCKS.append(InstrumentBlockPhysics(15, "minecraft:glowstone", False, False))

if __name__ == "__main__":
    nbs_file_path = "songs/test.nbs"
    save_to_path = "./output/"
    filename = "wall.nbt"
    max_height = 384
    generate_wall_sequencer(nbs_file_path, save_to_path, BLOCKS, max_height)
