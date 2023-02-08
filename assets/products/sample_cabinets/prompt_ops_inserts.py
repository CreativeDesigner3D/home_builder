import bpy
import math
from pc_lib import pc_utils, pc_types, pc_unit
from . import material_pointers_cabinet
from . import types_cabinet
from . import types_appliances
from . import types_cabinet_starters
from . import const_cabinets as const
from . import enum_cabinets
from . import utils_cabinet


class hb_sample_cabinets_OT_door_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.door_prompts"
    bl_label = "Door Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Door"),
                                              ('TOP',"Top","Top Swing Door"),
                                              ('BOTTOM',"Bottom","Bottom Swing Door")])

    insert = None
    calculators = []

    def check(self, context):
        door_swing = self.insert.get_prompt("Door Swing")
        if self.door_swing == 'LEFT':
            door_swing.set_value(0)
        if self.door_swing == 'RIGHT':
            door_swing.set_value(1)
        if self.door_swing == 'DOUBLE':
            door_swing.set_value(2)         
        if self.door_swing == 'TOP':
            door_swing.set_value(3)     
        if self.door_swing == 'BOTTOM':
            door_swing.set_value(4)                             
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        door_swing = self.insert.get_prompt("Door Swing")
        if door_swing.get_value() == 0:
            self.door_swing = 'LEFT'
        if door_swing.get_value() == 1:
            self.door_swing = 'RIGHT'
        if door_swing.get_value() == 2:
            self.door_swing = 'DOUBLE' 
        if door_swing.get_value() == 3:
            self.door_swing = 'TOP' 
        if door_swing.get_value() == 4:
            self.door_swing = 'BOTTOM' 

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.DOOR_INSERT_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
              
        layout = self.layout
        inset = self.insert.get_prompt("Inset Front")
        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        open_door = self.insert.get_prompt("Open Door")  
        turn_off_pulls = self.insert.get_prompt("Turn Off Pulls") 
        door_type = self.insert.get_prompt("Door Type")
        s_qty = self.insert.get_prompt("Shelf Quantity")

        box = layout.box()
        row = box.row()
        row.label(text="Swing")      
        row.prop(self,'door_swing',expand=True) 

        row = box.row()
        row.label(text="Open Door")      
        row.prop(open_door,'percentage_value',text="")  

        box = layout.box()
        box.label(text="Overlays")
        row = box.row()
        row.prop(inset,'checkbox_value',text="Inset Front")         
        row = box.row()
        row.label(text="Half")
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 

        box = layout.box()
        box.label(text="Pulls")
        row = box.row()
        row.label(text="Turn Off Pulls")      
        row.prop(turn_off_pulls,'checkbox_value',text="")    
        h_loc = self.insert.get_prompt("Pull Horizontal Location") 
        if door_type.get_value() == "Base":
            vert_loc = self.insert.get_prompt("Base Pull Vertical Location")      
        if door_type.get_value() == "Tall":
            vert_loc = self.insert.get_prompt("Tall Pull Vertical Location")                    
        if door_type.get_value() == "Upper":
            vert_loc = self.insert.get_prompt("Upper Pull Vertical Location") 

        if self.door_swing not in {'TOP','BOTTOM'}:        
            row = box.row()
            row.label(text="Pull Vertical Location")               
            row.prop(vert_loc,'distance_value',text="")  

        row = box.row()
        row.label(text="Pull Dim from Edge")               
        row.prop(h_loc,'distance_value',text="")  

        if s_qty:
            box = layout.box()
            row = box.row()
            row.label(text="Shelf Quantity")      
            row.prop(s_qty,'quantity_value',text="")    


