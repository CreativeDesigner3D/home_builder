import bpy
import math
from mathutils import Vector
from pc_lib import pc_types, pc_unit, pc_utils
from . import types_cabinet_starters
from . import types_cabinet
from . import utils_cabinet
from . import const_cabinets as const

def event_is_place_asset(event):
    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        return True
    elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
        return True
    elif event.type == 'RET' and event.value == 'PRESS':
        return True
    else:
        return False

def event_is_cancel_command(event):
    if event.type in {'RIGHTMOUSE', 'ESC'}:
        return True
    else:
        return False

def event_is_pass_through(event):
    if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
        return True
    else:
        return False

def accumulate_z_rotation(selected_obj,start = 0,total = True):
    ##recursive parent traverser accumulating all rotations ie. total heirarchy rotation
    rotations = [start]
    if selected_obj and selected_obj.parent:
        if total:
            rotations.append(selected_obj.parent.rotation_euler.z)
            return accumulate_z_rotation(selected_obj.parent,sum(rotations))
        else:
            ## breaks after one parent
            return selected_obj.parent.rotation_euler.z
    else:
        return start

def rotate_to_normal(obj_bp,selected_normal):
    ## cabinet vector
    base_vect = Vector((0, -1, 0))

    if selected_normal.y == 1:
        ## if Vector(0,1,0) it is a negative vector relationship with cabinet Vector(0,-1,0)
        ## quaternion calcs fail with these, 180 rotation is all thats required
        obj_bp.rotation_euler.z =+ math.radians(180)

    else:
        ## Vector.rotation_difference() returns quaternion rotation so change mode
        obj_bp.rotation_mode = 'QUATERNION'
        ## quaternion calc - required rotation to align cab to face
        rot_quat = base_vect.rotation_difference(selected_normal)

        obj_bp.rotation_quaternion = rot_quat
        obj_bp.rotation_mode = 'XYZ'

def create_placement_obj(context):
    placement_obj = bpy.data.objects.new('PLACEMENT OBJECT',None)
    placement_obj.location = (0,0,0)
    placement_obj.empty_display_type = 'ARROWS'
    placement_obj.empty_display_size = .1           
    context.view_layer.active_layer_collection.collection.objects.link(placement_obj)
    return placement_obj        

def calc_depth(assembly):
    """ 
    Calculates the depth of the assembly based on the rotation. 
    Used to determine collisions for rotated groups.
    """
    #TODO: This not correct
    if assembly.obj_bp.rotation_euler.z < 0:
        return math.fabs(assembly.obj_x.location.x)
    else:
        return math.fabs(assembly.obj_y.location.y)

def base_point_is_closet(obj_bp):
    if const.CLOSET_TAG in obj_bp or const.CLOSET_INSIDE_CORNER_TAG in obj_bp:
        return True
    else:
        return False

def get_wall_assemblies(wall):
    """ This returns a sorted list of all of the assemblies base points
        parented to the wall
    """
    list_obj_bp = []
    for child in wall.obj_bp.children:
        if 'IS_ASSEMBLY_BP' in child:
            list_obj_bp.append(child)
    list_obj_bp.sort(key=lambda obj: obj.location.x, reverse=False)
    return list_obj_bp

def get_wall_products(wall,cabinet,placement_obj,loc_sort='X'):
    """ This returns a sorted list of all of the assemblies base points
        parented to the wall
    """
    list_obj_bp = []
    list_obj_bp.append(placement_obj)
    for child in wall.obj_bp.children:
        if 'IS_ASSEMBLY_BP' in child and child.name != cabinet.obj_bp.name:
            list_obj_bp.append(child)
    if loc_sort == 'X':
        list_obj_bp.sort(key=lambda obj: obj.location.x, reverse=False)
    if loc_sort == 'Y':
        list_obj_bp.sort(key=lambda obj: obj.location.y, reverse=False)            
    if loc_sort == 'Z':
        list_obj_bp.sort(key=lambda obj: obj.location.z, reverse=False)
    return list_obj_bp

