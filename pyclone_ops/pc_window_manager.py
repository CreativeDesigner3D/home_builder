import bpy
import os
from bpy.types import Operator

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)

from .. import pyclone_utils

class WM_OT_drag_and_drop(bpy.types.Operator):
    bl_idname = "wm.drag_and_drop"
    bl_label = "Drag and Drop"
    bl_description = "This is a special operator that will be called when an image is dropped from the file browser"

    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    def execute(self, context):
        wm_props = pyclone_utils.get_wm_props(context.window_manager)
        scene_props = pyclone_utils.get_wm_props(context.scene)

        print('FILEPATH',self.filepath)
        filename, ext = os.path.splitext(self.filepath)
        if ext == '.blend':
            bpy.ops.wm.drop_blend_file('INVOKE_DEFAULT',filepath=self.filepath)
            return {'FINISHED'}
        if self.filepath == 'Error':
            path = pyclone_utils.get_file_browser_path(context)
            lib = wm_props.libraries[scene_props.active_library_name]
            eval('bpy.ops.' + lib.drop_id + '("INVOKE_DEFAULT",filepath=path)')
        elif scene_props.active_library_name in wm_props.libraries:
            lib = wm_props.libraries[scene_props.active_library_name]
            eval('bpy.ops.' + lib.drop_id + '("INVOKE_DEFAULT",filepath=self.filepath)')
        return {'FINISHED'}

classes = (
    WM_OT_drag_and_drop,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
