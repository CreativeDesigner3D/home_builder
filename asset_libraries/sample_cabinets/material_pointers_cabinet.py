import bpy
import os

WOOD_FINISHED_PATH = os.path.join(os.path.dirname(__file__),'library','Wood Finished','library.blend')   

CABINET_POINTERS = []
CABINET_POINTERS.append(("Cabinet Unfinished Surfaces",WOOD_FINISHED_PATH,"Candlelight"))
CABINET_POINTERS.append(("Cabinet Unfinished Edges",WOOD_FINISHED_PATH,"Candlelight"))
CABINET_POINTERS.append(("Cabinet Exposed Surfaces",WOOD_FINISHED_PATH,"Cayenne Maple"))
CABINET_POINTERS.append(("Cabinet Exposed Edges",WOOD_FINISHED_PATH,"Cayenne Maple"))
CABINET_POINTERS.append(("Cabinet Interior Surfaces",WOOD_FINISHED_PATH,"Candlelight"))
CABINET_POINTERS.append(("Cabinet Interior Edges",WOOD_FINISHED_PATH,"Candlelight"))
CABINET_POINTERS.append(("Cabinet Door Surfaces",WOOD_FINISHED_PATH,"Cayenne Maple"))
CABINET_POINTERS.append(("Cabinet Door Edges",WOOD_FINISHED_PATH,"Cayenne Maple"))
CABINET_POINTERS.append(("Cabinet Pull Finish",WOOD_FINISHED_PATH,"Candlelight"))

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
        p = pointers[pointer.pointer_name]
        if index + 1 <= len(obj.material_slots):
            slot = obj.material_slots[index]
            slot.material = get_material(p.library_path,p.material_name)

def assign_materials_to_assembly(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            assign_materials_to_object(child)

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