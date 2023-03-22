from nbt_helper.nbt_structure_helper import BlockData

air: BlockData = BlockData("minecraft:air")
redstone_wire: BlockData = BlockData("minecraft:redstone_wire")
redstone_wire_neutral: BlockData = BlockData(
    "minecraft:redstone_wire",
    [("east", "none"), ("north", "none"), ("south", "none"), ("west", "none")],
)
redstone_torch: BlockData = BlockData("minecraft:redstone_torch")
repeater: BlockData = BlockData("minecraft:repeater")
observer: BlockData = BlockData("minecraft:observer")
note_block: BlockData = BlockData("minecraft:note_block")
piston: BlockData = BlockData("minecraft:piston")

neutral_building: BlockData = BlockData("minecraft:cyan_terracotta")
floor_building: BlockData = BlockData("minecraft:light_gray_stained_glass")
light_source: BlockData = BlockData("minecraft:ochre_froglight", [("axis", "y")])
wall: BlockData = BlockData("minecraft:polished_deepslate_wall")
redstone_solid_support: BlockData = BlockData("minecraft:iron_block")
redstone_slab: BlockData = BlockData("minecraft:smooth_stone_slab", [("type", "top")])
redstone_line_main: BlockData = BlockData("minecraft:blue_concrete")
redstone_line_torch: BlockData = BlockData("minecraft:red_concrete")
redstone_line_start: BlockData = BlockData("minecraft:lime_concrete")
redstone_line_reset: BlockData = BlockData("minecraft:purple_concrete")
piston_payload: BlockData = BlockData("minecraft:green_concrete")
observer_wire_alt: BlockData = BlockData("minecraft:powered_rail",[("shape", "east_west")])

observer_up: BlockData = BlockData("minecraft:observer",[("facing", "up")])
observer_down: BlockData = BlockData("minecraft:observer",[("facing", "down")])
observer_north: BlockData = BlockData("minecraft:observer",[("facing", "north")])
observer_south: BlockData = BlockData("minecraft:observer",[("facing", "south")])
observer_east: BlockData = BlockData("minecraft:observer",[("facing", "east")])
observer_west: BlockData = BlockData("minecraft:observer",[("facing", "west")])

