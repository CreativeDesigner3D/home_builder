import bpy
import os
from pc_lib import pc_types

SAMPLE_CABINET_MATERIALS = os.path.join(os.path.dirname(__file__),'library','Sample Cabinet Materials','library.blend')   

CABINET_POINTERS = []
CABINET_POINTERS.append(("Cabinet Unfinished Surfaces",SAMPLE_CABINET_MATERIALS,"Particle Board"))
CABINET_POINTERS.append(("Cabinet Unfinished Edges",SAMPLE_CABINET_MATERIALS,"Particle Board"))
CABINET_POINTERS.append(("Cabinet Exposed Surfaces",SAMPLE_CABINET_MATERIALS,"Autumn Leaves"))
CABINET_POINTERS.append(("Cabinet Exposed Edges",SAMPLE_CABINET_MATERIALS,"Autumn Leaves"))
CABINET_POINTERS.append(("Cabinet Interior Surfaces",SAMPLE_CABINET_MATERIALS,"White Melamine"))
CABINET_POINTERS.append(("Cabinet Interior Edges",SAMPLE_CABINET_MATERIALS,"White Melamine"))
CABINET_POINTERS.append(("Cabinet Door Surfaces",SAMPLE_CABINET_MATERIALS,"Autumn Leaves"))
CABINET_POINTERS.append(("Cabinet Door Edges",SAMPLE_CABINET_MATERIALS,"Autumn Leaves"))
CABINET_POINTERS.append(("Molding",SAMPLE_CABINET_MATERIALS,"Autumn Leaves"))
CABINET_POINTERS.append(("Cabinet Pull Finish",SAMPLE_CABINET_MATERIALS,"Polished Chrome"))
CABINET_POINTERS.append(("Countertop Surface",SAMPLE_CABINET_MATERIALS,"Midnight Granite"))
CABINET_POINTERS.append(("Shelf Holes",SAMPLE_CABINET_MATERIALS,"Black Melamine"))
CABINET_POINTERS.append(("Hanging Rod",SAMPLE_CABINET_MATERIALS,"Polished Chrome"))
CABINET_POINTERS.append(("Wire Baskets",SAMPLE_CABINET_MATERIALS,"Polished Chrome"))

def get_material(library_path,material_name):
    if material_name in bpy.data.materials:
        return bpy.data.materials[material_name]

    if os.path.exists(library_path):

        with bpy.data.libraries.load(library_path) as (data_from, data_to):
            for mat in data_from.materials:
                if mat == material_name:
                    data_to.materials = [mat]
                    break    
        
        for mat in data_to.materials:
            return mat

def assign_materials_to_object(obj):
    scene_props = bpy.context.scene.home_builder  
    pointers = scene_props.material_pointers  
    for index, pointer in enumerate(obj.pyclone.pointers):
        if pointer.pointer_name in pointers:
            p = pointers[pointer.pointer_name]
            if index + 1 <= len(obj.material_slots):
                slot = obj.material_slots[index]
                slot.material = get_material(p.library_path,p.material_name)

def assign_materials_to_assembly(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            assign_materials_to_object(child)

def assign_pointer_to_object(obj,pointer_name):
    if len(obj.pyclone.pointers) == 0:
        bpy.ops.pc_material.add_material_slot(object_name=obj.name)    
    for index, pointer in enumerate(obj.pyclone.pointers):  
        pointer.pointer_name = pointer_name  
    assign_materials_to_object(obj)  

def assign_pointer_to_assembly(assembly,pointer_name):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            assign_pointer_to_object(child,pointer_name)

def assign_design_carcass_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Interior':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Edges':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Left':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"     
                if pointer.name == 'Right':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"    
                if pointer.name == 'Back':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"    

def assign_open_design_carcass_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Interior':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Edges':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Left':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"     
                if pointer.name == 'Right':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"    
                if pointer.name == 'Back':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"    

def assign_double_sided_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Exposed Edges"      
                if pointer.name == 'Notch':
                    pointer.pointer_name = "Cabinet Exposed Edges"   
                    
def assign_carcass_part_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Unfinished Edges"     

def assign_blind_panel_part_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Unfinished Edges"  

def assign_design_base_assembly_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'Left':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"     
                if pointer.name == 'Right':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"    
                if pointer.name == 'Front':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"                       
                if pointer.name == 'Back':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"                   

def assign_door_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Door Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Door Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Door Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Door Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Door Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Door Edges"

def assign_cabinet_shelf_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Interior Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Interior Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Interior Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Interior Edges" 

def assign_hanging_rods_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                pointer.pointer_name = "Hanging Rod"     

def update_side_material(assembly,is_finished_end,is_finished_back,is_finished_top,is_finished_bottom):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_end:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"          
                if pointer.name == 'W1':
                    if is_finished_bottom:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"     
                if pointer.name == 'W2':
                    if is_finished_top:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"    
    assign_materials_to_assembly(assembly)

def update_top_material(assembly,is_finished_back,is_finished_top):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_top:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"           
    assign_materials_to_assembly(assembly)

def update_bottom_material(assembly,is_finished_back,is_finished_bottom):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_bottom:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"           
    assign_materials_to_assembly(assembly)

def update_cabinet_back_material(assembly,is_finished_back):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name in {'L1','L2','W1','W2'}:
                    pointer.pointer_name = "Cabinet Unfinished Edges"

    assign_materials_to_assembly(assembly)

def update_design_carcass_pointers(assembly,is_finished_left,is_finished_right,is_finished_back,is_finished_top,is_finished_bottom):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Interior':
                    parent_carcass = pc_types.Assembly(assembly.obj_bp.parent)
                    is_exposed_interior = parent_carcass.get_prompt("Is Exposed Interior")
                    if is_exposed_interior:
                        if is_exposed_interior.get_value():
                            pointer.pointer_name = "Cabinet Exposed Surfaces"
                        else:
                            pointer.pointer_name = "Cabinet Interior Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Edges':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'Top':
                    if is_finished_top:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'Bottom':
                    if is_finished_bottom:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'Left':
                    if is_finished_left:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"   
                if pointer.name == 'Right':
                    if is_finished_right:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces" 
                if pointer.name == 'Back':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces" 
    assign_materials_to_assembly(assembly)

def update_design_base_assembly_pointers(assembly,is_finished_left,is_finished_right,is_finished_back):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Left':
                    if is_finished_left:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'Right':
                    if is_finished_right:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'Back':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Surfaces"
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"   
    assign_materials_to_assembly(assembly)                                                                      