def has_height_collision(active_assembly,assembly):
    cab1_z_1 = active_assembly.obj_bp.matrix_world[2][3]
    cab1_z_2 = active_assembly.obj_z.matrix_world[2][3]
    cab2_z_1 = assembly.obj_bp.matrix_world[2][3]
    cab2_z_2 = assembly.obj_z.matrix_world[2][3]
    
    if cab1_z_1 >= cab2_z_1 and cab1_z_1 <= cab2_z_2:
        return True
        
    if cab1_z_2 >= cab2_z_1 and cab1_z_2 <= cab2_z_2:
        return True

    if cab2_z_1 >= cab1_z_1 and cab2_z_1 <= cab1_z_2:
        return True
        
    if cab2_z_2 >= cab1_z_1 and cab2_z_2 <= cab1_z_2:
        return True

def has_closet_height_collision(current_assembly,assembly):
    if current_assembly.is_hanging:
        if hasattr(assembly,'is_base'):
            if assembly.is_base:
                return False
            else:
                return has_height_collision(current_assembly,assembly)
        else:
            return has_height_collision(current_assembly,assembly)
    else:
        if hasattr(assembly,'is_hanging'):
            if assembly.is_hanging:
                return False
            else:
                return has_height_collision(current_assembly,assembly)
        else:
            return has_height_collision(current_assembly,assembly)

def get_cabinet_placement_location(cabinet,sel_cabinet,mouse_location):
    sel_cabinet_world_loc = (sel_cabinet.obj_bp.matrix_world[0][3],
                                sel_cabinet.obj_bp.matrix_world[1][3],
                                sel_cabinet.obj_bp.matrix_world[2][3])
    
    sel_cabinet_x_world_loc = (sel_cabinet.obj_x.matrix_world[0][3],
                               sel_cabinet.obj_x.matrix_world[1][3],
                               sel_cabinet.obj_x.matrix_world[2][3])

    dist_to_bp = pc_utils.calc_distance(mouse_location,sel_cabinet_world_loc)
    dist_to_x = pc_utils.calc_distance(mouse_location,sel_cabinet_x_world_loc)

    if has_height_collision(cabinet,sel_cabinet):
        if dist_to_bp < dist_to_x:
            return 'LEFT'
        else:
            return 'RIGHT'
    else:
        return 'CENTER'

def get_left_collision_location(assembly):
    wall = pc_types.Assembly(pc_utils.get_bp_by_tag(assembly.obj_bp,const.WALL_TAG))
    list_obj_bp = get_wall_assemblies(wall)
    list_obj_left_bp = []
    for index, obj_bp in enumerate(list_obj_bp):
        if obj_bp.name == assembly.obj_bp.name:
            list_obj_left_bp = list_obj_bp[:index]
            break
    list_obj_left_bp.reverse()
    for obj_bp in list_obj_left_bp:
        prev_assembly = pc_types.Assembly(obj_bp)
        if has_height_collision(assembly,prev_assembly):
            return prev_assembly.obj_bp.location.x + prev_assembly.obj_x.location.x
        #TODO:CHECK NEXT WALL
    
    return 0
    
def get_right_collision_location(assembly):
    wall = pc_types.Assembly(pc_utils.get_bp_by_tag(assembly.obj_bp,const.WALL_TAG))   
    list_obj_bp = get_wall_assemblies(wall)
    list_obj_right_bp = []   
    for index, obj_bp in enumerate(list_obj_bp):
        if obj_bp.name == assembly.obj_bp.name:
            list_obj_right_bp = list_obj_bp[index + 1:]
            break  
    for obj_bp in list_obj_right_bp:
        next_assembly = pc_types.Assembly(obj_bp)
        if has_height_collision(assembly,next_assembly):
            return obj_bp.location.x - math.sin(next_assembly.obj_bp.rotation_euler.z) * next_assembly.obj_y.location.y   
        #TODO:CHECK NEXT WALL
    return wall.obj_x.location.x   

