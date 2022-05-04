import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        )

from .. import pyclone_utils
from ..pc_lib import pc_utils, pc_types

class VIEW3D_PT_pc_object_prompts(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Prompts"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='LINENUMBERS_ON')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        obj.pyclone.draw_prompts(layout)

class VIEW3D_PT_pc_object_material_pointers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Material Pointers"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='SHADING_TEXTURE')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        slot = None
        if len(obj.material_slots) >= obj.active_material_index + 1:
            slot = obj.material_slots[obj.active_material_index]

        is_sortable = len(obj.material_slots) > 1
        rows = 3
        if (is_sortable):
            rows = 5

        row = layout.row()

        if obj.type == 'GPENCIL':
            row.template_list("GPENCIL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=rows)
        else:
            row.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=rows)

        col = row.column(align=True)
        col.operator("pc_material.add_material_slot", icon='ADD', text="").object_name = obj.name
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

        if is_sortable:
            col.separator()

            col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if slot:
            row = layout.row()
            if len(obj.pyclone.pointers) >= obj.active_material_index + 1:
                pointer_slot = obj.pyclone.pointers[obj.active_material_index]
                row.prop(pointer_slot,'name')
                row = layout.row()
                row.prop(pointer_slot,'pointer_name')
            else:
                row.operator('pc_material.add_material_pointers').object_name = obj.name

        # row = layout.row()
        # row.template_ID(obj, "active_material", new="material.new")
        # if slot:
        #     icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
        #     row.prop(slot, "link", icon=icon_link, icon_only=True)

        if obj.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")

        # if obj.type == 'GPENCIL':
        #     pass
        # else:
        #     layout.operator("bp_general.open_new_editor",text="Open Material Editor",icon='MATERIAL').space_type = 'NODE_EDITOR'


class VIEW3D_PT_pc_object_drivers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Object"
    bl_label = "Drivers"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='AUTO')

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            drivers = pyclone_utils.get_drivers(obj)

            if len(drivers) == 0:
                layout.label(text="No Drivers Found on Object")

            for driver in drivers:
                pyclone_utils.draw_driver(layout,obj,driver)

classes = (
    VIEW3D_PT_pc_object_prompts,
    VIEW3D_PT_pc_object_drivers,
    VIEW3D_PT_pc_object_material_pointers
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
