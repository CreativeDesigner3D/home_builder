import bpy
import os
import math
from pc_lib import pc_utils, pc_placement_utils
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

class home_builder_OT_drop_material(bpy.types.Operator):
    bl_idname = "home_builder.drop_material"
    bl_label = "Drop Material"

    mat = None
    region = None

    @classmethod
    def poll(cls, context):  
        if context.object and context.object.mode != 'OBJECT':
            return False
        return True
        
    def execute(self, context):
        self.region = pc_utils.get_3d_view_region(context)
        self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def get_material(self,context):
        wm_props = context.window_manager.home_builder
        library = wm_props.get_active_library(context)
        asset = wm_props.get_active_asset(context)
        return pc_utils.get_material(library.library_path,asset.file_data.name)

    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event,ignore_opening_meshes=True)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select_set(True)
            context.view_layer.objects.active = selected_obj
        
            if pc_placement_utils.event_is_place_asset(event):
                if hasattr(selected_obj.data,'uv_layers') and len(selected_obj.data.uv_layers) == 0:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT') 
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)  
                    bpy.ops.object.editmode_toggle()

                if len(selected_obj.material_slots) == 0:
                    bpy.ops.object.material_slot_add()

                if len(selected_obj.pyclone.pointers) > 0:
                    print(self.mat,selected_obj)
                    bpy.ops.home_builder.assign_material_dialog('INVOKE_DEFAULT',material_name = self.mat.name, object_name = selected_obj.name)
                    return self.finish(context)
                else:
                    for slot in selected_obj.material_slots:
                        slot.material = self.mat
                        
                return self.finish(context)

        if pc_placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if pc_placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_drop_decoration(bpy.types.Operator):
    bl_idname = "home_builder.drop_decoration"
    bl_label = "Drop Decoration"
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
        library = wm_props.get_active_library(context)
        asset = wm_props.get_active_asset(context)   
        path = os.path.join(os.path.dirname(library.library_path),'assets',asset.file_data.name + ".blend")
        
        with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            obj.display_type = 'WIRE'
            self.all_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)            
            context.view_layer.active_layer_collection.collection.objects.link(obj)  

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event,exclude_objects=self.all_objects)

        self.position_object(selected_point,selected_obj)

        if pc_placement_utils.event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if pc_placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if pc_placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]

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
            bpy.ops.home_builder.drop_decoration(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_assign_material_dialog(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_dialog"
    bl_label = "Assign Material Dialog"
    bl_description = "This is a dialog to assign materials to Home Builder objects"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    obj = None
    material = None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        self.material = bpy.data.materials[self.material_name]
        self.obj = bpy.data.objects[self.object_name]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=480)
        
    def draw(self,context):
        scene_props = pc_utils.get_hb_scene_props(context.scene)
        # obj_props = home_builder_utils.get_object_props(self.obj)
        layout = self.layout
        box = layout.box()
        box.label(text=self.obj.name,icon='OBJECT_DATA')
        pointer_list = []

        # if len(scene_props.material_pointer_groups) - 1 >= obj_props.material_group_index:
        #     mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        # else:
        #     mat_group = scene_props.material_pointer_groups[0]

        for index, mat_slot in enumerate(self.obj.material_slots):
            row = box.split(factor=.80)
            pointer = None

            if index + 1 <= len(self.obj.pyclone.pointers):
                pointer = self.obj.pyclone.pointers[index]

            if mat_slot.name == "":
                row.label(text='No Material')
            else:
                if pointer:
                    row.prop(mat_slot,"name",text=pointer.name,icon='MATERIAL')
                else:
                    row.prop(mat_slot,"name",text=" ",icon='MATERIAL')

            if pointer and pointer.pointer_name not in pointer_list and pointer.pointer_name != "":
                pointer_list.append(pointer.pointer_name)

            props = row.operator('home_builder.assign_material_to_slot',text="Override",icon='BACK')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index

        if len(pointer_list) > 0:
            box = layout.box()
            row = box.row()
            row.label(text="Update Material Pointers",icon='MATERIAL')
            for pointer in pointer_list:
                row = box.split(factor=.80)
                mat_pointer = scene_props.material_pointers[pointer] 
                row.label(text=pointer + ": " + mat_pointer.category_name + "/" + mat_pointer.material_name)    
                props = row.operator('home_builder.assign_material_to_pointer',text="Update All",icon='FILE_REFRESH')
                props.pointer_name = pointer
        
    def execute(self,context):
        return {'FINISHED'}        


class home_builder_OT_assign_material_to_slot(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_to_slot"
    bl_label = "Assign Material to Slot"
    bl_description = "This will assign a material to a material slot"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    index: bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        obj.material_slots[self.index].material = mat
        return {'FINISHED'}


class home_builder_OT_place_custom_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.place_custom_cabinet"
    bl_label = "Place Custom Cabinet"
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
        self.get_asset(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_asset(self,context):
        wm_props = context.window_manager.home_builder
        library = wm_props.get_active_library(context)
        asset = wm_props.get_active_asset(context)
        path = os.path.join(os.path.dirname(library.library_path),'assets',asset.file_data.name + ".blend")
        with bpy.data.libraries.load(path) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            obj.display_type = 'WIRE'
            self.all_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)            
            context.view_layer.active_layer_collection.collection.objects.link(obj)  

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event,exclude_objects=self.all_objects)

        self.position_object(selected_point,selected_obj)

        if pc_placement_utils.event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if pc_placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if pc_placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]

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
        return {'FINISHED'}

classes = (
    home_builder_OT_drop_material,
    home_builder_OT_drop_decoration,
    home_builder_OT_assign_material_dialog,
    home_builder_OT_assign_material_to_slot,
    home_builder_OT_place_custom_cabinet,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        