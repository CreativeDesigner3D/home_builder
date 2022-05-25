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