import bpy
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import const_cabinets as const
from . import prompts_cabinet
from . import types_cabinet_exteriors
from . import types_cabinet_interiors

class Design_Carcass(pc_types.Assembly):

    exposed_interior = False
    carcass_type = ""

    left_side = None
    right_side = None
    back = None
    bottom = None
    top = None
    design_carcass = None
    design_base_assembly = None
    interior = None
    exterior = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if "IS_LEFT_SIDE_BP" in child:
                    self.left_side = pc_types.Assembly(child)
                if "IS_RIGHT_SIDE_BP" in child:
                    self.right_side = pc_types.Assembly(child)    
                if "IS_BACK_BP" in child:
                    self.back = pc_types.Assembly(child)   
                if "IS_BOTTOM_BP" in child:
                    self.bottom = pc_types.Assembly(child)
                if "IS_TOP_BP" in child:
                    self.top = pc_types.Assembly(child)      
                if "IS_DESIGN_CARCASS_BP" in child:
                    self.design_carcass = pc_types.Assembly(child)         
                if "IS_DESIGN_BASE_ASSEMBLY_BP" in child:
                    self.design_base_assembly = pc_types.Assembly(child)                                          
                if "IS_INTERIOR_BP" in child:
                    self.interior = types_cabinet_interiors.Cabinet_Interior(child)    
                if "IS_EXTERIOR_BP" in child:
                    self.exterior = types_cabinet_exteriors.Cabinet_Exterior(child)   

    def add_insert(self,insert):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        material_thickness = self.get_prompt('Material Thickness').get_var('material_thickness')
        carcass_type = self.get_prompt("Carcass Type")

        if insert.carcass_type == "":
            insert.carcass_type = carcass_type.get_value()

        insert = self.add_assembly(insert)
        insert.loc_x('material_thickness',[material_thickness])
        insert.loc_y('depth',[depth])
        if carcass_type.get_value() == "Upper":
            insert.loc_z('material_thickness',[material_thickness])
            insert.dim_z('height-(material_thickness*2)',[height,material_thickness])
        else:
            toe_kick_height = self.get_prompt('Toe Kick Height').get_var('toe_kick_height')
            insert.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
            insert.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
        
        insert.dim_x('width-(material_thickness*2)',[width,material_thickness])
        insert.dim_y('fabs(depth)-material_thickness',[depth,material_thickness])
        insert.obj_x.empty_display_size = .001
        insert.obj_y.empty_display_size = .001
        insert.obj_z.empty_display_size = .001
        insert.obj_bp.empty_display_size = .001
        insert.obj_prompts.empty_display_size = .001

        bpy.context.view_layer.update()

        # calculator = insert.get_calculator('Front Height Calculator')
        # if calculator:
        #     calculator.calculate()
        
        return insert

    def draw(self):
        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        prompts_cabinet.add_thickness_prompts(self)
        prompts_cabinet.add_carcass_prompts(self)
        prompts_cabinet.add_filler_prompts(self)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)
        is_exposed_interior = self.get_prompt("Is Exposed Interior")
        is_exposed_interior.set_value(self.exposed_interior)

        if carcass_type.get_value() == "Upper":
            carcass = assemblies_cabinet.add_design_carcass(self,self.exposed_interior)
            carcass.set_name("Design Carcass")
            carcass.dim_x('width',[width])
            carcass.dim_y('depth',[depth])
            carcass.dim_z('height',[height])
            carcass.loc_z(value=0)
        else:
            prompts_cabinet.add_base_assembly_prompts(self)

            tkh = self.get_prompt("Toe Kick Height").get_var('tkh') 
            tk_setback = self.get_prompt("Toe Kick Setback").get_var('tk_setback') 

            carcass = assemblies_cabinet.add_design_carcass(self,self.exposed_interior)
            carcass.set_name("Design Carcass")
            carcass.dim_x('width',[width])
            carcass.dim_y('depth',[depth])
            carcass.dim_z('height-tkh',[height,tkh])
            carcass.loc_z('tkh',[tkh])

            law = self.get_prompt("Left Adjustment Width").get_var('law')
            raw = self.get_prompt("Right Adjustment Width").get_var('raw')

            base_assembly = assemblies_cabinet.add_base_assembly(self)
            base_assembly.set_name("Base Assembly")
            base_assembly.loc_x('-law',[law])
            base_assembly.dim_x('width+law+raw',[width,law,raw])
            base_assembly.dim_y('depth+tk_setback',[depth,tk_setback])
            base_assembly.dim_z('tkh',[height,tkh])   


