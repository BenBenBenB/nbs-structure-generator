import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common_blocks import *  # noqa: F403
from nbt_structure_utils import BlockData

redstone_bus_main: BlockData = BlockData("blue_concrete")
redstone_bus_secondary: BlockData = BlockData("pink_concrete")
sand_support: BlockData = BlockData("smooth_stone_slab", [("type", "top")])
building_floor: BlockData = BlockData("light_gray_stained_glass")
wall_material: str = "polished_deepslate"