def get_closet_collision_location(closet,wall,placement_obj,mouse_location,direction='LEFT'):
    if wall:
        placement_obj.parent = wall.obj_bp
        placement_obj.matrix_world[0][3] = mouse_location[0]
        placement_obj.matrix_world[1][3] = mouse_location[1]   

        list_obj_bp = get_wall_products(wall,closet,placement_obj)
        list_obj_left_bp = []
        list_obj_right_bp = []
        for index, obj_bp in enumerate(list_obj_bp):
            if obj_bp.name == placement_obj.name:
                list_obj_left_bp = list_obj_bp[:index]
                list_obj_right_bp = list_obj_bp[index + 1:]
                break

        if direction == 'LEFT':
            list_obj_left_bp.reverse()
            for obj_bp in list_obj_left_bp:
                if base_point_is_closet(obj_bp):
                    prev_ass = types_cabinet_starters.Closet(obj_bp)
                else:
                    prev_ass = pc_types.Assembly(obj_bp)
                if has_closet_height_collision(closet,prev_ass):
                    return obj_bp.location.x + prev_ass.obj_x.location.x, prev_ass, wall
            
            # CHECK NEXT WALL
            left_wall_bp =  pc_utils.get_connected_left_wall_bp(wall)
            if left_wall_bp:
                left_wall = pc_types.Assembly(left_wall_bp)
                rotation_difference = math.degrees(wall.obj_bp.rotation_euler.z) - math.degrees(left_wall.obj_bp.rotation_euler.z)
                if rotation_difference < 0 or rotation_difference > 180:
                    list_obj_bp = get_wall_products(left_wall,closet,placement_obj)
                    for obj in list_obj_bp:
                        if obj == placement_obj:
                            continue                            
                        if base_point_is_closet(obj):
                            prev_ass = types_cabinet_starters.Closet(obj)
                        else:
                            prev_ass = pc_types.Assembly(obj)
                        product_x = obj.location.x
                        product_width = prev_ass.obj_x.location.x
                        x_dist = left_wall.obj_x.location.x  - (product_x + product_width)
                        product_depth = math.fabs(closet.obj_y.location.y)
                        if x_dist <= product_depth:
                            if has_closet_height_collision(closet,prev_ass): 
                                return math.fabs(prev_ass.obj_y.location.y), prev_ass, left_wall
            return 0, None, None
        
        if direction == 'RIGHT':
            for obj_bp in list_obj_right_bp:
                if base_point_is_closet(obj_bp):
                    next_assembly = types_cabinet_starters.Closet(obj_bp)
                else:
                    next_assembly = pc_types.Assembly(obj_bp)
                if has_closet_height_collision(closet,next_assembly):
                    wall_length = wall.obj_x.location.x
                    product_x_loc = next_assembly.obj_bp.location.x
                    product_size = 0
                    if next_assembly.obj_bp.rotation_euler.z < 0:
                        product_size = calc_depth(next_assembly)
                    return wall_length - product_x_loc + product_size, next_assembly, wall
    
            # CHECK NEXT WALL
            right_wall_bp =  pc_utils.get_connected_right_wall_bp(wall)
            if right_wall_bp:
                right_wall = pc_types.Assembly(right_wall_bp)
                rotation_difference = math.degrees(wall.obj_bp.rotation_euler.z) - math.degrees(right_wall.obj_bp.rotation_euler.z)
                if rotation_difference > 0 or rotation_difference < -180:
                    list_obj_bp = get_wall_products(right_wall,closet,placement_obj)
                    for obj in list_obj_bp:
                        if obj == placement_obj:
                            continue
                        if base_point_is_closet(obj):
                            next_ass = types_cabinet_starters.Closet(obj)
                        else:
                            next_ass = pc_types.Assembly(obj)
                        product_x = obj.location.x
                        product_width = next_ass.obj_x.location.x
                        product_depth = math.fabs(closet.obj_y.location.y)
                        if product_x <= product_depth:
                            if has_closet_height_collision(closet,next_ass):
                                product_depth = math.fabs(next_ass.obj_y.location.y)
                                return product_depth, next_ass, right_wall
    
            return 0, None, None

    return 0, None, None

