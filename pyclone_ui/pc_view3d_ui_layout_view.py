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
from ..pc_lib import pc_utils, pc_types

class VIEW3D_PT_pc_layout_view(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layout View"
    bl_label = "Layout View"
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return True
        # for scene in bpy.data.scenes:
        #     props = pyclone_utils.get_scene_props(scene)
        #     if props.is_view_scene:
        #         return True
        # return False

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="",icon='SCENE')

    def draw_camera_settings(self,context,layout):
        scene = context.scene
        rd = scene.render
        wm_props = context.window_manager.pyclone
        scene_props = pyclone_utils.get_scene_props(scene)
        box = layout.box()

        box.label(text="Layout View List")
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
            row.label(text="Page Scale Unit")
            row.prop(scene_props,'page_scale_unit_type',text="")

            row = box.row()
            row.label(text="Drawing Scale")            
            # row.prop(scene_props,'fit_to_paper',text="Fit to Paper")
            if not scene_props.fit_to_paper:
                if scene_props.page_scale_unit_type == 'METRIC':
                    row.prop(scene_props,'metric_page_scale',text="")
                else:
                    row.prop(scene_props,'imperial_page_scale',text="")
            row = box.row()
            row.label(text="Print Style")                   
            row.prop(scene_props,'page_style',text="")
            row = box.row()
            row.label(text="Render Lines") 
            row.prop(rd, "use_freestyle", text="")            
            row = box.row()
            row.label(text="Transparent Background") 
            row.prop(rd, "film_transparent", text="")    

            #CREATE VIEW OF ASSEMBLY    
            box = layout.box()
            box.label(text="Create View",icon='SEQ_PREVIEW')    
            row = box.row()        
            row.operator('pc_assembly.create_assembly_view',text="Top",icon='AXIS_TOP').view = 'TOP'
            row.operator('pc_assembly.create_assembly_view',text="Front",icon='FACESEL').view = 'FRONT'
            row.operator('pc_assembly.create_assembly_view',text="Side",icon='AXIS_SIDE').view = 'SIDE'

            #ADD DIMENSION ADD ANNOTATION
            box = layout.box()
            box.label(text="Dimensions and Annotations",icon='DRIVER_DISTANCE')               
            box.operator('pc_assembly.create_assembly_dimension',text="Add Dimension",icon='TRACKING_FORWARDS_SINGLE')
            box.operator('pc_assembly.add_add_annotation',text="Add Annotation",icon='CON_ROTLIMIT')
            box.operator('pc_assembly.add_title_block',text="Add Title Block",icon='MENU_PANEL')

        else:
            box = layout.box()
            box.operator('pc_assembly.create_render_view',text="Add Render View",icon='MENU_PANEL')


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


classes = (
    VIEW3D_PT_pc_layout_view,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()        