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

def get_sink_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Sinks')

def get_faucet_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Faucets')

def get_cooktop_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cooktops')

def get_range_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Ranges')

def get_range_hood_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Range Hoods')

def get_dishwasher_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Dishwashers')

def get_refrigerator_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Refrigerators')

def get_built_in_oven_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Built In Ovens')

def get_built_in_microwave_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Built In Microwaves')

def get_geo_parts_paths():
    return os.path.join(os.path.dirname(__file__),'geo_objects')

def get_current_handle_path():
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    category_name = props.cabinet_handle_category
    item_name = props.cabinet_handle        
    path = os.path.join(get_handles_paths(),category_name,item_name + ".blend")
    return path

def get_current_door_path():
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    if props.show_door_library:
        category_name = props.cabinet_door_category
        item_name = props.cabinet_door        
        path = os.path.join(get_door_paths(),category_name,item_name + ".blend")
        return path    
    else:
        return os.path.join(get_assembly_path(),"Part.blend")