import bpy

def draw_layout_view_commands(self,context):
    layout = self.layout
    layout.operator('hb_sample_cabinets.create_2d_plan_view')
    layout.operator('hb_sample_cabinets.create_2d_elevation_views')


def register():
    bpy.types.VIEW3D_MT_layout_view_creation.append(draw_layout_view_commands)

def unregister():    
    bpy.types.VIEW3D_MT_layout_view_creation.remove(draw_layout_view_commands)