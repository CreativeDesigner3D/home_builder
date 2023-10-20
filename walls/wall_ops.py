import bpy
import os
import math
import time
import inspect
from pc_lib import pc_utils, pc_types, pc_unit, pc_snap, pc_placement_utils
from .. import hb_utils
# from .. import home_builder_pointers
from . import wall_library
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

def set_wall_angles(current_wall):
    prev_rot = 0
    next_rot = 0
    left_angle = current_wall.get_prompt("Left Angle")
    right_angle = current_wall.get_prompt("Right Angle")    
    rot = math.degrees(current_wall.obj_bp.matrix_world.to_euler().z)
    previous_wall_bp = pc_utils.get_connected_left_wall_bp(current_wall)
    next_wall_bp = pc_utils.get_connected_right_wall_bp(current_wall)

    prev_wall = None
    if previous_wall_bp:
        prev_wall = pc_types.Assembly(previous_wall_bp)
        prev_left_angle = prev_wall.get_prompt("Left Angle")
        prev_right_angle = prev_wall.get_prompt("Right Angle") 
        prev_rot = math.degrees(prev_wall.obj_bp.matrix_world.to_euler().z)

    next_wall = None
    if next_wall_bp:
        next_wall = pc_types.Assembly(next_wall_bp)
        next_left_angle = next_wall.get_prompt("Left Angle")
        next_rot = math.degrees(next_wall.obj_bp.matrix_world.to_euler().z) 

    if next_wall:
        right_angle.set_value((rot-next_rot)/2)
        next_left_angle.set_value((next_rot-rot)/2)
    else:
        right_angle.set_value(0)

    if prev_wall:
        prev_right_angle.set_value((prev_rot-rot)/2)
        left_angle.set_value((rot-prev_rot)/2)
    else:
        left_angle.set_value(0)

    current_wall.obj_prompts.location = current_wall.obj_prompts.location
    if prev_wall:
        prev_wall.obj_prompts.location = prev_wall.obj_prompts.location
    if next_wall:
        next_wall.obj_prompts.location = next_wall.obj_prompts.location

