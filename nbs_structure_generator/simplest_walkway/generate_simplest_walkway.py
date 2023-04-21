import block_settings as blocks
import pynbs
from nbt_structure_utils import Cuboid, NBTStructure, Vector
from tqdm import tqdm


def generate_simplest_walkway_nbt_structure(
    song_path: str,
    instruments: list[blocks.InstrumentBlock],
    song_tps: int = 10,
    tileable_width: int = 7,
    walkway_option: str = None,
) -> NBTStructure:
    if song_tps == 10:
        tick_delay = 1
    elif song_tps == 5:
        tick_delay = 2
    else:
        raise ValueError("song_tps must be 5 or 10")
    if not (2 <= tileable_width <= 7):
        raise ValueError("tileable_width must be at least 2 and at most 7.")
    simple = NBTStructure()
    curr_pos = Vector(0, 0, 0)
    t_curr = 0
    song = pynbs.read(song_path)
    for tick, chord in song:
        while t_curr < tick:
            simple.set_block(curr_pos, blocks.redstone_bus_main)
            simple.set_block(curr_pos + Vector(0, 1, 0), get_delay_block(tick_delay))
            place_walkway(simple, curr_pos, walkway_option)
            curr_pos.x += 1
            t_curr += 1
        simple.set_block(curr_pos, blocks.redstone_bus_main)
        place_walkway(simple, curr_pos, walkway_option)
        place_chord(
            simple,
            curr_pos,
            chord,
            instruments,
            tileable_width - 1,
            tick_delay,
            walkway_option,
        )
        t_curr += 1
        curr_pos.x += 1

    return simple


def generate_simplest_segments(
    song_path: str,
    instruments: "list[blocks.InstrumentBlock]",
    song_tps: int = 10,
    tileable_width: int = 7,
    segment_length: int = 32,
    walkway_option: str = None,
) -> "list[NBTStructure]":
    if song_tps == 10:
        tick_delay = 1
    elif song_tps == 5:
        tick_delay = 2
    else:
        raise ValueError("song_tps must be 5 or 10")
    if not (3 <= tileable_width <= 7):
        raise ValueError("tileable_width must be at least 3 and at most 7.")
    simple = NBTStructure()
    simple_segments = []
    segment_volume = Cuboid(Vector(0, -1, -3), Vector(segment_length - 1, 4, 3))
    curr_pos = Vector(0, 0, 0)
    t_curr = 0
    song = pynbs.read(song_path)
    for tick, chord in tqdm(song):
        while t_curr < tick:
            simple.set_block(curr_pos, blocks.redstone_bus_main)
            simple.set_block(curr_pos + Vector(0, 1, 0), get_delay_block(tick_delay))
            place_walkway(simple, curr_pos, walkway_option)
            curr_pos.x += 1
            t_curr += 1
        simple.set_block(curr_pos, blocks.redstone_bus_main)
        place_walkway(simple, curr_pos, walkway_option)
        place_chord(
            simple,
            curr_pos,
            chord,
            instruments,
            tileable_width - 1,
            tick_delay,
            walkway_option,
        )
        t_curr += 1
        curr_pos.x += 1
        if curr_pos.x >= segment_length:
            simple_segments.append(simple.copy(segment_volume))
            simple.fill(segment_volume, None)
            simple.translate(Vector(-segment_length, 0, 0))
            curr_pos.x -= segment_length
    if any(simple.blocks):
        simple_segments.append(simple.copy(segment_volume))
    return simple_segments


def get_delay_block(tick_delay, use_observer=False) -> blocks.BlockData:
    if use_observer and tick_delay == 1:
        return blocks.get_observer(facing="west")
    else:
        return blocks.get_repeater(facing="west", delay=tick_delay)


def place_walkway(nbt_s: NBTStructure, anchor_pos: Vector, option: str) -> None:
    if option == "boat":
        place_boatway(nbt_s, anchor_pos)
    if option == "horse":
        place_horseway(nbt_s, anchor_pos)


def place_boatway(nbt_s: NBTStructure, anchor_pos: Vector) -> None:
    nbt_s.set_block(anchor_pos + Vector(0, 5, 0), blocks.packed_ice)
    wall_block = blocks.get_flat_wall(is_top=True, dir="e")
    nbt_s.set_block(anchor_pos + Vector(0, 6, 2), wall_block)
    nbt_s.set_block(anchor_pos + Vector(0, 6, -2), wall_block)


