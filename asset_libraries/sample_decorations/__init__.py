import os

KITCHEN_DECO_PATH = os.path.join(os.path.dirname(__file__),'library',"Kitchen Decorations")
ROOM_DECO_PATH = os.path.join(os.path.dirname(__file__),'library',"Room Decorations")

SAMPLE_KITCHEN_DECORATIONS = {"library_name": "Sample Kitchen Decorations",
                              "library_type": "DECORATIONS",
                              "library_path": KITCHEN_DECO_PATH}

SAMPLE_ROOM_DECORATIONS = {"library_name": "Sample Room Decorations",
                           "library_type": "DECORATIONS",
                           "library_path": ROOM_DECO_PATH}

LIBRARIES = [SAMPLE_KITCHEN_DECORATIONS,
             SAMPLE_ROOM_DECORATIONS]

def register():
    pass