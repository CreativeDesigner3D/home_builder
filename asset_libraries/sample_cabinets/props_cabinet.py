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
from pc_lib import pc_types, pc_unit, pc_utils

class HB_Cabinet_Scene_Props(PropertyGroup):    
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

    upper_stacked_cabinet_height: FloatProperty(name="Upper Stacked Cabinet Height",
                                                description="Default Height for Stacked Upper Cabinet Height",
                                                default=pc_unit.inch(46.0),
                                                unit='LENGTH')

    stacked_top_cabinet_height: FloatProperty(name="Stacked Top Cabinet Height",
                                                description="Default Height for the Top Cabinet on Stacked Cabinets",
                                                default=pc_unit.inch(12.0),
                                                unit='LENGTH')

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
                                                        description="Check this center pulls on drawer fronts. Otherwise vertical location will be used.", 
                                                        default=True)

    equal_drawer_stack_heights: BoolProperty(name="Equal Drawer Stack Heights", 
                                                        description="Check this make all drawer stack heights equal. Otherwise the Top Drawer Height will be set.", 
                                                        default=True)
    
    top_drawer_front_height: FloatProperty(name="Top Drawer Front Height",
                                                      description="Default top drawer front height.",
                                                      default=pc_unit.inch(6.0),
                                                      unit='LENGTH')

    toe_kick_height: bpy.props.FloatProperty(name="Toe Kick Height",
                                             description="This is the default height of the toe kick.",
                                             default=pc_unit.inch(4.0),
                                             unit='LENGTH')

    toe_kick_setback: bpy.props.FloatProperty(name="Toe Kick Setback",
                                             description="This is the default setback of the toe kick.",
                                             default=pc_unit.inch(4.0),
                                             unit='LENGTH')

    add_backsplash: bpy.props.BoolProperty(name="Add Backsplash",
                                           description="Check this to include a countertop backsplash",
                                           default=True)

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

    countertop_thickness: bpy.props.FloatProperty(name="Countertop Thickness",
                                                       description="This is the thickness of countertops.",
                                                       default=pc_unit.inch(1.5),
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

classes = (
    HB_Cabinet_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)                                                                                             