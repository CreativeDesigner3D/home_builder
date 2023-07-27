import bpy
from . import types_cabinet
from . import types_cabinet_carcass
from . import types_cabinet_exteriors
from . import types_cabinet_interiors
from . import utils_cabinet
from pc_lib import pc_unit

class Base_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.base_cabinet_height 
        self.depth = props.base_cabinet_depth      
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.door_type = "Base"
        self.splitter = None
        self.include_countertop = True

# class Base_1_Door(types_cabinet.Geo_Cabinet):
    
#     def __init__(self):
#         props = utils_cabinet.get_scene_props(bpy.context.scene)
#         self.width = props.width_1_door
#         self.height = props.base_cabinet_height 
#         self.depth = props.base_cabinet_depth      
#         self.carcass = types_cabinet_carcass.Base_Design_Carcass()
#         if props.add_shelves_to_interior:
#             self.carcass.interior = types_cabinet_interiors.Shelves()
#         self.carcass.exterior = types_cabinet_exteriors.Doors()
#         self.carcass.exterior.door_swing = 0
#         self.carcass.exterior.door_type = "Base"
#         self.splitter = None
#         self.include_countertop = True

class Base_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.door_type = "Base"
        self.include_countertop = True


class Base_Open(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = types_cabinet_interiors.Exposed_Shelves()
        self.carcass.exterior = None
        self.carcass.exposed_interior = True
        self.include_countertop = True
        

class Base_Drawer(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_drawer
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Drawers()
        self.include_countertop = True        


class Base_2_Door_2_Drawer(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Door_Drawer()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.two_drawers = True
        self.include_countertop = True      


class Base_2_Door_1_Drawer(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Door_Drawer()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.two_drawers = False
        self.include_countertop = True      


class Base_1_Door_1_Drawer(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Door_Drawer()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.two_drawers = False
        self.include_countertop = True   


class Base_Blind_1_Door(types_cabinet.Blind_Corner_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.base_width_blind
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Blind_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.door_type = "Base"
        self.include_countertop = True   


class Tall_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth   
        self.carcass = types_cabinet_carcass.Tall_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
            self.carcass.interior.shelf_qty = 3
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.door_type = "Tall"        


class Tall_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth           
        self.carcass = types_cabinet_carcass.Tall_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
            self.carcass.interior.shelf_qty = 3
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.door_type = "Tall"


class Tall_Open(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth           
        self.carcass = types_cabinet_carcass.Tall_Design_Carcass()
        self.carcass.interior = types_cabinet_interiors.Exposed_Shelves()
        self.carcass.interior.shelf_qty = 3
        self.carcass.exterior = None
        self.carcass.exposed_interior = True     


class Tall_Blind_1_Door(types_cabinet.Blind_Corner_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.tall_width_blind
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth     
        self.carcass = types_cabinet_carcass.Tall_Blind_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
            self.carcass.interior.shelf_qty = 3
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.door_type = "Tall"        


class Upper_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth                   
        self.carcass = types_cabinet_carcass.Upper_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
            self.carcass.interior.shelf_qty = 2
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.door_type = "Upper"

class Upper_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door        
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth   
        self.carcass = types_cabinet_carcass.Upper_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
            self.carcass.interior.shelf_qty = 2
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.door_type = "Upper"        


class Upper_Open(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door        
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth   
        self.carcass = types_cabinet_carcass.Upper_Design_Carcass()
        self.carcass.interior = types_cabinet_interiors.Exposed_Shelves()
        self.carcass.interior.shelf_qty = 2
        self.carcass.exterior = None
        self.carcass.exposed_interior = True


class Upper_Blind_1_Door(types_cabinet.Blind_Corner_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.upper_width_blind
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth     
        self.carcass = types_cabinet_carcass.Upper_Blind_Design_Carcass()
        if props.add_shelves_to_interior:
            self.carcass.interior = types_cabinet_interiors.Shelves()
            self.carcass.interior.shelf_qty = 2
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.door_type = "Upper"        


class Tall_Stacked(types_cabinet.Stacked_Cabinet):

    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door  
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.bottom_cabinet_height = props.tall_cabinet_height - props.stacked_top_cabinet_height
        self.top_carcass = types_cabinet_carcass.Upper_Design_Carcass()
        if props.add_shelves_to_interior:
            self.top_carcass.interior = types_cabinet_interiors.Shelves()
        self.top_carcass.exterior = types_cabinet_exteriors.Doors()
        self.top_carcass.exterior.door_swing = 0
        self.top_carcass.exterior.door_type = "Upper"        
        self.bottom_carcass = types_cabinet_carcass.Tall_Design_Carcass()
        if props.add_shelves_to_interior:
            self.bottom_carcass.interior = types_cabinet_interiors.Shelves()
            self.bottom_carcass.interior.shelf_qty = 2
        self.bottom_carcass.exterior = types_cabinet_exteriors.Doors()
        self.bottom_carcass.exterior.door_swing = 0
        self.bottom_carcass.exterior.door_type = "Tall"           
        self.is_upper = False


class Upper_Stacked(types_cabinet.Stacked_Cabinet):

    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door  
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.bottom_cabinet_height = props.upper_cabinet_height - props.stacked_top_cabinet_height
        self.top_carcass = types_cabinet_carcass.Upper_Design_Carcass()
        if props.add_shelves_to_interior:
            self.top_carcass.interior = types_cabinet_interiors.Shelves()
        self.top_carcass.exterior = types_cabinet_exteriors.Doors()
        self.top_carcass.exterior.door_swing = 2
        self.top_carcass.exterior.door_type = "Upper"
        self.bottom_carcass = types_cabinet_carcass.Upper_Design_Carcass()
        if props.add_shelves_to_interior:
            self.bottom_carcass.interior = types_cabinet_interiors.Shelves()
            self.bottom_carcass.interior.shelf_qty = 2
        self.bottom_carcass.exterior = types_cabinet_exteriors.Doors()
        self.bottom_carcass.exterior.door_swing = 2
        self.bottom_carcass.exterior.door_type = "Upper"
        self.is_upper = True


class Base_Cabinet(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Opening()
        self.carcass.exposed_interior = False
        self.include_countertop = True       


class Tall_Cabinet(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth           
        self.carcass = types_cabinet_carcass.Tall_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Opening()
        self.carcass.exposed_interior = False      


class Upper_Cabinet(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door        
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth   
        self.carcass = types_cabinet_carcass.Upper_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Opening()
        self.carcass.exposed_interior = False            