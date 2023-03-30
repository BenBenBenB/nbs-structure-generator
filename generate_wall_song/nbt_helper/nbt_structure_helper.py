from nbt.nbt import *
from nbt_helper.plot_helpers import LineSegment, Vector, Cuboid
from nbt_helper.item_helper import *

AIR_BLOCK_NAME = "minecraft:air"


class BlockData:
    name: str
    properties: list[tuple]

    def __init__(self, item_id: str, props: list[tuple] = []) -> None:
        if ":" not in item_id:
            self.name = "minecraft:" + item_id
        else:
            self.name = item_id
        self.properties = props.copy()

    def __eq__(self, __o: object) -> bool:
        if __o is None:
            return False
        return self.name == __o.name and sorted(self.properties) == sorted(
            __o.properties
        )

    def copy(self):
        return BlockData(self.name, self.properties)

    def get_nbt(self) -> TAG_Compound:
        nbt_block_state = TAG_Compound()
        if any(self.properties):
            block_properties = TAG_Compound(name="Properties")
            for prop in self.properties:
                block_properties.tags.append(
                    TAG_String(name=prop[0], value=str(prop[1]))
                )
            nbt_block_state.tags.append(block_properties)
        nbt_block_state.tags.append(TAG_String(name="Name", value=self.name))
        return nbt_block_state


AIR_BLOCK = BlockData(AIR_BLOCK_NAME)


class Palette:
    """Holds distinct list of blocks used in structure. BlockPosition 'state' refers to index from this list.

    Methods:
        try_append(block):
            adds a block if not in palette
        extend(blocks):
            adds any blocks not in palette
        get_state(block):
            return index of state that matches block
        try_get_state(block):
            return None or index of block
        get_nbt():
            return TAG_List representation of palette
    """

    __blocks: list[BlockData]

    def __init__(self, block_data: list[BlockData] = []) -> None:
        self.__blocks = []
        self.extend(block_data.copy())

    def __iter__(self):
        return iter(self.__blocks)

    def __getitem__(self, key) -> BlockData:
        return self.__blocks[key]

    def try_append(self, block: BlockData) -> None:
        if block is None:
            raise ValueError("Palette cannont contain None")
        if block not in self.__blocks:
            self.__blocks.append(block)

    def copy(self) -> None:
        return Palette(self.__blocks)

    def extend(self, blocks: list[BlockData]) -> None:
        for block in blocks:
            self.try_append(block)

    def get_state(self, block: BlockData) -> int:
        return self.__blocks.index(block)

    def try_get_state(self, block: BlockData) -> int:
        try:
            return self.__blocks.index(block)
        except ValueError:
            return None

    def get_nbt(self) -> TAG_List:
        nbt_list = TAG_List(name="palette", type=TAG_Compound)
        for block in self.__blocks:
            nbt_list.tags.append(block.get_nbt())
        return nbt_list


class BlockPosition:
    """For use in NbtStructure. Stores block position and integer state from Palette."""

    pos: Vector
    state: int  # from Palette
    inv: Inventory

    def __init__(self, pos: Vector, state: int, inventory: Inventory = None) -> None:
        self.pos = pos.copy()
        self.state = state
        self.inv = inventory

    def __hash__(self) -> int:
        return hash(self.pos)

    def update_state(self, new_state: int) -> bool:
        if self.state != new_state:
            self.state = new_state
            return True
        else:
            return False

    def get_nbt(self) -> TAG_Compound:
        nbt_block = TAG_Compound()
        if self.inv is not None:
            nbt_block.tags.append(self.inv.get_nbt())
        nbt_block.tags.append(self.pos.get_nbt("pos"))
        nbt_block.tags.append(TAG_Int(name="state", value=self.state))

        return nbt_block


