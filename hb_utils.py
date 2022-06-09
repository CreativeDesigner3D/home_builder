import bpy
import os
import sys
from . import pyclone_utils

addon_version = ()

def get_object_props(obj):
    return obj.home_builder

def get_scene_props(scene):
    return scene.home_builder

def get_library(wm_props,library_type):
    active_wm_library_prop_name = ""
    if library_type == 'CABINETS':
        active_wm_library_prop_name = 'active_cabinet_library_name'
    if library_type == 'APPLIANCES':
        active_wm_library_prop_name = 'active_appliance_library_name'
    if library_type == 'DOORS_WINDOWS':
        active_wm_library_prop_name = 'active_entry_door_window_library_name'
    if library_type == 'STARTERS':
        active_wm_library_prop_name = 'active_starter_library_name'
    if library_type == 'INSERTS':
        active_wm_library_prop_name = 'active_insert_library_name'
    if library_type == 'PARTS':
        active_wm_library_prop_name = 'active_part_library_name'
    if library_type == 'DECORATIONS':
        active_wm_library_prop_name = 'active_decorations_library_name'
    if library_type == 'MATERIALS':
        active_wm_library_prop_name = 'active_materials_library_name'
    if library_type == 'FIXTURES':
        active_wm_library_prop_name = 'active_fixture_library_name'

    active_wm_library_name = eval('wm_props.' + active_wm_library_prop_name)

    if active_wm_library_name == '':
        for library in wm_props.asset_libraries:
            if library.library_type == library_type:
                exec("wm_props." + active_wm_library_prop_name + " = library.name")
                return library
    else:
        for library in wm_props.asset_libraries:
            if library.library_type == library_type and library.name == active_wm_library_name:
                return library
    
    #IF REACHED THIS FAR CHECK AGAIN
    for library in wm_props.asset_libraries:
        if library.library_type == library_type:
            exec("wm_props." + active_wm_library_prop_name + " = library.name")
            return library    

def get_active_library(context):
    hb_scene = context.scene.home_builder
    wm = context.window_manager        
    wm_props = wm.home_builder

    if hb_scene.library_tabs == 'CABINETS':
        return get_library(wm_props,'CABINETS')

    if hb_scene.library_tabs == 'APPLIANCES':
        return get_library(wm_props,'APPLIANCES')

    if hb_scene.library_tabs == 'ROOMS':
        if hb_scene.room_tabs == 'DOORS_WINDOWS':
            return get_library(wm_props,'DOORS_WINDOWS')   

    if hb_scene.library_tabs == 'FIXTURES':
        return get_library(wm_props,'FIXTURES')  

    if hb_scene.library_tabs == 'BUILD':
        if hb_scene.build_tabs == 'STARTERS':
            return get_library(wm_props,'STARTERS')    

        if hb_scene.build_tabs == 'INSERTS':
            return get_library(wm_props,'INSERTS')  

        if hb_scene.build_tabs == 'PARTS':
            return get_library(wm_props,'PARTS') 

    if hb_scene.library_tabs == 'DECORATIONS':
        return get_library(wm_props,'DECORATIONS') 

    if hb_scene.library_tabs == 'MATERIALS':
        return get_library(wm_props,'MATERIALS')       

def apply_hook_modifiers(context,obj):
    context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.type == 'HOOK':
            bpy.ops.object.modifier_apply(modifier=mod.name)            

def unwrap_obj(context,obj):
    context.view_layer.objects.active = obj
    apply_hook_modifiers(context,obj)       

    mode = obj.mode
    if obj.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
        
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)
    if mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()

    bpy.ops.pc_assembly.connect_meshes_to_hooks_in_assembly(obj_name = obj.name)      

def add_material_pointers(pointers):
    scene_props = bpy.context.scene.home_builder

    #TODO: Update Existing Pointers and Remove Unused Ones
    #      For now clear entire collection
    for p in scene_props.material_pointers:
        scene_props.material_pointers.remove(0)

    for pointer in pointers:
        p = scene_props.material_pointers.add()
        p.name = pointer[0]
        p.library_name = pointer[1]
        p.category_name = pointer[2]
        p.material_name = pointer[3]  
        p.library_path = pointer[4]    

def load_libraries(context):
        path = os.path.join(os.path.dirname(__file__),'asset_libraries')

        prefs = context.preferences
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

        wm_props = context.window_manager.home_builder
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
                            
        add_material_pointers(pointer_list)  

def load_custom_driver_functions():
    import inspect
    from . import pyclone_driver_functions
    for name, obj in inspect.getmembers(pyclone_driver_functions):
        if name not in bpy.app.driver_namespace:
            bpy.app.driver_namespace[name] = obj
    for obj in bpy.data.objects:
        if obj.type in {'EMPTY','MESH'}:
            drivers = pyclone_utils.get_drivers(obj)
            for DR in drivers:  
                DR.driver.expression = DR.driver.expression