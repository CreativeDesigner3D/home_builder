import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)

from ..pc_lib import pc_unit, pc_utils, pc_types

class pc_material_OT_add_material_slot(bpy.types.Operator):
    bl_idname = "pc_material.add_material_slot"
    bl_label = "Add Material Slot"
    bl_description = "This adds a material slot and a material pointer"
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name="Object Name")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        obj.pyclone.pointers.add()
        override = {'active_object':obj,'object':obj}
        bpy.ops.object.material_slot_add(override)
        return{'FINISHED'}


class pc_material_OT_add_material_pointer(bpy.types.Operator):
    bl_idname = "pc_material.add_material_pointers"
    bl_label = "Add Material Pointers"
    bl_description = "This add a material pointer"
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name="Object Name")
    
    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        for index, mat_slot in enumerate(obj.material_slots):
            if len(obj.pyclone.pointers) < index + 1:
                slot = obj.pyclone.pointers.add()
        return{'FINISHED'}

classes = (
    pc_material_OT_add_material_slot,
    pc_material_OT_add_material_pointer,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