def position_cabinet_next_to_door_window(cabinet,mouse_location,assembly):
    placement = get_cabinet_placement_location(cabinet,assembly,mouse_location)

    cabinet_width = cabinet.obj_x.location.x
    sel_assembly_width = assembly.obj_x.location.x
    sel_assembly_world_x = assembly.obj_bp.matrix_world[0][3]
    sel_assembly_world_y = assembly.obj_bp.matrix_world[1][3]
    sel_assembly_width_world_x = assembly.obj_x.matrix_world[0][3]
    sel_assembly_width_world_y = assembly.obj_x.matrix_world[1][3]

    cabinet.obj_bp.rotation_euler.z = 0

    if placement == 'LEFT':
        cabinet.obj_bp.matrix_world[0][3] = sel_assembly_world_x
        cabinet.obj_bp.matrix_world[1][3] = sel_assembly_world_y
        cabinet.obj_bp.location.x -= cabinet_width
    elif placement == 'RIGHT':
        cabinet.obj_bp.matrix_world[0][3] = sel_assembly_width_world_x
        cabinet.obj_bp.matrix_world[1][3] = sel_assembly_width_world_y                                  
    else:
        cabinet.obj_bp.matrix_world[0][3] = sel_assembly_world_x
        cabinet.obj_bp.matrix_world[1][3] = sel_assembly_world_y  
        cabinet.obj_bp.location.x += (sel_assembly_width/2)  - (cabinet_width/2)  

    return placement      

