import bpy
import os
from .pc_lib import pc_utils, pc_types

addon_version = ()

def get_wm_props(window_manager):
    return window_manager.pyclone

def get_scene_props(scene):
    return scene.pyclone    

def get_object_props(obj):
    return obj.pyclone    

def get_drivers(obj):
    drivers = []
    if obj.animation_data:
        for driver in obj.animation_data.drivers:
            drivers.append(driver)

    if obj.data and obj.data.animation_data:
        for driver in obj.data.animation_data.drivers:
            drivers.append(driver)

    if obj.data and obj.data.shape_keys and obj.data.shape_keys.animation_data:
        for driver in obj.data.shape_keys.animation_data.drivers:
            drivers.append(driver)

    return drivers            

def draw_driver(layout,obj,driver):
    props = get_scene_props(bpy.context.scene)
    col = layout.column(align=True)
    box = col.box()
    row = box.row()
    driver_name = driver.data_path
    if driver_name in {"location","rotation_euler","dimensions" ,"lock_scale",'lock_location','lock_rotation'}:
        if driver.array_index == 0:
            driver_name = driver_name + " X"
        if driver.array_index == 1:
            driver_name = driver_name + " Y"
        if driver.array_index == 2:
            driver_name = driver_name + " Z"    
    try:
        value = eval('bpy.data.objects["' + obj.name + '"].' + driver.data_path)
    except:
        if "key_blocks" in driver.data_path:
            value = eval('bpy.data.objects["' + obj.name + '"].data.shape_keys.' + driver.data_path)
        else:
            value = eval('bpy.data.objects["' + obj.name + '"].data.' + driver.data_path)
    if type(value).__name__ == 'str':
        row.label(text=driver_name + " = " + str(value),icon='AUTO')
    elif type(value).__name__ == 'float':
        row.label(text=driver_name + " = " + str(value),icon='AUTO')
    elif type(value).__name__ == 'int':
        row.label(text=driver_name + " = " + str(value),icon='AUTO')
    elif type(value).__name__ == 'bool':
        row.label(text=driver_name + " = " + str(value),icon='AUTO')
    elif type(value).__name__ == 'bpy_prop_array':
        row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
    elif type(value).__name__ == 'Vector':
        row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
    elif type(value).__name__ == 'Euler':
        row.label(text=driver_name + " = " + str(value[driver.array_index]),icon='AUTO')
    else:
        row.label(text=driver_name + " = " + str(type(value)),icon='AUTO')

    row = box.row(align=True)
    if driver.driver.is_valid:
        row.prop(driver.driver,"expression",text="",expand=True,icon='DECORATE')
        if driver.mute:
            row.prop(driver,"mute",text="",icon='DECORATE')
        else:
            row.prop(driver,"mute",text="",icon='DECORATE')
    else:
        row.prop(driver.driver,"expression",text="",expand=True,icon='ERROR')
        if driver.mute:
            row.prop(driver,"mute",text="",icon='DECORATE')
        else:
            row.prop(driver,"mute",text="",icon='DECORATE') 

    box = col.box()
    row = box.row()
    row.label(text="Formula Variables:")
    row = box.row()
    row.prop(props,'driver_override_object',text="",icon='DRIVER')
    obj_bp = pc_utils.get_assembly_bp(obj)
    if props.driver_override_object:
        override_obj_bp = pc_utils.get_assembly_bp(props.driver_override_object)
        assembly = pc_types.Assembly(override_obj_bp)
        if assembly.obj_prompts:
            props = row.operator('pc_driver.get_vars_from_object',text=override_obj_bp.name,icon='DRIVER')
            props.object_name = obj.name
            props.var_object_name = assembly.obj_prompts.name
            props.data_path = driver.data_path
            props.array_index = driver.array_index    
    elif obj_bp:
        assembly = pc_types.Assembly(obj_bp)
        props = row.operator('pc_driver.get_vars_from_object',text=assembly.obj_bp.name,icon='DRIVER')
        props.object_name = obj.name
        props.var_object_name = assembly.obj_prompts.name
        props.data_path = driver.data_path
        props.array_index = driver.array_index
    else:
        props = row.operator('pc_driver.get_vars_from_object',text=obj.name,icon='DRIVER')
        props.object_name = obj.name
        props.var_object_name = obj.name
        props.data_path = driver.data_path
        props.array_index = driver.array_index



    draw_driver_variables(box,obj,driver)   

def draw_driver_variables(layout,obj,driver):
    for var in driver.driver.variables:
        col = layout.column()
        boxvar = col.box()
        row = boxvar.row(align=True)
        row.prop(var,"name",text="",icon='FORWARD')
        
        props = row.operator("pc_driver.remove_variable",text="",icon='X',emboss=False)
        props.object_name = obj.name
        props.data_path = driver.data_path
        props.array_index = driver.array_index
        props.var_name = var.name

        for target in var.targets:
            if obj.pyclone.show_driver_debug_info:
                row = boxvar.row()
                row.prop(var,"type",text="")
                row = boxvar.row()
                row.prop(target,"id",text="")
                row = boxvar.row(align=True)
                row.prop(target,"data_path",text="",icon='ANIM_DATA')

            if target.id and target.data_path != "":
                value = eval('bpy.data.objects["' + target.id.name + '"]'"." + target.data_path)
            else:
                value = "ERROR#"
            row = boxvar.row()
            row.alignment = 'CENTER'
            if type(value).__name__ == 'str':
                row.label(text="Value: " + value)
            elif type(value).__name__ == 'float':
                row.label(text="Value: " + str(bpy.utils.units.to_string(bpy.context.scene.unit_settings.system,'LENGTH',value)))
            elif type(value).__name__ == 'int':
                row.label(text="Value: " + str(value))
            elif type(value).__name__ == 'bool':
                row.label(text="Value: " + str(value))  

def update_file_browser_path(context,path):
    for area in context.screen.areas:
        if area.type == 'FILE_BROWSER':
            for space in area.spaces:
                if space.type == 'FILE_BROWSER':
                    params = space.params
                    params.directory = str.encode(path)
                    if not context.screen.show_fullscreen:
                        params.use_filter = True
                        params.display_type = 'THUMBNAIL'
                        params.use_filter_movie = False
                        params.use_filter_script = False
                        params.use_filter_sound = False
                        params.use_filter_text = False
                        params.use_filter_font = False
                        params.use_filter_folder = False
                        params.use_filter_blender = False
                        params.use_filter_image = True    

def get_file_browser_path(context):
    for area in context.screen.areas:
        if area.type == 'FILE_BROWSER':
            for space in area.spaces:
                if space.type == 'FILE_BROWSER':
                    params = space.params     
                    return os.path.join(params.directory.decode('utf-8'),params.filename)                  