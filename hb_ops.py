import bpy
import os
import time
import math
import inspect
from .pc_lib import pc_utils, pc_unit
from . import hb_placement_utils
from . import hb_utils
from .walls import wall_library

class home_builder_OT_about_home_builder(bpy.types.Operator):
    bl_idname = "home_builder.about_home_builder"
    bl_label = "About Home Builder"

    tabs: bpy.props.EnumProperty(name="Library Tabs",
                       items=[('VERSION',"Version","Show the Home Builder Version"),
                              ('INSTALLED_LIBRARIES',"Installed Libraries","Show the Installed Libraries"),
                              ('TRAINING',"Training","Show the Training Videos")],
                       default='VERSION')

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def execute(self, context):  
        return {'FINISHED'}

    def get_library_icon(self,library):
        if library.library_type == 'DOOR_WINDOWS':
            return  'MESH_GRID'
        if library.library_type == 'CABINETS':
            return  'META_CUBE'
        if library.library_type == 'APPLIANCES':
            return  'MOD_FLUIDSIM'
        if library.library_type == 'DECORATIONS':
            return  'SCENE_DATA'
        if library.library_type == 'FIXTURES':
            return  'MATPLANE'
        if library.library_type == 'STARTERS':
            return  'STICKY_UVS_LOC'
        if library.library_type == 'INSERTS':
            return  'STICKY_UVS_VERT'
        if library.library_type == 'PARTS':
            return  'STICKY_UVS_DISABLE'
        if library.library_type == 'MATERIALS':
            return  'MATERIAL_DATA'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager        
        wm_props = wm.home_builder
        
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop_enum(self, "tabs", 'VERSION',icon='INFO')
        row.prop_enum(self, "tabs", 'INSTALLED_LIBRARIES',icon='ASSET_MANAGER')
        row.prop_enum(self, "tabs", 'TRAINING',icon='QUESTION')

        if self.tabs == 'INSTALLED_LIBRARIES':
            main_box = layout.box()
            row = main_box.row()
            row.label(text="Installed Libraries")
            row.label(text=" ")
            row.operator('home_builder.todo',text="Install Library",icon='IMPORT')
            
            col = main_box.column(align=True)
            for lib in wm_props.asset_libraries:
                row = col.row()
                row.label(text="",icon=self.get_library_icon(lib))
                row.prop(lib,'enabled',text=lib.name)


class home_builder_OT_todo(bpy.types.Operator):
    bl_idname = "home_builder.todo"
    bl_label = "TODO"

    def execute(self, context):
        print("NOT IMPLEMENTED: TODO")
        return {'FINISHED'}


class home_builder_OT_update_library_path(bpy.types.Operator):
    bl_idname = "home_builder.update_library_path"
    bl_label = "Update Library Path"

    asset_type: bpy.props.StringProperty(name="Asset Type")
    asset_path: bpy.props.StringProperty(name="Asset Path")
    asset_folder: bpy.props.StringProperty(name="Asset Path")

    def execute(self, context):
        wm_props = context.window_manager.home_builder
        sel_library = None
        for library in wm_props.asset_libraries:
            if library.library_path == self.asset_path:
                sel_library = library
                break

        scene_props = context.scene.home_builder
        prefs = context.preferences
        asset_lib = prefs.filepaths.asset_libraries.get("home_builder_library")  

        if scene_props.library_tabs == 'ROOMS':
            if scene_props.room_tabs == 'DOORS_WINDOWS':
                wm_props.active_entry_door_window_library_name = sel_library.name

        if scene_props.library_tabs == 'APPLIANCES':
            wm_props.active_appliance_library_name = sel_library.name 

        if scene_props.library_tabs == 'CABINETS':
            wm_props.active_cabinet_library_name = sel_library.name 

        if scene_props.library_tabs == 'BUILD':
            if scene_props.build_tabs == 'STARTERS':
                wm_props.active_starter_library_name = sel_library.name
            if scene_props.build_tabs == 'INSERTS':
                wm_props.active_insert_library_name = sel_library.name
            if scene_props.build_tabs == 'PARTS':
                wm_props.active_part_library_name = sel_library.name

        if scene_props.library_tabs == 'FIXTURES':
            wm_props.active_fixture_library_name = sel_library.name 

        if scene_props.library_tabs == 'DECORATIONS':
            wm_props.active_decorations_library_name = sel_library.name
            
        if scene_props.library_tabs == 'MATERIALS':
            wm_props.active_materials_library_name = sel_library.name 
        
        asset_lib.path = os.path.join(self.asset_path)
        bpy.ops.asset.library_refresh()
        return {'FINISHED'}

