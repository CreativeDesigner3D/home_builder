from . import types_closet_inserts
from . import types_cabinet_exteriors

class Adj_Shelves(types_closet_inserts.Shelves):

    def __init__(self):
        pass    


class Hanging_Rod(types_closet_inserts.Hanging_Rod):

    def __init__(self):
        pass        


class Double_Hang(types_closet_inserts.Hanging_Rod):

    def __init__(self):
        self.is_double = True        


class Slanted_Shoe_Shelf(types_closet_inserts.Slanted_Shoe_Shelf):

    def __init__(self):
        pass


class Cubbies(types_closet_inserts.Cubbies):

    def __init__(self):
        pass        


class Base_Doors(types_cabinet_exteriors.Doors):

    def __init__(self):
        self.door_type = "Base"      


class Tall_Doors(types_cabinet_exteriors.Doors):

    def __init__(self):
        self.door_type = "Tall"          


class Upper_Doors(types_cabinet_exteriors.Doors):

    def __init__(self):
        self.door_type = "Upper"                  


class Drawers(types_cabinet_exteriors.Drawers):

    def __init__(self):
        pass            


class Wire_Baskets(types_closet_inserts.Wire_Baskets):

    def __init__(self):
        pass             


class Division_1(types_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 1


class Division_2(types_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 2


class Division_3(types_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 3      


class Division_4(types_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 4                  