import os

def get_asset_folder_path():
    return os.path.join(os.path.dirname(__file__),'assets')

def get_entry_door_frame_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Frames')  

def get_entry_door_jamb_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Jambs')

def get_entry_door_handle_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Handles')       

def get_entry_door_panel_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Panels')      

def get_window_frame_path():
    return os.path.join(get_asset_folder_path(),'Window Frames')   

def get_window_insert_path():
    return os.path.join(get_asset_folder_path(),'Window Inserts')     