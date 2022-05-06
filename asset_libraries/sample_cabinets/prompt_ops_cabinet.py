import bpy

class hb_sample_cabinets_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.cabinet_prompts"
    bl_label = "Cabinet Prompts"    

    def execute(self, context):
        return {'FINISHED'}

classes = (
    hb_sample_cabinets_OT_cabinet_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    