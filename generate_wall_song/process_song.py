import pynbs


# get channels that need to be activated for each tick of song
def process_song(songpath: str):
    song = pynbs.read(songpath)
    all_channels = get_channels(song)
    ticks = []
    for tick, chord in song:
        v_chord = VanillaChord.create_from_nbs_chord(
            [note for note in chord if note.instrument <= 15 and 33 <= note.key <= 57]
        )
        channels_on_tick = get_channels_in_chord(all_channels, v_chord)
        ticks.append(TickChannels(tick, channels_on_tick))
    return all_channels, ticks


def get_distinct_chords(song: pynbs.File):
    distinct_chords = []  # instrument, key
    for _, chord in song:
        v_chord = VanillaChord.create_from_nbs_chord(
            [note for note in chord if note.instrument <= 15 and 33 <= note.key <= 57]
        )
        if not any(x == v_chord for x in distinct_chords):
            distinct_chords.append(v_chord)
    return distinct_chords


def get_channels(song: pynbs.File):
    channels = []
    chords_working_list = get_distinct_chords(song)
    chords_working_list.sort()
    # by using smallest chords, remove notes from larger chords
    while len(chords_working_list) > 0:
        chord = chords_working_list.pop(0)
        if len(chord) > 0:
            channels.append(Channel(len(channels), chord))
            for working_chord in chords_working_list:
                if working_chord.contains(chord):
                    working_chord.removenotes(chord)
        chords_working_list.sort()
    return channels


# todo: for  chords with 3+ notes and nonsolid blocks, we need space. place single note chords between them
# perhaps handle in nbt side of code
def reorder_channels(channels):
    return channels


class VanillaNote:
    block_id: int  # 0-15, block to be placed under note block
    key: int  # 0-23
    # isVanilla: bool

    def __init__(self, instrument: int, key: int) -> None:
        self.block_id = instrument
        self.key = key

    def __repr__(self) -> str:
        return "(%i, %i)" % (self.block_id, self.key)

    def __eq__(self, __o: object):
        return self.key == __o.key and self.block_id == __o.block_id

    def __lt__(self, __o: object):
        if __o is None:
            return False
        if self.block_id != __o.block_id:
            return self.block_id < __o.block_id
        else:
            return self.key < __o.key

    @staticmethod
    def create_from_nbs_note(note: pynbs.Note):
        return VanillaNote(note.instrument, note.key - 33)


class VanillaChord:
    notes: list[VanillaNote]

    def __init__(self, notes) -> None:
        self.notes = notes

    def __iter__(self):
        return iter(self.notes)

    def __repr__(self):
        return str(self.notes)

    def __len__(self):
        return len(self.notes)

    def __lt__(self, __o: object):
        if len(self) != len(__o):
            return len(self) < len(__o)
        if any(self) and any(__o):
            return min(self) < min(__o)
        else:
            return False

    def __eq__(self, __o: object):
        return len(self) == len(__o) and self.contains(__o)

    def contains(self, note_search: "VanillaChord | list[VanillaNote]") -> bool:
        working_copy_notes = self.copy()
        for note in note_search:
            if note not in working_copy_notes:
                return False
            working_copy_notes.remove(note)
        return True

    def copy(self) -> "VanillaChord":
        return VanillaChord(self.notes.copy())

    def remove(self, note: VanillaNote) -> None:
        self.notes.remove(note)

    def removenotes(self, chord: "VanillaChord | list[VanillaNote]") -> None:
        for note in chord:
            self.remove(note)

    @staticmethod
    def create_from_nbs_chord(chord: list[pynbs.Note]) -> "VanillaChord":
        new_chord = []
        for note in chord:
            new_chord.append(VanillaNote.create_from_nbs_note(note))
        return VanillaChord(new_chord)


class Channel:
    id: int
    chord: VanillaChord

    def __init__(self, id, notes) -> None:
        self.id = id
        self.chord = notes

    def __iter__(self):
        return iter(self.chord)

    def __repr__(self):
        return "%i, %s" % (self.id, self.chord)

    def __lt__(self, __o: object):
        return self.chord < __o.chord

    def __len__(self):
        return len(self.chord)


# Stores list of all channels that should play on a given tick
class TickChannels:
    tick: int
    channels: list[int]

    def __init__(self, tick, channel_ids) -> None:
        self.tick = tick
        self.channels = channel_ids

    def __iter__(self):
        return iter(self.channels)

    def __repr__(self):
        return "%i %s" % (self.tick, self.channels)

    def __len__(self):
        return len(self.channels)

    def __lt__(self, __o: object):
        return self.tick < __o.tick


# determine the combination of channels to form chord
def get_channels_in_chord(
    channels: list[Channel], chord: "VanillaChord | list[VanillaNote]"
):
    channels_played_in_chord = []
    chord_working_copy = chord.copy()
    for channel in channels:
        if len(chord_working_copy) == 0:
            break
        if chord_working_copy.contains(channel.chord):
            channels_played_in_chord.append(channel.id)
            chord_working_copy.removenotes(channel.chord)
    channels_played_in_chord.sort()
    return channels_played_in_chord
