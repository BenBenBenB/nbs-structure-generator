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
        
def get_default_blocks():
    blocks = []
    blocks.append(Block( 0,"minecraft:dirt"         ,False,True))
    blocks.append(Block( 1,"minecraft:oak_planks"   ,False,True))
    blocks.append(Block( 2,"minecraft:stone"        ,False,True))
    blocks.append(Block( 3,"minecraft:sand"         ,True ,True))
    blocks.append(Block( 4,"minecraft:glass"        ,False,False))
    blocks.append(Block( 5,"minecraft:brown_wool"   ,False,True))
    blocks.append(Block( 6,"minecraft:clay"         ,False,True))
    blocks.append(Block( 7,"minecraft:gold_block"   ,False,True))
    blocks.append(Block( 8,"minecraft:packed_ice"   ,False,True))
    blocks.append(Block( 9,"minecraft:bone_block"   ,False,True))
    blocks.append(Block(10,"minecraft:iron_block"   ,False,True))
    blocks.append(Block(11,"minecraft:soul_sand"    ,False,True))
    blocks.append(Block(12,"minecraft:pumpkin"      ,False,True))
    blocks.append(Block(13,"minecraft:emerald_block",False,True))
    blocks.append(Block(14,"minecraft:hay_block"    ,False,True))
    blocks.append(Block(15,"minecraft:glowstone"    ,False,False))
    return blocks

BLOCKS = get_default_blocks()
#todo: give customization options. e.g. wool color
def get_block(instrument_id):
    return next((x for x in BLOCKS if x.id == instrument_id), None)
        
class VanillaNote:
    block_id: int #0-15, block to be placed under note block
    key: int    #0-23
    #isVanilla: bool 
    
    def __init__(self, instrument, key) -> None:
        self.block_id = instrument
        self.key = key 
        
    def __repr__(self) -> str:
        return "(%i, %i)" % (self.block_id, self.key)
    
    def __eq__(self, __o: object) -> bool:
        return self.key == __o.key and self.block_id == __o.block_id
    
    def __lt__(self, other):
        if self.block_id != other.block_id:
            return self.block_id < other.block_id
        else:
            return self.key < other.key
    
class VanillaChord:
    notes: list[VanillaNote]
    
    def __init__(self, notes) -> None:
        self.notes = notes
        
    def __repr__(self) -> str:
        return str(self.notes)
        
    def __getitem__(self, index):
        return self.notes[index]
    
    def __len__(self):
        return len(self.notes)
    
    def copy(self):
        return VanillaChord(self.notes.copy())
        
    @staticmethod
    def create_from_nbs_chord(chord):
        note_list = []
        for note in chord:
            note_list.append(VanillaNote(note.instrument, note.key-33))
        return VanillaChord(note_list)
        
    def contains(self, note_search: list[VanillaNote]):
        working_copy_notes = self.notes.copy()
        for note in note_search:
            if note not in working_copy_notes:
                return False
            working_copy_notes.remove(note)
        return True
    
    def remove(self, note:VanillaNote):
        self.notes.remove(note)
        
    def removenotes(self, chord:list[VanillaNote]):
        for note in chord:
            self.remove(note)
                
    def __lt__(self, other):
        if len(self.notes) != len(other.notes):
            return len(self.notes) < len(other.notes)
        if any(self.notes) and any(other.notes): 
            return min(self.notes) < min(other.notes)
        else:
            return False
        
    def __eq__(self, other_chord: object):
        return len(self.notes) == len(other_chord.notes) and self.contains(other_chord.notes)

class Channel:
    id: int
    chord: VanillaChord 
    def __init__(self, id, notes) -> None:
        self.id = id
        self.chord = notes
        
    def __repr__(self) -> str:
        return "%i, %s" % (self.id, self.chord)
        
    def __getitem__(self, index):
        return self.chord[index]
        
    def is_same_chord(self, other_chord: VanillaChord):
        return self.chord == other_chord
        
# Stores list of all channels that should play on a given tick
class TickChannels:
    tick: int
    channels: list[int]
    def __init__(self, tick, channel_ids) -> None:
        self.tick = tick
        self.channels = channel_ids
        
    def __repr__(self) -> str:
        return "%i %s" % (self.tick, self.channels)
        
    def __getitem__(self, index):
        return self.channels[index]
    
    def __len__(self):
        return len(self.channels)
    
    # determine the combination of channels to form chord
    @staticmethod
    def get_channels(channels:list[Channel], chord:VanillaChord):
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
        
        
    
        