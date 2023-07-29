import bpy
from . import utils_cabinet
from . import const_cabinets as const
from pc_lib import pc_utils

class HOME_BUILDER_MT_cabinet_settings(bpy.types.Menu):
    bl_label = "Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="HOME_BUILDER_PT_cabinet_sizes",text="Cabinet Sizes",icon='DRIVER_DISTANCE')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_construction",text="Cabinet Construction",icon='MODIFIER_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_material_thickness",text="Cabinet Material Thickness",icon='MATERIAL_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_hardware",text="Cabinet Hardware",icon='MATERIAL_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_fronts",text="Cabinet Fronts",icon='SNAP_FACE')
        layout.separator()
        layout.popover(panel="HOME_BUILDER_PT_asset_management",text="Asset Management",icon='ASSET_MANAGER')
        # layout.separator()
        # layout.operator('hb_sample_cabinets.build_library',text="Build Cabinet Library")


class HOME_BUILDER_MT_cabinet_commands(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CABINET_TAG)
        layout = self.layout
        layout.operator('hb_sample_cabinets.cabinet_prompts',icon='WINDOW')   
        layout.operator('hb_sample_cabinets.place_cabinet_on_wall',icon='EMPTY_ARROWS')   
        layout.operator('hb_sample_cabinets.clear_cabinet_carcass',icon='CUBE') 
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Cabinet",icon='X').obj_name = bp.name


class HOME_BUILDER_MT_cabinet_opening_commands(bpy.types.Menu):
    bl_label = "Cabinet Opening Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_TAG)
        layout = self.layout
        layout.operator('hb_sample_cabinets.change_cabinet_offsets',icon='TRACKING_CLEAR_FORWARDS')  
        layout.operator('hb_sample_cabinets.change_number_of_openings',icon='UV_ISLANDSEL')  
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Starter",icon='X').obj_name = bp.name
        

class HOME_BUILDER_MT_cabinet_insert_commands(bpy.types.Menu):
    bl_label = "Cabinet Insert Commands"

    def draw(self, context):
        insert_bp = pc_utils.get_bp_by_tag(context.object,const.INSERT_TAG)
        layout = self.layout      
        layout.operator('hb_sample_cabinets.duplicate_closet_insert',icon='DUPLICATE')  
        layout.separator()
        layout.operator('hb_sample_cabinets.delete_cabinet_insert',text="Delete Insert",icon='X')        


class HOME_BUILDER_MT_closets_corner_commands(bpy.types.Menu):
    bl_label = "Closet Corner Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.CLOSET_INSIDE_CORNER_TAG)
        layout = self.layout        
        layout.operator('home_builder.delete_assembly',text="Delete Corner Starter",icon='X').obj_name = bp.name


class HOME_BUILDER_MT_appliance_commands(bpy.types.Menu):
    bl_label = "Appliance Commands"

    def draw(self, context):
        bp = pc_utils.get_bp_by_tag(context.object,const.APPLIANCE_TAG)
        layout = self.layout
        layout.operator('hb_sample_cabinets.place_cabinet_on_wall',text="Place Appliance on Wall",icon='EMPTY_ARROWS')  
        layout.operator('home_builder.delete_assembly',text="Delete Appliance",icon='X').obj_name = bp.name


