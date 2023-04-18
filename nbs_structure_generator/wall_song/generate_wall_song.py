import block_settings as blocks
from nbt_structure_utils import (
    BlockData,
    Cuboid,
    Inventory,
    ItemStack,
    NBTStructure,
    Vector,
)
from process_song import Channel, TickChannels

MAX_NOTES_IN_CHANNEL = 10


def generate_wall_song_nbt_structure(
    instruments: list[blocks.InstrumentBlock],
    channels: list[Channel],
    tickchannels: list[TickChannels],
    max_height: int = 384,
) -> NBTStructure:
    channel_count_1, channel_count_2 = determine_channel_counts(len(channels))
    ordered_channels = reorder_channels(channels)
    channels1 = ordered_channels[0:channel_count_1]
    channels2 = ordered_channels[channel_count_1:] if channel_count_2 > 0 else []

    # build layer by layer and structure by structure.
    structure1 = build_sequencer(instruments, channels1, tickchannels, True, max_height)
    place_starter(structure1)
    # listening zone
    curr_vol = Cuboid(Vector(0, 1, -1), Vector(6, 1, -3))
    structure1.fill_keep(curr_vol, blocks.floor_building)
    structure1.set_block(Vector(3, 1, -2), blocks.light_source)

    # if we needed the space, generate a 2nd one and place behind player listening spot.
    if any(channels2):
        offset = Vector(0, 0, -3 - len(channels2))
        structure2 = build_sequencer(
            instruments, channels2, tickchannels, False, max_height
        )
        structure1.clone_structure(structure2, offset)

    return structure1


def determine_channel_counts(total_channels: int) -> tuple[int, int]:
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


def reorder_channels(channels: list[Channel]) -> list[Channel]:
    working_channels = sorted(channels, key=len)
    ordered_channels = []
    while any(working_channels):
        ordered_channels.append(working_channels.pop(0))
        if any(working_channels):
            ordered_channels.append(working_channels.pop())
    return ordered_channels


def build_sequencer(
    instruments: list[blocks.InstrumentBlock],
    channels: list[Channel],
    tickchannels: TickChannels,
    is_south_half: bool,
    max_height: int,
) -> NBTStructure:
    structure = NBTStructure()
    build_base(structure, instruments, channels, is_south_half)
    encode_song(structure, channels, tickchannels, is_south_half, max_height)

    return structure


def build_base(
    structure: NBTStructure,
    instruments: list[blocks.InstrumentBlock],
    channels: list[Channel],
    is_south_half: bool,
) -> None:
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
        curr_block = (
            blocks.get_powered_rail("east_west") if z % 2 == 0 else blocks.redstone_wire
        )
        curr_vol = Cuboid(Vector(2, 1, z), Vector(6, 1, z))
        structure.fill(curr_vol, curr_block)
        structure.set_block(Vector(0, 3, z), curr_block)

    curr_vol = Cuboid(Vector(2, 2, 0), Vector(2, 2, max_z))
    structure.fill(curr_vol, blocks.get_observer("down"))
    curr_vol = Cuboid(Vector(1, 3, 0), Vector(1, 3, max_z))
    structure.fill(curr_vol, blocks.get_observer("west"))
    curr_vol = Cuboid(Vector(0, 4, 0), Vector(0, 4, max_z))
    structure.fill(curr_vol, blocks.get_observer("up"))
    curr_vol = Cuboid(Vector(6, 3, 0), Vector(6, 4, max_z))
    structure.fill(curr_vol, blocks.get_observer("up"))

    # fill in note blocks and floor around them
    for z, channel in enumerate(channels):
        build_chord(structure, instruments, channel, z)
    curr_vol = Cuboid(Vector(3, 2, 0), Vector(5, 2, max_z))
    structure.fill_keep(curr_vol, blocks.floor_building)

    bus_to_torch_towers(structure, max_z, is_south_half)


