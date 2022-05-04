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

from .. import pyclone_utils
from ..pc_lib import pc_unit, pc_utils, pc_types


class PC_prompt_collection(PropertyGroup):
    add: BoolProperty(name="Add")
    prompt_type: StringProperty(name="Type")

class DRIVER_OT_get_vars_from_object(Operator):
    bl_idname = "pc_driver.get_vars_from_object"
    bl_label = "Quick Variables"
    bl_description = "This gets the available variables from an object"
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name='Object Name')
    var_object_name: StringProperty(name='Variable Object Name')
    data_path: StringProperty(name='Data Path')
    array_index: IntProperty(name='Array Index')
    
    x_dim: BoolProperty(name='X Dimension',default=False)
    y_dim: BoolProperty(name='Y Dimension',default=False)
    z_dim: BoolProperty(name='Z Dimension',default=False)
    x_loc: BoolProperty(name='X Location',default=False)
    y_loc: BoolProperty(name='Y Location',default=False)
    z_loc: BoolProperty(name='Z Location',default=False)
    x_rot: BoolProperty(name='X Rotation',default=False)
    y_rot: BoolProperty(name='Y Rotation',default=False)
    z_rot: BoolProperty(name='Z Rotation',default=False)
    
    prompts: CollectionProperty(name='Collection Prompts',type=PC_prompt_collection)
    
    obj = None
    assembly = None
    
    @classmethod
    def poll(cls, context):
        return True

    def get_prompts(self):
        for old_prompt in self.prompts:
            self.prompts.remove(0)

        if self.assembly:
            for prompt in self.assembly.obj_prompts.pyclone.prompts:
                prompt_copy = self.prompts.add()
                prompt_copy.name = prompt.name
                prompt_copy.prompt_type = prompt.prompt_type
        else:
            for prompt in self.obj.pyclone.prompts:
                prompt_copy = self.prompts.add()
                prompt_copy.name = prompt.name
                prompt_copy.prompt_type = prompt.prompt_type

    def execute(self, context):
        drivers = pyclone_utils.get_drivers(self.obj)
        for DR in drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                # DR.driver.show_debug_info = False
                if self.x_loc:
                    var = DR.driver.variables.new()
                    var.name = 'loc_x'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_bp
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'location.x'
                if self.y_loc:
                    var = DR.driver.variables.new()
                    var.name = 'loc_y'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_bp
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'location.y'
                if self.z_loc:
                    var = DR.driver.variables.new()
                    var.name = 'loc_z'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_bp
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'location.z'
                if self.x_rot:
                    var = DR.driver.variables.new()
                    var.name = 'rot_x'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_bp
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'rotation_euler.x'
                if self.y_rot:
                    var = DR.driver.variables.new()
                    var.name = 'rot_y'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_bp
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'rotation_euler.y'
                if self.z_rot:
                    var = DR.driver.variables.new()
                    var.name = 'rot_z'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_bp
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'rotation_euler.z'
                if self.x_dim:
                    var = DR.driver.variables.new()
                    var.name = 'dim_x'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_x
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'location.x'
                if self.y_dim:
                    var = DR.driver.variables.new()
                    var.name = 'dim_y'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_y
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'location.y'
                if self.z_dim:
                    var = DR.driver.variables.new()
                    var.name = 'dim_z'
                    if self.assembly:
                        var.targets[0].id = self.assembly.obj_z
                    else:
                        var.targets[0].id = self.obj
                    var.targets[0].data_path = 'location.z'      

                for prompt in self.prompts:
                    if prompt.add:
                        var = DR.driver.variables.new()
                        var.name = prompt.name.replace(" ","")
                        if self.assembly:
                            var.targets[0].id = self.assembly.obj_prompts
                        else:
                            var.targets[0].id = self.obj                            
                        
                        if prompt.prompt_type == 'FLOAT':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].float_value'
                        if prompt.prompt_type == 'DISTANCE':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].distance_value'
                        if prompt.prompt_type == 'ANGLE':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].angle_value'
                        if prompt.prompt_type == 'QUANTITY':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].quantity_value'
                        if prompt.prompt_type == 'PERCENTAGE':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].percentage_value'
                        if prompt.prompt_type == 'CHECKBOX':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].checkbox_value'
                        if prompt.prompt_type == 'COMBOBOX':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].combobox_index'
                        if prompt.prompt_type == 'TEXT':
                            var.targets[0].data_path = 'pyclone.prompts["' + prompt.name + '"].text_value'

                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
                    
        #HOW DO I UPDATE THIS DATA!?!?
        if self.assembly:
            self.assembly.obj_prompts.tag = True
            self.assembly.obj_prompts.update_tag(refresh={'OBJECT', 'DATA', 'TIME'})
        self.obj.tag = True
        self.obj.update_tag(refresh={'OBJECT', 'DATA', 'TIME'})
        context.view_layer.update()
        return {'FINISHED'}

    def reset_variables(self):
        self.x_dim = False
        self.y_dim = False
        self.z_dim = False
        self.x_loc = False
        self.y_loc = False
        self.z_loc = False
        self.x_rot = False
        self.y_rot = False
        self.z_rot = False

    def invoke(self,context,event):
        self.reset_variables()
        self.obj = bpy.data.objects[self.object_name]
        var_obj = bpy.data.objects[self.var_object_name]
        obj_bp = pc_utils.get_assembly_bp(var_obj)
        if obj_bp:
            self.assembly = pc_types.Assembly(obj_bp)
        self.get_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        if self.assembly:
            box.label(text='Main Properties - ' + self.assembly.obj_bp.name)
        else:
            box.label(text='Main Properties - ' + self.obj.name)
        row = box.row()
        col = row.column()
        col.prop(self,'x_dim')
        col.prop(self,'y_dim')
        col.prop(self,'z_dim')
        col = row.column()
        col.prop(self,'x_loc')
        col.prop(self,'y_loc')
        col.prop(self,'z_loc')
        col = row.column()
        col.prop(self,'x_rot')
        col.prop(self,'y_rot')
        col.prop(self,'z_rot')
        box = layout.box()
        box.label(text='Prompts')
        col = box.column(align=True)
        for prompt in self.prompts:
            row = col.row()
            row.label(text=prompt.name)
            row.prop(prompt,'add')

