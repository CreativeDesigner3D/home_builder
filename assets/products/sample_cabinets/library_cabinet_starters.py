from . import types_cabinet_starters

class Base_Openings(types_cabinet_starters.Closet_Starter):

    def __init__(self,obj_bp=None):
        self.is_hanging = False
        self.is_base = True

class Tall_Openings(types_cabinet_starters.Closet_Starter):

    def __init__(self):
        self.is_hanging = False

class Upper_Openings(types_cabinet_starters.Closet_Starter):

    def __init__(self):
        self.is_hanging = True

class Base_Corner_Pie_Cut(types_cabinet_starters.Closet_Inside_Corner):

    def __init__(self):
        self.is_inside_corner = True
        self.is_base = True

class Tall_Corner_Pie_Cut(types_cabinet_starters.Closet_Inside_Corner):

    def __init__(self):
        self.is_inside_corner = True

class Upper_Corner_Pie_Cut(types_cabinet_starters.Closet_Inside_Corner):

    def __init__(self):
        self.is_inside_corner = True
        self.is_hanging = True

class Base_Corner_Filler(types_cabinet_starters.Closet_Inside_Corner_Filler):

    def __init__(self):
        self.is_base = True
        self.is_inside_corner = True

class Tall_Corner_Filler(types_cabinet_starters.Closet_Inside_Corner_Filler):

    def __init__(self):
        self.is_inside_corner = True       

class Upper_Corner_Filler(types_cabinet_starters.Closet_Inside_Corner_Filler):

    def __init__(self):
        self.is_hanging = True
        self.is_inside_corner = True                       