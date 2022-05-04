import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os
from ..pc_lib import pc_types, pc_utils
from .. import pyclone_utils 

class pc_general_OT_change_file_browser_path(bpy.types.Operator):
    bl_idname = "pc_general.change_file_browser_path"
    bl_label = "Change File Browser Path"
    bl_description = "Changes the file browser path"
    bl_options = {'UNDO'}

    file_path: StringProperty(name='File Path')

    def execute(self, context):
        pyclone_utils.update_file_browser_path(context,self.file_path)
        return {'FINISHED'}

class pc_general_OT_prompts(bpy.types.Operator):
    bl_idname = "pc_general.prompts"
    bl_label = "Prompts"
    bl_description = "Opens the prompts for the selected assembly"
    bl_options = {'UNDO'}

    def execute(self, context):
        obj = context.object
        prompt_id = ""
        menu_id = ""
        if obj and "PROMPT_ID" in obj and obj["PROMPT_ID"] != "":
            prompt_id = obj["PROMPT_ID"]
        if obj and "MENU_ID" in obj and obj["MENU_ID"] != "":
            menu_id = obj["MENU_ID"]

        try:
            eval('bpy.ops.' + prompt_id + '("INVOKE_DEFAULT")')
            # eval('bpy.ops.' + prompt_id + '("INVOKE_DEFAULT",object_name=obj.name)')
        except:
            pass

        return {'FINISHED'}

class pc_general_OT_show_render_settings(Operator):
    bl_idname = "pc_general.show_render_settings"
    bl_label = "Render Settings"
    bl_description = "This will show the render settings"
    # bl_options = {'UNDO'}

    def check(self, context):    
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render        
        if rd.has_multiple_engines:
            box = layout.box()
            box.label(text="Render Type")
            row = box.row()
            row.label(text="Engine:")
            row.prop(rd, "engine", text="")  

        if context.engine == 'BLENDER_EEVEE':
            props = scene.eevee
            box = layout.box()
            box.label(text="Eevee Settings")
            box.prop(props, "use_gtao", text="Ambient Occlusion")
            box.prop(props, "use_bloom", text="Bloom")
            box.prop(props, "use_ssr", text="Screen Space Reflections")
            box.prop(props, "use_ssr_refraction", text="Screen Space Refraction")

            box = layout.box()
            box.label(text="Shadow Settings")
            row = box.row()
            row.label(text="Cube Size:")
            row.prop(props, "shadow_cube_size", text="")
            row = box.row()
            row.label(text="Cascade Size:")            
            row.prop(props, "shadow_cascade_size", text="")
            box.prop(props, "use_shadow_high_bitdepth", text="High Bit Depth")
            box.prop(props, "use_soft_shadows", text="Soft Shadows")

            box = layout.box()
            box.label(text="Samples")
            row = box.row()
            row.label(text="Render:")
            row.prop(props, "taa_render_samples", text="")
            row = box.row()
            row.label(text="Viewport:")            
            row.prop(props, "taa_samples", text="")

        if context.engine == 'CYCLES':
            cscene = scene.cycles     
            
            box = layout.box()
            box.label(text="Samples")
            row = box.row()
            row.label(text="Render:")
            row.prop(cscene, "samples", text="")
            row.prop(cscene, "use_denoising", text="")
            row = box.row()
            row.label(text="Viewport:")
            row.prop(cscene, "preview_samples", text="")   
            row.prop(cscene, "use_preview_denoising", text="")

            box = layout.box()
            box.label(text="Device Information")
            row = box.row()     
            row.label(text="Type:")       
            row.prop(cscene, "device",text="")
            row = box.row()   
            row.label(text="Threads:")   
            row.prop(rd, "threads_mode",text="")
            if rd.threads_mode == 'FIXED':
                row.prop(rd, "threads")

    def execute(self, context):

        return {'FINISHED'}

classes = (
    pc_general_OT_change_file_browser_path,
    pc_general_OT_prompts,
    pc_general_OT_show_render_settings,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()