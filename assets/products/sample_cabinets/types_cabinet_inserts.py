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
from . import const_cabinets as const
from . import types_fronts

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

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()
        self.obj_bp[const.CLOSET_SHELVES_TAG] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.adj_shelves_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75)) 
        self.add_prompt("Shelf Clip Gap",'DISTANCE',hb_props.shelf_clip_gap) 
        self.add_prompt("Shelf Quantity",'QUANTITY',3) 

        self.add_shelves()

    def update_prompts_after_placement(self,context):
        shelf_qty = self.get_prompt("Shelf Quantity")
        shelf_qty.set_value(math.ceil(self.obj_z.location.z/pc_unit.inch(15)))

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
        self.obj_bp[const.CLOSET_HANGING_ROD] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.hanging_rod_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"

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
        self.obj_bp[const.CLOSET_SLANTED_SHOE_SHELVES] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.slanted_shoe_shelf_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"
        
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

    def update_prompts_after_placement(self,context):
        shelf_qty = self.get_prompt("Shelf Quantity")
        shelf_qty.set_value(math.ceil(self.obj_z.location.z/pc_unit.inch(15)))


class Cubbies(Closet_Insert):

    def draw(self):      
        self.create_assembly()
        self.add_closet_insert_prompts()        
        self.obj_bp[const.CLOSET_CUBBIES_TAG] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.cubby_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        self.add_prompt("Cubby Placement",'COMBOBOX',0,["Bottom","Top","Fill"])
        self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        self.add_prompt("Divider Thickness",'DISTANCE',pc_unit.inch(1)) 
        self.add_prompt("Horizontal Quantity",'QUANTITY',2) 
        self.add_prompt("Vertical Quantity",'QUANTITY',2) 
        self.add_prompt("Cubby Setback",'DISTANCE',pc_unit.inch(.125)) 
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
        v_cubby.loc_y(value=0)
        v_cubby.loc_z('IF(placement==1,height-c_height,0)',[placement,height,c_height,s_thickness])
        v_cubby.rot_x(value = 0)
        v_cubby.rot_y(value = math.radians(-90))
        v_cubby.rot_z(value = 0)
        v_cubby.dim_x('IF(placement==2,height,c_height)',[placement,height,c_height])
        v_cubby.dim_y('depth-back_inset',[depth,back_inset])
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

    def update_prompts_after_placement(self,context):
        placement = self.get_prompt("Cubby Placement")
        cubby_height = self.get_prompt("Cubby Height")
        insert_height = self.obj_z.location.z
        if cubby_height.get_value() > insert_height:
            placement.set_value(2)
        else:
            placement.set_value(0)


