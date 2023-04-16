from nbt_structure_utils import BlockData

air: BlockData = BlockData("minecraft:air")
redstone_wire: BlockData = BlockData("minecraft:redstone_wire")
redstone_wire_connecting: BlockData = BlockData(
    "minecraft:redstone_wire",
    [("east", "side"), ("north", "side"), ("south", "side"), ("west", "side")],
)
observer_wire_alt: BlockData = BlockData(
    "minecraft:powered_rail", [("shape", "east_west")]
)
note_block: BlockData = BlockData("minecraft:note_block")

neutral_building: BlockData = BlockData("minecraft:cyan_terracotta")
floor_building: BlockData = BlockData("minecraft:light_gray_stained_glass")
light_source: BlockData = BlockData("minecraft:ochre_froglight", [("axis", "y")])
wall_ns: BlockData = BlockData(
    "minecraft:polished_deepslate_wall", [("north", "tall"), ("south", "tall")]
)
wall_ns_top: BlockData = BlockData(
    "minecraft:polished_deepslate_wall", [("north", "low"), ("south", "low")]
)

redstone_solid_support: BlockData = BlockData("minecraft:iron_block")
redstone_slab: BlockData = BlockData("minecraft:smooth_stone_slab", [("type", "top")])
redstone_line_main: BlockData = BlockData("minecraft:blue_concrete")
redstone_line_torch: BlockData = BlockData("minecraft:red_concrete")
redstone_line_start: BlockData = BlockData("minecraft:lime_concrete")
redstone_line_reset: BlockData = BlockData("minecraft:purple_concrete")
piston_payload: BlockData = BlockData("minecraft:green_concrete")


def bool_to_str(value: bool) -> str:
    return "true" if value else "false"


def get_trap_door(material: str, facing: str, half: str) -> BlockData:
    name = "minecraft:" + material + "_trapdoor"
    return BlockData(name, [("facing", facing), ("half", half)])


def get_button(material: str, facing: str, face: str) -> BlockData:
    name = "minecraft:" + material + "_button"
    return BlockData(name, [("facing", facing), ("face", face)])


def get_dropper(facing: str) -> BlockData:
    return BlockData("minecraft:dropper", [("facing", facing)])


def get_piston(facing: str) -> BlockData:
    return BlockData("minecraft:piston", [("facing", facing)])


def get_sticky_piston(facing: str) -> BlockData:
    return BlockData("minecraft:sticky_piston", [("facing", facing)])


def get_observer(facing: str) -> BlockData:
    return BlockData("minecraft:observer", [("facing", facing)])


def get_repeater(facing: str, delay: int) -> BlockData:
    return BlockData("minecraft:repeater", [("facing", facing), ("delay", str(delay))])


def get_comparator(facing: str, mode: str) -> BlockData:
    return BlockData("minecraft:comparator", [("facing", facing), ("mode", mode)])


def get_redstone_torch(lit: bool = True, facing: str = None) -> BlockData:
    if facing is None:
        return BlockData("minecraft:redstone_torch", [("lit", bool_to_str(lit))])
    else:
        return BlockData(
            "minecraft:redstone_wall_torch",
            [("lit", bool_to_str(lit)), ("facing", facing)],
        )
