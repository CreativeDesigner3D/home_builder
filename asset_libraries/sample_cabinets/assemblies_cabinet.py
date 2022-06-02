from os import path
from pc_lib import pc_types, pc_utils
from . import paths_cabinet
from . import material_pointers_cabinet

def add_design_carcass(assembly,exposed_interior=False):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Design Carcass.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_DESIGN_CARCASS_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    if exposed_interior:
        material_pointers_cabinet.assign_open_design_carcass_pointers(part)
    else:
        material_pointers_cabinet.assign_design_carcass_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_base_assembly(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Design Base Assembly.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_DESIGN_BASE_ASSEMBLY_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    material_pointers_cabinet.assign_design_base_assembly_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part    

def add_door_assembly(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_DOOR_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    material_pointers_cabinet.assign_door_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part       

def add_carcass_part_assembly(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_carcass_part_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part           

def add_blind_panel_part_assembly(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_blind_panel_part_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part      

def add_carcass_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part 

def add_closet_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_closet_array_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Z Array Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)     
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_metal_shoe_shelf_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Metal Shoe Shelf.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp["IS_METAL_SHOE_SHELF_FENCE_BP"] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001
    part.add_prompt("Accessory Name",'TEXT',"")
    material_pointers_cabinet.assign_hanging_rods_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_shelf_holes(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Shelf Holes.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001   
    material_pointers_cabinet.assign_pointer_to_assembly(part,"Shelf Holes")
    return part    

def add_corner_notch_countertop_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Corner Notch Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    assembly.add_assembly(part)
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_pointer_to_assembly(part,"Countertop Surface")
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part    

def add_corner_notch_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Corner Notch Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part 

def add_corner_radius_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Corner Radius Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part        

def add_countertop_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    assembly.add_assembly(part)
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_pointer_to_assembly(part,"Countertop Surface")
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part    

def add_closet_array_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Z Array Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)    
    part.add_prompt("Left Depth",'DISTANCE',0)
    part.add_prompt("Right Depth",'DISTANCE',0)      
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_interior_shelves_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Z Array Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)        
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_cabinet_shelf_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_exposed_shelves_part(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Z Array Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)        
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_double_sided_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part

def add_closet_opening(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Opening.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_OPENING_BP'] = True
    assembly.add_assembly(part)
    part.add_prompt("Left Depth",'DISTANCE',0)
    part.add_prompt("Right Depth",'DISTANCE',0)
    part.add_prompt("Back Inset",'DISTANCE',0)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001  
    for child in part.obj_bp.children:
        if child.type == 'MESH':
            child['IS_OPENING_MESH'] = True
    return part       

def add_closet_hangers(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Hangers.blend")
    if path.exists(part_path):
        part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
        part.obj_bp['IS_HANGERS_BP'] = True
        assembly.add_assembly(part)
        part.obj_bp.empty_display_size = .001
        part.obj_x.empty_display_size = .001
        part.obj_y.empty_display_size = .001
        part.obj_z.empty_display_size = .001
        part.obj_prompts.empty_display_size = .001    
        pc_utils.add_bevel(part)
        return part        

def add_closet_oval_hanging_rod(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Oval Hanging Rod.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_HANGING_ROD_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    pc_utils.add_bevel(part)
    material_pointers_cabinet.assign_hanging_rods_pointers(part)
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part        

def add_wire_basket(assembly):
    part_path = path.join(paths_cabinet.get_assembly_path(),"Wire Basket.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_WIRE_BASKET_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    material_pointers_cabinet.assign_pointer_to_assembly(part,"Wire Baskets")
    material_pointers_cabinet.assign_materials_to_assembly(part)
    return part          