import bpy
import math
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        EnumProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
from pc_lib import pc_utils, pc_types, pc_unit, pc_snap
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

def get_view_rotation(context):
    cam = context.scene.camera
    if cam and cam.parent:
        rot = int(math.degrees(cam.parent.rotation_euler.z))
        if rot == 90:
            return "LEFT"
        if rot == 0:
            return "FRONT"
        if rot == -90:
            return "RIGHT"
        if rot == 180:
            return "BACK"                        
    else:
        return "PLAN"

def get_next_point(dim,hit_location,view_name):
    dim.set_input("Leader Length",pc_unit.inch(1)) 
    dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
    x = hit_location[0] - dim.obj.location.x
    y = hit_location[1] - dim.obj.location.y
    z = hit_location[2] - dim.obj.location.z

    if view_name == 'PLAN':
        if math.fabs(x) > math.fabs(y):
            dim_rot = "H"
            dim.obj.data.splines[0].bezier_points[1].co = (x,0,0)
        else:
            dim_rot = "V"
            dim.obj.data.splines[0].bezier_points[1].co = (0,y,0)
    if view_name == 'FRONT':
        if math.fabs(x) > math.fabs(z):
            dim_rot = "H"
            dim.obj.data.splines[0].bezier_points[1].co = (x,0,0)
        else:
            dim_rot = "V"
            dim.obj.data.splines[0].bezier_points[1].co = (0,z,0)
    if view_name == 'LEFT':
        if math.fabs(y) > math.fabs(z):
            dim_rot = "H"
            dim.obj.data.splines[0].bezier_points[1].co = (y,0,0)
        else:
            dim_rot = "V"
            dim.obj.data.splines[0].bezier_points[1].co = (0,z,0)
    if view_name == 'RIGHT':
        if math.fabs(y) > math.fabs(z):
            dim_rot = "H"
            dim.obj.data.splines[0].bezier_points[1].co = (-y,0,0)
        else:
            dim_rot = "V"
            dim.obj.data.splines[0].bezier_points[1].co = (0,z,0)
    if view_name == 'BACK':
        if math.fabs(x) > math.fabs(z):
            dim_rot = "H"
            dim.obj.data.splines[0].bezier_points[1].co = (-x,0,0)
        else:
            dim_rot = "V"
            dim.obj.data.splines[0].bezier_points[1].co = (0,z,0) 
    return dim_rot 

def set_leader_length(dim,hit_location,second_point,view_name,dim_rot):
    if view_name == 'PLAN':
        x = hit_location[0] - second_point[0]
        y = hit_location[1] - second_point[1]
        if dim_rot == "H":
            dim.set_input("Leader Length",y)
        else:
            dim.set_input("Leader Length",x)
    else:
        x = hit_location[0] - second_point[0]
        y = hit_location[1] - second_point[1]
        z = hit_location[2] - second_point[2]
        if dim_rot == "H":
            if view_name == 'BACK':
                dim.set_input("Leader Length",z)
            else:
                dim.set_input("Leader Length",z)
        else:
            if view_name == 'LEFT':
                dim.set_input("Leader Length",y) 
            if view_name == 'RIGHT':
                dim.set_input("Leader Length",-y) 
            if view_name == 'FRONT':
                dim.set_input("Leader Length",x) 
            if view_name == 'BACK':
                dim.set_input("Leader Length",-x)                                     

class pc_layout_view_OT_toggle_dimension_mode(bpy.types.Operator):
    bl_idname = "pc_layout_view.toggle_dimension_mode"
    bl_label = "Toggle Dimension Mode"

    def execute(self, context):
        for obj in bpy.data.objects:
            for mod in obj.modifiers:
                if mod.type == 'BEVEL':
                    mod.show_viewport = False
                    mod.show_render = False
        # context.space_data.overlay.show_floor = False
        # context.space_data.overlay.show_ortho_grid = False
        # context.space_data.overlay.show_axis_y = False
        # context.space_data.overlay.show_axis_x = False
        # context.space_data.overlay.show_extras = False
        context.scene.camera.hide_viewport = True
        cam_rot = context.scene.camera.matrix_world.to_quaternion()
        bpy.ops.view3d.view_camera()
        context.space_data.region_3d.view_rotation = cam_rot
        context.space_data.region_3d.view_perspective = 'ORTHO'
        context.space_data.region_3d.is_orthographic_side_view = True
        return {'FINISHED'}


