import bpy
import os
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import paths_cabinet
from . import types_countertop
from . import const_cabinets as const
from . import prompts_cabinet

class Cabinet(pc_types.Assembly):
    cabinet_type = ""
    corner_type = ""

    include_countertop = False

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

    def add_countertop(self):
        prompts_cabinet.add_countertop_prompts(self)
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')    
        ctop_overhang_front = self.get_prompt("Countertop Overhang Front").get_var('ctop_overhang_front')
        ctop_overhang_back = self.get_prompt("Countertop Overhang Back").get_var('ctop_overhang_back')
        ctop_overhang_left = self.get_prompt("Countertop Overhang Left").get_var('ctop_overhang_left')
        ctop_overhang_right = self.get_prompt("Countertop Overhang Right").get_var('ctop_overhang_right')

        self.countertop = self.add_assembly(types_countertop.Countertop())
        self.countertop.set_name('Countertop')
        self.countertop.loc_x('-ctop_overhang_left',[ctop_overhang_left])
        self.countertop.loc_y('ctop_overhang_back',[ctop_overhang_back])
        self.countertop.loc_z('height',[height])
        self.countertop.dim_x('width+ctop_overhang_left+ctop_overhang_right',[width,ctop_overhang_left,ctop_overhang_right])
        self.countertop.dim_y('depth-(ctop_overhang_front+ctop_overhang_back)',[depth,ctop_overhang_front,ctop_overhang_back])


class Standard_Cabinet(Cabinet):

    width = pc_unit.inch(18)
    height = pc_unit.inch(34)
    depth = pc_unit.inch(21)

    carcass = None
    
    def __init__(self):
        pass

    def draw(self):
        self.create_assembly("Cabinet")
        self.obj_bp[const.CABINET_TAG] = True
        self.carcasses = []

        self.obj_x.location.x = self.width
        self.obj_y.location.y = -self.depth
        self.obj_z.location.z = self.height

        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_filler_prompts(self)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        cabinet_type = self.get_prompt("Cabinet Type")
        left_adjustment_width = self.get_prompt("Left Adjustment Width").get_var('left_adjustment_width')
        right_adjustment_width = self.get_prompt("Right Adjustment Width").get_var('right_adjustment_width')

        carcass = self.add_assembly(self.carcass)
        carcass.set_name('Carcass')
        carcass.loc_x('left_adjustment_width',[left_adjustment_width])
        carcass.loc_y(value=0)
        carcass.loc_z(value=0)
        carcass.dim_x('width-left_adjustment_width-right_adjustment_width',[width,left_adjustment_width,right_adjustment_width])
        carcass.dim_y('depth',[depth])
        carcass.dim_z('height',[height])
        self.carcasses.append(carcass)

        cabinet_type.set_value(carcass.carcass_type)

        if self.carcass.exterior:
            self.carcass.add_insert(self.carcass.exterior)
        if self.carcass.interior:
            self.carcass.add_insert(self.carcass.interior)

        if self.include_countertop:
            self.add_countertop()


class Stacked_Cabinet(Cabinet):

    width = pc_unit.inch(18)
    height = pc_unit.inch(34)
    depth = pc_unit.inch(21)

    carcass = None
    
    def __init__(self):
        pass

    def draw(self):
        self.create_assembly("Cabinet")
        self.obj_bp[const.CABINET_TAG] = True
        self.carcasses = []

        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_filler_prompts(self)
        prompts_cabinet.add_stacked_cabinet_prompts(self)     

        bottom_cabinet_height = self.get_prompt("Bottom Cabinet Height")
        bottom_cabinet_height.set_value(self.bottom_cabinet_height)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_adjment_width = self.get_prompt("Left Adjustment Width").get_var('left_adjment_width')
        right_adjment_width = self.get_prompt("Right Adjustment Width").get_var('right_adjment_width')
        bottom_cabinet_height = bottom_cabinet_height.get_var('bottom_cabinet_height')       

        self.bottom_carcass = self.add_assembly(self.bottom_carcass)
        self.bottom_carcass.set_name('Bottom Carcass')
        self.bottom_carcass.loc_x('left_adjment_width',[left_adjment_width])
        self.bottom_carcass.loc_y(value=0)
        self.bottom_carcass.loc_z(value=0)
        self.bottom_carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        self.bottom_carcass.dim_y('depth',[depth])
        self.bottom_carcass.dim_z('bottom_cabinet_height',[bottom_cabinet_height])

        self.top_carcass = self.add_assembly(self.top_carcass)
        self.top_carcass.set_name('Upper Carcass')
        self.top_carcass.loc_x('left_adjment_width',[left_adjment_width])
        self.top_carcass.loc_y(value=0)
        self.top_carcass.loc_z('bottom_cabinet_height',[bottom_cabinet_height])
        self.top_carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        self.top_carcass.dim_y('depth',[depth])
        self.top_carcass.dim_z('height-bottom_cabinet_height',[height,bottom_cabinet_height])

        self.obj_x.location.x = self.width
        self.obj_y.location.y = -self.depth
        self.obj_z.location.z = self.height
        # self.obj_bp.location.z = self.z_loc  

        if self.top_carcass.exterior:
            self.top_carcass.add_insert(self.top_carcass.exterior)
        if self.top_carcass.interior:
            self.top_carcass.add_insert(self.top_carcass.interior)              

        if self.bottom_carcass.exterior:
            self.bottom_carcass.add_insert(self.bottom_carcass.exterior)
        if self.bottom_carcass.interior:
            self.bottom_carcass.add_insert(self.bottom_carcass.interior)                                      