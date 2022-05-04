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
import os
from .. import pyclone_utils
from ..pc_lib import pc_utils, pc_types

class TEXT_PT_pc_text(Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "PyClone"
    bl_label = "PyClone"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout    
        layout.label(text="PyClone Templates")
        TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'templates')
        layout.operator('text.open',text="Assembly Creation").filepath = os.path.join(TEMPLATE_PATH,"assembly_creation.py")
        layout.operator('text.open',text="Assembly Export").filepath = os.path.join(TEMPLATE_PATH,"assembly_export.py")

classes = (
    TEXT_PT_pc_text,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                        