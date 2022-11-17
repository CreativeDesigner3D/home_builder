from . import types_closet_starters

class Tall_Starter(types_closet_starters.Closet_Starter):

    def __init__(self):
        self.is_hanging = False

class Hanging_Starter(types_closet_starters.Closet_Starter):

    def __init__(self):
        self.is_hanging = True

class Base_Starter(types_closet_starters.Closet_Starter):

    def __init__(self,obj_bp=None):
        self.is_hanging = False
        self.is_base = True

class Tall_L_Shelves(types_closet_starters.Closet_Inside_Corner):

    def __init__(self):
        self.is_inside_corner = True

class Hanging_L_Shelves(types_closet_starters.Closet_Inside_Corner):

    def __init__(self):
        self.is_inside_corner = True
        self.is_hanging = True

class Corner_Filler(types_closet_starters.Closet_Inside_Corner_Filler):

    def __init__(self):
        self.is_inside_corner = True        