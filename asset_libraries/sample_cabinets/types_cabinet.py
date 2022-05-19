import bpy
import os
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import paths_cabinet
from . import const_cabinets as const
from . import prompts_cabinet

class Countertop(pc_types.Assembly):
    category_name = "Countertop"
    prompt_id = ""
    placement_id = ""

    def draw(self):
        self.create_assembly("Countertop")
        self.obj_bp["IS_COUNTERTOP_BP"] = True

        prompts_cabinet.add_countertop_prompts(self)

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -pc_unit.inch(22) 
        self.obj_z.location.z = pc_unit.inch(1.5) 

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        deck_thickness = self.get_prompt("Deck Thickness").get_var('deck_thickness')
        splash_thickness = self.get_prompt("Splash Thickness").get_var('splash_thickness')

        deck = assemblies_cabinet.add_countertop_part(self)
        deck.set_name('Top')
        deck.loc_x(value=0)
        deck.loc_y(value=0)
        deck.loc_z(value=0)
        deck.dim_x('width',[width])
        deck.dim_y('depth',[depth])
        deck.dim_z('deck_thickness',[deck_thickness])
        pc_utils.flip_normals(deck)

        self.obj_z.location.z = self.get_prompt("Deck Thickness").get_value()


class Design_Carcass(pc_types.Assembly):

    use_design_carcass = True
    left_side = None
    right_side = None
    back = None
    bottom = None
    top = None
    design_carcass = None
    design_base_assembly = None
    interior = None
    exterior = None

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
        if carcass_type.get_value() == "Upper": #UPPER CABINET
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
        prompts_cabinet.add_base_assembly_prompts(self)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        tkh = self.get_prompt("Toe Kick Height").get_var('tkh') 
        tk_setback = self.get_prompt("Toe Kick Setback").get_var('tk_setback') 

        carcass = assemblies_cabinet.add_design_carcass(self)
        carcass.set_name("Design Carcass")
        carcass.dim_x('width',[width])
        carcass.dim_y('depth',[depth])
        carcass.dim_z('height-tkh',[height,tkh])
        carcass.loc_z('tkh',[tkh])

        base_assembly = assemblies_cabinet.add_base_assembly(self)
        base_assembly.set_name("Base Assembly")
        base_assembly.dim_x('width',[width])
        base_assembly.dim_y('depth+tk_setback',[depth,tk_setback])
        base_assembly.dim_z('tkh',[height,tkh])   

class Cabinet(pc_types.Assembly):
    cabinet_type = ""
    corner_type = ""

    left_filler = None
    right_filler = None
    countertop = None
    sink_appliance = None
    faucet_appliance = None
    cooktop_appliance = None
    range_hood_appliance = None
    carcasses = []

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  


class Standard_Cabinet(Cabinet):
    
    width = pc_unit.inch(18)
    height = pc_unit.inch(34)
    depth = pc_unit.inch(21)

    carcass = None
    
    def __init__(self):
        pass

    def draw(self):
        self.create_assembly("Base Cabinet")
        self.obj_bp[const.CABINET_TAG] = True
        self.carcasses = []

        self.obj_x.location.x = self.width
        self.obj_y.location.y = -self.depth
        self.obj_z.location.z = self.height

        prompts_cabinet.add_filler_prompts(self)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        left_adjment_width = self.get_prompt("Left Adjustment Width").get_var('left_adjment_width')
        right_adjment_width = self.get_prompt("Right Adjustment Width").get_var('right_adjment_width')

        carcass = self.add_assembly(self.carcass)
        carcass.set_name('Carcass')
        carcass.loc_x('left_adjment_width',[left_adjment_width])
        carcass.loc_y(value=0)
        carcass.loc_z(value=0)
        carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        carcass.dim_y('depth',[depth])
        carcass.dim_z('height',[height])
        self.carcasses.append(carcass)

        if self.carcass.exterior:
            self.carcass.add_insert(self.carcass.exterior)

         