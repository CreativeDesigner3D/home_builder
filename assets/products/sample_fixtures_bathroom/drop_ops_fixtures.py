import bpy,os,inspect, sys
import math
from pc_lib import pc_unit, pc_utils, pc_types 
from pc_lib import pc_placement_utils as placement_utils

class hb_sample_fixtures_OT_drop_fixture(bpy.types.Operator):
    bl_idname = "hb_sample_fixtures.drop_fixture"
    bl_label = "Drop Fixture"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    current_wall = None

    starting_point = ()

    parent_obj_dict = {}
    all_objects = []

    region = None

    def reset_properties(self):
        self.current_wall = None
        self.starting_point = ()
        self.parent_obj_dict = {}
        self.all_objects = []

    def execute(self, context):
        self.region = pc_utils.get_3d_view_region(context)
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        wm_props = context.window_manager.home_builder
        sel_library = wm_props.get_active_library(context)

        asset_file_handle = context.asset_file_handle
 
        path = os.path.join(sel_library.library_path,'assets',asset_file_handle.name + ".blend")

        with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            obj.display_type = 'WIRE'
            self.all_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)            
            context.view_layer.active_layer_collection.collection.objects.link(obj)  

    def set_placed_properties(self,obj):
        if "obj_x" in obj:
            obj.hide_viewport = True     
        if "obj_y" in obj:
            obj.hide_viewport = True   
        if "obj_z" in obj:
            obj.hide_viewport = True   
        if "obj_bp" in obj:
            obj.hide_viewport = True           
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event,exclude_objects=self.all_objects)

        self.position_object(selected_point,selected_obj)

        if placement_utils.event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]
                    
        wall_bp = pc_utils.get_bp_by_tag(selected_obj,'IS_WALL_BP')
        if wall_bp:
            for obj, location in self.parent_obj_dict.items():            
                obj.parent = wall_bp
                obj.matrix_world[0][3] = selected_point[0]
                obj.matrix_world[1][3] = selected_point[1]
                obj.matrix_world[2][3] = 0
                obj.rotation_euler.z = 0

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.all_objects:
            obj_list.append(obj)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        bpy.ops.object.select_all(action='DESELECT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        for obj, location in self.parent_obj_dict.items():
            obj.select_set(True)  
            context.view_layer.objects.active = obj     
        for obj in self.all_objects:
            self.set_placed_properties(obj) 
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_bathroom_fixture(filepath=self.filepath)
        return {'FINISHED'}

classes = (
    hb_sample_fixtures_OT_drop_fixture,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                                    