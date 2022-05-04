import bpy
import os

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

def get_wall_bp(obj):
    if not obj:
        return None
    if "IS_WALL_BP" in obj:
        return obj
    elif obj.parent:
        return get_wall_bp(obj.parent)

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
    
def update_id_props(obj,parent_obj):
    if "PROMPT_ID" in parent_obj:
        obj["PROMPT_ID"] = parent_obj["PROMPT_ID"]
    if "MENU_ID" in parent_obj:
        obj["MENU_ID"] = parent_obj["MENU_ID"]           

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