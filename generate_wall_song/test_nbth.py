# todo write actual unit tests
from nbt_helper.nbt_structure_helper import StructureBlocks, AIR_BLOCK
from nbt_helper.plot_helpers import Vector, LineSegment, Cuboid
import block_settings as blocks


def christmas_tree(save_to_path, filename, width, block):
    t_structure = StructureBlocks()
    step_height = 3
    c1 = Vector(0, 0, 0)
    c2 = Vector(width - 1, step_height - 1, width - 1)
    count = 0
    while c2.x >= c1.x:
        pvol = Cuboid(c1, c2)
        count += t_structure.fill(pvol, block)
        count += t_structure.fill_frame(pvol, None)
        c1.add(Vector(1, step_height, 1))
        c2.add(Vector(-1, step_height, -1))
    t_structure.shift(Vector(0, 2, 0))
    c1.y = 0
    c2.y = 2
    pvol = Cuboid(c1, c2)
    t_structure.fill(pvol, block)
    t_structure.get_nbt().write_file(filename=save_to_path + filename)


def create_pyramid_range(save_to_path, base_width_range, block, step_height=1):
    for x in base_width_range:
        name = "p_%i.nbt" % x
        create_pyramid(save_to_path, name, x, block, step_height)


def create_pyramid(save_to_path, filename, width, block, step_height=1):
    p_structure = StructureBlocks()
    c1 = Vector(0, 0, 0)
    c2 = Vector(width - 1, step_height - 1, width - 1)
    count = 0
    while c2.x >= c1.x:
        pvol = Cuboid(c1, c2)
        count += p_structure.fill(pvol, blocks.light_source)
        count += p_structure.fill_frame(pvol, block)
        c1.x, c1.y, c1.z = c1.x + 1, c1.y + step_height, c1.z + 1
        c2.x, c2.y, c2.z = c2.x - 1, c2.y + step_height, c2.z - 1

    p_structure.get_nbt().write_file(filename=save_to_path + filename)


def test_fill(save_to_path, name, size: int, block1, block2):
    f_structure = StructureBlocks()
    c1 = Vector(0, 0, 0)
    c2 = Vector(size - 1, size - 1, size - 1)
    count = 0
    vol1 = Cuboid(c1, c2)
    vol2 = Cuboid(c1, c1)
    vol3 = Cuboid(c2, c2)
    count += f_structure.fill(vol1, block1)
    count += f_structure.fill(vol2, block2)
    count += f_structure.fill(vol3, None)
    f_structure.get_nbt().write_file(filename=save_to_path + name)


def test_fill_replace(save_to_path, name, size: int, block, filter):
    f_structure = StructureBlocks()
    c1 = Vector(0, 0, 0)
    c2 = Vector(size - 1, size - 1, size - 1)
    count = 0
    vol1 = Cuboid(c1, c2)
    vol2 = Cuboid(c1, c1)
    vol3 = Cuboid(c2, c2)
    count += f_structure.fill_replace(vol1, filter, None)
    count += f_structure.fill_replace(vol2, block, filter)
    count += f_structure.fill_replace(vol3, None, filter)
    f_structure.get_nbt().write_file(filename=save_to_path + name)


def test_clone(save_to_path, name, block1, block2):
    f_structure = StructureBlocks()
    c1 = Vector(0, 0, 0)
    c2 = Vector(1, 1, 1)
    count = 0
    count += f_structure.set_block(c1, block1)
    count += f_structure.set_block(c2, block2)
    count += f_structure.clone_block(c1, c2 * 2)
    vol1 = Cuboid(c1, c2)
    count += f_structure.clone(vol1, c2 * 2)
    f_structure.get_nbt().write_file(filename=save_to_path + name)

    g_structure = StructureBlocks()
    g_structure.clone_structure(f_structure, c2 * 5)
    g_structure.set_block(c1, AIR_BLOCK)
    if g_structure.get_block_state(c2 * 5) != block1:
        raise ValueError("should be block1")
    g_structure.get_nbt(fill_void_with_air=False).write_file(
        filename=save_to_path + "c" + name
    )

    try:
        count += f_structure.clone(vol1, c2)
    except:
        return count
    raise ValueError("That should have failed")


def test_fills(save_to_path, name, block1, block2):
    c1 = Vector(0, 0, 0)
    f_structure = StructureBlocks()

    c2 = Vector(1, 1, 1)
    vol1 = Cuboid(c1, c2 * 9)
    f_structure.fill(vol1, block1)
    f_structure.fill_outline(vol1, block2)
    f_structure.fill_frame(vol1, block1)

    c2 = Vector(7, 2, 7)
    vol2 = Cuboid(c1, c2)
    f_structure.fill_hollow(vol2, block2)

    c2 = Vector(5, 2, 5)
    vol3 = Cuboid(c1, c2)
    f_structure.fill_keep(vol3, block1)

    f_structure.get_nbt().write_file(filename=save_to_path + name)


def cuboid_corners(save_to_path, name, dist: Vector, block1, block2):
    c0 = Vector(0, 0, 0)
    dest_vectors = []
    dest_vectors.append(Vector(dist.x, dist.y, dist.z))
    dest_vectors.append(Vector(dist.x, dist.y, -dist.z))
    dest_vectors.append(Vector(dist.x, -dist.y, dist.z))
    dest_vectors.append(Vector(dist.x, -dist.y, -dist.z))
    dest_vectors.append(Vector(-dist.x, dist.y, dist.z))
    dest_vectors.append(Vector(-dist.x, dist.y, -dist.z))
    dest_vectors.append(Vector(-dist.x, -dist.y, dist.z))
    dest_vectors.append(Vector(-dist.x, -dist.y, -dist.z))
    f_structure = StructureBlocks()

    for vec in dest_vectors:
        f_structure.fill_line(LineSegment(dest_vectors), block1)
        
    f_structure.set_block(c0, block2)

    f_structure.get_nbt().write_file(filename=save_to_path + name)


def connect_the_dots(save_to_path, name, block1, block2):
    c0 = Vector(0, 0, 0)
    dest_vectors = []
    dest_vectors.append(Vector(0,0,0 ))
    dest_vectors.append(Vector(0,10,0 ))
    dest_vectors.append(Vector(0,10,10 ))
    dest_vectors.append(Vector(10,0,0 ))
    dest_vectors.append(Vector(10,5,5 ))
    dest_vectors.append(Vector(7,7,7 ))
    f_structure = StructureBlocks()

    for vec in dest_vectors:
        f_structure.fill_line(LineSegment(dest_vectors), block1)
        
    f_structure.set_block(c0, block2)

    f_structure.get_nbt().write_file(filename=save_to_path + name)


# testing
if __name__ == "__main__":
    save_to_path = "./output/"
    test_fill(save_to_path, "f.nbt", 3, blocks.floor_building, blocks.neutral_building)
    test_fill_replace(
        save_to_path, "fr.nbt", 3, blocks.floor_building, blocks.neutral_building
    )
    create_pyramid_range(save_to_path, range(5, 10), blocks.floor_building, 3)
    test_clone(save_to_path, "c.nbt", blocks.floor_building, blocks.redstone_slab)
    christmas_tree(save_to_path, "tree.nbt", 9, blocks.piston_payload)
    test_fills(save_to_path, "fill.nbt", blocks.piston_payload, blocks.floor_building)
    cuboid_corners(save_to_path, "line.nbt", Vector(3,3,3), blocks.piston_payload, blocks.light_source)
    connect_the_dots(save_to_path, "lines.nbt", blocks.piston_payload, blocks.light_source)
