from nbt_helper.nbt_structure_helper import BlockData


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