class Wire_Baskets(Closet_Insert):
    
    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()      
        self.obj_bp[const.CLOSET_WIRE_BASKETS_TAG] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp['PROMPT_ID'] = 'hb_sample_cabinets.wire_baskets_prompts'
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)        

        self.add_prompt("Wire Basket Quantity",'QUANTITY',3)
        self.add_prompt("Wire Basket 1 Height",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Wire Basket 2 Height",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Wire Basket 3 Height",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Wire Basket 4 Height",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Wire Basket 5 Height",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Wire Basket 6 Height",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Vertical Spacing",'DISTANCE',pc_unit.inch(3))
        
        prompts_cabinet.add_closet_thickness_prompts(self)

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')      
        qty = self.get_prompt("Wire Basket Quantity").get_var('qty') 
        wbh1 = self.get_prompt("Wire Basket 1 Height").get_var('wbh1')
        wbh2 = self.get_prompt("Wire Basket 2 Height").get_var('wbh2')
        wbh3 = self.get_prompt("Wire Basket 3 Height").get_var('wbh3') 
        wbh4 = self.get_prompt("Wire Basket 4 Height").get_var('wbh4') 
        wbh5 = self.get_prompt("Wire Basket 5 Height").get_var('wbh5') 
        wbh6 = self.get_prompt("Wire Basket 6 Height").get_var('wbh6')
        v = self.get_prompt("Shelf Thickness").get_var('v')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        #TOP SHELF
        shelf = assemblies_cabinet.add_closet_part(self)          
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Wire Basket Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('wbh1+v+IF(qty>1,wbh2+v,0)+IF(qty>2,wbh3+v,0)+IF(qty>3,wbh4+v,0)+IF(qty>4,wbh5+v,0)+IF(qty>5,wbh6+v,0)',
                    [qty,wbh1,wbh2,wbh3,wbh4,wbh5,wbh6,v])        
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y-back_inset',[y,back_inset])
        shelf.dim_z('s_thickness',[s_thickness])

        shelf_z_loc = shelf.obj_bp.pyclone.get_var('location.z','shelf_z_loc')

        opening = self.add_opening()
        opening.loc_z('shelf_z_loc+s_thickness',[shelf_z_loc,s_thickness])
        opening.dim_z('z-shelf_z_loc-s_thickness',[z,shelf_z_loc,s_thickness])

        prev_wire_basket_empty = None

        for i in range(1,7):
            wire_basket_height = self.get_prompt('Wire Basket ' + str(i) + " Height")
            wbh = wire_basket_height.get_var('wbh')
            wire_basket_empty = self.add_empty('Z Loc ' + str(i))
            if prev_wire_basket_empty:
                prev_z_loc = prev_wire_basket_empty.pyclone.get_var('location.z','prev_z_loc')
                wire_basket_empty.pyclone.loc_z('prev_z_loc-wbh-v',[prev_z_loc,wbh,v])
            else:
                wire_basket_empty.pyclone.loc_z('shelf_z_loc-wbh-v',
                                          [shelf_z_loc,wbh,v])      

            z_loc = wire_basket_empty.pyclone.get_var('location.z','z_loc')

            basket = assemblies_cabinet.add_wire_basket(self)
            basket.loc_x(value = 0)
            basket.loc_y(value = 0)
            basket.loc_z('z_loc',[z_loc])                                                                             
            basket.rot_x(value = 0)
            basket.rot_y(value = 0)
            basket.rot_z(value = 0)
            basket.dim_x('x',[x])
            basket.dim_y('y-back_inset',[y,back_inset])            
            basket.dim_z('wbh',[wbh])
            hide = basket.get_prompt('Hide')
            hide.set_formula('IF(qty>' + str(i-1) + ',False,True)',[qty])

            prev_wire_basket_empty = wire_basket_empty
               
    def update_prompts_after_placement(self,context):
        qty = self.get_prompt("Wire Basket Quantity")
        qty.set_value(math.ceil(self.obj_z.location.z/pc_unit.inch(15)))
            

