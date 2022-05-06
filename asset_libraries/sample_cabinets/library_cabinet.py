from . import types_cabinet
from . import types_cabinet_exteriors
from pc_lib import pc_unit

class Base_1_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        self.carcass = types_cabinet.Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.splitter = None
        self.cabinet_type = "Base"

class Base_2_Door(types_cabinet.Standard_Cabinet):
    
    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = types_cabinet.Design_Carcass()
        self.carcass.interior = None
        self.carcass.exterior = types_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.splitter = None
        self.cabinet_type = "Base"   