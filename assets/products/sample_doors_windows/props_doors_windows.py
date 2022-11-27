import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
import inspect
from pc_lib import pc_types, pc_unit, pc_utils
from . import enum_doors_windows


class HB_Door_Window_Scene_Props(PropertyGroup):    

    entry_door_panel_category: bpy.props.EnumProperty(name="Entry Door Panel Category",
        items=enum_doors_windows.enum_entry_door_panel_categories,
        update=enum_doors_windows.update_entry_door_panel_category)
    entry_door_panel: bpy.props.EnumProperty(name="Entry Door Panel",
        items=enum_doors_windows.enum_entry_door_panels_names)

    entry_door_frame_category: bpy.props.EnumProperty(name="Entry Door Frame Category",
        items=enum_doors_windows.enum_entry_door_frame_categories,
        update=enum_doors_windows.update_entry_door_frame_category)
    entry_door_frame: bpy.props.EnumProperty(name="Entry Door Frame",
        items=enum_doors_windows.enum_entry_door_frame_names)

    entry_door_handle_category: bpy.props.EnumProperty(name="Entry Door Handle Category",
        items=enum_doors_windows.enum_entry_door_handle_categories,
        update=enum_doors_windows.update_entry_door_handle_category)
    entry_door_handle: bpy.props.EnumProperty(name="Entry Door Handle",
        items=enum_doors_windows.enum_entry_door_handle_names)

    entry_door_handle_category: bpy.props.EnumProperty(name="Entry Door Handle Category",
        items=enum_doors_windows.enum_entry_door_handle_categories,
        update=enum_doors_windows.update_entry_door_handle_category)
    entry_door_handle: bpy.props.EnumProperty(name="Entry Door Handle",
        items=enum_doors_windows.enum_entry_door_handle_names)

    window_frame_category: bpy.props.EnumProperty(name="Window Frame Category",
        items=enum_doors_windows.enum_window_frame_categories,
        update=enum_doors_windows.update_window_frame_category)
    window_frame: bpy.props.EnumProperty(name="Window Frame",
        items=enum_doors_windows.enum_window_frame_names)

    window_insert_category: bpy.props.EnumProperty(name="Window Insert Category",
        items=enum_doors_windows.enum_window_insert_categories,
        update=enum_doors_windows.update_window_insert_category)
    window_insert: bpy.props.EnumProperty(name="Window Insert",
        items=enum_doors_windows.enum_window_insert_names)

    #ENTRY DOORS
    single_door_width: bpy.props.FloatProperty(name="Single Door Width",
                                               description="Is the width of single entry doors",
                                               default=pc_unit.inch(36),
                                               unit='LENGTH')

    double_door_width: bpy.props.FloatProperty(name="Double Door Width",
                                               description="Is the width of double entry doors",
                                               default=pc_unit.inch(72),
                                               unit='LENGTH')

    door_height: bpy.props.FloatProperty(name="Double Door Width",
                                         description="Is the width of double entry doors",
                                         default=pc_unit.inch(80),
                                         unit='LENGTH')     

    #WINDOWS
    window_height_from_floor: bpy.props.FloatProperty(name="Window Height from Floor",
                                                      description="This is the height off the window from the floor",
                                                      default=pc_unit.inch(40),
                                                      unit='LENGTH')

    window_height: bpy.props.FloatProperty(name="Window Height",
                                           description="This is the height of windows",
                                           default=pc_unit.inch(40),
                                           unit='LENGTH')

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_doors_windows = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_doors_windows               

classes = (
    HB_Door_Window_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)         