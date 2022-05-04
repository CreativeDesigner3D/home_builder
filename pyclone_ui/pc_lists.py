import bpy
from bpy.types import UIList
from ..pc_lib import pc_unit

class PC_UL_combobox(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

class PC_UL_prompts(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)
        if item.prompt_type == 'FLOAT':
            layout.label(text=str(item.float_value))
        if item.prompt_type == 'DISTANCE':
            layout.label(text=str(pc_unit.meter_to_active_unit(item.distance_value)))
        if item.prompt_type == 'ANGLE':
            layout.label(text=str(item.angle_value))
        if item.prompt_type == 'QUANTITY':
            layout.label(text=str(item.quantity_value))
        if item.prompt_type == 'PERCENTAGE':
            layout.label(text=str((item.percentage_value)))
        if item.prompt_type == 'CHECKBOX':
            layout.label(text=str(item.checkbox_value))
        if item.prompt_type == 'COMBOBOX':
            layout.label(text=str(item.combobox_index))
        if item.prompt_type == 'TEXT':
            layout.label(text=str(item.text_value))

class PC_UL_calculators(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

class PC_UL_scenes(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if not item.pyclone.is_view_scene:
            layout.label(text="Model Space",icon='SNAP_VOLUME')
        else:
            layout.label(text=item.name,icon='SNAP_FACE')
            layout.operator('pc_assembly.delete_assembly_layout',text="",icon='X',emboss=False).view_name = item.name

classes = (
    PC_UL_combobox,
    PC_UL_prompts,
    PC_UL_calculators,
    PC_UL_scenes
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
