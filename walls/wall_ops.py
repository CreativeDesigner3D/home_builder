import bpy
import os
import math
import time
import inspect
from pc_lib import pc_utils, pc_types, pc_unit
from .. import hb_utils
# from .. import home_builder_pointers
from . import wall_library

class home_builder_OT_draw_multiple_walls(bpy.types.Operator):
    bl_idname = "home_builder.draw_multiple_walls"
    bl_label = "Draw Multiple Walls"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    region = None

    drawing_plane = None

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

    def reset_properties(self):
        self.drawing_plane = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""
        self.obj_wall_meshes = []        

    def execute(self, context):
        self.region = pc_utils.get_3d_view_region(context)
        self.reset_properties()   
        self.create_drawing_plane(context)
        self.create_wall()
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
        #TODO: ASSIGN POINTERS
        # home_builder_pointers.assign_pointer_to_assembly(wall,"Walls")
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

        self.dim = pc_types.Dimension()
        self.dim.create_dimension()
        self.dim.obj_bp.rotation_euler.y = 0
        self.dim.obj_y.location.y = pc_unit.inch(20)
        self.dim.obj_bp.parent = self.current_wall.obj_bp
        self.dim.obj_x.location.x = self.current_wall.obj_x.location.x
        self.dim.obj_bp.location.z = self.current_wall.obj_z.location.z + .01
        self.dim.obj_bp.hide_viewport = False
        self.dim.obj_x.hide_viewport = False
        self.dim.obj_y.hide_viewport = False
        self.dim.obj_z.hide_viewport = False
        self.dim.get_prompt("Font Size").set_value(0)
        self.dim.get_prompt("Arrow Height").set_value(pc_unit.inch(4))
        self.dim.get_prompt("Arrow Length").set_value(pc_unit.inch(5))
        self.dim.get_prompt("Line Thickness").set_value(pc_unit.inch(.5))
        self.dim.update_dim_text()        

    def connect_walls(self):
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
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
            obj.display_type = 'TEXTURED'   
            self.obj_wall_meshes.append(obj)
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def set_type_value(self,event):
        if event.value == 'PRESS':
            if event.type == "ONE" or event.type == "NUMPAD_1":
                self.typed_value += "1"
            if event.type == "TWO" or event.type == "NUMPAD_2":
                self.typed_value += "2"
            if event.type == "THREE" or event.type == "NUMPAD_3":
                self.typed_value += "3"
            if event.type == "FOUR" or event.type == "NUMPAD_4":
                self.typed_value += "4"
            if event.type == "FIVE" or event.type == "NUMPAD_5":
                self.typed_value += "5"
            if event.type == "SIX" or event.type == "NUMPAD_6":
                self.typed_value += "6"
            if event.type == "SEVEN" or event.type == "NUMPAD_7":
                self.typed_value += "7"
            if event.type == "EIGHT" or event.type == "NUMPAD_8":
                self.typed_value += "8"
            if event.type == "NINE" or event.type == "NUMPAD_9":
                self.typed_value += "9"
            if event.type == "ZERO" or event.type == "NUMPAD_0":
                self.typed_value += "0"
            if event.type == "PERIOD" or event.type == "NUMPAD_PERIOD":
                last_value = self.typed_value[-1:]
                if last_value != ".":
                    self.typed_value += "."
            if event.type == 'BACK_SPACE':
                if self.typed_value != "":
                    self.typed_value = self.typed_value[:-1]

    def modal(self, context, event):
        context.area.tag_redraw()
        self.set_type_value(event)

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)
        self.set_end_angles()            

        if self.event_is_place_first_point(event):
            self.starting_point = (selected_point[0],selected_point[1],0)
            return {'RUNNING_MODAL'}
            
        if self.event_is_place_next_point(event):
            pc_utils.delete_object_and_children(self.dim.obj_bp)
            self.set_placed_properties(self.current_wall.obj_bp)
            self.create_wall()
            self.connect_walls()
            self.typed_value = ""
            self.starting_point = (selected_point[0],selected_point[1],0)
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

    def set_end_angles(self):
        if self.previous_wall and self.current_wall:
            left_angle = self.current_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 

            prev_rot = round(math.degrees(self.previous_wall.obj_bp.rotation_euler.z),0) 
            rot = round(math.degrees(self.current_wall.obj_bp.rotation_euler.z),0)
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
            value = eval(self.typed_value)
            if bpy.context.scene.unit_settings.system == 'METRIC':
                self.current_wall.obj_x.location.x = pc_unit.millimeter(float(value))
            else:
                self.current_wall.obj_x.location.x = pc_unit.inch(float(value))     

    def position_object(self,selected_point,selected_obj):
        if self.starting_point == ():
            self.current_wall.obj_bp.location.x = selected_point[0]
            self.current_wall.obj_bp.location.y = selected_point[1]
            self.current_wall.obj_bp.location.z = 0
        else:
            x = selected_point[0] - self.starting_point[0]
            y = selected_point[1] - self.starting_point[1]
            parent_rot = self.current_wall.obj_bp.parent.rotation_euler.z if self.current_wall.obj_bp.parent else 0
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
            
            self.dim.obj_x.location.x = self.current_wall.obj_x.location.x
            
            if self.current_wall.obj_bp.rotation_euler.z > math.radians(179):
                self.dim.obj_text.scale.x = -1
                self.dim.obj_text.scale.y = -1
            else:
                self.dim.obj_text.scale.x = 1
                self.dim.obj_text.scale.y = 1
            font_size = self.dim.get_prompt("Font Size")
            if self.dim.obj_x.location.x == 0:
                font_size.set_value(0)  
            elif self.dim.obj_x.location.x >= pc_unit.inch(30):
                font_size.set_value(.2) 
            elif self.dim.obj_x.location.x >= pc_unit.inch(20):
                font_size.set_value(.1)                 
            elif self.dim.obj_x.location.x >= pc_unit.inch(15):
                font_size.set_value(.05)             
            elif self.dim.obj_x.location.x >= pc_unit.inch(10):
                font_size.set_value(.03)             
            elif self.dim.obj_x.location.x >= pc_unit.inch(5):
                font_size.set_value(.02)             
            else:
                font_size.set_value(0)              
            self.dim.update_dim_text()

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
            if not obj.hide_viewport:
                hb_utils.unwrap_obj(context,obj)
            self.hide_empties(obj.parent)
        print("Wall Unwrap: Draw Time --- %s seconds ---" % (time.time() - start_time))

        pc_utils.delete_object_and_children(self.dim.obj_bp)
        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.current_wall.obj_bp)
        for child in self.current_wall.obj_bp.children:
            obj_list.append(child)
        pc_utils.delete_obj_list(obj_list)
        # bpy.ops.view3d.view_all(center=False)

        return {'FINISHED'}


