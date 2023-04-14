import bpy
import os
import sys
import xml.etree.ElementTree as ET
from pc_lib import pc_utils
from . import hb_paths
from . import pyclone_utils


addon_version = ()

def get_object_props(obj):
    return obj.home_builder

def get_scene_props(scene):
    return scene.home_builder

def get_library(wm_props,library_type):
    active_wm_library_prop_name = ""

    if library_type == 'PRODUCTS':
        active_wm_library_prop_name = 'active_product_library_name'
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
    if library_type == 'BUILD_LIBRARY':
        active_wm_library_prop_name = 'active_build_library_name'

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

    if hb_scene.library_tabs == 'PRODUCTS':
        return get_library(wm_props,'PRODUCTS')

    if hb_scene.library_tabs == 'ROOMS':
        if hb_scene.room_tabs == 'DOORS_WINDOWS':
            return get_library(wm_props,'DOORS_WINDOWS')   

    if hb_scene.library_tabs == 'BUILD':
        if hb_scene.build_tabs == 'STARTERS':
            return get_library(wm_props,'STARTERS')    

        if hb_scene.build_tabs == 'INSERTS':
            return get_library(wm_props,'INSERTS')  

        if hb_scene.build_tabs == 'PARTS':
            return get_library(wm_props,'PARTS') 

        if hb_scene.build_tabs == 'LIBRARY':
            return get_library(wm_props,'BUILD_LIBRARY') 

    if hb_scene.library_tabs == 'DECORATIONS':
        return get_library(wm_props,'DECORATIONS') 

    if hb_scene.library_tabs == 'MATERIALS':
        return get_library(wm_props,'MATERIALS')       

def unwrap_obj(context,obj):
    context.view_layer.objects.active = obj
    pc_utils.apply_hook_modifiers(context,obj)       

    mode = obj.mode
    if obj.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
        
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)
    if mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()

    bpy.ops.pc_assembly.connect_meshes_to_hooks_in_assembly(obj_name = obj.name)      

def add_material_pointers(context,pointers):
    scene_props = context.scene.home_builder

    #Collect Current Pointers then Clear Collection
    current_pointers = {}
    custom_pointers = {}
    for p in scene_props.material_pointers:
        if p.is_custom:
            custom_pointers[p.name] = (p.library_name,p.category_name,p.material_name,p.library_path)
        else:
            current_pointers[p.name] = (p.library_name,p.category_name,p.material_name,p.library_path)
    
    for p in scene_props.material_pointers:
        scene_props.material_pointers.remove(0)
    
    #Add Default Pointers and Update Value if Found
    for pointer in pointers:
        if pointer[0] not in scene_props.material_pointers:
            p = scene_props.material_pointers.add()
            if pointer[0] in current_pointers:
                p.name = pointer[0]
                p.library_name = current_pointers[pointer[0]][0]
                p.category_name = current_pointers[pointer[0]][1]
                p.material_name = current_pointers[pointer[0]][2]
                p.library_path = current_pointers[pointer[0]][3]   
            else:
                p.name = pointer[0]
                p.library_name = pointer[1]
                p.category_name = pointer[2]
                p.material_name = pointer[3]  
                p.library_path = pointer[4] 

    #Add Custom Pointers
    for custom_pointer in custom_pointers:
        if custom_pointer not in scene_props.material_pointers:
            p = scene_props.material_pointers.add()   
            p.name = custom_pointer
            p.is_custom = True
            p.library_name = custom_pointers[custom_pointer][0]
            p.category_name = custom_pointers[custom_pointer][1]
            p.material_name = custom_pointers[custom_pointer][2]
            p.library_path = custom_pointers[custom_pointer][3]   
        
def load_libraries_from_xml(context):
    wm_props = context.window_manager.home_builder

    for pkg in wm_props.library_packages:
        wm_props.library_packages.remove(0)

    xml_file = hb_paths.get_library_path_xml()
    if os.path.exists(xml_file):
        root = ET.parse(xml_file).getroot()
        for node in root:
            if "LibraryPaths" in node.tag:
                for c_node in node:
                    if "Packages" in c_node.tag:
                        for nc_node in c_node:
                            if "Package" in nc_node.tag:
                                path = nc_node.attrib["Name"]
                                if os.path.exists(path):
                                    lib = wm_props.library_packages.add()
                                    lib.name = path
                                    lib.package_path = path
                                    for nnc_node in nc_node:
                                        if "Enabled" in nnc_node.tag:
                                            lib.enabled = True if nnc_node.text == "True" else False