def position_cabinet_next_to_cabinet(cabinet,selected_cabinet,mouse_location,placement_obj):
    wall_bp = pc_utils.get_bp_by_tag(selected_cabinet.obj_bp,const.WALL_TAG)

    placement = get_cabinet_placement_location(cabinet,selected_cabinet,mouse_location)

    sel_cabinet_z_rot = selected_cabinet.obj_bp.rotation_euler.z
    cabinet_width = cabinet.obj_x.location.x
    sel_cabinet_width = selected_cabinet.obj_x.location.x
    sel_cabinet_world_x = selected_cabinet.obj_bp.matrix_world[0][3]
    sel_cabinet_world_y = selected_cabinet.obj_bp.matrix_world[1][3]
    sel_cabinet_width_world_x = selected_cabinet.obj_x.matrix_world[0][3]
    sel_cabinet_width_world_y = selected_cabinet.obj_x.matrix_world[1][3]

    if not wall_bp:
        #CABINET NOT ON WALL
        cabinet.obj_bp.parent = selected_cabinet.obj_bp.parent
        if placement == 'LEFT':
            x_loc = sel_cabinet_world_x - math.cos(sel_cabinet_z_rot) * cabinet_width
            y_loc = sel_cabinet_world_y - math.sin(sel_cabinet_z_rot) * cabinet_width
            cabinet.obj_bp.matrix_world[0][3] = x_loc
            cabinet.obj_bp.matrix_world[1][3] = y_loc
            cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
            if selected_cabinet.corner_type == 'Blind':
                blind_location = selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                if blind_location.get_value() == 0:
                    sel_cabinet_depth = selected_cabinet.obj_y.location.y
                    cabinet.obj_bp.location.x += cabinet_width
                    cabinet.obj_bp.location.y += sel_cabinet_depth - cabinet_width
                    cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(90)
                    placement = 'BLIND_LEFT'
        elif placement == 'RIGHT':
            cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_width_world_x
            cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_width_world_y
            cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
            if selected_cabinet.corner_type == 'Blind':
                blind_location = selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                if blind_location.get_value() == 1:   
                    sel_cabinet_depth = selected_cabinet.obj_y.location.y
                    cabinet.obj_bp.location.y += sel_cabinet_depth
                    cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(-90)
                    placement = 'BLIND_RIGHT' 
        else:
            x_loc = sel_cabinet_world_x - math.cos(sel_cabinet_z_rot) * ((cabinet_width/2) - (sel_cabinet_width/2))
            y_loc = sel_cabinet_world_y - math.sin(sel_cabinet_z_rot) * ((cabinet_width/2) - (sel_cabinet_width/2))
            cabinet.obj_bp.matrix_world[0][3] = x_loc
            cabinet.obj_bp.matrix_world[1][3] = y_loc
            cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
    else:
        #CABINET ON WALL
        current_wall = pc_types.Assembly(wall_bp)
        cabinet.obj_bp.parent = wall_bp
        placement_obj.parent = current_wall.obj_bp
        placement_obj.matrix_world[0][3] = mouse_location[0]
        placement_obj.matrix_world[1][3] = mouse_location[1]  

        if placement == 'LEFT':
            cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_world_x
            cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_world_y
            cabinet.obj_bp.location.x -= cabinet_width
            cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
            if selected_cabinet.corner_type == 'Blind':
                blind_location = selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                if blind_location.get_value() == 0:
                    sel_cabinet_depth = selected_cabinet.obj_y.location.y
                    cabinet.obj_bp.location.x += cabinet_width
                    cabinet.obj_bp.location.y += sel_cabinet_depth - cabinet_width
                    cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(90)
                    placement = 'BLIND_LEFT'    
                    if selected_cabinet.obj_bp.location.x == 0:
                        l_wall_bp = pc_utils.get_connected_left_wall_bp(current_wall)  
                        if l_wall_bp is None:
                            return
                        l_wall = pc_types.Assembly(l_wall_bp)
                        cabinet.obj_bp.parent = l_wall.obj_bp
                        cabinet.obj_bp.rotation_euler.z = 0
                        cabinet.obj_bp.location.y = 0
                        cabinet.obj_bp.location.x = l_wall.obj_x.location.x - math.fabs(sel_cabinet_depth) - cabinet_width
        elif placement == 'RIGHT':
            cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_width_world_x
            cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_width_world_y
            cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
            if selected_cabinet.corner_type == 'Blind':
                blind_location = selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                if blind_location.get_value() == 1:   
                    sel_cabinet_depth = selected_cabinet.obj_y.location.y
                    cabinet.obj_bp.location.y += sel_cabinet_depth
                    cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(-90)
                    placement = 'BLIND_RIGHT'   
                    if selected_cabinet.obj_bp.location.x >= current_wall.obj_x.location.x - sel_cabinet_width - .01:
                        r_wall_bp = pc_utils.get_connected_right_wall_bp(current_wall)  
                        if r_wall_bp is None:
                            return
                        r_wall = pc_types.Assembly(r_wall_bp)
                        cabinet.obj_bp.parent = r_wall.obj_bp
                        cabinet.obj_bp.rotation_euler.z = 0
                        cabinet.obj_bp.location.y = 0                            
                        cabinet.obj_bp.location.x = math.fabs(sel_cabinet_depth)                                   
        else:
            cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_world_x
            cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_world_y
            cabinet.obj_bp.location.x += (sel_cabinet_width/2)  - (cabinet_width/2)

    return placement

def position_cabinet_on_object(mouse_location,cabinet,selected_obj,cursor_z,selected_normal,height_above_floor):
    cabinet.obj_bp.parent = None
    cabinet.obj_bp.location.x = mouse_location[0]
    cabinet.obj_bp.location.y = mouse_location[1]
    
    if selected_obj and selected_normal.z == 0:
        rotate_to_normal(cabinet.obj_bp,selected_normal)
        parented_rotation_sum = accumulate_z_rotation(selected_obj)
        cabinet.obj_bp.rotation_euler.z += selected_obj.rotation_euler.z + parented_rotation_sum

    cabinet.obj_bp.location.z = height_above_floor + cursor_z

    return "OBJECT"