class home_builder_OT_draw_multiple_walls(pc_snap.Drop_Operator):
    bl_idname = "home_builder.draw_multiple_walls"
    bl_label = "Draw Multiple Walls"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    region = None

    current_wall = None
    previous_wall = None

    starting_point = ()

    typed_value = ""

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    obj_wall_meshes = []

    wall_counter = 1

    distance_to_snap_to_end = pc_unit.inch(10)

    ht_start_command = "(LEFT CLICK = Set Start Point of Walls)"
    ht_next_click_command = "(LEFT CLICK = Set Wall Length)"
    ht_space = "                         "
    ht_cancel_command = "(RIGHT CLICK or ESC = Exit Command)"
    ht_close_room = "(C = Close Room)"
    ht_set_angle = "(HOLD ALT = Set Angle)"
    ht_type_numbers = "(Type numbers to set wall Length)"
    ht_start = ht_start_command + ht_space + ht_cancel_command
    ht_second_click = ht_next_click_command + ht_space + ht_type_numbers + ht_space + ht_set_angle + ht_space + ht_cancel_command
    ht_forth_click = ht_next_click_command + ht_space + ht_close_room + ht_space + ht_type_numbers + ht_space + ht_set_angle + ht_space + ht_cancel_command

    def reset_properties(self):
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""
        self.obj_wall_meshes = []        

    def execute(self, context):
        self.setup_drop_operator(context)
        self.reset_properties()   
        self.create_wall()
        context.workspace.status_text_set(text=self.ht_start)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def create_wall(self):
        props = hb_utils.get_scene_props(bpy.context.scene)
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)        
        wall = None
        for name, obj in inspect.getmembers(wall_library):
            if name == filename.replace(" ","_"):        
                wall = obj()
        if not wall:
            wall = wall_library.Wall()
        wall.draw_wall()
        wall.set_name("Wall")

        if self.current_wall:
            self.previous_wall = self.current_wall
        self.current_wall = wall
        self.current_wall.obj_x.location.x = 0
        self.current_wall.obj_y.location.y = props.wall_thickness
        self.current_wall.obj_z.location.z = props.wall_height
        self.current_wall.obj_bp.hide_viewport = False
        self.current_wall.obj_x.hide_viewport = False
        self.current_wall.obj_y.hide_viewport = False
        self.current_wall.obj_z.hide_viewport = False
        self.current_wall.obj_prompts.hide_viewport = False
        self.set_child_properties(self.current_wall.obj_bp)

        self.dim = pc_types.GeoNodeDimension()
        self.dim.create()
        self.dim.obj.parent = self.current_wall.obj_bp
        self.dim.set_input("Leader Length",pc_unit.inch(3))
        self.dim.set_input("Offset Text Amount",pc_unit.inch(6))
        self.dim.set_input("Text Size",.15)
        self.dim.set_input("Arrow Height",.08)
        self.dim.set_input("Arrow Length",.1)
        self.dim.set_input("Line Thickness",.007)
        self.dim.obj.location.z = self.current_wall.obj_z.location.z
        self.dim.obj.select_set(False)
        self.dim.obj.color = (0,0,0,1)
        self.dim.obj.show_in_front = True

        for obj in self.current_wall.obj_bp.children:
            self.exclude_objects.append(obj)

        self.exclude_objects.append(self.dim.obj)

    def connect_walls(self):
        self.current_wall.obj_bp.location = self.previous_wall.obj_x.matrix_world.translation
        constraint_obj = self.previous_wall.obj_x
        constraint = self.current_wall.obj_bp.constraints.new('COPY_LOCATION')
        constraint.target = constraint_obj
        constraint.use_x = True
        constraint.use_y = True
        constraint.use_z = True
        #Used to get connected wall for prompts
        hb_utils.get_object_props(constraint_obj).connected_object = self.current_wall.obj_bp

    def set_child_properties(self,obj):
        pc_utils.update_id_props(obj,self.current_wall.obj_bp)  
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'              
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
            obj.display_type = 'TEXTURED'   
            self.obj_wall_meshes.append(obj)
        for child in obj.children:
            self.set_placed_properties(child) 

    def get_first_wall(self,wall):
        if len(wall.obj_bp.constraints) > 0:
            obj_bp = wall.obj_bp.constraints[0].target.parent
            return self.get_first_wall(pc_types.Assembly(obj_bp))
        else:
            return wall 

    def get_number_of_walls(self,wall,counter):
        if len(wall.obj_bp.constraints) > 0:
            counter += 1
            obj_bp = wall.obj_bp.constraints[0].target.parent
            return self.get_number_of_walls(pc_types.Assembly(obj_bp),counter)
        else:
            return counter

    def connect_to_first_wall(self,first_wall,current_wall):
        self.current_wall.obj_bp.rotation_euler.z = 0

        constraint_obj = first_wall.obj_bp
        constraint = current_wall.obj_bp.constraints.new('LOCKED_TRACK')
        constraint.target = constraint_obj
        constraint.track_axis = 'TRACK_X'
        constraint.lock_axis = 'LOCK_Z'

        driver = current_wall.obj_x.driver_add('location',0)
        driver.driver.type = 'SCRIPTED'

        var = driver.driver.variables.new()
        var.name = 'distance'
        var.type = 'LOC_DIFF'
        var.targets[0].id = current_wall.obj_bp
        var.targets[1].id = first_wall.obj_bp

        driver.driver.expression = 'distance'

        bpy.context.view_layer.update()

        set_wall_angles(self.current_wall)
        
        # hb_utils.get_object_props(self.current_wall.obj_x).connected_object = first_wall.obj_bp

    def warp_cursor_to_bp(self,context):
        context.view_layer.update()
        region = context.region
        self.previous_wall.obj_x
        co = location_3d_to_region_2d(region,context.region_data,self.current_wall.obj_bp.matrix_world.translation)
        region_offset = Vector((region.x,region.y))
        x_y = (co + region_offset)
        context.window.cursor_warp(x=int(x_y[0]),y=int(x_y[1]))    

    def hide_objects(self,hide):
        for obj in self.current_wall.obj_bp.children:
            if obj.type == 'MESH':
                obj.hide_viewport = hide

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.area.tag_redraw()
        self.set_type_value(event)

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        if event.ctrl:
            selected_point = self.hit_location
        else:
            selected_point = self.get_snap_location(self.hit_location)

        self.hide_objects(True)
        self.mouse_pos = Vector((event.mouse_x - self.region.x, event.mouse_y - self.region.y))  
        context.view_layer.update()          
        pc_snap.main(self, event.ctrl, context)
        self.hide_objects(False)

        connected_wall_bp = None
        if self.hit_object:
            wall_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_WALL_BP')
            if wall_bp and self.previous_wall == None:
                connected_wall_bp = wall_bp

        self.position_object(selected_point,self.hit_object,event.alt,event.ctrl)
        self.set_end_angles() 

        number_of_walls = self.get_number_of_walls(self.current_wall,0)

        if self.starting_point == ():
            self.dim.obj.hide_viewport = True
            context.workspace.status_text_set(text=self.ht_start)
        else:
            self.dim.obj.hide_viewport = False
            if number_of_walls > 1:
                context.workspace.status_text_set(text=self.ht_forth_click)
            else:
                context.workspace.status_text_set(text=self.ht_second_click)

        if self.starting_point == () and connected_wall_bp:
            previous_wall = pc_types.Assembly(connected_wall_bp)
            select_point = (selected_point[0],selected_point[1],0)
            end_point = (previous_wall.obj_x.matrix_world[0][3],previous_wall.obj_x.matrix_world[1][3],0)
            dist = pc_utils.calc_distance(select_point,end_point)
            if dist < self.distance_to_snap_to_end:
                for child in previous_wall.obj_bp.children:
                    if child.type == 'MESH':
                        child.select_set(True)        

        if self.event_close_room(event) and number_of_walls > 1:
            first_wall = self.get_first_wall(self.current_wall)
            self.connect_to_first_wall(first_wall,self.current_wall)
            self.set_placed_properties(self.current_wall.obj_bp)
            pc_utils.delete_object_and_children(self.dim.obj)
            #CREATE AND DELETE NEW WALL SO NAMING IS CONSISTENT
            self.create_wall()
            pc_utils.delete_object_and_children(self.current_wall.obj_bp)
            context.workspace.status_text_set(text=None)
            return {'FINISHED'}

        if self.event_is_place_first_point(event):
            self.starting_point = (selected_point[0],selected_point[1],0)
            #ONLY CONNECT IF CURSOR IS NEAR END POINT
            if connected_wall_bp:
                previous_wall = pc_types.Assembly(connected_wall_bp)
                select_point = (selected_point[0],selected_point[1],0)
                end_point = (previous_wall.obj_x.matrix_world[0][3],previous_wall.obj_x.matrix_world[1][3],0)
                dist = pc_utils.calc_distance(select_point,end_point)
                if dist < self.distance_to_snap_to_end:
                    self.previous_wall = previous_wall
                    self.connect_walls()
                self.typed_value = ""                
            return {'RUNNING_MODAL'}
            
        if self.event_is_place_next_point(event):
            context.workspace.status_text_set(text=self.ht_second_click)
            pc_utils.delete_object_and_children(self.dim.obj)
            self.set_placed_properties(self.current_wall.obj_bp)
            self.create_wall()
            self.connect_walls()
            self.warp_cursor_to_bp(context)
            self.typed_value = ""
            new_wall_loc = self.current_wall.obj_bp.matrix_world.translation
            self.starting_point = (new_wall_loc[0],new_wall_loc[1],0)
            return {'RUNNING_MODAL'}

        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'} 

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def event_is_place_next_point(self,event):
        if self.starting_point == ():
            return False
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_place_first_point(self,event):
        if self.starting_point != ():
            return False
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_cancel_command(self,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return True
        else:
            return False
    
    def event_is_pass_through(self,event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return True
        else:
            return False

    def event_close_room(self,event):
        if event.type in {'C'}:
            return True
        else:
            return False

    def set_end_angles(self):
        if self.previous_wall and self.current_wall:
            left_angle = self.current_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 

            prev_rot = round(math.degrees(self.previous_wall.obj_bp.matrix_world.to_euler().z),0) 
            rot = round(math.degrees(self.current_wall.obj_bp.matrix_world.to_euler().z),0)
            diff = int(math.fabs(rot-prev_rot))
            if diff == 0 or diff == 180:
                left_angle.set_value(0)
                prev_right_angle.set_value(0)
            else:
                left_angle.set_value((rot-prev_rot)/2)
                prev_right_angle.set_value((prev_rot-rot)/2)

            self.current_wall.obj_prompts.location = self.current_wall.obj_prompts.location
            self.previous_wall.obj_prompts.location = self.previous_wall.obj_prompts.location   

    def set_wall_length(self,length):
        if self.typed_value == "":
            self.current_wall.obj_x.location.x = math.fabs(length)
        else:
            if self.typed_value == ".":
                value = 0
            else:
                value = eval(self.typed_value)
            if bpy.context.scene.unit_settings.system == 'METRIC':
                self.current_wall.obj_x.location.x = pc_unit.millimeter(float(value))
            else:
                self.current_wall.obj_x.location.x = pc_unit.inch(float(value))     

    def get_snap_location(self,selected_point):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        x = math.ceil(selected_point[0]/sv)
        y = math.ceil(selected_point[1]/sv)
        return x*sv, y*sv

    def get_snap_angle(self,angle):
        sv = bpy.context.scene.home_builder.wall_angle_snap_value
        return round(angle/sv)*sv
    
    def position_object(self,selected_point,selected_obj,set_angle,use_snap):
        if self.starting_point == ():
            self.current_wall.obj_bp.location.x = selected_point[0]
            self.current_wall.obj_bp.location.y = selected_point[1]           
            self.current_wall.obj_bp.location.z = 0
        else:
            x = selected_point[0] - self.starting_point[0]
            y = selected_point[1] - self.starting_point[1]
            parent_rot = self.current_wall.obj_bp.parent.rotation_euler.z if self.current_wall.obj_bp.parent else 0

            if set_angle:
                dist = pc_utils.calc_distance(self.starting_point, (x,y,0))
                self.set_wall_length(dist)
                if dist != 0 and x != 0:
                    asin_value = y/dist
                    acos_value = x/dist
                    if asin_value < -1:
                        asin_value = -1
                    if asin_value > 1:
                        asin_value = 1
                    if acos_value > 1:
                        acos_value = 1
                    if acos_value < -1:
                        acos_value = -1
                    as_angle = math.radians(int(math.degrees(math.asin(asin_value))))
                    ac_angle = math.radians(int(math.degrees(math.acos(acos_value))))
                    if x > 0:
                        self.current_wall.obj_bp.rotation_euler.z = self.get_snap_angle(as_angle)
                    elif y > 0:
                        self.current_wall.obj_bp.rotation_euler.z = self.get_snap_angle(ac_angle)
                    else:
                        self.current_wall.obj_bp.rotation_euler.z = self.get_snap_angle(math.fabs(as_angle)) + math.radians(180)
            else:
                if use_snap:
                    if round(self.current_wall.obj_bp.rotation_euler.z,3) == round(math.radians(0) + parent_rot,3):
                        self.set_wall_length(x)
                    if round(self.current_wall.obj_bp.rotation_euler.z,3) == round(math.radians(180) + parent_rot,3):
                        self.set_wall_length(x)
                    if round(self.current_wall.obj_bp.rotation_euler.z,3) == round(math.radians(90) + parent_rot,3):
                        self.set_wall_length(y)
                    if round(self.current_wall.obj_bp.rotation_euler.z,3) == round(math.radians(-90) + parent_rot,3):
                        self.set_wall_length(y)                                                            
                else:
                    if math.fabs(x) > math.fabs(y):
                        if x > 0:
                            self.current_wall.obj_bp.rotation_euler.z = math.radians(0) + parent_rot
                        else:
                            self.current_wall.obj_bp.rotation_euler.z = math.radians(180) + parent_rot
                        self.set_wall_length(x)
                
                    if math.fabs(y) > math.fabs(x):
                        if y > 0:
                            self.current_wall.obj_bp.rotation_euler.z = math.radians(90) + parent_rot
                        else:
                            self.current_wall.obj_bp.rotation_euler.z = math.radians(-90) + parent_rot
                        self.set_wall_length(y)
            
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim.obj.data.splines[0].bezier_points[1].co = (self.current_wall.obj_x.location.x,0,0)

            if self.current_wall.obj_x.location.x < pc_unit.inch(20):
                self.dim.set_input("Offset Text From Line",True)
            else:
                self.dim.set_input("Offset Text From Line",False)

            if self.current_wall.obj_bp.rotation_euler.z > math.radians(179):
                self.dim.set_input("Flip Text",True)
            else:
                self.dim.set_input("Flip Text",False)

            self.dim.set_dim_decimal()

    def hide_empties(self,obj):
        for child in obj.children:
            if child.type == 'EMPTY':
                child.hide_viewport = True

    def cancel_drop(self,context):
        if self.previous_wall:
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_right_angle.set_value(0)

        start_time = time.time()
        for obj in self.obj_wall_meshes:
            # if not obj.hide_viewport:
            #     hb_utils.unwrap_obj(context,obj)
            self.hide_empties(obj.parent)
        print("Wall Unwrap: Draw Time --- %s seconds ---" % (time.time() - start_time))

        pc_utils.delete_object_and_children(self.dim.obj)
        obj_list = []
        obj_list.append(self.current_wall.obj_bp)
        for child in self.current_wall.obj_bp.children:
            obj_list.append(child)
        pc_utils.delete_obj_list(obj_list)
        context.workspace.status_text_set(text=None)
        return {'FINISHED'}
    

class home_builder_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "home_builder.wall_prompts"
    bl_label = "Wall Prompts"

    current_wall = None
    previous_wall = None
    next_wall = None
    all_walls = []

    def execute(self, context):
        return {'FINISHED'}

    def get_all_walls(self,context,wall,all_walls):
        all_walls.append(wall)
        if wall.obj_x.home_builder.connected_object:
            next_wall = pc_types.Assembly(wall.obj_x.home_builder.connected_object)
            self.get_all_walls(context,next_wall,all_walls)
        return all_walls

    def get_first_wall_bp(self,context,obj_bp):
        if len(obj_bp.constraints) > 0:
            bp = obj_bp.constraints[0].target.parent
            return self.get_first_wall_bp(context,bp)
        else:
            return obj_bp   

    def check(self, context):
        for wall in self.all_walls:
            set_wall_angles(wall)
        return True

    def get_next_wall(self,context):
        obj_x = self.current_wall.obj_x
        connected_obj = obj_x.home_builder.connected_object
        if connected_obj:
            self.next_wall = pc_types.Assembly(connected_obj) 

    def get_previous_wall(self,context):
        if len(self.current_wall.obj_bp.constraints) > 0:
            obj_bp = self.current_wall.obj_bp.constraints[0].target.parent
            self.previous_wall = pc_types.Assembly(obj_bp)    

    def invoke(self,context,event):
        wall_bp = pc_utils.get_bp_by_tag(context.object,'IS_WALL_BP')
        self.next_wall = None
        self.previous_wall = None
        self.current_wall = pc_types.Assembly(wall_bp)  
        first_wall_bp = self.get_first_wall_bp(context,self.current_wall.obj_bp)
        first_wall = pc_types.Assembly(first_wall_bp)
        all_walls = []
        self.all_walls = self.get_all_walls(context,first_wall,all_walls)
        self.get_previous_wall(context)
        self.get_next_wall(context)
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=400)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.current_wall.obj_x):
            x = math.fabs(self.current_wall.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Length: ' + value)
        else:
            row1.label(text='Length:')
            row1.prop(self.current_wall.obj_x,'location',index=0,text="")
            row1.prop(self.current_wall.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.current_wall.obj_z):
            z = math.fabs(self.current_wall.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self.current_wall.obj_z,'location',index=2,text="")
            row1.prop(self.current_wall.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.current_wall.obj_y):
            y = math.fabs(self.current_wall.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Thickness: ' + value)
        else:
            row1.label(text='Thickness:')
            row1.prop(self.current_wall.obj_y,'location',index=1,text="")
            row1.prop(self.current_wall.obj_y,'hide_viewport',text="")
            
        if len(self.current_wall.obj_bp.constraints) > 0:
            # col = row.column(align=True)
            # col.label(text="Location:")
            # col.operator('home_builder.disconnect_constraint',text='Disconnect Wall',icon='CONSTRAINT').obj_name = self.current_wall.obj_bp.name
            first_wall = self.get_first_wall_bp(context,self.current_wall.obj_bp)
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(first_wall,'location',text="")            
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.current_wall.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.current_wall.obj_bp,'rotation_euler',index=2,text="")  

        if len(self.current_wall.obj_bp.constraints) > 0:        
            col = row.column(align=True)
            # col.label(text="Location:")
            col.operator('home_builder.disconnect_wall_constraint',text='Disconnect Wall',icon='CONSTRAINT').obj_name = self.current_wall.obj_bp.name

    def draw_brick_wall_props(self,layout,context):
        brick_length = self.current_wall.get_prompt("Brick Length")
        brick_height = self.current_wall.get_prompt("Brick Height")
        mortar_thickness = self.current_wall.get_prompt("Mortar Thickness")
        mortar_inset = self.current_wall.get_prompt("Mortar Inset")

        box = layout.box()
        box.label(text="Brick Options")        
        brick_length.draw(box,allow_edit=False)
        brick_height.draw(box,allow_edit=False)
        mortar_thickness.draw(box,allow_edit=False)
        mortar_inset.draw(box,allow_edit=False)

    def draw_framed_wall_props(self,layout,context):
        stud_spacing_distance = self.current_wall.get_prompt("Stud Spacing Distance")
        material_thickness = self.current_wall.get_prompt("Material Thickness")

        box = layout.box()
        box.label(text="Framing Wall Options")        
        stud_spacing_distance.draw(box,allow_edit=False)
        material_thickness.draw(box,allow_edit=False)

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)

        brick_length = self.current_wall.get_prompt("Brick Length")
        if brick_length:
            self.draw_brick_wall_props(layout,context)

        stud_spacing_distance = self.current_wall.get_prompt("Stud Spacing Distance")
        if stud_spacing_distance:
            self.draw_framed_wall_props(layout,context)

        box = layout.box()
        box.label(text="Room Tools",icon='MODIFIER')
        row = box.row()
        row.operator('home_builder.add_room_light',text='Add Room Light',icon='LIGHT_SUN')
        row.operator('home_builder.draw_floor_plane',text='Add Floor',icon='MESH_PLANE')


