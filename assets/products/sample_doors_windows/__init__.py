import os
from . import const_doors_windows as const
from . import material_pointers_doors_windows
from . import ui_doors_windows
from . import props_doors_windows
from . import drop_ops_doors_windows
from . import prompt_ops_doors_windows
from . import ops_doors_windows

DOOR_WINDOW_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Doors and Windows")

DOOR_AND_WINDOWS = {"library_name": "Doors and Windows",
                    "library_type": "PRODUCTS",
                    "library_path": DOOR_WINDOW_LIBRARY_PATH,
                    "library_menu_id": "HOME_BUILDER_MT_doors_windows_settings",
                    "libary_drop_id": const.lib_name + ".place_door_window"}
            
DOOR_WINDOW_MATERIALS = {"library_name": "Door and Window Materials",
                         "library_type": "MATERIALS",
                         "library_path": material_pointers_doors_windows.MATERIAL_PATH,
                         "libary_drop_id": "home_builder.drop_material"}

LIBRARIES = [DOOR_AND_WINDOWS,
             DOOR_WINDOW_MATERIALS]

DOOR_WINDOW_POINTERS = {}
DOOR_WINDOW_POINTERS["Door and Window Materials"] = material_pointers_doors_windows.DOOR_WINDOW_POINTERS

MATERIAL_POINTERS = [DOOR_WINDOW_POINTERS]

def register():
    props_doors_windows.register()
    ops_doors_windows.register()
    ui_doors_windows.register()
    drop_ops_doors_windows.register()
    prompt_ops_doors_windows.register()