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

class pc_object_OT_select_object(Operator):
    bl_idname = "pc_object.select_object"
    bl_label = "Select Object"
    bl_description = "This selects an object and sets it as an active object"
    bl_options = {'UNDO'}

    obj_name: StringProperty(name='Object Name')

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        return True

    def execute(self, context):
        if self.obj_name in context.scene.objects:
            bpy.ops.object.select_all(action = 'DESELECT')
            obj = context.scene.objects[self.obj_name]
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}

class pc_object_OT_toggle_edit_mode(Operator):
    bl_idname = "pc_object.toggle_edit_mode"
    bl_label = "Toggle Edit Mode"
    bl_description = "This will toggle between object and edit mode"
    
    obj_name: StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.hide_set(False)
        obj.hide_select = False
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

class pc_object_OT_clear_vertex_groups(Operator):
    bl_idname = "pc_object.clear_vertex_groups"
    bl_label = "Clear Vertex Groups"
    bl_description = "This clears all of the vertex group assignments"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name")
    
    def execute(self,context):

        obj = bpy.data.objects[self.obj_name]
        
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
            
        for vgroup in obj.vertex_groups:
            for vert in obj.data.vertices:
                vgroup.remove((vert.index,))

        if obj.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()

        return{'FINISHED'}


class pc_object_OT_assign_verties_to_vertex_group(Operator):
    bl_idname = "pc_object.assign_verties_to_vertex_group"
    bl_label = "Assign Verties to Vertex Group"
    bl_description = "This assigns selected verties to the group that is passed in"
    bl_options = {'UNDO'}
    
    vertex_group_name: StringProperty(name="Vertex Group Name")
    
    def execute(self,context):

        obj = context.active_object
        
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
            
        vgroup = obj.vertex_groups[self.vertex_group_name]
        
        for vert in obj.data.vertices:
            if vert.select == True:
                vgroup.add((vert.index,),1,'ADD')

        if obj.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()

        return{'FINISHED'}

class pc_object_OT_apply_modifiers_and_drivers(Operator):
    bl_idname = "pc_object.apply_modifiers_and_drivers"
    bl_label = "Apply Modifiers and Drivers"
    bl_description = "This will apply all of the modifiers and drivers in the scene"
    bl_options = {'UNDO'}
    
    def execute(self,context):

        for obj in bpy.data.objects:
            pass
            for mod in obj.modifiers:
                if mod.type == 'HOOK':
                    pass #apply modifier

        return{'FINISHED'}

classes = (
    pc_object_OT_select_object,
    pc_object_OT_toggle_edit_mode,
    pc_object_OT_clear_vertex_groups,
    pc_object_OT_assign_verties_to_vertex_group
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
