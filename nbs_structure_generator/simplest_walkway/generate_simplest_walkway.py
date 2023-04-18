import block_settings as blocks
import pynbs
from nbt_structure_utils import Cuboid, NBTStructure, Vector


def generate_simplest_walkway_nbt_structure(
    song_path: str,
    instruments: list[blocks.InstrumentBlock],
    walkway_option: str = None,
) -> NBTStructure:
    simple = NBTStructure()
    curr_pos = Vector(0, 0, 0)

    t_curr = 0
    song = pynbs.read(song_path)
    for tick, chord in song:
        while t_curr < tick:
            simple.set_block(curr_pos, blocks.redstone_bus_main)
            simple.set_block(
                curr_pos + Vector(0, 1, 0), blocks.get_observer(facing="west")
            )
            place_walkway(simple, curr_pos, walkway_option)
            curr_pos.x += 1
            t_curr += 1
        simple.set_block(curr_pos, blocks.redstone_bus_main)
        place_walkway(simple, curr_pos, walkway_option)
        place_chord(simple, curr_pos, chord, instruments, walkway_option)
        t_curr += 1
        curr_pos.x += 1

    return simple


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
    walkway_option: str,
) -> None:
    nbt_s.set_block(pos + Vector(0, 1, 0), blocks.get_observer(facing="west"))
    instrument_blocks = [
        next(i for i in instruments if i.id == n.instrument).copy_with_key(n.key - 33)
        for n in chord
    ]
    reorder_chord(instrument_blocks)
    for i, instr in enumerate(instrument_blocks):
        i_mod = i % 6
        if i_mod == 0:
            if i > 0:
                pos.x += 1
                nbt_s.set_block(pos, blocks.redstone_bus_main)
                nbt_s.set_block(pos + Vector(0, 1, 0), blocks.redstone_wire_connecting)
                place_walkway(nbt_s, pos, walkway_option)

            nbt_s.set_block(pos + Vector(0, 1, -2), blocks.redstone_bus_secondary)
            nbt_s.set_block(pos + Vector(0, 1, -1), blocks.get_observer("south"))
            place_instrument(nbt_s, pos + Vector(0, 1, -3), instr)
        if i_mod == 1:
            place_instrument(nbt_s, pos + Vector(0, 2, -2), instr)
        if i_mod == 2:
            nbt_s.set_block(pos + Vector(0, 3, 0), blocks.lamp)
            nbt_s.set_block(pos + Vector(0, 2, 0), blocks.get_observer("down"))
            place_instrument(nbt_s, pos + Vector(0, 3, -1), instr)
        if i_mod == 3:
            place_instrument(nbt_s, pos + Vector(0, 3, 1), instr)
        if i_mod == 4:
            nbt_s.set_block(pos + Vector(0, 1, 2), blocks.redstone_bus_secondary)
            nbt_s.set_block(pos + Vector(0, 1, 1), blocks.get_observer("north"))
            place_instrument(nbt_s, pos + Vector(0, 2, 2), instr)
        if i_mod == 5:
            place_instrument(nbt_s, pos + Vector(0, 1, 3), instr)


# 2nd and 5th instruments in each group of 6 must use solid blocks.
def reorder_chord(blocks: list[blocks.InstrumentBlock]) -> list[blocks.InstrumentBlock]:
    bad = next(
        (
            i
            for i, instr in enumerate(blocks)
            if i % 6 in [1, 4] and not instr.transmits_redstone
        ),
        None,
    )
    while bad is not None:
        good = next(
            (
                j
                for j, instr in enumerate(blocks)
                if j % 6 not in [1, 4] and instr.transmits_redstone
            ),
            None,
        )
        if good is None:
            blocks.insert(bad, None)
        else:
            blocks[bad], blocks[good] = blocks[good], blocks[bad]
        bad = next(
            (
                i
                for i, instr in enumerate(blocks)
                if i % 6 in [1, 4] and not instr.transmits_redstone
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
