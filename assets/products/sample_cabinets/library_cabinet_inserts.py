from . import types_cabinet_inserts
from . import types_cabinet_exteriors

class Adj_Shelves(types_cabinet_inserts.Shelves):

    def __init__(self):
        pass    


class Hanging_Rod(types_cabinet_inserts.Hanging_Rod):

    def __init__(self):
        pass        


class Double_Hang(types_cabinet_inserts.Hanging_Rod):

    def __init__(self):
        self.is_double = True        


class Slanted_Shoe_Shelf(types_cabinet_inserts.Slanted_Shoe_Shelf):

    def __init__(self):
        pass


class Cubbies(types_cabinet_inserts.Cubbies):

    def __init__(self):
        pass        


class Doors_Base(types_cabinet_exteriors.Doors):

    def __init__(self):
        self.door_type = "Base"      


class Doors_Tall(types_cabinet_exteriors.Doors):

    def __init__(self):
        self.door_type = "Tall"          


class Doors_Upper(types_cabinet_exteriors.Doors):

    def __init__(self):
        self.door_type = "Upper"                  


class Drawers(types_cabinet_exteriors.Drawers):

    def __init__(self):
        pass            


class Single_Fixed_Shelf(types_cabinet_inserts.Vertical_Splitter):

    def __init__(self):
        self.splitter_qty = 1


class Wire_Baskets(types_cabinet_inserts.Wire_Baskets):

    def __init__(self):
        pass             


class Wine_Rack(types_cabinet_inserts.Wine_Rack):

    def __init__(self):
        pass             


class Division_1(types_cabinet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 1


class Division_2(types_cabinet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 2


class Division_3(types_cabinet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 3      


class Division_4(types_cabinet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 4                  