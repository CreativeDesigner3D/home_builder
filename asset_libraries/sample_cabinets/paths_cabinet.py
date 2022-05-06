import os

def get_assembly_path():
    return os.path.join(os.path.dirname(__file__),'assemblies')

def get_pull_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cabinet Pulls')

def get_door_paths():
    return os.path.join(os.path.dirname(__file__),'cabinet_assets','Cabinet Doors')    