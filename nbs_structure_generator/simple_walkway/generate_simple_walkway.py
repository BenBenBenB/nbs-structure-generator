import os
import sys

from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import block_settings as blocks
from nbt_structure_utils import Cuboid, NBTStructure, Vector
from simplest_walkway.generate_simplest_walkway import (
    generate_simplest_segments,
)

MAX_DIST_FROM_PATH = 24
TILABLE_HEIGHT = 4
structure_cache: dict[str, NBTStructure] = {}  # for cloning prebuilt structures


def generate_simple_walkway_nbt_structure(
    song_path: str,
    instruments: list[blocks.InstrumentBlock],
    song_tps=10,
    max_height: int = 30,
    tileable_width=7,
    walkway_option: str = None,
) -> NBTStructure:
    if not (3 <= tileable_width <= 7):
        raise ValueError("tileable_width must be at least 2 and at most 7.")
    preload_structures()
    main_structure = NBTStructure()
    segments = generate_simplest_segments(
        song_path, instruments, song_tps, tileable_width, MAX_DIST_FROM_PATH, None
    )
    place_song(main_structure, segments, tileable_width, max_height)
    place_walkway(main_structure, walkway_option)
    return main_structure


def preload_structures() -> None:
    pdir = os.path.dirname(__file__)
    structure_cache["bus_down_east"] = NBTStructure(
        os.path.join(pdir, "prebuilt_nbt/bus_down_east.nbt")
    )
    structure_cache["bus_down_west"] = NBTStructure(
        os.path.join(pdir, "prebuilt_nbt/bus_down_west.nbt")
    )
    structure_cache["bus_up"] = NBTStructure(
        os.path.join(pdir, "prebuilt_nbt/bus_up.nbt")
    )

    structure_cache["bus_down_west"].translate(Vector(-1, -4, -1))
    structure_cache["bus_down_east"].translate(Vector(0, -4, -1))
    structure_cache["bus_up"].translate(Vector(0, 0, -2))


def place_song(
    main_structure: NBTStructure,
    segments: "list[NBTStructure]",
    tileable_width: int,
    max_height: int,
) -> None:
    seg_start = Vector(0, 0, 0)
    prev_seg_start = None
    for song_segment in tqdm(segments):
        if seg_start.x > 0:
            song_segment.reflect(Vector(0, None, None))
        # 5 wide design needs to be reversed to prevent early note activations
        add_back_z = False
        if tileable_width == 6 and (seg_start.z / tileable_width) % 2 == 1:
            seg_start.z -= 1
            add_back_z = True
            song_segment.reflect(Vector(None, None, 0))

        main_structure.clone_structure(song_segment, seg_start)
        if prev_seg_start is not None:
            link_segments(main_structure, prev_seg_start, seg_start)

        seg_start, prev_seg_start = get_next_seg_start(
            prev_seg_start, seg_start, max_height, tileable_width
        )
        if add_back_z:
            seg_start.z += 1


def link_segments(
    main_structure: NBTStructure, prev_seg_start: Vector, seg_start: Vector
) -> None:
    bus_start_pos = Vector(
        x=seg_start.x + 1 if seg_start.x > 0 else seg_start.x - 1,
        y=prev_seg_start.y,
        z=prev_seg_start.z,
    )
    bus_end_pos = seg_start.copy()
    bus_end_pos.x = bus_start_pos.x
    if bus_start_pos.y == bus_end_pos.y:
        vol = Cuboid(bus_start_pos, bus_end_pos)
        main_structure.fill(vol, blocks.redstone_bus_main)
        vol.translate(Vector(0, 1, 0))
        main_structure.set_block(vol.min_corner, blocks.redstone_wire_connecting)
        main_structure.set_block(vol.max_corner, blocks.redstone_wire_connecting)
        vol.min_corner.z += 1
        vol.max_corner.z -= 1
        vol.translate(Vector(0, -1, 0))
        main_structure.fill(vol, blocks.redstone_wire_connecting)
        vol.translate(Vector(0, -1, 0))
        main_structure.fill(vol, blocks.redstone_bus_trans)

    elif bus_start_pos.y < bus_end_pos.y:
        main_structure.clone_structure(structure_cache["bus_up"], bus_start_pos)
    else:
        structure_name = "bus_down_east" if bus_start_pos.x > 0 else "bus_down_west"
        main_structure.clone_structure(structure_cache[structure_name], bus_start_pos)


def get_next_seg_start(
    prev: Vector, curr: Vector, max_height: int, tilable_width: int
) -> tuple("Vector, Vector"):
    if prev is None:
        # first time, guide it to go up or right
        prev = Vector(0, -1, 0)

    next_pos = curr.copy()
    next_pos.x = MAX_DIST_FROM_PATH - 1 if curr.x == 0 else 0
    if curr.y > prev.y:
        # moved up last time, go up or right
        if curr.y + 2 * TILABLE_HEIGHT < max_height:
            # move in +y
            next_pos.y += TILABLE_HEIGHT
        else:
            # move in +z
            next_pos.z += tilable_width
    elif curr.y < prev.y:
        # moved down last time, go right or down
        if curr.y == 0:
            # move in +z
            next_pos.z += tilable_width
        else:
            # move in -y
            next_pos.y -= TILABLE_HEIGHT
    elif curr.y == prev.y:
        # moved right last time, go down, up or right
        if curr.y > 0:
            # move in -y
            next_pos.y -= TILABLE_HEIGHT
        elif 2 * TILABLE_HEIGHT < max_height:
            # move in +y
            next_pos.y += TILABLE_HEIGHT
        else:
            # move in +z
            next_pos.z += tilable_width

    return next_pos, curr


def place_walkway(nbt_s: NBTStructure, option: str) -> None:
    place_path(nbt_s, Vector(0, 0, 0))
    if option == "minecart":
        place_track(nbt_s)


def place_path(nbt_s: NBTStructure, anchor_pos: Vector) -> None:
    pass


def place_track(nbt_s, anchor_pos) -> None:
    pass
