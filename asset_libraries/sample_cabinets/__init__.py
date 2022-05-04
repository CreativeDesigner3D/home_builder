import os
from . import cabinet_prompt_ops
from . import cabinet_library
from . import cabinet_ui
from . import cabinet_ops
from . import cabinet_material_pointers

CABINET_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Sample Cabinets")
APPLIANCE_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Appliances")
CLOSET_STARTER_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Closet Starters")
CLOSET_INSERT_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Closet Inserts")
CLOSET_PART_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Closet Parts")
WOOD_FINISHED_PATH = os.path.join(os.path.dirname(__file__),'library',"Wood Finished")
WOOD_UNFINISHED_PATH = os.path.join(os.path.dirname(__file__),'library',"Wood Unfinished")
MELAMINE_PATH = os.path.join(os.path.dirname(__file__),'library',"Melamine")

CABINETS = {"library_name": "Sample Cabinets",
            "library_type": "CABINETS",
            "library_path": CABINET_LIBRARY_PATH,
            "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
            "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
            "libary_drop_id": "hb_sample_cabinets.drop_cabinet_library"}

APPLIANCES = {"library_name": "Appliances",
              "library_type": "APPLIANCES",
              "library_path": APPLIANCE_LIBRARY_PATH,
              "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
              "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
              "libary_drop_id": "hb_sample_cabinets.drop_cabinet_library"}

CLOSET_STARTERS = {"library_name": "Closet Starters",
                   "library_type": "STARTERS",
                   "library_path": CLOSET_STARTER_LIBRARY_PATH,
                   "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                   "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
                   "libary_drop_id": "hb_sample_cabinets.drop_cabinet_library"}

CLOSET_INSERTS = {"library_name": "Closet Inserts",
                  "library_type": "INSERTS",
                  "library_path": CLOSET_INSERT_LIBRARY_PATH,
                  "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                  "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
                  "libary_drop_id": "hb_sample_cabinets.drop_cabinet_library"}

CLOSET_PARTS = {"library_name": "Closet Parts",
                "library_type": "PARTS",
                "library_path": CLOSET_PART_LIBRARY_PATH,
                "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
                "libary_drop_id": "hb_sample_cabinets.drop_cabinet_library"}

WOOD_FINISHED = {"library_name": "Wood Finished",
                "library_type": "MATERIALS",
                "library_path": WOOD_FINISHED_PATH,
                "library_menu_id": "HOME_BUILDER_MT_cabinet_settings",
                "library_activate_id": "hb_sample_cabinets.active_cabinet_library",
                "libary_drop_id": "hb_sample_cabinets.drop_cabinet_library"}

LIBRARIES = [CABINETS,
             APPLIANCES,
             CLOSET_STARTERS,
             CLOSET_INSERTS,
             CLOSET_PARTS,
             WOOD_FINISHED]

CABINET_POINTERS = {}
CABINET_POINTERS["Cabinet Materials"] = cabinet_material_pointers.CABINET_POINTERS

MATERIAL_POINTERS = [CABINET_POINTERS]

def register():
    cabinet_ops.register()
    cabinet_prompt_ops.register()
    cabinet_ui.register()