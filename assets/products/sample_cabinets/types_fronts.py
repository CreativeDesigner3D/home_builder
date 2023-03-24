import bpy
import math
from . import paths_cabinet
from . import material_pointers_cabinet
from . import prompts_cabinet
from . import const_cabinets as const
from pc_lib import pc_types, pc_unit, pc_utils

class Fronts(pc_types.Assembly):

    carcass_type = '' #Base, Tall, Upper
    overlay_prompts = None

    def add_overlay_prompts(self):
        inset = self.get_prompt("Inset Front").get_var('inset')
        i_reveal = self.get_prompt("Inset Reveal").get_var('i_reveal')
        hot = self.get_prompt("Half Overlay Top").get_var('hot')
        hob = self.get_prompt("Half Overlay Bottom").get_var('hob')
        hol = self.get_prompt("Half Overlay Left").get_var('hol')
        hor = self.get_prompt("Half Overlay Right").get_var('hor')
        mat_thickness = self.get_prompt("Material Thickness").get_var('mat_thickness')
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

        to.set_formula('IF(inset,-i_reveal,IF(hot,(mat_thickness-vertical_gap)/2,mat_thickness-tr))',[inset,i_reveal,hot,mat_thickness,vertical_gap,tr])
        bo.set_formula('IF(inset,-i_reveal,IF(hob,(mat_thickness-vertical_gap)/2,mat_thickness-br))',[inset,i_reveal,hob,mat_thickness,vertical_gap,br])
        lo.set_formula('IF(inset,-i_reveal,IF(hol,(mat_thickness-vertical_gap)/2,mat_thickness-lr))',[inset,i_reveal,hol,mat_thickness,vertical_gap,lr])
        ro.set_formula('IF(inset,-i_reveal,IF(hor,(mat_thickness-vertical_gap)/2,mat_thickness-rr))',[inset,i_reveal,hor,mat_thickness,vertical_gap,rr])

        return to, bo, lo, ro

    def add_door_pull(self,front,path=""):
        pull_length = self.get_prompt("Pull Length")  
        if not pull_length:
            return #DON'T ADD PULLS TO APPLIED ENDS

        if path == "":
            pull_path = paths_cabinet.get_current_handle_path()
        else:
            pull_path = path
        pull_obj = pc_utils.get_object(pull_path) 
        front.add_object(pull_obj)

        pull_length.set_value(round(pull_obj.dimensions.x,2))

        part_name = front.obj_bp.hb_cabinet.part_name

        #VARS
        door_width = front.obj_y.pyclone.get_var('location.y','door_width')
        door_length = front.obj_x.pyclone.get_var('location.x','door_length')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        hide = front.get_prompt("Hide").get_var('hide')
        pull_length_var = pull_length.get_var('pull_length_var')
        swing = self.get_prompt("Door Swing").get_var('swing')
        bp_vert_loc = self.get_prompt("Base Pull Vertical Location").get_var('bp_vert_loc')
        tp_vert_loc = self.get_prompt("Tall Pull Vertical Location").get_var('tp_vert_loc')
        up_vert_loc = self.get_prompt("Upper Pull Vertical Location").get_var('up_vert_loc')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location")
        ph_loc = pull_horizontal_location.get_var('ph_loc')
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')
        door_type_prompt = self.get_prompt("Door Type")

        #FORMULAS
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        if door_type_prompt.get_value() == 'Base':
            pull_obj.pyclone.loc_x('IF(swing==3,door_length-ph_loc,IF(swing==4,door_length-ph_loc,door_length-bp_vert_loc-(pull_length_var/2)))',
            [swing,ph_loc,door_length,bp_vert_loc,pull_length_var])  
        if door_type_prompt.get_value() == 'Tall':
            pull_obj.pyclone.loc_x('IF(swing==3,door_length-ph_loc,IF(swing==4,door_length-ph_loc,tp_vert_loc-(pull_length_var/2)))',
            [swing,ph_loc,door_length,tp_vert_loc,pull_length_var])  
        if door_type_prompt.get_value() == 'Upper':
            pull_obj.pyclone.loc_x('IF(swing==3,door_length-ph_loc,IF(swing==4,door_length-ph_loc,up_vert_loc+(pull_length_var/2)))',
            [swing,ph_loc,door_length,up_vert_loc,pull_length_var])
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.rot_z('IF(swing>2,radians(90),0)',[swing])
        pull_obj.pyclone.loc_y('IF(swing>2,door_width/2,IF(door_width>0,door_width-ph_loc,door_width+ph_loc))',
                               [swing,door_width,ph_loc])
        pull_obj.pyclone.hide('IF(OR(hide,turn_off_pulls),True,False)',[hide,turn_off_pulls])

        pull_obj[const.CABINET_HANDLE_TAG] = True

        if 'Left' in part_name:
            pull_obj.pyclone.rot_z('IF(swing>2,radians(90),radians(180))',[swing])
        else:
            pull_obj.pyclone.rot_z('IF(swing>2,radians(90),0)',[swing])      

        material_pointers_cabinet.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")  
        return pull_obj

    def add_drawer_pull(self,front,path=""):
        drawer_front_width = front.obj_y.pyclone.get_var('location.y',"drawer_front_width")
        drawer_front_height = front.obj_x.pyclone.get_var('location.x',"drawer_front_height")
        front_thickness = front.obj_z.pyclone.get_var('location.z',"front_thickness")
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')
        hide_drawer_front = front.get_prompt("Hide").get_var('hide_drawer_front')
        center_pull_prompt = self.get_prompt("Center Pull On Front")
        vert_location_prompt = self.get_prompt("Drawer Pull Vertical Location")
        center_pull = center_pull_prompt.get_var('center_pull')
        vert_loc = vert_location_prompt.get_var('vert_loc')

        if path == "":
            pull_path = paths_cabinet.get_current_handle_path()
        else:
            pull_path = path
        pull_obj = pc_utils.get_object(pull_path)
        pull_obj[const.CABINET_HANDLE_TAG] = True

        front.add_object(pull_obj)
        pull_obj.parent = front.obj_bp
        pull_obj.pyclone.loc_x('IF(center_pull,(drawer_front_height/2),drawer_front_height-vert_loc)',[drawer_front_height,center_pull,vert_loc])
        pull_obj.pyclone.loc_y('(fabs(drawer_front_width)/2)*-1',[drawer_front_width])
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.rotation_euler.y = math.radians(0)
        pull_obj.rotation_euler.z = math.radians(-90)
        pull_obj.pyclone.hide('IF(turn_off_pulls,True,hide_drawer_front)',[turn_off_pulls,hide_drawer_front])

        material_pointers_cabinet.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")

    def set_child_properties(self,obj,insert_bp):
        pc_utils.update_id_props(obj,insert_bp)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True              
        for child in obj.children:
            self.set_child_properties(child,insert_bp)

    def replace_front(self,old_door_panel,new_front,is_door=True):
        hb_props = bpy.context.scene.hb_cabinet
        if "FRONT_NUMBER" in old_door_panel.obj_bp:
            new_front.obj_bp["FRONT_NUMBER"] = old_door_panel.obj_bp["FRONT_NUMBER"]

        pull_length = old_door_panel.get_prompt("Pull Length")
        top_overlay = old_door_panel.get_prompt("Top Overlay")
        bottom_overlay = old_door_panel.get_prompt("Bottom Overlay")
        left_overlay = old_door_panel.get_prompt("Left Overlay")
        right_overlay = old_door_panel.get_prompt("Right Overlay")

        if pull_length:
            new_front.add_prompt("Pull Length",'DISTANCE',pull_length.get_value())  
        if top_overlay:
            new_front.add_prompt("Top Overlay",'DISTANCE',top_overlay.get_value())  
        if bottom_overlay:
            new_front.add_prompt("Bottom Overlay",'DISTANCE',bottom_overlay.get_value())  
        if left_overlay:
            new_front.add_prompt("Left Overlay",'DISTANCE',left_overlay.get_value()) 
        if right_overlay:
            new_front.add_prompt("Right Overlay",'DISTANCE',right_overlay.get_value()) 

        pc_utils.replace_assembly(old_door_panel,new_front)
        if is_door:
            new_front.obj_bp[const.DOOR_FRONT_TAG] = True
            self.add_door_pull(new_front)
        else:
            new_front.obj_bp[const.DRAWER_FRONT_TAG] = True
            self.add_drawer_pull(new_front)
        material_pointers_cabinet.assign_door_pointers(new_front)
        material_pointers_cabinet.assign_materials_to_assembly(new_front)            
        self.set_child_properties(new_front.obj_bp,self.obj_bp)

        center_pull_prompt = self.get_prompt("Center Pull On Front")
        if center_pull_prompt:
            center_pull_prompt.set_value(hb_props.center_pulls_on_drawer_front)
        
        pull_vert_loc = self.get_prompt("Drawer Pull Vertical Location")
        if pull_vert_loc:
            pull_vert_loc.set_value(hb_props.pull_vertical_location_drawers)

    def add_door_panel(self,front,location,to_var,bo_var,ro_var,lo_var):
        x = self.obj_x.pyclone.get_var('location.x','x') 
        z = self.obj_z.pyclone.get_var('location.z','z')  
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')  
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        inset = self.get_prompt("Inset Front").get_var('inset')
        hide_doors = self.get_prompt("Hide").get_var('hide_doors')
           
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')

        front.obj_bp[const.DOOR_FRONT_TAG] = True
        front.add_prompt("Pull Length",'DISTANCE',0)
        top_o = front.add_prompt("Top Overlay",'DISTANCE',0)
        top_o.set_formula("to_var",[to_var])
        bottom_o = front.add_prompt("Bottom Overlay",'DISTANCE',0)
        bottom_o.set_formula("bo_var",[bo_var])
        left_o = front.add_prompt("Left Overlay",'DISTANCE',0)
        left_o.set_formula("lo_var",[lo_var])
        right_o = front.add_prompt("Right Overlay",'DISTANCE',0)
        right_o.set_formula("ro_var",[ro_var])
        front.loc_y('IF(inset,front_thickness,-door_to_cabinet_gap)',[inset,front_thickness,door_to_cabinet_gap])
        front.rot_x(value = math.radians(90))
        front.rot_y(value = math.radians(-90))    
        front.dim_z('front_thickness',[front_thickness])  
        hide = front.get_prompt("Hide")  
        if location == 'Left':
            hide.set_formula('IF(hide_doors,True,IF(OR(door_swing==0,door_swing==2),False,True))',[hide_doors,door_swing])
            front.loc_x('-lo_var',[lo_var])
            front.rot_z('-door_rotation*(open_door/100)',[door_rotation,open_door])
            front.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])
        if location == 'Right':
            hide.set_formula('IF(hide_doors,True,IF(OR(door_swing==1,door_swing==2),False,True))',[hide_doors,door_swing])
            front.loc_x('x+ro_var',[x,ro_var])
            front.rot_z('door_rotation*(open_door/100)',[door_rotation,open_door])
            front.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])  
        if location == 'Top':
            hide.set_formula('IF(hide_doors,True,IF(door_swing==3,False,True))',[hide_doors,door_swing])
            front.rot_x(value = 0)
            front.rot_y('radians(90)-(door_rotation*(open_door/100))',[door_rotation,open_door])  
            front.rot_z(value = math.radians(-90)) 
            front.loc_x('x+ro_var',[x,ro_var])
            front.dim_y('(x+lo_var+ro_var)*-1',[x,lo_var,ro_var])  
        if location == 'Bottom':
            front.rot_x(value = 0)
            front.rot_y('radians(-90)-(door_rotation*(open_door/100))',[door_rotation,open_door])  
            front.rot_z(value = math.radians(90))  
            hide.set_formula('IF(hide_doors,True,IF(door_swing==4,False,True))',[hide_doors,door_swing])
            front.loc_x('-lo_var',[lo_var])
            front.dim_y('(x+lo_var+ro_var)*-1',[x,lo_var,ro_var])  

        front.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        if location == 'Top':
            front.loc_z('z+to_var',[z,to_var])
        else:
            front.loc_z('-bo_var',[bo_var])

        material_pointers_cabinet.assign_door_pointers(front)
        material_pointers_cabinet.assign_materials_to_assembly(front)

        pull_obj = self.add_door_pull(front)
        return front

    def add_prompts(self,include_door_prompts,include_drawer_prompts):
        if include_door_prompts:
            prompts_cabinet.add_door_prompts(self)
            prompts_cabinet.add_door_pull_prompts(self)
        if include_drawer_prompts:
            prompts_cabinet.add_drawer_prompts(self)
            prompts_cabinet.add_drawer_pull_prompts(self)
        
        prompts_cabinet.add_front_prompts(self)
        prompts_cabinet.add_front_overlay_prompts(self)
        prompts_cabinet.add_thickness_prompts(self)