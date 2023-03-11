from process_song import process_song
from generate_nbt_structure import generate_nbt_structure, Block


# todo: actually generate nbt structure(s)
def generate_wall_sequencer(
    nbs_file_path: str,
    save_to_path: str,
    instruments: list[Block],
    max_height: int = 380,
) -> None:
    channels, tickchannels = process_song(nbs_file_path)
    for tick in tickchannels:
        print(tick)
    for channel in channels:
        print(channel)
    generate_nbt_structure(
        save_to_path, instruments, channels, tickchannels, max_height
    )


nbs_file_path = "songs/VengaBus.nbs"
save_to_path = "output/wall.nbt"
max_height = 380

BLOCKS = []
BLOCKS.append(Block(0, "minecraft:dirt", False, True))
BLOCKS.append(Block(1, "minecraft:oak_planks", False, True))
BLOCKS.append(Block(2, "minecraft:stone", False, True))
BLOCKS.append(Block(3, "minecraft:sand", True, True))
BLOCKS.append(Block(4, "minecraft:glass", False, False))
BLOCKS.append(Block(5, "minecraft:brown_wool", False, True))
BLOCKS.append(Block(6, "minecraft:clay", False, True))
BLOCKS.append(Block(7, "minecraft:gold_block", False, True))
BLOCKS.append(Block(8, "minecraft:packed_ice", False, True))
BLOCKS.append(Block(9, "minecraft:bone_block", False, True))
BLOCKS.append(Block(10, "minecraft:iron_block", False, True))
BLOCKS.append(Block(11, "minecraft:soul_sand", False, True))
BLOCKS.append(Block(12, "minecraft:pumpkin", False, True))
BLOCKS.append(Block(13, "minecraft:emerald_block", False, True))
BLOCKS.append(Block(14, "minecraft:hay_block", False, True))
BLOCKS.append(Block(15, "minecraft:glowstone", False, False))

generate_wall_sequencer(nbs_file_path, save_to_path, BLOCKS)
