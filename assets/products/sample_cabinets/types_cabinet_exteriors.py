import bpy
import os
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import paths_cabinet
from . import const_cabinets as const
from . import prompts_cabinet
from . import utils_cabinet
from . import material_pointers_cabinet
from . import types_fronts

class Cabinet_Exterior(pc_types.Assembly):
    carcass_type = '' #Base, Tall, Upper
    overlay_prompts = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if "OVERLAY_PROMPTS" in child:
                    self.overlay_prompts = child

    def draw_prompts(self,layout,context):
        open_door = self.get_prompt("Open Door")
        drawer_qty = self.get_prompt("Drawer Quantity")
        front_height_calculator = self.get_calculator("Front Height Calculator")
        door_swing = self.get_prompt("Door Swing")
        turn_off_pulls = self.get_prompt("Turn Off Pulls")
        top_drawer_front_height = self.get_prompt("Top Drawer Front Height")
        carcass_type = self.get_prompt("Carcass Type")
        add_two_drawer_fronts = self.get_prompt("Add Two Drawer Fronts")
        center_pulls_on_front = self.get_prompt("Center Pull On Front")
        drawer_pull_vertical_location = self.get_prompt("Drawer Pull Vertical Location")
        inset = self.get_prompt("Inset Front")

        if open_door:
            open_door.draw(layout,allow_edit=False)

        if door_swing:
            door_swing.draw(layout,allow_edit=False)    

        if drawer_qty:
            drawer_qty.draw(layout,allow_edit=False)

        if inset:
            inset.draw(layout,allow_edit=False)

        if turn_off_pulls:
            row = layout.row()
            row.label(text="Pulls:")
            row.prop(turn_off_pulls,'checkbox_value',text="Off")

            pull_horizontal_location = self.get_prompt("Pull Horizontal Location")

            if carcass_type and carcass_type.get_value() == 'Base':
                base_pull_location = self.get_prompt("Base Pull Vertical Location")
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(base_pull_location,'distance_value',text="Z")
            if carcass_type and carcass_type.get_value() == 'Tall':
                tall_pull_location = self.get_prompt("Tall Pull Vertical Location")
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(tall_pull_location,'distance_value',text="Z")                
            if carcass_type and carcass_type.get_value() == 'Upper':
                upper_pull_location = self.get_prompt("Upper Pull Vertical Location")     
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(upper_pull_location,'distance_value',text="Z")                       
            if carcass_type and carcass_type.get_value() == 'Drawer':
                pass            

        if center_pulls_on_front:
            row = layout.row()
            row.prop(center_pulls_on_front,'checkbox_value',text="Center Drawer Pulls")

            if drawer_pull_vertical_location:
                if center_pulls_on_front.get_value() == False:
                    row.prop(drawer_pull_vertical_location,'distance_value',text="Pull Location")

        if add_two_drawer_fronts:
            row = layout.row()
            row.label(text="Add Two Drawer Fronts")
            row.prop(add_two_drawer_fronts,'checkbox_value',text="")

        if top_drawer_front_height:
            row = layout.row()
            row.label(text="Top Drawer Front Height")
            row.prop(top_drawer_front_height,'distance_value',text="")

        if front_height_calculator:
            for i in range(1,9):
                if drawer_qty.get_value() > i - 1:
                    drawer_height = self.get_prompt("Drawer Front " + str(i) + " Height")
                    if drawer_height:
                        row = layout.row()
                        row.label(text="Drawer Front " + str(i) + " Height")   
                        row.prop(drawer_height,'equal',text="")                     
                        if drawer_height.equal:
                            row.label(text=str(round(pc_unit.meter_to_inch(drawer_height.distance_value),3)) + '"')
                        else:
                            row.prop(drawer_height,'distance_value',text="")                       