class HOME_BUILDER_PT_cabinet_sizes(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Sizes"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 23

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout

        box = layout.box()
        box.label(text="Standard Cabinet Sizes:")

        row = box.row(align=True)
        row.label(text="Base:")
        row.prop(props,'base_cabinet_height',text="Height")
        row.prop(props,'base_cabinet_depth',text="Depth")

        row = box.row(align=True)
        row.label(text="Tall:")    
        row.prop(props,'tall_cabinet_height',text="Height")    
        row.prop(props,'tall_cabinet_depth',text="Depth")
        
        row = box.row(align=True)
        row.label(text="Upper:")    
        row.prop(props,'upper_cabinet_height',text="Height")        
        row.prop(props,'upper_cabinet_depth',text="Depth")
        
        row = box.row(align=True)
        row.label(text="Sink:")       
        row.prop(props,'sink_cabinet_height',text="Height")     
        row.prop(props,'sink_cabinet_depth',text="Depth")
        
        row = box.row(align=True)
        row.label(text="Suspended:")
        row.prop(props,'suspended_cabinet_height',text="Height")
        row.prop(props,'suspended_cabinet_depth',text="Depth")
        
        row = box.row(align=True)
        row.label(text="Width:")  
        row.prop(props,'width_1_door',text="1 Door")
        row.prop(props,'width_2_door',text="2 Door")
        row.prop(props,'width_drawer',text="Drawer")

        row = box.row(align=True)
        row.label(text="Blind Widths:")  
        row.prop(props,'base_width_blind',text="Base")
        row.prop(props,'tall_width_blind',text="Tall")
        row.prop(props,'upper_width_blind',text="Upper")
        
        row = box.row(align=True)
        row.label(text="Inside Corner Widths:")     
        row.prop(props,'base_inside_corner_size',text="Base")
        row.prop(props,'tall_inside_corner_size',text="Tall")          
        row.prop(props,'upper_inside_corner_size',text="Upper")     
        
        row = box.row(align=True)
        row.label(text="Stacked Cabinet Heights:")
        row.prop(props,'stacked_top_cabinet_height',text="Top Cabinet Height")  

        box = layout.box()
        box.label(text="Upper Cabinet Placement:")
        row = box.row(align=True)
        row.label(text="Height Above Floor:")    
        row.prop(props,'height_above_floor',text="To Top of Cabinet")         


class HOME_BUILDER_PT_cabinet_construction(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Construction"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 20

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout

        box = layout.box()
        box.label(text="Cabinet Base Assembly:")
        row = box.row(align=True)
        row.label(text="Base Assembly Size:")       
        row.prop(props,'toe_kick_height',text="Height")       
        row.prop(props,'toe_kick_setback',text="Setback")       

        box = layout.box()
        box.label(text="Cabinet Interior:")
        row = box.row(align=True)
        row.label(text="Add Shelves to Interiors:")    
        row.prop(props,'add_shelves_to_interior',text="")  

        box = layout.box()
        box.label(text="Cabinet Countertop:")
        row = box.row(align=True)
        row.label(text="Overhang:")       
        row.prop(props,'countertop_front_overhang',text="Front")       
        row.prop(props,'countertop_rear_overhang',text="Rear")      
        row.prop(props,'countertop_front_overhang',text="Side")          


class HOME_BUILDER_PT_cabinet_material_thickness(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Material Thickness"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 16

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout
        box = layout.box()

        row = box.row()
        row.label(text="Countertop Thickness")
        row.prop(props,'countertop_thickness',text="")  

        row = box.row()
        row.label(text="Cabinet Carcass Thickness")
        row.prop(props,'cabinet_part_thickness',text="") 

        row = box.row()
        row.label(text="Cabinet Front Thickness")
        row.prop(props,'cabinet_front_thickness',text="") 

        row = box.row()
        row.label(text="Closet Shelf Thickness")
        row.prop(props,'closet_shelf_thickness',text="") 

        row = box.row()
        row.label(text="Closet Panel Thickness")
        row.prop(props,'closet_panel_thickness',text="") 


class HOME_BUILDER_PT_cabinet_hardware(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Hardware"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 16

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout

        box = layout.box()
        box.label(text="Cabinet Handle Library")
        row = box.row()
        row.operator('hb_sample_cabinets.update_all_pulls_in_room',text="Update All",icon='FILE_REFRESH')
        row.operator('hb_sample_cabinets.update_selected_pulls_in_room',text="Update Selected",icon='FILE_REFRESH')

        row = box.row()
        row.prop(props,'cabinet_handle_category',text="")    

        row = box.row()
        row.template_icon_view(props,"cabinet_handle",show_labels=True)   

        row = box.row()
        op_props = row.operator('home_builder.update_checkbox_prompt_in_scene',text="Turn Off Handles",icon='HIDE_ON')
        op_props.prompt_name = "Turn Off Pulls"
        op_props.prompt_value = True
        op_props = row.operator('home_builder.update_checkbox_prompt_in_scene',text="Show All Handles",icon='HIDE_OFF')
        op_props.prompt_name = "Turn Off Pulls"
        op_props.prompt_value = False

        box = layout.box()
        box.label(text="Cabinet Handle Location:")
        row = box.row(align=True)
        row.label(text="Center Pulls on Drawers:")        
        row.prop(props,'center_pulls_on_drawer_front',text="")      
        op_props = row.operator('home_builder.update_checkbox_prompt_in_scene',text="",icon='FILE_REFRESH',emboss=False)
        op_props.prompt_name = "Center Pull on Front"
        op_props.prompt_value = False          
        if not props.center_pulls_on_drawer_front:
            row = box.row(align=True)
            row.label(text="Drawer Pull Vertical Location:")        
            row.prop(props,'pull_vertical_location_drawers',text="From Top of Drawer")       

        row = box.row(align=True)
        row.label(text="Horizontal Location:")        
        row.prop(props,'pull_dim_from_edge',text="")       
        op_props = row.operator('home_builder.update_distance_prompt_in_scene',text="",icon='FILE_REFRESH',emboss=False)
        op_props.prompt_name = "Pull Horizontal Location"
        op_props.prompt_value = props.pull_dim_from_edge

        row = box.row(align=True)
        row.label(text="Base Vertical Location:")        
        row.prop(props,'pull_vertical_location_base',text="Top of Door")    
        op_props = row.operator('home_builder.update_distance_prompt_in_scene',text="",icon='FILE_REFRESH',emboss=False)
        op_props.prompt_name = "Base Pull Vertical Location"
        op_props.prompt_value = props.pull_vertical_location_base      

        row = box.row(align=True)
        row.label(text="Tall Vertical Location:")        
        row.prop(props,'pull_vertical_location_tall',text="Bottom of Door")   
        op_props = row.operator('home_builder.update_distance_prompt_in_scene',text="",icon='FILE_REFRESH',emboss=False)
        op_props.prompt_name = "Tall Pull Vertical Location"
        op_props.prompt_value = props.pull_vertical_location_tall      

        row = box.row(align=True)
        row.label(text="Upper Vertical Location:")        
        row.prop(props,'pull_vertical_location_upper',text="Bottom of Door")  
        op_props = row.operator('home_builder.update_distance_prompt_in_scene',text="",icon='FILE_REFRESH',emboss=False)
        op_props.prompt_name = "Upper Pull Vertical Location"
        op_props.prompt_value = props.pull_vertical_location_upper                   


class HOME_BUILDER_PT_cabinet_fronts(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Fronts"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 16

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout

        box = layout.box()
        box.prop(props,'show_door_library',text="Use Front Library")

        box.label(text="Cabinet Front Library")
        row = box.row()
        row.operator('hb_sample_cabinets.update_all_fronts_in_room',text="Update All",icon='FILE_REFRESH')
        row.operator('hb_sample_cabinets.update_selected_fronts_in_room',text="Update Selected",icon='FILE_REFRESH')     

        row = box.row()
        row.prop(props,'cabinet_door_category',text="")    

        row = box.row()
        row.template_icon_view(props,"cabinet_door",show_labels=True)     


class HOME_BUILDER_PT_asset_management(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Asset Management"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 25

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout
        layout.label(text="Cabinet Library Asset Management")
        split = layout.split(factor=.25)
        col = split.column(align=True)
        col.prop(props,'asset_tabs',expand=True)

        box = split.box()
        row = box.row()
        row.menu('HOME_BUILDER_MT_asset_management_commands_menu',text="_Sample",icon='FILEBROWSER')
        row.menu('HOME_BUILDER_MT_asset_management_commands_menu',text="",icon='DOWNARROW_HLT')
        # box.label(text="ASSET LIST")


class HOME_BUILDER_MT_asset_management_commands_menu(bpy.types.Menu):
    bl_label = "Asset Management Commands"

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)
        # path = props.get_active_category_path()
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('hb_sample_cabinets.save_asset_to_library',text="Save Asset to Library",icon='BACK')
        layout.operator('hb_sample_cabinets.save_asset_to_library',text="Create Thumbnail for Selected Assets",icon='FILE_IMAGE')
        layout.operator('hb_sample_cabinets.save_asset_to_library',text="Open Browser Window",icon='FILEBROWSER')
        layout.operator('hb_sample_cabinets.save_asset_to_library',text="Create New Asset",icon='ADD')

classes = (
    HOME_BUILDER_MT_cabinet_settings,
    HOME_BUILDER_MT_cabinet_commands,
    HOME_BUILDER_MT_cabinet_opening_commands,
    HOME_BUILDER_MT_cabinet_insert_commands,
    HOME_BUILDER_MT_closets_corner_commands,
    HOME_BUILDER_MT_appliance_commands,
    HOME_BUILDER_PT_cabinet_sizes,
    HOME_BUILDER_PT_cabinet_construction,
    HOME_BUILDER_PT_cabinet_material_thickness,
    HOME_BUILDER_PT_cabinet_hardware,
    HOME_BUILDER_PT_cabinet_fronts,
    HOME_BUILDER_PT_asset_management,
    HOME_BUILDER_MT_asset_management_commands_menu,
)

register, unregister = bpy.utils.register_classes_factory(classes)          