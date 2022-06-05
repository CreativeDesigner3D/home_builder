from . import types_closet_inserts

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


class Base_Doors(types_closet_inserts.Base_Doors):

    def __init__(self):
        pass        


class Tall_Doors(types_closet_inserts.Tall_Doors):

    def __init__(self):
        pass        


class Upper_Doors(types_closet_inserts.Upper_Doors):

    def __init__(self):
        pass                


class Drawers(types_closet_inserts.Drawers):

    def __init__(self):
        pass            


class Single_Drawer(types_closet_inserts.Single_Drawer):

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