# you need a fast horse with speed 2 to keep up with 10tps
def place_horseway(nbt_s: NBTStructure, anchor_pos: Vector) -> None:
    nbt_s.fill(
        Cuboid(
            anchor_pos + Vector(0, 5, -1),
            anchor_pos + Vector(0, 5, 1),
        ),
        blocks.building_floor,
    )
    wall_block = blocks.get_flat_wall(blocks.wall_material, True, "e")
    nbt_s.set_block(anchor_pos + Vector(0, 6, 2), wall_block)
    nbt_s.set_block(anchor_pos + Vector(0, 6, -2), wall_block)


def place_chord(
    nbt_s: NBTStructure,
    pos: Vector,
    chord: list[pynbs.Note],
    instruments: list[blocks.InstrumentBlock],
    max_notes_per_meter: int,
    tick_delay: int,
    walkway_option: str,
) -> None:
    nbt_s.set_block(pos + Vector(0, 1, 0), get_delay_block(tick_delay))
    instrument_blocks = [
        next(i for i in instruments if i.id == n.instrument).copy_with_key(n.key - 33)
        for n in chord
    ]
    reorder_chord(instrument_blocks, max_notes_per_meter)
    for i, instr in enumerate(instrument_blocks):
        i_mod = i % max_notes_per_meter
        if i_mod == 0:
            # too many notes, expand
            if i > 0:
                pos.x += 1
                nbt_s.set_block(pos, blocks.redstone_bus_main)
                nbt_s.set_block(pos + Vector(0, 1, 0), blocks.redstone_wire_connecting)
                place_walkway(nbt_s, pos, walkway_option)
            nbt_s.set_block(pos + Vector(0, 3, 0), blocks.redstone_bus_secondary)
            nbt_s.set_block(pos + Vector(0, 2, 0), blocks.get_observer("down"))
            place_instrument(nbt_s, pos + Vector(0, 3, 1), instr)
        if i_mod == 1:
            place_instrument(nbt_s, pos + Vector(0, 3, -1), instr)
        if i_mod == 2:
            nbt_s.set_block(pos + Vector(0, 1, -2), blocks.redstone_bus_secondary)
            nbt_s.set_block(pos + Vector(0, 1, -1), blocks.get_observer("south"))
            place_instrument(nbt_s, pos + Vector(0, 2, -2), instr)
        if i_mod == 3:
            place_instrument(nbt_s, pos + Vector(0, 1, -3), instr)
        if i_mod == 4:
            nbt_s.set_block(pos + Vector(0, 1, 2), blocks.redstone_bus_secondary)
            nbt_s.set_block(pos + Vector(0, 1, 1), blocks.get_observer("north"))
            place_instrument(nbt_s, pos + Vector(0, 2, 2), instr)
        if i_mod == 5:
            place_instrument(nbt_s, pos + Vector(0, 1, 3), instr)


# make sure instruments for middle y value use solid blocks.
def reorder_chord(
    blocks: list[blocks.InstrumentBlock], max_notes_per_meter: int
) -> list[blocks.InstrumentBlock]:
    must_be_solid = [2, 4]
    bad = next(
        (
            b
            for b, instr in enumerate(blocks)
            if b % max_notes_per_meter in must_be_solid and not instr.transmits_redstone
        ),
        None,
    )
    while bad is not None:
        good = next(
            (
                g
                for g, instr in enumerate(blocks)
                if g % max_notes_per_meter not in must_be_solid
                and instr.transmits_redstone
            ),
            None,
        )
        if good is None:
            blocks.insert(bad, None)
        else:
            blocks[bad], blocks[good] = blocks[good], blocks[bad]
        bad = next(
            (
                b
                for b, instr in enumerate(blocks)
                if b % max_notes_per_meter in must_be_solid
                and not instr.transmits_redstone
            ),
            None,
        )


def place_instrument(
    nbt_s: NBTStructure,
    note_block_pos: Vector,
    block_info: blocks.InstrumentBlock,
) -> None:
    if block_info is not None:
        curr_pos = note_block_pos.copy()
        curr_pos.y += 1
        nbt_s.set_block(curr_pos, blocks.air)
        curr_pos.y -= 1
        nbt_s.set_block(curr_pos, block_info.get_note_block())
        curr_pos.y -= 1
        nbt_s.set_block(curr_pos, block_info.block_data)
        curr_pos.y -= 1
        if block_info.gravity and nbt_s.get_block_state(curr_pos) is None:
            nbt_s.set_block(curr_pos, blocks.sand_support)