class NbtStructure:
    """Stores and manipulates list of block positions and states. Generates NBT for complete structure.
        Important Note about block behavior:
            None:
                Specify as fill_block in methods to remove block (including air) from pos.
            air:
                Include air block positions in list to overwrite existing blocks when cloning and loading in world

    Methods:
        get_nbt(make_structure_place_air=True):
            Get NBT file object representing the structure. input True to make it void the full cuboid when loading in MC
        get_block_state(pos) -> BlockData:
            Get corresponding BlockData from palette
        get_max_coords(include_air=True) -> Vector:
            Get max x,y,z found across all blocks
        get_min_coords(include_air=True) -> Vector:
            Get min x,y,z found across all blocks

    Fill Commands:
        set_block(pos, block) -> bool:
            Attempt to update block at position. return True if a change was made. Set as None to create void.
        fill(volume: Cuboid, fill_block: BlockData) -> int:
            Set all blocks in volume to fill_block.
        fill_hollow(self, volume: Cuboid, fill_block: BlockData) -> int:
            Fill all blocks along faces of cuboid to fill_block. Fill interior with air blocks.
        fill_keep(self, volume: Cuboid, fill_block: BlockData) -> int:
            Fill only air blocks and void spaces with fill_block. Leave others untouched.
        fill_outline(self, volume: Cuboid, fill_block: BlockData) -> int:
            Fill all blocks along faces of cuboid to fill_block. Leave interior untouched
        fill_frame(self, volume: Cuboid, fill_block: BlockData) -> int:
            Fill all blocks along edges of cuboid to fill_block.
        fill_replace( volume: Cuboid, fill_block: BlockData, filter_block: BlockData,) -> int:
            Replace all instances of filter_block with fill_block in volume. Use None to target voids.

    Update Methods:
        shift(delta: Vector) -> int:
            Move entire structure by delta vector
        crop(volume: Cuboid) -> int:
            Remove blocks outside of volume and shift remaining cuboid to align with 0,0,0
        clone_block(s_pos:Vector, t_pos:Vector):
            Clones a single block from one pos to another.
        clone(volume: Cuboid, dest: Vector):
            Clone blocks from self in source volume. Target volume is aligned to dest. Overlap not allowed.
        clone_structure(other: "NbtStructure", dest: Vector):
            Clone another NbtStructure object into this one. Target volume is aligned to dest.
        pressurize() -> int:
            Replace all voids with air blocks
        depressurize() -> int:
            Replace all air blocks with voids
    """

    blocks: dict[BlockPosition]
    palette: Palette

    def __init__(self) -> None:
        self.blocks = {}
        self.palette = Palette()

    def __getitem__(self, key) -> BlockPosition:
        return self.blocks.get(key, None)

    def get_nbt(
        self, fill_void_with_air: bool = True, trim_excess_air: bool = False
    ) -> NBTFile:
        """Create NBTFile that can be saved to disk then loaded into Minecraft via a structure block. Default args will save like a structure block would.

        Args:
            fill_void_with_air (bool, optional): Replace voids with air blocks so that structure loads like one created in minecraft would. Defaults to True.
            trim_excess_air (bool, optional): minimize size of structure by restricting to smallest cuboid containing all non-air blocks. Defaults to False.

        Returns:
            NBTFile: the complete structure
        """
        min_coords = self.get_min_coords(include_air=not trim_excess_air)
        max_coords = self.get_max_coords(include_air=not trim_excess_air)
        self.crop(Cuboid(min_coords, max_coords))
        self.shift(min_coords * -1)
        max_coords.sub(min_coords)
        min_coords.sub(min_coords)
        blocks_to_write = self.blocks.copy()
        if fill_void_with_air:
            self.__pressurize(blocks_to_write, Cuboid(min_coords, max_coords))

        structure_file = NBTFile()
        size = max_coords + Vector(1, 1, 1)
        structure_file.tags.append(size.get_nbt("size"))
        structure_file.tags.append(TAG_List(name="entities", type=TAG_Compound))
        nbt_blocks = TAG_List(name="blocks", type=TAG_Compound)
        for block in blocks_to_write.values():
            nbt_blocks.tags.append(block.get_nbt())
        structure_file.tags.append(nbt_blocks)
        structure_file.tags.append(self.palette.get_nbt())
        structure_file.tags.append(TAG_Int(name="DataVersion", value=3218))
        return structure_file

    def get_block_state(self, pos: Vector) -> BlockData:
        """Get block name and properties at pos"""
        block = self.__get_block(pos)
        if block is None:
            return None
        return self.palette[block.state]

    def __get_block(self, pos: Vector) -> BlockPosition:
        return self.blocks.get(pos, None)

    def set_block(self, pos: Vector, block: BlockData, inv: Inventory = None) -> bool:
        """Update block at pos. Remove if block is None. Returns True if an update was made."""
        if block is None:
            return self.__remove_block(pos)
        state = self.__upsert_palette(block)
        return self.__set_block(BlockPosition(pos, state, inv))

    def __set_block(self, new_block: BlockPosition) -> bool:
        self.blocks[new_block.pos] = new_block

    def __remove_block(self, pos: Vector) -> None:
        try:
            self.blocks.pop(pos)
        except KeyError:
            pass

    def __upsert_palette(self, new_block: BlockData) -> int:
        """adds block to palette and/or returns the state id"""
        self.palette.try_append(new_block)
        return self.palette.get_state(new_block)

    def get_max_coords(self, include_air=True) -> Vector:
        """get max x,y,z of smallest cuboid containing all blocks"""
        if not self.blocks:
            return Vector(0, 0, 0)
        filter_state = None if include_air else self.palette.try_get_state(AIR_BLOCK)
        first = self.blocks[next(iter(self.blocks))].pos
        x, y, z = first.x, first.y, first.z
        for block in (b for b in self.blocks.values() if b.state != filter_state):
            if block.pos.x > x:
                x = block.pos.x
            if block.pos.y > y:
                y = block.pos.y
            if block.pos.z > z:
                z = block.pos.z
        return Vector(x, y, z)

    def get_min_coords(self, include_air=True) -> Vector:
        """get min x,y,z of smallest cuboid containing all blocks"""
        if not self.blocks:
            return Vector(0, 0, 0)
        filter_state = None if include_air else self.palette.try_get_state(AIR_BLOCK)
        first = self.blocks[next(iter(self.blocks))].pos
        x, y, z = first.x, first.y, first.z
        for block in (b for b in self.blocks.values() if b.state != filter_state):
            if block.pos.x < x:
                x = block.pos.x
            if block.pos.y < y:
                y = block.pos.y
            if block.pos.z < z:
                z = block.pos.z
        return Vector(x, y, z)

    def shift(self, delta: Vector) -> None:
        """Add delta to every block's pos"""
        if delta == Vector(0, 0, 0):
            return
        new_blocks = {}
        for block in self.blocks.values():
            block.pos.add(delta)
            new_blocks[block.pos] = block
        self.blocks = new_blocks

    def clone_structure(self, other: "NbtStructure", dest: Vector) -> None:
        """Completely clone other structure to this one. dest defines minimum x,y,z corner of target volume"""
        for otherblock in other.blocks.values():
            dest_pos = otherblock.pos + dest
            self.set_block(dest_pos, other.palette[otherblock.state], otherblock.inv)

    def clone(self, source_volume: Cuboid, dest: Vector) -> None:
        """Clones blocks from source_volume. dest defines minimum x,y,z of target volume which must not overlap source."""
        if NbtStructure.__does_clone_dest_overlap(source_volume, dest):
            raise ValueError("The source and destination volumes cannot overlap")
        offset = dest - source_volume.min_corner
        for pos in source_volume:
            self.clone_block(pos, pos + offset)

    def clone_block(self, s_pos: Vector, t_pos: Vector) -> bool:
        """Clone a single block from s_pos to t_pos"""
        block = self.__get_block(s_pos)
        if block is None:
            return self.__remove_block(t_pos)
        else:
            return self.__set_block(BlockPosition(t_pos, block.state, block.inv))

    def crop(self, volume: Cuboid) -> None:
        """Remove blocks outside of volume

        Args:
            volume (Cuboid): defines corners of desired box
        """
        for k, v in self.blocks.items():
            if not volume.contains(v.pos):
                self.blocks.pop(k)

    def fill(
        self, volume: Cuboid, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Set all blocks in volume to fill_block.

        Args:
            volume (Cuboid): defines corners of desired box
            fill_block (BlockData): block to set. Use None to remove blocks.
        """
        if fill_block is None:
            return self.__remove(volume)
        new_state = self.__upsert_palette(fill_block)
        for pos in volume:
            self.__set_block(BlockPosition(pos, new_state, inv))

    def __remove(self, volume: Cuboid) -> None:
        """Remove all blocks in volume"""
        for pos in volume:
            self.__remove_block(pos)

    def fill_hollow(
        self, volume: Cuboid, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Fill all blocks along the 6 faces of cuboid to fill_block. Fill interior with air.

        Args:
            volume (Cuboid): defines corners of desired box
            fill_block (BlockData): block to set. Use None to remove blocks.
        """
        size = volume.size()
        if size.x > 2 and size.y > 2 and size.z > 2:
            shift = Vector(1, 1, 1)
            interior_min = volume.min_corner + shift
            interior_max = volume.max_corner - shift
            self.fill(Cuboid(interior_min, interior_max), AIR_BLOCK, None)
        self.fill_outline(volume, fill_block, inv)

    def __pressurize(
        self, blocks_to_write: list[BlockPosition], volume: Cuboid
    ) -> None:
        """Replace voids in the temp dict with air blocks so that structure loads like one from minecraft would."""
        air_state = self.__upsert_palette(AIR_BLOCK)
        for pos in volume:
            if self.__get_block(pos) is None:
                blocks_to_write[pos] = BlockPosition(pos, air_state, None)

    def pressurize(self) -> None:
        """Fill all voids with air. Use this to make entire cuboid overwrite existing blocks when loading into Minecraft or cloning."""
        min_coords = self.get_min_coords()
        max_coords = self.get_max_coords()
        return self.fill_keep(Cuboid(min_coords, max_coords), AIR_BLOCK, None)

    def depressurize(self) -> None:
        """Replace all air blocks with void. This allows you load in MC and clone without air overwriting existing blocks in target volume.

        Returns:
            int: count of blocks affected
        """
        min_coords = self.get_min_coords()
        max_coords = self.get_max_coords()
        return self.fill_keep(Cuboid(min_coords, max_coords), None, None)

    def fill_keep(
        self, volume: Cuboid, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Fill only air blocks and void spaces with fill_block. Leave others untouched.

        Args:
            volume (Cuboid):
                corners of volume to search
            fill_block (BlockData):
                use fill_block = None to remove all air blocks
        """
        self.fill_replace(volume, fill_block, AIR_BLOCK, inv)
        self.fill_replace(volume, fill_block, None, inv)

    def fill_outline(
        self, volume: Cuboid, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Fill all blocks along the 6 faces of cuboid to fill_block. Leave interior untouched

        Args:
            volume (Cuboid): defines corners of desired box
            fill_block (BlockData): block to set. Use None to remove blocks.
        """
        if fill_block.name == None:
            return self.__remove_outline(volume)
        new_state = self.__upsert_palette(fill_block)
        for pos in volume:
            if volume.boundary_contains(pos):
                self.__set_block(BlockPosition(pos, new_state, inv))

    def __remove_outline(self, volume: Cuboid) -> None:
        """Remove all blocks along faces of cuboid."""
        for pos in volume:
            if volume.boundary_contains(pos):
                self.__remove_block(pos)

    def fill_frame(
        self, volume: Cuboid, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Fill all blocks along edges of cuboid to fill_block."""
        if fill_block == None:
            return self.__remove_frame(volume)
        new_state = self.__upsert_palette(fill_block)
        for pos in volume:
            if volume.edge_contains(pos):
                self.__set_block(BlockPosition(pos, new_state, inv))

    def __remove_frame(self, volume: Cuboid) -> None:
        """Remove all blocks along edges of cuboid"""
        for pos in volume:
            if volume.edge_contains(pos):
                self.__remove_block(pos)

    def fill_replace(
        self,
        volume: Cuboid,
        fill_block: BlockData,
        filter_block: BlockData,
        inv: Inventory = None,
    ) -> None:
        """Replace all instances of filter_block with fill_block in volume. Use None to target voids."""
        if fill_block is None:
            return self.__remove_replace(volume, filter_block)
        if filter_block is None:
            return self.__fill_void(volume, fill_block, inv)
        elif fill_block == filter_block:
            return

        filter_state = self.palette.try_get_state(filter_block)
        if filter_state is None:
            return
        new_state = self.__upsert_palette(fill_block)

        for pos in volume:
            block = self.__get_block(pos)
            if block is not None and block.state == filter_state:
                block.state = new_state
                block.inventory = inv

    def __remove_replace(self, volume: Cuboid, filter_block: BlockData) -> None:
        """Remove all instances of filter_block from volume."""
        try:
            state_to_replace = self.palette.get_state(filter_block)
        except ValueError:  # block to replace is not in structure
            return
        for pos in volume:
            block = self.__get_block(pos)
            if block is not None and block.state == state_to_replace:
                self.__remove_block(pos)

    def __fill_void(
        self, volume: Cuboid, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Fill all void positions with fill_block. Leave existing blocks untouched"""
        new_state = self.__upsert_palette(fill_block)
        for pos in volume:
            block = self.__get_block(pos)
            if block is None:
                self.__set_block(BlockPosition(pos, new_state, inv))

    def fill_line(
        self, points: LineSegment, fill_block: BlockData, inv: Inventory = None
    ) -> None:
        """Draw a 1 block wide straight line connecting each point to the next."""
        new_state = None if fill_block is None else self.__upsert_palette(fill_block)
        for pos in points.draw_straight_lines():
            if new_state is None:
                self.__remove_block(pos)
            else:
                self.__set_block(BlockPosition(pos, new_state, inv))

    @staticmethod
    def __does_clone_dest_overlap(source_volume: Cuboid, dest: Vector) -> bool:
        """Check if a cuboid of same dimensions as source can be created at dest without overlapping source

        Returns:
            bool: True if overlap would occur
        """
        min_pos = source_volume.min_corner + Vector(1, 1, 1) - source_volume.size()
        max_pos = source_volume.max_corner
        return Cuboid(min_pos, max_pos).contains(dest)
