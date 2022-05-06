import bpy
import os

MATERIAL_PATH = os.path.join(os.path.dirname(__file__),'library','Door and Window Materials','library.blend')   

DOOR_WINDOW_POINTERS = []
DOOR_WINDOW_POINTERS.append(("Door Window Glass",MATERIAL_PATH,"Door Window Glass"))
DOOR_WINDOW_POINTERS.append(("Entry Door Frame",MATERIAL_PATH,"Door Window Frame"))
DOOR_WINDOW_POINTERS.append(("Entry Door Panels",MATERIAL_PATH,"Door Window Frame"))
DOOR_WINDOW_POINTERS.append(("Entry Door Handle",MATERIAL_PATH,"Door Window Hardware"))
DOOR_WINDOW_POINTERS.append(("Window Metal Frame",MATERIAL_PATH,"Door Window Frame"))