def load_libraries(context):
    prefs = context.preferences
    asset_lib = prefs.filepaths.asset_libraries.get("home_builder_library")

    if not asset_lib:
        bpy.ops.preferences.asset_library_add()
        asset_lib = prefs.filepaths.asset_libraries[-1]
        asset_lib.name = "home_builder_library"

    wm_props = context.window_manager.home_builder
    
    for lib in wm_props.asset_libraries:
        wm_props.asset_libraries.remove(0)

    mat_library_path = os.path.join(os.path.dirname(__file__),'assets','materials','Default Room Materials','library.blend')
    pointer_list = []
    pointer_list.append(("Walls","Room Materials","Default Room Materials","White Wall Paint",mat_library_path))
    pointer_list.append(("Floor","Room Materials","Default Room Materials","Wood Floor",mat_library_path))
    pointer_list.append(("Ceiling","Room Materials","Default Room Materials","White Wall Paint",mat_library_path)) 
    pointer_list.append(("Dimensions","Room Materials","Default Room Materials","Dimension",mat_library_path)) 

    #LOAD BUILT IN LIBRARIES
    load_library_from_path(context,hb_paths.get_product_library_path(),'PRODUCTS',None,pointer_list)
    load_library_from_path(context,hb_paths.get_build_library_path(),'BUILD_LIBRARY',None)
    load_library_from_path(context,hb_paths.get_decoration_library_path(),'DECORATIONS',None)
    load_library_from_path(context,hb_paths.get_material_library_path(),'MATERIALS',None)

    #LOAD EXTERNAL LIBRARIES
    for library_package in wm_props.library_packages:
        path = library_package.package_path
        if os.path.exists(path) and os.path.isdir(path):
            dirs = os.listdir(path)
            for folder in dirs:
                if folder == 'materials':
                    load_library_from_path(context,os.path.join(path,folder),'MATERIALS',library_package)
                if folder == 'decorations':
                    load_library_from_path(context,os.path.join(path,folder),'DECORATIONS',library_package)
                if folder == 'build_library':
                    load_library_from_path(context,os.path.join(path,folder),'BUILD_LIBRARY',library_package)
                if folder == 'products':
                    load_library_from_path(context,os.path.join(path,folder),'PRODUCTS',library_package,pointer_list)

    add_material_pointers(context,pointer_list)

def get_product_libraries_and_pointers(path):
    dirs = os.listdir(path) 
    libs = []
    pointers = []
    for folder in dirs:
        if os.path.isdir(os.path.join(path,folder)):
            files = os.listdir(os.path.join(path,folder))
            for file in files:
                if file == '__init__.py':            
                    sys.path.append(path)
                    mod = __import__(folder)
                    if hasattr(mod,'register'):
                        #If register fails the module is already registered
                        try:
                            mod.register()
                        except:
                            pass
                        if hasattr(mod,"LIBRARIES"):
                            for lib in mod.LIBRARIES:
                                libs.append(lib)
                        if hasattr(mod,"MATERIAL_POINTERS"):
                            for pointer in mod.MATERIAL_POINTERS:
                                pointers.append(pointer)
    return libs, pointers
                        
def load_library_from_path(context,path,library_type,library_package,material_pointers=[]):

    wm_props = context.window_manager.home_builder

    if library_type == 'MATERIALS':
        drop_id = "home_builder.drop_material"

    if library_type == 'DECORATIONS':
        drop_id = 'home_builder.drop_decoration'

    if library_type == 'BUILD_LIBRARY':
        drop_id = 'home_builder.drop_build_library'

    if not os.path.exists(path):
        return None
    
    if library_type == 'PRODUCTS':
        libs, pointers = get_product_libraries_and_pointers(path)
        for lib in libs:
            asset_lib = wm_props.asset_libraries.add()
            asset_lib.name = lib["library_name"]
            asset_lib.library_type = lib["library_type"]
            asset_lib.library_path = lib["library_path"]
            if library_package:
                asset_lib.is_external_library = True
                asset_lib.enabled = library_package.enabled
                #Used to display libraries in packages
                package_asset_lib = library_package.asset_libraries.add()
                package_asset_lib.name = lib["library_name"]
                package_asset_lib.library_type = lib["library_type"]
            else:
                asset_lib.is_external_library = False
            if "library_menu_id" in lib:
                asset_lib.library_menu_ui = lib["library_menu_id"]
            if "library_activate_id" in lib:
                asset_lib.activate_id = lib["library_activate_id"]
            if "libary_drop_id" in lib:
                asset_lib.drop_id = lib["libary_drop_id"]   
        for pointers in pointers:      
            for p in pointers:
                for p2 in pointers[p]:
                    lib_path = os.path.dirname(p2[1])
                    material_pointers.append((p2[0],p,os.path.basename(lib_path),p2[2],p2[1]))
    else:
        library_dirs = os.listdir(path)
        for dir_name in library_dirs:
            cat_path = os.path.join(path,dir_name)
            if os.path.isdir(cat_path):
                asset_lib = wm_props.asset_libraries.add()
                asset_lib.name = dir_name
                asset_lib.library_type = library_type
                asset_lib.library_path = os.path.join(cat_path,"library.blend")
                asset_lib.drop_id = drop_id
                if library_package:
                    asset_lib.is_external_library = True
                    asset_lib.enabled = library_package.enabled
                    #Used to display libraries in packages
                    package_asset_lib = library_package.asset_libraries.add()
                    package_asset_lib.name = dir_name  
                    package_asset_lib.library_type = library_type
                else:
                    asset_lib.is_external_library = False

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