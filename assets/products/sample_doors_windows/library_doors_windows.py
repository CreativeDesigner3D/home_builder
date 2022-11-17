import bpy
from . import types_doors_windows
from . import utils_doors_windows
from pc_lib import pc_unit


class Window_Small(types_doors_windows.Standard_Window):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.height = pc_unit.inch(40)
        self.depth = pc_unit.inch(6)


class Window_Large(types_doors_windows.Standard_Window):

    def __init__(self):
        self.width = pc_unit.inch(70)
        self.height = pc_unit.inch(55)
        self.depth = pc_unit.inch(6)


class Door_Single(types_doors_windows.Swing_Door):

    def __init__(self):
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        self.width = props.single_door_width
        self.height = props.door_height
        self.prompts = {"Entry Door Swing":0}    


class Door_Double(types_doors_windows.Swing_Door):

    def __init__(self):
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        print(props.entry_door_panel_category,props.entry_door_panel)
        self.width = props.double_door_width
        self.height = props.door_height
        self.prompts = {"Entry Door Swing":2}   
        