import bpy
import os
from . import library_doors_windows
from pc_lib import pc_types,pc_utils,pc_unit,pc_placement_utils

class home_builder_OT_place_door_window(bpy.types.Operator):
    bl_idname = "home_builder.place_door_window"
    bl_label = "Place Door or Window"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    region = None

    drawing_plane = None

    assembly = None
    obj = None
    exclude_objects = []
    # window_z_location = 0

    def execute(self, context):
        # props = home_builder_utils.get_scene_props(context.scene)
        # self.window_z_location = props.window_height_from_floor
        self.region = pc_utils.get_3d_view_region(context)
        self.create_drawing_plane(context)
        self.create_assembly(context)
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
            workspace = context.workspace
            wm = context.window_manager
            asset = wm.home_builder.home_builder_library_assets[workspace.home_builder.home_builder_library_index]
            self.assembly = eval("library_doors_windows." + asset.file_data.name.replace(" ","_") + "()")
            self.assembly.draw_assembly()
            # self.set_child_properties(self.cabinet.obj_bp)           

            # directory, file = os.path.split(self.filepath)
            # filename, ext = os.path.splitext(file)
            # self.assembly = eval("library_doors_windows." + filename.replace(" ","_") + "()")     
            # self.assembly.draw_assembly()

        self.set_child_properties(self.assembly.obj_bp)

    def set_child_properties(self,obj):
        pc_utils.update_id_props(obj,self.assembly.obj_bp)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        pc_utils.update_id_props(obj,self.assembly.obj_bp)
        if obj.type == 'MESH':
            if 'IS_BOOLEAN' in obj:
                obj.display_type = 'WIRE' 
                obj.hide_viewport = True
            else:
                obj.display_type = 'TEXTURED'  
        if obj.type == 'EMPTY':
            obj.hide_viewport = True
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def get_boolean_obj(self,obj):
        #TODO FIGURE OUT HOW TO DO RECURSIVE SEARCHING 
        #ONLY SERACHES THREE LEVELS DEEP :(
        if 'IS_BOOLEAN' in obj:
            return obj
        for child in obj.children:
            if 'IS_BOOLEAN' in child:
                return child
            for nchild in child.children:
                if 'IS_BOOLEAN' in nchild:
                    return nchild

    def add_boolean_modifier(self,wall_mesh):
        obj_bool = self.get_boolean_obj(self.assembly.obj_bp)
        if wall_mesh and obj_bool:
            mod = wall_mesh.modifiers.new(obj_bool.name,'BOOLEAN')
            mod.object = obj_bool
            mod.operation = 'DIFFERENCE'

    def confirm_placement(self):
        self.assembly.obj_bp.location.y = 0

    def modal(self, context, event):
        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if pc_placement_utils.event_is_place_asset(event):
            self.add_boolean_modifier(selected_obj)
            self.confirm_placement()
            # if hasattr(self.assembly,'add_doors'):
            #     self.assembly.add_doors()
            self.set_placed_properties(self.assembly.obj_bp)
            return self.finish(context,event.shift)

        if pc_placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if pc_placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'} 

        return {'RUNNING_MODAL'} 
            
    def position_object(self,selected_point,selected_obj):
        if selected_obj:
            wall_bp = pc_utils.get_bp_by_tag(selected_obj,'IS_WALL_BP')
            if self.assembly.obj_bp and wall_bp:
                self.assembly.obj_bp.parent = wall_bp
                self.assembly.obj_bp.matrix_world[0][3] = selected_point[0]
                self.assembly.obj_bp.matrix_world[1][3] = selected_point[1]
                self.assembly.obj_bp.rotation_euler.z = 0
            else:
                self.assembly.obj_bp.matrix_world[0][3] = selected_point[0]
                self.assembly.obj_bp.matrix_world[1][3] = selected_point[1]                

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
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def finish(self,context,is_recursive=False):
        context.window.cursor_set('DEFAULT')
        self.refresh_data(False)
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive and self.obj_bp_name == "":
            bpy.ops.home_builder.place_door_window(filepath=self.filepath)
        return {'FINISHED'}

classes = (
    home_builder_OT_place_door_window,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                                    