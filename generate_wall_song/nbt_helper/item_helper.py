from nbt.nbt import *


class Enchantment:
    id: str
    lvl: int

    def __init__(self, id: str, lvl: int):
        self.id = id
        self.lvl = lvl

    def get_nbt(self):
        nbt_enchant = TAG_Compound()
        nbt_enchant.tags.append(TAG_Short(name="lvl", value=self.lvl))
        nbt_enchant.tags.append(TAG_String(name="id", value=self.id))
        return nbt_enchant


class ItemStack:
    id: str
    count: int
    slot: int
    damage: int
    enchantments: list[Enchantment]

    def __init__(
        self,
        item_id: str,
        count: int,
        slot: int,
        damage: int = None,
        enchantments: list[Enchantment] = None,
    ):
        self.id = item_id
        self.count = count
        self.slot = slot
        self.damage = damage
        self.enchantments = enchantments

    def get_nbt(self) -> TAG_Compound:
        nbt_item = TAG_Compound()
        nbt_item.tags.append(TAG_Byte(name="Slot", value=self.slot))
        nbt_item.tags.append(TAG_String(name="id", value=self.id))
        nbt_item.tags.append(TAG_Byte(name="Count", value=self.count))
        if self.__needs_tags():
            nbt_item.tags.append(self.__get_tag_nbt())
        return nbt_item

    def __needs_tags(self) -> bool:
        return (self.damage is not None) or (self.enchantments is not None)

    def __get_tag_nbt(self) -> TAG_Compound:
        nbt_tag = TAG_Compound(name="tag")
        if self.damage is not None:
            nbt_tag.tags.append(TAG_Int(name="Damage", value=self.damage))
        if self.enchantments is not None:
            nbt_enchantments = TAG_List(name="Enchantments", type=TAG_Compound)
            for enchant in self.enchantments:
                nbt_enchantments.tags.append(enchant.get_nbt())
            nbt_tag.tags.append(nbt_enchantments)
        return nbt_tag


class Inventory:
    container_name: str
    items: list[ItemStack]

    def __init__(self, name, items: list[ItemStack] = []) -> None:
        self.container_name = name
        self.items = items

    def get_nbt(self) -> TAG_Compound:
        nbt_inv = TAG_Compound(name="nbt")
        nbt_inv_items = TAG_List(name="Items", type=TAG_Compound)
        for item in self.items:
            nbt_inv_items.tags.append(item.get_nbt())
        nbt_inv.tags.append(nbt_inv_items)
        nbt_inv.tags.append(TAG_String(name="id", value=self.container_name))
        return nbt_inv
