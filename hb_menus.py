import bpy

def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def register():
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder)

def unregister():    
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)