class pc_layout_view_OT_add_elevation_dimension(pc_snap.Drop_Operator):
    bl_idname = "pc_layout_view.add_elevation_dimension"
    bl_label = "Add Elevation Dimension"

    elevation_dim = None

    def execute(self, context):
        self.setup_drop_operator(context)
        self.create_data(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def hide_objects(self,hide):
        self.elevation_dim.obj.hide_viewport = hide

    def modal(self, context, event):
        context.area.tag_redraw()    

        #RUN SNAP
        self.hide_objects(True)
        self.mouse_pos = Vector((event.mouse_x - self.region.x, event.mouse_y - self.region.y))  
        context.view_layer.update()          
        pc_snap.main(self, event.ctrl, context)
        self.hide_objects(False)

        self.update_data(context)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            bpy.data.objects.remove(self.snap_line, do_unlink=True)
            self.remove_drop_operator(context)
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.delete_data(context)
            self.remove_drop_operator(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}
    
    def create_data(self,context):
        self.create_snap_line(context)
        self.elevation_dim = self.create_dimension(context)

    def delete_data(self,context):
        bpy.data.objects.remove(self.elevation_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.snap_line, do_unlink=True)

    def update_data(self,context):
        wall_bp = None
        hit_assembly = None
        if self.hit_object:
            wall_bp = pc_utils.get_bp_by_tag(self.hit_object,'IS_WALL_BP')

            assembly_tags = ['IS_WINDOW_BP','IS_ENTRY_DOOR_BP','IS_APPLIANCE_BP','IS_OPENING_BP','IS_CABINET_FF_STARTER_BP']
            hit_assembly = self.get_hit_assembly_from_tag(assembly_tags)

        if self.snap_line and wall_bp:
            wall = pc_types.Assembly(wall_bp)
            self.snap_line.parent = wall_bp
            self.elevation_dim.obj.parent = wall_bp
            self.snap_line.matrix_world[0][3] = self.hit_location[0]
            self.snap_line.matrix_world[1][3] = self.hit_location[1]      
            self.elevation_dim.obj.matrix_world[0][3] = self.hit_location[0]
            self.elevation_dim.obj.matrix_world[1][3] = self.hit_location[1]  
            self.elevation_dim.obj.rotation_euler.z = 0

            if hit_assembly:
                assembly_x_loc = hit_assembly.obj_bp.location.x
                assembly_width = hit_assembly.obj_x.location.x
                self.elevation_dim.obj.location.x = assembly_x_loc
                self.elevation_dim.obj.location.y = 0
                self.elevation_dim.obj.location.z = self.hit_location[2]
                self.elevation_dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
                self.elevation_dim.obj.data.splines[0].bezier_points[1].co = (assembly_width,0,0)                
            else:
                left_x, left_assembly = self.get_left_collision_location_and_assembly(wall)
                right_x, right_assembly = self.get_right_collision_location_and_assembly(wall)
                
                self.elevation_dim.obj.location.x = left_x
                self.elevation_dim.obj.location.y = 0
                self.elevation_dim.obj.location.z = self.hit_location[2]
                self.elevation_dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
                self.elevation_dim.obj.data.splines[0].bezier_points[1].co = (right_x-left_x,0,0)


class pc_layout_view_OT_draw_geo_node_dimension(bpy.types.Operator):
    bl_idname = "pc_layout_view.draw_geo_node_dimension"
    bl_label = "Add Geo Node Dimension"

    blf_text = ""
    region = None
    number_of_clicks = 0
    first_point = (0,0,0)
    second_point = (0,0,0)
    hit_location = (0,0,0)
    hit_grid = False
    mod = None
    view_name = ""
    dim_rot = ""

    def set_curve_to_vector(self,context):
        self.dim.obj.select_set(True)
        context.view_layer.objects.active = self.dim.obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.mode_set(mode='OBJECT')

    def modal(self, context, event):
        context.area.tag_redraw()

        if self.number_of_clicks == 0:
            self.dim.obj.hide_viewport = True
            self.dim.obj.location = self.hit_location
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim.obj.data.splines[0].bezier_points[1].co = (0,0,0)  
                     
        elif self.number_of_clicks == 1:
            self.dim.obj.hide_viewport = False
            self.dim.set_input("Leader Length",pc_unit.inch(1)) 
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim_rot = get_next_point(self.dim,self.hit_location,self.view_name)

        elif self.number_of_clicks == 2:
            self.dim.obj.hide_viewport = False
            set_leader_length(self.dim,self.hit_location,self.second_point,self.view_name,self.dim_rot)

        if event.type == 'MOUSEMOVE' or event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self.dim.obj.hide_viewport = True
            pc_snap.main(self, event.ctrl, context)
            self.dim.obj.hide_viewport = False
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.number_of_clicks += 1
            if self.number_of_clicks == 1:
                self.first_point = self.hit_location
                
            elif self.number_of_clicks == 2:
                self.second_point = self.hit_location

            elif self.number_of_clicks == 3:
                self.set_curve_to_vector(context)
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}
            else:
                self.number_of_clicks += 1

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.region = pc_utils.get_3d_view_region(context)
        if context.area.type == 'VIEW_3D':
            self.mouse_pos = Vector()
            self.hit_object = None
            self.number_of_clicks = 0
            layout_view = pc_types.Assembly_Layout(context.scene)
            self.dim = pc_types.GeoNodeDimension(layout_view=layout_view)
            self.dim.create()  
            self.dim.set_input("Leader Length",pc_unit.inch(1))
            self.dim.obj['HB_CURRENT_DRAW_OBJ'] = True

            self.view_name = get_view_rotation(context)

            if context.scene.camera and context.scene.camera.parent:
                self.dim.obj.rotation_euler.x = math.radians(90)
                self.dim.obj.rotation_euler.z = context.scene.camera.parent.rotation_euler.z
            else:
                self.dim.obj.rotation_euler = (0,0,0)

            for mod in self.dim.obj.modifiers:
                if mod.type == 'NODES':
                    self.mod = mod

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


