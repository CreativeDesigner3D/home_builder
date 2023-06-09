import bpy
from . import paths_doors_windows
from . import utils_doors_windows
from . import const_doors_windows as const
from pc_lib import pc_utils

class HOME_BUILDER_MT_doors_windows_settings(bpy.types.Menu):
    bl_label = "Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="HOME_BUILDER_PT_door_window_parts",text="Door and Window Parts",icon='ASSET_MANAGER')
        layout.popover(panel="HOME_BUILDER_PT_door_window_sizes",text="Door and Window Sizes",icon='DRIVER_DISTANCE')


class HOME_BUILDER_MT_window_commands(bpy.types.Menu):
    bl_idname = const.menu_name + "_MT_window_commands"
    bl_label = "Window Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        layout = self.layout
        layout.operator('home_builder.delete_assembly',text="Delete Window",icon='X').obj_name = bp.name


class HOME_BUILDER_MT_door_commands(bpy.types.Menu):
    bl_label = "Door Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.ENTRY_DOOR_TAG)
        layout = self.layout
        layout.operator('home_builder.delete_assembly',text="Delete Entry Door",icon='X').obj_name = bp.name


class HOME_BUILDER_MT_door_panel_library_commands(bpy.types.Menu):
    bl_label = "Door Panel Library Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        path = paths_doors_windows.get_entry_door_panel_path()
        layout = self.layout
        layout.operator('doors_windows.create_new_asset',text="Create New Door Panel",icon='ADD').asset_type = "ENTRY_DOOR_PANEL"
        layout.operator('home_builder.open_browser_window',text="Open Library Path",icon='FILE_FOLDER').path = path
        layout.operator('doors_windows.save_asset_to_library',text="Save Door Panel to Library",icon='FILE').asset_type = "ENTRY_DOOR_PANEL"


class HOME_BUILDER_MT_door_frame_library_commands(bpy.types.Menu):
    bl_label = "Door Frame Library Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        path = paths_doors_windows.get_entry_door_frame_path()
        layout = self.layout
        layout.operator('doors_windows.create_new_asset',text="Create New Door Panel",icon='ADD').asset_type = "ENTRY_DOOR_FRAME"
        layout.operator('home_builder.open_browser_window',text="Open Library Path",icon='FILE_FOLDER').path = path
        layout.operator('doors_windows.save_asset_to_library',text="Save Door Frame to Library",icon='FILE').asset_type = "ENTRY_DOOR_FRAME"


class HOME_BUILDER_MT_door_handle_library_commands(bpy.types.Menu):
    bl_label = "Door Handle Library Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        path = paths_doors_windows.get_entry_door_handle_path()
        layout = self.layout
        layout.operator('home_builder.open_browser_window',text="Open Library Path",icon='FILE_FOLDER').path = path
        layout.operator('doors_windows.save_asset_to_library',text="Save Door Handle to Library",icon='FILE').asset_type = "ENTRY_DOOR_HANDLE"
        layout.operator('doors_windows.add_handle_to_scene',text="Add Handle to Scene",icon='ADD')


class HOME_BUILDER_MT_window_frame_library_commands(bpy.types.Menu):
    bl_label = "Window Frame Library Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        path = paths_doors_windows.get_window_frame_path()
        layout = self.layout
        layout.operator('doors_windows.create_new_asset',text="Create New Window Frame",icon='ADD').asset_type = "WINDOW_FRAME"
        layout.operator('home_builder.open_browser_window',text="Open Library Path",icon='FILE_FOLDER').path = path
        layout.operator('doors_windows.save_asset_to_library',text="Save Window Frame to Library",icon='FILE').asset_type = "WINDOW_FRAME"


class HOME_BUILDER_MT_window_insert_library_commands(bpy.types.Menu):
    bl_label = "Window Insert Library Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        path = paths_doors_windows.get_window_insert_path()
        layout = self.layout
        layout.operator('doors_windows.create_new_asset',text="Create New Window Insert",icon='ADD').asset_type = "WINDOW_INSERT"
        layout.operator('home_builder.open_browser_window',text="Open Library Path",icon='FILE_FOLDER').path = path
        layout.operator('doors_windows.save_asset_to_library',text="Save Window Insert to Library",icon='FILE').asset_type = "WINDOW_INSERT"


class HOME_BUILDER_PT_door_window_parts(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Door and Window Parts"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 32

    def draw(self, context):
        layout = self.layout
        layout.label(text="Door and Window Parts")        
        props = utils_doors_windows.get_scene_props(context.scene)

        box = layout.box()
        box.label(text="Door Parts")

        row = box.row()
        row.label(text="Door Panel")
        row.menu('HOME_BUILDER_MT_door_panel_library_commands',text="",icon="SETTINGS")
        row.label(text="Door Frame")
        row.menu('HOME_BUILDER_MT_door_frame_library_commands',text="",icon="SETTINGS")
        row.label(text="Door Handle")
        row.menu('HOME_BUILDER_MT_door_handle_library_commands',text="",icon="SETTINGS")

        row = box.row()
        row.prop(props,'entry_door_panel_category',text="")
        row.prop(props,'entry_door_frame_category',text="")
        row.prop(props,'entry_door_handle_category',text="")

        row = box.row()
        row.template_icon_view(props,"entry_door_panel",show_labels=True)   
        row.template_icon_view(props,"entry_door_frame",show_labels=True)   
        row.template_icon_view(props,"entry_door_handle",show_labels=True)   

        box = layout.box()
        box.label(text="Window Parts")

        row = box.row()
        row.label(text="Window Frame")
        row.menu('HOME_BUILDER_MT_window_frame_library_commands',text="",icon="SETTINGS")
        row.label(text="Window Insert")
        row.menu('HOME_BUILDER_MT_window_insert_library_commands',text="",icon="SETTINGS")

        row = box.row()
        row.prop(props,'window_frame_category',text="")
        row.prop(props,'window_insert_category',text="")

        row = box.row()
        row.template_icon_view(props,"window_frame",show_labels=True)   
        row.template_icon_view(props,"window_insert",show_labels=True)  


class HOME_BUILDER_PT_door_window_sizes(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Door and Window Sizes"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 14

    def draw(self, context):
        layout = self.layout
        layout.label(text="Door and Window Sizes")        
        props = utils_doors_windows.get_scene_props(context.scene)

        box = layout.box()
        box.label(text="Entry Door Sizes")  
        row = box.row()
        row.label(text="Single Door Width")
        row.prop(props,'single_door_width',text="") 
        row = box.row()
        row.label(text="Double Door Width")         
        row.prop(props,'double_door_width',text="")  
        row = box.row()
        row.label(text="Door Height")        
        row.prop(props,'door_height',text="")  

        box = layout.box()       
        box.label(text="Window Sizes")  
        row = box.row()
        row.label(text="Window Height")           
        row.prop(props,'window_height',text="")     
        row = box.row()
        row.label(text="Window Height from Floor")           
        row.prop(props,'window_height_from_floor',text="")   
        


classes = (
    HOME_BUILDER_MT_doors_windows_settings,
    HOME_BUILDER_MT_window_commands,
    HOME_BUILDER_MT_door_commands,
    HOME_BUILDER_MT_door_panel_library_commands,
    HOME_BUILDER_MT_door_frame_library_commands,
    HOME_BUILDER_MT_door_handle_library_commands,
    HOME_BUILDER_MT_window_frame_library_commands,
    HOME_BUILDER_MT_window_insert_library_commands,
    HOME_BUILDER_PT_door_window_parts,
    HOME_BUILDER_PT_door_window_sizes,
)

register, unregister = bpy.utils.register_classes_factory(classes)             