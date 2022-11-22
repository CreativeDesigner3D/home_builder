import bpy
import os
import math
import inspect
import subprocess
import codecs
import time
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from pc_lib import pc_types, pc_unit, pc_utils
from . import library_cabinet
from . import utils_cabinet
from . import utils_placement
from . import types_closet_starters
from . import types_cabinet
from . import assemblies_cabinet
from . import const_cabinets as const
from . import types_fronts
from . import paths_cabinet

class Cabinet_Library_Item(bpy.types.PropertyGroup):
    library_type: StringProperty(name="Library Type")
    is_checked: BoolProperty(name="Is Checked")


class hb_sample_cabinets_OT_active_cabinet_library(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.active_cabinet_library"
    bl_label = "Active Cabinet Library"

    asset_name: StringProperty(name="Asset Name")

    def execute(self, context):
        return {'FINISHED'}


class hb_sample_cabinets_OT_assign_handle_pointer(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.assign_handle_pointer"
    bl_label = "Assign Handle Pointer"

    pointer_name: StringProperty(name="Pointer Name")

    def execute(self, context):
        props = utils_cabinet.get_scene_props(context.scene)
        pointer = eval("props." + self.pointer_name)
        pointer.category_name = props.cabinet_handle_category
        pointer.item_name = props.cabinet_handle
        return {'FINISHED'}


class hb_sample_cabinets_OT_assign_door_pointer(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.assign_door_pointer"
    bl_label = "Assign Door Pointer"

    pointer_name: StringProperty(name="Pointer Name")

    def execute(self, context):
        props = utils_cabinet.get_scene_props(context.scene)
        pointer = eval("props." + self.pointer_name)
        pointer.category_name = props.cabinet_door_category
        pointer.item_name = props.cabinet_door
        return {'FINISHED'}


class hb_sample_cabinets_OT_assign_molding_pointer(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.assign_molding_pointer"
    bl_label = "Assign Molding Pointer"

    pointer_name: StringProperty(name="Pointer Name")

    def execute(self, context):
        props = utils_cabinet.get_scene_props(context.scene)
        pointer = eval("props." + self.pointer_name)
        pointer.category_name = props.molding_category
        pointer.item_name = props.molding
        return {'FINISHED'}


class hb_sample_cabinets_OT_change_closet_offsets(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.change_closet_offsets"
    bl_label = "Change Closet Offsets"
    bl_description = "This allows you to easily adjust the closets left and right offset"
    bl_options = {'UNDO'}
    
    anchor_type: EnumProperty(name="Anchor Type",
                              items=[('SET_OFFSETS',"Set Offsets","Set Offsets"),
                                     ('FILL',"Fill","Fill"),
                                     ('LEFT',"Left","Left"),
                                     ('RIGHT',"Right","Right"),
                                     ('CENTER','Center','Center')],
                              default='SET_OFFSETS')

    left_offset: FloatProperty(name="Left Offset",subtype='DISTANCE',precision=5)
    right_offset: FloatProperty(name="Right Offset",subtype='DISTANCE',precision=5)
    fill_left_offset: FloatProperty(name="Left Offset",subtype='DISTANCE',precision=5)
    fill_right_offset: FloatProperty(name="Right Offset",subtype='DISTANCE',precision=5)    
    set_offset_start_x: FloatProperty(name="Set Offset Start X",subtype='DISTANCE',precision=5)
    start_x: FloatProperty(name="Start X",subtype='DISTANCE',precision=5)
    start_width: FloatProperty(name="Start Width",subtype='DISTANCE',precision=5)
    set_offset_start_width: FloatProperty(name="Set Offset Start Width",subtype='DISTANCE',precision=5)
    change_width: FloatProperty(name="Change Width",subtype='DISTANCE',precision=5)

    wall = None
    closet = None
    calculators = []

    def check(self, context):
        if self.anchor_type == 'SET_OFFSETS':
            left_offset = self.closet.get_prompt("Left Offset")
            right_offset = self.closet.get_prompt("Right Offset")
            left_offset.set_value(self.left_offset)
            right_offset.set_value(self.right_offset)            
            self.closet.obj_bp.location.x = self.set_offset_start_x + self.left_offset
            self.closet.obj_x.location.x = self.set_offset_start_width - self.left_offset - self.right_offset
        if self.anchor_type == 'FILL':
            if self.wall:
                left_x = utils_placement.get_left_collision_location(self.closet)
                right_x = utils_placement.get_right_collision_location(self.closet)
                offsets = self.fill_left_offset + self.fill_right_offset
                self.closet.obj_bp.location.x = left_x + self.fill_left_offset
                self.closet.obj_x.location.x = (right_x - left_x - offsets)              
        if self.anchor_type == 'LEFT':
            self.closet.obj_x.location.x = self.change_width
        if self.anchor_type == 'RIGHT':
            self.closet.obj_bp.location.x = self.start_x + (self.start_width - self.change_width)
            self.closet.obj_x.location.x = self.change_width
        if self.anchor_type == 'CENTER':
            self.closet.obj_bp.location.x = self.start_x + (self.start_width - self.change_width)/2
            self.closet.obj_x.location.x = self.change_width     
        for calculator in self.calculators:
            calculator.calculate()
        return True
    
    def invoke(self, context, event):
        self.closet = None
        self.wall = None
        self.calculators = []
        self.left_offset = 0
        self.right_offset = 0
        self.fill_left_offset = 0
        self.fill_right_offset = 0
        self.anchor_type = 'SET_OFFSETS'
        closet_bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        wall_bp = pc_utils.get_bp_by_tag(context.object,const.WALL_TAG)
        if closet_bp:
            self.closet = pc_types.Assembly(closet_bp)
            left_offset = self.closet.get_prompt("Left Offset").get_value()
            right_offset = self.closet.get_prompt("Right Offset").get_value()            
            self.start_x = self.closet.obj_bp.location.x
            self.left_offset = left_offset
            self.right_offset = right_offset
            self.set_offset_start_x = self.closet.obj_bp.location.x - self.left_offset
            self.set_offset_start_width = self.closet.obj_x.location.x + self.left_offset + self.right_offset
            self.start_width = self.closet.obj_x.location.x
            self.change_width = self.closet.obj_x.location.x
            self.get_calculators(self.closet.obj_bp)
        if wall_bp:
            self.wall = pc_types.Assembly(wall_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=320)
        
    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)        

    def draw(self,context):        
        layout = self.layout
        row = layout.row(align=True)
        row.prop_enum(self, "anchor_type", 'SET_OFFSETS') 
        if self.wall:
            row.prop_enum(self, "anchor_type", 'FILL') 
        row.prop_enum(self, "anchor_type", 'LEFT')  
        row.prop_enum(self, "anchor_type", 'RIGHT')      
        row.prop_enum(self, "anchor_type", 'CENTER')       

        if self.anchor_type == 'SET_OFFSETS':   
            row = layout.row()
            row.label(text="Offsets:")    
            row.prop(self,'left_offset',text="Left")
            row.prop(self,'right_offset',text="Right")
            row = layout.row()
            row.label(text="Closet Width")
            row.label(text=str(round(pc_unit.meter_to_inch(self.closet.obj_x.location.x),3)) + '"')
        elif self.anchor_type == 'FILL':
            row = layout.row()
            row.label(text="Offsets:")
            row.prop(self,'fill_left_offset',text="Left")
            row.prop(self,'fill_right_offset',text="Right")
            row = layout.row()
            row.label(text="Closet Width")
            row.label(text=str(round(pc_unit.meter_to_inch(self.closet.obj_x.location.x),3)) + '"')
        else:
            row = layout.row()
            row.label(text="Closet Width:")
            row.prop(self,'change_width',text="")

    def execute(self,context):
        return {'FINISHED'}    


class hb_sample_cabinets_OT_change_closet_openings(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.change_closet_openings"
    bl_label = "Change Closet Openings"

    change_type: bpy.props.EnumProperty(name="Change Type",
                                        items=[('SET_QUANTITY',"Set Quantity","Set Quantity"),
                                               ('ADD_REMOVE_LAST',"Add/Remove Last Opening","Add/Remove Last Opening")])

    quantity: bpy.props.IntProperty(name="Quantity",min=1,max=8)

    closet = None
    new_closet = None
    calculators = []

    def check(self, context):
        obj = context.object
        closet_bp = pc_utils.get_bp_by_tag(obj,const.CLOSET_TAG)
        self.closet = types_closet_starters.Closet_Starter(closet_bp) 
        return True

    def invoke(self,context,event):
        self.calculators = []
        obj = context.object
        closet_bp = pc_utils.get_bp_by_tag(obj,const.CLOSET_TAG)
        self.closet = types_closet_starters.Closet_Starter(closet_bp)     
        for i in range(1,9):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Width")
            if not opening_height_prompt:
                self.quantity = i - 1
                break
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self,'change_type',expand=True)
        if self.change_type == 'ADD_REMOVE_LAST':
            row = layout.row()
            row.operator('hb_sample_cabinets.delete_closet_opening',text="Delete Last Opening",icon='X')
            row.operator('hb_sample_cabinets.add_closet_opening',text="Add Opening",icon='ADD')            
        else:
            row = layout.row()
            row.label(text="Opening Quantity:")
            row.prop(self,'quantity',text="")

    def delete_reference_object(self,obj_bp):
        for obj in obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def set_child_properties(self,obj):
        pc_utils.update_id_props(obj,self.new_closet.obj_bp)
        for child in obj.children:
            self.set_child_properties(child)

    def execute(self, context):
        if self.change_type == 'SET_QUANTITY' and self.closet.obj_bp:
            # lfe = self.closet.get_prompt("Left Finished End").get_value()
            # rfe = self.closet.get_prompt("Right Finished End").get_value()
            # turn_off_left = self.closet.get_prompt("Turn Off Left Panel").get_value()
            # turn_off_right = self.closet.get_prompt("Turn Off Right Panel").get_value()
            # extend_panels = self.closet.get_prompt("Extend Panels to Countertop").get_value()
            # extend_panel_amount = self.closet.get_prompt("Extend Panel Amount").get_value()
                
            parent = self.closet.obj_bp.parent
            x_loc = self.closet.obj_bp.location.x
            y_loc = self.closet.obj_bp.location.y
            z_loc = self.closet.obj_bp.location.z
            z_rot = self.closet.obj_bp.rotation_euler.z
            length = self.closet.obj_x.location.x
            pc_utils.delete_object_and_children(self.closet.obj_bp)

            self.new_closet = types_closet_starters.Closet_Starter()
            self.new_closet.opening_qty = self.quantity
            self.new_closet.is_base = self.closet.is_base
            self.new_closet.is_hanging = self.closet.is_hanging
            # self.new_closet.is_island = self.closet.is_island
            # self.new_closet.is_double_island = self.closet.is_double_island
            self.new_closet.pre_draw()
            self.new_closet.draw()
            self.new_closet.obj_bp.parent = parent
            self.new_closet.obj_bp.location.x = x_loc
            self.new_closet.obj_bp.location.y = y_loc
            self.new_closet.obj_bp.location.z = z_loc
            self.new_closet.obj_bp.rotation_euler.z = z_rot
            self.new_closet.obj_x.location.x = length
            self.delete_reference_object(self.new_closet.obj_bp)

            self.new_closet.obj_bp.hide_viewport = True
            self.new_closet.obj_x.hide_viewport = True
            self.new_closet.obj_y.hide_viewport = True
            self.new_closet.obj_z.hide_viewport = True
            self.set_child_properties(self.new_closet.obj_bp)

            self.new_closet.obj_bp.hide_viewport = False
            context.view_layer.objects.active = self.new_closet.obj_bp
            self.new_closet.obj_bp.select_set(True)
            # self.new_closet.get_prompt("Left Finished End").set_value(lfe)
            # self.new_closet.get_prompt("Right Finished End").set_value(rfe)
            # self.new_closet.get_prompt("Turn Off Left Panel").set_value(turn_off_left)
            # self.new_closet.get_prompt("Turn Off Right Panel").set_value(turn_off_right)
            # self.new_closet.get_prompt("Extend Panels to Countertop").set_value(extend_panels)
            # self.new_closet.get_prompt("Extend Panel Amount").set_value(extend_panel_amount)

            self.get_calculators(self.new_closet.obj_bp)
            for calculator in self.calculators:
                calculator.calculate()            
        return {'FINISHED'}


class hb_sample_cabinets_OT_add_closet_opening(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.add_closet_opening"
    bl_label = "Add Closet Opening"

    closet = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        if bp:
            closet = types_closet_starters.Closet_Starter(bp)
            if closet.opening_qty == 1:
                return False
            elif closet.opening_qty == 8:
                return False
            else:
                if closet.obj_prompts:
                    return True
                else:
                    return False
        else:
            return False

    def get_number_of_openings(self):
        for i in range(1,10):
            width = self.closet.get_prompt('Opening ' + str(i) + ' Width')
            if not width:
                return i - 1

    def get_closet_panels(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_PANEL_BP' in child:
                panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def get_closet_partitions(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_CLOSET_PARTITION_BP' in child:
                panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def get_last_opening_defaults(self):  
        opening_qty = self.closet.opening_qty   
        width = self.closet.get_prompt("Opening " + str(opening_qty) + " Width").get_value()
        height = self.closet.get_prompt("Opening " + str(opening_qty) + " Height").get_value()
        depth = self.closet.get_prompt("Opening " + str(opening_qty) + " Depth").get_value()
        floor = self.closet.get_prompt("Opening " + str(opening_qty) + " Floor Mounted").get_value()
        remove_bottom = self.closet.get_prompt("Remove Bottom " + str(opening_qty)).get_value()
        return [width,height,depth,floor,remove_bottom]

    def add_opening(self,qty):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        defaults = self.get_last_opening_defaults()
        center_partitions = self.get_closet_partitions()
        panels = self.get_closet_panels()
        self.closet.opening_qty = qty+1
        self.closet.add_opening_prompts(qty+1)
        self.closet.add_prompt("Double Panel " + str(qty),'CHECKBOX',False) 
        new_panel = self.closet.add_panel(qty,pc_types.Assembly(center_partitions[-1]))
        self.closet.add_top_and_bottom_shelf(qty+1,new_panel,pc_types.Assembly(panels[-1]))
        self.closet.add_toe_kick(qty+1,new_panel,pc_types.Assembly(panels[-1]))
        self.closet.add_opening(qty+1,new_panel,pc_types.Assembly(panels[-1]))
        if props.show_closet_panel_drilling:
            self.closet.add_system_holes(qty+1,new_panel,pc_types.Assembly(panels[-1])) 
        self.closet.update_last_panel_formulas(pc_types.Assembly(panels[-1]))  
        width = self.closet.get_prompt("Opening " + str(qty+1) + " Width")
        height = self.closet.get_prompt("Opening " + str(qty+1) + " Height")
        depth = self.closet.get_prompt("Opening " + str(qty+1) + " Depth")
        floor = self.closet.get_prompt("Opening " + str(qty+1) + " Floor Mounted")
        remove_bottom = self.closet.get_prompt("Remove Bottom " + str(qty+1))
        width.set_value(defaults[0])
        height.set_value(defaults[1])
        depth.set_value(defaults[2])
        floor.set_value(defaults[3])
        remove_bottom.set_value(defaults[4])
        self.closet.update_calculator_formula()
        
    def execute(self, context):    
        self.get_assemblies(context)
        number_of_openings = self.get_number_of_openings()
        self.add_opening(number_of_openings)
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        self.closet = types_closet_starters.Closet_Starter(bp)


class hb_sample_cabinets_OT_delete_closet_opening(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.delete_closet_opening"
    bl_label = "Delete Closet Opening"

    closet = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        if bp:
            closet = types_closet_starters.Closet_Starter(bp)
            if closet.opening_qty == 1:
                return False
            else:            
                if closet.obj_prompts:
                    return True
                else:
                    return False
        else:
            return False

    def get_number_of_openings(self):
        if self.closet.obj_prompts:
            for i in range(1,10):
                width = self.closet.get_prompt('Opening ' + str(i) + ' Width')
                if not width:
                    return i - 1

    def get_closet_panels(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_PANEL_BP' in child:
                panel = pc_types.Assembly(child)
                hide = panel.get_prompt("Hide").get_value()
                if not hide:
                    panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def get_closet_partitions(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_CLOSET_PARTITION_BP' in child:
                panel = pc_types.Assembly(child)
                hide = panel.get_prompt("Hide").get_value()
                if not hide:                
                    panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def delete_opening(self,opening_number):
        calculator = self.closet.get_calculator("Opening Calculator")
        panels = self.get_closet_panels()
        center_panels = self.get_closet_partitions()
        for child in self.closet.obj_bp.children:
            props = utils_cabinet.get_object_props(child)
            if props.opening_number == opening_number:
                pc_utils.delete_object_and_children(child)
        pc_utils.delete_object_and_children(center_panels[-1])
        self.closet.update_last_panel_formulas(pc_types.Assembly(panels[-1])) 
        calculator.prompts.remove(opening_number-1)
        self.closet.obj_prompts.pyclone.delete_prompt("Opening " + str(opening_number) + " Height")
        self.closet.obj_prompts.pyclone.delete_prompt("Opening " + str(opening_number) + " Depth")
        self.closet.obj_prompts.pyclone.delete_prompt("Opening " + str(opening_number) + " Floor Mounted")
        self.closet.obj_prompts.pyclone.delete_prompt("Remove Bottom " + str(opening_number))
        self.closet.obj_prompts.pyclone.delete_prompt("Double Panel " + str(opening_number-1))
        self.closet.update_calculator_formula()

    def execute(self, context):    
        self.get_assemblies(context)
        number_of_openings = self.get_number_of_openings()
        self.closet.opening_qty = number_of_openings - 1
        self.delete_opening(number_of_openings)
        self.closet.obj_bp.hide_viewport = True
        self.closet.obj_bp.select_set(True)
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        self.closet = types_closet_starters.Closet_Starter(bp)


class hb_sample_cabinets_OT_duplicate_closet_insert(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.duplicate_closet_insert"
    bl_label = "Duplicate Closet Insert"

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    @classmethod
    def poll(cls, context):
        obj_bp = pc_utils.get_bp_by_tag(context.object,const.INSERT_TAG)
        if obj_bp:
            return True
        else:
            return False

    def select_obj_and_children(self,obj):
        obj.hide_viewport = False
        obj.select_set(True)
        for child in obj.children:
            obj.hide_viewport = False
            child.select_set(True)
            self.select_obj_and_children(child)

    def delete_drivers(self,obj):
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                obj.driver_remove(driver.data_path)

    def execute(self, context):
        obj_bp = pc_utils.get_bp_by_tag(context.object,const.INSERT_TAG)
        cabinet = pc_types.Assembly(obj_bp)
        bpy.ops.object.select_all(action='DESELECT')
        self.select_obj_and_children(cabinet.obj_bp)
        bpy.ops.object.duplicate_move()
        pc_utils.hide_empties(cabinet.obj_bp)

        new_obj_bp = pc_utils.get_bp_by_tag(context.object,const.INSERT_TAG)
        new_cabinet = pc_types.Assembly(new_obj_bp)
        new_cabinet.obj_bp.parent = None
        self.delete_drivers(new_cabinet.obj_bp)
        self.delete_drivers(new_cabinet.obj_x)
        self.delete_drivers(new_cabinet.obj_y)
        self.delete_drivers(new_cabinet.obj_z)

        pc_utils.hide_empties(new_cabinet.obj_bp)

        bpy.ops.hb_sample_cabinets.place_closet_insert(obj_bp_name=new_cabinet.obj_bp.name)

        return {'FINISHED'}


class hb_sample_cabinets_OT_delete_closet_insert(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.delete_closet_insert"
    bl_label = "Delete Closet insert"

    insert = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bp = pc_utils.get_bp_by_tag(context.object,const.INSERT_TAG)
        if bp:
            return True
        else:
            return False

    def execute(self, context):    
        self.get_assemblies(context)
        opening_bp = self.insert.obj_bp.parent
        pc_utils.delete_object_and_children(self.insert.obj_bp) 
        if opening_bp:
            del(opening_bp["IS_FILLED"])
            for child in opening_bp.children:
                if 'IS_OPENING_MESH' in child:
                    child.hide_viewport = False
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.INSERT_TAG)
        self.insert = pc_types.Assembly(bp)


class hb_sample_cabinets_OT_place_wall_cabinet(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.place_wall_cabinet"
    bl_label = "Place Wall Cabinet"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")
    
    allow_fills: bpy.props.BoolProperty(name="Allow Fills",default=True)
    allow_quantities: bpy.props.BoolProperty(name="Allow Quantities",default=True)

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    position: bpy.props.EnumProperty(name="Position",
                                     items=[('SELECTED_POINT',"Selected Point","Turn off automatic positioning"),
                                            ('FILL',"Fill","Fill"),
                                            ('FILL_LEFT',"Fill Left","Fill Left"),
                                            ('LEFT',"Left","Bump Left"),
                                            ('CENTER',"Center","Center"),
                                            ('RIGHT',"Right","Bump Right"),
                                            ('FILL_RIGHT',"Fill Right","Fill Right")],
                                     default='SELECTED_POINT')

    quantity: bpy.props.IntProperty(name="Quantity",default=1)
    left_offset: bpy.props.FloatProperty(name="Left Offset", default=0,subtype='DISTANCE')
    right_offset: bpy.props.FloatProperty(name="Right Offset", default=0,subtype='DISTANCE')

    default_width = 0
    selected_location = 0

    cabinet = None
    qty_cage = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        obj_bp = pc_utils.get_bp_by_tag(context.object,const.WALL_TAG)
        if obj_bp:
            return True
        else:
            return False

    def reset_variables(self):
        self.quantity = 1
        self.cabinet = None
        self.position = 'SELECTED_POINT'
        self.qty_cage = None

    def set_product_defaults(self):
        self.cabinet.obj_bp.location.x = self.selected_location + self.left_offset
        self.cabinet.obj_x.location.x = self.default_width - (self.left_offset + self.right_offset)

    def select_obj_and_children(self,obj):
        obj.hide_viewport = False
        obj.select_set(True)
        for child in obj.children:
            obj.hide_viewport = False
            child.select_set(True)
            self.select_obj_and_children(child)

    def hide_empties_and_boolean_meshes(self,obj):
        if obj.type == 'EMPTY' or obj.hide_render:
            obj.hide_viewport = True
        for child in obj.children:
            self.hide_empties_and_boolean_meshes(child)
    
    def copy_cabinet(self,context,cabinet):
        bpy.ops.object.select_all(action='DESELECT')
        self.select_obj_and_children(cabinet.obj_bp)
        bpy.ops.object.duplicate_move()
        obj = context.active_object
        cabinet_bp = pc_utils.get_bp_by_tag(obj,const.CABINET_TAG)
        return pc_types.Assembly(cabinet_bp)

    def check(self, context):
        # wall_bp = home_builder_utils.get_wall_bp(self.cabinet.obj_bp)
        # if wall_bp:
        left_x = utils_placement.get_left_collision_location(self.cabinet)
        right_x = utils_placement.get_right_collision_location(self.cabinet)
        offsets = self.left_offset + self.right_offset
        self.set_product_defaults()
        if self.position == 'FILL':
            self.cabinet.obj_bp.location.x = left_x + self.left_offset
            self.cabinet.obj_x.location.x = (right_x - left_x - offsets) / self.quantity
        if self.position == 'FILL_LEFT':
            self.cabinet.obj_bp.location.x = left_x + self.left_offset
            self.cabinet.obj_x.location.x = (self.default_width + (self.selected_location - left_x) - offsets) / self.quantity
        if self.position == 'LEFT':
            # if self.cabinet.obj_bp.mv.placement_type == 'Corner':
            #     self.cabinet.obj_bp.rotation_euler.z = math.radians(0)
            self.cabinet.obj_bp.location.x = left_x + self.left_offset
            self.cabinet.obj_x.location.x = self.width
        if self.position == 'CENTER':
            self.cabinet.obj_x.location.x = self.width
            self.cabinet.obj_bp.location.x = left_x + (right_x - left_x)/2 - ((self.cabinet.obj_x.location.x/2) * self.quantity)
        if self.position == 'RIGHT':
            # if self.cabinet.obj_bp.mv.placement_type == 'Corner':
            #     self.cabinet.obj_bp.rotation_euler.z = math.radians(-90)
            self.cabinet.obj_x.location.x = self.width
            self.cabinet.obj_bp.location.x = (right_x - self.cabinet.obj_x.location.x) - self.right_offset
        if self.position == 'FILL_RIGHT':
            self.cabinet.obj_bp.location.x = self.selected_location + self.left_offset
            self.cabinet.obj_x.location.x = ((right_x - self.selected_location) - offsets) / self.quantity
        self.update_quantity()
        return True

    def create_qty_cage(self):
        width = self.cabinet.obj_x.pyclone.get_var('location.x','width')
        height = self.cabinet.obj_z.pyclone.get_var('location.z','height')
        depth = self.cabinet.obj_y.pyclone.get_var('location.y','depth')

        self.qty_cage = assemblies_cabinet.add_cage(self.cabinet)
        self.qty_cage.obj_bp["IS_REFERENCE"] = True
        self.qty_cage.loc_x(value = 0)
        self.qty_cage.loc_y(value = 0)
        self.qty_cage.loc_z(value = 0)
        self.qty_cage.rot_x(value = 0)
        self.qty_cage.rot_y(value = 0)
        self.qty_cage.rot_z(value = 0)      
        self.qty_cage.dim_x('width',[width])
        self.qty_cage.dim_y('depth',[depth])
        self.qty_cage.dim_z('height',[height])   
    
    def update_quantity(self):
        qty = self.qty_cage.get_prompt("Quantity")
        a_left = self.qty_cage.get_prompt("Array Left")
        qty.set_value(self.quantity)
        if self.position == 'RIGHT':
            a_left.set_value(True)
        else:
            a_left.set_value(False)

    def execute(self, context):        
        new_products = []  
        previous_product = None
        width = self.cabinet.obj_x.location.x 
        pc_utils.delete_object_and_children(self.qty_cage.obj_bp)  
        if self.quantity > 1:
            for i in range(self.quantity - 1):
                if previous_product:
                    new_product = self.copy_cabinet(context,previous_product)
                else:
                    new_product = self.copy_cabinet(context,self.cabinet)
                if self.position == 'RIGHT':
                    new_product.obj_bp.location.x -= width
                else:
                    new_product.obj_bp.location.x += width
                new_products.append(new_product)
                previous_product = new_product

        for new_p in new_products:
            self.hide_empties_and_boolean_meshes(new_p.obj_bp)
            new_p.obj_x.hide_viewport = False
            new_p.obj_y.hide_viewport = False
            new_p.obj_z.hide_viewport = False
            new_p.obj_x.empty_display_size = .001
            new_p.obj_y.empty_display_size = .001
            new_p.obj_z.empty_display_size = .001                
            # home_builder_utils.show_assembly_xyz(new_p)

        self.hide_empties_and_boolean_meshes(self.cabinet.obj_bp)
        self.cabinet.obj_x.hide_viewport = False
        self.cabinet.obj_y.hide_viewport = False
        self.cabinet.obj_z.hide_viewport = False
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001            
        # home_builder_utils.show_assembly_xyz(self.cabinet)

        return {'FINISHED'}

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def invoke(self,context,event):
        self.reset_variables()
        self.get_assemblies(context)
        self.create_qty_cage()
        self.cabinet_name = self.cabinet.obj_bp.name
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
        self.selected_location = self.cabinet.obj_bp.location.x
        self.default_width = self.cabinet.obj_x.location.x
        bpy.ops.object.select_all(action='DESELECT')
        for child in self.qty_cage.obj_bp.children:
            if child.type == 'MESH':
                child.select_set(True)          
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CABINET_TAG)
        self.cabinet = types_cabinet.Cabinet(bp)

    def draw(self, context):
        layout = self.layout

        #IF CORNER ALLOW FILLS FALSE
        if self.cabinet.obj_x.lock_location[0]:
            self.allow_fills = False

        box = layout.box()
        row = box.row(align=True)
        row.label(text="Position Options:",icon='EMPTY_ARROWS')
        row = box.row(align=False)
        row.prop_enum(self,'position', 'SELECTED_POINT',icon='RESTRICT_SELECT_OFF',text="Selected Point")
        if self.allow_fills:
            row.prop_enum(self,'position', 'FILL',icon='ARROW_LEFTRIGHT',text="Fill")
        row = box.row(align=True)
        if self.allow_fills:
            row.prop_enum(self, "position", 'FILL_LEFT', icon='REW', text="Fill Left") 
        row.prop_enum(self, "position", 'LEFT', icon='TRIA_LEFT', text="Left") 
        row.prop_enum(self, "position", 'CENTER', icon='TRIA_DOWN', text="Center")
        row.prop_enum(self, "position", 'RIGHT', icon='TRIA_RIGHT', text="Right") 
        if self.allow_fills:  
            row.prop_enum(self, "position", 'FILL_RIGHT', icon='FF', text="Fill Right")
        if self.allow_quantities:
            row = box.row(align=True)
            row.prop(self,'quantity')
        split = box.split(factor=0.5)
        col = split.column(align=True)
        col.label(text="Dimensions:")
        if self.position in {'SELECTED_POINT','LEFT','RIGHT','CENTER'}:
            col.prop(self,"width",text="Width")
        else:
            col.label(text='Width: ' + str(round(pc_unit.meter_to_active_unit(self.cabinet.obj_x.location.x),4)))
        col.prop(self.cabinet.obj_y,"location",index=1,text="Depth")
        col.prop(self.cabinet.obj_z,"location",index=2,text="Height")

        col = split.column(align=True)
        col.label(text="Offset:")
        col.prop(self,"left_offset",text="Left")
        col.prop(self,"right_offset",text="Right")
        col.prop(self.cabinet.obj_bp,"location",index=2,text="Height From Floor")


class hb_sample_cabinets_OT_update_all_pulls_in_room(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.update_all_pulls_in_room"
    bl_label = "Update All Pulls in Room"

    def execute(self, context):
        pull_objs = []
        for obj in context.visible_objects:
            if const.CABINET_HANDLE_TAG in obj:
                pull_objs.append(obj)

        for pull in pull_objs:
            insert_bp = pc_utils.get_bp_by_tag(pull,const.DOOR_INSERT_TAG)
            if not insert_bp:
                insert_bp = pc_utils.get_bp_by_tag(pull,const.DOOR_DRAWER_INSERT_TAG)
            if not insert_bp:
                insert_bp = pc_utils.get_bp_by_tag(pull,const.DRAWER_INSERT_TAG)
            
            if insert_bp:
                insert = types_fronts.Fronts(insert_bp)
                panel = pc_types.Assembly(pull.parent)
                if const.DOOR_FRONT_TAG in panel.obj_bp:
                    insert.add_door_pull(panel)
                if const.DRAWER_FRONT_TAG in panel.obj_bp:
                    insert.add_drawer_pull(panel)            

        pc_utils.delete_obj_list(pull_objs)
        return {'FINISHED'}


class hb_sample_cabinets_OT_update_selected_pulls_in_room(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.update_selected_pulls_in_room"
    bl_label = "Update Selected Pulls in Room"

    def execute(self, context):

        pull_objs = []
        for obj in context.selected_objects:
            if const.CABINET_HANDLE_TAG in obj:
                pull_objs.append(obj)

        for pull in pull_objs:
            door_bp = pc_utils.get_bp_by_tag(pull,const.DOOR_INSERT_TAG)
            if door_bp:
                door = types_fronts.Fronts(door_bp)
                door_panel = pc_types.Assembly(pull.parent)
                door.add_door_pull(door_panel)

            drawer_bp = pc_utils.get_bp_by_tag(pull,const.DRAWER_INSERT_TAG)
            if drawer_bp:
                drawer = types_fronts.Fronts(drawer_bp)
                panel = pc_types.Assembly(pull.parent)
                drawer.add_drawer_pull(panel)

        pc_utils.delete_obj_list(pull_objs)
        return {'FINISHED'}


class hb_sample_cabinets_OT_update_selected_pulls_in_room(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.update_selected_pulls_in_room"
    bl_label = "Update Selected Pulls in Room"

    def execute(self, context):

        pull_objs = []
        for obj in context.selected_objects:
            if const.CABINET_HANDLE_TAG in obj:
                pull_objs.append(obj)

        for pull in pull_objs:
            door_bp = pc_utils.get_bp_by_tag(pull,const.DOOR_INSERT_TAG)
            if door_bp:
                door = types_fronts.Fronts(door_bp)
                door_panel = pc_types.Assembly(pull.parent)
                door.add_door_pull(door_panel)

            drawer_bp = pc_utils.get_bp_by_tag(pull,const.DRAWER_INSERT_TAG)
            if drawer_bp:
                drawer = types_fronts.Fronts(drawer_bp)
                panel = pc_types.Assembly(pull.parent)
                drawer.add_drawer_pull(panel)

        pc_utils.delete_obj_list(pull_objs)
        return {'FINISHED'}


class hb_sample_cabinets_OT_update_all_fronts_in_room(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.update_all_fronts_in_room"
    bl_label = "Update All Fronts in Room"
    bl_description = "This will update all of the fronts in the scene"

    def execute(self, context):
        part_path = paths_cabinet.get_current_door_path()

        drawer_panel_bps = []
        door_panel_bps = []
        for obj in bpy.data.objects:

            if const.DOOR_FRONT_TAG in obj:
                if obj not in door_panel_bps:
                    door_panel_bps.append(obj)

            if const.DRAWER_FRONT_TAG in obj:
                if obj not in drawer_panel_bps:
                    drawer_panel_bps.append(obj)

        for door_panel_bp in door_panel_bps:
            old_door_panel = pc_types.Assembly(door_panel_bp)
            door_insert = types_fronts.Fronts(door_panel_bp.parent)
            new_front = pc_types.Assembly(door_insert.add_assembly_from_file(part_path))
            door_insert.replace_front(old_door_panel,new_front,True)

        for door_panel_bp in drawer_panel_bps:
            old_door_panel = pc_types.Assembly(door_panel_bp)
            door_insert = types_fronts.Fronts(door_panel_bp.parent)
            new_front = pc_types.Assembly(door_insert.add_assembly_from_file(part_path))
            door_insert.replace_front(old_door_panel,new_front,False)

        return {'FINISHED'}


class hb_sample_cabinets_OT_update_selected_fronts_in_room(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.update_selected_fronts_in_room"
    bl_label = "Update Selected Fronts in Room"
    bl_description = "This will update the selected fronts in the scene"

    def execute(self, context):
        part_path = paths_cabinet.get_current_door_path()

        drawer_panel_bps = []
        door_panel_bps = []
        for obj in context.selected_objects:
            door_bp = pc_utils.get_bp_by_tag(obj,const.DOOR_FRONT_TAG)
            if door_bp:
                if door_bp not in door_panel_bps:
                    door_panel_bps.append(door_bp)

            drawer_bp = pc_utils.get_bp_by_tag(obj,const.DRAWER_FRONT_TAG)
            if drawer_bp:
                if drawer_bp not in drawer_panel_bps:
                    drawer_panel_bps.append(drawer_bp)

        for door_panel_bp in door_panel_bps:
            old_door_panel = pc_types.Assembly(door_panel_bp)
            door_insert = types_fronts.Fronts(door_panel_bp.parent)
            new_front = pc_types.Assembly(door_insert.add_assembly_from_file(part_path))
            door_insert.replace_front(old_door_panel,new_front,True)

        for door_panel_bp in drawer_panel_bps:
            old_door_panel = pc_types.Assembly(door_panel_bp)
            door_insert = types_fronts.Fronts(door_panel_bp.parent)
            new_front = pc_types.Assembly(door_insert.add_assembly_from_file(part_path))
            door_insert.replace_front(old_door_panel,new_front,False)

        return {'FINISHED'}


class hb_sample_cabinets_OT_build_library(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.build_library"
    bl_label = "Build Library"

    library_categories: EnumProperty(name="Library Categories",
                          items=[('APPLIANCES',"Appliances","Appliances"),
                                 ('CABINETS',"Cabinets","Cabinets"),
                                 ('CABINETS_STARTERS',"Cabinet Starters","Cabinet Starters"),
                                 ('CABINET_INSERTS',"Cabinet Inserts","Cabinet Inserts"),
                                 ('CABINET_PARTS',"Cabinet Parts","Cabinet Parts"),
                                 ('CLOSET_STARTERS',"Closet Starters","Closet Starters"),
                                 ('CLOSET_INSERTS',"Closet Inserts","Closet Inserts"),
                                 ('CLOSET_PARTS',"Closet Parts","Closet Parts")],
                          default='CABINETS')

    only_display_missing: BoolProperty(name="Only Display Missing",default=True)

    library_items: CollectionProperty(name="Library Items",type=Cabinet_Library_Item)

    def check(self, context):
        return True

    def get_library_items(self):
        for mod_name, mod in inspect.getmembers(library_cabinet):
            if "__" not in mod_name:
                item = self.library_items.add()
                item.name = mod_name.replace("_"," ")
                item.library_type = 'CABINETS'

    def invoke(self,context,event):
        for item in self.library_items:
            self.library_items.remove(0)
        self.get_library_items()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def create_asset_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("bpy.ops.mesh.primitive_cube_add()\n")
        file.write("obj = bpy.context.view_layer.objects.active\n")
        file.write("obj.name = 'TEST ASSET'\n")
        file.write("obj.asset_mark()\n")
        file.write("obj.asset_generate_preview()\n")
        file.write("bpy.ops.wm.save_mainfile()\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def execute(self, context):
        scene_props = context.scene.home_builder
        workspace = context.workspace
        wm = context.window_manager        
        library_folder = os.path.join(os.path.dirname(__file__),'library','Sample Cabinets')
        library_blend = os.path.join(library_folder,'library.blend')
        for item in self.library_items:
            if item.is_checked:
                script = self.create_asset_script(item)
                command = [bpy.app.binary_path,library_blend,"-b","--python",script]
                subprocess.call(command)

        time.sleep(3)
        prefs = context.preferences
        asset_lib = prefs.filepaths.asset_libraries.get('home_builder_library')  
        asset_lib.path = library_folder            
        scene_props.library_tabs = scene_props.library_tabs
        bpy.ops.asset.library_refresh()
        for asset in wm.home_builder.home_builder_library_assets:
            print('ASSET',asset.file_data.name)                 
                # item_class = eval('cabinet_library.' + item.name.replace(" ","_") + '()')
        #         item_class.draw()
                # for mod_name, mod in inspect.getmembers(cabinet_library):
                    
                #     if "__" not in mod_name:                
                #     print(item.name)
                # pass #GET CLASS, CALL DRAW and RENDER
    
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.scale_y = 1.3
        row.prop(self,'library_categories',text="")
        row = box.row()
        row.prop(self,'only_display_missing')
        box = col.box()
        for item in self.library_items:
            if item.library_type == self.library_categories:
                box.prop(item,'is_checked',text=item.name)


classes = (
    Cabinet_Library_Item,
    hb_sample_cabinets_OT_active_cabinet_library,
    hb_sample_cabinets_OT_assign_handle_pointer,
    hb_sample_cabinets_OT_assign_door_pointer,
    hb_sample_cabinets_OT_assign_molding_pointer,
    hb_sample_cabinets_OT_change_closet_offsets,
    hb_sample_cabinets_OT_change_closet_openings,
    hb_sample_cabinets_OT_add_closet_opening,
    hb_sample_cabinets_OT_delete_closet_opening,
    hb_sample_cabinets_OT_duplicate_closet_insert,
    hb_sample_cabinets_OT_delete_closet_insert,
    hb_sample_cabinets_OT_place_wall_cabinet,
    hb_sample_cabinets_OT_update_all_pulls_in_room,
    hb_sample_cabinets_OT_update_selected_pulls_in_room,
    hb_sample_cabinets_OT_update_all_fronts_in_room,
    hb_sample_cabinets_OT_update_selected_fronts_in_room,
    hb_sample_cabinets_OT_build_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    