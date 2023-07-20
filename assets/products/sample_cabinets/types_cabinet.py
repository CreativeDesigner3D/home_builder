import bpy
import os
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import paths_cabinet
from . import types_countertop
from . import types_cabinet_carcass
from . import const_cabinets as const
from . import prompts_cabinet
from . import material_pointers_cabinet

def get_sink(category,assembly_name):
    ASSET_DIR = paths_cabinet.get_sink_paths()
    if assembly_name == "":
        return os.path.join(ASSET_DIR,"_Sample","Generic Large Sink.blend")  
    else:
        return os.path.join(ASSET_DIR, category, assembly_name + ".blend")

def get_faucet(category,assembly_name):
    ASSET_DIR = paths_cabinet.get_faucet_paths()
    if assembly_name == "":
        return os.path.join(ASSET_DIR,"_Sample","Artifacts 99259.blend")  
    else:
        return os.path.join(ASSET_DIR, category, assembly_name + ".blend")

def get_cooktop(category,assembly_name):
    ASSET_DIR = paths_cabinet.get_cooktop_paths()
    if assembly_name == "":
        return os.path.join(ASSET_DIR,"_Sample","Cooktop 30in (762mm).blend")  
    else:
        return os.path.join(ASSET_DIR, category, assembly_name + ".blend")

