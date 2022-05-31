import bpy
import time
import math
from os import path
from pc_lib import pc_types, pc_unit, pc_utils

from . import assemblies_cabinet
from . import utils_cabinet

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