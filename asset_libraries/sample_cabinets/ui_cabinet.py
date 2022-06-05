import bpy
from . import utils_cabinet

class HOME_BUILDER_MT_cabinet_settings(bpy.types.Menu):
    bl_label = "Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="HOME_BUILDER_PT_cabinet_sizes",text="Cabinet Sizes",icon='DRIVER_DISTANCE')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_construction",text="Cabinet Construction",icon='MODIFIER_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_material_thickness",text="Cabinet Material Thickness",icon='MATERIAL_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_hardware",text="Cabinet Hardware",icon='MATERIAL_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_fronts",text="Cabinet Fronts",icon='SNAP_FACE')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_moldings",text="Cabinet Moldings",icon='IPO_CONSTANT')
        layout.separator()
        layout.operator('hb_sample_cabinets.build_library',text="Build Cabinet Library")


class HOME_BUILDER_MT_cabinet_commands(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator('hb_sample_cabinets.cabinet_prompts',icon='WINDOW')        


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
        row.prop(props,'cabinet_handle_category',text="")    

        row = box.row()
        row.template_icon_view(props,"cabinet_handle",show_labels=True)   

        box = layout.box()
        box.label(text="Cabinet Library Pointers")   
        row = box.row()
        row.operator('hb_sample_cabinets.assign_handle_pointer',text="",icon='TRIA_RIGHT').pointer_name = "base_handle"
        row.label(text="Base Handle: " + props.base_handle.category_name + " - " + props.base_handle.item_name)  
                       
        row = box.row()
        row.operator('hb_sample_cabinets.assign_handle_pointer',text="",icon='TRIA_RIGHT').pointer_name = "tall_handle"
        row.label(text="Tall Handle: " + props.tall_handle.category_name + " - " + props.tall_handle.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_handle_pointer',text="",icon='TRIA_RIGHT').pointer_name = "upper_handle"
        row.label(text="Upper Handle: " + props.upper_handle.category_name + " - " + props.upper_handle.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_handle_pointer',text="",icon='TRIA_RIGHT').pointer_name = "drawer_handle"
        row.label(text="Drawer Handle: " + props.drawer_handle.category_name + " - " + props.drawer_handle.item_name)                                         

        box = layout.box()
        box.label(text="Cabinet Handle Location:")
        row = box.row(align=True)
        row.label(text="Center Pulls on Drawers:")        
        row.prop(props,'center_pulls_on_drawer_front',text="")        
        if not props.center_pulls_on_drawer_front:
            row = box.row(align=True)
            row.label(text="Drawer Pull Vertical Location:")        
            row.prop(props,'pull_vertical_location_drawers',text="From Top of Drawer")       

        row = box.row(align=True)
        row.label(text="Horizontal Location:")        
        row.prop(props,'pull_dim_from_edge',text="")       
        row = box.row(align=True)
        row.label(text="Base Vertical Location:")        
        row.prop(props,'pull_vertical_location_base',text="Top of Door")                   
        row = box.row(align=True)
        row.label(text="Tall Vertical Location:")        
        row.prop(props,'pull_vertical_location_tall',text="Bottom of Door")   
        row = box.row(align=True)
        row.label(text="Upper Vertical Location:")        
        row.prop(props,'pull_vertical_location_upper',text="Bottom of Door")       


class HOME_BUILDER_PT_cabinet_fronts(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Fronts"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 16

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout

        box = layout.box()
        box.label(text="Cabinet Front Library")
        row = box.row()
        row.prop(props,'cabinet_door_category',text="")    

        row = box.row()
        row.template_icon_view(props,"cabinet_door",show_labels=True)   

        box = layout.box()
        box.label(text="Cabinet Front Pointers")   
        row = box.row()
        row.operator('hb_sample_cabinets.assign_door_pointer',text="",icon='TRIA_RIGHT').pointer_name = "base_door"
        row.label(text="Base Door: " + props.base_door.category_name + " - " + props.base_door.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_door_pointer',text="",icon='TRIA_RIGHT').pointer_name = "tall_door"
        row.label(text="Tall Door: " + props.tall_door.category_name + " - " + props.tall_door.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_door_pointer',text="",icon='TRIA_RIGHT').pointer_name = "upper_door"
        row.label(text="Upper Door: " + props.upper_door.category_name + " - " + props.upper_door.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_door_pointer',text="",icon='TRIA_RIGHT').pointer_name = "drawer_front"
        row.label(text="Drawer Front: " + props.drawer_front.category_name + " - " + props.drawer_front.item_name)       


class HOME_BUILDER_PT_cabinet_moldings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Moldings"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 16

    def draw(self, context):
        props = utils_cabinet.get_scene_props(context.scene)

        layout = self.layout

        box = layout.box()
        box.label(text="Molding Library")
        row = box.row()
        row.prop(props,'molding_category',text="")    

        row = box.row()
        row.template_icon_view(props,"molding",show_labels=True)   

        box = layout.box()
        box.label(text="Molding Pointers")   
        row = box.row()
        row.operator('hb_sample_cabinets.assign_molding_pointer',text="",icon='TRIA_RIGHT').pointer_name = "base_molding"
        row.label(text="Base Molding: " + props.base_molding.category_name + " - " + props.base_molding.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_molding_pointer',text="",icon='TRIA_RIGHT').pointer_name = "crown_molding"
        row.label(text="Crown Molding: " + props.crown_molding.category_name + " - " + props.crown_molding.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_molding_pointer',text="",icon='TRIA_RIGHT').pointer_name = "light_rail_molding"
        row.label(text="Light Rail Molding: " + props.light_rail_molding.category_name + " - " + props.light_rail_molding.item_name)  

        row = box.row()
        row.operator('hb_sample_cabinets.assign_molding_pointer',text="",icon='TRIA_RIGHT').pointer_name = "wall_crown_molding"
        row.label(text="Wall Crown Molding: " + props.wall_crown_molding.category_name + " - " + props.wall_crown_molding.item_name)   

classes = (
    HOME_BUILDER_MT_cabinet_settings,
    HOME_BUILDER_MT_cabinet_commands,
    HOME_BUILDER_PT_cabinet_sizes,
    HOME_BUILDER_PT_cabinet_construction,
    HOME_BUILDER_PT_cabinet_material_thickness,
    HOME_BUILDER_PT_cabinet_hardware,
    HOME_BUILDER_PT_cabinet_fronts,
    HOME_BUILDER_PT_cabinet_moldings,
)

register, unregister = bpy.utils.register_classes_factory(classes)          