class hb_sample_cabinets_OT_drawer_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.drawer_prompts"
    bl_label = "Drawer Prompts"

    drawer_qty: bpy.props.EnumProperty(name="Drawer Quantity",
                          items=[('1',"1","1 Drawer"),
                                 ('2',"2","2 Drawer"),
                                 ('3',"3","3 Drawer"),
                                 ('4',"4","4 Drawer"),
                                 ('5',"5","5 Drawer"),
                                 ('6',"6","6 Drawer"),
                                 ('7',"7","7 Drawer"),
                                 ('8',"8","8 Drawer")],
                          default='3')

    insert = None
    calculators = []

    def check(self, context):
        drawer_qty = int(self.drawer_qty)
        calculator = self.insert.get_calculator("Front Height Calculator")
        for i in range(1,9):
            dfh = calculator.get_calculator_prompt("Drawer Front " + str(i) + " Height")
            if i <= drawer_qty:
                dfh.include = True
            else:
                dfh.include = False
        drawer_qty_prompt = self.insert.get_prompt("Drawer Quantity")
        drawer_qty_prompt.set_value(drawer_qty)
        calculator.calculate()
        return True

    def execute(self, context):               
        return {'FINISHED'}

    def set_default_front_size(self):
        drawer_qty = self.insert.get_prompt("Drawer Quantity")
        self.drawer_qty = str(drawer_qty.get_value())

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_default_front_size()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.DRAWER_INSERT_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        open_drawer = self.insert.get_prompt("Open Drawer")
        drawer_qty = self.insert.get_prompt("Drawer Quantity")
        turn_off_pulls = self.insert.get_prompt("Turn Off Pulls")
        center_pull = self.insert.get_prompt("Center Pull On Front")
        pull_vert_loc = self.insert.get_prompt("Drawer Pull Vertical Location")
        inset = self.insert.get_prompt("Inset Front")
        
        row = box.row()
        row.label(text="Qty")            
        row.prop(self,'drawer_qty',expand=True)        
        row = box.row()

        if drawer_qty:
            for i in range(1,9):
                if drawer_qty.get_value() > i - 1:

                    drawer_height = self.insert.get_prompt("Drawer Front " + str(i) + " Height")
                    row = box.row()
                    row.label(text="Drawer Front " + str(i) + " Height")   
                    row.prop(drawer_height,'equal',text="")                     
                    if drawer_height.equal:
                        row.label(text=str(round(pc_unit.meter_to_inch(drawer_height.distance_value),3)) + '"')
                    else:
                        row.prop(drawer_height,'distance_value',text="")                  

            row = box.row()
            row.label(text="Open Drawer")
            row.prop(open_drawer,'percentage_value',text="")

        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        
        box = layout.box()
        box.label(text="Overlays")
        row = box.row()
        row.prop(inset,'checkbox_value',text="Inset Front")         
        row = box.row()
        row.label(text="Half")
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 

        box = layout.box()
        row = box.row()
        row.label(text="Turn Off Handles")
        row.prop(turn_off_pulls,'checkbox_value',text="")
        row = box.row()
        row.label(text="Center Handles on Fronts")
        row.prop(center_pull,'checkbox_value',text="")
        if center_pull.get_value() == False:
            row = box.row()
            row.label(text="Handle Vertical Location")
            row.prop(pull_vert_loc,'distance_value',text="")


class hb_sample_cabinets_OT_adj_shelves_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.adj_shelves_prompts"
    bl_label = "Adjustable Shelves Prompts"

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
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_SHELVES_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        shelf_qty = self.insert.get_prompt("Shelf Quantity")
        layout.prop(shelf_qty,'quantity_value',text="Shelf Quantity")
        row = layout.row()
        props = row.operator('hb_sample_cabinets.show_hide_opening',text="Show Opening")
        props.insert_obj_bp = self.insert.obj_bp.name
        props.hide = False
        props = row.operator('hb_sample_cabinets.show_hide_opening',text="Hide Opening")
        props.insert_obj_bp = self.insert.obj_bp.name
        props.hide = True


class hb_sample_cabinets_OT_hanging_rod_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.hanging_rod_prompts"
    bl_label = "Hanging Rod Prompts"

    top_opening_height: bpy.props.EnumProperty(name="Top Opening Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    insert = None

    def check(self, context):
        self.insert.obj_prompts.hide_viewport = False
        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            top_opening_height = self.insert.get_prompt("Top Opening Height")
            if top_opening_height:
                top_opening_height.distance_value = pc_unit.inch(float(self.top_opening_height) / 25.4)
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            top_opening_height = self.insert.get_prompt("Top Opening Height")
            if top_opening_height:
                value = round(top_opening_height.distance_value * 1000,2)
                for index, height in enumerate(const.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.top_opening_height = const.OPENING_HEIGHTS[index - 1][0]
                        break

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=230)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_HANGING_ROD)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        layout = self.layout
        loc_from_top = self.insert.get_prompt("Hanging Rod Location From Top")
        top_opening_height = self.insert.get_prompt("Top Opening Height")
        setback = self.insert.get_prompt("Hanging Rod Setback")
        if top_opening_height:
            if hb_props.use_fixed_closet_heights:
                row = layout.row()
                row.label(text="Top Opening Height")
                row.prop(self,'top_opening_height',text="") 
            else:
                layout.prop(top_opening_height,'distance_value',text="Top Opening Height")        
        if loc_from_top:
            layout.prop(loc_from_top,'distance_value',text="Rod Location From Top")
        if setback:
            layout.prop(setback,'distance_value',text="Rod Setback")


