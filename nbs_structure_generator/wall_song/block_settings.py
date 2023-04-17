import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common_blocks import *  # noqa: F403
from nbt_structure_utils import BlockData

neutral_building: BlockData = BlockData("cyan_terracotta")
floor_building: BlockData = BlockData("light_gray_stained_glass")
light_source: BlockData = BlockData("ochre_froglight", [("axis", "y")])

redstone_solid_support: BlockData = BlockData("iron_block")
redstone_bus_trans: BlockData = BlockData("smooth_stone_slab", [("type", "top")])
redstone_bus_main: BlockData = BlockData("blue_concrete")
redstone_bus_torch: BlockData = BlockData("red_concrete")
redstone_bus_start: BlockData = BlockData("lime_concrete")
redstone_bus_reset: BlockData = BlockData("purple_concrete")
piston_payload: BlockData = BlockData("green_concrete")
