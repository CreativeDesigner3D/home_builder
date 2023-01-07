import os
from . import props_cabinet
from . import drop_ops_cabinet
from . import prompt_ops_cabinet
from . import library_cabinet
from . import ui_cabinet
from . import ops_cabinet
from . import material_pointers_cabinet

CABINET_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Sample Cabinets")
APPLIANCE_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Appliances")
CABINET_STARTER_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Cabinet Starters")
CLOSET_STARTER_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Closet Starters")
CLOSET_INSERT_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Closet Inserts")
CLOSET_PART_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Closet Parts")

CABINETS = {"library_name": "Cabinets",
            "library_type": "PRODUCTS",
            "library_path": CABINET_LIBRARY_PATH,
            "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
            "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
            "libary_drop_id": "hb_sample_cabinets.drop_cabinet"}

APPLIANCES = {"library_name": "Appliances",
              "library_type": "PRODUCTS",
              "library_path": APPLIANCE_LIBRARY_PATH,
              "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
              "libary_drop_id": "hb_sample_cabinets.drop_appliance"}

CABINET_STARTERS = {"library_name": "Cabinet Starters",
                    "library_type": "STARTERS",
                    "library_path": CABINET_STARTER_LIBRARY_PATH,
                    "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                    "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
                    "libary_drop_id": "hb_sample_cabinets.drop_cabinet"}

CLOSET_STARTERS = {"library_name": "Closet Starters",
                   "library_type": "STARTERS",
                   "library_path": CLOSET_STARTER_LIBRARY_PATH,
                   "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                   "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
                   "libary_drop_id": "hb_sample_cabinets.drop_closet_starter"}

CLOSET_INSERTS = {"library_name": "Closet Inserts",
                  "library_type": "INSERTS",
                  "library_path": CLOSET_INSERT_LIBRARY_PATH,
                  "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                  "libary_drop_id": "hb_sample_cabinets.place_closet_insert"}

CLOSET_PARTS = {"library_name": "Closet Parts",
                "library_type": "PARTS",
                "library_path": CLOSET_PART_LIBRARY_PATH,
                "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                "libary_drop_id": "hb_sample_cabinets.place_closet_part"}

SAMPLE_CABINET_MATERIALS = {"library_name": "Sample Cabinet Materials",
                            "library_type": "MATERIALS",
                            "library_path": material_pointers_cabinet.SAMPLE_CABINET_MATERIALS,
                            "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                            "libary_drop_id": "home_builder.drop_material"}

LIBRARIES = [CABINETS,
             APPLIANCES,
             CLOSET_STARTERS,
             CABINET_STARTERS,
             CLOSET_INSERTS,
             CLOSET_PARTS,
             SAMPLE_CABINET_MATERIALS]

CABINET_POINTERS = {}
CABINET_POINTERS["Cabinet Materials"] = material_pointers_cabinet.CABINET_POINTERS

MATERIAL_POINTERS = [CABINET_POINTERS]

def register():
    props_cabinet.register()
    drop_ops_cabinet.register()
    ops_cabinet.register()
    prompt_ops_cabinet.register()
    ui_cabinet.register()

def unregister():
    props_cabinet.unregister()
    drop_ops_cabinet.unregister()
    ops_cabinet.unregister()
    prompt_ops_cabinet.unregister()
    ui_cabinet.unregister()    