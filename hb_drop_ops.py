import bpy
import os
from pc_lib import pc_utils

class home_builder_OT_drop_material(bpy.types.Operator):
    bl_idname = "home_builder.drop_material"
    bl_label = "Drop Material"

    mat = None
    region = None

    @classmethod
    def poll(cls, context):  
        if context.object and context.object.mode != 'OBJECT':
            return False
        return True
        
    def execute(self, context):
        self.region = pc_utils.get_3d_view_region(context)
        self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def get_material(self,context):
        wm_props = context.window_manager.home_builder
        library = wm_props.get_active_library(context)
        asset = wm_props.get_active_asset(context)
        return pc_utils.get_material(library.library_path,asset.file_data.name)

    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,self.region,event)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select_set(True)
            context.view_layer.objects.active = selected_obj
        
            if pc_utils.event_is_place_asset(event):
                if hasattr(selected_obj.data,'uv_layers') and len(selected_obj.data.uv_layers) == 0:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT') 
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)  
                    bpy.ops.object.editmode_toggle()

                if len(selected_obj.material_slots) == 0:
                    bpy.ops.object.material_slot_add()

                if len(selected_obj.pyclone.pointers) > 0:
                    print(self.mat,selected_obj)
                    bpy.ops.home_builder.assign_material_dialog('INVOKE_DEFAULT',material_name = self.mat.name, object_name = selected_obj.name)
                    return self.finish(context)
                else:
                    for slot in selected_obj.material_slots:
                        slot.material = self.mat
                        
                return self.finish(context)

        if pc_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if pc_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_assign_material_dialog(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_dialog"
    bl_label = "Assign Material Dialog"
    bl_description = "This is a dialog to assign materials to Home Builder objects"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    obj = None
    material = None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        self.material = bpy.data.materials[self.material_name]
        self.obj = bpy.data.objects[self.object_name]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=480)
        
    def draw(self,context):
        scene_props = pc_utils.get_hb_scene_props(context.scene)
        # obj_props = home_builder_utils.get_object_props(self.obj)
        layout = self.layout
        box = layout.box()
        box.label(text=self.obj.name,icon='OBJECT_DATA')
        pointer_list = []

        # if len(scene_props.material_pointer_groups) - 1 >= obj_props.material_group_index:
        #     mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        # else:
        #     mat_group = scene_props.material_pointer_groups[0]

        for index, mat_slot in enumerate(self.obj.material_slots):
            row = box.split(factor=.80)
            pointer = None

            if index + 1 <= len(self.obj.pyclone.pointers):
                pointer = self.obj.pyclone.pointers[index]

            if mat_slot.name == "":
                row.label(text='No Material')
            else:
                if pointer:
                    row.prop(mat_slot,"name",text=pointer.name,icon='MATERIAL')
                else:
                    row.prop(mat_slot,"name",text=" ",icon='MATERIAL')

            if pointer and pointer.pointer_name not in pointer_list and pointer.pointer_name != "":
                pointer_list.append(pointer.pointer_name)

            props = row.operator('home_builder.assign_material_to_slot',text="Override",icon='BACK')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index

        if len(pointer_list) > 0:
            box = layout.box()
            row = box.row()
            row.label(text="Update Material Pointers",icon='MATERIAL')
            for pointer in pointer_list:
                row = box.split(factor=.80)
                mat_pointer = scene_props.material_pointers[pointer] 
                row.label(text=pointer + ": " + mat_pointer.category_name + "/" + mat_pointer.material_name)    
                props = row.operator('home_builder.assign_material_to_pointer',text="Update All",icon='FILE_REFRESH')
                props.pointer_name = pointer
        
    def execute(self,context):
        return {'FINISHED'}        


class home_builder_OT_assign_material_to_slot(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_to_slot"
    bl_label = "Assign Material to Slot"
    bl_description = "This will assign a material to a material slot"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    index: bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        obj.material_slots[self.index].material = mat
        return {'FINISHED'}

classes = (
    home_builder_OT_drop_material,
    home_builder_OT_assign_material_dialog,
    home_builder_OT_assign_material_to_slot,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        