def position_corner_unit_on_wall(cabinet,wall,placement_obj,mouse_location,selected_normal,height_above_floor):
    placement = 'WALL'
    
    cabinet.obj_bp.parent = wall.obj_bp
    cabinet.obj_bp.matrix_world[0][3] = mouse_location[0]
    cabinet.obj_bp.matrix_world[1][3] = mouse_location[1]
    placement_obj.parent = wall.obj_bp
    placement_obj.matrix_world[0][3] = mouse_location[0]
    placement_obj.matrix_world[1][3] = mouse_location[1] 
    cabinet.obj_bp.location.y = 0   

    wall_length = wall.obj_x.location.x
    cabinet_width = cabinet.obj_x.location.x
    x_loc = cabinet.obj_bp.location.x

    #SNAP TO LEFT
    if x_loc < .25:
        placement = "WALL_LEFT"
        cabinet.obj_bp.rotation_euler.z = math.radians(0)
        cabinet.obj_bp.location.x = 0

    #SNAP TO RIGHT
    if x_loc > wall_length - cabinet_width:
        placement = "WALL_RIGHT"
        cabinet.obj_bp.rotation_euler.z = math.radians(-90)
        cabinet.obj_bp.location.x = wall_length

    #TODO: GET NEXT PRODUCT AND UPDATE LOCATION AND SIZE

    # if selected_normal.y == 1:
    #     #BACK SIDE OF WALL
    #     cabinet.obj_bp.rotation_euler.z = math.radians(180)
    # else:
    #     cabinet.obj_bp.rotation_euler.z = 0
    cabinet.obj_bp.location.z = height_above_floor
    return placement

def position_closet_on_wall(closet,wall,placement_obj,mouse_location):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    left_spacing = 0
    right_spacing = 0
    closet.obj_bp.parent = wall.obj_bp
    closet.obj_bp.location = (0,0,0)        
    closet.obj_x.location.x = wall.obj_x.location.x
    pc_utils.select_children(closet.obj_bp)              
    left_x_loc, left_product, left_wall = get_closet_collision_location(closet,wall,placement_obj,mouse_location,direction='LEFT')
    right_x_loc, right_product, right_wall = get_closet_collision_location(closet,wall,placement_obj,mouse_location,direction='RIGHT')
    if left_wall:
        if left_wall.obj_bp.name == wall.obj_bp.name:
            left_spacing = 0
        else:
            if left_product and const.CLOSET_INSIDE_CORNER_TAG not in left_product.obj_bp:
                left_spacing = props.closet_corner_spacing

    if right_wall:
        if right_wall.obj_bp.name == wall.obj_bp.name:
            right_spacing = 0
        else:
            if right_product and const.CLOSET_INSIDE_CORNER_TAG not in right_product.obj_bp:
                right_spacing = props.closet_corner_spacing

    closet.obj_bp.location.x = left_x_loc + left_spacing
    closet.obj_x.location.x -= left_x_loc + left_spacing + right_spacing + right_x_loc
    return 'WALL'

def position_closet_on_countertop(closet,countertop,placement_obj,mouse_location):
    wall = None
    wall_bp = pc_utils.get_bp_by_tag(countertop.obj_bp,const.WALL_TAG)
    if wall_bp:
        wall = pc_types.Assembly(wall_bp)

    sel_ctop_width = countertop.obj_x.location.x
    ctop_thickness = countertop.obj_z.location.z
    sel_ctop_world_x = countertop.obj_bp.matrix_world[0][3]
    sel_ctop_world_y = countertop.obj_bp.matrix_world[1][3]
    sel_ctop_world_z = countertop.obj_bp.matrix_world[2][3]

    if wall:
        closet.obj_bp.parent = wall.obj_bp
    pc_utils.select_children(closet.obj_bp)      
    pc_utils.select_children(countertop.obj_bp)     
    closet.obj_bp.matrix_world[0][3] = sel_ctop_world_x
    closet.obj_bp.matrix_world[1][3] = sel_ctop_world_y
    closet.obj_x.location.x = sel_ctop_width 
    closet.obj_bp.rotation_euler.z = countertop.obj_bp.rotation_euler.z
    hanging_height = closet.obj_z.matrix_world[2][3]
    target_height = hanging_height - (sel_ctop_world_z + ctop_thickness)

    return 'COUNTERTOP', target_height