class home_builder_OT_draw_floor_plane(bpy.types.Operator):
    bl_idname = "home_builder.draw_floor_plane"
    bl_label = "Draw Floor Plane"
    bl_options = {'UNDO'}
    
    def create_floor_mesh(self,name,size):
        
        verts = [(0.0, 0.0, 0.0),
                (0.0, size[1], 0.0),
                (size[0], size[1], 0.0),
                (size[0], 0.0, 0.0),
                ]

        faces = [(0, 1, 2, 3),
                ]

        return pc_utils.create_object_from_verts_and_faces(verts,faces,name)

    def execute(self, context):
        largest_x = 0
        largest_y = 0
        smallest_x = 0
        smallest_y = 0
        overhang = pc_unit.inch(6)
        wall_assemblies = []
        wall_bps = []
        for obj in context.visible_objects:
            if obj.parent and 'IS_WALL_BP' in obj.parent and obj.parent not in wall_bps:
                wall_bps.append(obj.parent)
                wall_assemblies.append(pc_types.Assembly(obj.parent))
            
        for assembly in wall_assemblies:
            start_point = (assembly.obj_bp.matrix_world[0][3],assembly.obj_bp.matrix_world[1][3],0)
            end_point = (assembly.obj_x.matrix_world[0][3],assembly.obj_x.matrix_world[1][3],0)

            if start_point[0] > largest_x:
                largest_x = start_point[0]
            if start_point[1] > largest_y:
                largest_y = start_point[1]
            if start_point[0] < smallest_x:
                smallest_x = start_point[0]
            if start_point[1] < smallest_y:
                smallest_y = start_point[1]
            if end_point[0] > largest_x:
                largest_x = end_point[0]
            if end_point[1] > largest_y:
                largest_y = end_point[1]
            if end_point[0] < smallest_x:
                smallest_x = end_point[0]
            if end_point[1] < smallest_y:
                smallest_y = end_point[1]

        loc = (smallest_x - overhang, smallest_y - overhang,0)
        width = math.fabs(smallest_y) + math.fabs(largest_y) + (overhang*2)
        length = math.fabs(largest_x) + math.fabs(smallest_x) + (overhang*2)
        if width == 0:
            width = pc_unit.inch(-48)
        if length == 0:
            length = pc_unit.inch(-48)
        obj_plane = self.create_floor_mesh('Floor',(length,width,0.0))
        obj_plane['IS_FLOOR'] = True
        context.view_layer.active_layer_collection.collection.objects.link(obj_plane)
        obj_plane.location = loc
        hb_utils.unwrap_obj(context,obj_plane)
        # home_builder_pointers.assign_pointer_to_object(obj_plane,"Floor")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        obj_plane["PROMPT_ID"] = "home_builder.floor_prompts"

        #SET CONTEXT
        context.view_layer.objects.active = obj_plane
        
        #Add Material Pointer
        bpy.ops.object.material_slot_add()
        pointer = obj_plane.pyclone.pointers.add()
        pointer.name = "Floor"
        pointer.pointer_name = "Floor"        

        pc_utils.assign_materials_to_object(obj_plane)
        return {'FINISHED'}


