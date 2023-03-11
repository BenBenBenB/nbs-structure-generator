from process_song import process_song
from generate_nbt_structure import generate_nbt_structure

#todo: actually generate nbt structure(s)
def generate_wall_sequencer() -> None:
    nbs_file_path = 'songs/VengaBus.nbs'
    save_to_path = 'output/wall.nbt'
    channels, tickchannels = process_song(nbs_file_path)
    for tick in tickchannels:
        print(tick)
    for channel in channels:
        print(channel)
    generate_nbt_structure(tickchannels, channels, save_to_path)

generate_wall_sequencer()