class Doors(types_fronts.Fronts):

    door_swing = 0 # Left = 0, Right = 1, Double = 2, Top = 3, Bottom = 4
    door_type = "Base" # Base, Tall, Upper

    def draw(self):    
        self.create_assembly()
        self.set_name("Doors")
        self.add_prompts(include_door_prompts=True,include_drawer_prompts=False)
        # self.add_closet_insert_prompts()    
        self.obj_bp[const.DOOR_INSERT_TAG] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.door_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value(self.door_type)

        #LEFT DOOR
        l_door = assemblies_cabinet.add_door_assembly(self)
        self.add_door_panel(l_door,"Left",to_var,bo_var,ro_var,lo_var)
        
        #RIGHT DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        self.add_door_panel(r_door,"Right",to_var,bo_var,ro_var,lo_var)

        #TOP DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        self.add_door_panel(r_door,"Top",to_var,bo_var,ro_var,lo_var)

        #BOTTOM DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        self.add_door_panel(r_door,"Bottom",to_var,bo_var,ro_var,lo_var)         

    def update_prompts_after_placement(self,context):
        door_swing = self.get_prompt("Door Swing")
        width = self.obj_x.location.x
        if width > pc_unit.inch(20):
            door_swing.set_value(2)
        else:
            door_swing.set_value(0)

