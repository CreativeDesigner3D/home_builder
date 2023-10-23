import bpy
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        )

from .. import pyclone_utils
from pc_lib import pc_utils, pc_types

class VIEW3D_PT_pc_layout_view(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"
    bl_label = "Layout Views"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='SCENE')

    def draw_camera_settings(self,context,layout):
        scene = context.scene
        rd = scene.render
        view = context.space_data
        wm_props = context.window_manager.pyclone
        scene_props = pyclone_utils.get_scene_props(scene)

        box = layout.box()
        box.label(text="Layout View Tools")
        row = box.row()
        row.operator('pc_layout_view.draw_geo_node_dimension',text="Plan Dimension",icon='DRIVER_DISTANCE')          
        row.operator('pc_layout_view.add_elevation_dimension',text="Elevation Dimension",icon='DRIVER_DISTANCE')

        box = layout.box()

        row = box.row()
        row.label(text="Layout View List")
        row.menu('VIEW3D_MT_layout_view_creation',text="Add View",icon='ADD')
        box.template_list("PC_UL_scenes"," ", bpy.data, "scenes", wm_props, "scene_index",rows=5,type='DEFAULT')

        if scene_props.is_view_scene:
            row = box.row(align=True)
            row.scale_y = 1.3   
            row.operator('render.render',text="Render",icon='SCENE').use_viewport=True         
            row.operator('pc_assembly.create_pdf_of_assembly_views',text="Create PDF",icon='FILE_BLANK')
            
            box = layout.box()
            box.label(text="Page Setup",icon='FILE')
            row = box.row()
            row.label(text="Page Size")
            row.prop(scene_props,'page_size',text="")

            row = box.row()
            row.label(text="Drawing Scale")        
            row.prop(scene_props,'numeric_page_scale',text="")

            box = layout.box()
            box.label(text="Render Settings",icon='IMAGE_DATA')
            row = box.row()
            # row.label(text="Render Lines") 
            row.prop(rd, "use_freestyle", text="Render Lines")     
            if rd.use_freestyle:
                    if 'Visible Lines' in bpy.data.linestyles:
                        vl = bpy.data.linestyles['Visible Lines']
                        hl = bpy.data.linestyles['Hidden Lines']
                        row = box.row()
                        row.label(text="Line Thickness")
                        row.prop(vl,'thickness',text="Visible")  
                        row.prop(hl,'thickness',text="Hidden") 
            row = box.row()
            # row.label(text="Transparent Background") 
            row.prop(rd, "film_transparent", text="Transparent Background") 

            box = layout.box()
            box.label(text='Camera Properties',icon='CAMERA_DATA')
            box.prop(view, "lock_camera")


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render

        scene_props = pyclone_utils.get_scene_props(scene)

        self.draw_camera_settings(context,layout)

        obj = context.object
        if obj:
            obj_props = pyclone_utils.get_object_props(obj)
            if obj_props.is_view_object:
                # layout.prop(obj,'name')

                if obj.type == 'CAMERA':
                    pass

                if obj.type == 'EMPTY':
                    pass


class VIEW3D_MT_layout_view_creation(bpy.types.Menu):
    bl_label = "Layout View Creation Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator('pc_layout_view.create_3d_view',text="Add Current 3D View",icon='MENU_PANEL')
        layout.operator('pc_layout_view.create_2d_plan_view',text="Add 2D Plan View",icon='MENU_PANEL')
        layout.operator('pc_layout_view.create_2d_elevation_views',text="Add 2D Elevation Views",icon='MENU_PANEL')

classes = (
    VIEW3D_PT_pc_layout_view,
    VIEW3D_MT_layout_view_creation,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        