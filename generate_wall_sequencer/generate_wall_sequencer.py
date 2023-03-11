import pynbs
from vanilla_noteblock import * 

#todo: actually generate nbt structure(s)
def generate_wall_sequencer() -> None:
    channels, tickchannels = process_song('songs/VengaBus.nbs')
    for tick in tickchannels:
        print(tick)
    for channel in channels:
        print(channel)
    #get_nbt_structure(tickchannels, channels)
    
# get channels that need to be activated for each tick of song
def process_song(songpath: str):
    song = pynbs.read(songpath)
    all_channels = get_channels(song)
    ticks = []
    for tick, chord in song:
        v_chord = VanillaChord.create_from_nbs_chord(chord)
        channels_on_tick = TickChannels.get_channels(all_channels, v_chord)
        ticks.append(TickChannels(tick, channels_on_tick))
    return all_channels, ticks
        
def get_distinct_chords(song):
    distinct_chords = [] #instrument, key
    for _, chord in song:
        note_list = VanillaChord.create_from_nbs_chord(chord)
        if not any(x == note_list for x in distinct_chords):
            distinct_chords.append(note_list)
    return distinct_chords

def get_channels(song):
    channels = []
    chords_working_list = get_distinct_chords(song)
    chords_working_list.sort()
    # by using smallest chords, remove notes from larger chords
    while len(chords_working_list) > 0:
        chord = chords_working_list.pop(0)
        if (len(chord) > 0):
            channels.append(Channel(len(channels),chord))
            for working_chord in chords_working_list:
                if working_chord.contains(chord):
                    working_chord.removenotes(chord.notes)
        chords_working_list.sort()
            
    return reorder_channels(channels)

#todo: for  chords with 3+ notes and nonsolid blocks, we need space. place single note chords between them
def reorder_channels(channels):
    return channels

generate_wall_sequencer()
