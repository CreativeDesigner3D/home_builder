import os

def get_assembly_path():
    return os.path.join(os.path.dirname(__file__),'assemblies')

def get_handles_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cabinet Handles')

def get_door_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cabinet Doors')    

def get_molding_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Moldings')