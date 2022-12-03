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
from pc_lib import pc_utils, pc_types

class TEXT_PT_python_crash_course(Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Documentation"
    bl_label = "Python Crash Course"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout    
        # layout.label(text="PyClone Examples")
        TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'docs','python_templates','Python Crash Course')
        layout.operator('text.open',text="Variables").filepath = os.path.join(TEMPLATE_PATH,"Variables.py")
        layout.operator('text.open',text="Arithmetic").filepath = os.path.join(TEMPLATE_PATH,"Arithmetic.py")

class TEXT_PT_pc_examples(Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Documentation"
    bl_label = "PyClone Examples"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout    
        # layout.label(text="PyClone Examples")
        TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'docs','python_templates','PyClone Examples')
        layout.operator('text.open',text="Assembly Creation").filepath = os.path.join(TEMPLATE_PATH,"assembly_creation.py")
        layout.operator('text.open',text="Assembly Export").filepath = os.path.join(TEMPLATE_PATH,"assembly_export.py")

classes = (
    TEXT_PT_python_crash_course,
    TEXT_PT_pc_examples,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                        