import bpy
import math
from pc_lib import pc_utils, pc_types
from . import material_pointers_cabinet
from . import types_cabinet
from . import const_cabinets as const
from . import enum_cabinets

def update_sink(self,context):
    self.sink_changed = True

def update_faucet(self,context):
    self.faucet_changed = True

def update_cooktop(self,context):
    self.cooktop_changed = True

def update_range_hood(self,context):
    self.range_hood_changed = True

class hb_sample_cabinets_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.cabinet_prompts"
    bl_label = "Cabinet Prompts"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CARCASS',"Carcass","Carcass Options"),
                                                ('EXTERIOR',"Exterior","Exterior Options"),
                                                ('INTERIOR',"Interior","Interior Options"),
                                                ('SPLITTER',"Openings","Openings Options")])

    position: bpy.props.EnumProperty(name="Position",
                                     items=[('OFF',"Off","Turn off automatic positioning"),
                                            ('LEFT',"Left","Bump Left"),
                                            ('RIGHT',"Right","Bump Right"),
                                            ('FILL',"Fill","Fill Area")])

    default_width = 0
    cabinet = None

    sink_changed: bpy.props.BoolProperty(name="Sink Changed",default=False)
    sink_category: bpy.props.EnumProperty(name="Sink Category",
        items=enum_cabinets.enum_sink_categories,
        update=enum_cabinets.update_sink_category)
    sink_name: bpy.props.EnumProperty(name="Sink Name",
        items=enum_cabinets.enum_sink_names,
        update=update_sink)

    faucet_changed: bpy.props.BoolProperty(name="Faucet Changed",default=False)
    faucet_category: bpy.props.EnumProperty(name="Faucet Category",
        items=enum_cabinets.enum_faucet_categories,
        update=enum_cabinets.update_faucet_category)
    faucet_name: bpy.props.EnumProperty(name="Faucet Name",
        items=enum_cabinets.enum_faucet_names,
        update=update_faucet)

    cooktop_changed: bpy.props.BoolProperty(name="Cooktop Changed",default=False)
    cooktop_category: bpy.props.EnumProperty(name="Cooktop Category",
        items=enum_cabinets.enum_cooktop_categories,
        update=enum_cabinets.update_cooktop_category)
    cooktop_name: bpy.props.EnumProperty(name="Cooktop Name",
        items=enum_cabinets.enum_cooktop_names,
        update=update_cooktop)

    range_hood_changed: bpy.props.BoolProperty(name="Range Hood Changed",default=False)
    range_hood_category: bpy.props.EnumProperty(name="Range Hood Category",
        items=enum_cabinets.enum_range_hood_categories,
        update=enum_cabinets.update_range_hood_category)
    range_hood_name: bpy.props.EnumProperty(name="Range Hood Name",
        items=enum_cabinets.enum_range_hood_names,
        update=update_range_hood)

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        #THIS IS BECAUSE POPUP DIALOGS CANNOT DISPLAY UILISTS ON INVOKE
        self.product_tabs = 'MAIN'
        self.cabinet = None

    def update_product_size(self):
        self.cabinet.obj_x.location.x = self.width

        if 'IS_MIRROR' in self.cabinet.obj_y and self.cabinet.obj_y['IS_MIRROR']:
            self.cabinet.obj_y.location.y = -self.depth
        else:
            self.cabinet.obj_y.location.y = self.depth
        
        if 'IS_MIRROR' in self.cabinet.obj_z and self.cabinet.obj_z['IS_MIRROR']:
            self.cabinet.obj_z.location.z = -self.height
        else:
            self.cabinet.obj_z.location.z = self.height

    def update_materials(self,context):
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")

            # if carcass.design_carcass:
            material_pointers_cabinet.update_design_carcass_pointers(carcass.design_carcass,
                                                                    left_finished_end.get_value(),
                                                                    right_finished_end.get_value(),
                                                                    finished_back.get_value(),
                                                                    finished_top.get_value(),
                                                                    finished_bottom.get_value())
                # if carcass.design_base_assembly:                                                     
            material_pointers_cabinet.update_design_base_assembly_pointers(carcass.design_base_assembly,
                                                                    left_finished_end.get_value(),
                                                                    right_finished_end.get_value(),
                                                                    finished_back.get_value())                                                                     
            # else:
            #     if finished_back and left_finished_end and right_finished_end:
            #         home_builder_pointers.update_side_material(carcass.left_side,left_finished_end.get_value(),finished_back.get_value(),finished_top.get_value(),finished_bottom.get_value())
            #         home_builder_pointers.update_side_material(carcass.right_side,right_finished_end.get_value(),finished_back.get_value(),finished_top.get_value(),finished_bottom.get_value())
            #         home_builder_pointers.update_top_material(carcass.top,finished_back.get_value(),finished_top.get_value())
            #         home_builder_pointers.update_bottom_material(carcass.bottom,finished_back.get_value(),finished_bottom.get_value())
            #         home_builder_pointers.update_cabinet_back_material(carcass.back,finished_back.get_value())

    def update_fillers(self,context):
        left_adjustment_width = self.cabinet.get_prompt("Left Adjustment Width")
        right_adjustment_width = self.cabinet.get_prompt("Right Adjustment Width")
        if left_adjustment_width.get_value() > 0 and self.cabinet.left_filler is None:
            self.cabinet.add_left_filler()
            pc_utils.update_assembly_id_props(self.cabinet.left_filler,self.cabinet)
        if right_adjustment_width.get_value() > 0 and self.cabinet.right_filler is None:
            self.cabinet.add_right_filler()   
            pc_utils.update_assembly_id_props(self.cabinet.right_filler,self.cabinet)          
        if left_adjustment_width.get_value() == 0 and self.cabinet.left_filler is not None:
            pc_utils.delete_object_and_children(self.cabinet.left_filler.obj_bp)
            self.cabinet.left_filler = None
        if right_adjustment_width.get_value() == 0 and self.cabinet.right_filler is not None:
            pc_utils.delete_object_and_children(self.cabinet.right_filler.obj_bp)
            self.cabinet.right_filler = None   

    def update_range_hood(self,context):
        if self.range_hood_changed:
            self.range_hood_changed = False
            add_range_hood = self.cabinet.get_prompt("Add Range Hood")
            if self.cabinet.range_hood_appliance:
                pc_utils.delete_object_and_children(self.cabinet.range_hood_appliance.obj_bp)   

            if add_range_hood.get_value():
                self.cabinet.add_range_hood(self.range_hood_category,self.range_hood_name)
                pc_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def update_sink(self,context):
        if self.sink_changed:
            self.sink_changed = False
            add_sink = self.cabinet.get_prompt("Add Sink")
            if self.cabinet.sink_appliance:
                pc_utils.delete_object_and_children(self.cabinet.sink_appliance.obj_bp)   

            if add_sink.get_value():
                self.cabinet.add_sink(self.sink_category,self.sink_name)
                pc_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def update_cooktop(self,context):
        if self.cooktop_changed:
            self.cooktop_changed = False
            add_cooktop = self.cabinet.get_prompt("Add Cooktop")
            if self.cabinet.cooktop_appliance:
                pc_utils.delete_object_and_children(self.cabinet.cooktop_appliance.obj_bp)   

            if add_cooktop.get_value():
                self.cabinet.add_cooktop(self.cooktop_category,self.cooktop_name)
                pc_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def update_faucet(self,context):
        if self.faucet_changed:
            self.faucet_changed = False
            add_faucet = self.cabinet.get_prompt("Add Faucet")
            if self.cabinet.faucet_appliance:
                pc_utils.delete_object_and_children(self.cabinet.faucet_appliance)   

            if add_faucet.get_value():
                self.cabinet.add_faucet(self.faucet_category,self.faucet_name)
                pc_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def check(self, context):
        self.update_product_size()
        self.update_fillers(context)
        self.update_sink(context)
        self.update_range_hood(context)
        self.update_cooktop(context)
        self.update_faucet(context)        
        self.update_materials(context)
        self.cabinet.update_range_hood_location()
        return True

    def execute(self, context):
        add_faucet = self.cabinet.get_prompt("Add Faucet")
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")
        add_sink = self.cabinet.get_prompt("Add Sink")
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")
        if add_faucet:
            if self.cabinet.faucet_appliance and not add_faucet.get_value():
                pc_utils.delete_object_and_children(self.cabinet.faucet_appliance)   
        if add_cooktop:
            if self.cabinet.cooktop_appliance and not add_cooktop.get_value():
                pc_utils.delete_object_and_children(self.cabinet.cooktop_appliance.obj_bp)   
        if add_sink:
            if self.cabinet.sink_appliance and not add_sink.get_value():
                pc_utils.delete_object_and_children(self.cabinet.sink_appliance.obj_bp)   
        if add_range_hood:
            if self.cabinet.range_hood_appliance and not add_range_hood.get_value():
                pc_utils.delete_object_and_children(self.cabinet.range_hood_appliance.obj_bp)                       
        return {'FINISHED'}

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def invoke(self,context,event):
        self.reset_variables()
        self.get_assemblies(context)
        self.cabinet_name = self.cabinet.obj_bp.name
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
        self.default_width = self.cabinet.obj_x.location.x
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CABINET_TAG)
        self.cabinet = types_cabinet.Cabinet(bp)

    def draw_sink_prompts(self,layout,context):
        add_sink = self.cabinet.get_prompt("Add Sink")

        if not add_sink:
            return False

        layout.prop(add_sink,'checkbox_value',text="Add Sink")
        if add_sink.get_value():
            layout.prop(self,'sink_category',text="",icon='FILE_FOLDER')  
            if len(self.sink_name) > 0:
                layout.template_icon_view(self,"sink_name",show_labels=True)  

    def draw_faucet_prompts(self,layout,context):
        add_faucet = self.cabinet.get_prompt("Add Faucet")

        if not add_faucet:
            return False

        layout.prop(add_faucet,'checkbox_value',text="Add Faucet")
        if add_faucet.get_value():
            layout.prop(self,'faucet_category',text="",icon='FILE_FOLDER')  
            if len(self.sink_name) > 0:
                layout.template_icon_view(self,"faucet_name",show_labels=True)  

    def draw_cooktop_prompts(self,layout,context):
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")

        if not add_cooktop:
            return False

        layout.prop(add_cooktop,'checkbox_value',text="Add Cooktop")
        if add_cooktop.get_value():
            layout.prop(self,'cooktop_category',text="",icon='FILE_FOLDER')
            layout.template_icon_view(self,"cooktop_name",show_labels=True)

    def draw_range_hood_prompts(self,layout,context):
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")

        if not add_range_hood:
            return False

        layout.prop(add_range_hood,'checkbox_value',text="Add Range Hood")
        if add_range_hood.get_value():
            layout.prop(self,'range_hood_category',text="",icon='FILE_FOLDER')  
            layout.template_icon_view(self,"range_hood_name",show_labels=True)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_x):
            x = math.fabs(self.cabinet.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(self.cabinet.obj_x,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.cabinet.obj_x.name

        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_z):
            z = math.fabs(self.cabinet.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.cabinet.obj_z,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.cabinet.obj_z.name
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_y):
            y = math.fabs(self.cabinet.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.cabinet.obj_y,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.cabinet.obj_y.name
            
        if len(self.cabinet.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.cabinet.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
            
            col = row.column(align=True)
            col.prop(self.cabinet.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.cabinet.obj_bp,'rotation_euler',index=2,text="")  

        row = box.row()
        row.label(text='Height from Floor:')
        row.prop(self.cabinet.obj_bp,'location',index=2,text="")          

        # props = home_builder_utils.get_scene_props(context.scene)
        # row = box.row()
        # row.alignment = 'LEFT'
        # row.prop(props,'show_cabinet_placement_options',emboss=False,icon='TRIA_DOWN' if props.show_cabinet_placement_options else 'TRIA_RIGHT')
        # if props.show_cabinet_placement_options:
        #     row = box.row()
        #     row.label(text="Anchor X:")
        #     row.prop(self,'anchor_x',expand=True)
        #     row = box.row()
        #     row.label(text="Anchor Z:")
        #     row.prop(self,'anchor_z',expand=True)            

    def draw_carcass_prompts(self,layout,context):
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")
            toe_kick_height = carcass.get_prompt("Toe Kick Height")
            toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
            blind_panel_location = carcass.get_prompt("Blind Panel Location")
            blind_panel_width = carcass.get_prompt("Blind Panel Width")
            blind_panel_reveal = carcass.get_prompt("Blind Panel Reveal")
            # add_bottom_light = carcass.get_prompt("Add Bottom Light")
            # add_top_light = carcass.get_prompt("Add Top Light")
            # add_side_light = carcass.get_prompt("Add Side Light")
  
            col = layout.column(align=True)
            box = col.box()
            row = box.row()
            row.label(text="Carcass - " + carcass.obj_bp.name)

            if blind_panel_location and blind_panel_width and blind_panel_reveal:
                row = box.row()
                blind_panel_location.draw(row,allow_edit=False)  
                row = box.row()
                row.label(text="Blind Options:")  
                row.prop(blind_panel_width,'distance_value',text="Width")
                row.prop(blind_panel_reveal,'distance_value',text="Reveal")  

            if toe_kick_height and toe_kick_setback:
                row = box.row()
                row.label(text="Base Assembly:")   
                row.prop(toe_kick_height,'distance_value',text="Height")
                row.prop(toe_kick_setback,'distance_value',text="Setback")   

            if left_finished_end and right_finished_end and finished_back and finished_top and finished_bottom:
                row = box.row()
                row.label(text="Finish:")
                row.prop(left_finished_end,'checkbox_value',text="Left")
                row.prop(right_finished_end,'checkbox_value',text="Right")
                row.prop(finished_top,'checkbox_value',text="Top")
                row.prop(finished_bottom,'checkbox_value',text="Bottom")
                row.prop(finished_back,'checkbox_value',text="Back")

            # if add_bottom_light and add_top_light and add_side_light:
            #     row = box.row()
            #     row.label(text="Cabinet Lighting:")   
            #     row.prop(add_bottom_light,'checkbox_value',text="Bottom")
            #     row.prop(add_top_light,'checkbox_value',text="Top")
            #     row.prop(add_side_light,'checkbox_value',text="Side")  

    def draw_cabinet_prompts(self,layout,context):
        bottom_cabinet_height = self.cabinet.get_prompt("Bottom Cabinet Height")    
        left_adjustment_width = self.cabinet.get_prompt("Left Adjustment Width")       
        right_adjustment_width = self.cabinet.get_prompt("Right Adjustment Width")    
        add_sink = self.cabinet.get_prompt("Add Sink")
        add_faucet = self.cabinet.get_prompt("Add Faucet")
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")        
        ctop_front = self.cabinet.get_prompt("Countertop Overhang Front")
        ctop_back = self.cabinet.get_prompt("Countertop Overhang Back")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")
        ctop_right = self.cabinet.get_prompt("Countertop Overhang Right")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")   

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Cabinet Options - " + self.cabinet.obj_bp.name)

        if bottom_cabinet_height:
            row = box.row()
            row.label(text="Bottom Cabinet Height:")
            row.prop(bottom_cabinet_height,'distance_value',text="")           
   
        if left_adjustment_width and right_adjustment_width:
            row = box.row()
            row.label(text="Filler Amount:")
            row.prop(left_adjustment_width,'distance_value',text="Left")
            row.prop(right_adjustment_width,'distance_value',text="Right")

        if ctop_front and ctop_back and ctop_left and ctop_right:
            row = box.row()
            row.label(text="Top Overhang:")       
            row.prop(ctop_front,'distance_value',text="Front")      
            row.prop(ctop_back,'distance_value',text="Rear")  
            row.prop(ctop_left,'distance_value',text="Left")  
            row.prop(ctop_right,'distance_value',text="Right")    

        if add_sink and add_faucet:
            box = layout.box()
            box.label(text="Cabinet Sink Selection")
            split = box.split()
            self.draw_sink_prompts(split.column(),context)
            self.draw_faucet_prompts(split.column(),context)

        if add_cooktop and add_range_hood:
            box = layout.box()
            box.label(text="Cabinet Cooktop Selection")
            split = box.split()
            self.draw_cooktop_prompts(split.column(),context)
            self.draw_range_hood_prompts(split.column(),context)

    def draw(self, context):
        layout = self.layout
        info_box = layout.box()
        
        # obj_props = home_builder_utils.get_object_props(self.cabinet.obj_bp)
        # scene_props = home_builder_utils.get_scene_props(context.scene)

        # mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        
        row = info_box.row(align=True)
        row.prop(self.cabinet.obj_bp,'name',text="Name")
        # row.separator()
        # row.menu('HOME_BUILDER_MT_change_product_material_group',text=mat_group.name,icon='COLOR')
        # row.operator('home_builder.update_product_material_group',text="",icon='FILE_REFRESH').object_name = self.cabinet.obj_bp.name

        self.draw_product_size(layout,context)

        prompt_box = layout.box()

        row = prompt_box.row(align=True)
        row.prop_enum(self, "product_tabs", 'MAIN') 
        row.prop_enum(self, "product_tabs", 'CARCASS') 
        row.prop_enum(self, "product_tabs", 'EXTERIOR') 
        row.prop_enum(self, "product_tabs", 'INTERIOR') 

        if self.product_tabs == 'MAIN':
            self.draw_cabinet_prompts(prompt_box,context)   
        
        if self.product_tabs == 'CARCASS':
            self.draw_carcass_prompts(prompt_box,context)

        if self.product_tabs == 'EXTERIOR':
            for carcass in reversed(self.cabinet.carcasses):
                if carcass.exterior:
                    box = prompt_box.box()
                    box.label(text=carcass.exterior.obj_bp.name)
                    carcass.exterior.draw_prompts(box,context)

        if self.product_tabs == 'INTERIOR':
            for carcass in reversed(self.cabinet.carcasses):
                if carcass.interior:
                    box = prompt_box.box()
                    box.label(text=carcass.interior.obj_bp.name)
                    carcass.interior.draw_prompts(box,context)


classes = (
    hb_sample_cabinets_OT_cabinet_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    