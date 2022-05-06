import bpy
import time
import os
import sys
import inspect

PATH = os.path.join(os.path.dirname(__file__),"python_libs")
sys.path.append(PATH)

from . import addon_updater_ops
from . import pyclone_utils
from . import pyclone_props
from . import hb_ui
from . import hb_ops
from . import hb_props
from . import hb_utils
from . import hb_menus
from .pyclone_ops import pc_assembly
from .pyclone_ops import pc_driver
from .pyclone_ops import pc_general
from .pyclone_ops import pc_library
from .pyclone_ops import pc_material
from .pyclone_ops import pc_object
from .pyclone_ops import pc_prompts
from .pyclone_ops import pc_window_manager
from .walls import wall_ops
from .pyclone_ui import pc_view3d_ui_sidebar_assemblies
from .pyclone_ui import pc_view3d_ui_menu

from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder",
    "author": "Andrew Peel",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "3D Viewport Sidebar",
    "description": "Library designed to help with architectural and interior design",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}

DEFAULT_ASSET_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'asset_libraries')

@persistent
def load_driver_functions(scene):
    """ Load Default Drivers
    """
    import inspect
    from . import pyclone_driver_functions
    for name, obj in inspect.getmembers(pyclone_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj
    start_time = time.time()
    for obj in bpy.data.objects:
        if obj.type in {'EMPTY','MESH'}:
            drivers = pyclone_utils.get_drivers(obj)
            for DR in drivers:  
                DR.driver.expression = DR.driver.expression
    print("Reloading Drivers: --- %s seconds ---" % (time.time() - start_time))

@persistent
def load_library(dummy):
    """
    Load Asset Libraries
    """
    prefs = bpy.context.preferences
    asset_lib = prefs.filepaths.asset_libraries.get("home_builder_library")

    if not asset_lib:
        bpy.ops.preferences.asset_library_add()
        asset_lib = prefs.filepaths.asset_libraries[-1]
        asset_lib.name = "home_builder_library"
        asset_lib.path = os.path.join(os.path.dirname(__file__),'asset_libraries','sample_cabinets','library','Sample Cabinets')
    else:
        asset_lib.name = "home_builder_library"
        asset_lib.path = os.path.join(os.path.dirname(__file__),'asset_libraries','sample_cabinets','library','Sample Cabinets')        

    for workspace in bpy.data.workspaces:
        workspace.asset_library_ref = "home_builder_library"

    wm_props = bpy.context.window_manager.home_builder
    path = DEFAULT_ASSET_LIBRARY_PATH
    dirs = os.listdir(path)
    mat_library_path = os.path.join(os.path.dirname(__file__),'materials','library.blend')
    pointer_list = []
    pointer_list.append(("Walls","Room Materials","Built In","White Wall Paint",mat_library_path))
    pointer_list.append(("Floor","Room Materials","Built In","Wood Floor",mat_library_path))
    pointer_list.append(("Ceiling","Room Materials","Built In","White Walls",mat_library_path))
    for folder in dirs:
        if os.path.isdir(os.path.join(path,folder)):
            files = os.listdir(os.path.join(path,folder))
            for file in files:
                if file == '__init__.py':            
                    sys.path.append(path)
                    mod = __import__(folder)
                    if hasattr(mod,'register'):
                        try:
                            mod.register()
                        except:
                            print("MOD ALREADY REGISTERED")
                        if hasattr(mod,"LIBRARIES"):
                            libs = list(mod.LIBRARIES)
                            for lib in libs:
                                asset_lib = wm_props.asset_libraries.add()
                                asset_lib.name = lib["library_name"]
                                asset_lib.library_type = lib["library_type"]
                                asset_lib.library_path = lib["library_path"]
                                if "library_menu_id" in lib:
                                    asset_lib.library_menu_ui = lib["library_menu_id"]
                                if "library_activate_id" in lib:
                                    asset_lib.activate_id = lib["library_activate_id"]
                                if "libary_drop_id" in lib:
                                    asset_lib.drop_id = lib["libary_drop_id"]

                        if hasattr(mod,"MATERIAL_POINTERS"):
                            for pointers in mod.MATERIAL_POINTERS:
                                for p in pointers:
                                    for p2 in pointers[p]:
                                        lib_path = os.path.dirname(p2[1])
                                        pointer_list.append((p2[0],p,os.path.basename(lib_path),p2[2],p2[1]))
                        
    hb_utils.add_material_pointers(pointer_list)


class Home_Builder_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    assets_filepath: bpy.props.StringProperty(
        name="Assets Filepath",
        subtype='FILE_PATH',
    )

    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "assets_filepath")
        addon_updater_ops.update_settings_ui(self, context)

def register():
    bpy.utils.register_class(Home_Builder_AddonPreferences)
    addon_updater_ops.register(bl_info)
    pc_assembly.register()
    pc_driver.register()
    pc_general.register()
    pc_library.register()
    pc_material.register()
    pc_object.register()
    pc_prompts.register()
    pc_window_manager.register()
    pc_view3d_ui_menu.register()
    hb_props.register()
    pyclone_props.register()
    pc_view3d_ui_sidebar_assemblies.register()
    hb_ui.register()
    hb_ops.register()
    wall_ops.register()
    hb_menus.register()
    bpy.app.handlers.load_post.append(load_driver_functions)
    bpy.app.handlers.load_post.append(load_library)

def unregister():
    pyclone_props.unregister()
    pc_assembly.unregister()
    pc_driver.unregister()
    pc_general.unregister()
    pc_library.unregister()
    pc_material.unregister()
    pc_object.unregister()
    pc_prompts.unregister()
    pc_window_manager.unregister()   
    pc_view3d_ui_menu.unregister() 
    pc_view3d_ui_sidebar_assemblies.unregister()
    hb_props.unregister()
    hb_ui.unregister()
    hb_ops.unregister()
    wall_ops.unregister()
    hb_menus.unregister()
    bpy.app.handlers.load_post.append(load_driver_functions)    
    bpy.app.handlers.load_post.remove(load_library)

if __name__ == '__main__':
    print('register')
    load_library(None)
    register()    