class Wine_Rack(Closet_Insert):
    
    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()      
        self.obj_bp[const.WINE_RACK_TAG] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp['PROMPT_ID'] = 'hb_sample_cabinets.wine_rack_prompts'
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)        

        self.add_prompt("Wine Rack Quantity",'QUANTITY',3)
        self.add_prompt("Space From Bottom",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Vertical Spacing",'DISTANCE',pc_unit.inch(6))
        self.add_prompt("Wine Rack Setback",'DISTANCE',pc_unit.inch(2))
        self.add_prompt("Wine Rack Depth",'DISTANCE',pc_unit.inch(10))

        prompts_cabinet.add_closet_thickness_prompts(self)

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')      
        qty = self.get_prompt("Wine Rack Quantity").get_var('qty') 
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")
        space_from_bot = self.get_prompt("Space From Bottom").get_var("space_from_bot")
        vert_spacing = self.get_prompt("Vertical Spacing").get_var("vert_spacing")
        setback = self.get_prompt("Wine Rack Setback").get_var("setback")
        rack_depth = self.get_prompt("Wine Rack Depth").get_var("rack_depth")

        rack = assemblies_cabinet.add_wine_rack(self)
        rack.loc_x('x',[x])
        rack.loc_y('rack_depth+setback',[rack_depth,setback])
        rack.loc_z('space_from_bot',[space_from_bot])                                                                         
        rack.rot_x(value = 0)
        rack.rot_y(value = 0)
        rack.rot_z(value = math.radians(180))
        rack.dim_x('x',[x])
        rack.dim_y('rack_depth',[rack_depth])            
        rack.dim_z(value = 0)
        z_quantity = rack.get_prompt("Z Quantity")
        z_offset = rack.get_prompt("Z Offset")
        z_quantity.set_formula('qty',[qty]) 
        z_offset.set_formula('vert_spacing',[vert_spacing])         

    def update_prompts_after_placement(self,context):
        qty = self.get_prompt("Wine Rack Quantity")
        space_from_bottom = self.get_prompt("Space From Bottom").get_value()
        vertical_spacing = self.get_prompt("Vertical Spacing").get_value()
        height = self.obj_z.location.z
        qty.set_value(math.floor((height/vertical_spacing)-(space_from_bottom*2)))


class Vertical_Splitter(Closet_Insert):

    splitter_qty = 1

    def add_splitters(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        # left_depth = self.get_prompt("Left Depth").get_var("left_depth")
        # right_depth = self.get_prompt("Right Depth").get_var("right_depth")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")

        previous_splitter = None

        for i in range(1,self.splitter_qty+1):
            opening_height = self.get_prompt('Opening ' + str(i) + ' Height').get_var('Opening Calculator','opening_height')
            splitter = assemblies_cabinet.add_closet_part(self)
            # splitter.obj_bp["IS_SHELF_BP"] = True
            # splitter.obj_bp['ADD_DIMENSION'] = True
            # props = home_builder_utils.get_object_props(splitter.obj_bp)
            # props.ebl2 = True
            # props.part_name = "Fixed Shelf"             
            splitter.loc_x(value = 0)
            splitter.loc_y(value = 0)
            if previous_splitter:
                loc_z = previous_splitter.obj_bp.pyclone.get_var('location.z','loc_z')
                splitter.loc_z('loc_z-opening_height-s_thickness',[loc_z,opening_height,s_thickness])
            else:
                splitter.loc_z('height-opening_height-s_thickness',[height,opening_height,s_thickness])
            splitter.rot_x(value = 0)
            splitter.rot_y(value = 0)
            splitter.rot_z(value = 0)
            splitter.dim_x('width',[width])
            splitter.dim_y('depth-back_inset',[depth,back_inset])
            splitter.dim_z('s_thickness',[s_thickness])
            # left_depth_p = splitter.get_prompt("Left Depth")
            # left_depth_p.set_formula('left_depth',[left_depth])
            # right_depth_p = splitter.get_prompt("Right Depth")
            # right_depth_p.set_formula('right_depth',[right_depth])

            s_loc_z = splitter.obj_bp.pyclone.get_var('location.z','s_loc_z')

            opening = self.add_opening()
            opening.loc_z('s_loc_z+s_thickness',[s_loc_z,s_thickness])
            opening.dim_z('opening_height',[opening_height])

            previous_splitter = splitter

        last_opening_height = self.get_prompt('Opening ' + str(self.splitter_qty+1) + ' Height').get_var('Opening Calculator','last_opening_height')

        opening = self.add_opening()
        opening.loc_z(value = 0)
        opening.dim_z('last_opening_height',[last_opening_height])       

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()   
        self.obj_bp["IS_SPLITTER_INSERT"] = True
        self.obj_bp[const.VERTICAL_SPLITTER_TAG] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.splitter_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75)) 

        height = self.obj_z.pyclone.get_var('location.z','height')
        s_thickness = shelf_thickness.get_var('s_thickness')
        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        opening_calculator = self.obj_prompts.pyclone.add_calculator("Opening Calculator",calc_distance_obj)

        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Height')

        opening_calculator.set_total_distance('height-s_thickness*' + str(self.splitter_qty),[height,s_thickness])

        self.add_splitters()

        bpy.context.view_layer.update()
        opening_calculator.calculate()

    def render(self):
        self.pre_draw()
        self.draw()


