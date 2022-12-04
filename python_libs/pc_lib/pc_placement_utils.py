import math
from . import pc_types, pc_unit, pc_utils

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

def position_assembly_on_wall(assembly,wall,mouse_location,selected_normal,height_above_floor):
    placement = 'WALL'
    
    assembly.obj_bp.parent = wall.obj_bp
    assembly.obj_bp.matrix_world[0][3] = mouse_location[0]
    assembly.obj_bp.matrix_world[1][3] = mouse_location[1]
    assembly.obj_bp.location.y = 0   

    wall_length = wall.obj_x.location.x
    cabinet_width = assembly.obj_x.location.x
    x_loc = assembly.obj_bp.location.x

    #SNAP TO LEFT
    if x_loc < .25:
        placement = "WALL_LEFT"
        assembly.obj_bp.location.x = 0

    #SNAP TO RIGHT
    if x_loc > wall_length - cabinet_width:
        placement = "WALL_RIGHT"
        assembly.obj_bp.location.x = wall_length - cabinet_width

    #TODO: FIX PLACING CABINET ON BACKSIDE OF WALL
    # if selected_normal.y == 1:
    #     #BACK SIDE OF WALL
    #     cabinet.obj_bp.rotation_euler.z = math.radians(180)
    # else:
    #     cabinet.obj_bp.rotation_euler.z = 0
    assembly.obj_bp.rotation_euler.z = 0
    assembly.obj_bp.location.z = height_above_floor

    return placement        


def position_assembly_next_to_cabinet(cabinet,selected_cabinet,mouse_location):
    wall_bp = pc_utils.get_bp_by_tag(selected_cabinet.obj_bp,'IS_WALL_BP')

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
            if hasattr(selected_cabinet,'corner_type'):
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
            if hasattr(selected_cabinet,'corner_type'):
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

        if placement == 'LEFT':
            cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_world_x
            cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_world_y
            cabinet.obj_bp.location.x -= cabinet_width
            cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
            if hasattr(selected_cabinet,'corner_type'):
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
            if hasattr(selected_cabinet,'corner_type'):
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