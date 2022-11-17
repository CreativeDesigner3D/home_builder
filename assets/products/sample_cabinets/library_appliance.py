from . import types_appliances

class Refrigerator(types_appliances.Refrigerator):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)

class Range(types_appliances.Range):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)        

class Dishwasher(types_appliances.Dishwasher):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)              