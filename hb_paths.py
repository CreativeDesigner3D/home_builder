import os

def get_built_in_asset_path():
    return os.path.join(os.path.dirname(__file__),'assets')

def get_build_library_path():
    return os.path.join(get_built_in_asset_path(),'build_library')

def get_decoration_library_path():
    return os.path.join(get_built_in_asset_path(),'decorations')

def get_material_library_path():
    return os.path.join(get_built_in_asset_path(),'materials')

def get_product_library_path():
    return os.path.join(get_built_in_asset_path(),'products')