
import bpy
import math
from pc_lib import pc_utils, pc_types, pc_unit
from . import material_pointers_cabinet
from . import types_cabinet
from . import types_closet_starters
from . import const_cabinets as const
from . import enum_cabinets
from . import utils_cabinet

def update_sink(self,context):
    self.sink_changed = True

def update_faucet(self,context):
    self.faucet_changed = True

def update_cooktop(self,context):
    self.cooktop_changed = True

def update_range_hood(self,context):
    self.range_hood_changed = True

def update_closet_height(self,context):
    ''' EVENT changes height for all closet openings
    '''
    self.opening_1_height = self.set_height
    self.opening_2_height = self.set_height
    self.opening_3_height = self.set_height
    self.opening_4_height = self.set_height
    self.opening_5_height = self.set_height
    self.opening_6_height = self.set_height
    self.opening_7_height = self.set_height
    self.opening_8_height = self.set_height
    
    obj_product_bp = pc_utils.get_bp_by_tag(context.active_object,const.CLOSET_TAG)
    product = pc_types.Assembly(obj_product_bp)
    if self.is_base:
        product.obj_z.location.z = pc_unit.millimeter(float(self.set_height))

    for i in range(1,10):
        opening_height = product.get_prompt("Opening " + str(i) + " Height")
        if opening_height:
            opening_height.set_value(pc_unit.millimeter(float(self.set_height)))

def update_closet_depth(self,context):
    ''' EVENT changes depth for all closet openings
    '''
    obj_product_bp = pc_utils.get_bp_by_tag(context.active_object,const.CLOSET_TAG)
    product = pc_types.Assembly(obj_product_bp)
    if self.is_base:
        product.obj_y.location.y = -self.set_depth

    for i in range(1,10):
        opening_depth = product.get_prompt("Opening " + str(i) + " Depth")
        if opening_depth:
            opening_depth.set_value(self.set_depth)

def update_corner_closet_height(self,context):
    ''' EVENT changes height for corner closet
    '''
    obj_product_bp = pc_utils.get_bp_by_tag(context.active_object,const.CLOSET_INSIDE_CORNER_TAG)
    product = pc_types.Assembly(obj_product_bp)
    is_hanging = product.get_prompt('Is Hanging')
    if is_hanging.get_value():
        panel_height = product.get_prompt('Panel Height')
        panel_height.set_value(pc_unit.millimeter(float(self.set_height)))
    else:
        product.obj_z.location.z = pc_unit.millimeter(float(self.set_height))

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


