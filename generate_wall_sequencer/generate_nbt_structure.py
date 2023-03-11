from process_song import TickChannels, Channel


class Block:
    id: int
    block_name: str
    gravity: bool
    transmits_redstone: bool

    def __init__(self, id, name, grav, reds) -> None:
        self.id = id
        self.block_name = name
        self.gravity = grav
        self.transmits_redstone = reds


def generate_nbt_structure(
    save_to_path: str,
    instruments: list[Block],
    tickchannels: list[TickChannels],
    channels: list[Channel],
    max_height: int = 380,
):
    pass
