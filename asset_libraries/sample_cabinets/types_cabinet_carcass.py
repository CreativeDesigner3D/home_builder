import bpy
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import const_cabinets as const
from . import prompts_cabinet

class Design_Carcass(pc_types.Assembly):

    carcass_type = ""
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
        prompts_cabinet.add_base_assembly_prompts(self)


        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        tkh = self.get_prompt("Toe Kick Height").get_var('tkh') 
        tk_setback = self.get_prompt("Toe Kick Setback").get_var('tk_setback') 
        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)

        if carcass_type.get_value() == "Upper":
            carcass = assemblies_cabinet.add_design_carcass(self)
            carcass.set_name("Design Carcass")
            carcass.dim_x('width',[width])
            carcass.dim_y('depth',[depth])
            carcass.dim_z('height',[height])
            carcass.loc_z(value=0)
        else:
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


class Base_Design_Carcass(Design_Carcass):
    carcass_type = "Base"


class Tall_Design_Carcass(Design_Carcass):
    carcass_type = "Tall"    


class Upper_Design_Carcass(Design_Carcass):
    carcass_type = "Upper"       