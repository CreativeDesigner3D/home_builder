from os import path
from .pc_lib import pc_types
from . import cabinet_paths
from . import cabinet_types
from . import cabinet_material_pointers

def add_design_carcass(assembly):
    part_path = path.join(cabinet_paths.get_assembly_path(),"Design Carcass.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_DESIGN_CARCASS_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    cabinet_material_pointers.assign_design_carcass_pointers(part)
    cabinet_material_pointers.assign_materials_to_assembly(part)
    return part

def add_base_assembly(assembly):
    part_path = path.join(cabinet_paths.get_assembly_path(),"Design Base Assembly.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_DESIGN_BASE_ASSEMBLY_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    cabinet_material_pointers.assign_design_base_assembly_pointers(part)
    cabinet_material_pointers.assign_materials_to_assembly(part)
    return part    

def add_door_assembly(assembly):
    part_path = path.join(cabinet_paths.get_assembly_path(),"Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_DOOR_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    cabinet_material_pointers.assign_design_base_assembly_pointers(part)
    cabinet_material_pointers.assign_materials_to_assembly(part)
    return part       