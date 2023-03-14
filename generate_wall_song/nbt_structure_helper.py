from nbt.nbt import *


class Coordinate:
    __slots__ = ["x", "y", "z"]

    def __init__(self, x: int, y: int, z: int):
        if x < 0 or y < 0 or z < 0:
            raise ValueError("Coordinates must be 0 or positive.")
        self.x = x
        self.y = y
        self.z = z

    def get_nbt(self, tag_name: str):
        nbt_pos = TAG_List(name=tag_name, type=TAG_Int)
        nbt_pos.tags.append(TAG_Int(self.x))
        nbt_pos.tags.append(TAG_Int(self.y))
        nbt_pos.tags.append(TAG_Int(self.z))
        return nbt_pos

    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y and self.z == __o.z

    def __add__(self, __o: object) -> "Coordinate":
        return Coordinate(self.x + __o.x, self.y + __o.y, self.z + __o.z)

    def __sub__(self, __o: object) -> "Coordinate":
        return Coordinate(self.x - __o.x, self.y - __o.y, self.z - __o.z)


class BlockData:
    name: str
    properties: list[tuple]

    def __init__(self, item_id: str, props: list[tuple] = []) -> None:
        self.name = item_id
        self.properties = props

    def __eq__(self, __o: object) -> bool:
        return self.name == __o.name and sorted(self.properties) == sorted(
            __o.properties
        )

    def get_nbt(self):
        nbt_block_state = TAG_Compound()
        if any(self.properties):
            block_properties = TAG_Compound(name="Properties")
            for prop in self.properties:
                block_properties.tags.append(TAG_String(name=prop[0], value=prop[1]))
            nbt_block_state.tags.append(block_properties)
        nbt_block_state.tags.append(TAG_String(name="Name", value=self.name))
        return nbt_block_state


# Holds distinct list of blocks used in structure. BlockPosition 'state' refers to index from this list.
class Palette:
    blocks: list[BlockData]

    def __init__(self, block_data: list[BlockData] = []) -> None:
        self.blocks = []
        self.extend(block_data)

    def __iter__(self):
        return iter(self.blocks)

    def try_append(self, block: BlockData):
        if block not in self.blocks:
            self.blocks.append(block)

    def extend(self, blocks: list[BlockData]):
        for block in blocks:
            self.append(block)

    def get_state(self, block: BlockData):
        return self.blocks.index(block)

    def get_nbt(self):
        nbt_list = TAG_List(name="palette", type=TAG_Compound)
        for block in self.blocks:
            nbt_list.tags.append(block.get_nbt())
        return nbt_list


# For use in StructureBlocks. Stores block position and state from Palette.
class BlockPosition:
    pos: Coordinate
    state: int  # from Palette

    def __init__(self, pos: Coordinate, state: int) -> None:
        self.pos = pos
        self.state = state

    def get_nbt(self):
        nbt_block = TAG_Compound()
        nbt_block.tags.append(self.pos.get_nbt("pos"))
        nbt_block.tags.append(TAG_Int(name="state", value=self.state))
        return nbt_block


# Stores and manipulates list of block positions and states. Generates NBT for complete structure.
class StructureBlocks:
    # todo: add other block setting commands straight from MC
    blocks: list[BlockPosition]
    palette: Palette

    def __init__(self) -> None:
        self.blocks = []
        self.palette = Palette()

    def set_block(self, pos: Coordinate, block: BlockData):
        self.palette.try_append(block)
        state = self.palette.get_state(block)
        edit_block = next((item for item in self.blocks if item.pos == pos), None)
        if edit_block is None:
            self.blocks.append(BlockPosition(pos, state))
        else:
            edit_block.state = state

    def get_structure_size(self):
        x, y, z = 0, 0, 0
        for block in self.blocks:
            if block.pos.x > x:
                x = block.pos.x
            if block.pos.y > y:
                y = block.pos.y
            if block.pos.z > z:
                z = block.pos.z
        # todo: determine actual max size and possibly throw error
        # structures larger than 32x32x32 are allowed, we just need to lie about the size
        x = min([x + 1, 32])
        y = min([y + 1, 32])
        z = min([z + 1, 32])
        return Coordinate(x, y, z)

    def get_nbt(self):
        structure_file = NBTFile()
        structure_file.tags.append(self.get_structure_size().get_nbt("size"))
        structure_file.tags.append(TAG_List(name="entities", type=TAG_Compound))
        nbt_blocks = TAG_List(name="blocks", type=TAG_Compound)
        for block in self.blocks:
            nbt_blocks.tags.append(block.get_nbt())
        structure_file.tags.append(nbt_blocks)
        structure_file.tags.append(self.palette.get_nbt())
        structure_file.tags.append(TAG_Int(name="DataVersion", value=3218))
        return structure_file

    # todo
    def clone(self, other: "StructureBlocks", dest: Coordinate):
        pass

    # todo
    def clone(self, corner1: Coordinate, corner2: Coordinate, dest: Coordinate):
        pass

    # todo, perhaps split up instead of being cool and copying the minecraft syntax exactly
    def fill(
        self,
        corner1: Coordinate,
        corner2: Coordinate,
        fill_block: BlockData,
        block_handling: str = None,
        block_filter: BlockData = None,
    ):
        return
        valid_handlers = [None, "", "destroy", "hollow", "keep", "outline", "replace"]
        if block_handling not in valid_handlers:
            print("Invalid block handler: '%s'" % block_handling)
            return
        if block_handling == "replace":
            if block_filter is None:
                print("Must specify filter block for 'replace': '%s'" % block_handling)