def get_range_hood(category,assembly_name):
    ASSET_DIR = paths_cabinet.get_range_hood_paths()
    if assembly_name == "":
        return os.path.join(ASSET_DIR,"_Sample","Generic Range Hood.blend")  
    else:
        return os.path.join(ASSET_DIR, category, assembly_name + ".blend")   


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
        self.carcasses = []
        if obj_bp:
            cabinet_type = self.get_prompt("Cabinet Type")
            if cabinet_type:
                self.cabinet_type = cabinet_type.get_value()
            corner_type = self.get_prompt("Corner Type")
            if corner_type:
                self.corner_type = corner_type.get_value()                
            for child in obj_bp.children:
                if "IS_LEFT_FILLER_BP" in child:
                    self.left_filler = pc_types.Assembly(child)
                if "IS_RIGHT_FILLER_BP" in child:
                    self.right_filler = pc_types.Assembly(child)     
                if "IS_COUNTERTOP_BP" in child:
                    self.countertop = pc_types.Assembly(child)     
                if "IS_SINK_BP" in child:
                    self.sink_appliance = pc_types.Assembly(child)  
                    for sink_child in self.sink_appliance.obj_bp.children:
                        if "IS_FAUCET_BP" in sink_child:
                            for faucet_child in sink_child.children:
                                self.faucet_appliance = faucet_child
                if "IS_COOKTOP_BP" in child:
                    self.cooktop_appliance = pc_types.Assembly(child)    
                if "IS_RANGE_HOOD_BP" in child:
                    self.range_hood_appliance = pc_types.Assembly(child)                                                                                                   
                if "IS_CARCASS_BP" in child:
                    carcass = types_cabinet_carcass.Design_Carcass(child)
                    self.carcasses.append(carcass)        

    def update_range_hood_location(self):
        if self.range_hood_appliance:
            self.range_hood_appliance.obj_bp.location.x = (self.obj_x.location.x/2) - (self.range_hood_appliance.obj_x.location.x)/2
            self.range_hood_appliance.obj_bp.location.z = pc_unit.inch(70)

    def add_sink(self,category="",assembly_name=""):
        self.sink_appliance = pc_types.Assembly(self.add_assembly_from_file(get_sink(category,assembly_name)))
        self.sink_appliance.obj_bp["IS_SINK_BP"] = True

        cabinet_width = self.obj_x.pyclone.get_var('location.x','cabinet_width')
        cabinet_depth = self.obj_y.pyclone.get_var('location.y','cabinet_depth')
        cabinet_height = self.obj_z.pyclone.get_var('location.z','cabinet_height')
        countertop_height = self.countertop.obj_z.pyclone.get_var('location.z','countertop_height')
        sink_width = self.sink_appliance.obj_x.location.x
        sink_depth = self.sink_appliance.obj_y.location.y

        self.sink_appliance.loc_x('(cabinet_width/2)-' + str(sink_width/2),[cabinet_width])
        self.sink_appliance.loc_y('(cabinet_depth/2)-' + str(sink_depth/2),[cabinet_depth])
        self.sink_appliance.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])

        for child in self.sink_appliance.obj_bp.children:
            if child.hide_render:
                child.hide_viewport = True
            if child.type == 'MESH':   
                if 'IS_BOOLEAN' in child and child['IS_BOOLEAN'] == True:   
                    bool_obj = child
                    break

        pc_utils.assign_boolean_to_child_assemblies(self.countertop,bool_obj)
        for carcass in self.carcasses:
            pc_utils.assign_boolean_to_child_assemblies(carcass,bool_obj)

        pc_utils.update_assembly_id_props(self.sink_appliance,self)

    def add_faucet(self,category="",object_name=""):
        if self.sink_appliance:
            self.faucet_appliance = self.add_object_from_file(get_faucet(category,object_name))
            self.faucet_appliance["IS_FAUCET"] = True

            faucet_bp = None

            for child in self.sink_appliance.obj_bp.children:
                if "IS_FAUCET_BP" in child and child["IS_FAUCET_BP"]:
                    faucet_bp = child

            self.faucet_appliance.parent = faucet_bp

    def add_cooktop(self,category="",assembly_name=""):
        self.cooktop_appliance = pc_types.Assembly(self.add_assembly_from_file(get_cooktop(category,assembly_name)))
        self.cooktop_appliance.obj_bp["IS_COOKTOP_BP"] = True

        cabinet_width = self.obj_x.pyclone.get_var('location.x','cabinet_width')
        cabinet_depth = self.obj_y.pyclone.get_var('location.y','cabinet_depth')
        cabinet_height = self.obj_z.pyclone.get_var('location.z','cabinet_height')
        countertop_height = self.countertop.obj_z.pyclone.get_var('location.z','countertop_height')
        cooktop_width = self.cooktop_appliance.obj_x.location.x
        cooktop_depth = self.cooktop_appliance.obj_y.location.y

        self.cooktop_appliance.loc_x('(cabinet_width/2)-' + str(cooktop_width/2),[cabinet_width])
        self.cooktop_appliance.loc_y('(cabinet_depth/2)-' + str(cooktop_depth/2),[cabinet_depth])
        self.cooktop_appliance.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])

        for child in self.cooktop_appliance.obj_bp.children:
            if child.type == 'MESH':   
                if 'IS_BOOLEAN' in child and child['IS_BOOLEAN'] == True:   
                    bool_obj = child
                    break

        pc_utils.assign_boolean_to_child_assemblies(self.countertop,bool_obj)
        for carcass in self.carcasses:
            pc_utils.assign_boolean_to_child_assemblies(carcass,bool_obj)

        pc_utils.update_assembly_id_props(self.cooktop_appliance,self)

    def add_range_hood(self,category="",assembly_name=""):
        self.range_hood_appliance = pc_types.Assembly(self.add_assembly_from_file(get_range_hood(category,assembly_name)))
        self.range_hood_appliance.obj_bp["IS_RANGE_HOOD_BP"] = True
        self.range_hood_appliance.obj_x.empty_display_size = pc_unit.inch(.5)
        self.range_hood_appliance.obj_y.empty_display_size = pc_unit.inch(.5)
        self.range_hood_appliance.obj_z.empty_display_size = pc_unit.inch(.5)

        if not self.range_hood_appliance.obj_x.lock_location[0]:
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.range_hood_appliance.dim_x('width',[width])

        self.update_range_hood_location()

        pc_utils.update_assembly_id_props(self.range_hood_appliance,self)

    def add_left_filler(self):
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_adjustment_width = self.get_prompt("Left Adjustment Width").get_var("left_adjustment_width")
        carcass_type = self.carcasses[0].get_prompt("Carcass Type")
        
        self.left_filler = assemblies_cabinet.add_carcass_part(self)
        self.left_filler.obj_bp["IS_LEFT_FILLER_BP"] = True
        self.left_filler.set_name('Left Filler')
        self.left_filler.loc_x(value=0)
        self.left_filler.loc_y(value=0)
        self.left_filler.loc_z(value=0)
        self.left_filler.dim_x('left_adjustment_width',[left_adjustment_width])
        self.left_filler.dim_y('depth',[depth])
        self.left_filler.dim_z('height',[height])
        pc_utils.flip_normals(self.left_filler)
        material_pointers_cabinet.assign_pointer_to_assembly(self.left_filler,"Cabinet Exposed Surfaces")

        if carcass_type.get_value() in ('Base','Tall'):
            kick_height = self.carcasses[0].get_prompt("Toe Kick Height").get_var("kick_height")
            self.left_filler.loc_z('kick_height',[kick_height])
            self.left_filler.dim_z('height-kick_height',[kick_height])

    def add_right_filler(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        right_adjustment_width = self.get_prompt("Right Adjustment Width").get_var("right_adjustment_width")
        carcass_type = self.carcasses[0].get_prompt("Carcass Type")

        self.right_filler = assemblies_cabinet.add_carcass_part(self)
        self.right_filler.obj_bp["IS_RIGHT_FILLER_BP"] = True
        self.right_filler.set_name('Right Filler')
        self.right_filler.loc_x('width',[width])
        self.right_filler.loc_y(value=0)
        self.right_filler.loc_z(value=0)
        self.right_filler.dim_x('-right_adjustment_width',[right_adjustment_width])
        self.right_filler.dim_y('depth',[depth])
        self.right_filler.dim_z('height',[height])
        material_pointers_cabinet.assign_pointer_to_assembly(self.right_filler,"Cabinet Exposed Surfaces")

        if carcass_type.get_value() in ('Base','Tall'):
            kick_height = self.carcasses[0].get_prompt("Toe Kick Height").get_var("kick_height")
            self.right_filler.loc_z('kick_height',[kick_height])
            self.right_filler.dim_z('height-kick_height',[kick_height])

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
    
    def get_object_from_path(self,path):
        pass

    def draw(self):
        self.create_assembly("Cabinet")
        self.obj_bp[const.CABINET_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.cabinet_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_commands"

        # self.obj_x.location.x = self.width
        # self.obj_y.location.y = -self.depth
        # self.obj_z.location.z = self.height

        # prompts_cabinet.add_cabinet_prompts(self)
        # prompts_cabinet.add_filler_prompts(self)
        # prompts_cabinet.add_thickness_prompts(self)

        # geo_part_path = os.path.join(paths_cabinet.get_geo_parts_paths(),"GeoPart1.blend")
        
        # width = self.obj_x.pyclone.get_var('location.x','width')
        # height = self.obj_z.pyclone.get_var('location.z','height')
        # depth = self.obj_y.pyclone.get_var('location.y','depth')
        # mat_thickness = self.get_prompt("Material Thickness").get_var('mat_thickness')

        # ls_obj = self.add_object_from_file(geo_part_path)
        # ls_obj.name = "Left Side"
        # length = ls_obj.pyclone.get_prompt("Length")
        # length.set_formula('height',[height])
        # part_width = ls_obj.pyclone.get_prompt("Width")
        # part_width.set_formula('fabs(depth)',[depth])        
        # thickness = ls_obj.pyclone.get_prompt("Thickness")
        # thickness.set_formula('mat_thickness',[mat_thickness])        
        # ls_obj.pyclone.rot_y(value=math.radians(-90))
        # ls_obj.pyclone.rot_z(value=math.radians(180))

        # rs_obj = self.add_object_from_file(geo_part_path)
        # rs_obj.name = "Right Side"
        # rs_obj.pyclone.loc_x('width-mat_thickness',[width,mat_thickness])
        # length = rs_obj.pyclone.get_prompt("Length")
        # length.set_formula('height',[height])        
        # part_width = rs_obj.pyclone.get_prompt("Width")
        # part_width.set_formula('fabs(depth)',[depth])           
        # thickness = rs_obj.pyclone.get_prompt("Thickness")
        # thickness.set_formula('mat_thickness',[mat_thickness])              
        # rs_obj.pyclone.rot_y(value=math.radians(-90))
        # rs_obj.pyclone.rot_z(value=math.radians(180))

        # top_obj = self.add_object_from_file(geo_part_path)
        # top_obj.name = "Top"
        # top_obj.pyclone.loc_x('mat_thickness',[mat_thickness])
        # top_obj.pyclone.loc_y('depth',[depth])
        # top_obj.pyclone.loc_z('height',[height])
        # length = top_obj.pyclone.get_prompt("Length")
        # length.set_formula('width-(mat_thickness*2)',[width,mat_thickness])  
        # part_width = top_obj.pyclone.get_prompt("Width")
        # part_width.set_formula('fabs(depth)',[depth])                 
        # thickness = top_obj.pyclone.get_prompt("Thickness")
        # thickness.set_formula('-mat_thickness',[mat_thickness])              
        # top_obj.pyclone.rot_y(value=math.radians(0))
        # top_obj.pyclone.rot_z(value=math.radians(0))

        # top_obj = self.add_object_from_file(geo_part_path)
        # top_obj.name = "Bottom"
        # top_obj.pyclone.loc_x('mat_thickness',[mat_thickness])
        # top_obj.pyclone.loc_y('depth',[depth])
        # length = top_obj.pyclone.get_prompt("Length")
        # length.set_formula('width-(mat_thickness*2)',[width,mat_thickness])  
        # part_width = top_obj.pyclone.get_prompt("Width")
        # part_width.set_formula('fabs(depth)',[depth])                 
        # thickness = top_obj.pyclone.get_prompt("Thickness")
        # thickness.set_formula('mat_thickness',[mat_thickness])              
        # top_obj.pyclone.rot_y(value=math.radians(0))
        # top_obj.pyclone.rot_z(value=math.radians(0))


        self.obj_y['IS_MIRROR'] = True
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
        law = carcass.get_prompt("Left Adjustment Width")
        law.set_formula('left_adjustment_width',[left_adjustment_width])
        raw = carcass.get_prompt("Right Adjustment Width")
        raw.set_formula('right_adjustment_width',[right_adjustment_width])        
        self.carcasses.append(carcass)

        cabinet_type.set_value(carcass.carcass_type)

        if self.carcass.exterior:
            self.carcass.add_insert(self.carcass.exterior)
        if self.carcass.interior:
            self.carcass.add_insert(self.carcass.interior)

        if self.include_countertop:
            self.add_countertop()
            prompts_cabinet.add_sink_prompts(self)
            prompts_cabinet.add_cooktop_prompts(self)            


class Stacked_Cabinet(Cabinet):

    width = pc_unit.inch(18)
    height = pc_unit.inch(34)
    depth = pc_unit.inch(21)

    carcass = None

    is_upper = False
    
    def __init__(self):
        pass

    def draw(self):
        self.create_assembly("Cabinet")
        self.obj_bp[const.CABINET_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.cabinet_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_commands"
        self.obj_y['IS_MIRROR'] = True        
        self.carcasses = []

        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_filler_prompts(self)
        prompts_cabinet.add_stacked_cabinet_prompts(self)     

        bottom_cabinet_height = self.get_prompt("Bottom Cabinet Height")
        bottom_cabinet_height.set_value(self.bottom_cabinet_height)

        cabinet_type = self.get_prompt("Cabinet Type")
        if self.is_upper:
            cabinet_type.set_value("Upper")
        else:
            cabinet_type.set_value("Tall")

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


class Blind_Corner_Cabinet(Cabinet):

    width = pc_unit.inch(18)
    height = pc_unit.inch(34)
    depth = pc_unit.inch(21)

    carcass = None

    is_upper = False
    
    def __init__(self):
        pass

    def draw(self):
        self.create_assembly("Cabinet")
        self.corner_type = "Blind"
        self.obj_bp[const.CABINET_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.cabinet_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_cabinet_commands"
        self.obj_y['IS_MIRROR'] = True        
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

        corner_type = self.get_prompt("Corner Type")
        corner_type.set_value("Blind")

        cabinet_type.set_value(carcass.carcass_type)

        if self.carcass.exterior:
            self.carcass.add_exterior_insert(self.carcass.exterior)
        if self.carcass.interior:
            self.carcass.add_interior_insert(self.carcass.interior)

        if self.include_countertop:
            self.add_countertop()        