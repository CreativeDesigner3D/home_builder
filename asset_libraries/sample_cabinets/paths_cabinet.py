import bpy
import os
from . import utils_cabinet

def get_assembly_path():
    return os.path.join(os.path.dirname(__file__),'assemblies')

def get_handles_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cabinet Handles')

def get_door_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cabinet Doors')    

def get_molding_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Moldings')

def get_handle_path_by_pointer(pointer):
    if pointer and pointer.category_name != "" and pointer.item_name != "":
        category_name = pointer.category_name
        item_name = pointer.item_name
    else:
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        category_name = props.cabinet_handle_category
        item_name = props.cabinet_handle        
    path = os.path.join(get_handles_paths(),category_name,item_name + ".blend")
    return path