class hb_sample_cabinets_OT_slanted_shoe_shelf_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.slanted_shoe_shelf_prompts"
    bl_label = "Slanted Shoe Shelf Prompts"

    insert = None
    calculators = []

    def get_shoe_shelf_fences(self):
        shoe_fences = []
        for child in self.insert.obj_bp.children:
            for nchild in child.children:
                if 'IS_METAL_SHOE_SHELF_FENCE_BP' in nchild:
                    part = pc_types.Assembly(nchild)
                    hide = part.get_prompt("Hide")
                    if hide and hide.get_value():
                        continue                
                    shoe_fences.append(part)
        return shoe_fences

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_SLANTED_SHOE_SHELVES)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        shelf_qty = self.insert.get_prompt("Shelf Quantity")
        space_from_bottom = self.insert.get_prompt("Space From Bottom")
        dim_between_shelves = self.insert.get_prompt("Distance Between Shelves")
        
        box = layout.box()

        row = box.row()
        row.label(text="Shelf Quantity")
        row.prop(shelf_qty,'quantity_value',text="")

        row = box.row()
        row.label(text="Space From Bottom")
        row.prop(space_from_bottom,'distance_value',text="")

        row = box.row()
        row.label(text="Distance Between Shelves")
        row.prop(dim_between_shelves,'distance_value',text="")