class Horizontal_Splitter(Closet_Insert):

    splitter_qty = 1

    def add_splitters(self):
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        d_thickness = self.get_prompt("Division Thickness").get_var("d_thickness")
        back_inset = self.get_prompt("Back Inset").get_var("back_inset")
        previous_splitter = None

        for i in range(1,self.splitter_qty+1):
            opening_width = self.get_prompt('Opening ' + str(i) + ' Width').get_var('Opening Calculator','opening_width')

            opening = self.add_opening()
            opening.set_name('Opening ' + str(i))
            if previous_splitter:
                loc_x = previous_splitter.obj_bp.pyclone.get_var('location.x','loc_x')
                opening.loc_x('loc_x',[loc_x])
            else:
                opening.loc_x(value = 0)
            opening.loc_y(value = 0)
            opening.loc_z(value = 0)
            opening.dim_x('opening_width',[opening_width])
            opening.dim_z('height',[height])

            splitter = assemblies_cabinet.add_closet_part(self)
            # splitter.obj_bp['IS_DIVISION_BP'] = True
            # props = home_builder_utils.get_object_props(splitter.obj_bp)
            # props.ebl2 = True
            # props.part_name = "Division"                   
            # splitter.set_name("Division " + str(i))
            if previous_splitter:
                loc_x = previous_splitter.obj_bp.pyclone.get_var('location.x','loc_x')
                splitter.loc_x('loc_x+opening_width+d_thickness',[loc_x,opening_width,d_thickness])
            else:
                splitter.loc_x('opening_width+d_thickness',[opening_width,d_thickness])            
            splitter.loc_y(value = 0)
            splitter.loc_z(value = 0)
            splitter.rot_x(value = 0)
            splitter.rot_y(value = math.radians(-90))
            splitter.rot_z(value = 0)
            splitter.dim_x('height',[height])
            splitter.dim_y('depth-back_inset',[depth,back_inset])
            splitter.dim_z('d_thickness',[d_thickness])

            previous_splitter = splitter

        previous_splitter_x = previous_splitter.obj_bp.pyclone.get_var('location.x','previous_splitter_x')
        last_opening_width = self.get_prompt('Opening ' + str(self.splitter_qty+1) + ' Width').get_var('Opening Calculator','last_opening_width')

        last_opening = assemblies_cabinet.add_closet_opening(self)
        last_opening.set_name('Opening ' + str(self.splitter_qty+1))
        last_opening.loc_x('previous_splitter_x',[previous_splitter_x])
        last_opening.loc_y(value = 0)
        last_opening.loc_z(value = 0)
        last_opening.rot_x(value = 0)
        last_opening.rot_y(value = 0)
        last_opening.rot_z(value = 0)
        last_opening.dim_x('last_opening_width',[last_opening_width])
        last_opening.dim_y('depth',[depth])
        last_opening.dim_z('height',[height])

    def draw(self):
        self.create_assembly()
        self.add_closet_insert_prompts()  
        self.obj_bp[const.HORIZONTAL_SPLITTER_TAG] = True
        self.obj_bp[const.INSERT_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.division_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_insert_commands"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        self.add_prompt("Division Thickness",'DISTANCE',pc_unit.inch(.75)) 

        width = self.obj_x.pyclone.get_var('location.x','width')
        d_thickness = self.get_prompt("Division Thickness").get_var('d_thickness')
        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        opening_calculator = self.obj_prompts.pyclone.add_calculator("Opening Calculator",calc_distance_obj)

        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Width')

        opening_calculator.set_total_distance('width-d_thickness*' + str(self.splitter_qty),[width,d_thickness])

        self.add_splitters()

        bpy.context.view_layer.update()
        opening_calculator.calculate()

