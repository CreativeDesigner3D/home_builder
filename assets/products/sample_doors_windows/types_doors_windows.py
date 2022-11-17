import bpy
from os import path
import math
from pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import material_pointers_doors_windows as mat_pointers
from . import utils_doors_windows
from . import paths_doors_windows
from . import const_doors_windows as const

class Hole(pc_types.Assembly):

    obj_mesh = None

    def assign_boolean(self,assembly):
        for child in assembly.obj_bp.children:
            if child.type == 'MESH':       
                mod = child.modifiers.new(self.obj_mesh.name,'BOOLEAN')
                mod.solver ='FAST'
                mod.object = self.obj_mesh
                mod.operation = 'DIFFERENCE'    
        self.obj_mesh.hide_viewport = True
        self.obj_mesh.display_type = 'WIRE'          

    def draw(self):
        self.create_assembly("Hole")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        #When assigning vertices to a hook the transformation is made so the size must be 0
        # size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        size = (0,0,0)
        self.obj_mesh = pc_utils.create_cube_mesh("Hole",size)
        self.obj_mesh.hide_render = True
        self.add_object(self.obj_mesh)
        self.obj_mesh['IS_BOOLEAN'] = True

        vgroup = self.obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')        

        vgroup = self.obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = self.obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = self.obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([2,3,6,7])

        hook = self.obj_mesh.modifiers.new('YHOOK','HOOK')
        hook.object = self.obj_y
        hook.vertex_indices_set([1,2,5,6])

        hook = self.obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

def get_door_frame(category,assembly_name):
    root_path = paths_doors_windows.get_entry_door_frame_path()
    if assembly_name == "":
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        return path.join(root_path, props.entry_door_frame_category, props.entry_door_frame + ".blend")  
    else:
        return path.join(root_path, category, assembly_name + ".blend")  

def get_door_handle(category,assembly_name):
    root_path = paths_doors_windows.get_entry_door_handle_path()
    if assembly_name == "":
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        return path.join(root_path, props.entry_door_handle_category, props.entry_door_handle + ".blend")  
    else:
        return path.join(root_path, category, assembly_name + ".blend")  

def get_door_panel(category,assembly_name):
    root_path = paths_doors_windows.get_entry_door_panel_path()
    if assembly_name == "":
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        return path.join(root_path, props.entry_door_panel_category, props.entry_door_panel + ".blend")  
    else:
        return path.join(root_path, category, assembly_name + ".blend")  

def get_default_door_jamb():
    root_path = paths_doors_windows.get_entry_door_jamb_path()
    return path.join(root_path,"_Sample","Door Jamb.blend") 

def get_window_frame(category,assembly_name):
    root_path = paths_doors_windows.get_window_frame_path()
    if assembly_name == "":
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        return path.join(root_path, props.window_insert_category, props.window_frame + ".blend")  
    else:
        return path.join(root_path, category, assembly_name + ".blend")  

def get_window_insert(category,assembly_name):
    root_path = paths_doors_windows.get_window_insert_path()
    if assembly_name == "":
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        return path.join(root_path, props.entry_door_panel_category, props.window_insert + ".blend")  
    else:
        return path.join(root_path, category, assembly_name + ".blend")  

