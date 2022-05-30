import bpy
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import utils_cabinet
from . import prompts_cabinet

def add_cabinet_shelf(assembly,is_exposed=False):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    shelf_qty = assembly.get_prompt("Shelf Quantity").get_var("shelf_qty")
    shelf_clip_gap = assembly.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
    shelf_setback = assembly.get_prompt("Shelf Setback").get_var("shelf_setback")

    if is_exposed:
        shelf = assemblies_cabinet.add_exposed_shelves_part(assembly)
    else:
        shelf = assemblies_cabinet.add_interior_shelves_part(assembly)
    shelf.set_name('Shelf')
    shelf.loc_x('shelf_clip_gap',[shelf_clip_gap])
    shelf.loc_y('shelf_setback',[shelf_setback])
    shelf.loc_z('(height-(material_thickness*shelf_qty))/(shelf_qty+1)',[height,material_thickness,shelf_qty])
    shelf.dim_x('width-(shelf_clip_gap*2)',[width,shelf_clip_gap])
    shelf.dim_y('depth-shelf_setback',[depth,shelf_setback])
    shelf.dim_z('material_thickness',[material_thickness])
    z_quantity = shelf.get_prompt("Z Quantity")
    z_offset = shelf.get_prompt("Z Offset")
    hide = shelf.get_prompt("Hide")
    z_quantity.set_formula('shelf_qty',[shelf_qty])
    z_offset.set_formula('((height-(material_thickness*shelf_qty))/(shelf_qty+1))+material_thickness',[height,material_thickness,shelf_qty])
    hide.set_formula('IF(shelf_qty==0,True,False)',[shelf_qty])
    return shelf

def add_shelf_holes(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    shelf_setback = assembly.get_prompt("Shelf Setback").get_var("shelf_setback")

    holes = assemblies_cabinet.add_shelf_holes(assembly)
    holes.loc_y('shelf_setback',[shelf_setback])
    holes.dim_x('width',[width])
    holes.dim_y('depth-shelf_setback',[depth,shelf_setback])
    holes.dim_z('height',[height])    


class Cabinet_Interior(pc_types.Assembly):
    carcass_type = '' #Base, Tall, Upper

    def draw_prompts(self,layout,context):
        shelf_quantity = self.get_prompt("Shelf Quantity")
        shelf_setback = self.get_prompt("Shelf Setback")
        
        if shelf_quantity:
            shelf_quantity.draw(layout,allow_edit=False)

        if shelf_setback:
            shelf_setback.draw(layout,allow_edit=False)  


class Shelves(Cabinet_Interior):

    shelf_qty = 1

    def draw(self):

        self.create_assembly("Shelves")
        self.obj_bp["IS_SHELVES_BP"] = True
        self.obj_bp["IS_INTERIOR_BP"] = True        

        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_thickness_prompts(self)
        prompts_cabinet.add_interior_shelf_prompts(self)

        add_cabinet_shelf(self)
        add_shelf_holes(self)

        shelf_qty = self.get_prompt("Shelf Quantity")
        if shelf_qty:
            shelf_qty.set_value(self.shelf_qty)


class Exposed_Shelves(Cabinet_Interior):

    shelf_qty = 1

    def draw(self):

        self.create_assembly("Shelves")
        self.obj_bp["IS_SHELVES_BP"] = True
        self.obj_bp["IS_INTERIOR_BP"] = True        

        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_thickness_prompts(self)
        prompts_cabinet.add_interior_shelf_prompts(self)

        add_cabinet_shelf(self,is_exposed=True)
        add_shelf_holes(self)

        shelf_qty = self.get_prompt("Shelf Quantity")
        if shelf_qty:
            shelf_qty.set_value(self.shelf_qty)