class pc_layout_view_OT_add_text(bpy.types.Operator):
    bl_idname = "pc_layout_view.add_text"
    bl_label = "Add Text"

    blf_text = ""
    region = None
    is_place_first_point = True
    first_point = (0,0,0)
    hit_location = (0,0,0)
    hit_grid = False

    def modal(self, context, event):
        context.area.tag_redraw()

        if self.hit_location:
            self.text.location = self.hit_location

        if event.type == 'MOUSEMOVE' or event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self.text.hide_viewport = True
            pc_snap.main(self, event.ctrl, context)
            self.text.hide_viewport = False
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.text.select_set(True)
            context.view_layer.objects.active = self.text
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.region = pc_utils.get_3d_view_region(context)
        dim_coll = None
        for coll in context.scene.collection.children:
            if coll.pyclone.is_dimension_collection:
                dim_coll = coll
        if context.area.type == 'VIEW_3D':
            mat = pc_utils.get_dimension_material()

            self.mouse_pos = Vector()
            self.hit_object = None
            cam_rot = (0,0,0)
            if context.scene.camera.parent:
                cam_rot = (math.radians(90),0,context.scene.camera.parent.rotation_euler.z)
            bpy.ops.object.text_add()
            self.text = context.object
            self.text.select_set(True)
            context.view_layer.objects.active = self.text
            # self.text.parent = context.scene.camera
            self.text.data.size = .08
            self.text.data.extrude = .01
            self.text.data.align_x = 'CENTER'
            self.text.data.align_y = 'CENTER'
            self.text.color = (0,0,0,1)
            self.text.display.show_shadows = False
            self.text.rotation_euler = cam_rot
            self.text['HB_CURRENT_DRAW_OBJ'] = True
            self.text['PC_LAYOUT_TEXT'] = True
            self.text['PROMPT_ID'] = 'pc_layout_view.show_text_properties'
            bpy.ops.object.material_slot_add()
            self.text.material_slots[0].material = mat
            for coll in self.text.users_collection:
                coll.objects.unlink(self.text)            
            dim_coll.objects.link(self.text)

            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(pc_snap.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class pc_layout_view_OT_draw_geo_node_arrow(bpy.types.Operator):
    bl_idname = "pc_layout_view.draw_geo_node_arrow"
    bl_label = "Add Geo Node Arrow"

    blf_text = ""
    region = None
    number_of_clicks = 0
    first_point = (0,0,0)
    second_point = (0,0,0)
    hit_location = (0,0,0)
    hit_grid = False
    mod = None
    view_name = ""

    def set_curve_to_vector(self,context):
        self.dim.obj.select_set(True)
        context.view_layer.objects.active = self.dim.obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.mode_set(mode='OBJECT')

    def modal(self, context, event):
        context.area.tag_redraw()

        if self.number_of_clicks == 0:
            self.dim.obj.hide_viewport = True
            self.dim.obj.location = self.hit_location
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim.obj.data.splines[0].bezier_points[1].co = (0,0,0)  
                     
        elif self.number_of_clicks == 1:
            self.dim.obj.hide_viewport = False
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim_rot = get_next_point(self.dim,self.hit_location,self.view_name)   

        elif self.number_of_clicks == 2:
            self.dim.obj.hide_viewport = False

        if event.type == 'MOUSEMOVE' or event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self.dim.obj.hide_viewport = True
            pc_snap.main(self, event.ctrl, context)
            self.dim.obj.hide_viewport = False
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.number_of_clicks += 1
            if self.number_of_clicks == 1:
                self.first_point = self.hit_location
                
            elif self.number_of_clicks == 2:
                self.set_curve_to_vector(context)
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}
            else:
                self.number_of_clicks += 1

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # self.set_curve_to_vector()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.region = pc_utils.get_3d_view_region(context)
        if context.area.type == 'VIEW_3D':
            self.mouse_pos = Vector()
            self.hit_object = None
            self.number_of_clicks = 0
            layout_view = pc_types.Assembly_Layout(context.scene)
            self.dim = pc_types.GeoNodeAnnotation(layout_view=layout_view)
            self.dim.create()  
            self.dim.set_input("Leader Length",0)
            self.dim.obj['HB_CURRENT_DRAW_OBJ'] = True

            self.view_name = get_view_rotation(context)

            if context.scene.camera.parent:
                self.dim.obj.rotation_euler.x = math.radians(90)
                self.dim.obj.rotation_euler.z = context.scene.camera.parent.rotation_euler.z
            else:
                self.dim.obj.rotation_euler = (0,0,0)

            for mod in self.dim.obj.modifiers:
                if mod.type == 'NODES':
                    self.mod = mod

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
        

