from process_song import TickChannels, Channel
import nbt_helper.nbt_structure_helper as nbth
from nbt_helper.plot_helpers import Vector, Cuboid
import block_settings as blocks


class InstrumentBlock:
    id: int
    instrument: str
    block_data: nbth.BlockData
    gravity: bool
    transmits_redstone: bool

    def __init__(self, id, name, block, grav, reds) -> None:
        self.id = id
        self.instrument = name
        self.block_data = block
        self.gravity = grav
        self.transmits_redstone = reds

    def get_note_block(self, key: int):
        nb = blocks.note_block.copy()
        nb.properties = [("instrument", self.instrument), ("note", key)]
        return nb


def generate_wall_song_nbt_structure(
    save_to_path: str,
    filename: str,
    instruments: list[InstrumentBlock],
    channels: list[Channel],
    tickchannels: list[TickChannels],
    max_height: int = 384,
):
    piston_height_for_noise = 20
    channel_count_1, channel_count_2 = determine_channel_counts(len(channels))
    ordered_channels = reorder_channels(channels)
    channels1 = ordered_channels[0:channel_count_1]
    channels2 = ordered_channels[channel_count_1 + 1 :] if channel_count_2 > 0 else []

    # build layer by layer and structure by structure.
    structure1 = build_sequencer(
        instruments, channels1, tickchannels, piston_height_for_noise, max_height
    )
    set_up_controls(structure1, piston_height_for_noise)

    # if we needed the space, generate a 2nd 1 and place behind player listening spot.
    if False and any(channels2):
        structure2 = build_sequencer(
            instruments, channels2, piston_height_for_noise, max_height
        )
        offset = nbth.Vector(0, 0, 0)
        structure1.clone_structure(structure2, offset)

    structure1.get_nbt(fill_void_with_air=False).write_file(
        filename=save_to_path + filename
    )


def determine_channel_counts(total_channels: int):
    max_channels_per_side = 30
    channel_count_1 = total_channels
    channel_count_2 = 0
    if channel_count_1 > max_channels_per_side * 2:
        raise ValueError(
            "Max channel count is %i but %i were parsed from song." % (channel_count_1)
        )
    if channel_count_1 > max_channels_per_side:
        channel_count_2 = channel_count_1 // 2
        channel_count_1 -= channel_count_2
    return channel_count_1, channel_count_2


def reorder_channels(channels: list[Channel]):
    working_channels = sorted(channels, key=len)
    ordered_channels = []
    while any(working_channels):
        ordered_channels.append(working_channels.pop(0))
        if any(working_channels):
            ordered_channels.append(working_channels.pop())
    return ordered_channels


def build_sequencer(
    instruments: list[InstrumentBlock],
    channels: list[Channel],
    tickchannels: TickChannels,
    piston_height: int,
    max_height: int,
) -> nbth.StructureBlocks:
    structure = nbth.StructureBlocks()
    build_base(structure, instruments, channels, piston_height)
    encode_song(structure, tickchannels, max_height)

    return structure


def build_base(
    structure: nbth.StructureBlocks,
    instruments: list[InstrumentBlock],
    channels: list[Channel],
    piston_height: int,
):
    """build section from bottom up to just before note encoding"""
    # layers 0 - 4 without note blocks. align 1st channel's walls with 0,y,0
    max_z = len(channels) - 1
    curr_block = blocks.redstone_solid_support
    curr_vol = Cuboid(Vector(2, 0, 0), Vector(6, 0, max_z))
    structure.fill(curr_vol, curr_block)
    curr_vol = Cuboid(Vector(0, 2, 0), Vector(0, 2, max_z))
    structure.fill(curr_vol, curr_block)
    curr_vol = Cuboid(Vector(6, 2, 0), Vector(6, 2, max_z))
    structure.fill(curr_vol, curr_block)

    for z in range(0, max_z + 1):
        curr_block = blocks.observer_wire_alt if z % 2 == 0 else blocks.redstone_wire
        curr_vol = Cuboid(Vector(2, 1, z), Vector(6, 1, z))
        structure.fill(curr_vol, curr_block)
        structure.set_block(Vector(0, 3, z), curr_block)

    curr_vol = Cuboid(Vector(2, 2, 0), Vector(2, 2, max_z))
    structure.fill(curr_vol, blocks.observer_down)
    curr_vol = Cuboid(Vector(1, 3, 0), Vector(1, 3, max_z))
    structure.fill(curr_vol, blocks.observer_west)
    curr_vol = Cuboid(Vector(0, 4, 0), Vector(0, 4, max_z))
    structure.fill(curr_vol, blocks.observer_up)
    curr_vol = Cuboid(Vector(6, 3, 0), Vector(6, 4, max_z))
    structure.fill(curr_vol, blocks.observer_up)

    for z, channel in enumerate(channels):
        build_chord(structure, instruments, channel, z)


def build_chord(
    structure: nbth.StructureBlocks,
    instruments: list[InstrumentBlock],
    channel: Channel,
    z: int,
):
    notes_in_chord = []
    for note in channel:
        instr = next(i for i in instruments if i.id == note.block_id)
        notes_in_chord.append((instr, note.key))

    if len(channel) <= 2 and any(b for b in notes_in_chord if b[0].transmits_redstone):
        notes_in_chord.sort(key=lambda n: n[0].transmits_redstone)
        block = notes_in_chord.pop(0)
        structure.set_block(Vector(2, 3, z), block[0].block_data)
        structure.set_block(Vector(2, 4, z), block[0].get_note_block(block[1]))
        if any(notes_in_chord):
            block = notes_in_chord.pop(0)
            structure.set_block(Vector(3, 2, z), block[0].block_data)
            structure.set_block(Vector(3, 3, z), block[0].get_note_block(block[1]))
    else: # build big chord
        pass
    


def encode_song(
    structure: nbth.StructureBlocks, channels: list[Channel], max_height: int
):
    """place pistons that will activate walls"""
    pass


def set_up_controls(structure: nbth.StructureBlocks, piston_height: int):
    """feed redstone signals from start, to each segment, and back to start"""
    pass