class DRIVER_OT_remove_variable(Operator):
    bl_idname = "pc_driver.remove_variable"
    bl_label = "Remove Variable"
    bl_description = "This removes a variable"
    bl_options = {'UNDO'}
    
    object_name: StringProperty(name='Object Name')
    data_path: StringProperty(name='Data Path')
    var_name: StringProperty(name='Variable Name')
    array_index: IntProperty(name='Array Index')

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        drivers = pyclone_utils.get_drivers(obj)
        for driver in drivers:
            if driver.data_path == self.data_path:
                if driver.array_index == self.array_index:
                    for var in driver.driver.variables:
                        if var.name == self.var_name:
                            driver.driver.variables.remove(var)
        return {'FINISHED'}


class DRIVER_OT_add_driver(Operator):
    bl_idname = "pc_driver.add_driver"
    bl_label = "Add Driver"
    bl_description = "This adds a driver to a prompt"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        assembly_bp = pc_utils.get_assembly_bp(context.object)    
        assembly = pc_types.Assembly(assembly_bp)
        prompt = assembly.obj_prompts.pyclone.prompts[assembly.obj_prompts.pyclone.prompt_index]
        assembly.obj_prompts.driver_add(prompt.get_data_path())
        return {'FINISHED'}


class DRIVER_OT_remove_driver(Operator):
    bl_idname = "pc_driver.remove_driver"
    bl_label = "Remove Driver"
    bl_description = "This removes a driver on a prompt"
    bl_options = {'UNDO'}

    def execute(self, context):
        assembly_bp = pc_utils.get_assembly_bp(context.object)    
        assembly = pc_types.Assembly(assembly_bp)
        prompt = assembly.obj_prompts.pyclone.prompts[assembly.obj_prompts.pyclone.prompt_index]
        assembly.obj_prompts.driver_remove(prompt.get_data_path())
        return {'FINISHED'}


class DRIVER_OT_add_calculator_driver(Operator):
    bl_idname = "pc_driver.add_calculator_driver"
    bl_label = "Add Calculator Driver"
    bl_description = "This adds a driver to a prompt"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        assembly_bp = pc_utils.get_assembly_bp(context.object)    
        assembly = pc_types.Assembly(assembly_bp)
        calculator = assembly.obj_prompts.pyclone.calculators[assembly.obj_prompts.pyclone.calculator_index]
        if calculator.distance_obj:
            calculator.distance_obj.driver_add('pyclone.calculator_distance')
        return {'FINISHED'}


class DRIVER_OT_remove_calculator_driver(Operator):
    bl_idname = "pc_driver.remove_calculator_driver"
    bl_label = "Remove Calculator Driver"
    bl_description = "This removes a driver on a prompt"
    bl_options = {'UNDO'}

    def execute(self, context):
        assembly_bp = pc_utils.get_assembly_bp(context.object)    
        assembly = pc_types.Assembly(assembly_bp)
        calculator = assembly.obj_prompts.pyclone.calculators[assembly.obj_prompts.pyclone.calculator_index]
        if calculator.distance_obj:
            calculator.distance_obj.driver_remove('pyclone.calculator_distance')
        return {'FINISHED'}


classes = (
    PC_prompt_collection,
    DRIVER_OT_get_vars_from_object,
    DRIVER_OT_remove_variable,
    DRIVER_OT_add_driver,
    DRIVER_OT_remove_driver,
    DRIVER_OT_add_calculator_driver,
    DRIVER_OT_remove_calculator_driver,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()          