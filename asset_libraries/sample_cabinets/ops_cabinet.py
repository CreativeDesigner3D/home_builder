import bpy
import os
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
from . import const_cabinets as const

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
    hb_sample_cabinets_OT_build_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    