class home_builder_OT_add_room_light(bpy.types.Operator):
    bl_idname = "home_builder.add_room_light"
    bl_label = "Add Room Light"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        largest_x = 0
        largest_y = 0
        smallest_x = 0
        smallest_y = 0
        wall_groups = []
        height = 0

        wall_assemblies = []
        wall_bps = []
        for obj in context.visible_objects:
            if obj.parent and 'IS_WALL_BP' in obj.parent and obj.parent not in wall_bps:
                wall_bps.append(obj.parent)
                wall_assemblies.append(pc_types.Assembly(obj.parent))

        for assembly in wall_assemblies:
            start_point = (assembly.obj_bp.matrix_world[0][3],assembly.obj_bp.matrix_world[1][3],0)
            end_point = (assembly.obj_x.matrix_world[0][3],assembly.obj_x.matrix_world[1][3],0)
            height = assembly.obj_z.location.z
            
            if start_point[0] > largest_x:
                largest_x = start_point[0]
            if start_point[1] > largest_y:
                largest_y = start_point[1]
            if start_point[0] < smallest_x:
                smallest_x = start_point[0]
            if start_point[1] < smallest_y:
                smallest_y = start_point[1]
            if end_point[0] > largest_x:
                largest_x = end_point[0]
            if end_point[1] > largest_y:
                largest_y = end_point[1]
            if end_point[0] < smallest_x:
                smallest_x = end_point[0]
            if end_point[1] < smallest_y:
                smallest_y = end_point[1]

        x = (math.fabs(largest_x) - math.fabs(smallest_x))/2
        y = (math.fabs(largest_y) - math.fabs(smallest_y))/2
        z = height - pc_unit.inch(.01)
        
        width = math.fabs(smallest_y) + math.fabs(largest_y)
        length = math.fabs(largest_x) + math.fabs(smallest_x)
        if width == 0:
            width = pc_unit.inch(-48)
        if length == 0:
            length = pc_unit.inch(-48)

        bpy.ops.object.light_add(type = 'AREA')
        obj_lamp = context.active_object
        obj_lamp['IS_ROOM_LIGHT'] = True
        obj_lamp.location.x = x
        obj_lamp.location.y = y
        obj_lamp.location.z = z
        obj_lamp.data.shape = 'RECTANGLE'
        obj_lamp.data.size = length + pc_unit.inch(20)
        obj_lamp.data.size_y = math.fabs(width) + pc_unit.inch(20)
        obj_lamp.data.energy = 120
        obj_lamp["PROMPT_ID"] = "home_builder.light_prompts"
        return {'FINISHED'}



class home_builder_OT_light_prompts(bpy.types.Operator):
    bl_idname = "home_builder.light_prompts"
    bl_label = "Light Prompts"
    
    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        obj = context.object
        light = obj.data
        box = layout.box()
        row = box.row()
        row.prop(light, "type",expand=True)
        row = box.row()
        row.label(text="Color")
        row.prop(light, "color",text="")
        row = box.row()
        row.label(text="Energy")
        row.prop(light, "energy",text="")
        row = box.row()
        row.label(text="Specular")
        row.prop(light, "specular_factor", text="")
        row = box.row()
        row.prop(light, "use_custom_distance", text="Use Custom Distance")
        if light.use_custom_distance:
            row.prop(light,"cutoff_distance",text="Distance")

        if light.type in {'POINT', 'SPOT', 'SUN'}:
            row = box.row()
            row.label(text="Radius")            
            row.prop(light, "shadow_soft_size", text="")
        elif light.type == 'AREA':
            box = layout.box()
            row = box.row()
            row.label(text="Shape:")
            row.prop(light, "shape",expand=True)

            sub = box.column(align=True)

            if light.shape in {'SQUARE', 'DISK'}:
                row = sub.row(align=True)
                row.label(text="Size:")     
                row.prop(light, "size",text="")
            elif light.shape in {'RECTANGLE', 'ELLIPSE'}:
                row = sub.row(align=True)
                row.label(text="Size:")

                row.prop(light, "size", text="X")
                row.prop(light, "size_y", text="Y")
        
        if light.type == 'SPOT':
            box = layout.box()
            row = box.row()        
            row.label(text="Spot Size:")    
            row.prop(light, "spot_size", text="")
            row = box.row()        
            row.label(text="Spot Blend:")                
            row.prop(light, "spot_blend", text="", slider=True)

            box.prop(light, "show_cone")            

        box = layout.box()
        box.prop(light, "use_shadow", text="Use Shadows")
        box.active = light.use_shadow

        col = box.column()
        row = col.row(align=True)
        row.label(text="Clip:")
        row.prop(light, "shadow_buffer_clip_start", text="Start")
        if light.type == 'SUN':
            row.prop(light, "shadow_buffer_clip_end", text="End")

        # row = col.row(align=True)
        # row.label(text="Softness:")
        # row.prop(light, "shadow_buffer_soft", text="")

        # col.separator()

        # row = col.row(align=True)
        # row.label(text="Bias:")
        # row.prop(light, "shadow_buffer_bias", text="")
        # row = col.row(align=True)
        # row.label(text="Bleed Bias:")        
        # row.prop(light, "shadow_buffer_bleed_bias", text="")        
        # row = col.row(align=True)
        # row.label(text="Exponent:")        
        # row.prop(light, "shadow_buffer_exp", text="")

        # col.separator()

        # col.prop(light, "use_contact_shadow", text="Use Contact Shadows")
        # if light.use_shadow and light.use_contact_shadow:
        #     col = box.column()
        #     row = col.row(align=True)
        #     row.label(text="Distance:")  
        #     row.prop(light, "contact_shadow_distance", text="")
        #     row = col.row(align=True)
        #     row.label(text="Softness:")  
        #     row.prop(light, "contact_shadow_soft_size", text="")
        #     row = col.row(align=True)
        #     row.label(text="Bias:")          
        #     row.prop(light, "contact_shadow_bias", text="")
        #     row = col.row(align=True)
        #     row.label(text="Thickness:")          
        #     row.prop(light, "contact_shadow_thickness", text="")

        # if light.type == 'SUN' and light.use_shadow:
        #     box = layout.box()
        #     box.label(text="Sun Shadow Settings")
        #     row = box.row(align=True)
        #     row.label(text="Cascade Count:")                
        #     row.prop(light, "shadow_cascade_count", text="")
        #     row = box.row(align=True)
        #     row.label(text="Fade:")                 
        #     row.prop(light, "shadow_cascade_fade", text="")

        #     row = box.row(align=True)
        #     row.label(text="Max Distance:")      
        #     row.prop(light, "shadow_cascade_max_distance", text="")
        #     row = box.row(align=True)
        #     row.label(text="Distribution:")                  
        #     row.prop(light, "shadow_cascade_exponent", text="")

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_floor_prompts(bpy.types.Operator):
    bl_idname = "home_builder.floor_prompts"
    bl_label = "Floor Prompts"
    
    mapping_node = None

    def check(self, context):
        return True

    def invoke(self,context,event):
        self.mapping_node = None
        floor = context.object
        for slot in floor.material_slots:
            mat = slot.material
            if mat:
                for node in mat.node_tree.nodes:
                    if node.type == 'MAPPING':
                        self.mapping_node = node

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=150)
        
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        if self.mapping_node:
            col.label(text="Texture Mapping")
            col.prop(self.mapping_node.inputs[1],'default_value',text="Location")
            col.prop(self.mapping_node.inputs[2],'default_value',text="Rotation")
            col.prop(self.mapping_node.inputs[3],'default_value',text="Scale")
        else:
            col.label(text="No Material Found")

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_collect_walls(bpy.types.Operator):
    bl_idname = "home_builder.collect_walls"
    bl_label = "Collect Walls"
    bl_description = "This collects all of the walls in the current scene"
    bl_options = {'UNDO'}

    def execute(self,context):
        props = hb_utils.get_scene_props(context.scene)
        for wall in props.walls:
            props.walls.remove(0)
        for obj in context.scene.objects:
            if 'IS_WALL_BP' in obj:
                wall = props.walls.add()
                wall.obj_bp = obj
                for child in wall.obj_bp.children:
                    if child.type == 'MESH':
                        wall.wall_mesh = child

        return {'FINISHED'}    


