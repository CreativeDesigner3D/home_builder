import bpy
import math
from pc_lib import pc_utils, pc_types, pc_unit
from . import material_pointers_cabinet
from . import types_cabinet
from . import types_appliances
from . import types_cabinet_starters
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

def update_range(self,context):
    self.range_changed = True

def update_dishwasher(self,context):
    self.dishwasher_changed = True

def update_refrigerator(self,context):
    self.refrigerator_changed = True

def update_built_in_oven(self,context):
    self.built_in_oven_changed = True

def update_built_in_microwave(self,context):
    self.built_in_microwave_changed = True

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



class Appliance_Prompts(bpy.types.Operator):

    anchor_x: bpy.props.EnumProperty(name="Anchor X",
                                     items=[('LEFT',"Left","Left"),
                                            ('CENTER',"Center","Center"),
                                            ('RIGHT',"Right","Bump Right")])
    
    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    x_loc_left: bpy.props.FloatProperty(name="X Location Left",unit='LENGTH',precision=4)
    x_loc_center: bpy.props.FloatProperty(name="X Location Center",unit='LENGTH',precision=4)
    x_loc_right: bpy.props.FloatProperty(name="X Location Right",unit='LENGTH',precision=4)    
    start_width: bpy.props.FloatProperty(name="Start Width",unit='LENGTH',precision=4)

    wall = None
    first_connected_cabinet = None
    first_connected_cabinet_x = 0

    def set_default_properties(self,assembly):
        self.depth = math.fabs(assembly.obj_y.location.y)
        self.height = math.fabs(assembly.obj_z.location.z)
        self.width = math.fabs(assembly.obj_x.location.x)           
        self.x_loc_left = assembly.obj_bp.location.x
        self.x_loc_center = assembly.obj_bp.location.x + (assembly.obj_x.location.x/2)
        if self.wall:
            self.x_loc_right = self.wall.obj_x.location.x - (assembly.obj_bp.location.x + assembly.obj_x.location.x)
        else:
            self.x_loc_right = assembly.obj_bp.location.x  
        self.start_width = assembly.obj_x.location.x
        first_cab = self.get_first_connected_cabinet(assembly.obj_bp)
        if first_cab:
            self.first_connected_cabinet_x = first_cab.location.x

    def get_first_connected_cabinet(self,obj_bp):
        if len(obj_bp.constraints):
            for con in obj_bp.constraints:
                if con.type == 'COPY_LOCATION':
                    target = con.target
                    cabinet_bp = target.parent
                    return self.get_first_connected_cabinet(cabinet_bp)
        else:
            return obj_bp
        
    def update_product_size(self,assembly):
        assembly.obj_x.location.x = self.width
        assembly.obj_y.location.y = -self.depth
        assembly.obj_z.location.z = self.height
        if self.wall:
            if self.anchor_x == 'LEFT':
                assembly.obj_bp.location.x = self.x_loc_left
            if self.anchor_x == 'CENTER':
                assembly.obj_bp.location.x = self.x_loc_center - (self.width/2)
            if self.anchor_x == 'RIGHT':
                if self.wall:
                    assembly.obj_bp.location.x = self.wall.obj_x.location.x - (self.x_loc_right + self.width)
                else:
                    assembly.obj_bp.location.x = self.x_loc_right

            cab_bp = self.get_first_connected_cabinet(assembly.obj_bp)
            if cab_bp and cab_bp.name != assembly.obj_bp.name:
                if self.anchor_x == 'RIGHT':
                    cab_bp.location.x = self.first_connected_cabinet_x - (self.width - self.start_width)
                if self.anchor_x == 'CENTER':
                    cab_bp.location.x = self.first_connected_cabinet_x - (self.width - self.start_width)/2

    def draw_product_size(self,assembly,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(assembly.obj_x) or assembly.obj_x.lock_location[0]:
            x = math.fabs(assembly.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(assembly.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(assembly.obj_z) or assembly.obj_z.lock_location[2]:
            z = math.fabs(assembly.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(assembly.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(assembly.obj_y) or assembly.obj_y.lock_location[1]:
            y = math.fabs(assembly.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(assembly.obj_y,'hide_viewport',text="")
            
        if len(assembly.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_cabinet_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = assembly.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")

            if self.wall:
                col = row.column(align=True) 
                if self.anchor_x == 'LEFT':
                    col.prop(self,'x_loc_left',text='Left')
                if self.anchor_x == 'CENTER':
                    col.prop(self,'x_loc_center',text='Center')
                if self.anchor_x == 'RIGHT':
                    col.prop(self,'x_loc_right',text='Right')
                col.prop(assembly.obj_bp,'location',index=1,text="")
                col.prop(assembly.obj_bp,'location',index=2,text="")
            else:
                col = row.column(align=True)    
                col.prop(assembly.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text="X Anchor")
        row.prop(self,'anchor_x',expand=True)

        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(assembly.obj_bp,'rotation_euler',index=2,text="") 


class hb_sample_cabinets_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.cabinet_prompts"
    bl_label = "Cabinet Prompts"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)
    start_width: bpy.props.FloatProperty(name="Start Width",unit='LENGTH',precision=4)

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

    anchor_z: bpy.props.EnumProperty(name="Anchor Z",
                                     items=[('BOTTOM',"Bottom","Bottom"),
                                            ('TOP',"Top","Top")])
    
    anchor_x: bpy.props.EnumProperty(name="Anchor X",
                                     items=[('LEFT',"Left","Left"),
                                            ('CENTER',"Center","Center"),
                                            ('RIGHT',"Right","Bump Right")])
    
    x_loc_left: bpy.props.FloatProperty(name="X Location Left",unit='LENGTH',precision=4)
    x_loc_center: bpy.props.FloatProperty(name="X Location Center",unit='LENGTH',precision=4)
    x_loc_right: bpy.props.FloatProperty(name="X Location Right",unit='LENGTH',precision=4)

    z_loc_top: bpy.props.FloatProperty(name="Z Location Top",unit='LENGTH',precision=4)
    z_loc_bottom: bpy.props.FloatProperty(name="Z Location Bottom",unit='LENGTH',precision=4)

    default_width = 0
    cabinet = None
    first_connected_cabinet = None
    first_connected_cabinet_x = 0
    wall = None
    calculators = []

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
        self.calculators = []

    def get_first_connected_cabinet(self,obj_bp):
        if len(obj_bp.constraints):
            for con in obj_bp.constraints:
                if con.type == 'COPY_LOCATION':
                    target = con.target
                    cabinet_bp = target.parent
                    return self.get_first_connected_cabinet(cabinet_bp)
        else:
            return obj_bp

    def update_product_size(self):
        self.cabinet.obj_x.location.x = self.width
        self.cabinet.obj_y.location.y = -self.depth
        self.cabinet.obj_z.location.z = self.height
        if self.wall:
            if self.anchor_x == 'LEFT':
                self.cabinet.obj_bp.location.x = self.x_loc_left
            if self.anchor_x == 'CENTER':
                self.cabinet.obj_bp.location.x = self.x_loc_center - (self.width/2)
            if self.anchor_x == 'RIGHT':
                if self.wall:
                    self.cabinet.obj_bp.location.x = self.wall.obj_x.location.x - (self.x_loc_right + self.width)
                else:
                    self.cabinet.obj_bp.location.x = self.x_loc_right

            if self.anchor_z == 'TOP':
                self.cabinet.obj_bp.location.z = self.z_loc_top - self.height
            if self.anchor_z == 'BOTTOM':
                self.cabinet.obj_bp.location.z = self.z_loc_bottom
            
            cab_bp = self.get_first_connected_cabinet(self.cabinet.obj_bp)
            if cab_bp and cab_bp.name != self.cabinet.obj_bp.name:
                if self.anchor_x == 'RIGHT':
                    cab_bp.location.x = self.first_connected_cabinet_x - (self.width - self.start_width)
                if self.anchor_x == 'CENTER':
                    cab_bp.location.x = self.first_connected_cabinet_x - (self.width - self.start_width)/2
        
    def update_materials(self,context):
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")

            if carcass.design_carcass:
                material_pointers_cabinet.update_design_carcass_pointers(carcass.design_carcass,
                                                                        left_finished_end.get_value(),
                                                                        right_finished_end.get_value(),
                                                                        finished_back.get_value(),
                                                                        finished_top.get_value(),
                                                                        finished_bottom.get_value())
            if carcass.design_base_assembly:                                                     
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

    def update_drawer_qty(self,context):
        for carcass in self.cabinet.carcasses:
            if carcass.exterior:
                drawer_qty_prompt = carcass.exterior.get_prompt("Drawer Quantity")
                calculator = carcass.exterior.get_calculator("Front Height Calculator")
                if calculator and drawer_qty_prompt:
                    for i in range(1,9):
                        dfh = calculator.get_calculator_prompt("Drawer Front " + str(i) + " Height")
                        if i <= drawer_qty_prompt.get_value():
                            dfh.include = True
                        else:
                            dfh.include = False
                    # calculator.calculate()

    def check(self, context):
        self.update_product_size()
        self.update_fillers(context)
        self.update_sink(context)
        self.update_range_hood(context)
        self.update_cooktop(context)
        self.update_faucet(context)        
        self.update_materials(context)
        self.update_drawer_qty(context)
        self.cabinet.update_range_hood_location()
        for calculator in self.calculators:
            calculator.calculate()
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
        self.start_width = math.fabs(self.cabinet.obj_x.location.x)
        self.x_loc_left = self.cabinet.obj_bp.location.x
        self.x_loc_center = self.cabinet.obj_bp.location.x + (self.cabinet.obj_x.location.x/2)
        if self.wall:
            self.x_loc_right = self.wall.obj_x.location.x - (self.cabinet.obj_bp.location.x + self.cabinet.obj_x.location.x)
        else:
            self.x_loc_right = self.cabinet.obj_bp.location.x
        self.z_loc_bottom = self.cabinet.obj_bp.location.z
        self.z_loc_top = self.cabinet.obj_bp.location.z + self.cabinet.obj_z.location.z
        self.default_width = self.cabinet.obj_x.location.x
        first_cab = self.get_first_connected_cabinet(self.cabinet.obj_bp)
        if first_cab:
            self.first_connected_cabinet_x = first_cab.location.x
        # if len(self.cabinet.obj_bp.constraints) > 0:
        #     self.anchor_x = 'LEFT'
        self.get_calculators(self.cabinet.obj_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CABINET_TAG)
        self.cabinet = types_cabinet.Cabinet(bp)

        if self.cabinet.obj_bp.parent and 'IS_WALL_BP' in self.cabinet.obj_bp.parent:
            self.wall = pc_types.Assembly(self.cabinet.obj_bp.parent)
        else:
            self.wall = None

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
            col.operator('home_builder.disconnect_cabinet_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.cabinet.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
            
            col = row.column(align=True)
            if self.wall:
                if self.anchor_x == 'LEFT':
                    col.prop(self,'x_loc_left',text="Left")
                if self.anchor_x == 'CENTER':
                    col.prop(self,'x_loc_center',text="Center")
                if self.anchor_x == 'RIGHT':                     
                    col.prop(self,'x_loc_right',text="Right")
                col.prop(self.cabinet.obj_bp,'location',index=1,text="")
                if self.anchor_z == 'TOP':
                    col.prop(self,'z_loc_top',text="Top")
                if self.anchor_z == 'BOTTOM':
                    col.prop(self,'z_loc_bottom',text="Bottom")                
            else:
                col.prop(self.cabinet.obj_bp,'location',text="")

        if self.wall:
            row = box.row()
            row.label(text='Anchor X:')
            row.prop(self,'anchor_x',expand=True)
            row.label(text='Anchor Z:')
            row.prop(self,'anchor_z',expand=True)

        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.cabinet.obj_bp,'rotation_euler',index=2,text="")  

        row = box.row()
        row.label(text='Height from Floor:')
        row.prop(self.cabinet.obj_bp,'location',index=2,text="")                  

    def draw_carcass_prompts(self,layout,context):
        for carcass in self.cabinet.carcasses:
            is_exposed_interior = carcass.get_prompt("Is Exposed Interior")
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
                row.prop(is_exposed_interior,'checkbox_value',text="Exposed Interior")
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


class hb_sample_cabinets_OT_range_prompts(Appliance_Prompts):
    bl_idname = "hb_sample_cabinets.range_prompts"
    bl_label = "Range Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    add_range_hood: bpy.props.BoolProperty(name="Add Range Hood",default=False)
    range_changed: bpy.props.BoolProperty(name="Range Changed",default=False)
    range_hood_changed: bpy.props.BoolProperty(name="Range Changed",default=False)

    range_category: bpy.props.EnumProperty(name="Range Category",
        items=enum_cabinets.enum_range_categories,
        update=enum_cabinets.update_range_category)
    range_name: bpy.props.EnumProperty(name="Range Name",
        items=enum_cabinets.enum_range_names,
        update=update_range)

    range_hood_category: bpy.props.EnumProperty(name="Range Hood Category",
        items=enum_cabinets.enum_range_hood_categories,
        update=enum_cabinets.update_range_hood_category)
    range_hood_name: bpy.props.EnumProperty(name="Range Hood Name",
        items=enum_cabinets.enum_range_hood_names,
        update=update_range_hood)

    product = None

    def reset_variables(self,context):
        self.product = None
        enum_cabinets.update_range_category(self,context)
        enum_cabinets.update_range_hood_category(self,context)

    def check(self, context):
        add_range_hood = self.product.get_prompt("Add Range Hood")
        add_range_hood.set_value(self.add_range_hood)        
        self.update_product_size(self.product)
        self.update_range(context)
        self.update_range_hood(context)
        self.product.update_range_hood_location()
        self.product.update_range_hood_location()
        return True

    def update_range(self,context):
        if self.range_changed:
            self.range_changed = False

            if self.product.range_appliance:
                pc_utils.delete_object_and_children(self.product.range_appliance.obj_bp)                

            self.product.add_range(self.range_category,self.range_name)
            self.width = self.product.range_appliance.obj_x.location.x
            self.depth = math.fabs(self.product.range_appliance.obj_y.location.y)
            self.height = self.product.range_appliance.obj_z.location.z
            context.view_layer.objects.active = self.product.obj_bp
            self.get_assemblies(context)

    def update_range_hood(self,context):
        if self.range_hood_changed:
            self.range_hood_changed = False
            add_range_hood = self.product.get_prompt("Add Range Hood")
            add_range_hood.set_value(self.add_range_hood)
            if self.product.range_hood_appliance:
                pc_utils.delete_object_and_children(self.product.range_hood_appliance.obj_bp)   

            if self.add_range_hood:
                self.product.add_range_hood(self.range_hood_category,self.range_hood_name)
            context.view_layer.objects.active = self.product.obj_bp
            self.get_assemblies(context)

    def execute(self, context):
        add_range_hood = self.product.get_prompt("Add Range Hood")
        if add_range_hood:
            if self.product.range_hood_appliance and not add_range_hood.get_value():
                pc_utils.delete_object_and_children(self.product.range_hood_appliance.obj_bp)          
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.APPLIANCE_TAG)
        self.product = types_appliances.Range(bp)

        if self.product.obj_bp.parent and 'IS_WALL_BP' in self.product.obj_bp.parent:
            self.wall = pc_types.Assembly(self.product.obj_bp.parent)
        else:
            self.wall = None

    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
        add_range_hood = self.product.get_prompt("Add Range Hood")
        self.add_range_hood = add_range_hood.get_value()     
        self.set_default_properties(self.product)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw_range_prompts(self,layout,context):
        layout.label(text="")
        box = layout.box()
        box.prop(self,'range_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"range_name",show_labels=True)  

    def draw_range_hood_prompts(self,layout,context):
        layout.prop(self,'add_range_hood',text="Add Range Hood")
        
        if not self.add_range_hood:
            return False
        else:
            box = layout.box()
            box.prop(self,'range_hood_category',text="",icon='FILE_FOLDER')  
            box.template_icon_view(self,"range_hood_name",show_labels=True)  

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        split = layout.split()
        self.draw_range_prompts(split.column(),context)
        self.draw_range_hood_prompts(split.column(),context)


class hb_sample_cabinets_OT_dishwasher_prompts(Appliance_Prompts):
    bl_idname = "hb_sample_cabinets.dishwasher_prompts"
    bl_label = "Dishwasher Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    dishwasher_changed: bpy.props.BoolProperty(name="Range Changed",default=False)

    dishwasher_category: bpy.props.EnumProperty(name="Dishwasher Category",
        items=enum_cabinets.enum_dishwasher_categories,
        update=enum_cabinets.update_dishwasher_category)
    dishwasher_name: bpy.props.EnumProperty(name="Dishwasher Name",
        items=enum_cabinets.enum_dishwasher_names,
        update=update_dishwasher)

    product = None

    def reset_variables(self,context):
        self.product = None
        enum_cabinets.update_dishwasher_category(self,context)

    def check(self, context):
        self.update_product_size(self.product)
        self.update_dishwasher(context)
        return True

    def update_dishwasher(self,context):
        if self.dishwasher_changed:
            self.dishwasher_changed = False

            if self.product:
                pc_utils.delete_object_and_children(self.product.dishwasher.obj_bp)                

            self.product.add_dishwasher(self.dishwasher_category,self.dishwasher_name)
            self.width = self.product.obj_x.location.x
            self.depth = math.fabs(self.product.obj_y.location.y)
            self.height = self.product.obj_z.location.z
            context.view_layer.objects.active = self.product.obj_bp
            pc_utils.hide_empties(self.product.obj_bp)
            self.get_assemblies(context)

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.APPLIANCE_TAG)
        self.product = types_appliances.Dishwasher(bp)

        if self.product.obj_bp.parent and 'IS_WALL_BP' in self.product.obj_bp.parent:
            self.wall = pc_types.Assembly(self.product.obj_bp.parent)
        else:
            self.wall = None

    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
        self.set_default_properties(self.product)      
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw_dishwasher_prompts(self,layout,context):
        box = layout.box()
        box.prop(self,'dishwasher_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"dishwasher_name",show_labels=True)  

    def draw_countertop_prompts(self,layout,context):
        ctop_front = self.product.get_prompt("Countertop Overhang Front")
        ctop_back = self.product.get_prompt("Countertop Overhang Back")
        ctop_left = self.product.get_prompt("Countertop Overhang Left")
        ctop_right = self.product.get_prompt("Countertop Overhang Right")
        ctop_left = self.product.get_prompt("Countertop Overhang Left")   

        col = layout.column(align=True)
        box = col.box()      
   
        # if left_adjustment_width and right_adjustment_width:
        #     row = box.row()
        #     row.label(text="Filler Amount:")
        #     row.prop(left_adjustment_width,'distance_value',text="Left")
        #     row.prop(right_adjustment_width,'distance_value',text="Right")

        if ctop_front and ctop_back and ctop_left and ctop_right:
            row = box.row()
            row.label(text="Countertop Overhang:")     
            row = box.row()  
            row.prop(ctop_front,'distance_value',text="Front")      
            row.prop(ctop_back,'distance_value',text="Rear")  
            row.prop(ctop_left,'distance_value',text="Left")  
            row.prop(ctop_right,'distance_value',text="Right")            
    
    def draw_filler_prompts(self,layout,context):
        left_filler_amount = self.product.get_prompt("Left Filler Amount")
        right_filler_amount = self.product.get_prompt("Right Filler Amount")

        if left_filler_amount and right_filler_amount:
            box = layout.box()
            row = box.row()
            row.label(text="Fillers")
            row.prop(left_filler_amount,'distance_value',text="Left")
            row.prop(right_filler_amount,'distance_value',text="Right")

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        self.draw_filler_prompts(layout,context)
        self.draw_countertop_prompts(layout,context)
        self.draw_dishwasher_prompts(layout,context)


class hb_sample_cabinets_OT_built_in_oven_prompts(Appliance_Prompts):
    bl_idname = "hb_sample_cabinets.built_in_oven_prompts"
    bl_label = "Built In Oven Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    built_in_oven_changed: bpy.props.BoolProperty(name="Built In Oven Changed",default=False)

    built_in_oven_category: bpy.props.EnumProperty(name="Built In Oven Category",
        items=enum_cabinets.enum_built_in_oven_categories,
        update=enum_cabinets.update_built_in_oven_category)
    built_in_oven_name: bpy.props.EnumProperty(name="Built In Oven Name",
        items=enum_cabinets.enum_built_in_oven_names,
        update=update_built_in_oven)

    product = None

    def reset_variables(self,context):
        self.product = None
        # enum_cabinets.update_refrigerator_category(self,context)

    def check(self, context):
        # self.update_product_size(self.product)
        # self.update_dishwasher(context)
        return True

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
        # self.set_default_properties(self.product)      
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=425)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.APPLIANCE_TAG)
        self.product = types_appliances.Built_In_Oven(bp)

    def draw(self, context):
        unit_system = context.scene.unit_settings.system

        layout = self.layout

        remove_filler = self.product.get_prompt("Remove Filler")
        lo = self.product.get_prompt("Appliance Left Offset")
        ro = self.product.get_prompt("Appliance Right Offset")
        to = self.product.get_prompt("Appliance Top Offset")
        bo = self.product.get_prompt("Appliance Bottom Offset")

        box = layout.box()
        split = box.split()
        col = split.column(align=True)
        col.label(text="Dimensions")
        if pc_utils.object_has_driver(self.product.obj_x):
            x = self.product.obj_x.location.x
            col.label(text="Width: " + str(bpy.utils.units.to_string(unit_system,'LENGTH',x)))
        else:
            col.prop(self.product.obj_x,'location',index=0,text="Width")

        if pc_utils.object_has_driver(self.product.obj_z):
            z = self.product.obj_z.location.z
            col.label(text="Height: " + str(bpy.utils.units.to_string(unit_system,'LENGTH',z)))
        else:
            col.prop(self.product.obj_z,'location',index=2,text="Height")

        if pc_utils.object_has_driver(self.product.obj_x):
            y = self.product.obj_y.location.y
            col.label(text="Depth: " + str(bpy.utils.units.to_string(unit_system,'LENGTH',y)))
        else:
            col.prop(self.product.obj_y,'location',index=1,text="Depth")

        split.prop(self.product.obj_bp,'location')

        box.prop(remove_filler,'checkbox_value',text="Remove Filler")

        row = box.row()
        row.label(text="Offset")
        row = box.row(align=True)
        row.prop(lo,'distance_value',text="Left")
        row.prop(ro,'distance_value',text="Right")
        row.prop(to,'distance_value',text="Top")
        row.prop(bo,'distance_value',text="Bottom")

        box = layout.box()
        box.prop(self,'built_in_oven_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"built_in_oven_name",show_labels=True)     


class hb_sample_cabinets_OT_built_in_microwave_prompts(Appliance_Prompts):
    bl_idname = "hb_sample_cabinets.built_in_microwave_prompts"
    bl_label = "Built In Microwave Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    built_in_microwave_changed: bpy.props.BoolProperty(name="Built In Microwave Changed",default=False)

    built_in_microwave_category: bpy.props.EnumProperty(name="Built In Microwave Category",
        items=enum_cabinets.enum_built_in_microwave_categories,
        update=enum_cabinets.update_built_in_microwave_category)
    built_in_microwave_name: bpy.props.EnumProperty(name="Built In Microwave Name",
        items=enum_cabinets.enum_built_in_microwave_names,
        update=update_built_in_microwave)

    product = None

    def reset_variables(self,context):
        self.product = None
        # enum_cabinets.update_refrigerator_category(self,context)

    def check(self, context):
        # self.update_product_size(self.product)
        # self.update_dishwasher(context)
        return True

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
        # self.set_default_properties(self.product)      
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=425)

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.APPLIANCE_TAG)
        self.product = types_appliances.Built_In_Microwave(bp)

    def draw(self, context):
        unit_system = context.scene.unit_settings.system

        layout = self.layout

        remove_filler = self.product.get_prompt("Remove Filler")
        lo = self.product.get_prompt("Appliance Left Offset")
        ro = self.product.get_prompt("Appliance Right Offset")
        to = self.product.get_prompt("Appliance Top Offset")
        bo = self.product.get_prompt("Appliance Bottom Offset")

        box = layout.box()
        split = box.split()
        col = split.column(align=True)
        col.label(text="Dimensions")
        if pc_utils.object_has_driver(self.product.obj_x):
            x = self.product.obj_x.location.x
            col.label(text="Width: " + str(bpy.utils.units.to_string(unit_system,'LENGTH',x)))
        else:
            col.prop(self.product.obj_x,'location',index=0,text="Width")

        if pc_utils.object_has_driver(self.product.obj_z):
            z = self.product.obj_z.location.z
            col.label(text="Height: " + str(bpy.utils.units.to_string(unit_system,'LENGTH',z)))
        else:
            col.prop(self.product.obj_z,'location',index=2,text="Height")

        if pc_utils.object_has_driver(self.product.obj_x):
            y = self.product.obj_y.location.y
            col.label(text="Depth: " + str(bpy.utils.units.to_string(unit_system,'LENGTH',y)))
        else:
            col.prop(self.product.obj_y,'location',index=1,text="Depth")

        split.prop(self.product.obj_bp,'location')

        box.prop(remove_filler,'checkbox_value',text="Remove Filler")

        row = box.row()
        row.label(text="Offset")
        row = box.row(align=True)
        row.prop(lo,'distance_value',text="Left")
        row.prop(ro,'distance_value',text="Right")
        row.prop(to,'distance_value',text="Top")
        row.prop(bo,'distance_value',text="Bottom")

        box = layout.box()
        box.prop(self,'built_in_microwave_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"built_in_microwave_name",show_labels=True)  


class hb_sample_cabinets_OT_refrigerator_prompts(Appliance_Prompts):
    bl_idname = "hb_sample_cabinets.refrigerator_prompts"
    bl_label = "Refrigerator Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    refrigerator_changed: bpy.props.BoolProperty(name="Refrigerator Changed",default=False)

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Door"),
                                              ('TOP',"Top","Top Swing Door"),
                                              ('BOTTOM',"Bottom","Bottom Swing Door")])

    refrigerator_category: bpy.props.EnumProperty(name="Refrigerator Category",
        items=enum_cabinets.enum_refrigerator_categories,
        update=enum_cabinets.update_refrigerator_category)
    refrigerator_name: bpy.props.EnumProperty(name="Refrigerator Name",
        items=enum_cabinets.enum_refrigerator_names,
        update=update_refrigerator)

    product = None

    def reset_variables(self,context):
        self.product = None
        enum_cabinets.update_refrigerator_category(self,context)

    def check(self, context):
        door_swing = self.product.doors.get_prompt("Door Swing")
        if self.door_swing == 'LEFT':
            door_swing.set_value(0)
        if self.door_swing == 'RIGHT':
            door_swing.set_value(1)
        if self.door_swing == 'DOUBLE':
            door_swing.set_value(2)         
        if self.door_swing == 'TOP':
            door_swing.set_value(3)     
        if self.door_swing == 'BOTTOM':
            door_swing.set_value(4)                             
        self.update_product_size(self.product)
        self.update_refrigerator(context)
        return True

    def update_refrigerator(self,context):
        if self.refrigerator_changed:
            self.refrigerator_changed = False

            if self.product:
                pc_utils.delete_object_and_children(self.product.refrigerator.obj_bp)                

            self.product.add_refrigerator(self.refrigerator_category,self.refrigerator_name)
            self.width = self.product.obj_x.location.x
            self.depth = math.fabs(self.product.obj_y.location.y)
            self.height = self.product.obj_z.location.z
            context.view_layer.objects.active = self.product.obj_bp
            pc_utils.hide_empties(self.product.obj_bp)
            self.get_assemblies(context)

    def set_properties_from_prompts(self):
        door_swing = self.product.doors.get_prompt("Door Swing")
        if door_swing.get_value() == 0:
            self.door_swing = 'LEFT'
        if door_swing.get_value() == 1:
            self.door_swing = 'RIGHT'
        if door_swing.get_value() == 2:
            self.door_swing = 'DOUBLE' 
        if door_swing.get_value() == 3:
            self.door_swing = 'TOP' 
        if door_swing.get_value() == 4:
            self.door_swing = 'BOTTOM' 

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = pc_utils.get_bp_by_tag(context.object,const.APPLIANCE_TAG)
        self.product = types_appliances.Refrigerator(bp)

        if self.product.obj_bp.parent and 'IS_WALL_BP' in self.product.obj_bp.parent:
            self.wall = pc_types.Assembly(self.product.obj_bp.parent)
        else:
            self.wall = None

    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        self.set_default_properties(self.product)    
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw_refrigerator_selection(self,layout,context):
        box = layout.box()
        box.prop(self,'refrigerator_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"refrigerator_name",show_labels=True)          

    def draw_refrigerator_prompts(self,layout,context):
        box = layout.box()
        left_filler = self.product.get_prompt("Left Filler Amount")
        right_filler = self.product.get_prompt("Right Filler Amount")

        y_loc = self.product.get_prompt("Refrigerator Y Location")
        y_loc.draw(box,allow_edit=False)
        remove_carcass = self.product.get_prompt("Remove Cabinet Carcass")
        remove_carcass.draw(box,allow_edit=False)
        carcass_height = self.product.get_prompt("Carcass Height")
        carcass_height.draw(box,allow_edit=False)
        if left_filler and right_filler:
            row = box.row()
            row.label(text="Filler")
            row.prop(left_filler,'distance_value',text="Left")
            row.prop(right_filler,'distance_value',text="Right")
        if remove_carcass.get_value() == False and self.product.doors:
            open_door = self.product.doors.get_prompt("Open Door")
            row = box.row()
            row.label(text="Swing")
            row.prop(self,'door_swing',expand=True)
            if open_door:
                open_door.draw(box,allow_edit=False)

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        self.draw_refrigerator_prompts(layout,context)
        self.draw_refrigerator_selection(layout,context)


class hb_sample_cabinets_OT_opening_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.opening_cabinet_prompts"
    bl_label = "Opening Cabinet Prompts"

    is_base: bpy.props.BoolProperty(name="Is Base")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CONSTRUCTION',"Construction","Construction Options")])

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
        self.closet = types_cabinet_starters.Closet_Starter(bp)
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

        if self.product_tabs == 'MAIN':
            self.draw_closet_prompts(prompt_box,context)   
        
        if self.product_tabs == 'CONSTRUCTION':
            self.draw_construction_prompts(prompt_box,context)


class hb_sample_cabinets_OT_inside_corner_cabinet_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.inside_corner_cabinet_prompts"
    bl_label = "Inside Corner Cabinet Prompts"

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
        self.closet = types_cabinet_starters.Closet_Inside_Corner(bp)
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
        filler_left_depth = self.closet.get_prompt("Left Filler Width")
        filler_right_depth = self.closet.get_prompt("Right Filler Width")        
        
        kick_height = self.closet.get_prompt("Closet Kick Height")
        kick_setback = self.closet.get_prompt("Closet Kick Setback")
        shelf_qty = self.closet.get_prompt("Shelf Quantity")
        back_width = self.closet.get_prompt("Back Width")
        flip_back_support_location = self.closet.get_prompt("Flip Back Support Location")

        box = layout.box()
        if left_depth and right_depth:
            row = box.row()
            row.label(text="Left Depth")
            row.prop(left_depth,'distance_value',text="")
            row.label(text="Right Depth")
            row.prop(right_depth,'distance_value',text="")      
        if filler_left_depth and filler_right_depth:
            row = box.row()
            row.label(text="Left Filler Amount")
            row.prop(filler_left_depth,'distance_value',text="")
            row = box.row()
            row.label(text="Right Filler Amount")
            row.prop(filler_right_depth,'distance_value',text="")      

        if kick_height and kick_setback:
            row = box.row()
            row.label(text="Toe Kick")
            row.prop(kick_height,'distance_value',text="Height")
            row.prop(kick_setback,'distance_value',text="Setback")

        if shelf_qty:
            row = box.row()
            row.label(text="Shelf Quantity")
            row.prop(shelf_qty,'quantity_value',text="")

        if back_width:
            row = box.row()
            row.label(text="Back Width")
            row.prop(back_width,'distance_value',text="")

        if flip_back_support_location:
            row.prop(flip_back_support_location,'checkbox_value',text="Flip")

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout)
        self.draw_construction_prompts(layout)


classes = (
    hb_sample_cabinets_OT_cabinet_prompts,
    hb_sample_cabinets_OT_range_prompts,
    hb_sample_cabinets_OT_dishwasher_prompts,
    hb_sample_cabinets_OT_built_in_oven_prompts,
    hb_sample_cabinets_OT_built_in_microwave_prompts,
    hb_sample_cabinets_OT_refrigerator_prompts,
    hb_sample_cabinets_OT_opening_cabinet_prompts,
    hb_sample_cabinets_OT_inside_corner_cabinet_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    