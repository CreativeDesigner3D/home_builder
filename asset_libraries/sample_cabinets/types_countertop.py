from pc_lib import pc_types, pc_unit, pc_utils
from . import prompts_cabinet
from . import assemblies_cabinet

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