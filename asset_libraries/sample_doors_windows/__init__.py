import os

LIBRARY_TYPE = 'CABINET'
DOOR_WINDOW_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Sample Doors and Windows")

DOOR_AND_WINDOWS = {"library_name": "Sample Doors and Windows",
                    "library_type": "DOORS_WINDOWS",
                    "library_path": DOOR_WINDOW_LIBRARY_PATH}
            
LIBRARIES = [DOOR_AND_WINDOWS]

def register():
    pass