from nbt_helper.nbt_structure_helper import BlockData

air: BlockData = BlockData("minecraft:air")
redstone_wire: BlockData = BlockData("minecraft:redstone_wire")
redstone_wire_connecting: BlockData = BlockData(
    "minecraft:redstone_wire",
    [("east", "side"), ("north", "side"), ("south", "side"), ("west", "side")],
)
observer_wire_alt: BlockData = BlockData("minecraft:powered_rail",[("shape", "east_west")])
redstone_torch: BlockData = BlockData("minecraft:redstone_torch")
redstone_torch_north: BlockData = BlockData("minecraft:redstone_wall_torch",[("facing","north")])
redstone_torch_south: BlockData = BlockData("minecraft:redstone_wall_torch",[("facing","south")])
repeater: BlockData = BlockData("minecraft:repeater")
observer: BlockData = BlockData("minecraft:observer")
note_block: BlockData = BlockData("minecraft:note_block")
piston_east: BlockData = BlockData("minecraft:piston",[("facing","east")])
piston_west: BlockData = BlockData("minecraft:piston",[("facing","west")])

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

observer_up: BlockData = BlockData("minecraft:observer",[("facing", "up")])
observer_down: BlockData = BlockData("minecraft:observer",[("facing", "down")])
observer_north: BlockData = BlockData("minecraft:observer",[("facing", "north")])
observer_south: BlockData = BlockData("minecraft:observer",[("facing", "south")])
observer_east: BlockData = BlockData("minecraft:observer",[("facing", "east")])
observer_west: BlockData = BlockData("minecraft:observer",[("facing", "west")])

