from process_song import TickChannels, Channel
import nbt_structure_helper as nbth
import block_settings as blocks


class InstrumentBlockPhysics:
    id: int
    block_name: str
    gravity: bool
    transmits_redstone: bool

    def __init__(self, id, name, grav, reds) -> None:
        self.id = id
        self.block_name = name
        self.gravity = grav
        self.transmits_redstone = reds


def generate_wall_song_nbt_structure(
    save_to_path: str,
    filename: str,
    instruments: list[InstrumentBlockPhysics],
    tickchannels: list[TickChannels],
    channels: list[Channel],
    max_height: int = 384,
):
    piston_height_for_noise = 20

    # build layer by layer
    structure = nbth.StructureBlocks()
    build_base(structure, instruments, channels, piston_height_for_noise)
    encode_song(structure, tickchannels, max_height)
    structure.get_nbt().write_file(filename=save_to_path + filename)
    pass


# build section from bottom up to just before note encoding
def build_base(
    structure: nbth.StructureBlocks,
    instruments: list[InstrumentBlockPhysics],
    channels: list[Channel],
    piston_height: int,
):
    pass


def encode_song(
    structure: nbth.StructureBlocks, channels: list[Channel], max_height: int
):
    pass


# testing
if __name__ == "__main__":
    save_to_path = "./output/"
    filename = "tall1.nbt"
    structure = nbth.StructureBlocks()
    structure.set_block(nbth.Coordinate(0, 0, 0), blocks.floor_building)
    structure.set_block(nbth.Coordinate(0, 1, 0), blocks.light_source)
    structure.set_block(nbth.Coordinate(0, 383, 0), blocks.redstone_slab)
    structure.get_nbt().write_file(filename=save_to_path + filename)
