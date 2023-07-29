import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
import inspect
from . import const_cabinets as const
from . import enum_cabinets
from pc_lib import pc_types, pc_unit, pc_utils

class Pointer(PropertyGroup):
    category_name: StringProperty(name="Category Name")
    item_name: StringProperty(name="Item Name")

class HB_Cabinet_Scene_Props(PropertyGroup):    

    #ENUMS
    cabinet_handle_category: bpy.props.EnumProperty(name="Cabinet Handle Category",
        items=enum_cabinets.enum_cabinet_handle_categories,
        update=enum_cabinets.update_cabinet_handle_category)
    cabinet_handle: bpy.props.EnumProperty(name="Cabinet Handle",
        items=enum_cabinets.enum_cabinet_handle_names)

    cabinet_door_category: bpy.props.EnumProperty(name="Cabinet Door Category",
        items=enum_cabinets.enum_cabinet_door_categories,
        update=enum_cabinets.update_cabinet_door_category)
    cabinet_door: bpy.props.EnumProperty(name="Cabinet Door",
        items=enum_cabinets.enum_cabinet_door_names)

    molding_category: bpy.props.EnumProperty(name="Molding Category",
        items=enum_cabinets.enum_molding_categories,
        update=enum_cabinets.update_molding_category)
    molding: bpy.props.EnumProperty(name="Molding",
        items=enum_cabinets.enum_molding_names)

    show_door_library: BoolProperty(name="Show Door Library", 
                                    description="This will show the door library", 
                                    default=False)

    asset_tabs: EnumProperty(name="Asset Tabs",
                             items=[('BUILT_IN_OVENS',"Built in Ovens","Show the Built in Oven Appliances"),
                                    ('BUILT_IN_MICROWAVE',"Built in Microwave","Show the Built in Microwave Appliances"),
                                    ('CABINET_DOORS',"Cabinet Doors","Show the Cabinet Doors"),
                                    ('CABINET_PULLS',"Cabinet Pulls","Show the Cabinet Pulls"),
                                    ('COOKTOPS',"Cooktops","Show the Cooktops"),
                                    ('DISHWASHERS',"Dishwashers","Show the Dishwashers"),
                                    ('FAUCETS',"Faucets","Show the Faucets"),
                                    ('MOLDINGS',"Moldings","Show the Moldings"),
                                    ('RANGE_HOODS',"Range Hoods","Show the Range Hoods"),
                                    ('RANGES',"Ranges","Show the Ranges"),
                                    ('REFRIGERATORS',"Refrigerators","Show the Refrigerators"),
                                    ('SINKS',"Sinks","Show the Sinks")],
                             default='BUILT_IN_OVENS')
    
    #CABINET SIZES
    base_cabinet_depth: FloatProperty(name="Base Cabinet Depth",
                                                 description="Default depth for base cabinets",
                                                 default=pc_unit.inch(23.0),
                                                 unit='LENGTH')
    
    base_cabinet_height: FloatProperty(name="Base Cabinet Height",
                                                  description="Default height for base cabinets",
                                                  default=pc_unit.inch(34.0),
                                                  unit='LENGTH')
    
    base_inside_corner_size: FloatProperty(name="Base Inside Corner Size",
                                           description="Default width and depth for the inside base corner cabinets",
                                           default=pc_unit.inch(36.0),
                                           unit='LENGTH')
    
    tall_inside_corner_size: FloatProperty(name="Tall Inside Corner Size",
                                           description="Default width and depth for the inside tall corner cabinets",
                                           default=pc_unit.inch(36.0),
                                           unit='LENGTH')

    upper_inside_corner_size: FloatProperty(name="Upper Inside Corner Size",
                                           description="Default width and depth for the inside upper corner cabinets",
                                           default=pc_unit.inch(24.0),
                                           unit='LENGTH')

    tall_cabinet_depth: FloatProperty(name="Tall Cabinet Depth",
                                                 description="Default depth for tall cabinets",
                                                 default=pc_unit.inch(25.0),
                                                 unit='LENGTH')
    
    tall_cabinet_height: FloatProperty(name="Tall Cabinet Height",
                                                  description="Default height for tall cabinets",
                                                  default=pc_unit.inch(84.0),
                                                  unit='LENGTH')
    
    upper_cabinet_depth: FloatProperty(name="Upper Cabinet Depth",
                                                  description="Default depth for upper cabinets",
                                                  default=pc_unit.inch(12.0),
                                                  unit='LENGTH')
    
    upper_cabinet_height: FloatProperty(name="Upper Cabinet Height",
                                                   description="Default height for upper cabinets",
                                                   default=pc_unit.inch(34.0),
                                                   unit='LENGTH')
    
    upper_inside_corner_size: FloatProperty(name="Upper Inside Corner Size",
                                                      description="Default width and depth for the inside upper corner cabinets",
                                                      default=pc_unit.inch(24.0),
                                                      unit='LENGTH')
    
    sink_cabinet_depth: FloatProperty(name="Upper Cabinet Depth",
                                                 description="Default depth for sink cabinets",
                                                 default=pc_unit.inch(23.0),
                                                 unit='LENGTH')
    
    sink_cabinet_height: FloatProperty(name="Upper Cabinet Height",
                                                  description="Default height for sink cabinets",
                                                  default=pc_unit.inch(34.0),
                                                  unit='LENGTH')

    suspended_cabinet_depth: FloatProperty(name="Upper Cabinet Depth",
                                                      description="Default depth for suspended cabinets",
                                                      default=pc_unit.inch(23.0),
                                                      unit='LENGTH')
    
    suspended_cabinet_height: FloatProperty(name="Upper Cabinet Height",
                                                       description="Default height for suspended cabinets",
                                                       default=pc_unit.inch(6.0),
                                                       unit='LENGTH')

    column_width: FloatProperty(name="Column Width",
                                           description="Default width for cabinet columns",
                                           default=pc_unit.inch(2),
                                           unit='LENGTH')

    width_1_door: FloatProperty(name="Width 1 Door",
                                           description="Default width for one door wide cabinets",
                                           default=pc_unit.inch(18.0),
                                           unit='LENGTH')
    
    width_2_door: FloatProperty(name="Width 2 Door",
                                           description="Default width for two door wide and open cabinets",
                                           default=pc_unit.inch(36.0),
                                           unit='LENGTH')
    
    width_drawer: FloatProperty(name="Width Drawer",
                                           description="Default width for drawer cabinets",
                                           default=pc_unit.inch(18.0),
                                           unit='LENGTH')
    
    base_width_blind: FloatProperty(name="Base Width Blind",
                                               description="Default width for base blind corner cabinets",
                                               default=pc_unit.inch(48.0),
                                               unit='LENGTH')
    
    tall_width_blind: FloatProperty(name="Tall Width Blind",
                                               description="Default width for tall blind corner cabinets",
                                               default=pc_unit.inch(48.0),
                                               unit='LENGTH')
    
    blind_panel_reveal: FloatProperty(name="Blind Panel Reveal",
                                                 description="Default reveal for blind panels",
                                                 default=pc_unit.inch(3.0),
                                                 unit='LENGTH')
    
    inset_blind_panel: BoolProperty(name="Inset Blind Panel",
                                               description="Check this to inset the blind panel into the cabinet carcass",
                                               default=True)
    
    upper_width_blind: FloatProperty(name="Upper Width Blind",
                                                description="Default width for upper blind corner cabinets",
                                                default=pc_unit.inch(36.0),
                                                unit='LENGTH')

    stacked_top_cabinet_height: FloatProperty(name="Stacked Top Cabinet Height",
                                                description="Default Height for the Top Cabinet on Stacked Cabinets",
                                                default=pc_unit.inch(12.0),
                                                unit='LENGTH')

    #CABINET HANDLES
    height_above_floor: FloatProperty(name="Height Above Floor",
                                                 description="Default height above floor for upper cabinets",
                                                 default=pc_unit.inch(84.0),
                                                 unit='LENGTH')
    
    pull_dim_from_edge: FloatProperty(name="Pull Distance From Edge",
                                                 description="Distance from Edge of Door to center of pull",
                                                 default=pc_unit.inch(2.0),
                                                 unit='LENGTH')

    pull_vertical_location_base: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Top of Base Door to Top of Pull",
                                                 default=pc_unit.inch(1.5),
                                                 unit='LENGTH')

    pull_vertical_location_tall: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Bottom of Tall Door to Center of Pull",
                                                 default=pc_unit.inch(45),
                                                 unit='LENGTH')

    pull_vertical_location_upper: FloatProperty(name="Pull Vertical Location Base",
                                                 description="Distance from Bottom of Upper Door to Bottom of Pull",
                                                 default=pc_unit.inch(1.5),
                                                 unit='LENGTH')

    pull_vertical_location_drawers: FloatProperty(name="Pull Vertical Location Drawers",
                                                 description="Distance from Top of Drawer Front to Center of Pull",
                                                 default=pc_unit.inch(1.5),
                                                 unit='LENGTH')

    center_pulls_on_drawer_front: BoolProperty(name="Center Pulls on Drawer Front", 
                                                        description="Check this to center pulls on drawer fronts. Otherwise vertical location will be used.", 
                                                        default=True)

    equal_drawer_stack_heights: BoolProperty(name="Equal Drawer Stack Heights", 
                                                        description="Check this make all drawer stack heights equal. Otherwise the Top Drawer Height will be set.", 
                                                        default=True)
    
    top_drawer_front_height: FloatProperty(name="Top Drawer Front Height",
                                                      description="Default top drawer front height.",
                                                      default=pc_unit.inch(6.0),
                                                      unit='LENGTH')

    #CABINET CONSTRUCTION
    toe_kick_height: bpy.props.FloatProperty(name="Toe Kick Height",
                                             description="This is the default height of the toe kick.",
                                             default=pc_unit.inch(4.0),
                                             unit='LENGTH')

    toe_kick_setback: bpy.props.FloatProperty(name="Toe Kick Setback",
                                             description="This is the default setback of the toe kick.",
                                             default=pc_unit.inch(2.5),
                                             unit='LENGTH')

    add_backsplash: bpy.props.BoolProperty(name="Add Backsplash",
                                           description="Check this to include a countertop backsplash",
                                           default=True)

    add_shelves_to_interior: BoolProperty(name="Add Shelves to Interior", 
                                          description="Check this to add shelves to cabinet interiors", 
                                          default=False)

    countertop_backsplash_height: bpy.props.FloatProperty(name="Coutnertop Backsplash Height",
                                                          description="Enter the Height for the Countertop Backsplash",
                                                          default=pc_unit.inch(4.0))

    countertop_front_overhang: bpy.props.FloatProperty(name="Countertop Front Overhang",
                                                       description="This front overhang of the countertop.",
                                                       default=pc_unit.inch(1.0),
                                                       unit='LENGTH')

    countertop_side_overhang: bpy.props.FloatProperty(name="Countertop Side Overhang",
                                                       description="This is the side overhang of countertops with Finished Ends",
                                                       default=pc_unit.inch(1.0),
                                                       unit='LENGTH')

    countertop_rear_overhang: bpy.props.FloatProperty(name="Countertop Rear Overhang",
                                                       description="This is the rear overhang of countertops.",
                                                       default=pc_unit.inch(1.0),
                                                       unit='LENGTH')     

    #MATERIAL THICKNESS
    countertop_thickness: bpy.props.FloatProperty(name="Countertop Thickness",
                                                  description="This is the thickness of countertops.",
                                                  default=pc_unit.inch(1.5),
                                                  unit='LENGTH')       

    cabinet_part_thickness: bpy.props.FloatProperty(name="Cabinet Part Thickness",
                                                    description="This is the thickness of cabinet carcass part.",
                                                    default=pc_unit.inch(.75),
                                                    unit='LENGTH')  

    cabinet_front_thickness: bpy.props.FloatProperty(name="Cabinet Front Thickness",
                                                     description="This is the thickness of cabinet door and drawer fronts.",
                                                     default=pc_unit.inch(.75),
                                                     unit='LENGTH')  

    closet_shelf_thickness: bpy.props.FloatProperty(name="Closet Shelf Thickness",
                                                    description="This is the thickness of closet shelf thickness.",
                                                    default=pc_unit.inch(.75),
                                                    unit='LENGTH')  

    closet_panel_thickness: bpy.props.FloatProperty(name="Closet Panel Thickness",
                                                    description="This is the thickness of closet panels.",
                                                    default=pc_unit.inch(.75),
                                                    unit='LENGTH')  

    #CLOSET OPTIONS
    use_fixed_closet_heights: bpy.props.BoolProperty(name="Use Fixed Closet Heights",
                                           description="Check this option to use the 32mm system and force panel heights to change in 32mm increments.",
                                           default=False) 

    add_bottom_filler_shelf: bpy.props.BoolProperty(name="Add Bottom Filler Shelf",
                                           description="Check this option to add a bottom shelf when turning on filler panels.",
                                           default=False) 

    closet_toe_kick_height: bpy.props.FloatProperty(name="Closet Toe Kick Height",
                                             description="This is the default height of the toe kick.",
                                             default=pc_unit.millimeter(96),
                                             unit='LENGTH')

    closet_toe_kick_setback: bpy.props.FloatProperty(name="Closet Toe Kick Setback",
                                             description="This is the default setback of the toe kick.",
                                             default=pc_unit.inch(1.625),
                                             unit='LENGTH')

    default_closet_hanging_height: bpy.props.EnumProperty(name="Default Closet Hanging Height",
                                                     items=const.PANEL_HEIGHTS,
                                                     default = '2131')

    tall_closet_panel_height: bpy.props.EnumProperty(name="Tall Closet Panel Height",
                                                     items=const.PANEL_HEIGHTS,
                                                     default = '2131')

    hanging_closet_panel_height: bpy.props.EnumProperty(name="Hanging Closet Panel Height",
                                                     items=const.PANEL_HEIGHTS,
                                                     default = '1267')

    base_closet_panel_height: bpy.props.EnumProperty(name="Base Closet Panel Height",
                                                     items=const.PANEL_HEIGHTS,
                                                     default = '819')

    default_base_closet_depth: bpy.props.FloatProperty(name="Default Base Closet Depth",
                                                 description="Default depth for base closets",
                                                 default=pc_unit.inch(14.0),
                                                 unit='LENGTH')

    opening_height_to_fill_doors: bpy.props.FloatProperty(name="Opening Height to Fill Doors",
                                                 description="The maximum opening height to automatically fill opening when placing closet doors.",
                                                 default=pc_unit.inch(35.0),
                                                 unit='LENGTH')

    default_hanging_closet_depth: bpy.props.FloatProperty(name="Default hanging Closet Depth",
                                                 description="Default depth for Hanging closets",
                                                 default=pc_unit.inch(14.0),
                                                 unit='LENGTH')

    default_tall_closet_depth: bpy.props.FloatProperty(name="Default Tall Closet Depth",
                                                 description="Default depth for tall closets",
                                                 default=pc_unit.inch(14.0),
                                                 unit='LENGTH')

    closet_corner_spacing: bpy.props.FloatProperty(name="Closet Corner Spacing",
                                                 description="Offset for closets when meeting in corner",
                                                 default=pc_unit.inch(12.0),
                                                 unit='LENGTH')

    show_closet_panel_drilling: bpy.props.BoolProperty(name="Show Panel Drilling",
                                                       description="Check this option if you want drilling to show on the closet panels",
                                                       default=False)      

    adj_shelf_setback: bpy.props.FloatProperty(name="Adjustable Shelf Setback",
                                                 description="Default setback for adjustable shelves",
                                                 default=0,
                                                 unit='LENGTH')

    fixed_shelf_setback: bpy.props.FloatProperty(name="Fixed Shelf Setback",
                                                 description="Default setback for fixed shelves",
                                                 default=0,
                                                 unit='LENGTH')

    shelf_clip_gap: bpy.props.FloatProperty(name="Shelf Clip Gap",
                                                 description="Amount to deduct from shelf width for adjustable shelf clips",
                                                 default=0,
                                                 unit='LENGTH')

    extend_panel_amount: bpy.props.FloatProperty(name="Extend Panel Amount",
                                                 description="The amount to extend the panels to countertop",
                                                 default=0,
                                                 unit='LENGTH')

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_cabinet = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_cabinet               


class HB_Cabinet_Object_Props(PropertyGroup):

    part_name: bpy.props.StringProperty(name="Part Name")
    
    ebw1: bpy.props.BoolProperty(name="Edgeband Width 1",default=False)
    ebw2: bpy.props.BoolProperty(name="Edgeband Width 2",default=False)
    ebl1: bpy.props.BoolProperty(name="Edgeband Length 1",default=False)
    ebl2: bpy.props.BoolProperty(name="Edgeband Length 2",default=False)

    opening_number: bpy.props.IntProperty(name="Opening Number") 

    @classmethod
    def register(cls):
        bpy.types.Object.hb_cabinet = PointerProperty(
            name="HB Cabinet Props",
            description="HB Cabinet Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.hb_cabinet

classes = (
    Pointer,
    HB_Cabinet_Scene_Props,
    HB_Cabinet_Object_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)                                                                                             