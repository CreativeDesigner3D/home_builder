import bpy
import os
import math
from pc_lib import pc_types, pc_unit, pc_utils
from . import assemblies_cabinet
from . import paths_cabinet
from . import const_cabinets as const
from . import prompts_cabinet

class Cabinet_Exterior(pc_types.Assembly):
    carcass_type = '' #Base, Tall, Upper
    overlay_prompts = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if "OVERLAY_PROMPTS" in child:
                    self.overlay_prompts = child

    def add_overlay_prompts(self):
        hot = self.get_prompt("Half Overlay Top").get_var('hot')
        hob = self.get_prompt("Half Overlay Bottom").get_var('hob')
        hol = self.get_prompt("Half Overlay Left").get_var('hol')
        hor = self.get_prompt("Half Overlay Right").get_var('hor')
        material_thickness = self.get_prompt("Material Thickness").get_var('material_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        tr = self.get_prompt("Top Reveal").get_var('tr')
        br = self.get_prompt("Bottom Reveal").get_var('br')
        lr = self.get_prompt("Left Reveal").get_var('lr')
        rr = self.get_prompt("Right Reveal").get_var('rr')

        self.overlay_prompts = self.add_empty('Overlay Prompt Obj')
        self.overlay_prompts['OVERLAY_PROMPTS'] = True
        self.overlay_prompts.empty_display_size = .01

        to = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Top Overlay")
        bo = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Bottom Overlay")
        lo = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Left Overlay")
        ro = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Right Overlay")

        to.set_formula('IF(hot,(material_thickness-vertical_gap)/2,material_thickness-tr)',[hot,material_thickness,vertical_gap,tr])
        bo.set_formula('IF(hob,(material_thickness-vertical_gap)/2,material_thickness-br)',[hob,material_thickness,vertical_gap,br])
        lo.set_formula('IF(hol,(material_thickness-vertical_gap)/2,material_thickness-lr)',[hol,material_thickness,vertical_gap,lr])
        ro.set_formula('IF(hor,(material_thickness-vertical_gap)/2,material_thickness-rr)',[hor,material_thickness,vertical_gap,rr])

        return to, bo, lo, ro

    def add_door_pull(self,front,pointer):
        pull_length = self.get_prompt("Pull Length")  
        if not pull_length:
            return #DON'T ADD PULLS TO APPLIED ENDS

        pull_path = os.path.join(assemblies_cabinet.get_pull_path(),pointer.category,pointer.item_name + ".blend")
        pull_obj = pc_utils.get_object(pull_path) 
        front.add_object(pull_obj)

        pull_length.set_value(round(pull_obj.dimensions.x,2))

        #VARS
        door_width = front.obj_y.pyclone.get_var('location.y','door_width')
        door_length = front.obj_x.pyclone.get_var('location.x','door_length')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        hide = front.get_prompt("Hide").get_var('hide')
        pull_length_var = pull_length.get_var('pull_length_var')
        base_pull_vertical_location = self.get_prompt("Base Pull Vertical Location").get_var('base_pull_vertical_location')
        tall_pull_vertical_location = self.get_prompt("Tall Pull Vertical Location").get_var('tall_pull_vertical_location')
        upper_pull_vertical_location = self.get_prompt("Upper Pull Vertical Location").get_var('upper_pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')

        #FORMULAS
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        if pointer.name == 'Base Cabinet Pulls':
            pull_obj.pyclone.loc_x('door_length-base_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if pointer.name == 'Tall Cabinet Pulls':
            pull_obj.pyclone.loc_x('tall_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if pointer.name == 'Upper Cabinet Pulls':
            pull_obj.pyclone.loc_x('upper_pull_vertical_location+(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])     
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.loc_y('IF(door_width>0,door_width-pull_horizontal_location,door_width+pull_horizontal_location)',[door_width,pull_horizontal_location])
        pull_obj.pyclone.hide('IF(OR(hide,turn_off_pulls),True,False)',[hide,turn_off_pulls])

        pull_obj['IS_CABINET_PULL'] = True
        # home_builder_pointers.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")  
        # home_builder_utils.get_object_props(pull_obj).pointer_name = pointer.name

    def draw_prompts(self,layout,context):
        open_door = self.get_prompt("Open Door")
        front_height_calculator = self.get_calculator("Front Height Calculator")
        door_swing = self.get_prompt("Door Swing")
        turn_off_pulls = self.get_prompt("Turn Off Pulls")
        top_drawer_front_height = self.get_prompt("Top Drawer Front Height")
        carcass_type = self.get_prompt("Carcass Type")
        add_two_drawer_fronts = self.get_prompt("Add Two Drawer Fronts")
        center_pulls_on_front = self.get_prompt("Center Pull On Front")
        drawer_pull_vertical_location = self.get_prompt("Drawer Pull Vertical Location")

        if open_door:
            open_door.draw(layout,allow_edit=False)

        if door_swing:
            door_swing.draw(layout,allow_edit=False)    

        if turn_off_pulls:
            row = layout.row()
            row.label(text="Pulls:")
            row.prop(turn_off_pulls,'checkbox_value',text="Off")

            pull_horizontal_location = self.get_prompt("Pull Horizontal Location")

            if carcass_type.get_value() == 'Base':
                base_pull_location = self.get_prompt("Base Pull Vertical Location")
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(base_pull_location,'distance_value',text="Z")
            if carcass_type.get_value() == 'Tall':
                tall_pull_location = self.get_prompt("Tall Pull Vertical Location")
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(tall_pull_location,'distance_value',text="Z")                
            if carcass_type.get_value() == 'Upper':
                upper_pull_location = self.get_prompt("Upper Pull Vertical Location")     
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(upper_pull_location,'distance_value',text="Z")                       
            if carcass_type.get_value() == 'Drawer':
                pass            

        if center_pulls_on_front:
            row = layout.row()
            row.prop(center_pulls_on_front,'checkbox_value',text="Center Drawer Pulls")

            if drawer_pull_vertical_location:
                if center_pulls_on_front.get_value() == False:
                    row.prop(drawer_pull_vertical_location,'distance_value',text="Pull Location")

        if add_two_drawer_fronts:
            row = layout.row()
            row.label(text="Add Two Drawer Fronts")
            row.prop(add_two_drawer_fronts,'checkbox_value',text="")

        if top_drawer_front_height:
            row = layout.row()
            row.label(text="Top Drawer Front Height")
            row.prop(top_drawer_front_height,'distance_value',text="")

        if front_height_calculator:
            for prompt in front_height_calculator.prompts:
                prompt.draw(layout)      
            row = layout.row()   
            row.scale_y = 1.3
            props = row.operator('pc_prompts.run_calculator',text="Calculate Drawer Front Heights")
            props.calculator_name = front_height_calculator.name
            props.obj_name = self.obj_prompts.name        

class Doors(Cabinet_Exterior):

    door_swing = 0 # Left = 0, Right = 1, Double = 2

    def draw(self):
        self.create_assembly("Doors")
        self.obj_bp["IS_DOORS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True       

        prompts_cabinet.add_carcass_prompts(self)
        prompts_cabinet.add_cabinet_prompts(self)
        prompts_cabinet.add_door_prompts(self)
        prompts_cabinet.add_front_prompts(self)
        prompts_cabinet.add_front_overlay_prompts(self)
        prompts_cabinet.add_pull_prompts(self)
        prompts_cabinet.add_thickness_prompts(self)    

        self.add_prompt("Back Inset",'DISTANCE',0)    

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        #VARS
        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        hide_doors = self.get_prompt("Hide").get_var('hide_doors')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        # props = home_builder_utils.get_scene_props(bpy.context.scene)

        # front_pointer = None
        # pull_pointer = None
        # if self.carcass_type == 'Base':
        #     front_pointer = props.cabinet_door_pointers["Base Cabinet Doors"]
        #     pull_pointer = props.pull_pointers["Base Cabinet Pulls"]
        # if self.carcass_type == 'Tall':
        #     front_pointer = props.cabinet_door_pointers["Tall Cabinet Doors"]
        #     pull_pointer = props.pull_pointers["Tall Cabinet Pulls"]
        # if self.carcass_type == 'Upper':
        #     front_pointer = props.cabinet_door_pointers["Upper Cabinet Doors"]
        #     pull_pointer = props.pull_pointers["Upper Cabinet Pulls"]

        #LEFT DOOR
        l_door = assemblies_cabinet.add_door_assembly(self)
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,hide_doors)',[door_swing,hide_doors])
        # self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = assemblies_cabinet.add_door_assembly(self)
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,hide_doors)',[door_swing,hide_doors])
        # self.add_door_pull(r_door,pull_pointer)

        self.set_prompts()        