class hb_sample_cabinets_OT_cubby_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.cubby_prompts"
    bl_label = "Cubby Prompts"

    cubby_location: bpy.props.EnumProperty(name="Cubby Location",
                                           items=[('BOTTOM',"Bottom","Place on Bottom"),
                                                  ('TOP',"Top","Place on Top"),
                                                  ('FILL',"Fill","Fill Opening")])

    cubby_height: bpy.props.EnumProperty(name="Cubby Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')
    
    insert = None
    calculators = []

    def check(self, context):
        self.insert.obj_prompts.hide_viewport = False
        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            cubby_height = self.insert.get_prompt("Cubby Height")
            if cubby_height:
                cubby_height.distance_value = pc_unit.inch(float(self.cubby_height) / 25.4)  

        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if self.cubby_location == 'BOTTOM':
            cubby_placement.set_value(0)
        if self.cubby_location == 'TOP':
            cubby_placement.set_value(1)
        if self.cubby_location == 'FILL':
            cubby_placement.set_value(2)         
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            cubby_height = self.insert.get_prompt("Cubby Height")
            if cubby_height:
                value = round(cubby_height.distance_value * 1000,2)
                for index, height in enumerate(const.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.cubby_height = const.OPENING_HEIGHTS[index - 1][0]
                        break

        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if cubby_placement.get_value() == 0:
            self.cubby_location = 'BOTTOM'
        if cubby_placement.get_value() == 1:
            self.cubby_location = 'TOP'
        if cubby_placement.get_value() == 2:
            self.cubby_location = 'FILL'  

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_CUBBIES_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        h_qty = self.insert.get_prompt("Horizontal Quantity")
        v_qty = self.insert.get_prompt("Vertical Quantity")
        c_height = self.insert.get_prompt("Cubby Height")
        c_setback = self.insert.get_prompt("Cubby Setback")
        row = layout.row()
        row.label(text="Location")
        row.prop(self,'cubby_location',expand=True)
        if self.cubby_location != 'FILL':
            hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
            if hb_props.use_fixed_closet_heights:  
                row = layout.row()
                row.label(text="Cubby Height")        
                row.prop(self,'cubby_height',text="")
            else:
                row = layout.row()
                row.label(text="Cubby Height")        
                row.prop(c_height,'distance_value',text="")
        row = layout.row()
        row.label(text="Shelf Quantity")           
        row.prop(h_qty,'quantity_value',text="")
        row = layout.row()
        row.label(text="Division Quantity")           
        row.prop(v_qty,'quantity_value',text="")        
        row = layout.row()
        row.label(text="Cubby Setback")           
        row.prop(c_setback,'distance_value',text="")


class hb_sample_cabinets_OT_wire_baskets_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.wire_baskets_prompts"
    bl_label = "Wire Baskets Prompts"

    insert = None

    def check(self, context):     
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_WIRE_BASKETS_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        qty = self.insert.get_prompt("Wire Basket Quantity")
        spacing = self.insert.get_prompt("Vertical Spacing")

        box = layout.box()
        row = box.row()
        row.label(text="Wire Basket Quantity")
        row.prop(qty,'quantity_value',text="")

        for i in range(1,7):
            if qty.get_value() > i - 1:
                height = self.insert.get_prompt("Wire Basket " + str(i) + " Height")
                row = box.row()
                row.label(text="Height " + str(i))                
                row.prop(height,'distance_value',text="")

        box = layout.box()
        row = box.row()
        row.label(text="Vertical Spacing")
        row.prop(spacing,'distance_value',text="")


class hb_sample_cabinets_OT_wine_rack_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.wine_rack_prompts"
    bl_label = "Wine Rack Prompts"

    insert = None

    def check(self, context):     
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.WINE_RACK_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout

        rack_qty = self.insert.get_prompt("Wine Rack Quantity")
        space_from_bottom = self.insert.get_prompt("Space From Bottom")
        setback = self.insert.get_prompt("Wine Rack Setback")
        spacing = self.insert.get_prompt("Vertical Spacing")
        depth = self.insert.get_prompt("Wine Rack Depth")

        box = layout.box()
        row = box.row()
        row.label(text="Wine Rack Quantity")
        row.prop(rack_qty,'quantity_value',text="")

        box = layout.box()
        row = box.row()
        row.label(text="Space From Bottom")
        row.prop(space_from_bottom,'distance_value',text="")

        row = box.row()
        row.label(text="Vertical Spacing")
        row.prop(spacing,'distance_value',text="")

        row = box.row()
        row.label(text="Wine Rack Setback")
        row.prop(setback,'distance_value',text="")

        row = box.row()
        row.label(text="Wine Rack Depth")
        row.prop(depth,'distance_value',text="")                


class hb_sample_cabinets_OT_single_fixed_shelf_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_parts.single_fixed_shelf_prompts"
    bl_label = "Single Fixed Shelf Prompts"

    set_height_location: bpy.props.EnumProperty(name="Set Height Location",
                                           items=[('TOP',"Top","Set Top Height"),
                                                  ('Bottom',"Bottom","Set Bottom Height")])

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')
    
    opening_2_height: bpy.props.EnumProperty(name="Opening 2 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_3_height: bpy.props.EnumProperty(name="Opening 3 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_4_height: bpy.props.EnumProperty(name="Opening 4 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_5_height: bpy.props.EnumProperty(name="Opening 5 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    insert = None
    calculators = []

    def check(self, context): 
        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:        
            opening_top = self.insert.get_prompt("Opening 1 Height")
            opening_bottom = self.insert.get_prompt("Opening 2 Height")
            if self.set_height_location == 'TOP':
                opening_top.equal = False
                opening_bottom.equal = True
            else:
                opening_top.equal = True
                opening_bottom.equal = False  


                for i in range(1,6):
                    opening = self.insert.get_prompt("Opening " + str(i) + " Height")
                    if opening:
                        height = eval("float(self.opening_" + str(i) + "_height)/1000")
                        opening.set_value(height)        
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            for i in range(1,6):
                opening = self.insert.get_prompt("Opening " + str(i) + " Height")
                if opening:
                    value = round(opening.distance_value * 1000,2)
                    for index, height in enumerate(const.OPENING_HEIGHTS):
                        if not value >= float(height[0]):
                            exec("self.opening_" + str(i) + "_height = const.OPENING_HEIGHTS[index - 1][0]")
                            break

    def invoke(self,context,event):
        self.get_assemblies(context) 
        self.get_calculators(self.insert.obj_bp)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.VERTICAL_SPLITTER_TAG)
        self.insert = pc_types.Assembly(bp)

    def get_number_of_equal_openings(self,name="Height"):
        number_of_equal_openings = 0
        
        for i in range(1,9):
            size = self.insert.get_prompt("Opening " + str(i) + " " + name)
            if size:
                number_of_equal_openings += 1 if size.equal else 0
            else:
                break
            
        return number_of_equal_openings

    def draw_prompts(self,layout,name="Height"):
        unit_settings = bpy.context.scene.unit_settings
        for i in range(1,10):
            opening = self.insert.get_prompt("Opening " + str(i) + " " + name)
            if opening:
                row = layout.row()
                if opening.equal == False:
                    row.prop(opening,'equal',text="")
                else:
                    if self.get_number_of_equal_openings(name=name) != 1:
                        row.prop(opening,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')                
                row.label(text="Opening " + str(i) + " " + name + ":")
                if opening.equal:
                    value = pc_unit.unit_to_string(unit_settings,opening.distance_value)
                    row.label(text=value)
                else:
                    if name == 'Height':
                        row.prop(opening,'distance_value',text="")
                    else:
                        row.prop(opening,'distance_value',text="")            

    def draw(self, context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
        layout = self.layout
        if hb_props.use_fixed_closet_heights:          
            unit_settings = bpy.context.scene.unit_settings
            row = layout.row()
            row.prop(self,'set_height_location',expand=True)
            opening_top = self.insert.get_prompt("Opening 1 Height")
            opening_bottom = self.insert.get_prompt("Opening 2 Height")
            if self.set_height_location == 'TOP':
                row = layout.row()
                row.label(text="Top Opening Height:")
                row.prop(self,'opening_1_height',text="")
                row = layout.row()
                row.label(text="Bottom Opening Height:")
                row.label(text=pc_unit.unit_to_string(unit_settings,opening_bottom.distance_value))                  
            else:
                row = layout.row()
                row.label(text="Top Opening Height:")
                row.label(text=pc_unit.unit_to_string(unit_settings,opening_top.distance_value))     
                row = layout.row()
                row.label(text="Bottom Opening Height:")
                row.prop(self,'opening_2_height',text="")    
        else:
            self.draw_prompts(layout,name="Height")       


class hb_sample_cabinets_OT_division_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.division_prompts"
    bl_label = "Division Prompts"

    insert = None
    calculators = []

    def check(self, context):       
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context) 
        self.get_calculators(self.insert.obj_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.HORIZONTAL_SPLITTER_TAG)
        self.insert = pc_types.Assembly(bp)

    def get_number_of_equal_openings(self):
        number_of_equal_openings = 0
        
        for i in range(1,9):
            size = self.insert.get_prompt("Opening " + str(i) + " Width")
            if size:
                number_of_equal_openings += 1 if size.equal else 0
            else:
                break
            
        return number_of_equal_openings

    def draw(self, context):
        layout = self.layout
        unit_settings = bpy.context.scene.unit_settings
        for i in range(1,10):
            opening = self.insert.get_prompt("Opening " + str(i) + " Width")
            if opening:
                row = layout.row()
                if opening.equal == False:
                    row.prop(opening,'equal',text="")
                else:
                    if self.get_number_of_equal_openings() != 1:
                        row.prop(opening,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')                
                row.label(text="Opening " + str(i) + " Width:")
                if opening.equal:
                    value = pc_unit.unit_to_string(unit_settings,opening.distance_value)
                    row.label(text=value)
                else:
                    row.prop(opening,'distance_value',text="")


classes = (
    hb_sample_cabinets_OT_drawer_prompts,
    hb_sample_cabinets_OT_door_prompts,
    hb_sample_cabinets_OT_adj_shelves_prompts,
    hb_sample_cabinets_OT_hanging_rod_prompts,
    hb_sample_cabinets_OT_slanted_shoe_shelf_prompts,
    hb_sample_cabinets_OT_cubby_prompts,
    hb_sample_cabinets_OT_wire_baskets_prompts,
    hb_sample_cabinets_OT_wine_rack_prompts,
    hb_sample_cabinets_OT_single_fixed_shelf_prompts,
    hb_sample_cabinets_OT_division_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    