class pc_layout_view_OT_draw_geo_node_elevation(bpy.types.Operator):
    bl_idname = "pc_layout_view.draw_geo_node_elevation"
    bl_label = "Add Geo Node Elevation"

    blf_text = ""
    region = None
    number_of_clicks = 0
    first_point = (0,0,0)
    second_point = (0,0,0)
    hit_location = (0,0,0)
    hit_grid = False
    mod = None

    def set_curve_to_vector(self,context):
        self.dim.obj.select_set(True)
        context.view_layer.objects.active = self.dim.obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.mode_set(mode='OBJECT')

    def modal(self, context, event):
        context.area.tag_redraw()

        if self.number_of_clicks == 0:
            self.dim.obj.hide_viewport = True
            self.dim.obj.location = self.hit_location
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim.obj.data.splines[0].bezier_points[1].co = (0,0,0)  
                     
        elif self.number_of_clicks == 1:
            self.dim.obj.hide_viewport = False
            self.dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
            self.dim_rot = get_next_point(self.dim,self.hit_location,self.view_name)   

        elif self.number_of_clicks == 2:
            self.dim.obj.hide_viewport = False

        if event.type == 'MOUSEMOVE' or event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self.dim.obj.hide_viewport = True
            pc_snap.main(self, event.ctrl, context)
            self.dim.obj.hide_viewport = False
            
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.number_of_clicks += 1
            if self.number_of_clicks == 1:
                self.first_point = self.hit_location
                
            elif self.number_of_clicks == 2:
                self.set_curve_to_vector(context)
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}
            else:
                self.number_of_clicks += 1

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # self.set_curve_to_vector()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.region = pc_utils.get_3d_view_region(context)
        if context.area.type == 'VIEW_3D':
            self.mouse_pos = Vector()
            self.hit_object = None
            self.number_of_clicks = 0
            layout_view = pc_types.Assembly_Layout(context.scene)
            self.dim = pc_types.GeoNodeElevationSymbol(layout_view=layout_view)
            self.dim.create()  
            self.dim.set_input("Leader Length",0)
            self.dim.obj['HB_CURRENT_DRAW_OBJ'] = True

            self.view_name = get_view_rotation(context)

            if context.scene.camera.parent:
                self.dim.obj.rotation_euler.x = math.radians(90)
                self.dim.obj.rotation_euler.z = context.scene.camera.parent.rotation_euler.z
            else:
                self.dim.obj.rotation_euler = (0,0,0)

            for mod in self.dim.obj.modifiers:
                if mod.type == 'NODES':
                    self.mod = mod

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

