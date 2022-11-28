import bpy
import os
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import utils_cabinet
from . import prompts_cabinet
from . import assemblies_cabinet
from . import material_pointers_cabinet
from . import types_countertop
from . import types_cabinet_exteriors
from . import paths_cabinet
from . import const_cabinets as const

def get_range_hood(category,assembly_name):
    ASSET_DIR = paths_cabinet.get_range_hood_paths()
    if assembly_name == "":
        return os.path.join(ASSET_DIR,"_Sample","Generic Range Hood.blend")  
    else:
        return os.path.join(ASSET_DIR, category, assembly_name + ".blend")   

class Dishwasher(pc_types.Assembly):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if const.DISHWASHER_TAG in child:
                    self.dishwasher = pc_types.Assembly(child)
                if const.COUNTERTOP_TAG in child:
                    self.countertop = pc_types.Assembly(child)       

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

    def add_dishwasher(self):
        path = os.path.join(os.path.dirname(__file__),'library','Appliances','assets','Dishwasher.blend')
        self.dishwasher = pc_types.Assembly(self.add_assembly_from_file(path))
        self.dishwasher.obj_bp[const.DISHWASHER_TAG] = True
        
        if self.dishwasher.obj_x.lock_location[0]:
            self.obj_x.location.x = self.dishwasher.obj_x.location.x
        else:
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.dishwasher.dim_x('width',[width])
        
        if self.dishwasher.obj_y.lock_location[1]:
            self.obj_y.location.y = self.dishwasher.obj_y.location.y
        else:
            depth = self.obj_y.pyclone.get_var('location.y','depth')
            self.dishwasher.dim_y('depth',[depth])

        if self.dishwasher.obj_z.lock_location[2]:
            self.obj_z.location.z = self.dishwasher.obj_z.location.z
        else:
            height = self.obj_z.pyclone.get_var('location.z','height')
            self.dishwasher.dim_z('height',[height])   
        
        pc_utils.update_assembly_id_props(self.dishwasher,self)

    def draw(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp[const.APPLIANCE_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.dishwasher_prompts"   
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_appliance_commands"    
        self.obj_y['IS_MIRROR'] = True

        self.add_dishwasher()
        self.add_countertop()      

        self.obj_x.location.x = pc_unit.inch(24)
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

class Range(pc_types.Assembly):

    range_appliance = None
    range_hood_appliance = None
    
    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if const.RANGE_TAG in child:
                    self.range_appliance = pc_types.Assembly(child)
                if const.RANGE_HOOD_TAG in child:
                    self.range_hood_appliance = pc_types.Assembly(child)       

    def update_range_hood_location(self):
        if self.range_hood_appliance:
            self.range_hood_appliance.obj_bp.location.x = (self.obj_x.location.x/2) - (self.range_hood_appliance.obj_x.location.x)/2
            self.range_hood_appliance.obj_bp.location.z = pc_unit.inch(70)

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
        #Location must be updated twice for some reason
        self.update_range_hood_location()

        pc_utils.update_assembly_id_props(self.range_hood_appliance,self)

    def add_range(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        path = os.path.join(os.path.dirname(__file__),'library','Appliances','assets','Range.blend')
        self.range_appliance = pc_types.Assembly(self.add_assembly_from_file(path))
        self.range_appliance.obj_bp[const.RANGE_TAG] = True
        self.range_appliance.obj_x.empty_display_size = pc_unit.inch(.5)
        self.range_appliance.obj_y.empty_display_size = pc_unit.inch(.5)
        self.range_appliance.obj_z.empty_display_size = pc_unit.inch(.5)

        self.obj_x.location.x = self.range_appliance.obj_x.location.x
        self.obj_y.location.y = self.range_appliance.obj_y.location.y
        self.obj_z.location.z = self.range_appliance.obj_z.location.z
        self.obj_x.lock_location[0] = self.range_appliance.obj_x.lock_location[0]
        self.obj_y.lock_location[1] = self.range_appliance.obj_y.lock_location[1]
        self.obj_z.lock_location[2] = self.range_appliance.obj_z.lock_location[2]

        if self.range_appliance.obj_x.lock_location[0]:
            self.obj_x.location.x = self.range_appliance.obj_x.location.x
        else:
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.range_appliance.dim_x('width',[width])
        
        if self.range_appliance.obj_y.lock_location[1]:
            self.obj_y.location.y = self.range_appliance.obj_y.location.y
        else:
            depth = self.obj_y.pyclone.get_var('location.y','depth')
            self.range_appliance.dim_y('depth',[depth])

        if self.range_appliance.obj_x.lock_location[2]:
            self.obj_z.location.z = self.range_appliance.obj_z.location.z
        else:
            height = self.obj_z.pyclone.get_var('location.z','height')
            self.range_appliance.dim_z('height',[height])   
        
        pc_utils.update_assembly_id_props(self.range_appliance,self)

    def draw(self):
        self.create_assembly("Range")
        self.obj_bp[const.APPLIANCE_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.range_prompts"
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_appliance_commands"
        self.obj_y['IS_MIRROR'] = True
        self.add_prompt("Add Range Hood",'CHECKBOX',False)
        self.add_range()


class Refrigerator(pc_types.Assembly):

    refrigerator = None
    doors = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if const.REFRIGERATOR_TAG in child:
                    self.refrigerator = pc_types.Assembly(child)   
                if const.DOOR_INSERT_TAG in child:
                    self.doors = pc_types.Assembly(child)

    def add_refrigerator(self,assembly_name=""):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        material_thickness = self.get_prompt("Material Thickness")
        m_thickness = material_thickness.get_var('m_thickness')
        carcass_height = self.get_prompt("Carcass Height")
        c_height = carcass_height.get_var('c_height')

        path = os.path.join(os.path.dirname(__file__),'library','Appliances','assets','Refrigerator.blend')
        self.refrigerator = pc_types.Assembly(self.add_assembly_from_file(path))
        self.refrigerator.obj_bp[const.REFRIGERATOR_TAG] = True

        if self.refrigerator.obj_x.lock_location[0]:
            self.obj_x.location.x = self.refrigerator.obj_x.location.x + material_thickness.get_value()*2
        else:
            self.obj_x.location.x = pc_unit.inch(36) + material_thickness.get_value()*2
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.refrigerator.dim_x('width-m_thickness*2',[width,m_thickness])
        
        if self.refrigerator.obj_y.lock_location[1]:
            self.obj_y.location.y = self.refrigerator.obj_y.location.y
        else:
            self.obj_y.location.y = -props.tall_cabinet_depth
            depth = self.obj_y.pyclone.get_var('location.y','depth')
            self.refrigerator.dim_y('depth',[depth])

        if self.refrigerator.obj_z.lock_location[2]:
            self.obj_z.location.z = self.refrigerator.obj_z.location.z + carcass_height.get_value()
        else:
            self.obj_z.location.z = props.tall_cabinet_height 
            height = self.obj_z.pyclone.get_var('location.z','height')
            self.refrigerator.dim_z('height-c_height',[height,c_height])   

        y_loc = self.get_prompt("Refrigerator Y Location").get_var('y_loc')

        self.refrigerator.loc_y('-y_loc',[y_loc])   
        self.refrigerator.loc_x('m_thickness',[m_thickness])   
        pc_utils.update_assembly_id_props(self.refrigerator,self)

    def add_carcass(self):
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        width = self.obj_x.pyclone.get_var('location.x','width')
        left_finished_end = self.get_prompt("Left Finished End")
        right_finished_end = self.get_prompt("Right Finished End")
        finished_top = self.get_prompt("Finished Top")
        finished_back = self.get_prompt("Finished Back")
        finished_bottom = self.get_prompt("Finished Bottom")
        material_thickness = self.get_prompt("Material Thickness").get_var('material_thickness')
        carcass_height = self.get_prompt("Carcass Height").get_var('carcass_height')
        remove_carcass = self.get_prompt("Remove Cabinet Carcass").get_var('remove_carcass')

        left_side = assemblies_cabinet.add_carcass_part_assembly(self)
        left_side.obj_bp["IS_LEFT_SIDE_BP"] = True
        left_side.set_name('Left Side')
        left_side.loc_x(value=0)
        left_side.loc_y(value=0)
        left_side.loc_z(value=0)
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_x('height',[height])
        left_side.dim_y('depth',[depth])
        left_side.dim_z('-material_thickness',[material_thickness])
        hide = left_side.get_prompt("Hide")
        hide.set_formula('remove_carcass',[remove_carcass])

        right_side = assemblies_cabinet.add_carcass_part_assembly(self)
        right_side.obj_bp["IS_RIGHT_SIDE_BP"] = True
        right_side.set_name('Right Side')
        right_side.loc_x('width',[width])
        right_side.loc_y(value=0)
        right_side.loc_z(value=0)
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_x('height',[height])
        right_side.dim_y('depth',[depth])
        right_side.dim_z('material_thickness',[material_thickness])
        hide = right_side.get_prompt("Hide")
        hide.set_formula('remove_carcass',[remove_carcass])        
        pc_utils.flip_normals(right_side)
        material_pointers_cabinet.update_side_material(left_side,left_finished_end.get_value(),finished_back.get_value(),finished_top.get_value(),finished_bottom.get_value())
        material_pointers_cabinet.update_side_material(right_side,right_finished_end.get_value(),finished_back.get_value(),finished_top.get_value(),finished_bottom.get_value())

        top = assemblies_cabinet.add_carcass_part_assembly(self)
        top.obj_bp["IS_TOP_BP"] = True
        top.set_name('Top')
        top.loc_x('material_thickness',[material_thickness])
        top.loc_y(value = 0)
        top.loc_z('height',[height])
        top.rot_y(value = 0)
        top.dim_x('width-(material_thickness*2)',[width,material_thickness])
        top.dim_y('depth',[depth])
        top.dim_z('-material_thickness',[material_thickness])
        hide = top.get_prompt("Hide")
        hide.set_formula('remove_carcass',[remove_carcass])        
        material_pointers_cabinet.update_top_material(top,finished_back.get_value(),finished_top.get_value())
        pc_utils.flip_normals(top)

        bottom = assemblies_cabinet.add_carcass_part_assembly(self)
        bottom.obj_bp["IS_BOTTOM_BP"] = True
        bottom.set_name('Bottom')
        bottom.loc_x('material_thickness',[material_thickness])
        bottom.loc_y(value = 0)
        bottom.loc_z('height-carcass_height',[height,carcass_height])
        bottom.rot_y(value = 0)
        bottom.dim_x('width-(material_thickness*2)',[width,material_thickness])
        bottom.dim_y('depth',[depth])
        bottom.dim_z('material_thickness',[material_thickness])
        hide = bottom.get_prompt("Hide")
        hide.set_formula('remove_carcass',[remove_carcass])        
        material_pointers_cabinet.update_bottom_material(bottom,finished_back.get_value(),finished_top.get_value())

    def draw(self):
        self.create_assembly("Refrigerator")
        self.obj_bp[const.APPLIANCE_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_cabinets.refrigerator_prompts"    
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_appliance_commands"  
        self.obj_y['IS_MIRROR'] = True

        self.add_prompt("Refrigerator Y Location",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Remove Cabinet Carcass",'CHECKBOX',False)
        self.add_prompt("Carcass Height",'DISTANCE',pc_unit.inch(15))        
        prompts_cabinet.add_carcass_prompts(self)
        prompts_cabinet.add_thickness_prompts(self)

        self.add_refrigerator()
        self.add_carcass()

        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        width = self.obj_x.pyclone.get_var('location.x','width')
        material_thickness = self.get_prompt("Material Thickness").get_var('material_thickness')
        carcass_height = self.get_prompt("Carcass Height").get_var('carcass_height')
        remove_carcass = self.get_prompt("Remove Cabinet Carcass").get_var('remove_carcass')

        doors = types_cabinet_exteriors.Doors()
        doors.carcass_type = 'Upper'
        doors.door_type = 'Upper'
        doors.door_swing = 2
        insert = self.add_assembly(doors)
        insert.loc_x('material_thickness',[material_thickness])
        insert.loc_y('depth',[depth])
        insert.loc_z('height-carcass_height+material_thickness',[height,carcass_height,material_thickness])
        insert.dim_x('width-(material_thickness*2)',[width,material_thickness])
        insert.dim_y('fabs(depth)-material_thickness',[depth,material_thickness])
        insert.dim_z('carcass_height-material_thickness*2',[carcass_height,material_thickness])
        hide = insert.get_prompt('Hide')
        hide.set_formula('remove_carcass',[remove_carcass])        

