from nbt_helper.block_helper import *
from nbt_helper.nbt_structure_helper import BlockData

air: BlockData = BlockData("minecraft:air")
redstone_wire: BlockData = BlockData("minecraft:redstone_wire")
redstone_wire_connecting: BlockData = BlockData(
    "minecraft:redstone_wire",
    [("east", "side"), ("north", "side"), ("south", "side"), ("west", "side")],
)
observer_wire_alt: BlockData = BlockData("minecraft:powered_rail",[("shape", "east_west")])
note_block: BlockData = BlockData("minecraft:note_block")

neutral_building: BlockData = BlockData("minecraft:cyan_terracotta")
floor_building: BlockData = BlockData("minecraft:light_gray_stained_glass")
light_source: BlockData = BlockData("minecraft:ochre_froglight", [("axis", "y")])
wall_ns: BlockData = BlockData("minecraft:polished_deepslate_wall",[("north", "tall"), ("south", "tall")])
wall_ns_top: BlockData = BlockData("minecraft:polished_deepslate_wall",[("north", "low"), ("south", "low")])

redstone_solid_support: BlockData = BlockData("minecraft:iron_block")
redstone_slab: BlockData = BlockData("minecraft:smooth_stone_slab", [("type", "top")])
redstone_line_main: BlockData = BlockData("minecraft:blue_concrete")
redstone_line_torch: BlockData = BlockData("minecraft:red_concrete")
redstone_line_start: BlockData = BlockData("minecraft:lime_concrete")
redstone_line_reset: BlockData = BlockData("minecraft:purple_concrete")
piston_payload: BlockData = BlockData("minecraft:green_concrete")

