import bpy
import os
import math
from . import library_doors_windows
from mathutils import Vector
from . import const_doors_windows as const
from pc_lib import pc_types,pc_utils,pc_unit,pc_placement_utils,pc_snap

class home_builder_OT_place_door_window(pc_snap.Drop_Operator):
    bl_idname = const.lib_name + ".place_door_window"
    bl_label = "Place Door or Window"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    region = None

    drawing_plane = None

    assembly = None
    obj = None
    exclude_objects = []

    first_point = (0,0,0)
    mouse_pos = (0,0,0)
    hit_location = (0,0,0)
    hit_object = None
    hit_grid = False

    typed_value = ""
    default_width = 0

    blf_text = ""

    left_dim = None
    right_dim = None

    def execute(self, context):
        self.setup_drop_operator(context)

        self.create_assembly(context)
        view_name = self.get_view_orientation_from_quaternion()
        self.left_dim = pc_types.GeoNodeDimension()
        self.left_dim.create()
        if view_name == 'TOP':
            self.left_dim.obj.rotation_euler.x = 0
        else:
            self.left_dim.obj.rotation_euler.x = math.radians(90)
        self.left_dim.set_input("Leader Length",pc_unit.inch(3))
        self.left_dim.obj.select_set(False)
        self.left_dim.obj.show_in_front = True
        self.left_dim.obj.hide_viewport = True

        self.width_dim = pc_types.GeoNodeDimension()
        self.width_dim.create()
        if view_name == 'TOP':
            self.width_dim.obj.rotation_euler.x = 0
        else:
            self.width_dim.obj.rotation_euler.x = math.radians(90)
        self.width_dim.set_input("Leader Length",pc_unit.inch(3))
        self.width_dim.obj.select_set(False)
        self.width_dim.obj.show_in_front = True
        self.width_dim.obj.hide_viewport = True

        self.right_dim = pc_types.GeoNodeDimension()
        self.right_dim.create()
        if view_name == 'TOP':
            self.right_dim.obj.rotation_euler.x = 0
        else:
            self.right_dim.obj.rotation_euler.x = math.radians(90)
        self.right_dim.set_input("Leader Length",pc_unit.inch(3))
        self.right_dim.obj.select_set(False)
        self.right_dim.obj.show_in_front = True
        self.right_dim.obj.hide_viewport = True

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def remove_old_boolean_modifier(self):
        wall_bp = pc_utils.get_bp_by_tag(self.assembly.obj_bp,'IS_WALL_BP')
        wall_mesh = None
        for child in wall_bp.children:
            if child.type == 'MESH':
                wall_mesh = child
        obj_bool = self.get_boolean_obj(self.assembly.obj_bp)
        if wall_mesh:
            for mod in wall_mesh.modifiers:
                if mod.type == 'BOOLEAN':
                    if mod.object == obj_bool:
                        wall_mesh.modifiers.remove(mod)
                        
    def create_assembly(self,context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            self.assembly = pc_types.Assembly(obj_bp)
            self.remove_old_boolean_modifier()
        else:
            asset_file_handle = context.asset_file_handle
            self.assembly = eval("library_doors_windows." + asset_file_handle.name.replace(" ","_") + "()")
            self.assembly.draw_assembly()

        self.default_width = self.assembly.obj_x.location.x

        self.set_child_properties(self.assembly.obj_bp)

    def set_visibility_for_raycast(self,hide):
        for child in self.assembly.obj_bp.children_recursive:
            if child.type != 'EMPTY':
                child.hide_viewport = hide

    def set_child_properties(self,obj):
        pc_utils.update_id_props(obj,self.assembly.obj_bp)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH' or obj.type == 'CURVE':
            obj.display_type = 'WIRE'             
        for child in obj.children:
            self.set_child_properties(child)

    def set_width(self):
        if self.typed_value == "":
            self.assembly.obj_x.location.x = math.fabs(self.default_width)
        else:
            if self.typed_value == ".":
                value = 0
            else:
                value = eval(self.typed_value)
            if bpy.context.scene.unit_settings.system == 'METRIC':
                self.assembly.obj_x.location.x = pc_unit.millimeter(float(value))
            else:
                self.assembly.obj_x.location.x = pc_unit.inch(float(value)) 

    def set_placed_properties(self,obj):
        pc_utils.update_id_props(obj,self.assembly.obj_bp)
        if obj.type in {'MESH','CURVE'}:
            if 'IS_BOOLEAN' in obj:
                obj.display_type = 'WIRE' 
                obj.hide_viewport = True
            else:
                obj.display_type = 'TEXTURED'  
        if obj.type == 'EMPTY':
            obj.hide_viewport = True
        for child in obj.children:
            self.set_placed_properties(child) 

    def get_boolean_obj(self,obj):
        for child in obj.children_recursive:
            if 'IS_BOOLEAN' in child:
                return child

    def add_boolean_modifier(self,wall_mesh):
        obj_bool = self.get_boolean_obj(self.assembly.obj_bp)
        if wall_mesh and obj_bool:
            mod = wall_mesh.modifiers.new(obj_bool.name,'BOOLEAN')
            mod.object = obj_bool
            mod.operation = 'DIFFERENCE'

    def confirm_placement(self):
        self.assembly.obj_bp.location.y = 0
        bpy.data.objects.remove(self.left_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.width_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.right_dim.obj, do_unlink=True)            
        self.set_placed_properties(self.assembly.obj_bp)
        
    def modal(self, context, event):
        context.view_layer.update()
        bpy.ops.object.select_all(action='DESELECT')

        self.set_type_value(event)
        self.set_width()
        context.workspace.status_text_set(text="[PLACEMENT MODE: Move Cursor to Wall]   [RIGHT CLICK: Cancel Command]")

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        self.mouse_pos = Vector((event.mouse_x - self.region.x, event.mouse_y - self.region.y))
        self.set_visibility_for_raycast(True)
        pc_snap.main(self, event.ctrl, context)
        if self.hit_object:
            self.set_visibility_for_raycast(False)
        self.position_object(context,self.hit_location,self.hit_object)

        if pc_placement_utils.event_is_place_asset(event) and self.hit_object:
            self.add_boolean_modifier(self.hit_object)
            self.confirm_placement()
            context.workspace.status_text_set(text=None)
            return self.finish(context,event.shift)

        if pc_placement_utils.event_is_cancel_command(event):
            context.workspace.status_text_set(text=None)
            return self.cancel_drop(context)

        if pc_placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'} 

        return {'RUNNING_MODAL'} 
            
    def position_object(self,context,selected_point,selected_obj):
        if selected_point:
            wall_bp = pc_utils.get_bp_by_tag(selected_obj,'IS_WALL_BP')
            if self.assembly.obj_bp and wall_bp:
                wall = pc_types.Assembly(wall_bp)
                context.workspace.status_text_set(text="[LEFT CLICK: Place on Wall]   [RIGHT CLICK: Cancel Command]   [TYPE NUMBERS: Set Width (" + self.typed_value + ")]")
                self.assembly.obj_bp.parent = wall_bp
                self.assembly.obj_bp.matrix_world[0][3] = selected_point[0]
                self.assembly.obj_bp.matrix_world[1][3] = selected_point[1]
                self.assembly.obj_bp.rotation_euler.z = 0
                self.assembly.obj_bp.location.x = self.get_snap_value(self.assembly.obj_bp.location.x)
                self.assembly.obj_bp.location.y = 0
                for child in wall_bp.children:
                    if child.type == 'MESH':
                        child.select_set(True)  
                        break
                window_x = self.assembly.obj_bp.location.x
                window_length = self.assembly.obj_x.location.x
                wall_length = wall.obj_x.location.x
                wall_height = wall.obj_z.location.z
                self.left_dim.obj.parent = wall_bp
                self.left_dim.obj.hide_viewport = False
                self.left_dim.obj.location.z = wall_height
                self.left_dim.obj.data.splines[0].bezier_points[0].co = (0,0,0)
                self.left_dim.obj.data.splines[0].bezier_points[1].co = (window_x,0,0)  
                self.left_dim.update()                    

                self.width_dim.obj.parent = wall_bp
                self.width_dim.obj.hide_viewport = False
                self.width_dim.obj.location.z = wall_height
                self.width_dim.obj.data.splines[0].bezier_points[0].co = (window_x,0,0)
                self.width_dim.obj.data.splines[0].bezier_points[1].co = (window_x+window_length,0,0)  
                self.width_dim.update()     

                self.right_dim.obj.parent = wall_bp
                self.right_dim.obj.hide_viewport = False
                self.right_dim.obj.location.z = wall_height
                self.right_dim.obj.data.splines[0].bezier_points[0].co = (window_x+window_length,0,0)
                self.right_dim.obj.data.splines[0].bezier_points[1].co = (wall_length,0,0)  
                self.right_dim.update()  

            else:
                self.left_dim.obj.hide_viewport = True
                self.width_dim.obj.hide_viewport = True
                self.right_dim.obj.hide_viewport = True
                self.assembly.obj_bp.matrix_world[0][3] = selected_point[0]
                self.assembly.obj_bp.matrix_world[1][3] = selected_point[1]    
        else:
            self.left_dim.obj.hide_viewport = True
            self.width_dim.obj.hide_viewport = True
            self.right_dim.obj.hide_viewport = True         

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.assembly.obj_x.hide_viewport = hide
        self.assembly.obj_y.hide_viewport = hide
        self.assembly.obj_z.hide_viewport = hide
        self.assembly.obj_x.empty_display_size = .001
        self.assembly.obj_y.empty_display_size = .001
        self.assembly.obj_z.empty_display_size = .001

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.assembly.obj_bp)
        bpy.data.objects.remove(self.left_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.width_dim.obj, do_unlink=True)
        bpy.data.objects.remove(self.right_dim.obj, do_unlink=True)           
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        return {'CANCELLED'}

    def finish(self,context,is_recursive=False):
        context.window.cursor_set('DEFAULT')
        self.refresh_data(False)
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        if is_recursive and self.obj_bp_name == "":
            bpy.ops.home_builder.place_door_window(filepath=self.filepath)
        return {'FINISHED'}

classes = (
    home_builder_OT_place_door_window,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                                    