class hb_closet_starters_OT_closet_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_starters.closet_prompts"
    bl_label = "Closet Prompts"

    is_base: bpy.props.BoolProperty(name="Is Base")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CONSTRUCTION',"Construction","Construction Options"),
                                                ('MACHINING',"Machining","Machining Options")])

    set_height: bpy.props.EnumProperty(name="Set Height",
                                       items=const.PANEL_HEIGHTS,
                                       default = '2131',
                                       update = update_closet_height)

    set_depth: bpy.props.FloatProperty(name="Set Depth",unit='LENGTH',precision=4,update=update_closet_depth)

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_2_height: bpy.props.EnumProperty(name="Opening 2 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_3_height: bpy.props.EnumProperty(name="Opening 3 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_4_height: bpy.props.EnumProperty(name="Opening 4 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_5_height: bpy.props.EnumProperty(name="Opening 5 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_6_height: bpy.props.EnumProperty(name="Opening 6 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_7_height: bpy.props.EnumProperty(name="Opening 7 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_8_height: bpy.props.EnumProperty(name="Opening 8 Height",
                                    items=const.PANEL_HEIGHTS,
                                    default = '2131')
    
    kick_height: bpy.props.EnumProperty(name="Kick Height",
                                    items=const.KICK_HEIGHTS,
                                    default = '96')

    closet = None
    calculators = []

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        #THIS IS BECAUSE POPUP DIALOGS CANNOT DISPLAY UILISTS ON INVOKE
        self.product_tabs = 'MAIN'
        self.closet = None
        self.calculators = []

    def update_product_size(self,context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
        self.closet.obj_x.location.x = self.width
        if hb_props.use_fixed_closet_heights:
            for i in range(1,9):
                opening_height = self.closet.get_prompt("Opening " + str(i) + " Height")
                if opening_height:
                    height = eval("float(self.opening_" + str(i) + "_height)/1000")
                    opening_height.set_value(height)

            kick_height = self.closet.get_prompt("Closet Kick Height")
            if kick_height:
                kick_height.distance_value = pc_unit.inch(float(self.kick_height) / 25.4)

    def update_materials(self,context):
        pass

    def update_bridge_parts(self,context):
        left_bridge = self.closet.get_prompt("Bridge Left")
        right_bridge = self.closet.get_prompt("Bridge Right")
        if left_bridge.get_value() == True and len(self.closet.left_bridge_parts) == 0:
            self.closet.add_left_blind_parts()
            for part in self.closet.left_bridge_parts:
                pc_utils.update_assembly_id_props(part,self.closet)
        if left_bridge.get_value() == False and len(self.closet.left_bridge_parts) > 0:
            for part in self.closet.left_bridge_parts:
                pc_utils.delete_object_and_children(part.obj_bp)
            self.closet.left_bridge_parts = []
        if right_bridge.get_value() == True and len(self.closet.right_bridge_parts) == 0:
            self.closet.add_right_blind_parts()
            for part in self.closet.right_bridge_parts:
                pc_utils.update_assembly_id_props(part,self.closet)
        if right_bridge.get_value() == False and len(self.closet.right_bridge_parts) > 0:
            for part in self.closet.right_bridge_parts:
                pc_utils.delete_object_and_children(part.obj_bp)
            self.closet.right_bridge_parts = []

    def update_fillers(self,context):
        left_side_wall_filler = self.closet.get_prompt("Left Side Wall Filler")
        right_side_wall_filler = self.closet.get_prompt("Right Side Wall Filler")
        if left_side_wall_filler.get_value() > 0 and self.closet.left_filler is None:
            self.closet.add_left_filler()
            pc_utils.update_assembly_id_props(self.closet.left_filler,self.closet)
        if right_side_wall_filler.get_value() > 0 and self.closet.right_filler is None:
            self.closet.add_right_filler()   
            pc_utils.update_assembly_id_props(self.closet.right_filler,self.closet)          
        if left_side_wall_filler.get_value() == 0 and self.closet.left_filler is not None:
            pc_utils.delete_object_and_children(self.closet.left_filler.obj_bp)
            self.closet.left_filler = None
        if right_side_wall_filler.get_value() == 0 and self.closet.right_filler is not None:
            pc_utils.delete_object_and_children(self.closet.right_filler.obj_bp)
            self.closet.right_filler = None   

    def set_default_size(self):
        self.width = self.closet.obj_x.location.x
        for i in range(1,9):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height_prompt:
                opening_height = round(pc_unit.meter_to_millimeter(opening_height_prompt.get_value()),0)
                for index, height in enumerate(const.PANEL_HEIGHTS):
                    if not opening_height >= int(height[0]):
                        exec('self.opening_' + str(i) + '_height = const.PANEL_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                        break
        kick_height = self.closet.get_prompt("Closet Kick Height")
        if kick_height:
            value = round(kick_height.distance_value * 1000,1)
            for index, height in enumerate(const.KICK_HEIGHTS):
                if not value >= float(height[0]):
                    self.kick_height = const.KICK_HEIGHTS[index - 1][0]
                    break

    def check(self, context):
        self.update_product_size(context)
        self.update_fillers(context)    
        self.update_bridge_parts(context) 
        self.update_materials(context)
        for calculator in self.calculators:
            calculator.calculate() 
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def invoke(self,context,event):
        self.reset_variables()
        self.get_assemblies(context)
        self.set_default_size()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        self.closet = types_closet_starters.Closet_Starter(bp)
        self.is_base = self.closet.is_base
        if self.is_base:
            self.set_depth = math.fabs(self.closet.obj_y.location.y)
        self.get_calculators(self.closet.obj_bp)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.closet.obj_x):
            x = math.fabs(self.closet.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',index=0,text="")
            row1.prop(self.closet.obj_x,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_x.name

        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.closet.obj_z):
            z = math.fabs(self.closet.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Set Height: ' + value)
        else:
            row1.label(text='Set Height:')
            row1.prop(self,'set_height',text="")
            row1.prop(self.closet.obj_z,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_z.name

        if not self.closet.is_base:
            row1 = col.row(align=True)
            if pc_utils.object_has_driver(self.closet.obj_z):
                z = math.fabs(self.closet.obj_z.location.z)
                value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
                row1.label(text='Hanging Height: ' + value)
            else:
                row1.label(text='Hanging Height:')
                row1.prop(self.closet.obj_z,'location',index=2,text="")
                row1.prop(self.closet.obj_z,'hide_viewport',text="")
                row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_z.name
        else:
            row1 = col.row(align=True)
            row1.label(text='Set Depth:')
            row1.prop(self,'set_depth',text="")
            row1.prop(self.closet.obj_y,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_y.name

        row1 = col.row(align=True)
        if len(self.closet.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.closet.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.closet.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.closet.obj_bp,'rotation_euler',index=2,text="")  

        # row = box.row()
        # row.label(text='Height from Floor:')
        # row.prop(self.closet.obj_bp,'location',index=2,text="")          

        # props = home_builder_utils.get_scene_props(context.scene)
        # row = box.row()
        # row.alignment = 'LEFT'
        # row.prop(props,'show_cabinet_placement_options',emboss=False,icon='TRIA_DOWN' if props.show_cabinet_tools else 'TRIA_RIGHT')
        # if props.show_cabinet_placement_options:
        #     row = box.row()
        #     row.label(text="TODO: Implement Closet Placement Options")

    def draw_construction_prompts(self,layout,context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
        kick_height = self.closet.get_prompt("Closet Kick Height")
        kick_setback = self.closet.get_prompt("Closet Kick Setback")
        r_bridge = self.closet.get_prompt("Bridge Right")         
        l_bridge = self.closet.get_prompt("Bridge Left")
        r_bridge = self.closet.get_prompt("Bridge Right") 
        l_bridge_width = self.closet.get_prompt("Left Bridge Shelf Width")
        r_bridge_width = self.closet.get_prompt("Right Bridge Shelf Width")       
        l_filler = self.closet.get_prompt("Left Side Wall Filler")
        r_filler = self.closet.get_prompt("Right Side Wall Filler")      
        ctop_oh_front = self.closet.get_prompt("Countertop Overhang Front")       
        ctop_oh_left = self.closet.get_prompt("Countertop Overhang Left")   
        ctop_oh_right = self.closet.get_prompt("Countertop Overhang Right")   
        lfe = self.closet.get_prompt("Left Finished End")   
        rfe = self.closet.get_prompt("Right Finished End")   
        extend_panels_to_ctop = self.closet.get_prompt("Extend Panels to Countertop")   
        extend_panel_amount = self.closet.get_prompt("Extend Panel Amount") 
        
        row = layout.row()    
        row.label(text="Finished Ends:")
        row.prop(lfe,'checkbox_value',text="Left")    
        row.prop(rfe,'checkbox_value',text="Right")    

        row = layout.row()    
        row.label(text="Top Filler Panels:")
        col_l = row.column()
        col_l.prop(l_bridge,'checkbox_value',text="Left")
        if l_bridge.get_value():
            col_l.prop(l_bridge_width,'distance_value',text="Width")
        col_r = row.column()
        col_r.prop(r_bridge,'checkbox_value',text="Right")
        if r_bridge.get_value():
            col_r.prop(r_bridge_width,'distance_value',text="Width")

        row = layout.row()    
        row.label(text="Toe Kick:")
        if hb_props.use_fixed_closet_heights:
            row.prop(self,'kick_height',text="") 
        else:
            row.prop(kick_height,'distance_value',text="Height")    
        row.prop(kick_setback,'distance_value',text="Setback")    

        row = layout.row()   
        row.label(text="Fillers:") 
        row.prop(l_filler,'distance_value',text="Left Width")
        row.prop(r_filler,'distance_value',text="Right Width")

        row = layout.row()   
        row.label(text="Panels to Countertop:") 
        row.prop(extend_panels_to_ctop,'checkbox_value',text="Extend")
        if extend_panels_to_ctop.checkbox_value:
            row.prop(extend_panel_amount,'distance_value',text="Distance")
        else:
            row.label(text="")

        if ctop_oh_front and ctop_oh_left and ctop_oh_right:
            row = layout.row()   
            row.label(text="Countertop Overhang:") 
            row.prop(ctop_oh_front,'distance_value',text="Front")
            row.prop(ctop_oh_left,'distance_value',text="Left")
            row.prop(ctop_oh_right,'distance_value',text="Right")

        row = layout.row()  
        row.label(text="Remove Bottom:")
        for i in range(1,9):
            remove_bottom = self.closet.get_prompt("Remove Bottom " + str(i))
            if remove_bottom:
                row.prop(remove_bottom,'checkbox_value',text=str(i))

        row = layout.row()  
        row.label(text="Double Panels:")
        for i in range(1,9):
            double_panel = self.closet.get_prompt("Double Panel " + str(i))
            if double_panel:
                row.prop(double_panel,'checkbox_value',text=str(i))

    def get_number_of_equal_widths(self):
        number_of_equal_widths = 0
        
        for i in range(1,9):
            width = self.closet.get_prompt("Opening " + str(i) + " Width")
            if width:
                number_of_equal_widths += 1 if width.equal else 0
            else:
                break
            
        return number_of_equal_widths

    def draw_closet_prompts(self,layout,context):
        unit_settings = context.scene.unit_settings
        hb_props = utils_cabinet.get_scene_props(context.scene)

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Opening:")
        row.label(text="",icon='BLANK1')
        row.label(text="Width:")
        row.label(text="Height:")
        row.label(text="Depth:")
        
        box = col.box()

        for i in range(1,9):
            width = self.closet.get_prompt("Opening " + str(i) + " Width")
            height = self.closet.get_prompt("Opening " + str(i) + " Height")
            depth = self.closet.get_prompt("Opening " + str(i) + " Depth")
            floor = self.closet.get_prompt("Opening " + str(i) + " Floor Mounted")
            if width:
                row = box.row()
                row.prop(floor,'checkbox_value',text=str(i) + ": " + "Floor" if floor.get_value() else str(i) + ": " + "Hanging",icon='TRIA_DOWN' if floor.get_value() else 'TRIA_UP')                
                if width.equal == False:
                    row.prop(width,'equal',text="")
                else:
                    if self.get_number_of_equal_widths() != 1:
                        row.prop(width,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')                
                
                if width.equal:
                    value = pc_unit.unit_to_string(unit_settings,width.distance_value)  
                    row.label(text=value)
                else:
                    row.prop(width,'distance_value',text="")
                
                if hb_props.use_fixed_closet_heights:
                    row.prop(self,'opening_' + str(i) + '_height',text="")
                else:
                    row.prop(height,'distance_value',text="")

                if self.is_base:
                    value = pc_unit.unit_to_string(unit_settings,depth.distance_value) 
                    row.label(text=value)
                else:
                    row.prop(depth,'distance_value',text="")

    def draw(self, context):
        layout = self.layout
        info_box = layout.box()
        
        # obj_props = home_builder_utils.get_object_props(self.closet.obj_bp)
        # scene_props = home_builder_utils.get_scene_props(context.scene)

        # mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        
        row = info_box.row(align=True)
        row.prop(self.closet.obj_bp,'name',text="Name")
        # row.separator()
        # row.menu('HOME_BUILDER_MT_change_product_material_group',text=mat_group.name,icon='COLOR')
        # row.operator('home_builder.update_product_material_group',text="",icon='FILE_REFRESH').object_name = self.closet.obj_bp.name

        self.draw_product_size(layout,context)

        prompt_box = layout.box()

        row = prompt_box.row(align=True)
        row.prop_enum(self, "product_tabs", 'MAIN') 
        row.prop_enum(self, "product_tabs", 'CONSTRUCTION') 
        row.prop_enum(self, "product_tabs", 'MACHINING')

        if self.product_tabs == 'MAIN':
            self.draw_closet_prompts(prompt_box,context)   
        
        if self.product_tabs == 'CONSTRUCTION':
            self.draw_construction_prompts(prompt_box,context)

        if self.product_tabs == 'MACHINING':
            pass
            # for carcass in reversed(self.cabinet.carcasses):
            #     if carcass.exterior:
            #         box = prompt_box.box()
            #         box.label(text=carcass.exterior.obj_bp.name)
            #         carcass.exterior.draw_prompts(box,context)

class hb_closet_starters_OT_closet_inside_corner_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_starters.closet_inside_corner_prompts"
    bl_label = "Closet Inside Corner Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)  

    set_height: bpy.props.EnumProperty(name="Set Height",
                                       items=const.PANEL_HEIGHTS,
                                       default = '2131',
                                       update = update_corner_closet_height)

    closet = None
    
    def check(self, context):
        self.closet.obj_x.location.x = self.width
        self.closet.obj_y.location.y = -self.depth             
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_INSIDE_CORNER_TAG)
        self.closet = types_closet_starters.Closet_Inside_Corner(bp)
        self.width = self.closet.obj_x.location.x
        self.depth = math.fabs(self.closet.obj_y.location.y)      

    def set_default_heights(self):
        for i in range(1,9):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height_prompt:
                opening_height = round(pc_unit.meter_to_millimeter(opening_height_prompt.get_value()),0)
                for index, height in enumerate(const.PANEL_HEIGHTS):
                    if not opening_height >= int(height[0]):
                        exec('self.opening_' + str(i) + '_height = const.PANEL_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                        break

    def draw_product_size(self,layout):
        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        row1.label(text='Width:')
        row1.prop(self,'width',text="")
        row1.prop(self.closet.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        row1.label(text='Height:')
        row1.prop(self,'set_height',text="")
        row1.prop(self.closet.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        row1.label(text='Depth:')
        row1.prop(self,'depth',text="")
        row1.prop(self.closet.obj_y,'hide_viewport',text="")
            
        col = row.column(align=True)
        col.label(text="Location X:")
        col.label(text="Location Y:")
        col.label(text="Location Z:")
        
        col = row.column(align=True)
        col.prop(self.closet.obj_bp,'location',text="")
        
        is_hanging = self.closet.get_prompt("Is Hanging")
        
        if is_hanging:
            row = box.row()
            # row.label(text="Is Hanging")
            row.prop(is_hanging,'checkbox_value',text="Is Hanging")
            # is_hanging.draw_prompt(row)
            if is_hanging.get_value():
                row.prop(self.closet.obj_z,'location',index=2,text="Hanging Height")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.closet.obj_bp,'rotation_euler',index=2,text="")  

    def draw_construction_prompts(self,layout):
        left_depth = self.closet.get_prompt("Left Depth")
        right_depth = self.closet.get_prompt("Right Depth")
        kick_height = self.closet.get_prompt("Closet Kick Height")
        kick_setback = self.closet.get_prompt("Closet Kick Setback")
        shelf_qty = self.closet.get_prompt("Shelf Quantity")
        back_width = self.closet.get_prompt("Back Width")
        flip_back_support_location = self.closet.get_prompt("Flip Back Support Location")

        box = layout.box()
        row = box.row()
        row.label(text="Left Depth")
        row.prop(left_depth,'distance_value',text="")
        row.label(text="Right Depth")
        row.prop(right_depth,'distance_value',text="")      

        row = box.row()
        row.label(text="Toe Kick")
        row.prop(kick_height,'distance_value',text="Height")
        row.prop(kick_setback,'distance_value',text="Setback")

        row = box.row()
        row.label(text="Shelf Quantity")
        row.prop(shelf_qty,'quantity_value',text="")

        row = box.row()
        row.label(text="Back Width")
        row.prop(back_width,'distance_value',text="")

        if flip_back_support_location:
            row.prop(flip_back_support_location,'checkbox_value',text="Flip")

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout)
        self.draw_construction_prompts(layout)


class hb_closet_inserts_OT_closet_door_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.closet_door_prompts"
    bl_label = "Closet Door Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Door")])

    door_opening_height: bpy.props.EnumProperty(name="Door Opening Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')
    
    insert = None
    calculators = []

    def check(self, context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            insert_height = self.insert.get_prompt("Door Height")
            if insert_height:
                insert_height.distance_value = pc_unit.inch(float(self.door_opening_height) / 25.4)

        door_swing = self.insert.get_prompt("Door Swing")
        if self.door_swing == 'LEFT':
            door_swing.set_value(0)
        if self.door_swing == 'RIGHT':
            door_swing.set_value(1)
        if self.door_swing == 'DOUBLE':
            door_swing.set_value(2)         
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            door_height = self.insert.get_prompt("Door Height")
            if door_height:
                value = round(door_height.distance_value * 1000,2)
                for index, height in enumerate(const.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.door_opening_height = const.OPENING_HEIGHTS[index - 1][0]
                        break
        door_swing = self.insert.get_prompt("Door Swing")
        if door_swing.get_value() == 0:
            self.door_swing = 'LEFT'
        if door_swing.get_value() == 1:
            self.door_swing = 'RIGHT'
        if door_swing.get_value() == 2:
            self.door_swing = 'DOUBLE' 

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_DOORS_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
              
        layout = self.layout
        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        open_door = self.insert.get_prompt("Open Door")  
        door_height = self.insert.get_prompt("Door Height") 
        turn_off_pulls = self.insert.get_prompt("Turn Off Pulls") 
        door_type = self.insert.get_prompt("Door Type")
        fill_opening = self.insert.get_prompt("Fill Opening")
        s_qty = self.insert.get_prompt("Shelf Quantity")

        box = layout.box()
        row = box.row()
        row.label(text="Door Swing")      
        row.prop(self,'door_swing',expand=True) 
        if door_height:         
            if fill_opening:
                row = box.row()
                row.label(text="Fill Opening")
                row.prop(fill_opening,'checkbox_value',text="")   

                if fill_opening.get_value() == False:
                    row = box.row()
                    if hb_props.use_fixed_closet_heights:  
                        row.label(text="Door Opening Height")      
                        row.prop(self,'door_opening_height',text="") 
                    else:
                        row.label(text="Door Opening Height")      
                        row.prop(door_height,'distance_value',text="")  

        row = box.row()
        row.label(text="Open Door")      
        row.prop(open_door,'percentage_value',text="")  

        box = layout.box()
        box.label(text="Front Half Overlays")
        row = box.row()
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 

        box = layout.box()
        box.label(text="Pulls")
        row = box.row()
        row.label(text="Turn Off Pulls")      
        row.prop(turn_off_pulls,'checkbox_value',text="")    
        if door_type.get_value() == "Base":
            vert_loc = self.insert.get_prompt("Base Pull Vertical Location")  
            row = box.row()
            row.label(text="Pull Location")               
            row.prop(vert_loc,'distance_value',text="")       
        if door_type.get_value() == "Tall":
            vert_loc = self.insert.get_prompt("Tall Pull Vertical Location")   
            row = box.row()
            row.label(text="Pull Location")               
            row.prop(vert_loc,'distance_value',text="")                  
        if door_type.get_value() == "Upper":
            vert_loc = self.insert.get_prompt("Upper Pull Vertical Location")         
            row = box.row()
            row.label(text="Pull Location")               
            row.prop(vert_loc,'distance_value',text="")  

        box = layout.box()
        row = box.row()
        row.label(text="Shelf Quantity")      
        row.prop(s_qty,'quantity_value',text="")     


class hb_closet_inserts_OT_closet_shelves_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.closet_shelves_prompts"
    bl_label = "Closet Shelves Prompts"

    insert = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_SHELVES_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        shelf_qty = self.insert.get_prompt("Shelf Quantity")
        layout.prop(shelf_qty,'quantity_value',text="Shelf Quantity")
        row = layout.row()
        props = row.operator('home_builder.show_hide_closet_opening',text="Show Opening")
        props.insert_obj_bp = self.insert.obj_bp.name
        props.hide = False
        props = row.operator('home_builder.show_hide_closet_opening',text="Hide Opening")
        props.insert_obj_bp = self.insert.obj_bp.name
        props.hide = True


class hb_closet_inserts_OT_hanging_rod_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.hanging_rod_prompts"
    bl_label = "Hanging Rod Prompts"

    top_opening_height: bpy.props.EnumProperty(name="Top Opening Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    insert = None

    def check(self, context):
        self.insert.obj_prompts.hide_viewport = False
        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            top_opening_height = self.insert.get_prompt("Top Opening Height")
            if top_opening_height:
                top_opening_height.distance_value = pc_unit.inch(float(self.top_opening_height) / 25.4)
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            top_opening_height = self.insert.get_prompt("Top Opening Height")
            if top_opening_height:
                value = round(top_opening_height.distance_value * 1000,2)
                for index, height in enumerate(const.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.top_opening_height = const.OPENING_HEIGHTS[index - 1][0]
                        break

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=230)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_HANGING_ROD)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        layout = self.layout
        loc_from_top = self.insert.get_prompt("Hanging Rod Location From Top")
        top_opening_height = self.insert.get_prompt("Top Opening Height")
        setback = self.insert.get_prompt("Hanging Rod Setback")
        if top_opening_height:
            if hb_props.use_fixed_closet_heights:
                row = layout.row()
                row.label(text="Top Opening Height")
                row.prop(self,'top_opening_height',text="") 
            else:
                layout.prop(top_opening_height,'distance_value',text="Top Opening Height")        
        if loc_from_top:
            layout.prop(loc_from_top,'distance_value',text="Rod Location From Top")
        if setback:
            layout.prop(setback,'distance_value',text="Rod Setback")


class hb_closet_inserts_OT_closet_shoe_shelf_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.closet_shoe_shelf_prompts"
    bl_label = "Closet Shoe Shelf Prompts"

    insert = None
    calculators = []

    def get_shoe_shelf_fences(self):
        shoe_fences = []
        for child in self.insert.obj_bp.children:
            for nchild in child.children:
                if 'IS_METAL_SHOE_SHELF_FENCE_BP' in nchild:
                    part = pc_types.Assembly(nchild)
                    hide = part.get_prompt("Hide")
                    if hide and hide.get_value():
                        continue                
                    shoe_fences.append(part)
        return shoe_fences

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_SLANTED_SHOE_SHELVES)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        shelf_qty = self.insert.get_prompt("Shelf Quantity")
        space_from_bottom = self.insert.get_prompt("Space From Bottom")
        dim_between_shelves = self.insert.get_prompt("Distance Between Shelves")
        
        box = layout.box()

        row = box.row()
        row.label(text="Shelf Quantity")
        row.prop(shelf_qty,'quantity_value',text="")

        row = box.row()
        row.label(text="Space From Bottom")
        row.prop(space_from_bottom,'distance_value',text="")

        row = box.row()
        row.label(text="Distance Between Shelves")
        row.prop(dim_between_shelves,'distance_value',text="")


class hb_closet_inserts_OT_closet_drawer_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.closet_drawer_prompts"
    bl_label = "Closet Drawer Prompts"

    drawer_qty: bpy.props.EnumProperty(name="Drawer Quantity",
                          items=[('1',"1","1 Drawer"),
                                 ('2',"2","2 Drawer"),
                                 ('3',"3","3 Drawer"),
                                 ('4',"4","4 Drawer"),
                                 ('5',"5","5 Drawer"),
                                 ('6',"6","6 Drawer"),
                                 ('7',"7","7 Drawer"),
                                 ('8',"8","8 Drawer")],
                          default='3')

    front_1_height: bpy.props.EnumProperty(name="Front 1 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')

    front_2_height: bpy.props.EnumProperty(name="Front 2 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')

    front_3_height: bpy.props.EnumProperty(name="Front 3 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')

    front_4_height: bpy.props.EnumProperty(name="Front 4 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')

    front_5_height: bpy.props.EnumProperty(name="Front 5 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')

    front_6_height: bpy.props.EnumProperty(name="Front 6 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')      

    front_7_height: bpy.props.EnumProperty(name="Front 7 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')

    front_8_height: bpy.props.EnumProperty(name="Front 8 Height",
                                    items=const.FRONT_HEIGHTS,
                                    default = '140.95')   

    insert = None
    calculators = []

    def check(self, context):
        self.update_front_height_size(context)
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def update_front_height_size(self,context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
        drawer_height = self.insert.get_prompt("Drawer Height")
        if drawer_height:             
            if hb_props.use_fixed_closet_heights:
                height = eval("float(self.front_1_height)/1000")
                drawer_height.set_value(height)
        else:
            drawer_qty = self.insert.get_prompt("Drawer Quantity")
            drawer_qty.set_value(int(self.drawer_qty))             
            if hb_props.use_fixed_closet_heights:
                for i in range(1,9):
                    drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                    if drawer_height:                        
                        height = eval("float(self.front_" + str(i) + "_height)/1000")
                        drawer_height.set_value(height)

    def set_default_front_size(self):
        drawer_height = self.insert.get_prompt("Drawer Height")
        if drawer_height:
            front_height = round(drawer_height.distance_value * 1000,2)
            for index, height in enumerate(const.FRONT_HEIGHTS):
                if not front_height >= float(height[0]):
                    exec("self.front_1_height = const.FRONT_HEIGHTS[index - 1][0]")
                    break                
        else:
            drawer_qty = self.insert.get_prompt("Drawer Quantity")
            self.drawer_qty = str(drawer_qty.get_value())               
            for i in range(1,9):
                drawer_height_prompt = self.insert.get_prompt("Drawer " + str(i) + " Height")
                if drawer_height_prompt:
                    front_height = round(drawer_height_prompt.distance_value * 1000,2)
                    for index, height in enumerate(const.FRONT_HEIGHTS):
                        if not front_height >= float(height[0]):
                            exec('self.front_' + str(i) + '_height = const.FRONT_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                            break

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_default_front_size()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_DRAWERS_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = utils_cabinet.get_scene_props(context.scene)
        layout = self.layout
        box = layout.box()
        open_drawer = self.insert.get_prompt("Open Drawer")
        drawer_qty = self.insert.get_prompt("Drawer Quantity")
        drawer_height = self.insert.get_prompt("Drawer Height")
        remove_top_shelf = self.insert.get_prompt("Remove Top Shelf")
        
        total_drawer_height = 0
        if drawer_height:
            row = box.row()
            row.label(text="Drawer Height")
            if hb_props.use_fixed_closet_heights:
                row.prop(self,'front_1_height',text="")
            else:
                row.prop(drawer_height,'distance_value',text="")
            total_drawer_height += drawer_height.get_value()
        if drawer_qty:
            row = box.row()
            row.label(text="Qty")            
            row.prop(self,'drawer_qty',expand=True)
            for i in range(1,9):
                if drawer_qty.get_value() > i - 1:
                    if hb_props.use_fixed_closet_heights:
                        drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                        row = box.row()
                        row.label(text="Drawer " + str(i) + " Height")                      
                        row.prop(self,'front_' + str(i) + '_height',text="")
                    else:
                        drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                        row = box.row()
                        row.label(text="Drawer " + str(i) + " Height")                      
                        row.prop(drawer_height,'distance_value',text="")
                    total_drawer_height += drawer_height.get_value()
            row = box.row()
            row.label(text="Open Drawer")
            row.prop(open_drawer,'percentage_value',text="")

        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        
        box = layout.box()
        box.label(text="Front Half Overlays")
        row = box.row()
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 

        box = layout.box()
        row = box.row()
        row.label(text="Remove Top Shelf")
        row.prop(remove_top_shelf,'checkbox_value',text="")
        
        box = layout.box()
        height = round(pc_unit.meter_to_inch(total_drawer_height),2)
        row = box.row()
        row.label(text="Total Drawer Height: ")
        row.label(text=str(height) + '"')


class hb_closet_inserts_OT_closet_cubby_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.closet_cubby_prompts"
    bl_label = "Closet Cubby Prompts"

    cubby_location: bpy.props.EnumProperty(name="Cubby Location",
                                           items=[('BOTTOM',"Bottom","Place on Bottom"),
                                                  ('TOP',"Top","Place on Top"),
                                                  ('FILL',"Fill","Fill Opening")])

    cubby_height: bpy.props.EnumProperty(name="Cubby Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')
    
    insert = None
    calculators = []

    def check(self, context):
        self.insert.obj_prompts.hide_viewport = False
        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            cubby_height = self.insert.get_prompt("Cubby Height")
            if cubby_height:
                cubby_height.distance_value = pc_unit.inch(float(self.cubby_height) / 25.4)  

        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if self.cubby_location == 'BOTTOM':
            cubby_placement.set_value(0)
        if self.cubby_location == 'TOP':
            cubby_placement.set_value(1)
        if self.cubby_location == 'FILL':
            cubby_placement.set_value(2)         
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            cubby_height = self.insert.get_prompt("Cubby Height")
            if cubby_height:
                value = round(cubby_height.distance_value * 1000,2)
                for index, height in enumerate(const.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.cubby_height = const.OPENING_HEIGHTS[index - 1][0]
                        break

        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if cubby_placement.get_value() == 0:
            self.cubby_location = 'BOTTOM'
        if cubby_placement.get_value() == 1:
            self.cubby_location = 'TOP'
        if cubby_placement.get_value() == 2:
            self.cubby_location = 'FILL'  

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_CUBBIES_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        h_qty = self.insert.get_prompt("Horizontal Quantity")
        v_qty = self.insert.get_prompt("Vertical Quantity")
        c_height = self.insert.get_prompt("Cubby Height")
        c_setback = self.insert.get_prompt("Cubby Setback")
        row = layout.row()
        row.label(text="Location")
        row.prop(self,'cubby_location',expand=True)
        if self.cubby_location != 'FILL':
            hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
            if hb_props.use_fixed_closet_heights:  
                row = layout.row()
                row.label(text="Cubby Height")        
                row.prop(self,'cubby_height',text="")
            else:
                row = layout.row()
                row.label(text="Cubby Height")        
                row.prop(c_height,'distance_value',text="")
        row = layout.row()
        row.label(text="Shelf Quantity")           
        row.prop(h_qty,'quantity_value',text="")
        row = layout.row()
        row.label(text="Division Quantity")           
        row.prop(v_qty,'quantity_value',text="")        
        row = layout.row()
        row.label(text="Cubby Setback")           
        row.prop(c_setback,'distance_value',text="")


class hb_closet_inserts_OT_closet_wire_baskets_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.closet_wire_baskets_prompts"
    bl_label = "Closet Wire Baskets Prompts"

    insert = None

    def check(self, context):     
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_WIRE_BASKETS_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        qty = self.insert.get_prompt("Wire Basket Quantity")
        spacing = self.insert.get_prompt("Vertical Spacing")

        box = layout.box()
        row = box.row()
        row.label(text="Wire Basket Quantity")
        row.prop(qty,'quantity_value',text="")

        for i in range(1,7):
            if qty.get_value() > i - 1:
                height = self.insert.get_prompt("Wire Basket " + str(i) + " Height")
                row = box.row()
                row.label(text="Height " + str(i))                
                row.prop(height,'distance_value',text="")

        box = layout.box()
        row = box.row()
        row.label(text="Vertical Spacing")
        row.prop(spacing,'distance_value',text="")


class hb_closet_parts_OT_closet_single_adj_shelf_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_parts.closet_single_adj_shelf_prompts"
    bl_label = "Closet Single Adjustable Shelf Prompts"

    insert = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_SINGLE_ADJ_SHELF_TAG)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        layout.prop(self.insert.obj_bp,'location',index=2,text="Shelf Location")


class hb_closet_parts_OT_closet_cleat_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_parts.closet_cleat_prompts"
    bl_label = "Closet Cleat Prompts"

    cleat_width: bpy.props.FloatProperty(name="Width",min=pc_unit.inch(1),unit='LENGTH',precision=4)

    part = None
    calculators = []

    def check(self, context):
        if self.part.obj_y.location.y > 0:
            self.part.obj_y.location.y = self.cleat_width
        else:
            self.part.obj_y.location.y = -self.cleat_width
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_CLEAT_TAG)
        self.part = pc_types.Assembly(bp)
        self.cleat_width = math.fabs(self.part.obj_y.location.y)

    def draw(self, context):
        layout = self.layout
        inset = self.part.get_prompt("Cleat Inset")
        width = self.part.get_prompt("Cleat Width")
        row = layout.row()
        row.label(text="Cleat Inset")
        row.prop(inset,'distance_value',text="")
        row = layout.row()
        row.label(text="Cleat Width")
        row.prop(self,'cleat_width',text="")


class hb_closet_parts_OT_closet_back_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_parts.closet_back_prompts"
    bl_label = "Closet Back Prompts"

    part = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_BACK_TAG)
        self.part = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        inset = self.part.get_prompt("Back Inset")
        row = layout.row()
        row.label(text="Back Inset")
        row.prop(inset,'distance_value',text="")


class hb_closet_parts_OT_closet_single_fixed_shelf_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_parts.closet_single_fixed_shelf_prompts"
    bl_label = "Fixed Shelf Prompts"

    set_height_location: bpy.props.EnumProperty(name="Set Height Location",
                                           items=[('TOP',"Top","Set Top Height"),
                                                  ('Bottom',"Bottom","Set Bottom Height")])

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')
    
    opening_2_height: bpy.props.EnumProperty(name="Opening 2 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_3_height: bpy.props.EnumProperty(name="Opening 3 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_4_height: bpy.props.EnumProperty(name="Opening 4 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_5_height: bpy.props.EnumProperty(name="Opening 5 Height",
                                    items=const.OPENING_HEIGHTS,
                                    default = '716.95')

    insert = None
    calculators = []

    def check(self, context): 
        opening_top = self.insert.get_prompt("Opening 1 Height")
        opening_bottom = self.insert.get_prompt("Opening 2 Height")
        if self.set_height_location == 'TOP':
            opening_top.equal = False
            opening_bottom.equal = True
        else:
            opening_top.equal = True
            opening_bottom.equal = False  

        hb_props = utils_cabinet.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            for i in range(1,6):
                opening = self.insert.get_prompt("Opening " + str(i) + " Height")
                if opening:
                    height = eval("float(self.opening_" + str(i) + "_height)/1000")
                    opening.set_value(height)        
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = utils_cabinet.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            for i in range(1,6):
                opening = self.insert.get_prompt("Opening " + str(i) + " Height")
                if opening:
                    value = round(opening.distance_value * 1000,2)
                    for index, height in enumerate(const.OPENING_HEIGHTS):
                        if not value >= float(height[0]):
                            exec("self.opening_" + str(i) + "_height = const.OPENING_HEIGHTS[index - 1][0]")
                            break

    def invoke(self,context,event):
        self.get_assemblies(context) 
        self.get_calculators(self.insert.obj_bp)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.VERTICAL_SPLITTER_TAG)
        self.insert = pc_types.Assembly(bp)

    def get_number_of_equal_openings(self,name="Height"):
        number_of_equal_openings = 0
        
        for i in range(1,9):
            size = self.insert.get_prompt("Opening " + str(i) + " " + name)
            if size:
                number_of_equal_openings += 1 if size.equal else 0
            else:
                break
            
        return number_of_equal_openings

    def draw_prompts(self,layout,name="Height"):
        unit_settings = bpy.context.scene.unit_settings
        row = layout.row()
        row.prop(self,'set_height_location',expand=True)
        opening_top = self.insert.get_prompt("Opening 1 Height")
        opening_bottom = self.insert.get_prompt("Opening 2 Height")
        if self.set_height_location == 'TOP':
            row = layout.row()
            row.label(text="Top Opening Height:")
            row.prop(self,'opening_1_height',text="")
            row = layout.row()
            row.label(text="Bottom Opening Height:")
            row.label(text=pc_unit.unit_to_string(unit_settings,opening_bottom.distance_value))                  
        else:
            row = layout.row()
            row.label(text="Top Opening Height:")
            row.label(text=pc_unit.unit_to_string(unit_settings,opening_top.distance_value))     
            row = layout.row()
            row.label(text="Bottom Opening Height:")
            row.prop(self,'opening_2_height',text="")               

    def draw(self, context):
        layout = self.layout
        unit_settings = bpy.context.scene.unit_settings
        row = layout.row()
        row.prop(self,'set_height_location',expand=True)
        opening_top = self.insert.get_prompt("Opening 1 Height")
        opening_bottom = self.insert.get_prompt("Opening 2 Height")
        if self.set_height_location == 'TOP':
            row = layout.row()
            row.label(text="Top Opening Height:")
            row.prop(self,'opening_1_height',text="")
            row = layout.row()
            row.label(text="Bottom Opening Height:")
            row.label(text=pc_unit.unit_to_string(unit_settings,opening_bottom.distance_value))                  
        else:
            row = layout.row()
            row.label(text="Top Opening Height:")
            row.label(text=pc_unit.unit_to_string(unit_settings,opening_top.distance_value))     
            row = layout.row()
            row.label(text="Bottom Opening Height:")
            row.prop(self,'opening_2_height',text="")           


class hb_closet_inserts_OT_division_prompts(bpy.types.Operator):
    bl_idname = "hb_closet_inserts.division_prompts"
    bl_label = "Division Prompts"

    insert = None
    calculators = []

    def check(self, context):       
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context) 
        self.get_calculators(self.insert.obj_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.HORIZONTAL_SPLITTER_TAG)
        self.insert = pc_types.Assembly(bp)

    def get_number_of_equal_openings(self):
        number_of_equal_openings = 0
        
        for i in range(1,9):
            size = self.insert.get_prompt("Opening " + str(i) + " Width")
            if size:
                number_of_equal_openings += 1 if size.equal else 0
            else:
                break
            
        return number_of_equal_openings

    def draw(self, context):
        layout = self.layout
        unit_settings = bpy.context.scene.unit_settings
        for i in range(1,10):
            opening = self.insert.get_prompt("Opening " + str(i) + " Width")
            if opening:
                row = layout.row()
                if opening.equal == False:
                    row.prop(opening,'equal',text="")
                else:
                    if self.get_number_of_equal_openings() != 1:
                        row.prop(opening,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')                
                row.label(text="Opening " + str(i) + " Width:")
                if opening.equal:
                    value = pc_unit.unit_to_string(unit_settings,opening.distance_value)
                    row.label(text=value)
                else:
                    row.prop(opening,'distance_value',text="")


classes = (
    hb_sample_cabinets_OT_cabinet_prompts,
    hb_closet_starters_OT_closet_prompts,
    hb_closet_starters_OT_closet_inside_corner_prompts,
    hb_closet_inserts_OT_closet_door_prompts,
    hb_closet_inserts_OT_closet_shelves_prompts,
    hb_closet_inserts_OT_hanging_rod_prompts,
    hb_closet_inserts_OT_closet_shoe_shelf_prompts,
    hb_closet_inserts_OT_closet_cubby_prompts,
    hb_closet_inserts_OT_closet_drawer_prompts,
    hb_closet_inserts_OT_closet_wire_baskets_prompts,
    hb_closet_parts_OT_closet_single_adj_shelf_prompts,
    hb_closet_parts_OT_closet_cleat_prompts,
    hb_closet_parts_OT_closet_back_prompts,
    hb_closet_parts_OT_closet_single_fixed_shelf_prompts,
    hb_closet_inserts_OT_division_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    