import bpy
from . import utils_doors_windows
class HOME_BUILDER_MT_doors_windows_settings(bpy.types.Menu):
    bl_label = "Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="HOME_BUILDER_PT_door_window_parts",text="Door and Window Parts",icon='DRIVER_DISTANCE')
        layout.separator()
        layout.operator('hb_sample_cabinets.build_library',text="Build Cabinet Library")

class HOME_BUILDER_PT_door_window_parts(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Door and Window Parts"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 32

    def draw(self, context):
        layout = self.layout
        layout.label(text="Door and Window Parts")        
        props = utils_doors_windows.get_scene_props(context.scene)
        row = layout.row()
        row.prop(props,'entry_door_panel_category',text="")
        row.prop(props,'entry_door_frame_category',text="")
        row.prop(props,'entry_door_handle_category',text="")

        row = layout.row()
        row.template_icon_view(props,"entry_door_panel",show_labels=True)   
        row.template_icon_view(props,"entry_door_frame",show_labels=True)   
        row.template_icon_view(props,"entry_door_handle",show_labels=True)   


classes = (
    HOME_BUILDER_MT_doors_windows_settings,
    HOME_BUILDER_PT_door_window_parts,
)

register, unregister = bpy.utils.register_classes_factory(classes)             