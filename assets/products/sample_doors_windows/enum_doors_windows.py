import bpy
import os
from pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import paths_doors_windows

preview_collections = {}
preview_collections["entry_door_panel_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_panel_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_frame_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_frame_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_handle_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_handle_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_insert_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_insert_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_frame_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_frame_items"] = pc_pointer_utils.create_image_preview_collection()

#ENTRY DOOR PANELS     
def enum_entry_door_panel_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_doors_windows.get_entry_door_panel_path()
    pcoll = preview_collections["entry_door_panel_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_entry_door_panels_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_doors_windows.get_entry_door_panel_path(),self.entry_door_panel_category)
    pcoll = preview_collections["entry_door_panel_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_entry_door_panel_category(self,context):
    if preview_collections["entry_door_panel_items"]:
        bpy.utils.previews.remove(preview_collections["entry_door_panel_items"])
        preview_collections["entry_door_panel_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_entry_door_panels_names(self,context)           

#ENTRY DOOR FRAMES     
def enum_entry_door_frame_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_doors_windows.get_entry_door_frame_path()
    pcoll = preview_collections["entry_door_frame_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_entry_door_frame_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_doors_windows.get_entry_door_frame_path(),self.entry_door_frame_category)
    pcoll = preview_collections["entry_door_frame_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_entry_door_frame_category(self,context):
    if preview_collections["entry_door_frame_items"]:
        bpy.utils.previews.remove(preview_collections["entry_door_frame_items"])
        preview_collections["entry_door_frame_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_entry_door_frame_names(self,context)

#ENTRY DOOR HANDLES     
def enum_entry_door_handle_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_doors_windows.get_entry_door_handle_path()
    pcoll = preview_collections["entry_door_handle_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_entry_door_handle_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_doors_windows.get_entry_door_handle_path(),self.entry_door_handle_category)
    pcoll = preview_collections["entry_door_handle_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_entry_door_handle_category(self,context):
    if preview_collections["entry_door_handle_items"]:
        bpy.utils.previews.remove(preview_collections["entry_door_handle_items"])
        preview_collections["entry_door_handle_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_entry_door_handle_names(self,context)

#WINDOW INSERTS     
def enum_window_insert_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_doors_windows.get_window_insert_path()
    pcoll = preview_collections["window_insert_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_window_insert_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_doors_windows.get_window_insert_path(),self.window_insert_category)
    pcoll = preview_collections["window_insert_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_window_insert_category(self,context):
    if preview_collections["window_insert_items"]:
        bpy.utils.previews.remove(preview_collections["window_insert_items"])
        preview_collections["window_insert_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_window_insert_names(self,context)

#WINDOW FRAMES     
def enum_window_frame_categories(self,context):
    if context is None:
        return []
    
    icon_dir = paths_doors_windows.get_window_frame_path()
    pcoll = preview_collections["window_frame_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_window_frame_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(paths_doors_windows.get_window_frame_path(),self.window_frame_category)
    pcoll = preview_collections["window_frame_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_window_frame_category(self,context):
    if preview_collections["window_frame_items"]:
        bpy.utils.previews.remove(preview_collections["window_frame_items"])
        preview_collections["window_frame_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_window_frame_names(self,context)