import bpy,os

from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator,
                       PropertyGroup)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)

from ..pc_lib import pc_unit, pc_utils, pc_types

class pc_library_OT_set_active_library(Operator):
    bl_idname = "pc_library.set_active_library"
    bl_label = "Set Active Library"
    bl_description = "This will set the active library"
    bl_options = {'UNDO'}
    
    library_name: StringProperty(name='Library Name')

    def execute(self, context):
        pyclone_scene = pc_utils.get_scene_props(context.scene)
        pyclone_scene.active_library_name = self.library_name

        pyclone_wm = pc_utils.get_scene_props(context.window_manager)
        for library in pyclone_wm.libraries:
            if library.name == self.library_name:
                if library.activate_id != "":
                    eval('bpy.ops.' + library.activate_id + '("INVOKE_DEFAULT",library_name=self.library_name)')
                    
        context.area.tag_redraw()
        return {'FINISHED'}

classes = (
    pc_library_OT_set_active_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
