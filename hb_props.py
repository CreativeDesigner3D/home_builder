import bpy
import os
from pc_lib import pc_unit
from . import hb_utils
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

def update_library_tab(self,context):
    prefs = context.preferences
    asset_lib = prefs.filepaths.asset_libraries.get('home_builder_library')
    library = hb_utils.get_active_library(context)
    if library:
        asset_lib.path = library.library_path

        for workspace in bpy.data.workspaces:
            workspace.asset_library_ref = "home_builder_library"
        
        if bpy.ops.asset.library_refresh.poll():
            bpy.ops.asset.library_refresh()


class Material_Pointer(PropertyGroup):
    library_path: StringProperty(name="Library Path")
    library_name: StringProperty(name="Library Name")
    category_name: StringProperty(name="Category Name")
    material_name: StringProperty(name="Material Name")


class Asset_Library(PropertyGroup):
    library_type: StringProperty(name="Library Type")
    library_path: StringProperty(name="Library Path")
    library_menu_ui: StringProperty(name="Library Settings UI")
    activate_id: StringProperty(name="Activate ID")
    drop_id: StringProperty(name="Drop ID")
    enabled: BoolProperty(name="Enabled",default=True)
    material_pointers: CollectionProperty(name="Material Pointers",type=Material_Pointer)


class Home_Builder_Object_Props(PropertyGroup):

    connected_object: bpy.props.PointerProperty(name="Connected Object",
                                                type=bpy.types.Object,
                                                description="This is the used to store objects that are connected together.")

    @classmethod
    def register(cls):
        bpy.types.Object.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.home_builder

class Home_Builder_Scene_Props(PropertyGroup):  
    main_tabs: EnumProperty(name="Main Tabs",
                          items=[('LIBRARY',"Library","Show the Library"),
                                 ('SETTINGS',"Settings","Show the Library Settings")],
                          default='LIBRARY')

    library_tabs: EnumProperty(name="Library Tabs",
                          items=[('ROOMS',"Rooms","Show the Room Library"),
                                 ('APPLIANCES',"Appliances","Show the Appliance Library"),
                                 ('CABINETS',"Cabinets","Show the Appliance Library"),
                                 ('FIXTURES',"Fixtures","Show the Fixture Library"),
                                 ('BUILD',"Build","Show the Build Library"),
                                 ('DECORATIONS',"Decorations","Show the Decoration Library"),
                                 ('MATERIALS',"Materials","Show the Materials")],
                          default='ROOMS',
                          update=update_library_tab)

    room_tabs: EnumProperty(name="Room Tabs",
                          items=[('WALLS',"Walls","Show the Walls"),
                                 ('DOORS_WINDOWS',"Doors and Windows","Show the Doors and Windows"),
                                 ('OBSTACLES',"Obstacles","Show the Obstacles")],
                          default='WALLS',
                          update=update_library_tab)

    build_tabs: EnumProperty(name="Build Tabs",
                          items=[('STARTERS',"Starters","Show the Closet Starters"),
                                 ('INSERTS',"Inserts","Show the Closet Inserts"),
                                 ('PARTS',"Parts","Show the Closet Parts")],
                          default='STARTERS',
                          update=update_library_tab)

    material_pointers: CollectionProperty(name="Material Pointers",type=Material_Pointer)

    wall_height: FloatProperty(name="Wall Height",default=pc_unit.inch(96),subtype='DISTANCE')
    wall_thickness: FloatProperty(name="Wall Thickness",default=pc_unit.inch(6),subtype='DISTANCE')

    @classmethod
    def register(cls):
        bpy.types.Scene.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.home_builder    


class Home_Builder_Workspace_Props(PropertyGroup):  
    cabinet_library_index: bpy.props.IntProperty()
    appliance_library_index: bpy.props.IntProperty()
    home_builder_library_index: bpy.props.IntProperty()

    home_builder_library_ref: bpy.props.StringProperty(name="HB",default="home_builder_library")

    @classmethod
    def register(cls):
        bpy.types.WorkSpace.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WorkSpace.home_builder    


class Home_Builder_Window_Manager_Props(PropertyGroup):
    home_builder_library_assets: bpy.props.CollectionProperty(type=bpy.types.AssetHandle)
    cabinet_library_assets: bpy.props.CollectionProperty(type=bpy.types.AssetHandle)
    appliance_library_assets: bpy.props.CollectionProperty(type=bpy.types.AssetHandle)
    asset_libraries: bpy.props.CollectionProperty(type=Asset_Library)

    active_entry_door_window_library_name: bpy.props.StringProperty(name="Active Entry Door Window Library Name")
    active_cabinet_library_name: bpy.props.StringProperty(name="Active Cabinet Library Name")
    active_appliance_library_name: bpy.props.StringProperty(name="Active Appliance Library Name")
    active_fixture_library_name: bpy.props.StringProperty(name="Active Bath Fixture Library Name")
    active_starter_library_name: bpy.props.StringProperty(name="Active Closet Starter Library Name")
    active_insert_library_name: bpy.props.StringProperty(name="Active Closet Insert Library Name")
    active_part_library_name: bpy.props.StringProperty(name="Active Closet Part Library Name")
    active_decorations_library_name: bpy.props.StringProperty(name="Active Decorations Library Name")
    active_materials_library_name: bpy.props.StringProperty(name="Active Materials Library Name")

    def load_asset_libraries(self):
        print("LOADING ASSET LIBRARIES")

    @classmethod
    def register(cls):
        bpy.types.WindowManager.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.home_builder            


classes = (
    Material_Pointer,
    Asset_Library,
    Home_Builder_Object_Props,
    Home_Builder_Scene_Props,
    Home_Builder_Workspace_Props,
    Home_Builder_Window_Manager_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)             