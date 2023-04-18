from nbt_structure_utils import BlockData

WALL_MATERIAL = "polished_deepslate"


class InstrumentBlock:
    id: int
    instrument: str
    block_data: BlockData
    gravity: bool
    transmits_redstone: bool
    key: int  # will be "note" in block state

    def __init__(
        self,
        id: int,
        name: str,
        block: BlockData,
        grav: bool,
        reds: bool,
        key: int = None,
    ) -> None:
        self.id = id
        self.instrument = name
        self.block_data = block
        self.gravity = grav
        self.transmits_redstone = reds
        self.key = key

    def copy_with_key(self, key: int) -> "InstrumentBlock":
        return InstrumentBlock(
            self.id,
            self.instrument,
            self.block_data,
            self.gravity,
            self.transmits_redstone,
            key,
        )

    def get_note_block(self) -> BlockData:
        return BlockData(
            "note_block", [("instrument", self.instrument), ("note", self.key)]
        )


INSTRUMENTS = [
    (InstrumentBlock(0, "harp", BlockData("dirt"), False, True)),
    (InstrumentBlock(1, "bass", BlockData("oak_planks"), False, True)),
    (InstrumentBlock(2, "basedrum", BlockData("stone"), False, True)),
    (InstrumentBlock(3, "snare", BlockData("sand"), True, True)),
    (InstrumentBlock(4, "hat", BlockData("glass"), False, False)),
    (InstrumentBlock(5, "guitar", BlockData("brown_wool"), False, True)),
    (InstrumentBlock(6, "flute", BlockData("clay"), False, True)),
    (InstrumentBlock(7, "bell", BlockData("gold_block"), False, True)),
    (InstrumentBlock(8, "chime", BlockData("packed_ice"), False, True)),
    (InstrumentBlock(9, "xylophone", BlockData("bone_block"), False, True)),
    (InstrumentBlock(10, "iron_xylophone", BlockData("iron_block"), False, True)),
    (InstrumentBlock(11, "cow_bell", BlockData("soul_sand"), False, True)),
    (InstrumentBlock(12, "didgeridoo", BlockData("pumpkin"), False, True)),
    (InstrumentBlock(13, "bit", BlockData("emerald_block"), False, True)),
    (InstrumentBlock(14, "banjo", BlockData("hay_block"), False, True)),
    (InstrumentBlock(15, "pling", BlockData("glowstone"), False, False)),
]

air: BlockData = BlockData("air")
water: BlockData = BlockData("water")
blue_ice: BlockData = BlockData("blue_ice")
packed_ice: BlockData = BlockData("packed_ice")
soul_soil: BlockData = BlockData("soul_soil")
lamp: BlockData = BlockData("redstone_lamp")
redstone_wire: BlockData = BlockData("redstone_wire")
redstone_wire_connecting: BlockData = BlockData(
    "redstone_wire",
    [("east", "side"), ("north", "side"), ("south", "side"), ("west", "side")],
)


def get_flat_wall(
    material: str = WALL_MATERIAL, is_top: bool = False, dir: str = None
) -> BlockData:
    if dir[0] in ["e", "w"]:
        props = (
            [("east", "low"), ("west", "low")]
            if is_top
            else [("east", "tall"), ("west", "tall")]
        )
    elif dir[0] in ["n", "s"]:
        props = (
            [("north", "low"), ("south", "low")]
            if is_top
            else [("north", "tall"), ("south", "tall")]
        )
    return BlockData(material + "_wall", props)


def bool_to_str(value: bool) -> str:
    return "true" if value else "false"


def get_powered_rail(shape: str, powered: bool = False) -> BlockData:
    return BlockData(
        "powered_rail", [("shape", shape), ("powered", bool_to_str(powered))]
    )


def get_trap_door(material: str, facing: str, half: str) -> BlockData:
    name = material + "_trapdoor"
    return BlockData(name, [("facing", facing), ("half", half)])


def get_button(material: str, facing: str, face: str) -> BlockData:
    name = material + "_button"
    return BlockData(name, [("facing", facing), ("face", face)])


def get_dropper(facing: str) -> BlockData:
    return BlockData("dropper", [("facing", facing)])


def get_piston(facing: str) -> BlockData:
    return BlockData("piston", [("facing", facing)])


def get_sticky_piston(facing: str) -> BlockData:
    return BlockData("sticky_piston", [("facing", facing)])


def get_observer(facing: str, is_powered: bool = False) -> BlockData:
    return BlockData(
        "observer", [("powered", bool_to_str(is_powered)), ("facing", facing)]
    )


def get_repeater(facing: str, delay: int) -> BlockData:
    return BlockData("repeater", [("facing", facing), ("delay", str(delay))])


def get_comparator(facing: str, mode: str) -> BlockData:
    return BlockData("comparator", [("facing", facing), ("mode", mode)])


def get_redstone_torch(lit: bool = True, facing: str = None) -> BlockData:
    if facing is None:
        return BlockData("redstone_torch", [("lit", bool_to_str(lit))])
    else:
        return BlockData(
            "redstone_wall_torch",
            [("lit", bool_to_str(lit)), ("facing", facing)],
        )