class home_builder_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "home_builder.wall_prompts"
    bl_label = "Wall Prompts"

    current_wall = None
    previous_wall = None
    next_wall = None

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        prev_rot = 0
        next_rot = 0
        left_angle = self.current_wall.get_prompt("Left Angle")
        right_angle = self.current_wall.get_prompt("Right Angle")    
        rot = math.degrees(self.current_wall.obj_bp.rotation_euler.z)

        if self.previous_wall:
            prev_left_angle = self.previous_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_rot = math.degrees(self.previous_wall.obj_bp.rotation_euler.z)  

        if self.next_wall:
            next_left_angle = self.next_wall.get_prompt("Left Angle")
            next_rot = math.degrees(self.next_wall.obj_bp.rotation_euler.z)  

        if self.next_wall:
            right_angle.set_value((rot-next_rot)/2)
            next_left_angle.set_value((next_rot-rot)/2)

        if self.previous_wall:
            prev_right_angle.set_value((prev_rot-rot)/2)
            left_angle.set_value((rot-prev_rot)/2)

        self.current_wall.obj_prompts.location = self.current_wall.obj_prompts.location
        if self.previous_wall:
            self.previous_wall.obj_prompts.location = self.previous_wall.obj_prompts.location
        if self.next_wall:
            self.next_wall.obj_prompts.location = self.next_wall.obj_prompts.location
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
        self.get_previous_wall(context)
        self.get_next_wall(context)
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=370)

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
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Wall',icon='CONSTRAINT').obj_name = self.current_wall.obj_bp.name
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


class HOMEBUILDER_MT_wall_menu(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        layout = self.layout
        obj_bp = pc_utils.get_assembly_bp(context.object)
        wall_bp = None

        wall_bp = pc_utils.get_bp_by_tag(context.object,'IS_WALL_BP')  
        if wall_bp:

            layout.operator_context = 'INVOKE_DEFAULT'

            #TODO: Implement additional wall commands
            # if wall_bp:
            #     layout.operator('home_builder.move_wall',text="Move Wall - " + door_window_bp.name,icon='OBJECT_ORIGIN').obj_bp_name = door_window_bp.name
            #     layout.operator('home_builder.free_move_wall',text="Grab Wall - " + door_window_bp.name,icon='VIEW_PAN').obj_bp_name = door_window_bp.name
            #     layout.operator('home_builder.duplicate_wall',text="Duplicate Wall - " + door_window_bp.name,icon='DUPLICATE').obj_bp_name = door_window_bp.name
            #     layout.separator()

            layout.operator('home_builder.edit_part',text="Edit Wall",icon='EDITMODE_HLT')
            # layout.separator()
            #TODO: Create Delete Wall Command that keeps connected wall locations
            # layout.operator('home_builder.delete_assembly',text="Delete",icon='X').obj_name = wall_bp.name

classes = (
    home_builder_OT_wall_prompts,
    home_builder_OT_draw_multiple_walls,
    home_builder_OT_draw_floor_plane,
    home_builder_OT_add_room_light,
    home_builder_OT_light_prompts,
    home_builder_OT_floor_prompts,
    HOMEBUILDER_MT_wall_menu
)

register, unregister = bpy.utils.register_classes_factory(classes)        
