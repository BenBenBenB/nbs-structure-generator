from process_song import TickChannels, Channel

def generate_nbt_structure(tickchannels, channels, save_to_path):
    pass

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
