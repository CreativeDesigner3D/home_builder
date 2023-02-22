import os
from . import props_cabinet
from . import drop_ops_cabinet
from . import prompt_ops_cabinet
from . import prompt_ops_inserts
from . import prompt_ops_parts
from . import library_cabinet
from . import ui_cabinet
from . import ui_menu_cabinet
from . import ops_cabinet
from . import ops_2d_cabinet_views
from . import material_pointers_cabinet

CABINET_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Sample Cabinets")
APPLIANCE_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Appliances")
CABINET_STARTER_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Cabinet Starters")
CABINET_INSERT_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Cabinet Inserts")
CABINET_ACCESSORY_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Cabinet Accessories")
CABINET_PART_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Cabinet Parts")
MOLDING_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Moldings")

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
                    "libary_drop_id": "home_builder.lookup_drop_id"}

CABINET_INSERTS = {"library_name": "Cabinet Inserts",
                   "library_type": "INSERTS",
                   "library_path": CABINET_INSERT_LIBRARY_PATH,
                   "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                   "libary_drop_id": "hb_sample_cabinets.drop_cabinet_insert"}

CABINET_ACCESSORIES = {"library_name": "Cabinet Accessories",
                       "library_type": "INSERTS",
                       "library_path": CABINET_ACCESSORY_LIBRARY_PATH,
                       "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                       "libary_drop_id": "hb_sample_cabinets.drop_cabinet_insert"}

CABINET_PARTS = {"library_name": "Cabinet Parts",
                 "library_type": "PARTS",
                 "library_path": CABINET_PART_LIBRARY_PATH,
                 "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                 "libary_drop_id": "home_builder.lookup_drop_id"}

MOLDING = {"library_name": "Moldings",
           "library_type": "PARTS",
           "library_path": MOLDING_LIBRARY_PATH,
           "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
           "libary_drop_id": "hb_sample_cabinets.place_molding"}

SAMPLE_CABINET_MATERIALS = {"library_name": "Sample Cabinet Materials",
                            "library_type": "MATERIALS",
                            "library_path": material_pointers_cabinet.SAMPLE_CABINET_MATERIALS,
                            "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                            "libary_drop_id": "home_builder.drop_material"}

LIBRARIES = [CABINETS,
             APPLIANCES,
             CABINET_STARTERS,
             CABINET_INSERTS,
             CABINET_ACCESSORIES,
             CABINET_PARTS,
             MOLDING,
             SAMPLE_CABINET_MATERIALS]

CABINET_POINTERS = {}
CABINET_POINTERS["Cabinet Materials"] = material_pointers_cabinet.CABINET_POINTERS

MATERIAL_POINTERS = [CABINET_POINTERS]

def register():
    props_cabinet.register()
    drop_ops_cabinet.register()
    ops_cabinet.register()
    ops_2d_cabinet_views.register()
    prompt_ops_cabinet.register()
    prompt_ops_inserts.register()
    prompt_ops_parts.register()
    ui_cabinet.register()
    ui_menu_cabinet.register()

def unregister():
    props_cabinet.unregister()
    drop_ops_cabinet.unregister()
    ops_cabinet.unregister()
    ops_2d_cabinet_views.unregister()
    prompt_ops_cabinet.unregister()
    prompt_ops_inserts.unregister()
    prompt_ops_parts.unregister()
    ui_cabinet.unregister()
    ui_menu_cabinet.unregister()