class home_builder_OT_show_hide_walls(bpy.types.Operator):
    bl_idname = "home_builder.show_hide_walls"
    bl_label = "Show Hide Walls"
    bl_description = "This toggles the walls visibility"
    bl_options = {'UNDO'}

    wall_obj_bp: bpy.props.StringProperty(name="Wall Base Point Name")

    def hide_children(self,obj,context):
        if obj.name in context.view_layer.objects:
            if obj.type in {'MESH','CURVE'}:
                if obj.hide_get():
                    obj.hide_set(False)
                else:
                    obj.hide_set(True)
        for child in obj.children:
            self.hide_children(child,context)

    def execute(self,context):
        wall_bp = bpy.data.objects[self.wall_obj_bp]
        self.hide_children(wall_bp,context)
        return {'FINISHED'}    


class home_builder_OT_delete_wall(bpy.types.Operator):
    bl_idname = "home_builder.delete_wall"
    bl_label = "Delete Wall"
    bl_description = "This toggles the walls visibility"
    bl_options = {'UNDO'}

    wall_obj_bp_name: bpy.props.StringProperty(name="Wall Base Point Name")

    def get_wall(self,obj,wall_list):
        if 'IS_WALL_BP' in obj and obj not in wall_list:
            wall_list.append(obj)
        if obj.parent:
            self.get_wall(obj.parent,wall_list)
        return wall_list

    def execute(self,context):
        walls = []
        for obj in context.selected_objects:
            walls = self.get_wall(obj,walls)
        for wall_bp in walls:
            wall = pc_types.Assembly(wall_bp)
            prev_wall_bp = pc_utils.get_connected_left_wall_bp(wall)
            next_wall_bp = pc_utils.get_connected_right_wall_bp(wall)
            if prev_wall_bp:
                prev_wall_bp.home_builder.connected_object = None
                prev_wall = pc_types.Assembly(prev_wall_bp)
                prev_wall.get_prompt("Right Angle").set_value(0)
            if next_wall_bp:
                mat_world = next_wall_bp.matrix_world.translation.copy()
                next_wall = pc_types.Assembly(next_wall_bp)
                next_wall.get_prompt("Left Angle").set_value(0)
                next_wall.obj_bp.matrix_world.translation = mat_world
            pc_utils.delete_object_and_children(wall_bp)
        return {'FINISHED'}    


class home_builder_OT_hide_wall(bpy.types.Operator):
    bl_idname = "home_builder.hide_wall"
    bl_label = "Hide Wall"
    bl_description = "This toggles the walls visibility"
    bl_options = {'UNDO'}

    wall_obj_bp: bpy.props.StringProperty(name="Wall Base Point Name")

    def hide_children(self,obj,context):
        if obj.name in context.view_layer.objects:
            if obj.type in {'MESH','CURVE'}:
                obj.hide_set(True)
        for child in obj.children:
            self.hide_children(child,context)

    def execute(self,context):
        wall_bp = bpy.data.objects[self.wall_obj_bp]
        self.hide_children(wall_bp,context)
        return {'FINISHED'}    


class home_builder_OT_show_wall(bpy.types.Operator):
    bl_idname = "home_builder.show_wall"
    bl_label = "Show Wall"
    bl_description = "This toggles the walls visibility"
    bl_options = {'UNDO'}

    wall_obj_bp: bpy.props.StringProperty(name="Wall Base Point Name")

    def hide_children(self,obj,context):
        if obj.name in context.view_layer.objects:
            if obj.type in {'MESH','CURVE'}:
                obj.hide_set(False)
        for child in obj.children:
            self.hide_children(child,context)

    def execute(self,context):
        wall_bp = bpy.data.objects[self.wall_obj_bp]
        self.hide_children(wall_bp,context)
        return {'FINISHED'}    


class home_builder_OT_show_wall_front_view(bpy.types.Operator):
    bl_idname = "home_builder.show_wall_front_view"
    bl_label = "Show Wall Front View"

    wall_bp_name: bpy.props.StringProperty("Wall BP Name")

    def execute(self, context):
        for wall in context.scene.home_builder.walls:
            bpy.ops.home_builder.show_wall(wall_obj_bp=wall.obj_bp.name)       

        area = None
        for a in context.window.screen.areas:
            if a.type == 'VIEW_3D':
                area = a
        r3d = area.spaces[0].region_3d
        wall_bp = bpy.data.objects[self.wall_bp_name]
        wall = pc_types.Assembly(wall_bp)
        wall_loc_x = wall.obj_bp.location.x
        wall_loc_y = wall.obj_bp.location.y
        wall_loc_z = (wall.obj_z.location.z/2)
        wall_z_rot = round(math.degrees(wall.obj_bp.rotation_euler.z))
        r3d.view_location = (wall_loc_x,wall_loc_y,wall_loc_z)
        if wall_z_rot == 0:
            r3d.view_rotation = (.7071,.7071,0,0)
        if wall_z_rot == 90:
            r3d.view_rotation = (.5,.5,.5,.5)
        if wall_z_rot == -90:
            r3d.view_rotation = (.5,.5,-.5,-.5)
        if wall_z_rot == 180:
            r3d.view_rotation = (0,0,.7071,.7071)

        for wall in context.scene.home_builder.walls:
            if wall.obj_bp.name != self.wall_bp_name:
                bpy.ops.home_builder.hide_wall(wall_obj_bp=wall.obj_bp.name)

        if r3d.is_perspective:
            bpy.ops.view3d.view_persportho()
            
        context.view_layer.update()
        return {'FINISHED'}


