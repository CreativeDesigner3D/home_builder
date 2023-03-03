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
from . import hb_drop_ops
from .pyclone_ops import pc_assembly
from .pyclone_ops import pc_driver
from .pyclone_ops import pc_general
from .pyclone_ops import pc_library
from .pyclone_ops import pc_material
from .pyclone_ops import pc_object
from .pyclone_ops import pc_prompts
from .walls import wall_ops
from .pyclone_ui import pc_view3d_ui_sidebar_assemblies
from .pyclone_ui import pc_view3d_ui_sidebar_object
from .pyclone_ui import pc_text_ui_sidebar_library
from .pyclone_ui import pc_view3d_ui_menu
from .pyclone_ui import pc_view3d_ui_layout_view
from .pyclone_ui import pc_lists

from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder",
    "author": "Andrew Peel",
    "version": (3, 0, 2),
    "blender": (3, 2, 0),
    "location": "3D Viewport Sidebar",
    "description": "Library designed to help with architectural and interior design",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}

@persistent
def load_driver_functions(scene):
    """ Load Default Drivers
    """
    hb_utils.load_custom_driver_functions()

@persistent
def load_library(dummy):
    """
    Load Asset Libraries
    """
    hb_utils.load_libraries_from_xml(bpy.context)
    hb_utils.load_libraries(bpy.context)


class Home_Builder_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

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
    pc_view3d_ui_menu.register()
    hb_props.register()
    pyclone_props.register()
    pc_view3d_ui_sidebar_assemblies.register()
    pc_view3d_ui_sidebar_object.register()
    pc_text_ui_sidebar_library.register()
    pc_view3d_ui_layout_view.register()
    hb_ui.register()
    hb_ops.register()
    wall_ops.register()
    pc_lists.register()
    hb_menus.register()
    hb_drop_ops.register()
    hb_utils.addon_version = bl_info['version']
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
    pc_view3d_ui_menu.unregister() 
    pc_view3d_ui_sidebar_assemblies.unregister()
    pc_view3d_ui_sidebar_object.unregister()
    pc_text_ui_sidebar_library.unregister()
    pc_view3d_ui_layout_view.unregister()
    hb_props.unregister()
    hb_ui.unregister()
    hb_ops.unregister()
    wall_ops.unregister()
    pc_lists.unregister()
    hb_menus.unregister()
    hb_drop_ops.unregister()
    bpy.app.handlers.load_post.append(load_driver_functions)    
    bpy.app.handlers.load_post.remove(load_library)

if __name__ == '__main__':
    print('register')
    load_library(None)
    register()    