import bpy
import os
from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector
import math, random
import bmesh
import inspect

def get_wm_props(window_manager):
    return window_manager.pyclone

def get_scene_props(scene):
    return scene.pyclone

def get_hb_object_props(scene):
    return scene.home_builder

def get_3d_view_region(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.data:
                    return region   

def get_object_icon(obj):
    ''' 
    This returns the correct icon for the object type

    ARGS
    obj (bpy.types.Object) - Object to get the icon for

    '''
    if 'IS_ASSEMBLY_BP' in obj:
        return 'FILE_3D'
    if obj.type == 'MESH':
        return 'OUTLINER_OB_MESH'
    if obj.type == 'CURVE':
        return 'OUTLINER_OB_CURVE'
    if obj.type == 'FONT':
        return 'OUTLINER_OB_FONT'
    if obj.type == 'EMPTY':
        return 'OUTLINER_OB_EMPTY'
    if obj.type == 'LATTICE':
        return 'OUTLINER_OB_LATTICE'
    if obj.type == 'META':
        return 'OUTLINER_OB_META'
    if obj.type == 'LIGHT':
        return 'OUTLINER_OB_LIGHT'
    if obj.type == 'CAMERA':
        return 'OUTLINER_OB_CAMERA'
    if obj.type == 'SURFACE':
        return 'OUTLINER_OB_SURFACE'
    if obj.type == 'ARMATURE':
        return 'OUTLINER_OB_ARMATURE'
    if obj.type == 'SPEAKER':
        return 'OUTLINER_OB_SPEAKER'
    if obj.type == 'FORCE_FIELD':
        return 'OUTLINER_OB_FORCE_FIELD'
    if obj.type == 'GPENCIL':
        return 'OUTLINER_OB_GREASEPENCIL'
    if obj.type == 'LIGHT_PROBE':
        return 'OUTLINER_OB_LIGHTPROBE'

def object_has_driver(obj):
    """ If the object has a driver this function will return True otherwise False
    """
    if obj.animation_data:
        if len(obj.animation_data.drivers) > 0:
            return True

def get_assembly_bp(obj):
    if "IS_ASSEMBLY_BP" in obj:
        return obj
    elif obj.parent:
        return get_assembly_bp(obj.parent)

def hook_vertex_group_to_object(obj_mesh, vertex_group, obj_hook):
    """ This function adds a hook modifier to the verties 
        in the vertex_group to the obj_hook
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj_hook.hide_set(False)
    obj_hook.hide_viewport = False
    obj_hook.hide_select = False
    obj_hook.select_set(True)
    obj_mesh.hide_set(False)
    obj_mesh.hide_select = False
    if vertex_group in obj_mesh.vertex_groups:
        vgroup = obj_mesh.vertex_groups[vertex_group]
        obj_mesh.vertex_groups.active_index = vgroup.index
        bpy.context.view_layer.objects.active = obj_mesh
        bpy.ops.pc_object.toggle_edit_mode(obj_name=obj_mesh.name)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_select()
        if obj_mesh.data.total_vert_sel > 0:
            bpy.ops.object.hook_add_selob()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.pc_object.toggle_edit_mode(obj_name=obj_mesh.name)

def apply_hook_modifiers(context, obj):
    """ This function applies all of the hook modifers on an object
    """
    obj.hide_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.type == 'HOOK':
            bpy.ops.object.modifier_apply(modifier=mod.name)

def delete_obj_list(obj_list):
    ''' 
    This function deletes every object in the list
    '''
    bpy.ops.object.select_all(action='DESELECT')
    for obj in obj_list:
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                # THESE DRIVERS MUST BE REMOVED TO DELETE OBJECTS
                if driver.data_path in {'hide', 'hide_select'}:
                    obj.driver_remove(driver.data_path)

        obj.parent = None
        obj.hide_select = False
        obj.hide_viewport = False
        obj.select_set(True)

        # TODO: FIGURE OUT IF THIS IS RIGHT
        if obj.name in bpy.context.view_layer.active_layer_collection.collection.objects:
            bpy.context.view_layer.active_layer_collection.collection.objects.unlink(obj)
            # bpy.context.scene.objects.unlink(obj)

    for obj in obj_list:
        bpy.data.objects.remove(obj, do_unlink=True)

def select_obj_list(obj_list):
    '''
    This function selects every object in the list
    '''
    for obj in obj_list:
        if obj.type != 'EMPTY' and obj.hide_render == False and obj.name in bpy.context.view_layer.objects:
            obj.hide_select = False
            obj.hide_viewport = False
            obj.select_set(True)

def delete_object_and_children(obj_bp):
    '''
    Deletes a object and all it's children

    ARGS
    obj_bp (bpy.types.Object) - Parent Object to Delete
    '''
    obj_list = []
    obj_list.append(obj_bp)
    for child in obj_bp.children:
        if len(child.children) > 0:
            delete_object_and_children(child)
        else:
            obj_list.append(child)
    delete_obj_list(obj_list)

def select_object_and_children(obj_bp):
    '''
    Selects an object and all it's children

    ARGS
    obj_bp (bpy.types.Object) - Parent Object to Select
    '''
    obj_list = []
    obj_list.append(obj_bp)
    for child in obj_bp.children:
        if len(child.children) > 0:
            select_object_and_children(child)
        else:
            obj_list.append(child)
    select_obj_list(obj_list)

def create_cube_mesh(name, size):
    verts = [(0.0, 0.0, 0.0),
             (0.0, size[1], 0.0),
             (size[0], size[1], 0.0),
             (size[0], 0.0, 0.0),
             (0.0, 0.0, size[2]),
             (0.0, size[1], size[2]),
             (size[0], size[1], size[2]),
             (size[0], 0.0, size[2]),
             ]

    faces = [(0, 1, 2, 3),
             (4, 7, 6, 5),
             (0, 4, 5, 1),
             (1, 5, 6, 2),
             (2, 6, 7, 3),
             (4, 0, 3, 7),
             ]

    return create_object_from_verts_and_faces(verts, faces, name)

def create_object_from_verts_and_faces(verts, faces, name):
    """
        Creates an object from Verties and Faces
        arg1: Verts List of tuples [(float,float,float)]
        arg2: Faces List of ints
        arg3: name of object

        RETURNS bpy.types.Object
    """
    mesh = bpy.data.meshes.new(name)

    bm = bmesh.new()

    for v_co in verts:
        bm.verts.new(v_co)

    for f_idx in faces:
        bm.verts.ensure_lookup_table()
        bm.faces.new([bm.verts[i] for i in f_idx])

    bm.to_mesh(mesh)

    mesh.update()

    obj_new = bpy.data.objects.new(mesh.name, mesh)

    return obj_new

def calc_distance(point1, point2):
    """ This gets the distance between two points (X,Y,Z)
    """
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)

def floor_raycast(context, mx, my):
    '''
    This casts a ray into the 3D view and returns information based on what is under the mouse

    ARGS
    context (bpy.context) = current blender context
    mx (float) = 2D mouse x location
    my (float) = 2D mouse y location

    RETURNS tuple
    has_hit (boolean) - determines if an object is under the mouse
    snapped_location (tuple) - x,y,z location of location under mouse
    snapped_normal (tuple) - normal direction
    snapped_rotation (tuple) - rotation
    face_index (int) - face index under mouse
    object (bpy.types.Object) - Blender Object under mouse
    martix (float multi-dimensional array of 4 * 4 items in [-inf, inf]) - matrix of placement under mouse
    '''
    r = context.region
    rv3d = context.region_data
    coord = mx, my

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(r, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(r, rv3d, coord)
    # ray_target = ray_origin + (view_vector * 1000000000)
    ray_target = ray_origin + view_vector

    snapped_location = mathutils.geometry.intersect_line_plane(ray_origin, ray_target, (0, 0, 0), (0, 0, 1),
                                                               False)
    if snapped_location != None:
        has_hit = True
        snapped_normal = Vector((0, 0, 1))
        face_index = None
        object = None
        matrix = None
        snapped_rotation = snapped_normal.to_track_quat('Z', 'Y').to_euler()
        offset_rotation_amount = 0
        randomize_rotation_amount = 0
        randomize_rotation = False
        if randomize_rotation:
            randoffset = offset_rotation_amount + math.pi + (
                    random.random() - 0.5) * randomize_rotation_amount
        else:
            randoffset = offset_rotation_amount + math.pi
        snapped_rotation.rotate_axis('Z', randoffset)

    return has_hit, snapped_location, snapped_normal, snapped_rotation, face_index, object, matrix

def get_selection_point(context, region, event, ray_max=10000.0, objects=None, floor=None, exclude_objects=[]):
    """Run this function on left mouse, execute the ray cast"""
    # get the context arguments
    scene = context.scene
    rv3d = region.data
    coord = event.mouse_x - region.x, event.mouse_y - region.y   

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""

        for obj in context.visible_objects:

            if objects:
                if obj in objects and obj not in exclude_objects:
                    yield (obj, obj.matrix_world.copy())

            else:
                if obj not in exclude_objects:
                    if floor is not None and obj == floor:
                        yield (obj, obj.matrix_world.copy())

                    if obj.type in {'MESH','CURVE'} and obj.hide_select == False:
                        yield (obj, obj.matrix_world.copy())

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""

        try:
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv @ ray_origin
            ray_target_obj = matrix_inv @ ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj

            # cast the ray
            success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
            if success:
                return location, normal, face_index
            else:
                return None, None, None
        except:
            print("ERROR IN obj_ray_cast", obj)
            return None, None, None

    best_length_squared = ray_max * ray_max
    best_obj = None
    best_hit = (0,0,0)
    best_norm = Vector((0, 0, 0))

    for obj, matrix in visible_objects_and_duplis():
        if obj.type in {'MESH','CURVE'}:
            if obj.data:

                hit, normal, face_index = obj_ray_cast(obj, matrix)
                if hit is not None:
                    hit_world = matrix @ hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if length_squared < best_length_squared:
                        best_hit = hit_world
                        best_length_squared = length_squared
                        best_obj = obj
                        best_norm = normal

    return best_hit, best_obj, best_norm    

def get_bp_by_tag(obj,tag):  
    if not obj:
        return None    
    if tag in obj:
        return obj
    elif obj.parent:
        return get_bp_by_tag(obj.parent,tag)   

def get_object(path):
    if os.path.exists(path):

        with bpy.data.libraries.load(path) as (data_from, data_to):
            data_to.objects = data_from.objects 
        
        for obj in data_to.objects:
            return obj    

def get_connected_left_wall_bp(current_wall):
    for con in current_wall.obj_bp.constraints:
        if con.type == 'COPY_LOCATION':
            target = con.target
            wall_bp = get_bp_by_tag(target,'IS_WALL_BP')
            if wall_bp:
                return wall_bp

def get_connected_right_wall_bp(current_wall):
    props = get_hb_object_props(current_wall.obj_x)
    if props.connected_object:
        wall_bp = get_bp_by_tag(props.connected_object,'IS_WALL_BP')
        if wall_bp:
            return wall_bp                