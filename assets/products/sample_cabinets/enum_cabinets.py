import bpy
import os
from pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import paths_cabinet

preview_collections = {}
preview_collections["handle_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["handle_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cabinet_door_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cabinet_door_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["molding_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["molding_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["sink_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["sink_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["faucet_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["faucet_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_hood_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_hood_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["dishwasher_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["dishwasher_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["refrigerator_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["refrigerator_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cooktop_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cooktop_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["built_in_oven_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["built_in_oven_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["built_in_microwave_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["built_in_microwave_items"] = pc_pointer_utils.create_image_preview_collection()

#CABINET HANDLES  
def enum_cabinet_handle_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_handles_paths()
    pcoll = preview_collections["handle_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_cabinet_handle_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_handles_paths(),self.cabinet_handle_category)
    pcoll = preview_collections["handle_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_cabinet_handle_category(self,context):
    if preview_collections["handle_items"]:
        bpy.utils.previews.remove(preview_collections["handle_items"])
        preview_collections["handle_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_cabinet_handle_names(self,context)           

#CABINET DOORS    
def enum_cabinet_door_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_door_paths()
    pcoll = preview_collections["cabinet_door_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_cabinet_door_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_door_paths(),self.cabinet_door_category)
    pcoll = preview_collections["cabinet_door_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_cabinet_door_category(self,context):
    if preview_collections["cabinet_door_items"]:
        bpy.utils.previews.remove(preview_collections["cabinet_door_items"])
        preview_collections["cabinet_door_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_cabinet_door_names(self,context)

#MOLDING    
def enum_molding_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_molding_paths()
    pcoll = preview_collections["molding_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_molding_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_molding_paths(),self.molding_category)
    pcoll = preview_collections["molding_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_molding_category(self,context):
    if preview_collections["molding_items"]:
        bpy.utils.previews.remove(preview_collections["molding_items"])
        preview_collections["molding_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_molding_names(self,context)    

#SINK    
def enum_sink_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_sink_paths()
    pcoll = preview_collections["sink_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_sink_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_sink_paths(),self.sink_category)
    pcoll = preview_collections["sink_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_sink_category(self,context):
    if preview_collections["sink_items"]:
        bpy.utils.previews.remove(preview_collections["sink_items"])
        preview_collections["sink_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_sink_names(self,context) 

#FAUCET    
def enum_faucet_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_faucet_paths()
    pcoll = preview_collections["faucet_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_faucet_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_faucet_paths(),self.faucet_category)
    pcoll = preview_collections["faucet_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_faucet_category(self,context):
    if preview_collections["faucet_items"]:
        bpy.utils.previews.remove(preview_collections["faucet_items"])
        preview_collections["faucet_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_faucet_names(self,context)  

#COOKTOP    
def enum_cooktop_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_cooktop_paths()
    pcoll = preview_collections["cooktop_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_cooktop_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_cooktop_paths(),self.cooktop_category)
    pcoll = preview_collections["cooktop_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_cooktop_category(self,context):
    if preview_collections["cooktop_items"]:
        bpy.utils.previews.remove(preview_collections["cooktop_items"])
        preview_collections["cooktop_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_cooktop_names(self,context)      

#RANGE    
def enum_range_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_range_paths()
    pcoll = preview_collections["range_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_range_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_range_paths(),self.range_category)
    pcoll = preview_collections["range_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_range_category(self,context):
    if preview_collections["range_items"]:
        bpy.utils.previews.remove(preview_collections["range_items"])
        preview_collections["range_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_range_names(self,context)      

#RANGE HOOD    
def enum_range_hood_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_range_hood_paths()
    pcoll = preview_collections["range_hood_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_range_hood_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_range_hood_paths(),self.range_hood_category)
    pcoll = preview_collections["range_hood_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_range_hood_category(self,context):
    if preview_collections["range_hood_items"]:
        bpy.utils.previews.remove(preview_collections["range_hood_items"])
        preview_collections["range_hood_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_range_hood_names(self,context)      

#DISHWASHER    
def enum_dishwasher_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_dishwasher_paths()
    pcoll = preview_collections["dishwasher_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_dishwasher_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_dishwasher_paths(),self.dishwasher_category)
    pcoll = preview_collections["dishwasher_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_dishwasher_category(self,context):
    if preview_collections["dishwasher_items"]:
        bpy.utils.previews.remove(preview_collections["dishwasher_items"])
        preview_collections["dishwasher_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_dishwasher_names(self,context)      

#REFRIGERATOR    
def enum_refrigerator_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_refrigerator_paths()
    pcoll = preview_collections["refrigerator_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_refrigerator_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_refrigerator_paths(),self.refrigerator_category)
    pcoll = preview_collections["refrigerator_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_refrigerator_category(self,context):
    if preview_collections["refrigerator_items"]:
        bpy.utils.previews.remove(preview_collections["refrigerator_items"])
        preview_collections["refrigerator_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_refrigerator_names(self,context)       

#BUILT_IN_OVENS    
def enum_built_in_oven_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_built_in_oven_paths()
    pcoll = preview_collections["built_in_oven_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_built_in_oven_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_built_in_oven_paths(),self.built_in_oven_category)
    pcoll = preview_collections["built_in_oven_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_built_in_oven_category(self,context):
    if preview_collections["built_in_oven_items"]:
        bpy.utils.previews.remove(preview_collections["built_in_oven_items"])
        preview_collections["built_in_oven_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_built_in_oven_names(self,context)       

#BUILT_IN_MICROWAVES    
def enum_built_in_microwave_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_cabinet.get_built_in_microwave_paths()
    pcoll = preview_collections["built_in_microwave_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_built_in_microwave_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_cabinet.get_built_in_microwave_paths(),self.built_in_microwave_category)
    pcoll = preview_collections["built_in_microwave_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_built_in_microwave_category(self,context):
    if preview_collections["built_in_microwave_items"]:
        bpy.utils.previews.remove(preview_collections["built_in_microwave_items"])
        preview_collections["built_in_microwave_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_built_in_microwave_names(self,context)           