class home_builder_OT_snap_line_prompts(bpy.types.Operator):
    bl_idname = "home_builder.snap_line_prompts"
    bl_label = "Snap Line Prompts"

    x_loc_left: bpy.props.FloatProperty(name="X Location Left",unit='LENGTH',precision=4)
    x_loc_right: bpy.props.FloatProperty(name="X Location Right",unit='LENGTH',precision=4)

    anchor_x: bpy.props.EnumProperty(name="Anchor X",
                                     items=[('LEFT',"Left","Left"),
                                            ('RIGHT',"Right","Right")])

    wall = None
    snap_line = None

    def check(self, context):
        if self.anchor_x == 'LEFT':
            self.snap_line.location.x = self.x_loc_left
        if self.anchor_x == 'RIGHT':
            self.snap_line.location.x = self.wall.obj_x.location.x - self.x_loc_right
        return True

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self,context,event):
        self.snap_line = context.object
        wall_bp = pc_utils.get_bp_by_tag(self.snap_line,'IS_WALL_BP')
        self.wall = pc_types.Assembly(wall_bp)
        self.x_loc_left = self.snap_line.location.x
        self.x_loc_right = self.wall.obj_x.location.x - self.snap_line.location.x
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'anchor_x',expand=True)
        if self.anchor_x == 'LEFT':
            layout.prop(self,'x_loc_left',text="Dim from Left")
        if self.anchor_x == 'RIGHT':
            layout.prop(self,'x_loc_right',text="Dim from Right")


