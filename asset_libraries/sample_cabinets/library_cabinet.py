import bpy
from . import types_cabinet
from . import types_cabinet_carcass
from . import types_cabinet_exteriors
from . import utils_cabinet
from pc_lib import pc_unit

class Base_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.base_cabinet_height 
        self.depth = props.base_cabinet_depth      
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.splitter = None


class Base_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door
        self.height = props.base_cabinet_height   
        self.depth = props.base_cabinet_depth     
        self.carcass = types_cabinet_carcass.Base_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.splitter = None


class Tall_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth   
        self.carcass = types_cabinet_carcass.Tall_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.splitter = None


class Tall_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door
        self.height = props.tall_cabinet_height   
        self.depth = props.tall_cabinet_depth           
        self.carcass = types_cabinet_carcass.Tall_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.splitter = None        


class Upper_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_1_door
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth                   
        self.carcass = types_cabinet_carcass.Upper_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.splitter = None


class Upper_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        props = utils_cabinet.get_scene_props(bpy.context.scene)
        self.width = props.width_2_door        
        self.height = props.upper_cabinet_height   
        self.depth = props.upper_cabinet_depth   
        self.carcass = types_cabinet_carcass.Upper_Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.splitter = None            