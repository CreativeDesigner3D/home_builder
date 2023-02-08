import bpy
import math
from pc_lib import pc_utils, pc_types, pc_unit
from . import const_cabinets as const


class hb_sample_cabinets_OT_single_adj_shelf_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.single_adj_shelf_prompts"
    bl_label = "Single Adjustable Shelf Prompts"

    insert = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_SINGLE_ADJ_SHELF_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        layout.prop(self.insert.obj_bp,'location',index=2,text="Shelf Location")


class hb_sample_cabinets_OT_cleat_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.cleat_prompts"
    bl_label = "Cleat Prompts"

    cleat_width: bpy.props.FloatProperty(name="Width",min=pc_unit.inch(1),unit='LENGTH',precision=4)

    part = None
    calculators = []

    def check(self, context):
        if self.part.obj_y.location.y > 0:
            self.part.obj_y.location.y = self.cleat_width
        else:
            self.part.obj_y.location.y = -self.cleat_width
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_CLEAT_TAG)
        self.part = pc_types.Assembly(bp)
        self.cleat_width = math.fabs(self.part.obj_y.location.y)

    def draw(self, context):
        layout = self.layout
        inset = self.part.get_prompt("Cleat Inset")
        width = self.part.get_prompt("Cleat Width")
        row = layout.row()
        row.label(text="Cleat Inset")
        row.prop(inset,'distance_value',text="")
        row = layout.row()
        row.label(text="Cleat Width")
        row.prop(self,'cleat_width',text="")


class hb_sample_cabinets_OT_back_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.back_prompts"
    bl_label = "Back Prompts"

    part = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_BACK_TAG)
        self.part = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        inset = self.part.get_prompt("Back Inset")
        row = layout.row()
        row.label(text="Back Inset")
        row.prop(inset,'distance_value',text="")


classes = (
    hb_sample_cabinets_OT_single_adj_shelf_prompts,
    hb_sample_cabinets_OT_cleat_prompts,
    hb_sample_cabinets_OT_back_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                   