class home_builder_OT_show_library_material_pointers(bpy.types.Operator):
    bl_idname = "home_builder.show_library_material_pointers"
    bl_label = "Library Material Pointers"

    library_name: bpy.props.StringProperty(name="Library Name")

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def execute(self, context):  
        return {'FINISHED'}

    def draw(self, context):
        wm_props = context.window_manager.home_builder
        workspace_props = context.workspace.home_builder
        asset = wm_props.home_builder_library_assets[workspace_props.home_builder_library_index]

        layout = self.layout
        scene_props = context.scene.home_builder
        box = layout.box()
        row = box.row()
        row.label(text=self.library_name)
        row.label(text="Selected Material: " + asset.file_data.name)
        col = box.column(align=True)
        for pointer in scene_props.material_pointers:
            if pointer.library_name == self.library_name:
                row = col.row()
                props = row.operator('home_builder.assign_material_to_pointer',text=pointer.name)
                props.library_name = self.library_name
                props.pointer_name = pointer.name     
                row.label(text=pointer.category_name + " - " + pointer.material_name,icon='MATERIAL')             
        

class home_builder_OT_assign_material_to_pointer(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_to_pointer"
    bl_label = "Assign Material to Pointer"

    library_name: bpy.props.StringProperty(name="Library Name")
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):  
        library = hb_utils.get_active_library(context)
        wm_props = context.window_manager.home_builder
        workspace_props = context.workspace.home_builder
        asset = wm_props.home_builder_library_assets[workspace_props.home_builder_library_index]
        scene_props = context.scene.home_builder
        for pointer in scene_props.material_pointers:
            if pointer.library_name == self.library_name and pointer.name == self.pointer_name:
                pointer.material_name = asset.file_data.name
                pointer.category_name = library.name
                pointer.library_path = os.path.join(library.library_path,"library.blend")
                bpy.ops.home_builder.update_materials_for_pointer(pointer_name=self.pointer_name)
        return {'FINISHED'}


class home_builder_OT_update_materials_for_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_materials_for_pointer"
    bl_label = "Update Materials for Pointer"

    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def get_material(self,library_path,material_name):
        if material_name in bpy.data.materials:
            return bpy.data.materials[material_name]

        if os.path.exists(library_path):

            with bpy.data.libraries.load(library_path) as (data_from, data_to):
                for mat in data_from.materials:
                    if mat == material_name:
                        data_to.materials = [mat]
                        break    
            
            for mat in data_to.materials:
                return mat

    def execute(self, context):  
        scene_props = context.scene.home_builder
        selected_pointer = None
        for pointer in scene_props.material_pointers:
            if pointer.name == self.pointer_name:
                selected_pointer = pointer

        for obj in bpy.data.objects:
            scene_props = bpy.context.scene.home_builder  
            for index, p in enumerate(obj.pyclone.pointers):
                if p.pointer_name == self.pointer_name:
                    if index + 1 <= len(obj.material_slots):
                        slot = obj.material_slots[index]
                        slot.material = self.get_material(selected_pointer.library_path,selected_pointer.material_name)    

        return {'FINISHED'}


class home_builder_OT_disconnect_constraint(bpy.types.Operator):
    bl_idname = "home_builder.disconnect_constraint"
    bl_label = "Disconnect Constraint"
    
    obj_name: bpy.props.StringProperty(name="Base Point Name")

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.constraints.clear()
        return {'FINISHED'}


classes = (
    home_builder_OT_about_home_builder,
    home_builder_OT_todo,
    home_builder_OT_update_library_path,
    home_builder_OT_show_library_material_pointers,
    home_builder_OT_assign_material_to_pointer,
    home_builder_OT_update_materials_for_pointer,
    home_builder_OT_disconnect_constraint,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