class pc_layout_view_OT_show_dimension_properties(Operator):
    bl_idname = "pc_layout_view.show_dimension_properties"
    bl_label = "Show Dimension Properties"
    bl_description = "This shows the dimension properties"
    bl_options = {'UNDO'}

    update_all_dimensions: BoolProperty(name="Update All Dimensions")
    update_selected_dimensions: BoolProperty(name="Update Selected Dimensions")
    set_defaults: BoolProperty(name="Set As Default")

    text_size: FloatProperty(name="Text Size",default=.07)

    arrow_length: FloatProperty(name="Arrow Length",default=pc_unit.inch(1.1811),subtype='DISTANCE')

    arrow_height: FloatProperty(name="Arrow Height",default=pc_unit.inch(1.1811),subtype='DISTANCE')

    leader_length: FloatProperty(name="Leader Length",default=pc_unit.inch(5),subtype='DISTANCE')

    line_thickness: FloatProperty(name="Line Thickness",default=pc_unit.inch(0.07874),subtype='DISTANCE')

    extend_line_amount: FloatProperty(name="Extend Line Amount",default=pc_unit.inch(1),subtype='DISTANCE')

    offset_text: BoolProperty(name="Offset Text from Line")

    offset_text_amount: FloatProperty(name="Offset Text Amount",default=pc_unit.inch(1),subtype='DISTANCE')

    align_text_to_curve: BoolProperty(name="Align Text to Curve")

    decimals: IntProperty(name="Decimals")

    flip_arrows: BoolProperty(name="Flip Arrows")

    flip_text: BoolProperty(name="Flip Text")

    dimension = None

    def execute(self, context):
        pc_props = context.scene.pyclone

        if self.update_all_dimensions:
            for obj in context.scene.objects:
                if 'GeoNodeDimension' in obj:
                    dim = pc_types.GeoNodeDimension(obj)
                    dim.set_input('Arrow Height',self.arrow_height)
                    dim.set_input('Arrow Length',self.arrow_length)
                    dim.set_input('Line Thickness',self.line_thickness)
                    dim.set_input('Text Size',self.text_size)
                    dim.set_input('Extend Line',self.extend_line_amount)

        if self.update_selected_dimensions:
            for obj in context.selected_objects:
                if 'GeoNodeDimension' in obj:
                    dim = pc_types.GeoNodeDimension(obj)  
                    dim.set_input('Leader Length',self.leader_length) 

        if self.set_defaults:
            pc_props.arrow_height = self.arrow_height
            pc_props.arrow_length = self.arrow_length
            pc_props.line_thickness = self.line_thickness
            pc_props.text_size = self.text_size
        context.area.tag_redraw()
        return {'FINISHED'}

    def check(self, context):
        self.dimension.set_input('Arrow Height',self.arrow_height)
        self.dimension.set_input('Arrow Length',self.arrow_length)
        self.dimension.set_input('Line Thickness',self.line_thickness)
        self.dimension.set_input('Text Size',self.text_size)   
        self.dimension.set_input('Leader Length',self.leader_length) 
        self.dimension.set_input('Extend Line',self.extend_line_amount) 
        self.dimension.set_input('Align Text To Curve',self.align_text_to_curve) 
        self.dimension.set_input('Offset Text From Line',self.offset_text) 
        self.dimension.set_input('Offset Text Amount',self.offset_text_amount) 
        self.dimension.set_input('Flip Arrows',self.flip_arrows) 
        self.dimension.set_input('Flip Text',self.flip_text) 
        self.dimension.set_input('Decimals',self.decimals)
        context.area.tag_redraw()
        return True

    def invoke(self,context,event):
        self.dimension = pc_types.GeoNodeDimension(context.object)
        self.arrow_height = self.dimension.get_input("Arrow Height")
        self.arrow_length = self.dimension.get_input("Arrow Length")
        self.line_thickness = self.dimension.get_input("Line Thickness")
        self.text_size = self.dimension.get_input("Text Size")
        self.leader_length = self.dimension.get_input("Leader Length")
        self.extend_line_amount = self.dimension.get_input("Extend Line")
        self.align_text_to_curve = self.dimension.get_input("Align Text To Curve")
        self.offset_text = self.dimension.get_input("Offset Text From Line")
        self.offset_text_amount = self.dimension.get_input("Offset Text Amount")
        self.flip_arrows = self.dimension.get_input("Flip Arrows")
        self.decimals = self.dimension.get_input("Decimals")
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Leader Length")
        row.prop(self,'leader_length',text="")
        row = box.row()
        row.prop(self,'update_selected_dimensions')        
        row = box.row()
        row.label(text="Decimals")
        row.prop(self,'decimals',text="")        
        row = box.row()
        row.prop(self,'flip_arrows',text="Flip Arrows")
        row.prop(self,'flip_text',text="Flip Text")
        row = box.row()
        row.prop(self,'offset_text')
        if self.offset_text:
            row.prop(self,'offset_text_amount')

        box = layout.box()
        row = box.row()
        row.label(text="Text Size")
        row.prop(self,'text_size',text="")
        row = box.row()
        row.label(text="Arrow Length")        
        row.prop(self,'arrow_length',text="")
        row = box.row()
        row.label(text="Arrow Height")        
        row.prop(self,'arrow_height',text="")
        row = box.row()
        row.label(text="Line Thickness")        
        row.prop(self,'line_thickness',text="")
        row = box.row()
        row.label(text="Extend Line Amount")        
        row.prop(self,'extend_line_amount',text="")
        box.prop(self,'align_text_to_curve')

        box = layout.box()
        row = box.row()
        row.prop(self,'update_all_dimensions')
        row.prop(self,'set_defaults')


