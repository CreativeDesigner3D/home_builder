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