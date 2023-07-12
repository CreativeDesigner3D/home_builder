import bpy
import math
from pc_lib import pc_types, pc_unit, pc_utils
import time
from .. import hb_utils
from . import data_parts

class Mesh_Wall(pc_types.Assembly):
    show_in_library = True
    category_name = "ROOMS"
    subcategory_name = "WALLS"
    
    def draw_wall(self):
        self.create_assembly("Wall Mesh")
        props = hb_utils.get_scene_props(bpy.context.scene)

        #ASSIGN PROPERTY
        self.obj_bp["IS_WALL_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.wall_prompts" 
        self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_wall_commands"

        #Set Default Dimensions
        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = props.wall_thickness
        self.obj_z.location.z = props.wall_height

        #Add Objects
        left_angle_empty = self.add_empty("Left Angle")
        right_angle_empty = self.add_empty("Right Angle")

        size = (0,0,0)
        obj_mesh = pc_utils.create_cube_mesh("Wall Mesh",size)
        obj_mesh.color = [0.252832, 0.500434, 0.735662, 1.000000]
        self.add_object(obj_mesh)

        #Assign Mesh Hooks
        vgroup = obj_mesh.vertex_groups[left_angle_empty.name]
        vgroup.add([1,5],1,'ADD')  

        vgroup = obj_mesh.vertex_groups[right_angle_empty.name]
        vgroup.add([2,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([3,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([3,7])

        hook = obj_mesh.modifiers.new('LEFTANGLE','HOOK')
        hook.object = left_angle_empty
        hook.vertex_indices_set([1,5])

        hook = obj_mesh.modifiers.new('RIGHTANGLE','HOOK')
        hook.object = right_angle_empty
        hook.vertex_indices_set([2,6])        

        hook = obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

        #Assign Drivers
        length = self.obj_x.pyclone.get_var('location.x','length')
        wall_thickness = self.obj_y.pyclone.get_var('location.y','wall_thickness')

        left_angle = self.add_prompt("Left Angle",'ANGLE',0)
        right_angle = self.add_prompt("Right Angle",'ANGLE',0)

        left_angle_var = left_angle.get_var('left_angle_var')
        right_angle_var = right_angle.get_var('right_angle_var')

        left_angle_empty.pyclone.loc_x('tan(left_angle_var)*wall_thickness',[left_angle_var,wall_thickness])
        left_angle_empty.pyclone.loc_y('wall_thickness',[wall_thickness])

        right_angle_empty.pyclone.loc_x('length+tan(right_angle_var)*wall_thickness',[length,right_angle_var,wall_thickness])
        right_angle_empty.pyclone.loc_y('wall_thickness',[wall_thickness])

        #Add Material Pointer
        bpy.context.view_layer.objects.active = obj_mesh
        bpy.ops.object.material_slot_add()
        pointer = obj_mesh.pyclone.pointers.add()
        pointer.name = "Wall"
        pointer.pointer_name = "Walls"

        # obj_mesh.lock_location = (True,True,True)
        # obj_mesh.lock_rotation = (True,True,True)
        pc_utils.assign_materials_to_object(obj_mesh)

# class Wall_Framed(pc_types.Assembly):
#     show_in_library = True
#     category_name = "ROOMS"
#     subcategory_name = "WALLS"

#     def draw_wall(self):
#         start_time = time.time()

#         #Create Assembly
#         props = hb_utils.get_scene_props(bpy.context.scene)
#         self.create_assembly("Wall")

#         #ASSIGN PROPERTY
#         self.obj_bp["IS_WALL_BP"] = True
#         self.obj_bp["PROMPT_ID"] = "home_builder.wall_prompts" 
#         self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_wall_commands"

#         #Set Default Dimensions
#         self.obj_x.location.x = pc_unit.inch(120) #Length
#         self.obj_y.location.y = props.wall_thickness
#         self.obj_z.location.z = props.wall_height

#         #Get Product Variables
#         length = self.obj_x.pyclone.get_var('location.x','length')
#         wall_thickness = self.obj_y.pyclone.get_var('location.y','wall_thickness')
#         height = self.obj_z.pyclone.get_var('location.z','height')

#         #Add Prompts
#         left_angle = self.add_prompt("Left Angle",'ANGLE',0)
#         right_angle = self.add_prompt("Right Angle",'ANGLE',0)
#         stud_spacing_distance = self.add_prompt("Stud Spacing Distance",'DISTANCE',pc_unit.inch(16))
#         material_thickness = self.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(2))

#         #Get Prompt Variables
#         material_thickness = material_thickness.get_var("material_thickness")
#         stud_spacing_distance = stud_spacing_distance.get_var("stud_spacing_distance")

#         #Add Parts
#         bottom_plate = self.add_assembly(data_parts.Stud())
#         bottom_plate.set_name('Bottom Plate')
#         bottom_plate.loc_x(value=0)
#         bottom_plate.loc_y(value=0)
#         bottom_plate.loc_z(value=0)
#         bottom_plate.dim_x('length',[length])
#         bottom_plate.dim_y('wall_thickness',[wall_thickness])
#         bottom_plate.dim_z('material_thickness',[material_thickness])
#         home_builder_pointers.assign_pointer_to_assembly(bottom_plate,"Lumber")

#         top_plate = self.add_assembly(data_parts.Stud())
#         top_plate.set_name('Top Plate')
#         top_plate.loc_x(value=0)
#         top_plate.loc_y(value=0)
#         top_plate.loc_z('height',[height])
#         top_plate.dim_x('length',[length])
#         top_plate.dim_y('wall_thickness',[wall_thickness])
#         top_plate.dim_z('-material_thickness',[material_thickness])
#         home_builder_pointers.assign_pointer_to_assembly(top_plate,"Lumber")

#         first_stud = self.add_assembly(data_parts.Stud())
#         first_stud.set_name('First Stud')
#         first_stud.loc_x(value=0)
#         first_stud.loc_y(value=0)
#         first_stud.loc_z('material_thickness',[material_thickness])
#         first_stud.rot_y(value=math.radians(-90))
#         first_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
#         first_stud.dim_y('wall_thickness',[wall_thickness])
#         first_stud.dim_z('-material_thickness',[material_thickness])
#         home_builder_pointers.assign_pointer_to_assembly(first_stud,"Lumber")

#         last_stud = self.add_assembly(data_parts.Stud())
#         last_stud.set_name('Last Stud')
#         last_stud.loc_x('length',[length])
#         last_stud.loc_y(value=0)
#         last_stud.loc_z('material_thickness',[material_thickness])
#         last_stud.rot_y(value=math.radians(-90))
#         last_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
#         last_stud.dim_y('wall_thickness',[wall_thickness])
#         last_stud.dim_z('material_thickness',[material_thickness])
#         home_builder_pointers.assign_pointer_to_assembly(last_stud,"Lumber")

#         center_stud = self.add_assembly(data_parts.Stud())
#         center_stud.set_name('Center Stud')
#         center_stud.loc_x('stud_spacing_distance',[stud_spacing_distance])
#         center_stud.loc_y(value=0)
#         center_stud.loc_z('material_thickness',[material_thickness])
#         center_stud.rot_y(value=math.radians(-90))
#         center_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
#         center_stud.dim_y('wall_thickness',[wall_thickness])
#         center_stud.dim_z('material_thickness',[material_thickness])
#         home_builder_pointers.assign_pointer_to_assembly(center_stud,"Lumber")

#         qty = center_stud.get_prompt('Quantity')
#         offset = center_stud.get_prompt('Array Offset')

#         qty.set_formula('int((length-material_thickness)/stud_spacing_distance)',[length,material_thickness,stud_spacing_distance])
#         offset.set_formula('-stud_spacing_distance',[stud_spacing_distance])  
             
#         print("WALL: Draw Time --- %s seconds ---" % (time.time() - start_time))


# class Wall_Brick(pc_types.Assembly):
#     show_in_library = True
#     category_name = "ROOMS"
#     subcategory_name = "WALLS"

#     def draw_wall(self):
#         start_time = time.time()     

#         #Create Assembly
#         self.create_assembly("Room")

#         #ASSIGN PROPERTY
#         self.obj_bp["IS_WALL_BP"] = True        
#         self.obj_bp["PROMPT_ID"] = "home_builder.wall_prompts" 
#         self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_wall_commands"

#         #Set Default Dimensions
#         props = hb_utils.get_scene_props(bpy.context.scene)
#         self.obj_x.location.x = pc_unit.inch(120) #Length
#         self.obj_y.location.y = pc_unit.inch(3.875)
#         self.obj_z.location.z = props.wall_height

#         #Get Product Variables
#         length = self.obj_x.pyclone.get_var('location.x','length')
#         wall_thickness = self.obj_y.pyclone.get_var('location.y','wall_thickness')
#         height = self.obj_z.pyclone.get_var('location.z','height')

#         #Add Prompts
#         left_angle = self.add_prompt("Left Angle",'ANGLE',0)
#         right_angle = self.add_prompt("Right Angle",'ANGLE',0)
#         brick_length = self.add_prompt("Brick Length",'DISTANCE',pc_unit.inch(7.875))
#         brick_height = self.add_prompt("Brick Height",'DISTANCE',pc_unit.inch(2.25))
#         mortar_thickness = self.add_prompt("Mortar Thickness",'DISTANCE',pc_unit.inch(.5))
#         mortar_inset = self.add_prompt("Mortar Inset",'DISTANCE',pc_unit.inch(.125))
#         boolean_overhang = self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))

#         #Get Vars
#         brick_length = brick_length.get_var("brick_length")
#         brick_height = brick_height.get_var("brick_height")
#         mortar_thickness = mortar_thickness.get_var("mortar_thickness")
#         mortar_inset = mortar_inset.get_var("mortar_inset")
#         boolean_overhang_var = boolean_overhang.get_var("boolean_overhang_var")

#         #Add Parts
#         brick1 = self.add_assembly(data_parts.Brick())
#         brick1.set_name('Bricks')
#         brick1.loc_x(value=0)
#         brick1.loc_y(value=0)
#         brick1.loc_z(value=0)
#         brick1.dim_x('brick_length',[brick_length])
#         brick1.dim_y('wall_thickness',[wall_thickness])
#         brick1.dim_z('brick_height',[brick_height])
#         x_quantity = brick1.get_prompt('X Quantity')
#         x_offset = brick1.get_prompt('X Offset')
#         z_quantity = brick1.get_prompt('Z Quantity')
#         z_offset = brick1.get_prompt('Z Offset')

#         x_quantity.set_formula('(length-brick_length)/(brick_length+mortar_thickness)+1',
#                                 [length,brick_length,mortar_thickness])
#         x_offset.set_formula('brick_length+mortar_thickness',[brick_length,mortar_thickness])        

#         z_quantity.set_formula('((height-brick_height)/(brick_height+mortar_thickness))/2+1',
#                                 [height,brick_height,mortar_thickness])
#         z_offset.set_formula('(brick_height+mortar_thickness)*2',[brick_height,mortar_thickness])  

#         brick2 = self.add_assembly(data_parts.Brick())
#         brick2.set_name('Bricks')
#         brick2.loc_x('-brick_length/2',[brick_length])
#         brick2.loc_y(value=0)
#         brick2.loc_z('brick_height+mortar_thickness',[brick_height,mortar_thickness])
#         brick2.dim_x('brick_length',[brick_length])
#         brick2.dim_y('wall_thickness',[wall_thickness])
#         brick2.dim_z('brick_height',[brick_height])
#         x_quantity = brick2.get_prompt('X Quantity')
#         x_offset = brick2.get_prompt('X Offset')
#         z_quantity = brick2.get_prompt('Z Quantity')
#         z_offset = brick2.get_prompt('Z Offset')

#         x_quantity.set_formula('(length-brick_length)/(brick_length+mortar_thickness)+2',
#                                 [length,brick_length,mortar_thickness])
#         x_offset.set_formula('brick_length+mortar_thickness',[brick_length,mortar_thickness])        

#         z_quantity.set_formula('((height-brick_height)/(brick_height+mortar_thickness))/2',
#                                 [height,brick_height,mortar_thickness])
#         z_offset.set_formula('(brick_height+mortar_thickness)*2',[brick_height,mortar_thickness])  

#         right_hole = self.add_assembly(home_builder_parts.Hole())
#         right_hole.set_name("Hole")
#         right_hole.loc_x('length',[length])
#         right_hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
#         right_hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
#         right_hole.rot_z(value=math.radians(0))
#         right_hole.dim_x('boolean_overhang_var+(brick_length/2)',[boolean_overhang_var,brick_length])
#         right_hole.dim_y('wall_thickness+(boolean_overhang_var*2)',[wall_thickness,boolean_overhang_var])
#         right_hole.dim_z('height+(boolean_overhang_var*2)',[height,boolean_overhang_var])
#         right_hole.assign_boolean(brick1)
#         right_hole.assign_boolean(brick2)

#         left_hole = self.add_assembly(home_builder_parts.Hole())
#         left_hole.set_name("Hole")
#         left_hole.loc_x('-boolean_overhang_var-(brick_length/2)',[boolean_overhang_var,brick_length])
#         left_hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
#         left_hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
#         left_hole.rot_z(value=math.radians(0))
#         left_hole.dim_x('boolean_overhang_var+(brick_length/2)',[boolean_overhang_var,brick_length])
#         left_hole.dim_y('wall_thickness+(boolean_overhang_var*2)',[wall_thickness,boolean_overhang_var])
#         left_hole.dim_z('height+(boolean_overhang_var*2)',[height,boolean_overhang_var])
#         left_hole.assign_boolean(brick1)
#         left_hole.assign_boolean(brick2)

#         morter = self.add_assembly(data_parts.Cube())
#         morter.set_name('Morter')
#         morter.loc_x('mortar_inset',[mortar_inset])
#         morter.loc_y('mortar_inset',[mortar_inset])
#         morter.loc_z('mortar_inset',[mortar_inset])
#         morter.dim_x('length-mortar_inset*2',[length,mortar_inset])
#         morter.dim_y('wall_thickness-mortar_inset*2',[wall_thickness,mortar_inset])
#         morter.dim_z('height-mortar_inset*2',[height,mortar_inset])

#         home_builder_pointers.assign_pointer_to_assembly(morter,"Morter")
#         home_builder_pointers.assign_pointer_to_assembly(brick1,"Bricks")
#         home_builder_pointers.assign_pointer_to_assembly(brick2,"Bricks")

# class Square_Room(pc_types.Assembly):
#     show_in_library = True
#     category_name = "ROOMS"
#     subcategory_name = "WALLS"

#     def render(self):
#         self.draw()

#     def draw(self):
#         start_time = time.time()
        
#         #Create Assembly
#         props = hb_utils.get_scene_props(bpy.context.scene)
#         self.create_assembly("Room")

#         #ASSIGN PROPERTY
#         self.obj_bp["IS_ROOM_BP"] = True
#         self.obj_bp["PROMPT_ID"] = "home_builder.room_prompts" 
#         self.obj_bp["MENU_ID"] = "HOME_BUILDER_MT_wall_commands"

#         #Set Default Dimensions
#         self.obj_x.location.x = pc_unit.inch(120) #Length
#         self.obj_y.location.y = pc_unit.inch(120) #Depth
#         self.obj_z.location.z = props.wall_height

#         #Get Product Variables
#         length = self.obj_x.pyclone.get_var('location.x','length')
#         depth = self.obj_y.pyclone.get_var('location.y','depth')
#         height = self.obj_z.pyclone.get_var('location.z','height')

#         #Add Prompts
#         wall_thickness = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Wall Thickness")

#         #Set Prompt Formulas or default values
#         wall_thickness.set_value(props.wall_thickness)

#         #Get Prompt Variables
#         wall_thickness = wall_thickness.get_var("wall_thickness")

#         wall = Mesh_Wall()
#         wall.draw_wall()
#         left_wall = self.add_assembly(wall)
#         # left_wall.draw_wall()
#         left_wall.obj_bp.location = (0,0,0)
#         left_wall.obj_bp.parent = self.obj_bp            
#         left_wall.set_name("Left Wall")
#         left_wall.loc_x(value=0)
#         left_wall.loc_y(value=0)
#         left_wall.loc_z(value=0)
#         left_wall.rot_z(value=math.radians(90))
#         left_wall.dim_x('depth',[depth])
#         left_wall.dim_y('wall_thickness',[wall_thickness])
#         left_wall.dim_z('height',[height])      
#         left_wall.get_prompt("Left Angle").set_value(-45)
#         left_wall.get_prompt("Right Angle").set_value(45)  

#         wall = Mesh_Wall()
#         wall.draw_wall()
#         back_wall = self.add_assembly(wall)
#         # back_wall.draw_wall()
#         back_wall.obj_bp.location = (0,0,0)
#         back_wall.obj_bp.parent = self.obj_bp            
#         back_wall.set_name("Back Wall")
#         back_wall.loc_x(value=0)
#         back_wall.loc_y('depth',[depth])
#         back_wall.loc_z(value=0)
#         back_wall.rot_z(value=math.radians(0))
#         back_wall.dim_x('length',[length])
#         back_wall.dim_y('wall_thickness',[wall_thickness])
#         back_wall.dim_z('height',[height])
#         back_wall.get_prompt("Left Angle").set_value(-45)
#         back_wall.get_prompt("Right Angle").set_value(45)   

#         wall = Mesh_Wall()
#         wall.draw_wall()
#         right_wall = self.add_assembly(wall)
#         # right_wall.draw_wall()
#         right_wall.obj_bp.location = (0,0,0)
#         right_wall.obj_bp.parent = self.obj_bp            
#         right_wall.set_name("Right Wall")
#         right_wall.loc_x('length',[length])
#         right_wall.loc_y('depth',[depth])
#         right_wall.loc_z(value=0)
#         right_wall.rot_z(value=math.radians(-90))
#         right_wall.dim_x('depth',[depth])
#         right_wall.dim_y('wall_thickness',[wall_thickness])
#         right_wall.dim_z('height',[height])       
#         right_wall.get_prompt("Left Angle").set_value(-45)
#         right_wall.get_prompt("Right Angle").set_value(45)

#         wall = Mesh_Wall()
#         wall.draw_wall()
#         front_wall = self.add_assembly(wall)
#         # front_wall.draw_wall()
#         front_wall.obj_bp.location = (0,0,0)
#         front_wall.obj_bp.parent = self.obj_bp        
#         front_wall.set_name("Front Wall")
#         front_wall.loc_x('length',[length])
#         front_wall.loc_y(value=0)
#         front_wall.loc_z(value=0)
#         front_wall.rot_z(value=math.radians(180))
#         front_wall.dim_x('length',[length])
#         front_wall.dim_y('wall_thickness',[wall_thickness])
#         front_wall.dim_z('height',[height])
#         front_wall.get_prompt("Left Angle").set_value(-45)
#         front_wall.get_prompt("Right Angle").set_value(45)

#         print("ROOM: Draw Time --- %s seconds ---" % (time.time() - start_time))   