class pc_layout_view_OT_show_text_properties(Operator):
    bl_idname = "pc_layout_view.show_text_properties"
    bl_label = "Show Text Properties"
    bl_description = "This shows the text properties"
    bl_options = {'UNDO'}

    update_all: BoolProperty(name="Update All")

    text_size: FloatProperty(name="Text Size",default=.07)

    align_text_x: EnumProperty(name="Align Text X",
                          items=[('LEFT',"Left","Align Text Left"),
                                 ('CENTER',"Center","Align Text Center"),
                                 ('RIGHT',"Right","Align Text Right")],
                          default='CENTER')

    align_text_z: EnumProperty(name="Align Text Z",
                          items=[('TOP',"Top","Align Text Top"),
                                 ('CENTER',"Center","Align Text Center"),
                                 ('BOTTOM',"Bottom","Align Text Bottom")],
                          default='CENTER')
    
    text_obj = None

    def execute(self, context):
        pc_props = context.scene.pyclone

        if self.update_all:
            for obj in context.scene.objects:
                if 'PC_LAYOUT_TEXT' in obj:
                    obj.data.size = self.text_size

        context.area.tag_redraw()
        return {'FINISHED'}

    def check(self, context):
        pc_props = context.scene.pyclone

        self.text_obj.data.size = self.text_size
        self.text_obj.data.align_x = self.align_text_x
        self.text_obj.data.align_y = self.align_text_z

        context.area.tag_redraw()
        return True
    
    def invoke(self,context,event):
        self.text_obj = context.object
        self.text_size = self.text_obj.data.size
        self.align_text_x = self.text_obj.data.align_x
        self.align_text_z  = self.text_obj.data.align_y
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Text Size")
        row.prop(self,'text_size',text="")
        row = box.row()
        row.prop(self,'align_text_x',expand=True)
        row = box.row()
        row.prop(self,'align_text_z',expand=True)
        box.prop(self,'update_all')


