import bpy
from pc_lib import pc_utils

class HOME_BUILDER_MT_wall_commands(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        wall_bp = pc_utils.get_bp_by_tag(context.object,'IS_WALL_BP')
        layout = self.layout
        layout.operator('home_builder.edit_part',text="Edit Wall",icon='EDITMODE_HLT')
        layout.operator('home_builder.add_wall_length_dimension',text="Add Wall Length Dimension",icon='DRIVER_DISTANCE').wall_bp_name = wall_bp.name
        layout.operator('home_builder.select_room_base_point',text="Select Room Base Point",icon='EMPTY_DATA').wall_bp_name = wall_bp.name
        layout.separator()
        layout.operator('home_builder.delete_wall',text="Delete Wall",icon='X').wall_obj_bp_name = wall_bp.name


def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def register():
    bpy.utils.register_class(HOME_BUILDER_MT_wall_commands)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder)

def unregister():    
    bpy.utils.unregister_class(HOME_BUILDER_MT_wall_commands)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)