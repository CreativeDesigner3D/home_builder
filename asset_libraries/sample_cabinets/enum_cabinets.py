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