class pc_layout_view_OT_show_arrow_properties(Operator):
    bl_idname = "pc_layout_view.show_arrow_properties"
    bl_label = "Show Arrow Properties"
    bl_description = "This shows the arrow properties"
    bl_options = {'UNDO'}

    update_all: BoolProperty(name="Update All")

    show_arrow: BoolProperty(name="Show Arrow")

    arrow_length: FloatProperty(name="Arrow Length",default=pc_unit.inch(1.1811),subtype='DISTANCE')

    arrow_height: FloatProperty(name="Arrow Height",default=pc_unit.inch(1.1811),subtype='DISTANCE')

    leader_length: FloatProperty(name="Leader Length",default=pc_unit.inch(5),subtype='DISTANCE')

    line_thickness: FloatProperty(name="Line Thickness",default=pc_unit.inch(0.07874),subtype='DISTANCE')

    arrow = None

    def execute(self, context):
        pc_props = context.scene.pyclone

        if self.update_all:
            for obj in context.scene.objects:
                if 'GeoNodeAnnotation' in obj:
                    dim = pc_types.GeoNodeDimension(obj)
                    dim.set_input('Arrow Height',self.arrow_height)
                    dim.set_input('Arrow Length',self.arrow_length)
                    dim.set_input('Line Thickness',self.line_thickness)

        context.area.tag_redraw()
        return {'FINISHED'}

    def check(self, context):
        pc_props = context.scene.pyclone
        self.arrow.set_input('Show Arrow',self.show_arrow)
        self.arrow.set_input('Arrow Height',self.arrow_height)
        self.arrow.set_input('Arrow Length',self.arrow_length)
        self.arrow.set_input('Line Thickness',self.line_thickness)

        context.area.tag_redraw()
        return True
    
    def invoke(self,context,event):
        self.arrow = pc_types.GeoNodeDimension(context.object)
        self.show_arrow = self.arrow.get_input("Show Arrow")
        self.arrow_height = self.arrow.get_input("Arrow Height")
        self.arrow_length = self.arrow.get_input("Arrow Length")    
        self.line_thickness = self.arrow.get_input("Line Thickness")     
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.prop(self,'show_arrow',text="Show Arrow")
        if self.show_arrow:
            row = box.row()
            # row.label(text="Arrow Size")
            row.prop(self,'arrow_height',text="Height")
            row.prop(self,'arrow_length',text="Length")
        row = box.row()
        row.label(text="Line Thickness")
        row.prop(self,'line_thickness',text="")

        box.prop(self,'update_all')


class pc_layout_view_OT_show_elv_symbol_properties(Operator):
    bl_idname = "pc_layout_view.show_elv_symbol_properties"
    bl_label = "Show Elevation Symbol Properties"
    bl_description = "This shows the elevation symbol properties"
    bl_options = {'UNDO'}

    update_all: BoolProperty(name="Update All")

    line_thickness: FloatProperty(name="Line Thickness",default=pc_unit.inch(0.07874),subtype='DISTANCE')
    circle_radius: FloatProperty(name="Circle Radius",default=pc_unit.inch(4),subtype='DISTANCE')

    arrow = None

    def execute(self, context):
        pc_props = context.scene.pyclone

        if self.update_all:
            for obj in context.scene.objects:
                if 'GeoNodeElevationSymbol' in obj:
                    dim = pc_types.GeoNodeDimension(obj)
                    dim.set_input('Line Thickness',self.line_thickness)
                    dim.set_input('Circle Radius',self.circle_radius)

        context.area.tag_redraw()
        return {'FINISHED'}

    def check(self, context):
        pc_props = context.scene.pyclone
        self.arrow.set_input('Line Thickness',self.line_thickness)
        self.arrow.set_input('Circle Radius',self.circle_radius)
        context.area.tag_redraw()
        return True
    
    def invoke(self,context,event):
        self.arrow = pc_types.GeoNodeDimension(context.object)
        self.line_thickness = self.arrow.get_input("Line Thickness")     
        self.circle_radius = self.arrow.get_input("Circle Radius") 
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Line Thickness")
        row.prop(self,'line_thickness',text="")
        row = box.row()
        row.label(text="Circle Radius")
        row.prop(self,'circle_radius',text="")
        box.prop(self,'update_all')