class Drawers(types_fronts.Fronts):

    drawer_qty = 3

    def add_drawer_front(self,index,prev_drawer_empty,calculator,to,bo,lo,ro):
        drawer_front_height = self.get_prompt("Drawer Front " + str(index) + " Height").get_var(calculator.name,'drawer_front_height')
        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')
        y = self.obj_y.pyclone.get_var('location.y','y')
        top_overlay = to.get_var('top_overlay')
        bottom_overlay = bo.get_var('bottom_overlay')
        left_overlay = lo.get_var('left_overlay')
        right_overlay = ro.get_var('right_overlay')
        open_drawer = self.get_prompt("Open Drawer").get_var('open_drawer')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        st = self.get_prompt("Material Thickness").get_var('st')
        dq = self.get_prompt("Drawer Quantity").get_var('dq')
        inset = self.get_prompt("Inset Front").get_var('inset')
        front_empty = self.add_empty('Front Z Location ' + str(index))
        front_empty.empty_display_size = .001
        
        if prev_drawer_empty:
            prev_drawer_z_loc = prev_drawer_empty.pyclone.get_var('location.z','prev_drawer_z_loc')
            front_empty.pyclone.loc_z('prev_drawer_z_loc-drawer_front_height-vertical_gap',[prev_drawer_z_loc,drawer_front_height,vertical_gap])
        else:
            front_empty.pyclone.loc_z('z-drawer_front_height+top_overlay',[z,drawer_front_height,top_overlay])        
        
        drawer_z_loc = front_empty.pyclone.get_var('location.z',"drawer_z_loc")

        drawer_front = assemblies_cabinet.add_door_assembly(self)
        drawer_front.add_prompt("Pull Length",'DISTANCE',0)      
        self.add_drawer_pull(drawer_front)
        drawer_front.add_prompt("Top Overlay",'DISTANCE',0)
        drawer_front.add_prompt("Bottom Overlay",'DISTANCE',0)
        drawer_front.add_prompt("Left Overlay",'DISTANCE',0)
        drawer_front.add_prompt("Right Overlay",'DISTANCE',0)    
        top_o = drawer_front.get_prompt("Top Overlay")
        bottom_o = drawer_front.get_prompt("Bottom Overlay")
        left_o = drawer_front.get_prompt("Left Overlay")
        right_o = drawer_front.get_prompt("Right Overlay")
        drawer_front.obj_bp[const.DRAWER_FRONT_TAG] = True
        drawer_front.obj_bp["FRONT_NUMBER"] = index  
        drawer_front.set_name('Drawer Front')
        drawer_front.loc_x('-left_overlay',[left_overlay])
        drawer_front.loc_y('IF(inset,front_thickness,-door_to_cabinet_gap)-(y*(open_drawer/100))',[inset,front_thickness,door_to_cabinet_gap,y,open_drawer])
        drawer_front.loc_z('drawer_z_loc',[drawer_z_loc])
        drawer_front.rot_x(value = math.radians(90))
        drawer_front.rot_y(value = math.radians(-90))
        drawer_front.dim_x('drawer_front_height',[drawer_front_height])
        drawer_front.dim_y('(x+left_overlay+right_overlay)*-1',[x,left_overlay,right_overlay])
        drawer_front.dim_z('front_thickness',[front_thickness])
        
        left_o.set_formula('left_overlay',[left_overlay])
        right_o.set_formula('right_overlay',[right_overlay])
        hide = drawer_front.get_prompt('Hide')
        hide.set_formula('IF(dq>' + str(index-1) + ',False,True)',[dq])        
        drawer_front.add_prompt("Drawer Override",'CHECKBOX',False)
        drawer_front.add_prompt("Drawer Type",'TEXT',"")
        drawer_front.add_prompt("Override Drawer Depth",'DISTANCE',0)   
        
        top_o.set_formula('top_overlay',[top_overlay])     
        bottom_o.set_formula('bottom_overlay',[bottom_overlay])      

        # stretcher = assemblies_cabinet.add_closet_part(self)
        # stretcher.set_name("Drawer Stretcher")
        # # props = utils_cabinet.get_object_props(stretcher.obj_bp)
        # # props.part_name = "Drawer Stretcher"  
        # # props.ebl1 = False
        # # props.ebl2 = True
        # # props.ebw1 = False
        # # props.ebw2 = False
        # stretcher.obj_bp['IS_DRAWER_STRETCHER_BP'] = True 
        # stretcher.loc_x(value = 0)
        # stretcher.loc_y(value = 0)
        # stretcher.loc_z('drawer_z_loc-vertical_gap-top_overlay',[drawer_z_loc,vertical_gap,top_overlay])
        # stretcher.rot_x(value = 0)
        # stretcher.rot_y(value = 0)
        # stretcher.rot_z(value = 0)
        # stretcher.dim_x('x',[x])
        # stretcher.dim_y(value = pc_unit.inch(6))
        # stretcher.dim_z('st',[st])
        # hide = stretcher.get_prompt('Hide')
        # hide.set_formula('IF(dq>' + str(index) + ',False,True)',[dq])

        return front_empty

    def draw(self):     
        self.create_assembly() 
        self.obj_bp[const.DRAWER_INSERT_TAG] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        self.obj_bp['PROMPT_ID'] = 'hb_sample_cabinets.drawer_prompts'
        # self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_closet_insert_commands"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        self.add_prompts(include_door_prompts=False,include_drawer_prompts=True)
        self.add_prompt("Drawer Quantity",'QUANTITY',3)

        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        fh_cal = self.obj_prompts.pyclone.add_calculator("Front Height Calculator",calc_distance_obj)

        f1 = fh_cal.add_calculator_prompt('Drawer Front 1 Height')
        f1.include = True
        f2 = fh_cal.add_calculator_prompt('Drawer Front 2 Height')
        f2.include = True
        f3 = fh_cal.add_calculator_prompt('Drawer Front 3 Height')
        f3.include = True
        f4 = fh_cal.add_calculator_prompt('Drawer Front 4 Height')
        f4.include = False
        f5 = fh_cal.add_calculator_prompt('Drawer Front 5 Height')
        f5.include = False
        f6 = fh_cal.add_calculator_prompt('Drawer Front 6 Height')
        f6.include = False
        f7 = fh_cal.add_calculator_prompt('Drawer Front 7 Height')
        f7.include = False
        f8 = fh_cal.add_calculator_prompt('Drawer Front 8 Height')
        f8.include = False

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")

        z = self.obj_z.pyclone.get_var('location.z','z')    
        dq = self.get_prompt("Drawer Quantity").get_var('dq') 
        v_gap = self.get_prompt("Vertical Gap").get_var('v_gap')
        inset = self.get_prompt("Inset Front").get_var('inset')

        fh_cal.set_total_distance('z+IF(inset,-v_gap*(dq+1),to_var+bo_var-v_gap*(dq-1))',[z,inset,to_var,bo_var,v_gap,dq])

        prev_drawer_empty = None

        drawer = None
        for i in range(1,9):
            drawer = self.add_drawer_front(i,drawer,fh_cal,to,bo,lo,ro)

    def update_prompts_after_placement(self,context):
        qty_prompt = self.get_prompt("Drawer Quantity")
        height = self.obj_z.location.z
        qty_prompt.set_value(min(math.ceil(height/pc_unit.inch(8)),8))
        qty = qty_prompt.get_value()
        calculator = self.get_calculator("Front Height Calculator")
        for i in range(1,9):
            dfh = calculator.get_calculator_prompt("Drawer Front " + str(i) + " Height")
            if i <= qty:
                dfh.include = True
            else:
                dfh.include = False

        for calculator in self.obj_prompts.pyclone.calculators:
            calculator.calculate()


