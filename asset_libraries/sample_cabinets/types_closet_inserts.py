import bpy
import time
import math
from os import path
from pc_lib import pc_types, pc_unit, pc_utils

from . import assemblies_cabinet
from . import utils_cabinet
from . import paths_cabinet
from . import material_pointers_cabinet
from . import prompts_cabinet

class Closet_Insert(pc_types.Assembly):
    
    def add_closet_insert_prompts(self):
        self.add_prompt("Left Depth",'DISTANCE',0) 
        self.add_prompt("Right Depth",'DISTANCE',0)         
        self.add_prompt("Back Inset",'DISTANCE',0)  

    def add_opening(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        left_depth = self.get_prompt("Left Depth").get_var("left_depth")
        right_depth = self.get_prompt("Right Depth").get_var("right_depth")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        opening = assemblies_cabinet.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('width',[width])
        opening.dim_y('depth-back_inset',[depth,back_inset])
        left_depth_p = opening.get_prompt("Left Depth")
        left_depth_p.set_formula('left_depth',[left_depth])
        right_depth_p = opening.get_prompt("Right Depth")
        right_depth_p.set_formula('right_depth',[right_depth])
        return opening


class Shelves(Closet_Insert):

    def add_shelves(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        shelf_qty = self.get_prompt("Shelf Quantity").get_var("shelf_qty")
        shelf_clip_gap = self.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
        shelf_thickness = self.get_prompt("Shelf Thickness").get_var("shelf_thickness")
        left_depth = self.get_prompt("Left Depth").get_var("left_depth")
        right_depth = self.get_prompt("Right Depth").get_var("right_depth")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        adj_shelf = assemblies_cabinet.add_closet_array_part(self)
        adj_shelf.obj_bp['IS_ADJ_SHELF'] = True
        adj_shelf.set_name("Adj Shelf")
        props = utils_cabinet.get_object_props(adj_shelf.obj_bp)
        props.ebl1 = True          
        props.ebl2 = True  
        props.ebw1 = True  
        props.ebw2 = True        
        is_locked_shelf = adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',False)
        is_lock_shelf_var = is_locked_shelf.get_var("is_lock_shelf_var")
        adj_shelf_setback = adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',hb_props.adj_shelf_setback)
        adj_shelf_setback_var = adj_shelf_setback.get_var("adj_shelf_setback_var")
        fixed_shelf_setback = adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',hb_props.fixed_shelf_setback)
        fixed_shelf_setback_var = fixed_shelf_setback.get_var("fixed_shelf_setback_var")
        l_depth = adj_shelf.get_prompt("Left Depth")
        r_depth = adj_shelf.get_prompt("Right Depth")

        adj_shelf.loc_x('IF(is_lock_shelf_var,0,shelf_clip_gap)',[shelf_clip_gap,is_lock_shelf_var])
        adj_shelf.loc_y('depth-back_inset',[depth,back_inset])
        adj_shelf.loc_z('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))',[height,shelf_thickness,shelf_qty])
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('width-IF(is_lock_shelf_var,0,shelf_clip_gap*2)',[width,is_lock_shelf_var,shelf_clip_gap])
        adj_shelf.dim_y('-depth+IF(is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var)+back_inset',[depth,back_inset,is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var])
        adj_shelf.dim_z('shelf_thickness',[shelf_thickness])
        pc_utils.flip_normals(adj_shelf)
        hide = adj_shelf.get_prompt("Hide")
        hide.set_formula('IF(shelf_qty==0,True,False)',[shelf_qty])
        z_quantity = adj_shelf.get_prompt("Z Quantity")
        z_offset = adj_shelf.get_prompt("Z Offset")

        l_depth.set_formula('left_depth',[left_depth]) 
        r_depth.set_formula('right_depth',[right_depth]) 
        z_quantity.set_formula('shelf_qty',[shelf_qty]) 
        z_offset.set_formula('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))+shelf_thickness',[height,shelf_thickness,shelf_qty]) 

    def pre_draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()
        self.obj_bp["IS_SHELVES_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_shelves_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

    def draw(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75)) 
        self.add_prompt("Shelf Clip Gap",'DISTANCE',hb_props.shelf_clip_gap) 
        self.add_prompt("Shelf Quantity",'QUANTITY',3) 

        self.add_shelves()

    def render(self):
        self.pre_draw()
        self.draw()


class Hanging_Rod(Closet_Insert):

    is_double = False

    def add_hanging_rod(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        hanging_rod_setback = self.get_prompt("Hanging Rod Setback").get_var("hanging_rod_setback")

        hanging_rod = assemblies_cabinet.add_closet_oval_hanging_rod(self)
        hangers = assemblies_cabinet.add_closet_hangers(self)

        hanging_rod.loc_x(value = 0)
        hanging_rod.loc_y('hanging_rod_setback',[hanging_rod_setback])
        hanging_rod.rot_x(value = 0)
        hanging_rod.rot_y(value = 0)
        hanging_rod.rot_z(value = 0)
        hanging_rod.dim_x('width',[width])
        hanging_rod.dim_y(value = 0)
        hanging_rod.dim_z(value = 0)

        loc_z = hanging_rod.obj_bp.pyclone.get_var('location.z','loc_z')

        if hangers:
            hangers.loc_x(value = 0)
            hangers.loc_y('hanging_rod_setback',[hanging_rod_setback])
            hangers.loc_z('loc_z',[loc_z])
            hangers.rot_x(value = 0)
            hangers.rot_y(value = 0)
            hangers.rot_z(value = 0)
            hangers.dim_x('width',[width])
            hangers.dim_y(value = 0)
            hangers.dim_z(value = 0)  
        return hanging_rod      

    def draw(self):      
        self.create_assembly()
        self.add_closet_insert_prompts()      
        self.obj_bp["IS_HANGING_RODS_BP"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.hanging_rod_prompts"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        self.add_prompt("Hanging Rod Location From Top",'DISTANCE',pc_unit.inch(2.145)) 
        self.add_prompt("Hanging Rod Setback",'DISTANCE',pc_unit.inch(2)) 
        self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75)) 

        height = self.obj_z.pyclone.get_var('location.z','height')
        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        hanging_rod_location_from_top = self.get_prompt("Hanging Rod Location From Top").get_var("hanging_rod_location_from_top")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        rod = self.add_hanging_rod()
        rod.loc_z('height-hanging_rod_location_from_top',[height,hanging_rod_location_from_top])

        if self.is_double:
            self.add_prompt("Top Opening Height",'DISTANCE',pc_unit.inch(38)) 
            top_opening_height = self.get_prompt("Top Opening Height").get_var("top_opening_height")

            rod = self.add_hanging_rod()
            rod.loc_z('height-top_opening_height-hanging_rod_location_from_top-s_thickness',[height,top_opening_height,hanging_rod_location_from_top,s_thickness])

            #MID SHELF
            shelf = assemblies_cabinet.add_closet_part(self)
            props = utils_cabinet.get_object_props(shelf.obj_bp)
            props.ebl1 = True                           
            shelf.obj_bp["IS_SHELF_BP"] = True
            shelf.obj_bp['ADD_DIMENSION'] = True
            shelf.set_name('Shelf')
            shelf.loc_x(value = 0)
            shelf.loc_y(value = 0)
            shelf.loc_z('height-top_opening_height-s_thickness',[height,top_opening_height,s_thickness])
            shelf.rot_y(value = 0)
            shelf.rot_z(value = 0)
            shelf.dim_x('x',[x])
            shelf.dim_y('y-back_inset',[y,back_inset])
            shelf.dim_z('s_thickness',[s_thickness])
            pc_utils.flip_normals(shelf)

            top_opening = self.add_opening()
            top_opening.set_name('Top Opening')
            top_opening.loc_z('height-top_opening_height',
                              [height,top_opening_height])
            top_opening.dim_z('top_opening_height',[top_opening_height])            

            bot_opening = self.add_opening()
            bot_opening.set_name('Bottom Opening')
            bot_opening.loc_z(value = 0)
            bot_opening.dim_z('height-top_opening_height-s_thickness',
                              [height,top_opening_height,s_thickness])           
      
        else:
            opening = self.add_opening()
            opening.set_name('Opening')
            opening.loc_z(value = 0)
            opening.dim_z('height',[height])    


class Slanted_Shoe_Shelf(Closet_Insert):

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()    
        self.obj_bp["IS_SHOE_SHELVES_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_shoe_shelf_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75)) 
        self.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(1)) 
        self.add_prompt("Shelf Setback",'DISTANCE',pc_unit.inch(0))
        self.add_prompt("Shelf Lip Width",'DISTANCE',pc_unit.inch(2))
        self.add_prompt("Metal Lip Width Inset",'DISTANCE',pc_unit.millimeter(19))
        self.add_prompt("Distance Between Shelves",'DISTANCE',pc_unit.inch(8))
        self.add_prompt("Space From Bottom",'DISTANCE',pc_unit.inch(0))
        self.add_prompt("Shelf Quantity",'QUANTITY',3) 
        self.add_prompt("Shelf Angle",'ANGLE',17.25) 
        self.add_prompt("Turn Off Top Shelf",'CHECKBOX',True)
        self.add_prompt("Accessory Name",'TEXT',"")

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        qty = self.get_prompt("Shelf Quantity").get_var("qty")
        lip_width = self.get_prompt("Shelf Lip Width").get_var('lip_width')
        bot_space = self.get_prompt("Space From Bottom").get_var('bot_space')
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        angle = self.get_prompt("Shelf Angle").get_var("angle")
        setback = self.get_prompt("Shelf Setback").get_var("setback")
        dim_between_shelves = self.get_prompt("Distance Between Shelves").get_var('dim_between_shelves')
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")
        metal_width_inset = self.get_prompt("Metal Lip Width Inset").get_var("metal_width_inset")
        turn_off_top_shelf = self.get_prompt("Turn Off Top Shelf").get_var("turn_off_top_shelf")

        #TOP SHELF
        shelf = assemblies_cabinet.add_closet_part(self)     
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Top Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('bot_space+dim_between_shelves*qty',[bot_space,dim_between_shelves,qty])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('width',[width])
        shelf.dim_y('depth-back_inset',[depth,back_inset])
        shelf.dim_z('s_thickness',[s_thickness])
        hide = shelf.get_prompt("Hide")
        hide.set_formula('turn_off_top_shelf',[turn_off_top_shelf])        

        z_loc = shelf.obj_bp.pyclone.get_var('location.z','z_loc')

        opening = self.add_opening()
        opening.loc_z('min(height,z_loc+s_thickness)',[height,z_loc,s_thickness])
        opening.dim_z('max(0,height-z_loc-s_thickness)',[height,z_loc,s_thickness])

        for i in range(1,11):
            slanted_shelf = assemblies_cabinet.add_closet_array_part(self)        
            slanted_shelf.set_name("Slanted Shelf")
            slanted_shelf.obj_bp['IS_SLANTED_SHOE_SHELF'] = True
            slanted_shelf.loc_x(value = 0)
            slanted_shelf.loc_y('depth-back_inset',[depth,back_inset])
            if i == 1:
                slanted_shelf.loc_z('((fabs(depth)-back_inset)*sin(angle))+bot_space',[depth,back_inset,angle,bot_space])
            else:
                slanted_shelf.loc_z('(((fabs(depth)-back_inset)*sin(angle))+bot_space)+dim_between_shelves*' + str(i-1),[depth,back_inset,angle,bot_space,dim_between_shelves])
            slanted_shelf.rot_x('angle',[angle])
            slanted_shelf.rot_y(value = 0)
            slanted_shelf.rot_z(value = 0)
            slanted_shelf.dim_x('width',[width])
            slanted_shelf.dim_y('-depth+setback+back_inset',[depth,setback,back_inset])
            slanted_shelf.dim_z('s_thickness',[s_thickness])
            hide = slanted_shelf.get_prompt('Hide')
            hide.set_formula('IF(' + str(i) + '>qty,True,False)',[qty])
            pc_utils.flip_normals(slanted_shelf)

            shelf_depth = slanted_shelf.obj_y.pyclone.get_var('location.y','shelf_depth')
            z_loc = slanted_shelf.obj_bp.pyclone.get_var('location.z','z_loc')

            shelf_lip = assemblies_cabinet.add_metal_shoe_shelf_part(slanted_shelf)
            shelf_lip.set_name("Shelf Lip")
            shelf_lip.loc_x('metal_width_inset',[metal_width_inset])
            shelf_lip.loc_y('-depth+back_inset+.02',[depth,back_inset])
            shelf_lip.loc_z('s_thickness',[s_thickness])
            shelf_lip.rot_y(value = 0)
            shelf_lip.rot_z(value = 0)
            shelf_lip.dim_x('width-metal_width_inset*2',[width,metal_width_inset])
            hide = shelf_lip.get_prompt('Hide')
            hide.set_formula('IF(' + str(i) + '>qty,True,False)',[qty])


class Cubbies(Closet_Insert):

    def draw(self):      
        self.create_assembly()
        self.add_closet_insert_prompts()        
        self.obj_bp["IS_CUBBY_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_cubby_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        self.add_prompt("Cubby Placement",'COMBOBOX',0,["Bottom","Top","Fill"])
        self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        self.add_prompt("Divider Thickness",'DISTANCE',pc_unit.inch(1)) 
        self.add_prompt("Horizontal Quantity",'QUANTITY',2) 
        self.add_prompt("Vertical Quantity",'QUANTITY',2) 
        self.add_prompt("Cubby Setback",'DISTANCE',pc_unit.inch(.25)) 
        self.add_prompt("Cubby Height",'DISTANCE',pc_unit.millimeter(556.95)) 
        
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        placement = self.get_prompt("Cubby Placement").get_var('placement')
        c_height = self.get_prompt("Cubby Height").get_var('c_height')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')
        d_thickness = self.get_prompt("Divider Thickness").get_var('d_thickness')
        h_qty = self.get_prompt("Horizontal Quantity").get_var('h_qty')
        v_qty = self.get_prompt("Vertical Quantity").get_var('v_qty')
        setback = self.get_prompt("Cubby Setback").get_var('setback')
        # left_depth = self.get_prompt("Left Depth").get_var("left_depth")
        # right_depth = self.get_prompt("Right Depth").get_var("right_depth")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        #TOP SHELF
        shelf = assemblies_cabinet.add_closet_part(self)                        
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Cubby Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('IF(placement==0,c_height+s_thickness,height-c_height)',[placement,c_height,height,s_thickness])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('width',[width])
        shelf.dim_y('depth-back_inset',[depth,back_inset])
        shelf.dim_z('-s_thickness',[s_thickness])
        hide = shelf.get_prompt('Hide')
        hide.set_formula('IF(placement==2,True,False)',[placement])
        pc_utils.flip_normals(shelf)
        # left_depth_p = shelf.get_prompt("Left Depth")
        # left_depth_p.set_formula('left_depth',[left_depth])
        # right_depth_p = shelf.get_prompt("Right Depth")
        # right_depth_p.set_formula('right_depth',[right_depth])

        opening = self.add_opening()
        opening.loc_z('IF(placement==0,c_height+s_thickness,0)',[placement,c_height,s_thickness])
        # opening.dim_x('IF(placement==2,0,width)',[placement,width])
        # opening.dim_y('IF(placement==2,0,depth)',[placement,depth])
        opening.dim_z('IF(placement==2,0,height-c_height-s_thickness)',[placement,height,c_height,s_thickness])

        v_cubby = assemblies_cabinet.add_closet_array_part(self)       
        v_cubby.loc_x('((width-(d_thickness*v_qty))/(v_qty+1))',[width,d_thickness,v_qty])
        v_cubby.loc_y('setback',[setback])
        v_cubby.loc_z('IF(placement==1,height-c_height,0)',[placement,height,c_height,s_thickness])
        v_cubby.rot_x(value = 0)
        v_cubby.rot_y(value = math.radians(-90))
        v_cubby.rot_z(value = 0)
        v_cubby.dim_x('IF(placement==2,height,c_height)',[placement,height,c_height])
        v_cubby.dim_y('depth-setback-back_inset',[depth,setback,back_inset])
        v_cubby.dim_z('-d_thickness',[d_thickness])
        qty = v_cubby.get_prompt('Z Quantity')
        offset = v_cubby.get_prompt('Z Offset')
        qty.set_formula('v_qty',[v_qty])
        offset.set_formula('-(((width-(d_thickness*v_qty))/(v_qty+1))+d_thickness)',[width,d_thickness,v_qty])
        pc_utils.flip_normals(v_cubby)

        start_placement = 'IF(placement==1,height-c_height,0)'
        v_spacing = '((IF(placement==2,height,c_height)-(s_thickness*h_qty))/(h_qty+1))'

        h_cubby = assemblies_cabinet.add_closet_array_part(self)        
        h_cubby.loc_x(value = 0)
        h_cubby.loc_y('setback',[setback])
        h_cubby.loc_z(start_placement + '+(' + v_spacing + ')',[placement,height,c_height,h_qty,s_thickness])
        h_cubby.rot_x(value = 0)
        h_cubby.rot_y(value = 0)
        h_cubby.rot_z(value = 0)
        h_cubby.dim_x('width',[width])
        h_cubby.dim_y('depth-setback-back_inset',[depth,setback,back_inset])
        h_cubby.dim_z('s_thickness',[s_thickness])
        qty = h_cubby.get_prompt('Z Quantity')
        offset = h_cubby.get_prompt('Z Offset')
        qty.set_formula('h_qty',[h_qty])
        offset.set_formula(v_spacing + '+s_thickness',[placement,height,c_height,h_qty,s_thickness])


class Doors(Closet_Insert):
    overlay_prompts = None

    def add_overlay_prompts(self):
        hot = self.get_prompt("Half Overlay Top").get_var('hot')
        hob = self.get_prompt("Half Overlay Bottom").get_var('hob')
        hol = self.get_prompt("Half Overlay Left").get_var('hol')
        hor = self.get_prompt("Half Overlay Right").get_var('hor')
        shelf_thickness = self.get_prompt("Shelf Thickness").get_var('shelf_thickness')
        panel_thickness = self.get_prompt("Panel Thickness").get_var('panel_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        tr = self.get_prompt("Top Reveal").get_var('tr')
        br = self.get_prompt("Bottom Reveal").get_var('br')
        lr = self.get_prompt("Left Reveal").get_var('lr')
        rr = self.get_prompt("Right Reveal").get_var('rr')

        self.overlay_prompts = self.add_empty('Overlay Prompt Obj')
        self.overlay_prompts['OVERLAY_PROMPTS'] = True
        self.overlay_prompts.empty_display_size = .01

        to = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Top Overlay")
        bo = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Bottom Overlay")
        lo = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Left Overlay")
        ro = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Right Overlay")

        to.set_formula('IF(hot,(shelf_thickness-vertical_gap)/2,shelf_thickness-tr)',[hot,shelf_thickness,vertical_gap,tr])
        bo.set_formula('IF(hob,(shelf_thickness-vertical_gap)/2,shelf_thickness-br)',[hob,shelf_thickness,vertical_gap,br])
        lo.set_formula('IF(hol,(panel_thickness-vertical_gap)/2,panel_thickness-lr)',[hol,panel_thickness,vertical_gap,lr])
        ro.set_formula('IF(hor,(panel_thickness-vertical_gap)/2,panel_thickness-rr)',[hor,panel_thickness,vertical_gap,rr])

        return to, bo, lo, ro

    def add_door_pull(self,front,pointer):
        pull_length = self.get_prompt("Pull Length")  
        if not pull_length:
            return #DON'T ADD PULLS TO APPLIED ENDS

        pull_path = paths_cabinet.get_handle_path_by_pointer(pointer)
        pull_obj = pc_utils.get_object(pull_path) 
        front.add_object(pull_obj)

        pull_length.set_value(round(pull_obj.dimensions.x,2))

        #VARS
        door_width = front.obj_y.pyclone.get_var('location.y','door_width')
        door_length = front.obj_x.pyclone.get_var('location.x','door_length')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        hide = front.get_prompt("Hide").get_var('hide')
        pull_length_var = pull_length.get_var('pull_length_var')
        base_pull_vertical_location = self.get_prompt("Base Pull Vertical Location").get_var('base_pull_vertical_location')
        tall_pull_vertical_location = self.get_prompt("Tall Pull Vertical Location").get_var('tall_pull_vertical_location')
        upper_pull_vertical_location = self.get_prompt("Upper Pull Vertical Location").get_var('upper_pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')
        door_type_prompt = self.get_prompt("Door Type")

        #FORMULAS
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        if door_type_prompt.get_value() == 'Base':
            pull_obj.pyclone.loc_x('door_length-base_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if door_type_prompt.get_value() == 'Tall':
            pull_obj.pyclone.loc_x('tall_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if door_type_prompt.get_value() == 'Upper':
            pull_obj.pyclone.loc_x('upper_pull_vertical_location+(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])     
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.loc_y('IF(door_width>0,door_width-pull_horizontal_location,door_width+pull_horizontal_location)',[door_width,pull_horizontal_location])
        pull_obj.pyclone.hide('IF(OR(hide,turn_off_pulls),True,False)',[hide,turn_off_pulls])

        pull_obj['IS_CABINET_PULL'] = True
        material_pointers_cabinet.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")  
        # home_builder_utils.get_object_props(pull_obj).pointer_name = pointer.name

    def add_drawer_pull(self,front,pointer):
        drawer_front_width = front.obj_y.pyclone.get_var('location.y',"drawer_front_width")
        drawer_front_height = front.obj_x.pyclone.get_var('location.x',"drawer_front_height")
        front_thickness = front.obj_z.pyclone.get_var('location.z',"front_thickness")
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')
        hide_drawer_front = front.get_prompt("Hide").get_var('hide_drawer_front')
        center_pull = self.get_prompt("Center Pull On Front").get_var('center_pull')
        vert_loc = self.get_prompt("Drawer Pull Vertical Location").get_var('vert_loc')

        pull_path = paths_cabinet.get_handle_path_by_pointer(pointer)
        pull_obj = pc_utils.get_object(pull_path) 
        pull_obj['IS_CABINET_PULL'] = True
        # home_builder_utils.get_object_props(pull_obj).pointer_name = "Drawer Pulls"
        front.add_object(pull_obj)
        pull_obj.parent = front.obj_bp
        pull_obj.pyclone.loc_x('IF(center_pull,(drawer_front_height/2),drawer_front_height-vert_loc)',[drawer_front_height,center_pull,vert_loc])
        pull_obj.pyclone.loc_y('(fabs(drawer_front_width)/2)*-1',[drawer_front_width])
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.rotation_euler.y = math.radians(0)
        pull_obj.rotation_euler.z = math.radians(90)
        pull_obj.pyclone.hide('IF(turn_off_pulls,True,hide_drawer_front)',[turn_off_pulls,hide_drawer_front])

        material_pointers_cabinet.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")  

    def add_prompts(self):
        prompts_cabinet.add_door_prompts(self)
        prompts_cabinet.add_front_prompts(self)
        prompts_cabinet.add_pull_prompts(self)
        prompts_cabinet.add_front_overlay_prompts(self)
        prompts_cabinet.add_closet_thickness_prompts(self)   

        hot = self.get_prompt("Half Overlay Top")  
        hot.set_value(True)   
        hob = self.get_prompt("Half Overlay Bottom")  
        hob.set_value(True)   
        hol = self.get_prompt("Half Overlay Left")  
        hol.set_value(True)   
        hor = self.get_prompt("Half Overlay Right")  
        hor.set_value(True)                           


class Base_Doors(Doors):

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()    
        self.obj_bp["IS_CLOSET_DOORS_BP"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_door_prompts"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        scene_props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.add_prompts()        
        self.add_prompt("Door Height",'DISTANCE',pc_unit.millimeter(716.95))
        self.add_prompt("Fill Opening",'CHECKBOX',False)
        self.add_prompt("Shelf Quantity",'QUANTITY',2)      

        # props = home_builder_utils.get_scene_props(bpy.context.scene)
        # front_pointer = props.cabinet_door_pointers["Base Cabinet Doors"]
        pull_pointer = scene_props.base_handle

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value("Base")

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')       
        fill = self.get_prompt("Fill Opening").get_var('fill')   
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')
        # left_depth = self.get_prompt("Left Depth").get_var("left_depth")
        # right_depth = self.get_prompt("Right Depth").get_var("right_depth")
        door_height_var = self.get_prompt("Door Height").get_var("door_height_var")
        s_qty = self.get_prompt("Shelf Quantity").get_var("s_qty")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        opening = self.add_opening()
        opening.set_name('Opening')
        opening.loc_z('IF(fill,0,door_height_var+s_thickness)',[fill,door_height_var,s_thickness])
        opening.dim_z('IF(fill,0,z-door_height_var-s_thickness)',[fill,z,door_height_var,s_thickness])

        #TOP SHELF
        shelf = assemblies_cabinet.add_closet_part(self)           
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Door Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('door_height_var',[door_height_var])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y-back_inset',[y,back_inset])
        shelf.dim_z('s_thickness',[s_thickness])
        hide = shelf.get_prompt("Hide")
        hide.set_formula('fill',[fill])        
        # left_depth_p = shelf.get_prompt("Left Depth")
        # left_depth_p.set_formula('left_depth',[left_depth])
        # right_depth_p = shelf.get_prompt("Right Depth")
        # right_depth_p.set_formula('right_depth',[right_depth])

        adj_shelf = assemblies_cabinet.add_closet_array_part(self)
        adj_shelf.obj_bp['IS_ADJ_SHELF'] = True
        adj_shelf.set_name("Adj Shelf")   
        adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',False)
        adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',scene_props.adj_shelf_setback)
        adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',scene_props.fixed_shelf_setback)
        # l_depth = adj_shelf.add_prompt("Left Depth",'DISTANCE',0)
        # r_depth = adj_shelf.add_prompt("Right Depth",'DISTANCE',0)

        adj_shelf.loc_x(value = 0)
        adj_shelf.loc_y('y-back_inset',[y,back_inset])
        adj_shelf.loc_z('((IF(fill,z,door_height_var)-(s_thickness*s_qty))/(s_qty+1))',[fill,door_height_var,z,s_thickness,s_qty])
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('x',[x])
        adj_shelf.dim_y('-y+back_inset',[y,back_inset])
        adj_shelf.dim_z('s_thickness',[s_thickness])
        hide = adj_shelf.get_prompt("Hide")
        z_quantity = adj_shelf.get_prompt("Z Quantity")
        z_offset = adj_shelf.get_prompt("Z Offset")
        hide.set_formula('IF(s_qty==0,True,False)',[s_qty])
        # l_depth.set_formula('left_depth',[left_depth]) 
        # r_depth.set_formula('right_depth',[right_depth]) 
        z_quantity.set_formula('s_qty',[s_qty]) 
        z_offset.set_formula('((IF(fill,z,door_height_var)-(s_thickness*s_qty))/(s_qty+1))+s_thickness',[fill,z,door_height_var,s_thickness,s_qty]) 

        #LEFT DOOR
        l_door = assemblies_cabinet.add_door_assembly(self)
        top_o = l_door.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = l_door.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = l_door.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = l_door.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('IF(fill,z,door_height_var)+to_var+bo_var',[fill,z,door_height_var,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)            
        top_o = r_door.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = r_door.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = r_door.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = r_door.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])        
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('IF(fill,z,door_height_var)+to_var+bo_var',[fill,z,door_height_var,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)        


class Tall_Doors(Doors):

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()    
        self.obj_bp["IS_CLOSET_DOORS_BP"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_door_prompts"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        scene_props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.add_prompts()
        self.add_prompt("Shelf Quantity",'QUANTITY',2) 

        # front_pointer = props.cabinet_door_pointers["Tall Cabinet Doors"]
        pull_pointer = scene_props.tall_handle

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value("Tall")

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')
        s_qty = self.get_prompt("Shelf Quantity").get_var('s_qty')
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        adj_shelf = assemblies_cabinet.add_closet_array_part(self)
        adj_shelf.obj_bp['IS_ADJ_SHELF'] = True
        adj_shelf.set_name("Adj Shelf")     
        adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',False)
        adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',scene_props.adj_shelf_setback)
        adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',scene_props.fixed_shelf_setback)

        adj_shelf.loc_x(value = 0)
        adj_shelf.loc_y('y-back_inset',[y,back_inset])
        adj_shelf.loc_z('(z-(s_thickness*s_qty))/(s_qty+1)',[z,s_thickness,s_qty])
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('x',[x])
        adj_shelf.dim_y('-y+back_inset',[y,back_inset])
        adj_shelf.dim_z('s_thickness',[s_thickness])
        hide = adj_shelf.get_prompt("Hide")
        z_quantity = adj_shelf.get_prompt("Z Quantity")
        z_offset = adj_shelf.get_prompt("Z Offset")
        hide.set_formula('IF(s_qty==0,True,False)',[s_qty])
        z_quantity.set_formula('s_qty',[s_qty]) 
        z_offset.set_formula('((z-(s_thickness*s_qty))/(s_qty+1))+s_thickness',[z,s_thickness,s_qty]) 

        #LEFT DOOR
        l_door = assemblies_cabinet.add_door_assembly(self)     
        top_o = l_door.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = l_door.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = l_door.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = l_door.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])        
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)        
        top_o = r_door.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = r_door.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = r_door.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = r_door.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])        
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)


class Upper_Doors(Doors):

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()    
        self.obj_bp["IS_CLOSET_DOORS_BP"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_door_prompts"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        scene_props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.add_prompts()      
        self.add_prompt("Fill Opening",'CHECKBOX',False)
        self.add_prompt("Door Height",'DISTANCE',pc_unit.millimeter(716.95))
        self.add_prompt("Shelf Quantity",'QUANTITY',2) 

        # front_pointer = props.cabinet_door_pointers["Upper Cabinet Doors"]
        pull_pointer = scene_props.upper_handle

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value("Upper")

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')    
        fill = self.get_prompt("Fill Opening").get_var('fill')    
        door_height_var = self.get_prompt("Door Height").get_var('door_height_var')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')
        s_qty = self.get_prompt("Shelf Quantity").get_var("s_qty")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        opening = self.add_opening()
        opening.set_name('Opening')
        opening.loc_z(value = 0)
        opening.dim_z('IF(fill,0,z-door_height_var-s_thickness)',[fill,z,door_height_var,s_thickness])

        #BOTTOM SHELF
        shelf = assemblies_cabinet.add_closet_part(self)     
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Door Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('z-door_height_var-s_thickness',[z,door_height_var,s_thickness])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y-back_inset',[y,back_inset])
        shelf.dim_z('s_thickness',[s_thickness])
        hide = shelf.get_prompt("Hide")
        hide.set_formula('fill',[fill])

        adj_shelf = assemblies_cabinet.add_closet_array_part(self)
        adj_shelf.obj_bp['IS_ADJ_SHELF'] = True
        adj_shelf.set_name("Adj Shelf")      
        adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',False)
        adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',scene_props.adj_shelf_setback)
        adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',scene_props.fixed_shelf_setback)

        adj_shelf.loc_x(value = 0)
        adj_shelf.loc_y('y-back_inset',[y,back_inset])
        adj_shelf.loc_z('IF(fill,0,z-door_height_var)+((IF(fill,z,door_height_var)-(s_thickness*s_qty))/(s_qty+1))',[fill,door_height_var,z,s_thickness,s_qty])
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('x',[x])
        adj_shelf.dim_y('-y+back_inset',[y,back_inset])
        adj_shelf.dim_z('s_thickness',[s_thickness])
        hide = adj_shelf.get_prompt("Hide")
        z_quantity = adj_shelf.get_prompt("Z Quantity")
        z_offset = adj_shelf.get_prompt("Z Offset")
        hide.set_formula('IF(s_qty==0,True,False)',[s_qty])
        z_quantity.set_formula('s_qty',[s_qty]) 
        z_offset.set_formula('((IF(fill,z,door_height_var)-(s_thickness*s_qty))/(s_qty+1))+s_thickness',[fill,z,door_height_var,s_thickness,s_qty]) 

        #LEFT DOOR
        l_door = assemblies_cabinet.add_door_assembly(self)
        top_o = l_door.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = l_door.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = l_door.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = l_door.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])           
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('IF(fill,0,z-door_height_var)-bo_var',[fill,z,door_height_var,bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('IF(fill,z,door_height_var)+to_var+bo_var',[fill,z,door_height_var,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)   
        top_o = r_door.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = r_door.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = r_door.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = r_door.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])             
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('IF(fill,0,z-door_height_var)-bo_var',[fill,z,door_height_var,bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('IF(fill,z,door_height_var)+to_var+bo_var',[fill,z,door_height_var,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)