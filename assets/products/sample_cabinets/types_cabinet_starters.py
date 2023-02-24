from email import utils
import bpy
import time
import math
from os import path
from pc_lib import pc_types, pc_unit, pc_utils

from . import prompts_cabinet
from . import assemblies_cabinet
from . import material_pointers_cabinet
from . import utils_cabinet
from . import const_cabinets as const

class Closet(pc_types.Assembly):
    # category_name = "CLOSETS"
    # subcategory_name = "STARTERS"
    # catalog_name = "_Sample"

    is_base = False
    is_hanging = False
    is_inside_corner = False

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp) 
        if obj_bp:
            if const.CLOSET_INSIDE_CORNER_TAG in obj_bp:
                self.is_inside_corner = True
            else:
                self.is_inside_corner = False
            if 'IS_BASE_BP' in obj_bp:
                self.is_base = True
            else:
                self.is_base = False
            self.is_hanging = True
            is_hanging_prompt = self.get_prompt('Is Hanging')
            if is_hanging_prompt and is_hanging_prompt.get_value() == False:
                self.is_hanging = False
            for i in range(1,10):
                opening_height_prompt = self.get_prompt("Opening " + str(i) + " Height")
                floor = self.get_prompt("Opening " + str(i) + " Floor Mounted")
                if floor:
                    if floor.get_value():
                        self.is_hanging = False
                if not opening_height_prompt:
                    self.opening_qty = i - 1
                    break

    def add_panel_prompts(self,panel):
        prompt_dict = {}
        panel.add_prompt("Left Depth",'DISTANCE',0)
        panel.add_prompt("Left Height",'DISTANCE',0)       
        panel.add_prompt("Left Floor",'CHECKBOX',False)  
        panel.add_prompt("Left Drill Start",'DISTANCE',0)
        panel.add_prompt("Left Drill Stop",'DISTANCE',0)
        panel.add_prompt("Right Depth",'DISTANCE',0)     
        panel.add_prompt("Right Height",'DISTANCE',0)
        panel.add_prompt("Right Floor",'CHECKBOX',False)
        panel.add_prompt("Right Drill Start",'DISTANCE',0)
        panel.add_prompt("Right Drill Stop",'DISTANCE',0)                                     
        panel.add_prompt("Drill From Left",'CHECKBOX',True)
        panel.add_prompt("Drill From One Side",'CHECKBOX',True)        
        
        prompt_dict["Left Depth"] = panel.get_prompt("Left Depth")
        prompt_dict["Left Height"] = panel.get_prompt("Left Height")
        prompt_dict["Left Floor"] = panel.get_prompt("Left Floor")
        prompt_dict["Left Drill Start"] = panel.get_prompt("Left Drill Start")
        prompt_dict["Left Drill Stop"] = panel.get_prompt("Left Drill Stop")
        prompt_dict["Right Depth"] = panel.get_prompt("Right Depth")
        prompt_dict["Right Height"] = panel.get_prompt("Right Height")
        prompt_dict["Right Floor"] = panel.get_prompt("Right Floor")
        prompt_dict["Right Drill Start"] = panel.get_prompt("Right Drill Start")
        prompt_dict["Right Drill Stop"] = panel.get_prompt("Right Drill Stop")
        prompt_dict["Drill From Left"] = panel.get_prompt("Drill From Left")
        prompt_dict["Drill From One Side"] = panel.get_prompt("Drill From One Side")
        return prompt_dict

