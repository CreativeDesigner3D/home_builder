import bpy
from pc_lib import pc_types, pc_unit, pc_utils
from . import utils_cabinet

def add_cabinet_prompts(assembly):
    assembly.add_prompt("Cabinet Type",'TEXT',"")
    assembly.add_prompt("Corner Type",'TEXT',"")

def add_stacked_cabinet_prompts(assembly):
    assembly.add_prompt("Bottom Cabinet Height",'DISTANCE',pc_unit.inch(50))

def add_filler_prompts(assembly):
    assembly.add_prompt("Left Adjustment Width",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Right Adjustment Width",'DISTANCE',pc_unit.inch(0))

def add_front_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Front Thickness",'DISTANCE',props.cabinet_front_thickness)
    assembly.add_prompt("Turn Off Pulls",'CHECKBOX',False)

def add_sink_prompts(assembly):
    assembly.add_prompt("Add Sink",'CHECKBOX',False)
    assembly.add_prompt("Add Faucet",'CHECKBOX',False)

def add_cooktop_prompts(assembly):
    assembly.add_prompt("Add Cooktop",'CHECKBOX',False)
    assembly.add_prompt("Add Range Hood",'CHECKBOX',False)

def add_door_prompts(assembly):
    door_swing = assembly.add_prompt("Door Swing",'COMBOBOX',0,["Left","Right","Double","Top","Bottom"])
    door_swing.combobox_columns = 3
    assembly.add_prompt("Door Rotation",'ANGLE',120)
    assembly.add_prompt("Open Door",'PERCENTAGE',0)
    assembly.add_prompt("Door Type",'TEXT',"")

def add_blind_cabinet_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    blind_panel_location = assembly.add_prompt("Blind Panel Location",'COMBOBOX',0,["Left","Right"])
    blind_panel_location.combobox_columns = 2
    carcass_type = assembly.get_prompt("Carcass Type")
    if carcass_type.get_value() == 'Base':
        assembly.add_prompt("Blind Panel Width",'DISTANCE',props.base_cabinet_depth)  
    elif carcass_type.get_value() == 'Upper':
        assembly.add_prompt("Blind Panel Width",'DISTANCE',props.upper_cabinet_depth)  
    else:
        assembly.add_prompt("Blind Panel Width",'DISTANCE',props.tall_cabinet_depth)  
    assembly.add_prompt("Blind Panel Reveal",'DISTANCE',pc_unit.inch(3))  

def add_drawer_prompts(assembly):
    assembly.add_prompt("Open Drawer",'PERCENTAGE',0)
    assembly.add_prompt("Drawer Box Gap",'DISTANCE',pc_unit.inch(.25))

def add_front_overlay_prompts(assembly):
    assembly.add_prompt("Hide",'CHECKBOX',False)
    assembly.add_prompt("Inset Front",'CHECKBOX',False)
    assembly.add_prompt("Door to Cabinet Gap",'DISTANCE',pc_unit.inch(.125))    
    assembly.add_prompt("Half Overlay Top",'CHECKBOX',False)
    assembly.add_prompt("Half Overlay Bottom",'CHECKBOX',False)
    assembly.add_prompt("Half Overlay Left",'CHECKBOX',False)
    assembly.add_prompt("Half Overlay Right",'CHECKBOX',False)
    assembly.add_prompt("Inset Reveal",'DISTANCE',pc_unit.inch(.125))
    assembly.add_prompt("Top Reveal",'DISTANCE',pc_unit.inch(.0625))
    assembly.add_prompt("Bottom Reveal",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Left Reveal",'DISTANCE',pc_unit.inch(.0625))
    assembly.add_prompt("Right Reveal",'DISTANCE',pc_unit.inch(.0625))
    assembly.add_prompt("Vertical Gap",'DISTANCE',pc_unit.inch(.125))
    assembly.add_prompt("Horizontal Gap",'DISTANCE',pc_unit.inch(.125))

def add_door_pull_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Base Pull Vertical Location",'DISTANCE',props.pull_vertical_location_base)
    assembly.add_prompt("Tall Pull Vertical Location",'DISTANCE',props.pull_vertical_location_tall)
    assembly.add_prompt("Upper Pull Vertical Location",'DISTANCE',props.pull_vertical_location_upper)
    assembly.add_prompt("Pull Horizontal Location",'DISTANCE',props.pull_dim_from_edge)
    assembly.add_prompt("Pull Length",'DISTANCE',pc_unit.inch(0))

def add_drawer_pull_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Center Pull On Front",'CHECKBOX',props.center_pulls_on_drawer_front)
    assembly.add_prompt("Drawer Pull Vertical Location",'DISTANCE',props.pull_vertical_location_drawers)

def add_countertop_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Countertop Overhang Front",'DISTANCE',pc_unit.inch(1))
    assembly.add_prompt("Countertop Overhang Back",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Countertop Overhang Left",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Countertop Overhang Right",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Add Backsplash",'CHECKBOX',True)
    assembly.add_prompt("Add Left Backsplash",'CHECKBOX',False)
    assembly.add_prompt("Add Right Backsplash",'CHECKBOX',False)
    assembly.add_prompt("Side Splash Setback",'DISTANCE',pc_unit.inch(2.75))
    assembly.add_prompt("Deck Thickness",'DISTANCE',props.countertop_thickness)
    assembly.add_prompt("Splash Thickness",'DISTANCE',pc_unit.inch(.75))    

def add_base_assembly_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Toe Kick Height",'DISTANCE',props.toe_kick_height)
    assembly.add_prompt("Toe Kick Setback",'DISTANCE',props.toe_kick_setback)
    assembly.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))  

def add_carcass_prompts(assembly):
    assembly.add_prompt("Carcass Type",'TEXT',"")
    assembly.add_prompt("Is Exposed Interior",'CHECKBOX',True)
    assembly.add_prompt("Left Finished End",'CHECKBOX',True)
    assembly.add_prompt("Right Finished End",'CHECKBOX',True)
    assembly.add_prompt("Finished Back",'CHECKBOX',True)
    assembly.add_prompt("Finished Top",'CHECKBOX',True)
    assembly.add_prompt("Finished Bottom",'CHECKBOX',True)
    assembly.add_prompt("Run Sides to Floor",'CHECKBOX',True)
    # assembly.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(.75))    
    
def add_cabinet_lighting_prompts(assembly):
    assembly.add_prompt("Add Top Light",'CHECKBOX',False)    
    assembly.add_prompt("Add Side Light",'CHECKBOX',False)  
    assembly.add_prompt("Add Bottom Light",'CHECKBOX',False)  
    assembly.add_prompt("Lighting Width",'DISTANCE',pc_unit.inch(.75)) 
    assembly.add_prompt("Lighting Dim From Front",'DISTANCE',pc_unit.inch(1.5)) 
    assembly.add_prompt("Lighting Inset From Sides",'DISTANCE',pc_unit.inch(.75)) 

def add_splitter_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Thickness",'DISTANCE',props.closet_shelf_thickness)
    assembly.add_prompt("Left Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Right Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Top Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Bottom Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Extend Top Amount",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Extend Bottom Amount",'DISTANCE',pc_unit.inch(0))

def add_interior_shelf_prompts(assembly):
    assembly.add_prompt("Shelf Quantity",'QUANTITY',1) 
    assembly.add_prompt("Shelf Setback",'DISTANCE',pc_unit.inch(.25))  
    assembly.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(.125))  
    # assembly.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(.75)) 

def add_thickness_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Material Thickness",'DISTANCE',props.cabinet_part_thickness) 

def add_closet_toe_kick_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Closet Kick Height",'DISTANCE',props.closet_toe_kick_height) 
    assembly.add_prompt("Closet Kick Setback",'DISTANCE',props.closet_toe_kick_setback) 

def add_closet_thickness_prompts(assembly):
    props = utils_cabinet.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Shelf Thickness",'DISTANCE',props.closet_shelf_thickness)
    assembly.add_prompt("Panel Thickness",'DISTANCE',props.closet_panel_thickness)    