class Door(pc_types.Assembly):

    width = pc_unit.inch(36)
    height = pc_unit.inch(70)
    depth = pc_unit.inch(6)

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  

    def add_frame(self,door_frame_category="",door_frame_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        door_frame = pc_types.Assembly(self.add_assembly_from_file(get_door_frame(door_frame_category,door_frame_name)))
        door_frame.obj_bp[const.ENTRY_DOOR_FRAME_TAG] = True
        self.add_assembly(door_frame)
        door_frame.set_name("Door Frame")
        door_frame.loc_x(value=0)
        door_frame.loc_y(value=0)
        door_frame.loc_z(value=0)
        door_frame.dim_x('width',[width])
        door_frame.dim_y('depth',[depth])
        door_frame.dim_z('height',[height])  
        pc_pointer_utils.assign_pointer_to_assembly(door_frame,"Entry Door Frame")
        pc_utils.update_assembly_id_props(door_frame,self)

        door_frame_width = door_frame.get_prompt("Door Frame Width").get_value()

        self.get_prompt("Door Frame Width").set_value(door_frame_width)    

    def add_door_handle(self,door_panel,door_handle_category="",door_handle_name=""):
        door_panel_width = door_panel.obj_x.pyclone.get_var('location.x','door_panel_width')
        door_thickness = door_panel.obj_y.pyclone.get_var('location.y','door_thickness')
        handle_vertical_location = self.get_prompt("Handle Vertical Location").get_var('handle_vertical_location')
        entry_door_swing = self.get_prompt("Entry Door Swing").get_var('entry_door_swing')
        handle_location_from_edge = self.get_prompt("Handle Location From Edge").get_var('handle_location_from_edge')
        turn_off_handles = self.get_prompt("Turn Off Handles").get_var('turn_off_handles')

        door_handle_center = door_panel.add_empty('Door Handle Center')
        door_handle_center.empty_display_size = .001
        door_handle_center.pyclone.loc_y('door_thickness/2',[door_thickness])

        door_handle_obj = pc_utils.get_object(get_door_handle(door_handle_category,door_handle_name))
        door_handle_obj[const.ENTRY_DOOR_HANDLE_TAG] = True
        door_panel.add_object(door_handle_obj)
        
        door_handle_obj.pyclone.loc_y(value=0)
        door_handle_obj.pyclone.loc_z('handle_vertical_location',[handle_vertical_location])
        if "Left" in door_panel.obj_bp.name:
            door_handle_obj.pyclone.loc_x('door_panel_width-handle_location_from_edge',[door_panel_width,handle_location_from_edge])
            door_handle_obj.pyclone.hide('IF(OR(entry_door_swing==1,turn_off_handles),True,False)',[entry_door_swing,turn_off_handles])
        else:
            door_handle_obj.pyclone.rot_y(value=math.radians(180))
            door_handle_obj.pyclone.loc_x('door_panel_width+handle_location_from_edge',[door_panel_width,handle_location_from_edge])
            door_handle_obj.pyclone.hide('IF(OR(entry_door_swing==0,turn_off_handles),True,False)',[entry_door_swing,turn_off_handles])
            door_handle_obj.scale.z = -1
        pc_pointer_utils.assign_pointer_to_object(door_handle_obj,"Entry Door Handle")  
        pc_utils.update_id_props(door_handle_obj,self.obj_bp)
        
        mirror = door_handle_obj.modifiers.new('Mirror','MIRROR')
        mirror.mirror_object = door_handle_center
        mirror.use_axis[0] = False
        mirror.use_axis[1] = True
        mirror.use_axis[2] = False

    def add_hole_and_jamb(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        boolean_overhang_var = self.get_prompt("Boolean Overhang").get_var("boolean_overhang_var")
        door_frame_reveal = self.get_prompt("Door Frame Reveal").get_var("door_frame_reveal")
        door_frame_width_parent = self.get_prompt("Door Frame Width").get_var("door_frame_width_parent")

        hole = self.add_assembly(Hole())
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
        hole.rot_z(value=math.radians(0))
        hole.dim_x('width',[width])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height+boolean_overhang_var',[height,boolean_overhang_var])

        door_jamb = pc_types.Assembly(self.add_assembly_from_file(get_default_door_jamb()))
        self.add_assembly(door_jamb)
        door_jamb.set_name("Door Jamb")
        door_jamb.loc_x('door_frame_reveal',[door_frame_reveal])
        door_jamb.loc_y(value=0)
        door_jamb.loc_z(value=0)
        door_jamb.dim_x('width-door_frame_reveal*2',[width,door_frame_reveal])
        door_jamb.dim_y('depth',[depth])
        door_jamb.dim_z('height-door_frame_reveal',[height,door_frame_reveal])  
        pc_pointer_utils.assign_pointer_to_assembly(door_jamb,"Entry Door Frame")
        door_frame_width = door_jamb.get_prompt("Door Frame Width")
        door_frame_width.set_formula('door_frame_width_parent',[door_frame_width_parent])

class Swing_Door(Door):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  

    def add_doors(self,door_panel_category="",door_panel_name="",door_handle_category="",door_handle_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        door_reveal = self.get_prompt("Door Reveal").get_var('door_reveal')
        door_thickness = self.get_prompt("Door Thickness").get_var('door_thickness')
        entry_door_swing = self.get_prompt("Entry Door Swing").get_var('entry_door_swing')
        door_frame_width = self.get_prompt("Door Frame Width").get_var('door_frame_width')
        door_frame_reveal = self.get_prompt("Door Frame Reveal").get_var('door_frame_reveal')
        outswing = self.get_prompt("Outswing").get_var('outswing')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        turn_off_door_panels = self.get_prompt("Turn Off Door Panels").get_var('turn_off_door_panels')

        #LEFT DOOR
        l_door_panel = pc_types.Assembly(self.add_assembly_from_file(get_door_panel(door_panel_category,door_panel_name)))
        l_door_panel.set_name("Left Door Panel")
        l_door_panel.obj_bp[const.ENTRY_DOOR_PANEL_TAG] = True
        self.add_assembly(l_door_panel)
        l_open_door = l_door_panel.get_prompt("Open Door")
        l_door_panel.loc_x('IF(outswing,width-door_frame_width-door_reveal-door_frame_reveal,door_frame_width+door_reveal+door_frame_reveal)',[outswing,width,door_frame_width,door_reveal,door_frame_reveal])
        l_door_panel.loc_y('IF(outswing,depth,0)',[outswing,depth])
        l_door_panel.loc_z(value = 0)
        if not l_open_door:
            l_door_panel.rot_z('IF(outswing,radians(180),0)-door_rotation*open_door',[open_door,door_rotation,outswing])
        else:
            l_door_panel.rot_z('IF(outswing,radians(180),0)',[outswing])
            l_open_door.set_formula('open_door',[open_door])
        l_door_panel.dim_x('IF(entry_door_swing==2,(width-(door_frame_width*2)-(door_reveal*3)-(door_frame_reveal*2))/2,width-(door_frame_width*2)-(door_reveal*2)-(door_frame_reveal*2))',[width,entry_door_swing,door_frame_width,door_reveal,door_frame_reveal])
        l_door_panel.dim_y('door_thickness',[door_thickness])
        l_door_panel.dim_z('height-door_frame_width-door_reveal-door_frame_reveal',[height,door_frame_width,door_reveal,door_frame_reveal])       
        pc_pointer_utils.assign_materials_to_assembly(l_door_panel)
        hide = l_door_panel.get_prompt("Hide")
        hide.set_formula('IF(OR(entry_door_swing==1,turn_off_door_panels),True,False)',[entry_door_swing,turn_off_door_panels]) 
        self.add_door_handle(l_door_panel,door_handle_category,door_handle_name)
        pc_utils.update_assembly_id_props(l_door_panel,self)

        #RIGHT DOOR
        r_door_panel = pc_types.Assembly(self.add_assembly_from_file(get_door_panel(door_panel_category,door_panel_name)))
        r_open_door = r_door_panel.get_prompt("Open Door")
        r_door_panel.set_name("Right Door Panel")
        r_door_panel.obj_bp[const.ENTRY_DOOR_PANEL_TAG] = True
        self.add_assembly(r_door_panel)
        r_door_panel.loc_x('IF(outswing,door_frame_width+door_reveal+door_frame_reveal,width-door_frame_width-door_reveal-door_frame_reveal)',[outswing,width,door_frame_width,door_reveal,door_frame_reveal])
        r_door_panel.loc_y('IF(outswing,depth,0)',[outswing,depth])
        r_door_panel.loc_z(value = 0)
        if not r_open_door:
            r_door_panel.rot_z('IF(outswing,radians(180),0)+door_rotation*open_door',[open_door,door_rotation,outswing])
        else:
            r_door_panel.rot_z('IF(outswing,radians(180),0)',[outswing])
            r_open_door.set_formula('open_door',[open_door])
        r_door_panel.dim_x('IF(entry_door_swing==2,(width-(door_frame_width*2)-(door_reveal*3)-(door_frame_reveal*2))/2,width-(door_frame_width*2)-(door_reveal*2)-(door_frame_reveal*2))*-1',[width,entry_door_swing,door_frame_width,door_reveal,door_frame_reveal])
        r_door_panel.dim_y('door_thickness',[door_thickness])
        r_door_panel.dim_z('height-door_frame_width-door_reveal-door_frame_reveal',[height,door_frame_width,door_reveal,door_frame_reveal])      
        pc_pointer_utils.assign_materials_to_assembly(r_door_panel)
        hide = r_door_panel.get_prompt("Hide")
        hide.set_formula('IF(OR(entry_door_swing==0,turn_off_door_panels),True,False)',[entry_door_swing,turn_off_door_panels]) 

        self.add_door_handle(r_door_panel,door_handle_category,door_handle_name)
        pc_utils.update_assembly_id_props(r_door_panel,self)

    def draw_assembly(self):
        self.create_assembly("Door")
        self.obj_bp[const.ENTRY_DOOR_TAG] = True
        self.obj_bp["IS_SWING_DOOR"] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_door_windows.door_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_door_commands"

        self.add_prompt("Entry Door Swing",'COMBOBOX',0,["Left","Right","Double"])
        self.add_prompt("Door Thickness",'DISTANCE',pc_unit.inch(1.5))
        self.add_prompt("Door Reveal",'DISTANCE',pc_unit.inch(.125))
        self.add_prompt("Door Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Door Frame Reveal",'DISTANCE',pc_unit.inch(.125))
        self.add_prompt("Handle Vertical Location",'DISTANCE',pc_unit.inch(36))
        self.add_prompt("Handle Location From Edge",'DISTANCE',pc_unit.inch(2.5))
        self.add_prompt("Outswing",'CHECKBOX',True)
        self.add_prompt("Turn Off Handles",'CHECKBOX',False)
        self.add_prompt("Turn Off Door Panels",'CHECKBOX',False)
        self.add_prompt("Open Door",'PERCENTAGE',0)
        self.add_prompt("Door Rotation",'ANGLE',120)
        self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))
        
        self.obj_x.location.x = self.width
        self.obj_y.location.y = self.depth
        self.obj_z.location.z = self.height

        self.add_hole_and_jamb()
        self.add_frame()
        self.add_doors()
        self.set_prompts()


class Standard_Window(pc_types.Assembly):

    width = pc_unit.inch(36)
    height = pc_unit.inch(40)
    depth = pc_unit.inch(6)
    z_loc = pc_unit.inch(0)

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  

    def add_window_frame(self,category="",assembly_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        window_frame = pc_types.Assembly(self.add_assembly_from_file(get_window_frame(category,assembly_name)))
        self.add_assembly(window_frame)
        window_frame.obj_bp[const.WINDOW_FRAME_TAG] = True
        window_frame.set_name("Window Frame")
        window_frame.loc_x(value=0)
        window_frame.loc_y(value=0)
        window_frame.loc_z(value=0)
        window_frame.dim_x('width',[width])
        window_frame.dim_y('depth',[depth])
        window_frame.dim_z('height',[height])  
        pc_pointer_utils.assign_pointer_to_assembly(window_frame,"Entry Door Frame")

        left_window_frame_width = window_frame.get_prompt("Left Window Frame Width").get_value()
        right_window_frame_width = window_frame.get_prompt("Right Window Frame Width").get_value()
        top_window_frame_width = window_frame.get_prompt("Top Window Frame Width").get_value()
        bottom_window_frame_width = window_frame.get_prompt("Bottom Window Frame Width").get_value()

        self.get_prompt("Left Window Frame Width").set_value(left_window_frame_width)
        self.get_prompt("Right Window Frame Width").set_value(right_window_frame_width)
        self.get_prompt("Top Window Frame Width").set_value(top_window_frame_width)
        self.get_prompt("Bottom Window Frame Width").set_value(bottom_window_frame_width)
        pc_utils.update_assembly_id_props(window_frame,self)
        self.add_array_modifier(window_frame)

    def add_window_insert(self,category="",assembly_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        left_window_frame_width = self.get_prompt("Left Window Frame Width").get_var("left_window_frame_width")
        right_window_frame_width = self.get_prompt("Right Window Frame Width").get_var("right_window_frame_width")
        top_window_frame_width = self.get_prompt("Top Window Frame Width").get_var("top_window_frame_width")
        bottom_window_frame_width = self.get_prompt("Bottom Window Frame Width").get_var("bottom_window_frame_width")
                
        window_insert = pc_types.Assembly(self.add_assembly_from_file(get_window_insert(category,assembly_name)))
        self.add_assembly(window_insert)
        window_insert.obj_bp[const.WINDOW_INSERT_TAG] = True
        window_insert.set_name("Window Insert")
        window_insert.loc_x('left_window_frame_width',[left_window_frame_width])
        window_insert.loc_y(value = 0)
        window_insert.loc_z('bottom_window_frame_width',[bottom_window_frame_width])
        window_insert.dim_x('width-left_window_frame_width-right_window_frame_width',[width,left_window_frame_width,right_window_frame_width])
        window_insert.dim_y('depth',[depth])
        window_insert.dim_z('height-top_window_frame_width-bottom_window_frame_width',[height,top_window_frame_width,bottom_window_frame_width])
        pc_pointer_utils.assign_materials_to_assembly(window_insert)
        pc_utils.update_assembly_id_props(window_insert,self)
        self.add_array_modifier(window_insert)

    def add_array_modifier(self,assembly):
        width = self.obj_x.pyclone.get_var('location.x','width')
        qty = self.get_prompt("Window Quantity").get_var("qty")
        x_offset = self.get_prompt("X Offset").get_var("x_offset")

        for child in assembly.obj_bp.children:
            if child.type != 'EMPTY':
                array = child.modifiers.new('Quantity','ARRAY')   
                array.use_constant_offset = True
                array.use_relative_offset = False
                child.pyclone.modifier(array,'count',-1,'qty',[qty])
                child.pyclone.modifier(array,'constant_offset_displace',0,'width+x_offset',[width,x_offset])

    def draw_assembly(self):
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
    
        self.create_assembly("Window")
        self.obj_bp[const.WINDOW_TAG] = True
        self.obj_bp["PROMPT_ID"] = "hb_sample_door_windows.window_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_window_commands"

        self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Left Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Right Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Top Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Bottom Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Window Quantity",'QUANTITY',1)
        self.add_prompt("X Offset",'DISTANCE',pc_unit.inch(10))

        self.obj_x.location.x = self.width
        self.obj_y.location.y = self.depth
        self.obj_z.location.z = self.height
        self.obj_bp.location.z = props.window_height_from_floor  

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        boolean_overhang_var = self.get_prompt("Boolean Overhang").get_var("boolean_overhang_var")

        hole = self.add_assembly(Hole())
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z(value=0)
        hole.rot_z(value=math.radians(0))
        hole.dim_x('width',[width])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height',[height])
        self.add_array_modifier(hole)

        self.add_window_frame()
        self.add_window_insert()        