def position_cabinet_on_wall(cabinet,wall,placement_obj,mouse_location,selected_normal,height_above_floor):
    placement = 'WALL'
    
    cabinet.obj_bp.parent = wall.obj_bp
    cabinet.obj_bp.matrix_world[0][3] = mouse_location[0]
    cabinet.obj_bp.matrix_world[1][3] = mouse_location[1]
    placement_obj.parent = wall.obj_bp
    placement_obj.matrix_world[0][3] = mouse_location[0]
    placement_obj.matrix_world[1][3] = mouse_location[1] 
    cabinet.obj_bp.location.y = 0   

    wall_length = wall.obj_x.location.x
    cabinet_width = cabinet.obj_x.location.x
    x_loc = cabinet.obj_bp.location.x

    #SNAP TO LEFT
    if x_loc < .25:
        placement = "WALL_LEFT"
        cabinet.obj_bp.location.x = 0

    #SNAP TO RIGHT
    if x_loc > wall_length - cabinet_width:
        placement = "WALL_RIGHT"
        cabinet.obj_bp.location.x = wall_length - cabinet_width

    #TODO: FIX PLACING CABINET ON BACKSIDE OF WALL
    # print('NORMAL',selected_normal.y)
    # if selected_normal.y == 1:
    #     #BACK SIDE OF WALL
    #     cabinet.obj_bp.rotation_euler.z = math.radians(180)
    # else:
    #     cabinet.obj_bp.rotation_euler.z = 0
    cabinet.obj_bp.rotation_euler.z = 0
    cabinet.obj_bp.location.z = height_above_floor

    return placement

def position_cabinet(cabinet,mouse_location,selected_obj,cursor_z,selected_normal,placement_obj,height_above_floor):
    cabinet_bp = pc_utils.get_bp_by_tag(selected_obj,const.CABINET_TAG)
    window_bp = pc_utils.get_bp_by_tag(selected_obj,const.WINDOW_TAG)
    door_bp = pc_utils.get_bp_by_tag(selected_obj,const.ENTRY_DOOR_TAG)
    placement = ""
    sel_cabinet = None
    sel_wall = None

    if not cabinet_bp:
        cabinet_bp = pc_utils.get_bp_by_tag(selected_obj,const.APPLIANCE_TAG)

    wall_bp = pc_utils.get_bp_by_tag(selected_obj,const.WALL_TAG)
    if window_bp:
        assembly = pc_types.Assembly(window_bp)
        placement = position_cabinet_next_to_door_window(cabinet,mouse_location,assembly)
    elif door_bp:
        assembly = pc_types.Assembly(door_bp)
        placement = position_cabinet_next_to_door_window(cabinet,mouse_location,assembly)
    elif cabinet_bp:
        sel_cabinet = types_cabinet.Cabinet(cabinet_bp)
        placement = position_cabinet_next_to_cabinet(cabinet,sel_cabinet,mouse_location,placement_obj)
    elif wall_bp:
        sel_wall = pc_types.Assembly(wall_bp)
        placement = position_cabinet_on_wall(cabinet,sel_wall,placement_obj,mouse_location,selected_normal,height_above_floor)
    elif selected_obj:
        placement = position_cabinet_on_object(mouse_location,cabinet,selected_obj,cursor_z,selected_normal,height_above_floor)
    else:
        placement = "NONE"

    return placement, sel_cabinet, sel_wall    