class pc_layout_view_OT_flip_selected_dimensions(Operator):
    bl_idname = "pc_layout_view.flip_selected_dimensions"
    bl_label = "Flip Selected Dimensions"
    bl_description = "This flips all of the selected dimensions"
    bl_options = {'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            if 'GeoNodeDimension' in obj:
                dim = pc_types.GeoNodeDimension(obj)
                leader_length = dim.get_input("Leader Length")
                offset_text_amount = dim.get_input("Offset Text Amount")
                dim.set_input("Leader Length",leader_length*-1)
                dim.set_input("Offset Text Amount",offset_text_amount*-1)

        context.area.tag_redraw()
        return {'FINISHED'}


class pc_layout_view_OT_create_iso_view(Operator):
    bl_idname = "pc_layout_view.create_iso_view"
    bl_label = "Create Iso View"
    bl_description = "This creates an isometric view of the assembly layout"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        lv_obj = None
        for obj in context.view_layer.objects:
            if obj.instance_collection:
                lv_obj = obj
                coll = obj.instance_collection

        lv_obj.hide_select = False
        lv_obj.select_set(True)
        context.view_layer.objects.active = lv_obj

        bpy.ops.object.duplicate()

        new_obj = context.active_object
        new_obj.rotation_euler.x = math.radians(19.7)
        new_obj.rotation_euler.y = math.radians(-12)
        new_obj.rotation_euler.z = math.radians(30)

        context.area.tag_redraw()
        return {'FINISHED'}
    
class pc_layout_view_OT_toggle_model_selection(Operator):
    bl_idname = "pc_layout_view.toggle_model_selection"
    bl_label = "Toggle Model Selection"
    bl_description = "This toggles the model selection"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in context.view_layer.objects:
            if obj.instance_collection:
                if obj.hide_select:
                    obj.hide_select = False
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                else:
                    obj.hide_select = True
                    obj.select_set(True)
                    context.view_layer.objects.active = obj

        context.area.tag_redraw()
        return {'FINISHED'}


class pc_layout_view_OT_delete_layout_view(Operator):
    bl_idname = "pc_layout_view.delete_layout_view"
    bl_label = "Delete Layout View"
    bl_description = "This will delete the layout view"
    bl_options = {'UNDO'}

    view_name: StringProperty(name="View Name",default="New Layout View")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = bpy.data.scenes[self.view_name]
        bpy.data.scenes.remove(scene)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the view layout?")
        layout.label(text="Layout Name - " + self.view_name)


classes = (
    pc_layout_view_OT_toggle_dimension_mode,
    pc_layout_view_OT_add_elevation_dimension,
    pc_layout_view_OT_draw_geo_node_dimension,
    pc_layout_view_OT_add_text,
    pc_layout_view_OT_draw_geo_node_arrow,
    pc_layout_view_OT_draw_geo_node_elevation,
    pc_layout_view_OT_show_dimension_properties,
    pc_layout_view_OT_show_text_properties,
    pc_layout_view_OT_show_arrow_properties,
    pc_layout_view_OT_show_elv_symbol_properties,
    pc_layout_view_OT_flip_selected_dimensions,
    pc_layout_view_OT_create_iso_view,
    pc_layout_view_OT_delete_layout_view,
    pc_layout_view_OT_toggle_model_selection,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
