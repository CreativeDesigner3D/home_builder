import bpy
from bpy.types import Header, Menu, Operator, PropertyGroup, Panel

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)

from ..pyclone_props import prompt_types


class pc_prompts_OT_add_prompt(Operator):
    bl_idname = "pc_prompts.add_prompt"
    bl_label = "Add Prompt"
    bl_description = "This adds a prompt to the object"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    prompt_type: EnumProperty(name="Prompt Type",items=prompt_types)
    # the_obj = PointerProperty(name="Object",type=bpy.types.Object) #WHY CANNOT I USE POINTER PROPERTY
    obj = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def execute(self, context):     
        self.obj.pyclone.add_prompt(self.prompt_type,self.prompt_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = bpy.data.objects[self.obj_name]    
        self.prompt_name = "New Prompt"
        counter = 1
        while self.prompt_name + " " + str(counter) in self.obj.pyclone.prompts:
            counter += 1
        self.prompt_name = self.prompt_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Prompt Name")
        row.prop(self,"prompt_name",text="")
        row = layout.row()
        row.label(text="Prompt Type")
        row.prop(self,"prompt_type",text="")


class pc_prompts_OT_delete_prompt(Operator):
    bl_idname = "pc_prompts.delete_prompt"
    bl_label = "Delete Prompt"
    bl_description = "This deletes the prompt that is passed in with prompt_name"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.pyclone.delete_prompt(self.prompt_name)
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.obj_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the prompt")
        layout.label(text=self.prompt_name)


class pc_prompts_OT_add_calculator(Operator):
    bl_idname = "pc_prompts.add_calculator"
    bl_label = "Add Calculator"
    bl_description = "This adds a calculator to the object"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Data Name",default="")

    calculator_name: StringProperty(name="Calculator Name",default="New Prompt")
    obj = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):     
        calc_distance_obj = bpy.data.objects.new('Calc Distance Obj',None)
        calc_distance_obj.empty_display_size = .001        
        calc_distance_obj.parent = self.obj.parent
        context.view_layer.active_layer_collection.collection.objects.link(calc_distance_obj)
        self.obj.pyclone.add_calculator(self.calculator_name,calc_distance_obj)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = bpy.data.objects[self.obj_name]
        self.calculator_name = "New Calculator"
        counter = 1
        while self.calculator_name + " " + str(counter) in self.obj.pyclone.calculators:
            counter += 1
        self.calculator_name = self.calculator_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Calculator Name")
        row.prop(self,"calculator_name",text="")


class pc_prompts_OT_add_calculator_prompt(Operator):
    bl_idname = "pc_prompts.add_calculator_prompt"
    bl_label = "Add Calculator"
    bl_description = "This adds a prompt to a calculator"
    bl_options = {'UNDO'}
    
    calculator_name: StringProperty(name="Calculator Name",default="")
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    obj = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def get_calculator(self):
        for calculator in self.obj.pyclone.calculators:
            if calculator.name == self.calculator_name:
                return calculator

    def execute(self, context):
        calculator = self.get_calculator()      
        calculator.add_calculator_prompt(self.prompt_name)
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = bpy.data.objects[self.obj_name]
        self.prompt_name = "New Prompt"
        counter = 1
        calculator = self.get_calculator()
        while self.prompt_name + " " + str(counter) in calculator.prompts:
            counter += 1
        self.prompt_name = self.prompt_name + " " + str(counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Prompt Name")
        row.prop(self,"prompt_name",text="")


class pc_prompts_OT_edit_calculator(Operator):
    bl_idname = "pc_prompts.edit_calculator"
    bl_label = "Edit Calculator"
    bl_description = "This opens a dialog to edit a calculator"
    bl_options = {'UNDO'}
    
    calculator_name: StringProperty(name="Calculator Name",default="")
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    obj = None
    calculator = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def get_calculator(self):
        for calculator in self.obj.pyclone.calculators:
            if calculator.name == self.calculator_name:
                return calculator

    def execute(self, context):
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        self.obj = self.get_data(context)
        self.calculator = self.get_calculator()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Calculator Name")
        row.prop(self.calculator,"name",text="")


class pc_prompts_OT_run_calculator(Operator):
    bl_idname = "pc_prompts.run_calculator"
    bl_label = "Run Calculator"
    bl_description = "This runs the calculate function for a calculator"
    bl_options = {'UNDO'}
    
    calculator_name: StringProperty(name="Calculator Name",default="")
    obj_name: StringProperty(name="Data Name",default="")

    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")
    obj = None
    calculator = None

    @classmethod
    def poll(cls, context):
        return True

    def get_data(self,context):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        else:
            return context.object

    def get_calculator(self):
        for calculator in self.obj.pyclone.calculators:
            if calculator.name == self.calculator_name:
                return calculator

    def execute(self, context):
        self.obj = self.get_data(context)
        self.calculator = self.get_calculator()
        if self.calculator:
            self.calculator.calculate()
        context.area.tag_redraw()
        return {'FINISHED'}


class pc_prompts_OT_edit_prompt(Operator):
    bl_idname = "pc_prompts.edit_prompt"
    bl_label = "Edit Prompt"
    bl_description = "This opens a dialog to edit a prompt"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    prompt = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.obj_name]
            self.prompt = obj.pyclone.prompts[self.prompt_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        self.prompt.draw_prompt_properties(layout)


class pc_prompts_OT_add_comboxbox_value(Operator):
    bl_idname = "pc_prompts.add_combobox_value"
    bl_label = "Add Combobox Value"
    bl_description = "This adds a combobox item to a combobox prompt"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    combobox_name: StringProperty(name="Combobox Name",default="Combobox Item")

    prompt = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        item = self.prompt.combobox_items.add()
        item.name = self.combobox_name
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.obj_name]
            self.prompt = obj.pyclone.prompts[self.prompt_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Name")
        row.prop(self,'combobox_name',text="")


class pc_prompts_OT_delete_comboxbox_value(Operator):
    bl_idname = "pc_prompts.delete_combobox_value"
    bl_label = "Delete Combobox Value"
    bl_description = "This deletes a combobox item from a combobox"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name",default="") #WHY DON"T POINTERS WORK?
    prompt_name: StringProperty(name="Prompt Name",default="New Prompt")

    combobox_name: StringProperty(name="Combobox Name",default="Combobox Item")

    prompt = None

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #TODO: Remove Item
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.obj_name in bpy.data.objects:
            obj = bpy.data.objects[self.obj_name]
            self.prompt = obj.pyclone.prompts[self.prompt_name]
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the combobox value")

classes = (
    pc_prompts_OT_add_prompt,
    pc_prompts_OT_delete_prompt,
    pc_prompts_OT_add_calculator,
    pc_prompts_OT_add_calculator_prompt,
    pc_prompts_OT_edit_calculator,
    pc_prompts_OT_run_calculator,
    pc_prompts_OT_edit_prompt,
    pc_prompts_OT_add_comboxbox_value,
    pc_prompts_OT_delete_comboxbox_value
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