class Closet_Starter(Closet):
    show_in_library = True

    opening_qty = 4
    panels = []
    left_bridge_parts = []
    right_bridge_parts = []
    left_filler = None
    right_filler = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)
        self.left_bridge_parts = []
        self.right_bridge_parts = []
        if obj_bp:
            for child in obj_bp.children:
                if "IS_LEFT_BRIDGE_BP" in child:
                    self.left_bridge_parts.append(pc_types.Assembly(child))
                if "IS_RIGHT_BRIDGE_BP" in child:
                    self.right_bridge_parts.append(pc_types.Assembly(child))
                if "IS_LEFT_FILLER_BP" in child:
                    self.left_filler = pc_types.Assembly(child)
                if "IS_RIGHT_FILLER_BP" in child:
                    self.right_filler = pc_types.Assembly(child)
        
    def get_drivers(self,obj):
        drivers = []
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                drivers.append(driver)

        if obj.data and obj.data.animation_data:
            for driver in obj.data.animation_data.drivers:
                drivers.append(driver)

        if obj.data and obj.data.shape_keys and obj.data.shape_keys.animation_data:
            for driver in obj.data.shape_keys.animation_data.drivers:
                drivers.append(driver)

        return drivers            

    def update_calculator_formula(self):
        calculator = self.get_calculator("Opening Calculator")
        width = self.obj_x.pyclone.get_var('location.x','width')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        left_filler_width = self.get_prompt("Left Side Wall Filler").get_var("left_filler_width")
        right_filler_width = self.get_prompt("Right Side Wall Filler").get_var("right_filler_width")
        calc_formula = 'width-left_filler_width-right_filler_width-p_thickness*' + str(self.opening_qty+1)
        calc_vars = [width,p_thickness,left_filler_width,right_filler_width]
        drivers = self.get_drivers(calculator.distance_obj)

        for driver in drivers:
            for var in driver.driver.variables:
                driver.driver.variables.remove(var)

        for i in range(1,self.opening_qty+1):
            if i != self.opening_qty:
                d_panel = self.get_prompt("Double Panel " + str(i)).get_var("d_panel_" + str(i))
                calc_vars.append(d_panel)
                calc_formula += "-IF(d_panel_" + str(i) + ",p_thickness,0)"

        calculator.set_total_distance(calc_formula,calc_vars)
        calculator.calculate()

    def add_opening_calculator(self):
        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        self.obj_prompts.pyclone.add_calculator("Opening Calculator",calc_distance_obj)

    def add_opening_prompts(self,number):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        default_height = pc_unit.millimeter(int(props.hanging_closet_panel_height)) if self.is_hanging else self.obj_z.location.z
        calculator = self.get_calculator("Opening Calculator")
        calculator.add_calculator_prompt('Opening ' + str(number) + ' Width')
        self.add_prompt("Opening " + str(number) + " Height",'DISTANCE',default_height)
        self.add_prompt("Opening " + str(number) + " Depth",'DISTANCE',math.fabs(self.obj_y.location.y))
        self.add_prompt("Opening " + str(number) + " Floor Mounted",'CHECKBOX',False if self.is_hanging else True)
        self.add_prompt("Remove Bottom " + str(number),'CHECKBOX',False)
        if number != self.opening_qty:
            double_panel = self.add_prompt("Double Panel " + str(number),'CHECKBOX',False)        

    def add_panel(self,index,previous_panel):
        previous_panel_x = previous_panel.obj_bp.pyclone.get_var('location.x',"previous_panel_x")

        height = self.obj_z.pyclone.get_var('location.z','height')
        opening_width_prompt = self.get_prompt("Opening " + str(index) + " Width")
        left_width = opening_width_prompt.get_var("Opening Calculator","left_width")
        left_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('left_depth')
        left_height = self.get_prompt("Opening " + str(index) + " Height").get_var('left_height')
        left_floor = self.get_prompt("Opening " + str(index) + " Floor Mounted").get_var('left_floor')
        right_floor = self.get_prompt("Opening " + str(index+1) + " Floor Mounted").get_var('right_floor')
        right_depth = self.get_prompt("Opening " + str(index+1) + " Depth").get_var('right_depth')
        right_height = self.get_prompt("Opening " + str(index+1) + " Height").get_var('right_height')
        drill_start_loc = self.get_prompt("Drill Start Location").get_var("drill_start_loc")
        dp = self.get_prompt("Double Panel " + str(index)).get_var('dp')
        left_filler = self.get_prompt("Left Side Wall Filler").get_var("left_filler")
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        ep = self.get_prompt("Extend Panels to Countertop").get_var("ep")
        ea = self.get_prompt("Extend Panel Amount").get_var("ea")

        panel = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(panel.obj_bp)
        props.ebl1 = True
        panel.obj_bp["IS_PANEL_BP"] = True
        panel.obj_bp["IS_CLOSET_PARTITION_BP"] = True
        panel.set_name('Closet Partition ' + str(index))
        panel.loc_x('previous_panel_x+left_width+p_thickness+IF(dp,p_thickness,0)',[previous_panel_x,left_width,p_thickness,dp])
        panel.loc_y(value = 0)
        panel.loc_z("IF(dp,IF(right_floor,0,height-right_height-IF(ep,ea,0)),IF(OR(left_floor,right_floor),0,min(height-left_height,height-right_height)-IF(ep,ea,0)))",
                    [dp,left_floor,right_floor,height,left_height,right_height,ep,ea])        
        panel.rot_y(value=math.radians(-90))
        panel.rot_z(value=0)
        panel.dim_x('IF(dp,right_height+IF(ep,ea,0),max(IF(left_floor,left_height,IF(right_floor,height,left_height+IF(ep,ea,0))),IF(right_floor,right_height,IF(left_floor,height,right_height+IF(ep,ea,0)))))',
                    [left_floor,height,right_floor,left_height,right_height,dp,ep,ea])        
        panel.dim_y('IF(dp,-right_depth,-max(left_depth,right_depth))',[dp,left_depth,right_depth])
        panel.dim_z('-p_thickness',[p_thickness])
        prompt_dict = self.add_panel_prompts(panel)
        prompt_dict["Left Depth"].set_formula('IF(dp,0,left_depth)',[left_depth,dp])
        prompt_dict["Left Height"].set_formula('IF(dp,0,left_height)',[left_height,dp])       
        prompt_dict["Left Floor"].set_formula('IF(dp,0,left_floor)',[left_floor,dp])       
        prompt_dict["Left Drill Start"].set_formula('IF(left_floor,drill_start_loc,IF(right_floor,height-left_height+drill_start_loc,IF(left_height<=right_height,right_height-left_height+drill_start_loc,drill_start_loc)))',
                                     [left_floor,right_floor,height,left_height,right_height,drill_start_loc])  
        prompt_dict["Left Drill Stop"].set_formula('IF(left_floor,left_height,IF(right_floor,height,max(left_height,right_height)))',
                                    [left_floor,right_floor,height,left_height,right_height])  
        prompt_dict["Right Depth"].set_formula('right_depth',[right_depth])          
        prompt_dict["Right Height"].set_formula('right_height',[right_height])        
        prompt_dict["Right Floor"].set_formula('right_floor',[right_floor])   
        prompt_dict["Right Drill Start"].set_formula('IF(right_floor,drill_start_loc,IF(left_floor,height-right_height+drill_start_loc,IF(right_height<=left_height,left_height-right_height+drill_start_loc,drill_start_loc)))',
                                      [right_floor,left_floor,height,right_height,left_height,drill_start_loc])
        prompt_dict["Right Drill Stop"].set_formula('IF(right_floor,right_height,IF(left_floor,height,max(left_height,right_height)))',
                                     [left_floor,right_floor,height,left_height,right_height])                                          
        prompt_dict["Drill From Left"].set_value(True)
        prompt_dict["Drill From One Side"].set_formula('IF(left_depth==right_depth,IF(left_floor==right_floor,True,False),False)',
                                        [left_depth,right_depth,left_floor,right_floor,dp])

        d_panel = assemblies_cabinet.add_closet_part(self)
        d_panel.obj_bp["IS_PANEL_BP"] = True
        d_panel.obj_bp["IS_DOUBLE_PANEL_BP"] = True
        props = utils_cabinet.get_object_props(d_panel.obj_bp)
        props.ebl1 = True
        d_panel.set_name('Double Panel ' + str(index))
        d_panel.loc_x('previous_panel_x+left_width+p_thickness+p_thickness',[previous_panel_x,left_width,p_thickness])
        d_panel.loc_y(value = 0)
        d_panel.loc_z("IF(left_floor,0,height-left_height)",[left_floor,height,left_height])
        d_panel.rot_y(value=math.radians(-90))
        d_panel.rot_z(value=0)
        d_panel.dim_x('left_height',[left_height])
        d_panel.dim_y('-left_depth',[left_depth])
        d_panel.dim_z('p_thickness',[p_thickness])    
        pc_utils.flip_normals(d_panel)
        hide = d_panel.get_prompt('Hide')
        hide.set_formula('IF(dp,False,True)',[dp])
        prompt_dict = self.add_panel_prompts(d_panel)
        prompt_dict["Left Depth"].set_formula('left_depth',[left_depth])
        prompt_dict["Left Height"].set_formula('left_height',[left_height])   
        prompt_dict["Left Floor"].set_formula('left_floor',[left_floor])
        prompt_dict["Left Drill Start"].set_formula('IF(left_floor,drill_start_loc,IF(right_floor,height-left_height+drill_start_loc,IF(left_height<=right_height,right_height-left_height+drill_start_loc,drill_start_loc)))',
                                     [left_floor,right_floor,height,left_height,right_height,drill_start_loc]) 
        prompt_dict["Left Drill Stop"].set_formula('IF(left_floor,left_height,IF(right_floor,height,max(left_height,right_height)))',
                                    [left_floor,right_floor,height,left_height,right_height])  
        prompt_dict["Right Depth"].set_formula('0',[])  
        prompt_dict["Right Height"].set_formula('0',[])  
        prompt_dict["Right Floor"].set_formula('False',[]) 
        prompt_dict["Right Drill Start"].set_formula('0',[])
        prompt_dict["Right Drill Stop"].set_formula('0',[])    
        prompt_dict["Drill From Left"].set_value(True)
        prompt_dict["Drill From One Side"].set_value(True)                                     
        return panel

    def add_shelf(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')
        right_panel_x = right_panel.obj_bp.pyclone.get_var('location.x','right_panel_x')
        left_depth = left_panel.get_prompt('Left Depth').get_var('left_depth')
        right_depth = right_panel.get_prompt('Right Depth').get_var('right_depth')

        opening_width = self.get_prompt("Opening " + str(index) + " Width").get_var('Opening Calculator','opening_width')
        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")

        shelf = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(shelf.obj_bp)
        props.ebl1 = True    
        props.opening_number = index
        l_depth = shelf.add_prompt("Left Depth",'DISTANCE',0)
        l_depth.set_formula('left_depth',[left_depth])
        r_depth = shelf.add_prompt("Right Depth",'DISTANCE',0)
        r_depth.set_formula('right_depth',[right_depth])        
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Shelf ' + str(index))
        shelf.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        shelf.loc_y(value = 0)
        shelf.loc_z(value = 0)
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('opening_width',[opening_width])
        shelf.dim_y('-opening_depth',[opening_depth])
        shelf.dim_z('s_thickness',[s_thickness])
        pc_utils.flip_normals(shelf)
        return shelf

    def add_countertop(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        ctop_thickness = self.add_prompt("Countertop Thickness",'DISTANCE',props.countertop_thickness) 
        ctop_overhang_front = self.add_prompt("Countertop Overhang Front",'DISTANCE',pc_unit.inch(1.5)) 
        ctop_overhang_left = self.add_prompt("Countertop Overhang Left",'DISTANCE',pc_unit.inch(0)) 
        ctop_overhang_right = self.add_prompt("Countertop Overhang Right",'DISTANCE',pc_unit.inch(0)) 
        ctop_thickness_var = ctop_thickness.get_var("ctop_thickness_var")
        ctop_overhang_front_var = ctop_overhang_front.get_var("ctop_overhang_front_var")
        ctop_overhang_left_var = ctop_overhang_left.get_var("ctop_overhang_left_var")
        ctop_overhang_right_var = ctop_overhang_right.get_var("ctop_overhang_right_var")

        ctop = assemblies_cabinet.add_countertop_part(self)
        ctop.obj_bp["IS_COUNTERTOP_BP"] = True
        ctop.set_name('Countertop')
        ctop.loc_x('-ctop_overhang_left_var',[ctop_overhang_left_var])
        ctop.loc_y(value = 0)
        ctop.loc_z('height',[height])
        ctop.rot_x(value = 0)
        ctop.rot_y(value = 0)
        ctop.rot_z(value = 0)
        ctop.dim_x('width+ctop_overhang_left_var+ctop_overhang_right_var',[width,ctop_overhang_left_var,ctop_overhang_right_var])
        ctop.dim_y('depth-ctop_overhang_front_var',[depth,ctop_overhang_front_var])
        ctop.dim_z('ctop_thickness_var',[ctop_thickness_var])
        ctop.obj_bp.hide_viewport = True
        ctop.obj_x.hide_viewport = True
        ctop.obj_y.hide_viewport = True
        ctop.obj_z.hide_viewport = True
        pc_utils.flip_normals(ctop)
        return ctop

    def add_toe_kick(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')
        right_panel_x = right_panel.obj_bp.pyclone.get_var('location.x','right_panel_x')
        floor = self.get_prompt("Opening " + str(index) + " Floor Mounted").get_var('floor')
        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        opening_width = self.get_prompt("Opening " + str(index) + " Width").get_var('Opening Calculator','opening_width')
        double_panel = self.get_prompt("Double Panel " + str(index))
        remove_bottom = self.get_prompt("Remove Bottom " + str(index)).get_var('remove_bottom')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        kick_height = self.get_prompt("Closet Kick Height").get_var("kick_height")
        kick_setback = self.get_prompt("Closet Kick Setback").get_var("kick_setback")

        kick = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(kick.obj_bp)  
        props.opening_number = index        
        kick.obj_bp["IS_TOE_KICK_BP"] = True
        kick.set_name('Kick ' + str(index))
        kick.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        kick.loc_y('-opening_depth+kick_setback',[opening_depth,kick_setback])
        kick.loc_z(value = 0)
        kick.rot_x(value = math.radians(-90))
        kick.rot_y(value = 0)
        kick.rot_z(value = 0)
        kick.dim_x('opening_width',[opening_width])
        kick.dim_y('-kick_height',[kick_height])
        kick.dim_z('s_thickness',[s_thickness])
        hide = kick.get_prompt("Hide")
        hide.set_formula('IF(floor,IF(remove_bottom,True,False),True)',[floor,remove_bottom])
        pc_utils.flip_normals(kick)
        return kick

    def add_opening(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')
        right_panel_x = right_panel.obj_bp.pyclone.get_var('location.x','right_panel_x')
        left_depth = left_panel.get_prompt('Left Depth').get_var('left_depth')
        right_depth = right_panel.get_prompt('Right Depth').get_var('right_depth')
        p_height = self.obj_z.pyclone.get_var('location.z','p_height')
        floor = self.get_prompt("Opening " + str(index) + " Floor Mounted").get_var('floor')
        opening_width = self.get_prompt("Opening " + str(index) + " Width").get_var('Opening Calculator','opening_width')
        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        opening_height = self.get_prompt("Opening " + str(index) + " Height").get_var('opening_height')
        remove_bottom = self.get_prompt("Remove Bottom " + str(index)).get_var('remove_bottom')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        kick_height = self.get_prompt("Closet Kick Height").get_var("kick_height")

        opening = assemblies_cabinet.add_closet_opening(self)
        l_depth = opening.get_prompt("Left Depth")
        l_depth.set_formula('left_depth',[left_depth])
        r_depth = opening.get_prompt("Right Depth")
        r_depth.set_formula('right_depth',[right_depth])
        props = utils_cabinet.get_object_props(opening.obj_bp)  
        props.opening_number = index 
        opening.obj_prompts.hide_viewport = False
        opening.set_name('Opening ' + str(index))
        opening.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        opening.loc_y('-opening_depth',[opening_depth])
        opening.loc_z('IF(floor,kick_height,p_height-opening_height)+IF(remove_bottom,0,s_thickness)',
                         [floor,kick_height,p_height,opening_height,remove_bottom,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('opening_width',[opening_width])
        opening.dim_y('opening_depth',[opening_depth])
        opening.dim_z('opening_height-IF(floor,kick_height,0)-IF(remove_bottom,s_thickness,s_thickness*2)',[opening_height,kick_height,s_thickness,floor,remove_bottom])
        return opening

    def pre_draw(self):
        self.create_assembly()
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.obj_x.location.x = pc_unit.inch(96)
        
        if self.is_hanging:
            self.obj_y.location.y = -props.default_hanging_closet_depth
            self.obj_z.location.z = pc_unit.millimeter(int(props.default_closet_hanging_height))
            
        if self.is_base:
            self.obj_y.location.y = -props.default_base_closet_depth
            self.obj_z.location.z = pc_unit.millimeter(int(props.base_closet_panel_height))

        if not self.is_hanging and not self.is_base:
            self.obj_y.location.y = -props.default_tall_closet_depth
            self.obj_z.location.z = pc_unit.millimeter(int(props.tall_closet_panel_height))

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = assemblies_cabinet.add_closet_part(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])          

    def add_left_blind_parts(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        p_height = self.obj_z.pyclone.get_var('location.z','p_height')
        floor_1 = self.get_prompt("Opening 1 Floor Mounted").get_var("floor_1")
        height_1 = self.get_prompt("Opening 1 Height").get_var("height_1")
        kick_setback = self.get_prompt('Closet Kick Setback').get_var('kick_setback')
        b_left_width = self.get_prompt('Left Bridge Shelf Width').get_var("b_left_width")
        kick_height = self.get_prompt('Closet Kick Height').get_var("kick_height")
        b_left = self.get_prompt('Bridge Left').get_var("b_left")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        depth_1 = self.get_prompt("Opening 1 Depth").get_var("depth_1")

        if props.add_bottom_filler_shelf:
            left_bot_bridge = assemblies_cabinet.add_closet_part(self)
            props = utils_cabinet.get_object_props(left_bot_bridge.obj_bp)
            props.ebl1 = True          
            left_bot_bridge.obj_bp["IS_LEFT_BRIDGE_BP"] = True
            left_bot_bridge.set_name('Left Bridge Bottom')
            left_bot_bridge.loc_x('-b_left_width',[b_left_width])
            left_bot_bridge.loc_y(value = 0)
            left_bot_bridge.loc_z('IF(floor_1,kick_height,p_height-height_1)',[floor_1,kick_height,p_height,height_1])
            left_bot_bridge.rot_y(value = 0)
            left_bot_bridge.rot_z(value = 0)
            left_bot_bridge.dim_x('b_left_width',[b_left_width])
            left_bot_bridge.dim_y('-depth_1',[depth_1])
            left_bot_bridge.dim_z('s_thickness',[s_thickness])
            hide = left_bot_bridge.get_prompt("Hide")
            hide.set_formula('IF(b_left,False,True)',[b_left])
            pc_utils.flip_normals(left_bot_bridge)
            self.left_bridge_parts.append(left_bot_bridge)

            left_bridge_kick = assemblies_cabinet.add_closet_part(self)
            left_bridge_kick.obj_bp["IS_LEFT_BRIDGE_BP"] = True
            left_bridge_kick.set_name('Left Bridge Bottom')
            left_bridge_kick.loc_x('-b_left_width-kick_setback',[b_left_width,kick_setback])
            left_bridge_kick.loc_y('-depth_1+kick_setback',[depth_1,kick_setback])
            left_bridge_kick.loc_z(value = 0)
            left_bridge_kick.rot_x(value = math.radians(-90))
            left_bridge_kick.rot_y(value = 0)
            left_bridge_kick.rot_z(value = 0)
            left_bridge_kick.dim_x('b_left_width+kick_setback',[b_left_width,kick_setback])
            left_bridge_kick.dim_y('-kick_height',[kick_height])
            left_bridge_kick.dim_z('s_thickness',[s_thickness])
            hide = left_bridge_kick.get_prompt("Hide")
            hide.set_formula('IF(b_left,IF(floor_1,False,True),True)',[b_left,floor_1])
            pc_utils.flip_normals(left_bridge_kick)
            self.left_bridge_parts.append(left_bridge_kick)

        left_top_bridge = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(left_top_bridge.obj_bp)
        props.ebl1 = True               
        left_top_bridge.obj_bp["IS_LEFT_BRIDGE_BP"] = True
        left_top_bridge.set_name('Left Bridge Bottom')
        left_top_bridge.loc_x('-b_left_width',[b_left_width])
        left_top_bridge.loc_y(value = 0)
        left_top_bridge.loc_z('IF(floor_1,height_1,p_height)',[floor_1,height_1,p_height])
        left_top_bridge.rot_y(value = 0)
        left_top_bridge.rot_z(value = 0)
        left_top_bridge.dim_x('b_left_width',[b_left_width])
        left_top_bridge.dim_y('-depth_1',[depth_1])
        left_top_bridge.dim_z('-s_thickness',[s_thickness])
        hide = left_top_bridge.get_prompt("Hide")
        hide.set_formula('IF(b_left,False,True)',[b_left])
        pc_utils.flip_normals(left_top_bridge)
        self.left_bridge_parts.append(left_top_bridge)

    def add_right_blind_parts(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        p_height = self.obj_z.pyclone.get_var('location.z','p_height')
        floor_last = self.get_prompt("Opening " + str(self.opening_qty) + " Floor Mounted").get_var("floor_last")        
        width = self.obj_x.pyclone.get_var('location.x','width')
        height_last = self.get_prompt("Opening " + str(self.opening_qty) + " Height").get_var("height_last")
        kick_setback = self.get_prompt('Closet Kick Setback').get_var('kick_setback')
        b_right_width = self.get_prompt('Right Bridge Shelf Width').get_var("b_right_width")
        kick_height = self.get_prompt('Closet Kick Height').get_var("kick_height")
        b_right = self.get_prompt('Bridge Right').get_var("b_right")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        depth_last = self.get_prompt("Opening " + str(self.opening_qty) + " Depth").get_var("depth_last")

        if props.add_bottom_filler_shelf:
            right_bot_bridge = assemblies_cabinet.add_closet_part(self)
            props = utils_cabinet.get_object_props(right_bot_bridge.obj_bp)
            props.ebl1 = True              
            right_bot_bridge.obj_bp["IS_RIGHT_BRIDGE_BP"] = True
            right_bot_bridge.set_name('Right Bridge Bottom')
            right_bot_bridge.loc_x('width',[width])
            right_bot_bridge.loc_y(value = 0)
            right_bot_bridge.loc_z('IF(floor_last,kick_height,p_height-height_last)',[floor_last,kick_height,p_height,height_last])
            right_bot_bridge.rot_y(value = 0)
            right_bot_bridge.rot_z(value = 0)
            right_bot_bridge.dim_x('b_right_width',[b_right_width])
            right_bot_bridge.dim_y('-depth_last',[depth_last])
            right_bot_bridge.dim_z('s_thickness',[s_thickness])
            hide = right_bot_bridge.get_prompt("Hide")
            hide.set_formula('IF(b_right,False,True)',[b_right])        
            pc_utils.flip_normals(right_bot_bridge)
            self.right_bridge_parts.append(right_bot_bridge)

            right_bridge_kick = assemblies_cabinet.add_closet_part(self)
            right_bridge_kick.obj_bp["IS_RIGHT_BRIDGE_BP"] = True
            right_bridge_kick.set_name('Right Bridge Kick')
            right_bridge_kick.loc_x('width',[width])
            right_bridge_kick.loc_y('-depth_last+kick_setback',[depth_last,kick_setback])
            right_bridge_kick.loc_z(value = 0)
            right_bridge_kick.rot_x(value = math.radians(-90))
            right_bridge_kick.rot_y(value = 0)
            right_bridge_kick.rot_z(value = 0)
            right_bridge_kick.dim_x('b_right_width+kick_setback',[b_right_width,kick_setback])
            right_bridge_kick.dim_y('-kick_height',[kick_height])
            right_bridge_kick.dim_z('s_thickness',[s_thickness])
            hide = right_bridge_kick.get_prompt("Hide")
            hide.set_formula('IF(b_right,IF(floor_last,False,True),True)',[b_right,floor_last])  
            pc_utils.flip_normals(right_bridge_kick)
            self.right_bridge_parts.append(right_bridge_kick)

        right_top_bridge = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(right_top_bridge.obj_bp)
        props.ebl1 = True           
        right_top_bridge.obj_bp["IS_RIGHT_BRIDGE_BP"] = True
        right_top_bridge.set_name('Right Bridge Bottom')
        right_top_bridge.loc_x('width',[width])
        right_top_bridge.loc_y(value = 0)
        right_top_bridge.loc_z('IF(floor_last,height_last,p_height)',[floor_last,height_last,p_height])
        right_top_bridge.rot_y(value = 0)
        right_top_bridge.rot_z(value = 0)
        right_top_bridge.dim_x('b_right_width',[b_right_width])
        right_top_bridge.dim_y('-depth_last',[depth_last])
        right_top_bridge.dim_z('-s_thickness',[s_thickness])
        hide = right_top_bridge.get_prompt("Hide")
        hide.set_formula('IF(b_right,False,True)',[b_right])        
        pc_utils.flip_normals(right_top_bridge)
        self.right_bridge_parts.append(right_top_bridge)

    def add_system_holes(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')

        p_height = self.obj_z.pyclone.get_var('location.z','p_height')
        floor = self.get_prompt("Opening " + str(index) + " Floor Mounted").get_var('floor')
        opening_width = self.get_prompt("Opening " + str(index) + " Width").get_var('Opening Calculator','opening_width')
        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        opening_height = self.get_prompt("Opening " + str(index) + " Height").get_var('opening_height')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")

        holes = assemblies_cabinet.add_shelf_holes(self)
        holes.set_name('System Holes ' + str(index))
        holes.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        holes.loc_y('-opening_depth',[opening_depth])
        holes.loc_z('IF(floor,0,p_height-opening_height)',[floor,p_height,opening_height])
        holes.rot_x(value = 0)
        holes.rot_y(value = 0)
        holes.rot_z(value = 0)
        holes.dim_x('opening_width',[opening_width])
        holes.dim_y('opening_depth',[opening_depth])
        holes.dim_z('opening_height',[opening_height])
        dim_from_bottom = holes.get_prompt("Shelf Hole Dim From Bottom")
        dim_from_bottom.set_value(pc_unit.millimeter(9.525))
        dim_from_top = holes.get_prompt("Shelf Hole Dim From Top")
        dim_from_top.set_value(0)
        dim_from_front = holes.get_prompt("Shelf Hole Dim From Front")
        dim_from_front.set_value(pc_unit.inch(2))
        dim_from_rear = holes.get_prompt("Shelf Hole Dim From Rear")
        dim_from_rear.set_value(pc_unit.inch(2))
        return holes

    def add_left_filler(self):
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_filler_width = self.get_prompt("Left Side Wall Filler").get_var("left_filler_width")
        floor_1 = self.get_prompt("Opening 1 Floor Mounted").get_var("floor_1")
        height_1 = self.get_prompt("Opening 1 Height").get_var("height_1")
        depth_1 = self.get_prompt("Opening 1 Depth").get_var("depth_1")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")

        self.left_filler = assemblies_cabinet.add_closet_part(self)
        self.left_filler.obj_bp["IS_LEFT_FILLER_BP"] = True
        self.left_filler.set_name('Left Filler')
        self.left_filler.loc_x(value=0)
        self.left_filler.loc_y('-depth_1',[depth_1])
        self.left_filler.loc_z('IF(floor_1,0,height-height_1)',[floor_1,height,height_1])
        self.left_filler.rot_x(value=0)
        self.left_filler.rot_y(value=math.radians(-90))
        self.left_filler.rot_z(value=math.radians(90))        
        self.left_filler.dim_x('height_1',[height_1])
        self.left_filler.dim_y('-left_filler_width',[left_filler_width])
        self.left_filler.dim_z('-s_thickness',[s_thickness])
        material_pointers_cabinet.assign_pointer_to_assembly(self.left_filler,"Cabinet Exposed Surfaces")

    def add_right_filler(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        floor_last = self.get_prompt("Opening " + str(self.opening_qty) + " Floor Mounted").get_var("floor_last")
        right_filler_width = self.get_prompt("Right Side Wall Filler").get_var("right_filler_width")
        height_last = self.get_prompt("Opening " + str(self.opening_qty) + " Height").get_var("height_last")
        depth_last = self.get_prompt("Opening " + str(self.opening_qty) + " Depth").get_var("depth_last")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")

        self.right_filler = assemblies_cabinet.add_closet_part(self)
        self.right_filler.obj_bp["IS_RIGHT_FILLER_BP"] = True
        self.right_filler.set_name('Right Filler')
        self.right_filler.loc_x('width',[width])
        self.right_filler.loc_y('-depth_last',[depth_last])
        self.right_filler.loc_z('IF(floor_last,0,height-height_last)',[floor_last,height,height_last])
        self.right_filler.rot_x(value=0)
        self.right_filler.rot_y(value=math.radians(-90))
        self.right_filler.rot_z(value=math.radians(90))
        self.right_filler.dim_x('height_last',[height_last])
        self.right_filler.dim_y('right_filler_width',[right_filler_width])
        self.right_filler.dim_z('-s_thickness',[s_thickness])
        pc_utils.flip_normals(self.right_filler)
        material_pointers_cabinet.assign_pointer_to_assembly(self.right_filler,"Cabinet Exposed Surfaces")

    def add_top_and_bottom_shelf(self,index,left_panel,right_panel):
        height = self.obj_z.pyclone.get_var('location.z','height')
        shelf_thickness_var = self.get_prompt("Shelf Thickness").get_var("shelf_thickness_var") 
        closet_kick_height_var = self.get_prompt("Closet Kick Height").get_var("closet_kick_height_var") 
        opening_height = self.get_prompt("Opening " + str(index) + " Height").get_var('opening_height')
        floor = self.get_prompt("Opening " + str(index) + " Floor Mounted").get_var('floor')
        remove_bottom = self.get_prompt("Remove Bottom " + str(index)).get_var('remove_bottom')

        bottom = self.add_shelf(index,left_panel,right_panel)
        bottom.loc_z('IF(floor,closet_kick_height_var,height-opening_height)',[floor,closet_kick_height_var,height,opening_height])
        hide = bottom.get_prompt('Hide')
        hide.set_formula('remove_bottom',[remove_bottom])

        top = self.add_shelf(index,left_panel,right_panel)
        top.loc_z('IF(floor,opening_height,height)-shelf_thickness_var',[floor,opening_height,height,shelf_thickness_var])

    def update_last_panel_formulas(self,last_panel):
        drivers = self.get_drivers(last_panel.obj_bp)
        pc_utils.delete_driver_variables(drivers)
        drivers = self.get_drivers(last_panel.obj_x)
        pc_utils.delete_driver_variables(drivers)
        drivers = self.get_drivers(last_panel.obj_y)
        pc_utils.delete_driver_variables(drivers)
        drivers = self.get_drivers(last_panel.obj_prompts)
        pc_utils.delete_driver_variables(drivers)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')      
        rfe = self.get_prompt("Right Finished End").get_var("rfe")                 
        depth_last = self.get_prompt("Opening " + str(self.opening_qty) + " Depth").get_var("depth_last")
        height_last = self.get_prompt("Opening " + str(self.opening_qty) + " Height").get_var("height_last")
        floor_last = self.get_prompt("Opening " + str(self.opening_qty) + " Floor Mounted").get_var("floor_last")
        right_filler = self.get_prompt("Right Side Wall Filler").get_var("right_filler")
        drill_start_loc = self.get_prompt("Drill Start Location").get_var("drill_start_loc")

        is_finished = last_panel.get_prompt("Is Finished")
        left_depth = last_panel.get_prompt("Left Depth")
        left_height = last_panel.get_prompt("Left Height") 
        left_floor = last_panel.get_prompt("Left Floor")
        left_drill_start = last_panel.get_prompt("Left Drill Start")
        left_drill_stop = last_panel.get_prompt("Left Drill Stop")
        right_depth = last_panel.get_prompt("Right Depth")
        right_height = last_panel.get_prompt("Right Height")   
        right_floor = last_panel.get_prompt("Right Floor")   
        right_drill_start = last_panel.get_prompt("Right Drill Start")
        right_drill_stop = last_panel.get_prompt("Right Drill Stop")

        last_panel.loc_x('width-right_filler',[width,right_filler])
        last_panel.loc_z('IF(floor_last,0,height-height_last)',[floor_last,height,height_last])
        last_panel.dim_x('height_last',[height_last])
        last_panel.dim_y('-depth_last',[depth_last])
        last_panel.dim_x('height_last',[height_last])
        last_panel.dim_y('-depth_last',[depth_last])
        if is_finished:       
            is_finished.set_formula('rfe',[rfe])
        left_depth.set_formula('depth_last',[depth_last]) 
        left_height.set_formula('height_last',[height_last])  
        left_floor.set_formula('floor_last',[floor_last])  
        left_drill_start.set_formula("drill_start_loc",[drill_start_loc]) 
        left_drill_stop.set_formula('height_last',[height_last]) 
        right_depth.set_formula('0',[])  
        right_height.set_formula('0',[]) 
        right_floor.set_formula('False',[]) 
        right_drill_start.set_formula('0',[]) 
        right_drill_stop.set_formula('0',[]) 

    def draw(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.panels = []
        start_time = time.time()

        self.obj_bp["IS_CLOSET_BP"] = True
        if self.is_base:
            self.obj_bp["IS_BASE_BP"] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.opening_cabinet_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_opening_commands"
        self.obj_y['IS_MIRROR'] = True

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')

        prompts_cabinet.add_closet_thickness_prompts(self)
        prompts_cabinet.add_closet_toe_kick_prompts(self)
        panel_thickness_var = self.get_prompt("Panel Thickness").get_var("panel_thickness_var")
        
        self.add_prompt("Drill Start Location",'DISTANCE',pc_unit.inch(.35)) 
        self.add_prompt("Left Finished End",'CHECKBOX',False)  
        self.add_prompt("Right Finished End",'CHECKBOX',False)   
        self.add_prompt("Left End Condition",'COMBOBOX',0,["EP","WP","CP","OFF"]) 
        self.add_prompt("Right End Condition",'COMBOBOX',0,["EP","WP","CP","OFF"]) 
        self.add_prompt("Left Side Wall Filler",'DISTANCE',0) 
        self.add_prompt("Right Side Wall Filler",'DISTANCE',0) 
        self.add_prompt("Left Offset",'DISTANCE',0)
        self.add_prompt("Right Offset",'DISTANCE',0)        
        self.add_prompt("Bridge Left",'CHECKBOX',False) 
        self.add_prompt("Bridge Right",'CHECKBOX',False) 
        self.add_prompt("Left Bridge Shelf Width",'DISTANCE',pc_unit.inch(14))
        self.add_prompt("Right Bridge Shelf Width",'DISTANCE',pc_unit.inch(14))
        self.add_prompt("Extend Panels to Countertop",'CHECKBOX',False)   
        self.add_prompt("Extend Panel Amount",'DISTANCE',props.extend_panel_amount)

        self.add_opening_calculator()
        for i in range(self.opening_qty):
            self.add_opening_prompts(i + 1)
        self.update_calculator_formula()

        depth_1 = self.get_prompt("Opening 1 Depth").get_var("depth_1")
        height_1 = self.get_prompt("Opening 1 Height").get_var("height_1")
        floor_1 = self.get_prompt("Opening 1 Floor Mounted").get_var("floor_1")
        drill_start_loc = self.get_prompt("Drill Start Location").get_var("drill_start_loc")
        depth_last = self.get_prompt("Opening " + str(self.opening_qty) + " Depth").get_var("depth_last")
        height_last = self.get_prompt("Opening " + str(self.opening_qty) + " Height").get_var("height_last")
        floor_last = self.get_prompt("Opening " + str(self.opening_qty) + " Floor Mounted").get_var("floor_last")
        lfe = self.get_prompt("Left Finished End").get_var("lfe")
        rfe = self.get_prompt("Right Finished End").get_var("rfe")
        lec = self.get_prompt("Left End Condition").get_var("lec")
        rec = self.get_prompt("Right End Condition").get_var("rec")
        left_filler = self.get_prompt("Left Side Wall Filler").get_var("left_filler")
        right_filler = self.get_prompt("Right Side Wall Filler").get_var("right_filler")
        ep = self.get_prompt("Extend Panels to Countertop").get_var("ep")
        ea = self.get_prompt("Extend Panel Amount").get_var("ea")

        left_side = assemblies_cabinet.add_closet_part(self)
        hb_props = utils_cabinet.get_object_props(left_side.obj_bp)
        hb_props.ebl1 = True              
        left_side.obj_bp["IS_PANEL_BP"] = True
        left_side.set_name('Closet Partition')
        left_side.loc_x('left_filler',[left_filler])
        left_side.loc_y(value = 0)
        left_side.loc_z('IF(floor_1,0,height-height_1-IF(ep,ea,0))',[floor_1,height,height_1,ep,ea])
        left_side.rot_y(value=math.radians(-90))
        left_side.rot_z(value=0)
        left_side.dim_x('height_1+IF(floor_1,0,IF(ep,ea,0))',[height_1,floor_1,ep,ea])
        left_side.dim_y('-depth_1',[depth_1])
        left_side.dim_z('-panel_thickness_var',[panel_thickness_var])
        self.panels.append(left_side)
        is_finished = left_side.add_prompt("Is Finished",'CHECKBOX',False)
        is_finished.set_formula('lfe',[lfe])
        left_side.add_prompt("Is Left End Panel",'CHECKBOX',True)

        prompt_dict = self.add_panel_prompts(left_side)
        prompt_dict["Left Depth"].set_formula('0',[])
        prompt_dict["Left Height"].set_formula('0',[])   
        prompt_dict["Left Floor"].set_formula('False',[])
        prompt_dict["Left Drill Start"].set_formula('0',[])
        prompt_dict["Left Drill Stop"].set_formula('0',[])  
        prompt_dict["Right Depth"].set_formula('depth_1',[depth_1]) 
        prompt_dict["Right Height"].set_formula('height_1',[height_1])  
        prompt_dict["Right Floor"].set_formula('floor_1',[floor_1]) 
        prompt_dict["Right Drill Start"].set_formula('drill_start_loc',[drill_start_loc])
        prompt_dict["Right Drill Stop"].set_formula('height_1',[height_1])    
        prompt_dict["Drill From Left"].set_value(False)
        prompt_dict["Drill From One Side"].set_value(True)      

        # left_depth = left_side.add_prompt("Left Depth",'DISTANCE',0)
        # left_depth.set_formula('0',[])     
        # left_height = left_side.add_prompt("Left Height",'DISTANCE',0) 
        # left_height.set_formula('0',[])   
        # left_floor = left_side.add_prompt("Left Floor",'CHECKBOX',0)     
        # left_floor.set_formula('False',[])     
        # left_drill_start = left_side.add_prompt("Left Drill Start",'DISTANCE',0)
        # left_drill_start.set_formula('0',[])  
        # left_drill_stop = left_side.add_prompt("Left Drill Stop",'DISTANCE',0)
        # left_drill_stop.set_formula('0',[])  

        # right_depth = left_side.add_prompt("Right Depth",'DISTANCE',0)
        # right_depth.set_formula('depth_1',[depth_1])  
        # right_height = left_side.add_prompt("Right Height",'DISTANCE',0)   
        # right_height.set_formula('height_1',[height_1])  
        # right_floor = left_side.add_prompt("Right Floor",'CHECKBOX',0)   
        # right_floor.set_formula('floor_1',[floor_1])   
        # right_drill_start = left_side.add_prompt("Right Drill Start",'DISTANCE',0)
        # right_drill_start.set_formula('drill_start_loc',[drill_start_loc]) 
        # right_drill_stop = left_side.add_prompt("Right Drill Stop",'DISTANCE',0)
        # right_drill_stop.set_formula('height_1',[height_1])  

        # drill_from_one_side = left_side.add_prompt("Drill From One Side",'CHECKBOX',True)
        # is_left_end_panel = left_side.add_prompt("Is Left End Panel",'CHECKBOX',True)
        # drill_from_left = left_side.add_prompt("Drill From Left",'CHECKBOX',False)  

        bpy.context.view_layer.update()

        # self.add_left_blind_parts()

        previous_panel = None
        for i in range(1,self.opening_qty):
            if previous_panel == None:
                previous_panel = self.add_panel(i,left_side)
                self.panels.append(previous_panel)
            else:
                previous_panel = self.add_panel(i,previous_panel)
                self.panels.append(previous_panel)

        right_side = assemblies_cabinet.add_closet_part(self)
        hb_props = utils_cabinet.get_object_props(right_side.obj_bp)
        hb_props.ebl1 = True           
        right_side.obj_bp["IS_PANEL_BP"] = True
        right_side.set_name('Closet Partition')
        right_side.loc_x('width-right_filler',[width,right_filler])
        right_side.loc_y(value = 0)
        right_side.loc_z('IF(floor_last,0,height-height_last-IF(ep,ea,0))',[floor_last,height,height_last,ep,ea])
        right_side.rot_y(value=math.radians(-90))
        right_side.rot_z(value=0)
        right_side.dim_x('height_last+IF(floor_last,0,IF(ep,ea,0))',[height_last,floor_last,ep,ea])
        right_side.dim_y('-depth_last',[depth_last])
        right_side.dim_z('panel_thickness_var',[panel_thickness_var])
        pc_utils.flip_normals(right_side)
        self.panels.append(right_side)
        is_finished = right_side.add_prompt("Is Finished",'CHECKBOX',False)
        is_finished.set_formula('rfe',[rfe])
        right_side.add_prompt("Is Right End Panel",'CHECKBOX',True)        

        prompt_dict = self.add_panel_prompts(right_side)
        prompt_dict["Left Depth"].set_formula('depth_last',[depth_last]) 
        prompt_dict["Left Height"].set_formula('height_last',[height_last])   
        prompt_dict["Left Floor"].set_formula('floor_last',[floor_last])
        prompt_dict["Left Drill Start"].set_formula("drill_start_loc",[drill_start_loc])
        prompt_dict["Left Drill Stop"].set_formula('height_last',[height_last])  
        prompt_dict["Right Depth"].set_formula('0',[]) 
        prompt_dict["Right Height"].set_formula('0',[])  
        prompt_dict["Right Floor"].set_formula('False',[]) 
        prompt_dict["Right Drill Start"].set_formula('0',[])
        prompt_dict["Right Drill Stop"].set_formula('0',[])    
        prompt_dict["Drill From Left"].set_value(True)
        prompt_dict["Drill From One Side"].set_value(True)    

        # left_depth = right_side.add_prompt("Left Depth",'DISTANCE',0)
        # left_depth.set_formula('depth_last',[depth_last])     
        # left_height = right_side.add_prompt("Left Height",'DISTANCE',0) 
        # left_height.set_formula('height_last',[height_last])   
        # left_floor = right_side.add_prompt("Left Floor",'CHECKBOX',0)
        # left_floor.set_formula('floor_last',[floor_last])  
        # left_drill_start = right_side.add_prompt("Left Drill Start",'DISTANCE',0)
        # left_drill_start.set_formula("drill_start_loc",[drill_start_loc]) 
        # left_drill_stop = right_side.add_prompt("Left Drill Stop",'DISTANCE',0)
        # left_drill_stop.set_formula('height_last',[height_last])  

        # right_depth = right_side.add_prompt("Right Depth",'DISTANCE',0)
        # right_depth.set_formula('0',[])  
        # right_height = right_side.add_prompt("Right Height",'DISTANCE',0)   
        # right_height.set_formula('0',[])  
        # right_floor = right_side.add_prompt("Right Floor",'CHECKBOX',0)   
        # right_floor.set_formula('False',[])   
        # right_drill_start = right_side.add_prompt("Right Drill Start",'DISTANCE',0)
        # right_drill_start.set_formula('0',[])  
        # right_drill_stop = right_side.add_prompt("Right Drill Stop",'DISTANCE',0)
        # right_drill_stop.set_formula('0',[])  

        # drill_from_one_side = right_side.add_prompt("Drill From One Side",'CHECKBOX',True)
        # is_right_end_panel = right_side.add_prompt("Is Right End Panel",'CHECKBOX',True)
        # drill_from_left = right_side.add_prompt("Drill From Left",'CHECKBOX',True)  

        bpy.context.view_layer.update()

        for index, panel in enumerate(self.panels):
            if index + 1 < len(self.panels):
                self.add_top_and_bottom_shelf(index + 1,panel,self.panels[index+1])
                kick = self.add_toe_kick(index + 1,panel,self.panels[index+1])
                opening = self.add_opening(index + 1,panel,self.panels[index+1])
                if props.show_closet_panel_drilling:
                    system_holes = self.add_system_holes(index + 1,panel,self.panels[index+1])

        if self.is_base:
            self.add_countertop()

        calculator = self.get_calculator('Opening Calculator')
        bpy.context.view_layer.update()
        calculator.calculate()
        print("Closet: Draw Time --- %s seconds ---" % (time.time() - start_time))

    def render(self):
        self.create_assembly()
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.obj_x.location.x = pc_unit.inch(96)
        self.obj_y.location.y = -props.default_closet_depth
        if self.is_base:
            self.obj_z.location.z = pc_unit.millimeter(819)
        else:
            self.obj_z.location.z = pc_unit.millimeter(2131)
        self.draw()


class Closet_Inside_Corner(Closet):
    show_in_library = True
    # category_name = "CLOSETS"
    # subcategory_name = "STARTERS"
    # catalog_name = "_Sample"

    style = 'PIE' # PIE, DIAGONAL, CURVED  

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)
        if obj_bp:
            pass

    def pre_draw(self):
        self.create_assembly()
        props = utils_cabinet.get_scene_props(bpy.context.scene)

        if self.is_hanging:
            self.obj_x.location.x = props.upper_inside_corner_size
            self.obj_z.location.z = props.upper_cabinet_height
            self.obj_y.location.y = -props.upper_inside_corner_size
        elif self.is_base:
            self.obj_x.location.x = props.base_inside_corner_size
            self.obj_z.location.z = props.base_cabinet_height
            self.obj_y.location.y = -props.base_inside_corner_size
        else:
            self.obj_x.location.x = props.tall_inside_corner_size
            self.obj_z.location.z = props.tall_cabinet_height
            self.obj_y.location.y = -props.tall_inside_corner_size

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = assemblies_cabinet.add_closet_part(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        self.obj_bp[const.CLOSET_INSIDE_CORNER_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.inside_corner_cabinet_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_closets_corner_commands"
        self.obj_y['IS_MIRROR'] = True

        props = utils_cabinet.get_scene_props(bpy.context.scene)

        prompts_cabinet.add_closet_thickness_prompts(self)
        
        if self.is_hanging:
            depth = props.upper_cabinet_depth
        elif self.is_base:
            depth = props.base_cabinet_depth
        else:
            depth = props.tall_cabinet_depth

        self.add_prompt("Drill Start Location",'DISTANCE',pc_unit.inch(.35))
        self.add_prompt("Back Width",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Left Depth",'DISTANCE',depth)
        self.add_prompt("Right Depth",'DISTANCE',depth)
        self.add_prompt("Shelf Wall Offset Amount",'DISTANCE',pc_unit.inch(.5))
        # self.add_prompt("Shelf Quantity",'QUANTITY',3) 
        # self.add_prompt("Is Hanging",'CHECKBOX',self.is_hanging) 
        
        # self.add_prompt("Use Square Notch Top Shelf",'CHECKBOX',False) 
        self.add_prompt("Flip Back Support Location",'CHECKBOX',False) 
        # self.add_prompt("Panel Height",'DISTANCE',pc_unit.millimeter(int(props.hanging_closet_panel_height)))

        if self.is_base:
            prompts_cabinet.add_countertop_prompts(self)
            self.add_prompt("Add Countertop",'CHECKBOX',self.is_base) 
            self.add_prompt("Countertop Thickness",'DISTANCE',pc_unit.inch(1.5)) 

        if not self.is_hanging:
            prompts_cabinet.add_closet_toe_kick_prompts(self)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        left_depth_var = self.get_prompt("Left Depth").get_var('left_depth_var')
        right_depth_var = self.get_prompt("Right Depth").get_var('right_depth_var')

        back_width_var = self.get_prompt("Back Width").get_var('back_width_var')
        # p_height = self.get_prompt("Panel Height").get_var('p_height')
        # is_hang = self.get_prompt("Is Hanging").get_var('is_hang')
        panel_thickness_var = self.get_prompt("Panel Thickness").get_var("panel_thickness_var")
        st = self.get_prompt("Shelf Thickness").get_var("st") 
        # qty = self.get_prompt("Shelf Quantity").get_var("qty")
        flip_back_support = self.get_prompt("Flip Back Support Location").get_var("flip_back_support")
        shelf_wall_offset = self.get_prompt("Shelf Wall Offset Amount").get_var("shelf_wall_offset")
        # use_square_notch_top_shelf = self.get_prompt("Use Square Notch Top Shelf").get_var("use_square_notch_top_shelf")
        # drill_start_loc = self.get_prompt("Drill Start Location").get_var("drill_start_loc")

        left_side = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(left_side.obj_bp)
        props.ebl1 = True               
        left_side.obj_bp["IS_PANEL_BP"] = True
        left_side.set_name('Closet Partition')
        left_side.loc_x(value = 0)
        left_side.loc_y('depth',[depth])
        left_side.loc_z(value = 0)
        left_side.rot_y(value=math.radians(-90))
        left_side.rot_z(value=math.radians(-90))
        left_side.dim_x('height',[height])
        left_side.dim_y('left_depth_var',[left_depth_var])
        left_side.dim_z('panel_thickness_var',[panel_thickness_var])

        # prompt_dict = self.add_panel_prompts(left_side)
        # prompt_dict["Left Depth"].set_formula('left_depth_var',[left_depth_var]) 
        # prompt_dict["Left Height"].set_formula('IF(is_hang,p_height,height)',[is_hang,p_height,height])   
        # prompt_dict["Left Floor"].set_formula('IF(is_hang,False,True)',[is_hang]) 
        # prompt_dict["Left Drill Start"].set_formula("drill_start_loc",[drill_start_loc])
        # prompt_dict["Left Drill Stop"].set_formula('IF(is_hang,p_height,height)',[is_hang,p_height,height])    
        # prompt_dict["Right Depth"].set_formula('0',[]) 
        # prompt_dict["Right Height"].set_formula('0',[])  
        # prompt_dict["Right Floor"].set_formula('0',[]) 
        # prompt_dict["Right Drill Start"].set_formula("0",[])
        # prompt_dict["Right Drill Stop"].set_formula('0',[])     
        # prompt_dict["Drill From Left"].set_value(True)
        # prompt_dict["Drill From One Side"].set_value(True)    

        back = assemblies_cabinet.add_closet_part(self)
        back.obj_bp["IS_PANEL_BP"] = True
        props = utils_cabinet.get_object_props(back.obj_bp)
        props.ebl1 = True           
        back.set_name('Back Support')
        back.loc_x('shelf_wall_offset',[shelf_wall_offset])
        back.loc_y('IF(flip_back_support,-back_width_var,0)-shelf_wall_offset',[flip_back_support,back_width_var,shelf_wall_offset])
        back.loc_z('st',[st])
        back.rot_y(value=math.radians(-90))
        back.rot_z('IF(flip_back_support,0,radians(-90))',[flip_back_support])
        back.dim_x('height-(st*2)',[height,st])
        back.dim_y('back_width_var',[back_width_var])
        back.dim_z('-panel_thickness_var',[panel_thickness_var])
        pc_utils.flip_normals(back)

        # prompt_dict = self.add_panel_prompts(back)
        # prompt_dict["Left Depth"].set_formula('0',[])
        # prompt_dict["Left Height"].set_formula('0',[])   
        # prompt_dict["Left Floor"].set_formula('0',[])  
        # prompt_dict["Left Drill Start"].set_formula("0",[])
        # prompt_dict["Left Drill Stop"].set_formula('',[])
        # prompt_dict["Right Depth"].set_formula('back_width_var',[back_width_var])
        # prompt_dict["Right Height"].set_formula('IF(is_hang,p_height,height)',[is_hang,p_height,height]) 
        # prompt_dict["Right Floor"].set_formula('IF(is_hang,False,True)',[is_hang])  
        # prompt_dict["Right Drill Start"].set_formula("drill_start_loc",[drill_start_loc])
        # prompt_dict["Right Drill Stop"].set_formula('IF(is_hang,p_height,height)',[is_hang,p_height,height])  
        # prompt_dict["Drill From Left"].set_value(False)
        # prompt_dict["Drill From One Side"].set_value(True) 

        right_side = assemblies_cabinet.add_closet_part(self)
        props = utils_cabinet.get_object_props(right_side.obj_bp)
        props.ebl1 = True           
        right_side.obj_bp["IS_PANEL_BP"] = True
        right_side.set_name('Closet Partition')
        right_side.loc_x('width',[width])
        right_side.loc_y(value = 0)
        right_side.loc_z(value = 0)
        right_side.rot_y(value=math.radians(-90))
        right_side.rot_z(value=math.radians(180))
        right_side.dim_x('height',[height])
        right_side.dim_y('right_depth_var',[right_depth_var])
        right_side.dim_z('-panel_thickness_var',[panel_thickness_var])
        pc_utils.flip_normals(right_side)

        # prompt_dict = self.add_panel_prompts(right_side)
        # prompt_dict["Left Depth"].set_formula('0',[])
        # prompt_dict["Left Height"].set_formula('0',[]) 
        # prompt_dict["Left Floor"].set_formula('0',[]) 
        # prompt_dict["Left Drill Start"].set_formula("0",[])
        # prompt_dict["Left Drill Stop"].set_formula('0',[])
        # prompt_dict["Right Depth"].set_formula('right_depth_var',[right_depth_var])
        # prompt_dict["Right Height"].set_formula('IF(is_hang,p_height,height)',[is_hang,p_height,height]) 
        # prompt_dict["Right Floor"].set_formula('IF(is_hang,False,True)',[is_hang]) 
        # prompt_dict["Right Drill Start"].set_formula("drill_start_loc",[drill_start_loc])
        # prompt_dict["Right Drill Stop"].set_formula('IF(is_hang,p_height,height)',[is_hang,p_height,height])    
        # prompt_dict["Drill From Left"].set_value(False)
        # prompt_dict["Drill From One Side"].set_value(True) 

        bottom = assemblies_cabinet.add_corner_notch_part(self)
        bottom.obj_bp["IS_FIXED_L_SHELF_BP"] = True
        props = utils_cabinet.get_object_props(bottom.obj_bp)
        props.ebl1 = True        
        bottom.set_name('Closet L Shelf')
        bottom.loc_x('shelf_wall_offset',[shelf_wall_offset])
        bottom.loc_y('-shelf_wall_offset',[shelf_wall_offset])
        if self.is_hanging:
            bottom.loc_z(value=0)
        else:
            kick_height = self.get_prompt("Closet Kick Height").get_var('kick_height')       
            bottom.loc_z('kick_height',[kick_height])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(-90))
        bottom.dim_x('fabs(depth)-panel_thickness_var-shelf_wall_offset',[depth,panel_thickness_var,shelf_wall_offset])
        bottom.dim_y('width-panel_thickness_var-shelf_wall_offset',[width,panel_thickness_var,shelf_wall_offset])
        bottom.dim_z('st',[st])
        l_depth = bottom.get_prompt('Left Depth')
        l_depth.set_formula('left_depth_var-shelf_wall_offset',[left_depth_var,shelf_wall_offset])
        r_depth = bottom.get_prompt('Right Depth')
        r_depth.set_formula('right_depth_var-shelf_wall_offset',[right_depth_var,shelf_wall_offset])

        top = assemblies_cabinet.add_corner_notch_part(self)
        top.obj_bp["IS_FIXED_L_SHELF_BP"] = True
        props = utils_cabinet.get_object_props(top.obj_bp)
        props.ebl1 = True         
        top.set_name('Closet L Shelf')
        top.loc_x('shelf_wall_offset',[shelf_wall_offset])
        top.loc_y('-shelf_wall_offset',[shelf_wall_offset])
        top.loc_z('height-st',[height,st])
        top.rot_x(value = 0)
        top.rot_y(value = 0)
        top.rot_z(value = math.radians(-90))
        top.dim_x('fabs(depth)-panel_thickness_var-shelf_wall_offset',[depth,panel_thickness_var,shelf_wall_offset])
        top.dim_y('width-panel_thickness_var-shelf_wall_offset',[width,panel_thickness_var,shelf_wall_offset])
        top.dim_z('st',[st])
        # hide = top.get_prompt('Hide')
        # hide.set_formula('IF(use_square_notch_top_shelf,False,True)',[use_square_notch_top_shelf])        
        l_depth = top.get_prompt('Left Depth')
        l_depth.set_formula('left_depth_var-shelf_wall_offset',[left_depth_var,shelf_wall_offset])
        r_depth = top.get_prompt('Right Depth')
        r_depth.set_formula('right_depth_var-shelf_wall_offset',[right_depth_var,shelf_wall_offset])
        # home_builder_utils.flip_normals(top)

        # top_radius = assemblies_cabinet.add_corner_radius_part(self)
        # top_radius.obj_bp["IS_FIXED_L_SHELF_BP"] = True
        # props = utils_cabinet.get_object_props(top_radius.obj_bp)
        # props.ebl1 = True         
        # top_radius.set_name('Closet L Shelf')
        # top_radius.loc_x('shelf_wall_offset',[shelf_wall_offset])
        # top_radius.loc_y('-shelf_wall_offset',[shelf_wall_offset])
        # top_radius.loc_z('height-st',[height,st])
        # top_radius.rot_x(value = 0)
        # top_radius.rot_y(value = 0)
        # top_radius.rot_z(value = math.radians(-90))
        # top_radius.dim_x('fabs(depth)-panel_thickness_var-shelf_wall_offset',[depth,panel_thickness_var,shelf_wall_offset])
        # top_radius.dim_y('width-panel_thickness_var-shelf_wall_offset',[width,panel_thickness_var,shelf_wall_offset])
        # top_radius.dim_z('st',[st])
        # hide = top_radius.get_prompt('Hide')
        # hide.set_formula('IF(use_square_notch_top_shelf,True,False)',[use_square_notch_top_shelf])
        # l_depth = top_radius.get_prompt('Left Depth')
        # l_depth.set_formula('left_depth_var-shelf_wall_offset',[left_depth_var,shelf_wall_offset])
        # r_depth = top_radius.get_prompt('Right Depth')
        # r_depth.set_formula('right_depth_var-shelf_wall_offset',[right_depth_var,shelf_wall_offset])

        if self.is_base:
            add_ctop = self.get_prompt("Add Countertop").get_var("add_ctop")
            ctop_thickness_var = self.get_prompt("Countertop Thickness").get_var("ctop_thickness_var")
            ctop_overhang_front = self.get_prompt("Countertop Overhang Front").get_var('ctop_overhang_front')
            ctop_overhang_back = self.get_prompt("Countertop Overhang Back").get_var('ctop_overhang_back')
            ctop_overhang_left = self.get_prompt("Countertop Overhang Left").get_var('ctop_overhang_left')
            ctop_overhang_right = self.get_prompt("Countertop Overhang Right").get_var('ctop_overhang_right')

            c_top = assemblies_cabinet.add_corner_notch_countertop_part(self)
            c_top.set_name('Closet L Shelf')
            c_top.loc_x(value = 0)
            c_top.loc_y(value = 0)
            c_top.loc_z('height',[height])
            c_top.rot_x(value = 0)
            c_top.rot_y(value = 0)
            c_top.rot_z(value = math.radians(-90))
            c_top.dim_x('fabs(depth)',[depth])
            c_top.dim_y('width',[width])
            c_top.dim_z('ctop_thickness_var',[ctop_thickness_var])
            l_depth = c_top.get_prompt('Left Depth')
            l_depth.set_formula('left_depth_var+ctop_overhang_front',[left_depth_var,ctop_overhang_front])
            r_depth = c_top.get_prompt('Right Depth')
            r_depth.set_formula('right_depth_var+ctop_overhang_front',[right_depth_var,ctop_overhang_front])
            hide = c_top.get_prompt("Hide")
            hide.set_formula('IF(add_ctop,False,True)',[add_ctop])

        if not self.is_hanging:
            kick_setback = self.get_prompt("Closet Kick Setback").get_var('kick_setback')    

            left_kick = assemblies_cabinet.add_closet_part(self)
            left_kick.obj_bp["IS_TOE_KICK_BP"] = True
            left_kick.set_name('Left Kick')
            left_kick.loc_x('left_depth_var-kick_setback',[left_depth_var,kick_setback])
            left_kick.loc_y('depth+panel_thickness_var',[depth,panel_thickness_var])
            left_kick.loc_z(value = 0)
            left_kick.rot_x(value=math.radians(90))
            left_kick.rot_y(value=0)
            left_kick.rot_z(value=math.radians(90))
            left_kick.dim_x('fabs(depth)-(panel_thickness_var*2)',[depth,panel_thickness_var])
            left_kick.dim_y('kick_height',[kick_height])
            left_kick.dim_z('panel_thickness_var',[panel_thickness_var])

            right_kick = assemblies_cabinet.add_closet_part(self)
            right_kick.obj_bp["IS_TOE_KICK_BP"] = True
            right_kick.set_name('Right Kick')
            right_kick.loc_x('width-panel_thickness_var',[width,panel_thickness_var])
            right_kick.loc_y('-right_depth_var+kick_setback',[right_depth_var,kick_setback])
            right_kick.loc_z(value = 0)
            right_kick.rot_x(value=math.radians(90))
            right_kick.rot_y(value=0)
            right_kick.rot_z(value=math.radians(180))
            right_kick.dim_x('width-left_depth_var-(panel_thickness_var*2)+kick_setback',[width,left_depth_var,kick_setback,panel_thickness_var])
            right_kick.dim_y('kick_height',[kick_height])
            right_kick.dim_z('panel_thickness_var',[panel_thickness_var])

        # b_loc = bottom.obj_bp.pyclone.get_var('location.z','b_loc')
        # t_loc = top.obj_bp.pyclone.get_var('location.z','t_loc')

        # shelf = assemblies_cabinet.add_corner_radius_part(self)
        # shelf.obj_bp["IS_ADJ_L_SHELF_BP"] = True
        # props = utils_cabinet.get_object_props(shelf.obj_bp)
        # props.ebl1 = True  
        # props.ebl2 = True 
        # props.ebw1 = True 
        # props.ebw2 = True             
        # shelf.set_name('Closet L Shelf')
        # shelf.loc_x('shelf_wall_offset',[shelf_wall_offset])
        # shelf.loc_y('-shelf_wall_offset',[shelf_wall_offset])
        # shelf.loc_z('b_loc+st+(((t_loc-b_loc-(st*2)-(st*qty)))/(qty+1))',[b_loc,t_loc,kick_height,st,height,qty])
        # shelf.rot_x(value = 0)
        # shelf.rot_y(value = 0)
        # shelf.rot_z(value = math.radians(-90))
        # shelf.dim_x('fabs(depth)-panel_thickness_var-shelf_wall_offset',[depth,panel_thickness_var,shelf_wall_offset])
        # shelf.dim_y('width-panel_thickness_var-shelf_wall_offset',[width,panel_thickness_var,shelf_wall_offset])
        # shelf.dim_z('st',[st])
        # l_depth = shelf.get_prompt('Left Depth')
        # l_depth.set_formula('left_depth_var-shelf_wall_offset',[left_depth_var,shelf_wall_offset])
        # r_depth = shelf.get_prompt('Right Depth')
        # r_depth.set_formula('right_depth_var-shelf_wall_offset',[right_depth_var,shelf_wall_offset])
        # quantity = shelf.get_prompt('Z Quantity')
        # quantity.set_formula('qty',[qty])
        # offset = shelf.get_prompt('Z Offset')
        # offset.set_formula('((t_loc-b_loc-(st*2)-(st*qty))/(qty+1))+st',[t_loc,b_loc,st,qty])

    def render(self):
        self.create_assembly()
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.obj_x.location.x = pc_unit.inch(24)
        self.obj_y.location.y = -pc_unit.inch(24)  
        self.obj_z.location.z = pc_unit.millimeter(2131)
        self.draw()


class Closet_Inside_Corner_Filler(Closet):
    show_in_library = True
    # category_name = "CLOSETS"
    # subcategory_name = "STARTERS"
    # catalog_name = "_Sample"

    style = 'PIE' # PIE, DIAGONAL, CURVED  

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)
        if obj_bp:
            pass

    def pre_draw(self):
        self.create_assembly()
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        # self.obj_x.location.x = props.default_base_closet_depth + pc_unit.inch(1.5)
        # self.obj_y.location.y = -props.default_base_closet_depth - pc_unit.inch(1.5)
        # self.obj_z.location.z = pc_unit.millimeter(int(props.base_closet_panel_height))

        if self.is_hanging:
            self.obj_x.location.x = props.upper_cabinet_depth + pc_unit.inch(1.5)
            self.obj_z.location.z = props.upper_cabinet_height
            self.obj_y.location.y = -props.upper_cabinet_depth - pc_unit.inch(1.5)
        elif self.is_base:
            self.obj_x.location.x = props.base_cabinet_depth + pc_unit.inch(1.5)
            self.obj_z.location.z = props.base_cabinet_height
            self.obj_y.location.y = -props.base_cabinet_depth - pc_unit.inch(1.5)
        else:
            self.obj_x.location.x = props.tall_cabinet_depth + pc_unit.inch(1.5)
            self.obj_z.location.z = props.tall_cabinet_height
            self.obj_y.location.y = -props.tall_cabinet_depth - pc_unit.inch(1.5)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = assemblies_cabinet.add_closet_part(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        self.obj_bp[const.CLOSET_INSIDE_CORNER_TAG] = True
        # self.obj_bp['IS_CLOSET_INSIDE_CORNER_BP'] = True
        self.obj_bp["IS_BASE_BP"] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.inside_corner_cabinet_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_closets_corner_commands"
        self.obj_y['IS_MIRROR'] = True

        props = utils_cabinet.get_scene_props(bpy.context.scene)

        prompts_cabinet.add_closet_thickness_prompts(self)

        self.add_prompt("Left Filler Width",'DISTANCE',pc_unit.inch(1.5))
        self.add_prompt("Right Filler Width",'DISTANCE',pc_unit.inch(1.5))        
        self.add_prompt("Countertop Thickness",'DISTANCE',pc_unit.inch(1.5)) 
        self.add_prompt("Is Hanging",'CHECKBOX',self.is_hanging) 
        self.add_prompt("Panel Height",'DISTANCE',pc_unit.millimeter(int(props.hanging_closet_panel_height)))

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        p_height = self.get_prompt("Panel Height").get_var('p_height')
        is_hang = self.get_prompt("Is Hanging").get_var('is_hang')
        lf_width = self.get_prompt("Left Filler Width").get_var('lf_width')
        rf_width = self.get_prompt("Right Filler Width").get_var('rf_width')
        ctop_thickness_var = self.get_prompt("Countertop Thickness").get_var('ctop_thickness_var')
        panel_thickness_var = self.get_prompt("Panel Thickness").get_var("panel_thickness_var")
        st = self.get_prompt("Shelf Thickness").get_var("st") 

        left_filler = assemblies_cabinet.add_closet_part(self)
        left_filler.set_name('Closet Partition')
        left_filler.loc_x('width-rf_width',[width,rf_width])
        left_filler.loc_y('depth',[depth])
        left_filler.loc_z('IF(is_hang,height-p_height,0)',[is_hang,height,p_height])
        left_filler.rot_y(value=math.radians(-90))
        left_filler.rot_z(value=math.radians(0))
        left_filler.dim_x('IF(is_hang,p_height,height)',[is_hang,height,p_height])
        left_filler.dim_y('lf_width',[lf_width])
        left_filler.dim_z('panel_thickness_var',[panel_thickness_var])

        right_filler = assemblies_cabinet.add_closet_part(self)
        right_filler.set_name('Closet Partition')
        right_filler.loc_x('width',[width])
        right_filler.loc_y('depth+lf_width',[depth,lf_width])
        right_filler.loc_z('IF(is_hang,height-p_height,0)',[is_hang,height,p_height])
        right_filler.rot_y(value=math.radians(-90))
        right_filler.rot_z(value=math.radians(90))
        right_filler.dim_x('IF(is_hang,p_height,height)',[is_hang,height,p_height])
        right_filler.dim_y('rf_width+panel_thickness_var',[rf_width,panel_thickness_var])
        right_filler.dim_z('-panel_thickness_var',[panel_thickness_var])
        pc_utils.flip_normals(right_filler)

        top = assemblies_cabinet.add_corner_notch_countertop_part(self)
        top.set_name('Closet L Shelf')
        top.loc_x(value = 0)
        top.loc_y(value = 0)
        top.loc_z('height',[height])
        top.rot_x(value = 0)
        top.rot_y(value = 0)
        top.rot_z(value = math.radians(-90))
        top.dim_x('fabs(depth)',[depth])
        top.dim_y('width',[width])
        top.dim_z('ctop_thickness_var',[ctop_thickness_var])
        l_depth = top.get_prompt('Left Depth')
        l_depth.set_formula('width',[width,rf_width])
        r_depth = top.get_prompt('Right Depth')
        r_depth.set_formula('fabs(depth)',[depth,rf_width])

    def render(self):
        self.create_assembly()
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.obj_x.location.x = pc_unit.inch(24)
        self.obj_y.location.y = -pc_unit.inch(24)  
        self.obj_z.location.z = pc_unit.millimeter(691)
        self.draw()