class home_builder_OT_add_wall_snap_line(bpy.types.Operator):
    bl_idname = "home_builder.add_wall_snap_line"
    bl_label = "Add Wall Snap Line"

    blf_text = ""
    region = None
    number_of_clicks = 0
    first_point = (0,0,0)
    second_point = (0,0,0)
    hit_location = (0,0,0)
    hit_grid = False
    mod = None
    snap_line = None
    view_name = ""

    blf_text = ""

    def set_curve_to_vector(self,context):
        self.snap_line.select_set(True)
        context.view_layer.objects.active = self.snap_line
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.mode_set(mode='OBJECT')

    def get_snap_location(self,selected_point):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        x = math.ceil(selected_point[0]/sv)
        y = math.ceil(selected_point[1]/sv)
        z = math.ceil(selected_point[2]/sv)
        return x*sv, y*sv, z*sv
    
    def get_snap_value(self,value):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        return math.ceil(value/sv)*sv

    def delete_dims(self):
        bpy.data.objects.remove(self.left_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.right_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.center_dim.obj, do_unlink=True)

    def create_dims(self):
        self.left_dim = pc_types.GeoNodeDimension()
        self.left_dim.create()
        self.left_dim.set_input("Leader Length",pc_unit.inch(3))
        self.left_dim.obj.rotation_euler.x = math.radians(90)
        self.left_dim.obj.select_set(False)
        self.left_dim.obj.show_in_front = True

        self.right_dim = pc_types.GeoNodeDimension()
        self.right_dim.create()
        self.right_dim.set_input("Leader Length",pc_unit.inch(3))
        self.right_dim.obj.rotation_euler.x = math.radians(90)
        self.right_dim.obj.select_set(False)
        self.right_dim.obj.show_in_front = True

        self.center_dim = pc_types.GeoNodeDimension()
        self.center_dim.create()
        self.center_dim.set_input("Leader Length",pc_unit.inch(0))
        self.center_dim.obj.rotation_euler.x = math.radians(90)
        self.center_dim.obj.select_set(False)
        self.center_dim.obj.color = (0,0,0,1)
        self.center_dim.obj.show_in_front = True

    def get_left_snap_point(self,snap_points):
        for index, sp in enumerate(snap_points):
            if sp.name == self.snap_line.name and index != 0:
                return snap_points[index-1]
        return None

    def get_right_snap_point(self,snap_points):
        for index, sp in enumerate(snap_points):
            if sp.name == self.snap_line.name and index != len(snap_points)-1:
                return snap_points[index+1]
        return None

    def update_dims(self,wall_bp):
        
        if wall_bp:
            self.left_dim.obj.hide_viewport = False
            self.right_dim.obj.hide_viewport = False
            self.center_dim.obj.hide_viewport = False
            self.left_dim.obj.parent = wall_bp        
            self.right_dim.obj.parent = wall_bp    
            self.center_dim.obj.parent = wall_bp
            wall = pc_types.Assembly(wall_bp)
            self.left_dim.obj.location.z = wall.obj_z.location.z
            self.right_dim.obj.location.z = wall.obj_z.location.z
            self.center_dim.obj.location.z = self.hit_location[2]

            wall_length = wall.obj_x.location.x
            snap_x = self.snap_line.location.x
            
            search_point = (self.snap_line.location.x,0,self.hit_location[2])
            left_assembly = pc_placement_utils.get_left_wall_collision_assembly_from_selected_point(wall,search_point)
            right_assembly = pc_placement_utils.get_right_wall_collision_assembly_from_selected_point(wall,search_point)
            snap_points = pc_placement_utils.get_snap_points(wall)
            left_sp = self.get_left_snap_point(snap_points)
            right_sp = self.get_right_snap_point(snap_points)

            #GET LEFT SNAP LOCATION
            cal_left_x_snap = 0
            if left_assembly and left_sp:
                left_assembly_x_snap = left_assembly.obj_bp.location.x + left_assembly.obj_x.location.x
                left_snap_location = left_sp.location.x
                if left_assembly_x_snap > left_snap_location:
                    cal_left_x_snap = left_assembly_x_snap
                else:
                    cal_left_x_snap = left_snap_location
            elif left_assembly:
                cal_left_x_snap = left_assembly.obj_bp.location.x + left_assembly.obj_x.location.x
            elif left_sp:
                cal_left_x_snap = left_sp.location.x
            else:
                cal_left_x_snap = 0
            self.left_dim.obj.data.splines[0].bezier_points[0].co = (cal_left_x_snap,0,0)
            self.left_dim.obj.data.splines[0].bezier_points[1].co = (snap_x,0,0)   

            #GET RIGHT SNAP LOCATION
            cal_right_x_snap = 0
            if right_assembly and right_sp:
                if right_assembly.obj_bp.location.x < right_sp.location.x:
                    cal_right_x_snap = right_assembly.obj_bp.location.x
                else:
                    cal_right_x_snap = right_sp.location.x
            elif right_assembly:
                cal_right_x_snap = right_assembly.obj_bp.location.x
            elif right_sp:
                cal_right_x_snap = right_sp.location.x
            else:
                cal_right_x_snap = wall_length
            self.right_dim.obj.data.splines[0].bezier_points[0].co = (snap_x,0,0)
            self.right_dim.obj.data.splines[0].bezier_points[1].co = (cal_right_x_snap,0,0)  

            left_x = self.left_dim.obj.data.splines[0].bezier_points[0].co[0]
            right_x = self.right_dim.obj.data.splines[0].bezier_points[1].co[0]
            self.center_dim.obj.data.splines[0].bezier_points[0].co = (left_x,0,0)
            self.center_dim.obj.data.splines[0].bezier_points[1].co = (right_x,0,0)   

            #MOVE TEXT IF SMALL DIMENSION
            left_dim_length = pc_utils.calc_distance(self.left_dim.obj.data.splines[0].bezier_points[0].co,self.left_dim.obj.data.splines[0].bezier_points[1].co)
            right_dim_length = pc_utils.calc_distance(self.right_dim.obj.data.splines[0].bezier_points[0].co,self.right_dim.obj.data.splines[0].bezier_points[1].co)
            if left_dim_length <= pc_unit.inch(7):
                self.left_dim.set_input("Offset Text From Line",True)
            else:
                self.left_dim.set_input("Offset Text From Line",False)
            if right_dim_length <= pc_unit.inch(7):
                self.right_dim.set_input("Offset Text From Line",True)  
            else:
                self.right_dim.set_input("Offset Text From Line",False)                          
        else:
            self.center_dim.obj.hide_viewport = True
            self.left_dim.obj.hide_viewport = True
            self.right_dim.obj.hide_viewport = True

    def modal(self, context, event):
        
        bpy.context.workspace.status_text_set(text="COMMAND: Add Snap Line to Wall   [Move Cursor to Wall]   [RIGHT CLICK: Cancel Command]")
        context.area.tag_redraw()

        wall_bp = None

        if self.number_of_clicks == 0:
            snap_point = self.get_snap_location(self.hit_location)
            self.snap_line.location = snap_point
            self.snap_line.data.splines[0].bezier_points[0].co = (0,0,0)
            self.snap_line.data.splines[0].bezier_points[1].co = (0,0,0)  
            if self.hit_object:
                wall_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_WALL_BP')
                if wall_bp:
                    bpy.context.workspace.status_text_set(text="COMMAND: Add Snap Line to Wall   [LEFT CLICK: Add Snap Line]   [RIGHT CLICK: Cancel Command]")
                    wall = pc_types.Assembly(wall_bp)
                    self.snap_line.location = self.hit_location
                    self.snap_line.location.z = wall_bp.location.z
                    self.snap_line.parent = wall_bp
                    self.snap_line.matrix_world[0][3] = self.hit_location[0]
                    self.snap_line.matrix_world[1][3] = self.hit_location[1]
                    self.snap_line.location.x = self.get_snap_value(self.snap_line.location.x)
                    self.snap_line.location.y = 0
                    self.snap_line.location.z = 0
                    self.snap_line.rotation_euler = (0,math.radians(-90),0)
                    self.snap_line.data.splines[0].bezier_points[0].co = (0,0,0)
                    self.snap_line.data.splines[0].bezier_points[1].co = (wall.obj_z.location.z,0,0)
                    self.snap_line.data.splines[0].bezier_points[2].co = (wall.obj_z.location.z,wall.obj_y.location.y,0)
                else:
                    self.snap_line.parent = None
            else:
                self.snap_line.parent = None
            self.update_dims(wall_bp)

        if event.type == 'MOUSEMOVE' or event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self.snap_line.hide_viewport = True
            pc_snap.main(self, event.ctrl, context)
            self.snap_line.hide_viewport = False            
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS' and wall_bp:
            self.snap_line.hide_viewport = False
            self.delete_dims()
            
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            
            self.delete_dims()
            bpy.data.objects.remove(self.snap_line, do_unlink=True)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.region = pc_utils.get_3d_view_region(context)
        if context.area.type == 'VIEW_3D':
            self.mouse_pos = Vector()
            self.hit_object = None
            self.number_of_clicks = 0

            self.create_dims()
            curve = bpy.data.curves.new('SNAPLINE','CURVE')
            spline = curve.splines.new('BEZIER')
            spline.bezier_points.add(2)
            self.snap_line = bpy.data.objects.new('SNAPLINE',curve)
            self.snap_line.rotation_euler.y = math.radians(-90)
            self.snap_line.data.bevel_depth = pc_unit.inch(.25)
            self.snap_line.color = (0,0,0,1)
            self.snap_line['IS_WALL_SNAP_POINT'] = True
            self.snap_line['PROMPT_ID'] = 'home_builder.snap_line_prompts'
            context.view_layer.active_layer_collection.collection.objects.link(self.snap_line)
            self.set_curve_to_vector(context)
            #ADD Array Modifier and show in plan and elevation view
            #snap to wall
            #Assign tag
            #Use tag in collisions

            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(pc_snap.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
        

class home_builder_OT_add_wall_elevation_dim(bpy.types.Operator):
    bl_idname = "home_builder.add_wall_elevation_dim"
    bl_label = "Add Wall Elevation Dim"

    blf_text = ""
    region = None
    number_of_clicks = 0
    first_point = (0,0,0)
    second_point = (0,0,0)
    hit_location = (0,0,0)
    hit_grid = False
    mod = None
    snap_line = None
    view_name = ""

    def set_curve_to_vector(self,context):
        self.snap_line.select_set(True)
        context.view_layer.objects.active = self.snap_line
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.mode_set(mode='OBJECT')

    def get_snap_location(self,selected_point):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        x = math.ceil(selected_point[0]/sv)
        y = math.ceil(selected_point[1]/sv)
        z = math.ceil(selected_point[2]/sv)
        return x*sv, y*sv, z*sv
    
    def get_snap_value(self,value):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        return math.ceil(value/sv)*sv

    def delete_dims(self):
        bpy.data.objects.remove(self.left_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.right_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.snap_line, do_unlink=True)

    def create_dims(self):
        self.left_dim = pc_types.GeoNodeDimension()
        self.left_dim.create()
        self.left_dim.set_input("Leader Length",pc_unit.inch(3))
        self.left_dim.obj.rotation_euler.x = math.radians(90)
        self.left_dim.obj.select_set(False)
        self.left_dim.obj.show_in_front = True

        self.right_dim = pc_types.GeoNodeDimension()
        self.right_dim.create()
        self.right_dim.set_input("Leader Length",pc_unit.inch(3))
        self.right_dim.obj.rotation_euler.x = math.radians(90)
        self.right_dim.obj.select_set(False)
        self.right_dim.obj.show_in_front = True

        self.center_dim = pc_types.GeoNodeDimension()
        self.center_dim.create()
        self.center_dim.set_input("Leader Length",pc_unit.inch(0))
        self.center_dim.obj.rotation_euler.x = math.radians(90)
        self.center_dim.obj.select_set(False)
        self.center_dim.obj.color = (0,0,0,1)
        self.center_dim.obj.show_in_front = True

    def get_left_snap_point(self,snap_points):
        for index, sp in enumerate(snap_points):
            if sp.name == self.snap_line.name and index != 0:
                return snap_points[index-1]
        return None

    def get_right_snap_point(self,snap_points):
        for index, sp in enumerate(snap_points):
            if sp.name == self.snap_line.name and index != len(snap_points)-1:
                return snap_points[index+1]
        return None

    def update_dims(self,wall_bp):
        
        if wall_bp:
            self.left_dim.obj.hide_viewport = True
            self.right_dim.obj.hide_viewport = True
            self.center_dim.obj.hide_viewport = False
            self.left_dim.obj.parent = wall_bp        
            self.right_dim.obj.parent = wall_bp    
            self.center_dim.obj.parent = wall_bp
            wall = pc_types.Assembly(wall_bp)
            self.left_dim.obj.location.z = wall.obj_z.location.z
            self.right_dim.obj.location.z = wall.obj_z.location.z
            self.center_dim.obj.location.z = self.hit_location[2]

            wall_length = wall.obj_x.location.x
            snap_x = self.snap_line.location.x
            
            sel_window_bp = None
            sel_entry_door_bp = None
            sel_appliance_bp = None
            sel_cabinet_bp = None
            hit_assembly = None
            if self.hit_object:
                sel_window_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_WINDOW_BP')
                sel_entry_door_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_ENTRY_DOOR_BP')
                sel_appliance_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_APPLIANCE_BP')
                sel_cabinet_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_CABINET_FF_STARTER_BP')

            if hit_assembly == None and sel_window_bp:
                hit_assembly = pc_types.Assembly(sel_window_bp)
            if hit_assembly == None and sel_entry_door_bp:
                hit_assembly = pc_types.Assembly(sel_entry_door_bp)
            if hit_assembly == None and sel_appliance_bp:
                hit_assembly = pc_types.Assembly(sel_appliance_bp)
            if hit_assembly == None and sel_cabinet_bp:
                hit_assembly = pc_types.Assembly(sel_cabinet_bp)

            if hit_assembly: #SELECTED ASSEMBLY
                left_x = hit_assembly.obj_bp.location.x
                right_x = hit_assembly.obj_bp.location.x + hit_assembly.obj_x.location.x
                self.center_dim.obj.data.splines[0].bezier_points[0].co = (left_x,0,0)
                self.center_dim.obj.data.splines[0].bezier_points[1].co = (right_x,0,0)   
            else:
                search_point = (self.snap_line.location.x,0,self.hit_location[2])
                left_assembly = pc_placement_utils.get_left_wall_collision_assembly_from_selected_point(wall,search_point)
                right_assembly = pc_placement_utils.get_right_wall_collision_assembly_from_selected_point(wall,search_point)
                snap_points = pc_placement_utils.get_snap_points(wall)
                left_sp = self.get_left_snap_point(snap_points)
                right_sp = self.get_right_snap_point(snap_points)

                #GET LEFT SNAP LOCATION
                cal_left_x_snap = 0
                if left_assembly and left_sp:
                    left_assembly_x_snap = left_assembly.obj_bp.location.x + left_assembly.obj_x.location.x
                    left_snap_location = left_sp.location.x
                    if left_assembly_x_snap > left_snap_location:
                        cal_left_x_snap = left_assembly_x_snap
                    else:
                        cal_left_x_snap = left_snap_location
                elif left_assembly:
                    cal_left_x_snap = left_assembly.obj_bp.location.x + left_assembly.obj_x.location.x
                elif left_sp:
                    cal_left_x_snap = left_sp.location.x
                else:
                    cal_left_x_snap = 0
                self.left_dim.obj.data.splines[0].bezier_points[0].co = (cal_left_x_snap,0,0)
                self.left_dim.obj.data.splines[0].bezier_points[1].co = (snap_x,0,0)   

                #GET RIGHT SNAP LOCATION
                cal_right_x_snap = 0
                if right_assembly and right_sp:
                    if right_assembly.obj_bp.location.x < right_sp.location.x:
                        cal_right_x_snap = right_assembly.obj_bp.location.x
                    else:
                        cal_right_x_snap = right_sp.location.x
                elif right_assembly:
                    cal_right_x_snap = right_assembly.obj_bp.location.x
                elif right_sp:
                    cal_right_x_snap = right_sp.location.x
                else:
                    cal_right_x_snap = wall_length
                self.right_dim.obj.data.splines[0].bezier_points[0].co = (snap_x,0,0)
                self.right_dim.obj.data.splines[0].bezier_points[1].co = (cal_right_x_snap,0,0)  

                left_x = self.left_dim.obj.data.splines[0].bezier_points[0].co[0]
                right_x = self.right_dim.obj.data.splines[0].bezier_points[1].co[0]
                self.center_dim.obj.data.splines[0].bezier_points[0].co = (left_x,0,0)
                self.center_dim.obj.data.splines[0].bezier_points[1].co = (right_x,0,0)   

                #MOVE TEXT IF SMALL DIMENSION
                center_dim_dim_length = pc_utils.calc_distance(self.center_dim.obj.data.splines[0].bezier_points[0].co,self.center_dim.obj.data.splines[0].bezier_points[1].co)
                if center_dim_dim_length <= pc_unit.inch(7):
                    self.center_dim.set_input("Offset Text From Line",True)
                else:
                    self.center_dim.set_input("Offset Text From Line",False)   
                self.center_dim.set_dim_decimal()       
        else:
            self.center_dim.obj.hide_viewport = True
            self.left_dim.obj.hide_viewport = True
            self.right_dim.obj.hide_viewport = True

    def modal(self, context, event):
        
        bpy.context.workspace.status_text_set(text="COMMAND: Add Elevation Dimension to Wall   [Move Cursor to Wall]   [RIGHT CLICK: Cancel Command]")
        context.area.tag_redraw()

        wall_bp = None

        if self.number_of_clicks == 0:
            snap_point = self.get_snap_location(self.hit_location)
            self.snap_line.location = snap_point
            self.snap_line.data.splines[0].bezier_points[0].co = (0,0,0)
            self.snap_line.data.splines[0].bezier_points[1].co = (0,0,0)  
            if self.hit_object:
                wall_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_WALL_BP')
                if wall_bp:
                    bpy.context.workspace.status_text_set(text="COMMAND: Add Elevation Dimension to Wall   [LEFT CLICK: Place Dimension]   [RIGHT CLICK: Cancel Command]")
                    wall = pc_types.Assembly(wall_bp)
                    self.snap_line.location = self.hit_location
                    self.snap_line.location.z = wall_bp.location.z
                    self.snap_line.parent = wall_bp
                    self.snap_line.matrix_world[0][3] = self.hit_location[0]
                    self.snap_line.matrix_world[1][3] = self.hit_location[1]
                    self.snap_line.location.x = self.get_snap_value(self.snap_line.location.x)
                    self.snap_line.location.y = 0
                    self.snap_line.location.z = 0
                    self.snap_line.rotation_euler = (0,math.radians(-90),0)
                    self.snap_line.data.splines[0].bezier_points[0].co = (0,0,0)
                    self.snap_line.data.splines[0].bezier_points[1].co = (wall.obj_z.location.z,0,0)
                    self.snap_line.data.splines[0].bezier_points[2].co = (wall.obj_z.location.z,wall.obj_y.location.y,0)
                    self.snap_line.hide_viewport = True
                else:
                    self.snap_line.parent = None
            else:
                self.snap_line.parent = None
            self.update_dims(wall_bp)

        if event.type == 'MOUSEMOVE' or event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self.snap_line.hide_viewport = True
            pc_snap.main(self, event.ctrl, context)
            # self.snap_line.hide_viewport = True            
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS' and wall_bp:
            # self.snap_line.hide_viewport = False
            self.delete_dims()
            bpy.context.workspace.status_text_set(text=None)
            
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.context.workspace.status_text_set(text=None)
            self.delete_dims()
            bpy.data.objects.remove(self.center_dim.obj, do_unlink=True)
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.region = pc_utils.get_3d_view_region(context)
        if context.area.type == 'VIEW_3D':
            self.mouse_pos = Vector()
            self.hit_object = None
            self.number_of_clicks = 0

            self.create_dims()
            curve = bpy.data.curves.new('SNAPLINE','CURVE')
            spline = curve.splines.new('BEZIER')
            spline.bezier_points.add(2)
            self.snap_line = bpy.data.objects.new('SNAPLINE',curve)
            self.snap_line.rotation_euler.y = math.radians(-90)
            self.snap_line.data.bevel_depth = pc_unit.inch(.25)
            # self.snap_line.color = (0,0,0,1)
            self.snap_line['IS_WALL_SNAP_POINT'] = True
            # self.snap_line['PROMPT_ID'] = 'home_builder.snap_line_prompts'
            context.view_layer.active_layer_collection.collection.objects.link(self.snap_line)
            self.set_curve_to_vector(context)

            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(pc_snap.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class HOMEBUILDER_UL_walls(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.obj_bp:
            layout.label(text=item.obj_bp.name)
            layout.operator('home_builder.show_wall_front_view',text="View").wall_bp_name = item.obj_bp.name
            if item.wall_mesh.hide_get():
                layout.operator('home_builder.show_hide_walls',text="",icon='HIDE_ON').wall_obj_bp = item.obj_bp.name
            else:
                layout.operator('home_builder.show_hide_walls',text="",icon='HIDE_OFF').wall_obj_bp = item.obj_bp.name


classes = (
    home_builder_OT_wall_prompts,
    home_builder_OT_draw_multiple_walls,
    home_builder_OT_draw_floor_plane,
    home_builder_OT_add_room_light,
    home_builder_OT_light_prompts,
    home_builder_OT_floor_prompts,
    home_builder_OT_collect_walls,
    home_builder_OT_show_hide_walls,
    home_builder_OT_delete_wall,
    home_builder_OT_hide_wall,
    home_builder_OT_show_wall,
    home_builder_OT_show_wall_front_view,
    home_builder_OT_snap_line_prompts,
    home_builder_OT_add_wall_snap_line,
    home_builder_OT_add_wall_elevation_dim,
    HOMEBUILDER_UL_walls,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