def build_chord(
    structure: NBTStructure,
    instruments: list[blocks.InstrumentBlock],
    channel: Channel,
    z: int,
) -> None:
    if len(channel) > MAX_NOTES_IN_CHANNEL:
        raise ValueError(
            "Can only support %i gravity blocks in a chord." % (MAX_NOTES_IN_CHANNEL)
        )

    instrument_blocks = [
        next(
            instr.copy_with_key(note.key)
            for instr in instruments
            if instr.id == note.block_id
        )
        for note in channel
    ]

    # sort list to have a solid block first
    instrument_blocks.sort(key=lambda n: (not n.transmits_redstone, n.id, n.key))
    # build all 1 note and some 2 note chords
    if len(channel) <= 2 and any(b for b in instrument_blocks if b.transmits_redstone):
        place_instrument(structure, Vector(2, 4, z), instrument_blocks.pop(0))
        if any(instrument_blocks):
            place_instrument(structure, Vector(3, 3, z), instrument_blocks.pop(0))
        return
    elif len(channel) == 1:
        structure.set_block(Vector(2, 3, z), blocks.redstone_solid_support)
        place_instrument(structure, Vector(3, 3, z), instrument_blocks.pop(0))
        return

    # fix 4th block, which is the only in design that can't use a gravity block
    skip_4th_block = False
    if len(instrument_blocks) >= 4 and instrument_blocks[3].gravity is True:
        index = next(
            (i for i, item in enumerate(instrument_blocks) if item.gravity is False), -1
        )
        if index == -1:
            skip_4th_block = True
            if len(channel) > MAX_NOTES_IN_CHANNEL - 1:
                raise ValueError(
                    "Can only support %i gravity blocks in a chord."
                    % (MAX_NOTES_IN_CHANNEL - 1)
                )
        else:
            instrument_blocks[index], instrument_blocks[3] = (
                instrument_blocks[3],
                instrument_blocks[index],
            )
    structure.set_block(Vector(2, 3, z), blocks.redstone_solid_support)
    structure.set_block(Vector(2, 4, z), blocks.redstone_wire_connecting)
    structure.set_block(Vector(3, 2, z), blocks.redstone_bus_trans)
    structure.set_block(Vector(3, 3, z), blocks.redstone_wire_connecting)
    # 1st
    place_instrument(structure, Vector(4, 3, z), instrument_blocks.pop(0))
    # 2nd
    place_instrument(structure, Vector(5, 3, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # bus wire
    structure.set_block(Vector(1, 4, z), blocks.redstone_bus_trans)
    structure.set_block(Vector(1, 5, z), blocks.redstone_wire_connecting)
    structure.set_block(Vector(2, 5, z), blocks.redstone_bus_trans)
    structure.set_block(Vector(2, 6, z), blocks.redstone_wire_connecting)
    # 3rd
    place_instrument(structure, Vector(3, 6, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # 4th
    if skip_4th_block is False:
        place_instrument(structure, Vector(4, 6, z), instrument_blocks.pop(0))
        if not any(instrument_blocks):
            return
    # bus wire
    structure.clone(Cuboid(Vector(1, 4, z), Vector(2, 5, z)), Vector(1, 6, z))
    structure.clone(Cuboid(Vector(1, 4, z), Vector(2, 5, z)), Vector(1, 8, z))
    structure.set_block(Vector(2, 10, z), blocks.redstone_wire_connecting)
    # 5th
    place_instrument(structure, Vector(3, 10, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # 6th
    place_instrument(structure, Vector(4, 10, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # bus wire
    structure.clone(Cuboid(Vector(1, 6, z), Vector(2, 9, z)), Vector(1, 10, z))
    structure.set_block(Vector(2, 14, z), blocks.redstone_wire_connecting)
    # 7th
    place_instrument(structure, Vector(3, 14, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # 8th
    place_instrument(structure, Vector(4, 14, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # bus wire
    structure.clone(Cuboid(Vector(1, 10, z), Vector(2, 13, z)), Vector(1, 14, z))
    structure.set_block(Vector(2, 18, z), blocks.redstone_wire_connecting)
    # 9th
    place_instrument(structure, Vector(3, 18, z), instrument_blocks.pop(0))
    if not any(instrument_blocks):
        return
    # 10th
    place_instrument(structure, Vector(4, 18, z), instrument_blocks.pop(0))


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
            nbt_s.set_block(curr_pos, blocks.redstone_bus_trans)


def bus_to_torch_towers(
    structure: NBTStructure, max_z: int, is_south_half: bool
) -> None:
    # bus signal to start of torch lines
    if max_z < 15:
        curr_vol = Cuboid(Vector(4, 19, -1), Vector(5, 19, -1))
        structure.fill(curr_vol, blocks.redstone_bus_torch)
        curr_vol = Cuboid(Vector(4, 20, -1), Vector(5, 20, -1))
        structure.fill(curr_vol, blocks.redstone_wire_connecting)
    else:
        # bus between torch towers
        curr_vol = Cuboid(Vector(5, 18, 0), Vector(5, 18, max_z))
        structure.fill(curr_vol, blocks.redstone_bus_trans)
        curr_vol = Cuboid(Vector(5, 19, 0), Vector(5, 19, max_z))
        structure.fill(curr_vol, blocks.redstone_wire_connecting)
        dir = "north" if is_south_half else "south"
        z_pos = (max_z + 3) // 3
        structure.set_block(Vector(5, 19, z_pos), blocks.get_repeater(dir, 1))
        structure.set_block(Vector(5, 19, z_pos * 2), blocks.get_repeater(dir, 1))
        # start of torch lines
        curr_vol = Cuboid(Vector(4, 19, max_z + 1), Vector(5, 19, max_z + 1))
        structure.fill(curr_vol, blocks.redstone_bus_torch)
        curr_vol = Cuboid(Vector(4, 20, max_z + 1), Vector(5, 20, max_z + 1))
        structure.fill(curr_vol, blocks.redstone_wire_connecting)
        curr_vol = Cuboid(Vector(4, 19, -1), Vector(5, 19, -1))
        structure.fill(curr_vol, blocks.redstone_bus_torch)
        curr_vol = Cuboid(Vector(4, 20, -1), Vector(5, 20, -1))
        structure.fill(curr_vol, blocks.redstone_wire_connecting)
        if is_south_half:
            structure.set_block(Vector(4, 20, -1), blocks.get_repeater("east", 2))
        else:
            structure.set_block(
                Vector(4, 20, max_z + 1), blocks.get_repeater("east", 2)
            )
            structure.set_block(Vector(4, 20, max_z + 3), blocks.air)


def place_starter(structure: NBTStructure) -> None:
    starter = NBTStructure()
    starter.set_block(Vector(0, 0, 0), blocks.get_button("stone", "south", "ceiling"))
    starter.set_block(Vector(0, 1, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(0, 2, 0), blocks.get_redstone_torch(True, None))
    starter.set_block(Vector(0, 3, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(0, 4, 0), blocks.get_redstone_torch(False, None))
    starter.set_block(Vector(0, 5, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(0, 6, 0), blocks.get_redstone_torch(True, None))
    starter.set_block(Vector(0, 7, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(0, 8, 0), blocks.get_redstone_torch(False, None))
    starter.set_block(Vector(0, 9, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(0, 10, 0), blocks.get_redstone_torch(True, None))
    starter.set_block(Vector(0, 11, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(0, 12, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(-1, 11, 0), blocks.get_sticky_piston("up"))
    starter.set_block(Vector(-1, 13, 0), blocks.get_observer("west"))
    starter.set_block(Vector(1, 11, 0), blocks.redstone_bus_trans)
    starter.set_block(Vector(2, 11, 0), blocks.redstone_bus_trans)
    starter.set_block(Vector(1, 12, 0), blocks.get_repeater("west", 2))
    starter.set_block(Vector(2, 12, 0), blocks.redstone_wire_connecting)

    starter.set_block(Vector(1, 8, 0), blocks.redstone_bus_start)
    starter.set_block(Vector(1, 9, 0), blocks.get_comparator("east", "compare"))
    starter.set_block(Vector(2, 9, 0), blocks.get_dropper("up"))
    inv = Inventory(
        "minecraft:dropper", [ItemStack("minecraft:wooden_sword", 1, 0, 0, [])]
    )
    starter.set_block(Vector(2, 10, 0), blocks.get_dropper("down"), inv)

    structure.clone_structure(starter, Vector(3, 7, -2))


def encode_song(
    structure: NBTStructure,
    channels: list[Channel],
    tickchannels: TickChannels,
    is_south_half: bool,
    max_height: int,
) -> None:
    """place pistons that will update walls"""
    channel_positions = get_channel_positions(channels)
    max_z = len(channels) - 1
    starting_height = 20
    repeating_blocks = get_piston_redstone_line(max_z, is_south_half)
    max_tick = max([t.tick for t in tickchannels])
    # fill middle section up to height, then add to sides to expand
    curr_tick = 0
    curr_y = starting_height
    while max_height >= (curr_y + 1) and max_tick >= curr_tick:
        structure.clone_structure(repeating_blocks, Vector(3, curr_y, 0))
        # on beat (even redstone tick)
        tick = next((item for item in tickchannels if item.tick == curr_tick), None)
        if tick is not None:
            place_pistons(
                structure,
                2,
                curr_y,  # yum
                tick.channels,
                channel_positions,
                blocks.get_piston("west"),
            )
        curr_tick += 1
        # on eighth (odd redstone tick)
        tick = next((item for item in tickchannels if item.tick == curr_tick), None)
        if tick is not None:
            place_pistons(
                structure,
                4,
                curr_y,
                tick.channels,
                channel_positions,
                blocks.get_piston("east"),
            )
        curr_tick += 1
        curr_y += 2

    # add walls and blocks that go next to walls
    wall_structure = get_wall(max_z, curr_y - 1)
    structure.clone_structure(wall_structure, Vector(0, 0, 0))
    structure.clone_structure(wall_structure, Vector(6, 0, 0))

    if curr_tick > max_tick:
        if is_south_half:
            place_downward_line(
                structure,
                Vector(6, 17, -2),
                curr_y - 1,
                blocks.redstone_bus_reset,
                False,
            )
            structure.set_block(
                Vector(4, curr_y - 1, -2), blocks.get_redstone_torch(False, "east")
            )
    else:
        downward_line_max_y = curr_y - 5
        if is_south_half:
            place_downward_line(
                structure,
                Vector(0, 21, -2),
                downward_line_max_y,
                blocks.redstone_bus_torch,
                True,
            )
            structure.set_block(
                Vector(4, downward_line_max_y, -2),
                blocks.get_redstone_torch(False, "east"),
            )
            place_downward_line(
                structure,
                Vector(6, 21, -2),
                downward_line_max_y,
                blocks.redstone_bus_torch,
                False,
            )
            structure.set_block(
                Vector(2, downward_line_max_y, -2),
                blocks.get_redstone_torch(False, "west"),
            )
        extend_song(
            structure,
            curr_tick,
            max_tick,
            tickchannels,
            channel_positions,
            is_south_half,
            starting_height,
            max_height,
            downward_line_max_y - 4,
            max_z,
            repeating_blocks,
            -3,
            9,
        )


# max_z is for wall blacks only and does not include the solid edges
def get_wall(max_z, height) -> NBTStructure:
    temp_structure = NBTStructure()
    curr_volume = Cuboid(Vector(0, 5, -1), Vector(0, height, -1))
    temp_structure.fill(curr_volume, blocks.neutral_building)
    curr_volume = Cuboid(Vector(0, 5, max_z), Vector(0, height, max_z + 1))
    temp_structure.fill(curr_volume, blocks.neutral_building)
    curr_volume = Cuboid(Vector(0, 5, 0), Vector(0, height - 1, max_z))
    temp_structure.fill(curr_volume, blocks.get_flat_wall(is_top=False, dir="north"))
    curr_volume = Cuboid(Vector(0, height, 0), Vector(0, height, max_z))
    temp_structure.fill(curr_volume, blocks.get_flat_wall(is_top=True, dir="north"))
    return temp_structure


def get_bottom_extender_east(max_z: int) -> NBTStructure:
    temp_structure = NBTStructure()
    curr_vol = Cuboid(Vector(0, 0, 0), Vector(4, 0, max_z))
    temp_structure.fill(curr_vol, blocks.redstone_solid_support)
    curr_vol = Cuboid(Vector(0, 1, 0), Vector(2, 1, max_z))
    temp_structure.fill(curr_vol, blocks.get_observer("east"))
    curr_vol = Cuboid(Vector(4, 2, 0), Vector(4, 2, max_z))
    temp_structure.fill(curr_vol, blocks.redstone_solid_support)
    curr_vol = Cuboid(Vector(4, 3, 0), Vector(4, 4, max_z))
    temp_structure.fill(curr_vol, blocks.get_observer("up"))
    for z in range(0, max_z + 1):
        curr_block = (
            blocks.get_powered_rail("east_west") if z % 2 == 0 else blocks.redstone_wire
        )
        curr_vol = Cuboid(Vector(2, 1, z), Vector(4, 1, z))
        temp_structure.fill(curr_vol, curr_block)
    return temp_structure


def get_bottom_extender_west(max_z: int) -> NBTStructure:
    temp_structure = NBTStructure()
    curr_vol = Cuboid(Vector(0, 0, 0), Vector(4, 0, max_z))
    temp_structure.fill(curr_vol, blocks.redstone_solid_support)
    curr_vol = Cuboid(Vector(3, 1, 0), Vector(4, 1, max_z))
    temp_structure.fill(curr_vol, blocks.get_observer("west"))
    curr_vol = Cuboid(Vector(0, 2, 0), Vector(0, 2, max_z))
    temp_structure.fill(curr_vol, blocks.get_observer("up"))
    for z in range(0, max_z + 1):
        curr_block = (
            blocks.get_powered_rail("east_west") if z % 2 == 0 else blocks.redstone_wire
        )
        curr_vol = Cuboid(Vector(0, 1, z), Vector(2, 1, z))
        temp_structure.fill(curr_vol, curr_block)
    return temp_structure


def extend_song(
    structure: NBTStructure,
    curr_tick: int,
    max_tick: int,
    tickchannels: TickChannels,
    channel_positions: dict[int, int],
    is_south_half: bool,
    starting_height: int,
    max_height: int,
    downward_line_max_y: int,
    max_channel_z: int,
    repeating_blocks: NBTStructure,
    x_west_center: int,
    x_east_center: int,
) -> None:
    west_wing = NBTStructure()  # on beat, even tick
    east_wing = NBTStructure()  # off beat, odd tick

    curr_y = starting_height
    while max_height >= (curr_y + 1) and max_tick >= curr_tick:
        west_wing.clone_structure(repeating_blocks, Vector(0, curr_y, 0))
        east_wing.clone_structure(repeating_blocks, Vector(0, curr_y, 0))
        # on beat (even redstone tick)
        tick = next((item for item in tickchannels if item.tick == curr_tick), None)
        if tick is not None:
            place_pistons(
                west_wing,
                1,
                curr_y,
                tick.channels,
                channel_positions,
                blocks.get_piston("east"),
            )
        curr_tick += 1
        # on eighth (odd redstone tick)
        tick = next((item for item in tickchannels if item.tick == curr_tick), None)
        if tick is not None:
            place_pistons(
                east_wing,
                -1,
                curr_y,
                tick.channels,
                channel_positions,
                blocks.get_piston("west"),
            )
        curr_tick += 1
        curr_y += 2
    bus_to_torch_towers_extended(
        west_wing, 2, starting_height, max_channel_z, is_south_half, False
    )
    bus_to_torch_towers_extended(
        east_wing, -2, starting_height, max_channel_z, is_south_half, True
    )

    structure.clone_structure(west_wing, Vector(x_west_center, 0, 0))
    structure.clone_structure(east_wing, Vector(x_east_center, 0, 0))

    if curr_tick > max_tick:
        if is_south_half:
            # place observer wire down to reset line
            y_top = ((curr_y - 20) // 2) + 20
            if y_top % 2 == 1:
                y_top -= 1
            pos_top = Vector(x_east_center - 1, y_top, -2)
            pos_bot = Vector(x_east_center - 1, 17, -2)
            structure.fill(Cuboid(pos_top, pos_bot), blocks.get_observer(facing="up"))
            pos_top.y += 1
            structure.set_block(pos_top, blocks.get_redstone_torch(False, "west"))
            pos_bot.y -= 1
            structure.set_block(pos_bot, blocks.redstone_bus_reset)
            pos_bot.x -= 1
            structure.set_block(pos_bot, blocks.redstone_wire_connecting)
            pos_bot.x -= 1
            structure.set_block(pos_bot, blocks.redstone_wire_connecting)
            pos_bot.y -= 1
            structure.set_block(pos_bot, blocks.redstone_bus_reset)
            pos_bot.x += 1
            structure.set_block(pos_bot, blocks.redstone_bus_reset)
    else:
        if is_south_half:
            # east
            place_downward_line(
                structure,
                Vector(x_east_center + 2, 21, -2),
                downward_line_max_y,
                blocks.redstone_bus_torch,
                True,
            )
            curr_pos = Vector(x_east_center, downward_line_max_y, -3)
            final_pos = Vector(x_east_center + 3, downward_line_max_y + 1, -3)
            curr_vol = Cuboid(curr_pos, final_pos)
            structure.fill(curr_vol, blocks.redstone_bus_torch)
            structure.set_block(curr_pos, blocks.get_redstone_torch("north", True))
            curr_pos.y += 1
            curr_pos.x += 1
            curr_vol = Cuboid(curr_pos, final_pos)
            structure.fill(curr_vol, blocks.redstone_wire_connecting)
            structure.set_block(curr_pos, blocks.get_repeater("west", 2))
            # reset line below
            pos1 = Vector(x_east_center - 3, 16, -2)
            pos2 = Vector(x_east_center + 1, 15, -2)
            structure.fill(Cuboid(pos1, pos2), blocks.redstone_bus_reset)
            pos1.x += 1
            pos2.y += 1
            structure.fill(Cuboid(pos1, pos2), blocks.redstone_wire_connecting)
            structure.set_block(pos1, blocks.get_repeater("east", 1))

            # west
            place_downward_line(
                structure,
                Vector(x_west_center - 2, 21, -2),
                downward_line_max_y,
                blocks.redstone_bus_torch,
                False,
            )
            curr_pos = Vector(x_west_center, downward_line_max_y, -3)
            final_pos = Vector(x_west_center - 3, downward_line_max_y + 1, -3)
            curr_vol = Cuboid(curr_pos, final_pos)
            structure.fill(curr_vol, blocks.redstone_bus_torch)
            structure.set_block(curr_pos, blocks.get_redstone_torch("north", True))
            curr_pos.y += 1
            curr_pos.x -= 1
            curr_vol = Cuboid(curr_pos, final_pos)
            structure.fill(curr_vol, blocks.redstone_wire_connecting)
            structure.set_block(curr_pos, blocks.get_repeater("east", 2))

        # place next wall + bussings
        wall_structure = get_wall(max_channel_z, curr_y - 1)
        structure.clone_structure(wall_structure, Vector(x_west_center - 2, 0, 0))
        structure.clone_structure(wall_structure, Vector(x_east_center + 2, 0, 0))
        east_bussing = get_bottom_extender_east(max_channel_z)
        structure.clone_structure(east_bussing, Vector(x_east_center - 2, 0, 0))
        west_bussing = get_bottom_extender_west(max_channel_z)
        structure.clone_structure(west_bussing, Vector(x_west_center - 2, 2, 0))

        # extend
        extend_song(
            structure,
            curr_tick,
            max_tick,
            tickchannels,
            channel_positions,
            is_south_half,
            starting_height,
            max_height,
            downward_line_max_y,
            max_channel_z,
            repeating_blocks,
            x_west_center - 5,
            x_east_center + 5,
        )


def bus_to_torch_towers_extended(
    structure: NBTStructure,
    x: int,
    y: int,
    max_z: int,
    is_south_half: bool,
    is_east_half: bool,
) -> None:
    # bus signal to start of torch lines

    if max_z < 15:
        structure.set_block(Vector(x, y - 1, -2), blocks.redstone_bus_torch)
        structure.set_block(Vector(x, y, -2), blocks.redstone_wire_connecting)
        structure.set_block(Vector(x, y - 1, -1), blocks.redstone_bus_torch)
        structure.set_block(Vector(x, y, -1), blocks.redstone_wire_connecting)
        if is_east_half:
            structure.set_block(Vector(x + 1, y - 1, -1), blocks.redstone_bus_torch)
            structure.set_block(Vector(x + 1, y, -1), blocks.get_repeater("west", 2))
            structure.set_block(Vector(x - 1, y + 2, -2), blocks.get_observer("up"))
        else:
            structure.set_block(Vector(x - 1, y - 1, -1), blocks.redstone_bus_torch)
            structure.set_block(Vector(x - 1, y, -1), blocks.get_repeater("east", 2))
            structure.set_block(Vector(x + 1, y + 2, -2), blocks.get_observer("up"))
    else:
        structure.set_block(Vector(x, y - 1, -1), blocks.redstone_bus_torch)
        structure.set_block(Vector(x, y, -1), blocks.redstone_wire_connecting)
        # bus between torch towers
        curr_vol = Cuboid(Vector(x, y - 2, 0), Vector(x, y - 2, max_z))
        structure.fill(curr_vol, blocks.redstone_bus_trans)
        curr_vol = Cuboid(Vector(x, y - 1, 0), Vector(x, y - 1, max_z))
        structure.fill(curr_vol, blocks.redstone_wire_connecting)
        dir = "north" if is_south_half else "south"
        z_pos = (max_z + 3) // 3
        structure.set_block(Vector(x, y - 1, z_pos), blocks.get_repeater(dir, 1))
        structure.set_block(Vector(x, y - 1, z_pos * 2), blocks.get_repeater(dir, 1))
        # start of torch lines
        if is_south_half:
            structure.set_block(Vector(x, y - 1, -2), blocks.redstone_bus_torch)
            structure.set_block(Vector(x, y, -2), blocks.redstone_wire_connecting)
        if is_east_half:
            structure.set_block(Vector(x + 1, y - 1, -1), blocks.redstone_bus_torch)
            if is_south_half:
                structure.set_block(
                    Vector(x + 1, y, -1), blocks.get_repeater("west", 2)
                )
                structure.set_block(Vector(x, y + 1, -2), blocks.get_observer("up"))
                structure.set_block(Vector(x - 1, y + 2, -2), blocks.get_observer("up"))
                structure.set_block(Vector(x, y + 2, -2), blocks.get_observer("west"))
            else:
                structure.set_block(
                    Vector(x + 1, y, -1), blocks.redstone_wire_connecting
                )
            curr_pos = Vector(x + 1, y - 1, max_z + 1)
            structure.set_block(curr_pos, blocks.redstone_bus_torch)
            curr_pos.x -= 1
            structure.set_block(curr_pos, blocks.redstone_bus_torch)
            curr_pos.y += 1
            structure.set_block(curr_pos, blocks.redstone_wire_connecting)
            curr_pos.x += 1
            if is_south_half:
                structure.set_block(curr_pos, blocks.redstone_wire_connecting)
            else:
                structure.set_block(curr_pos, blocks.get_repeater("west", 2))
                structure.set_block(Vector(x + 1, y, max_z + 3), blocks.air)
        else:
            structure.set_block(Vector(x - 1, y - 1, -1), blocks.redstone_bus_torch)
            if is_south_half:
                structure.set_block(
                    Vector(x - 1, y, -1), blocks.get_repeater("east", 2)
                )
                structure.set_block(Vector(x, y + 1, -2), blocks.get_observer("up"))
                structure.set_block(Vector(x + 1, y + 2, -2), blocks.get_observer("up"))
                structure.set_block(Vector(x, y + 2, -2), blocks.get_observer("east"))
            else:
                structure.set_block(
                    Vector(x - 1, y, -1), blocks.redstone_wire_connecting
                )
            curr_pos = Vector(x - 1, y - 1, max_z + 1)
            structure.set_block(curr_pos, blocks.redstone_bus_torch)
            curr_pos.x += 1
            structure.set_block(curr_pos, blocks.redstone_bus_torch)
            curr_pos.y += 1
            structure.set_block(curr_pos, blocks.redstone_wire_connecting)
            curr_pos.x -= 1
            if is_south_half:
                structure.set_block(curr_pos, blocks.redstone_wire_connecting)
            else:
                structure.set_block(curr_pos, blocks.get_repeater("east", 2))
                structure.set_block(Vector(x - 1, y, max_z + 3), blocks.air)


# goal: create list so we can input channel id as index, get back block's z
def get_channel_positions(channels: list[Channel]) -> dict[int, int]:
    channel_positions: dict[int, int] = {}
    for i in range(max(channel.id for channel in channels) + 1):
        pos = next((j for j, chan in enumerate(channels) if chan.id == i), None)
        channel_positions[i] = pos
    return channel_positions


def place_pistons(
    structure: NBTStructure,
    x: int,
    y: int,
    channels_to_place: list[int],
    channel_pos: dict,
    block: BlockData,
) -> None:
    for chan_id in channels_to_place:
        if channel_pos.get(chan_id, None) is not None:
            structure.set_block(Vector(x, y, channel_pos[chan_id]), block)


def get_piston_redstone_line(max_z: int, is_south_half: bool) -> NBTStructure:
    # main line
    p_structure = NBTStructure()
    curr_vol = Cuboid(Vector(0, 0, 0), Vector(0, 0, max_z))
    p_structure.fill(curr_vol, blocks.redstone_bus_main)
    curr_vol = Cuboid(Vector(0, 1, 0), Vector(0, 1, max_z))
    p_structure.fill(curr_vol, blocks.redstone_wire_connecting)
    # torch towers
    if is_south_half or max_z >= 15:
        p_structure.set_block(Vector(0, 0, -1), blocks.redstone_bus_torch)
        p_structure.set_block(
            Vector(0, 0, -2), blocks.get_redstone_torch(True, "north")
        )
        p_structure.set_block(Vector(0, 1, -2), blocks.redstone_bus_torch)
        p_structure.set_block(
            Vector(0, 1, -1), blocks.get_redstone_torch(False, "south")
        )
    if not is_south_half or max_z >= 15:
        p_structure.set_block(Vector(0, 0, max_z + 1), blocks.redstone_bus_torch)
        p_structure.set_block(
            Vector(0, 0, max_z + 2), blocks.get_redstone_torch(True, "south")
        )
        p_structure.set_block(Vector(0, 1, max_z + 2), blocks.redstone_bus_torch)
        p_structure.set_block(
            Vector(0, 1, max_z + 1), blocks.get_redstone_torch(False, "north")
        )
    return p_structure


def place_downward_line(
    structure: NBTStructure,
    observer_pos: Vector,
    max_y: int,
    bottom_block: BlockData,
    input_on_east: bool,
) -> None:
    structure.set_block(observer_pos, blocks.get_observer("up"))
    pos1 = observer_pos.copy()
    pos1.y -= 1
    structure.set_block(pos1, bottom_block)
    pos1.y += 2
    pos2 = observer_pos.copy()
    pos2.y = max_y
    curr_vol = Cuboid(pos1, pos2)
    structure.fill(curr_vol, blocks.get_flat_wall(is_top=False, dir="north"))
    structure.set_block(pos2, blocks.get_flat_wall(is_top=True, dir="north"))
    pos1.z -= 1
    pos2.z -= 1
    curr_vol = Cuboid(pos1, pos2)
    structure.fill(curr_vol, blocks.neutral_building)
    pos1.z += 2
    pos2.z += 2
    curr_vol = Cuboid(pos1, pos2)
    structure.fill(curr_vol, blocks.neutral_building)

    if input_on_east:
        curr_pos = Vector(observer_pos.x + 1, max_y, observer_pos.z)
        structure.set_block(curr_pos, blocks.get_trap_door("iron", "east", "top"))
    else:
        curr_pos = Vector(observer_pos.x - 1, max_y, observer_pos.z)
        structure.set_block(curr_pos, blocks.get_trap_door("iron", "west", "top"))