class Design_Blind_Carcass(pc_types.Assembly):

    exposed_interior = False
    carcass_type = ""

    left_side = None
    right_side = None
    back = None
    bottom = None
    top = None
    design_carcass = None
    design_base_assembly = None
    interior = None
    exterior = None

    def add_exterior_insert(self,insert):
        # x_loc_carcass = self.obj_bp.pyclone.get_var('location.x','x_loc_carcass')
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        material_thickness = self.get_prompt('Material Thickness').get_var('material_thickness')
        carcass_type = self.get_prompt("Carcass Type")
        blind_panel_location = self.get_prompt("Blind Panel Location").get_var("blind_panel_location")
        blind_panel_width = self.get_prompt("Blind Panel Width").get_var("blind_panel_width")
        blind_panel_reveal = self.get_prompt("Blind Panel Reveal").get_var("blind_panel_reveal")
        
        #ADD NAME OF EXTERIOR TO 
        #PASS PROMPTS IN CORRECT
        insert.carcass_type = carcass_type.get_value()

        insert = self.add_assembly(insert)
        insert.loc_x('IF(blind_panel_location==0,material_thickness+blind_panel_width+blind_panel_reveal,material_thickness)',
                     [blind_panel_location,width,blind_panel_width,blind_panel_reveal,material_thickness])
        insert.loc_y('depth',[depth])
        if carcass_type.get_value() == "Upper": #UPPER CABINET
            insert.loc_z('material_thickness',[material_thickness])
            insert.dim_z('height-(material_thickness*2)',[height,material_thickness])
        else:
            toe_kick_height = self.get_prompt('Toe Kick Height').get_var('toe_kick_height')
            insert.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
            insert.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
        
        insert.dim_x('width-(material_thickness*2)-blind_panel_width-blind_panel_reveal',[width,material_thickness,blind_panel_width,blind_panel_reveal])
        insert.dim_y('fabs(depth)-material_thickness',[depth,material_thickness])
        insert.obj_x.empty_display_size = .001
        insert.obj_y.empty_display_size = .001
        insert.obj_z.empty_display_size = .001
        insert.obj_bp.empty_display_size = .001
        insert.obj_prompts.empty_display_size = .001

        bpy.context.view_layer.update()

        # calculator = insert.get_calculator('Front Height Calculator')
        # if calculator:
        #     calculator.calculate()
        
        return insert

    def add_interior_insert(self,insert):
        # x_loc_carcass = self.obj_bp.pyclone.get_var('location.x','x_loc_carcass')
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        material_thickness = self.get_prompt('Material Thickness').get_var('material_thickness')
        carcass_type = self.get_prompt("Carcass Type")

        #ADD NAME OF EXTERIOR TO 
        #PASS PROMPTS IN CORRECT
        insert.carcass_type = carcass_type.get_value()

        insert = self.add_assembly(insert)
        insert.loc_x('material_thickness',[material_thickness])
        insert.loc_y('depth+material_thickness',[depth,material_thickness])
        if carcass_type.get_value() == "Upper": #UPPER CABINET
            insert.loc_z('material_thickness',[material_thickness])
            insert.dim_z('height-(material_thickness*2)',[height,material_thickness])
        else:
            toe_kick_height = self.get_prompt('Toe Kick Height').get_var('toe_kick_height')
            insert.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
            insert.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
        
        insert.dim_x('width-(material_thickness*2)',[width,material_thickness])
        insert.dim_y('fabs(depth)-(material_thickness*2)',[depth,material_thickness])
        insert.obj_x.empty_display_size = .001
        insert.obj_y.empty_display_size = .001
        insert.obj_z.empty_display_size = .001
        insert.obj_bp.empty_display_size = .001
        insert.obj_prompts.empty_display_size = .001

        bpy.context.view_layer.update()

        # calculator = insert.get_calculator('Front Height Calculator')
        # if calculator:
        #     calculator.calculate()
        
        return insert

    def add_blind_panel(self):
        prompts_cabinet.add_blind_cabinet_prompts(self)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        
        material_thickness = self.get_prompt("Material Thickness").get_var("material_thickness")
        blind_panel_location = self.get_prompt("Blind Panel Location").get_var("blind_panel_location")
        blind_panel_width = self.get_prompt("Blind Panel Width").get_var("blind_panel_width")
        blind_panel_reveal = self.get_prompt("Blind Panel Reveal").get_var("blind_panel_reveal")
        carcass_type = self.get_prompt("Carcass Type")

        blind_panel = assemblies_cabinet.add_blind_panel_part_assembly(self)
        blind_panel.obj_bp["IS_BLIND_PANEL_BP"] = True
        blind_panel.set_name('Blind Panel')
        blind_panel.loc_x('IF(blind_panel_location==0,material_thickness,width-material_thickness-blind_panel_width-blind_panel_reveal)',
                          [blind_panel_location,material_thickness,width,blind_panel_width,blind_panel_reveal])
        blind_panel.loc_y('depth',[depth])
        blind_panel.rot_y(value=math.radians(-90))
        blind_panel.rot_z(value=math.radians(90))
        blind_panel.dim_y('-blind_panel_width-blind_panel_reveal',[depth,blind_panel_width,blind_panel_reveal])
        blind_panel.dim_z('-material_thickness',[material_thickness])
        if carcass_type.get_value() == "Upper":
            blind_panel.loc_z('material_thickness',[material_thickness])
            blind_panel.dim_x('height-(material_thickness*2)',[height,material_thickness])
        else:
            toe_kick_height = self.get_prompt("Toe Kick Height").get_var("toe_kick_height")
            blind_panel.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])      
            blind_panel.dim_x('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])  
        return blind_panel

    def draw(self):
        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        prompts_cabinet.add_thickness_prompts(self)
        prompts_cabinet.add_carcass_prompts(self)        

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)
        is_exposed_interior = self.get_prompt("Is Exposed Interior")
        is_exposed_interior.set_value(self.exposed_interior)
        
        if carcass_type.get_value() == "Upper":
            self.design_carcass = assemblies_cabinet.add_design_carcass(self,self.exposed_interior)
            self.design_carcass.set_name("Design Carcass")
            self.design_carcass.dim_x('width',[width])
            self.design_carcass.dim_y('depth',[depth])
            self.design_carcass.dim_z('height',[height])
            self.design_carcass.loc_z(value=0)
        else:
            prompts_cabinet.add_base_assembly_prompts(self)
            tkh = self.get_prompt("Toe Kick Height").get_var('tkh') 
            tk_setback = self.get_prompt("Toe Kick Setback").get_var('tk_setback') 

            self.design_carcass = assemblies_cabinet.add_design_carcass(self,self.exposed_interior)
            self.design_carcass.set_name("Design Carcass")
            self.design_carcass.dim_x('width',[width])
            self.design_carcass.dim_y('depth',[depth])
            self.design_carcass.dim_z('height-tkh',[height,tkh])
            self.design_carcass.loc_z('tkh',[tkh])

            base_assembly = assemblies_cabinet.add_base_assembly(self)
            base_assembly.set_name("Base Assembly")
            base_assembly.dim_x('width',[width])
            base_assembly.dim_y('depth+tk_setback',[depth,tk_setback])
            base_assembly.dim_z('tkh',[height,tkh]) 

        self.add_blind_panel()


class Base_Design_Carcass(Design_Carcass):
    carcass_type = "Base"


class Tall_Design_Carcass(Design_Carcass):
    carcass_type = "Tall"    


class Upper_Design_Carcass(Design_Carcass):
    carcass_type = "Upper"       


class Base_Blind_Design_Carcass(Design_Blind_Carcass):
    carcass_type = "Base"


class Tall_Blind_Design_Carcass(Design_Blind_Carcass):
    carcass_type = "Tall"    


class Upper_Blind_Design_Carcass(Design_Blind_Carcass):
    carcass_type = "Upper"           