class Door_Drawer(types_fronts.Fronts):

    door_type = "Base"
    door_swing = 0 # Left = 0, Right = 1, Double = 2
    two_drawers = False

    def draw(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.create_assembly("Door Drawer")
        self.obj_bp[const.DOOR_DRAWER_INSERT_TAG] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        # self.obj_bp["EXTERIOR_NAME"] = "DOORS"
        
        prompts_cabinet.add_carcass_prompts(self)
        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_door_prompts(self)
        prompts_cabinet.add_drawer_prompts(self)
        prompts_cabinet.add_front_prompts(self)
        prompts_cabinet.add_front_overlay_prompts(self)
        prompts_cabinet.add_door_pull_prompts(self)
        prompts_cabinet.add_thickness_prompts(self)
        prompts_cabinet.add_drawer_pull_prompts(self)

        self.add_prompt("Back Inset",'DISTANCE',0)
        
        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        add_two_drawer_fronts = self.add_prompt("Add Two Drawer Fronts",'CHECKBOX',self.two_drawers)
        add_two_drawer_fronts_var = add_two_drawer_fronts.get_var('add_two_drawer_fronts_var')

        top_df_height = self.add_prompt("Top Drawer Front Height",'DISTANCE',pc_unit.inch(6))
        top_df_height_var = top_df_height.get_var('top_df_height_var')

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value(self.door_type)
        
        #VARS
        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_z.pyclone.get_var('location.y','y')  
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        h_gap = self.get_prompt("Horizontal Gap").get_var('h_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        inset = self.get_prompt("Inset Front").get_var('inset')
        open_drawer = self.get_prompt("Open Drawer").get_var('open_drawer')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        #LEFT DOOR
        l_door = assemblies_cabinet.add_door_assembly(self)
        door = self.add_door_panel(l_door,"Left",to_var,bo_var,ro_var,lo_var)
        door.dim_x('z+to_var+bo_var-top_df_height_var-h_gap',[z,to_var,bo_var,top_df_height_var,h_gap])
        
        #RIGHT DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        door = self.add_door_panel(r_door,"Right",to_var,bo_var,ro_var,lo_var)
        door.dim_x('z+to_var+bo_var-top_df_height_var-h_gap',[z,to_var,bo_var,top_df_height_var,h_gap])

        #TOP DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        door = self.add_door_panel(r_door,"Top",to_var,bo_var,ro_var,lo_var)
        door.dim_x('z+to_var+bo_var-top_df_height_var-h_gap',[z,to_var,bo_var,top_df_height_var,h_gap])
        door.loc_z('z+to_var-top_df_height_var-h_gap',[z,to_var,top_df_height_var,h_gap])

        #BOTTOM DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        door = self.add_door_panel(r_door,"Bottom",to_var,bo_var,ro_var,lo_var)       
        door.dim_x('z+to_var+bo_var-top_df_height_var-h_gap',[z,to_var,bo_var,top_df_height_var,h_gap])

        l_drawer_front = assemblies_cabinet.add_door_assembly(self)
        top_o = l_drawer_front.add_prompt("Top Overlay",'DISTANCE',0)
        bottom_o = l_drawer_front.add_prompt("Bottom Overlay",'DISTANCE',0)
        left_o = l_drawer_front.add_prompt("Left Overlay",'DISTANCE',0)
        right_o = l_drawer_front.add_prompt("Right Overlay",'DISTANCE',0)        
        l_drawer_front.obj_bp[const.DRAWER_FRONT_TAG] = True
        l_drawer_front.set_name('Drawer Front')
        l_drawer_front.loc_x('-lo_var',[lo_var])
        l_drawer_front.loc_y('IF(inset,front_thickness,-door_to_cabinet_gap)-(y*open_drawer)',[inset,front_thickness,door_to_cabinet_gap,y,open_drawer])
        l_drawer_front.loc_z('z+to_var-top_df_height_var',[z,to_var,top_df_height_var])
        l_drawer_front.rot_x(value = math.radians(90))
        l_drawer_front.rot_y(value = math.radians(-90))
        l_drawer_front.dim_x('top_df_height_var',[top_df_height_var])
        l_drawer_front.dim_y('IF(add_two_drawer_fronts_var,(((x+lo_var+ro_var)-vertical_gap)/2)*-1,(x+lo_var+ro_var)*-1)',[add_two_drawer_fronts_var,x,lo_var,ro_var,vertical_gap])
        l_drawer_front.dim_z('front_thickness',[front_thickness])
        self.add_drawer_pull(l_drawer_front)
        left_o.set_formula('lo_var',[lo_var])
        right_o.set_formula('IF(add_two_drawer_fronts_var,0,ro_var)',[add_two_drawer_fronts_var,ro_var])
        # self.add_drawer_box(l_drawer_front)

        r_drawer_front = assemblies_cabinet.add_door_assembly(self)
        top_o = r_drawer_front.add_prompt("Top Overlay",'DISTANCE',0)
        bottom_o = r_drawer_front.add_prompt("Bottom Overlay",'DISTANCE',0)
        left_o = r_drawer_front.add_prompt("Left Overlay",'DISTANCE',0)
        right_o = r_drawer_front.add_prompt("Right Overlay",'DISTANCE',0)        
        r_drawer_front.obj_bp[const.DRAWER_FRONT_TAG] = True
        r_drawer_front.set_name('Drawer Front')
        r_drawer_front.loc_x('(x/2)+(vertical_gap/2)',[x,vertical_gap])
        r_drawer_front.loc_y('IF(inset,front_thickness,-door_to_cabinet_gap)-(y*open_drawer)',[inset,front_thickness,door_to_cabinet_gap,y,open_drawer])
        r_drawer_front.loc_z('z+to_var-top_df_height_var',[z,to_var,top_df_height_var])
        r_drawer_front.rot_x(value = math.radians(90))
        r_drawer_front.rot_y(value = math.radians(-90))
        r_drawer_front.dim_x('top_df_height_var',[top_df_height_var])
        r_drawer_front.dim_y('(((x+lo_var+ro_var)-vertical_gap)/2)*-1',[x,lo_var,ro_var,vertical_gap])
        r_drawer_front.dim_z('front_thickness',[front_thickness])
        hide = r_drawer_front.get_prompt('Hide')
        hide.set_formula('IF(add_two_drawer_fronts_var,False,True)',[add_two_drawer_fronts_var])
        self.add_drawer_pull(r_drawer_front)
        left_o.set_formula('0',[])
        right_o.set_formula('ro_var',[ro_var])        
        # self.add_drawer_box(r_drawer_front)

        self.set_prompts()


class Opening(Cabinet_Exterior):

    def draw(self):        
        self.create_assembly("Opening")

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')  
        z = self.obj_z.pyclone.get_var('location.z','z')  

        opening = assemblies_cabinet.add_closet_opening(self)

        opening.obj_prompts.hide_viewport = False
        opening.set_name('Cabinet Opening')
        opening.loc_x(value=0)
        opening.loc_y(value=0)
        opening.loc_z(value=0)
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('x',[x])
        opening.dim_y('y',[y])
        opening.dim_z('z',[z])  