def position_closet(cabinet,mouse_location,selected_obj,cursor_z,selected_normal,placement_obj,height_above_floor):
    cabinet_bp = pc_utils.get_bp_by_tag(selected_obj,const.CABINET_TAG)
    window_bp = pc_utils.get_bp_by_tag(selected_obj,const.WINDOW_TAG)
    door_bp = pc_utils.get_bp_by_tag(selected_obj,const.ENTRY_DOOR_TAG)
    countertop_bp = pc_utils.get_bp_by_tag(selected_obj,const.COUNTERTOP_TAG)
    
    placement = ""
    sel_cabinet = None
    sel_wall = None
    override_height = 0

    if not cabinet_bp:
        cabinet_bp = pc_utils.get_bp_by_tag(selected_obj,const.APPLIANCE_TAG)

    wall_bp = pc_utils.get_bp_by_tag(selected_obj,const.WALL_TAG)

    if window_bp:
        sel_assembly = pc_types.Assembly(window_bp)
        placement = position_cabinet_next_to_door_window(cabinet,mouse_location,sel_assembly)
    elif door_bp:
        sel_assembly = pc_types.Assembly(door_bp)
        placement = position_cabinet_next_to_door_window(cabinet,mouse_location,sel_assembly)
    elif countertop_bp:
        sel_ctop = pc_types.Assembly(countertop_bp)
        placement, override_height = position_closet_on_countertop(cabinet,sel_ctop,mouse_location,placement_obj)        
    elif cabinet_bp:
        sel_cabinet = types_cabinet.Cabinet(cabinet_bp)
        placement = position_cabinet_next_to_cabinet(cabinet,sel_cabinet,mouse_location,placement_obj)
    elif wall_bp:
        sel_wall = pc_types.Assembly(wall_bp)
        placement = position_closet_on_wall(cabinet,sel_wall,placement_obj,mouse_location)
    elif selected_obj:
        placement = position_cabinet_on_object(mouse_location,cabinet,selected_obj,cursor_z,selected_normal,height_above_floor)
    else:
        placement = "NONE"
        
    return placement, sel_cabinet, sel_wall, override_height

def position_corner_unit(cabinet,mouse_location,selected_obj,cursor_z,selected_normal,placement_obj,height_above_floor):
    cabinet_bp = pc_utils.get_bp_by_tag(selected_obj,const.CABINET_TAG)
    window_bp = pc_utils.get_bp_by_tag(selected_obj,const.WINDOW_TAG)
    door_bp = pc_utils.get_bp_by_tag(selected_obj,const.ENTRY_DOOR_TAG)
    placement = ""
    sel_cabinet = None
    sel_wall = None
    override_height = 0

    if not cabinet_bp:
        cabinet_bp = pc_utils.get_bp_by_tag(selected_obj,const.APPLIANCE_TAG)

    wall_bp = pc_utils.get_bp_by_tag(selected_obj,const.WALL_TAG)

    if window_bp:
        sel_assembly = pc_types.Assembly(window_bp)
        placement = position_cabinet_next_to_door_window(cabinet,mouse_location,sel_assembly)
    elif door_bp:
        sel_assembly = pc_types.Assembly(door_bp)
        placement = position_cabinet_next_to_door_window(cabinet,mouse_location,sel_assembly)
    elif cabinet_bp:
        sel_cabinet = types_cabinet.Cabinet(cabinet_bp)
        placement = position_cabinet_next_to_cabinet(cabinet,sel_cabinet,mouse_location,placement_obj)
    elif wall_bp:
        sel_wall = pc_types.Assembly(wall_bp)
        placement = position_corner_unit_on_wall(cabinet,sel_wall,placement_obj,mouse_location,selected_normal,height_above_floor)
    else:
        placement = position_cabinet_on_object(mouse_location,cabinet,selected_obj,cursor_z,selected_normal,height_above_floor)

    return placement, sel_cabinet, sel_wall, override_height        