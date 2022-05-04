import bpy

class HOME_BUILDER_MT_cabinet_settings(bpy.types.Menu):
    bl_label = "Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        layout.popover(panel="HOME_BUILDER_PT_cabinet_sizes",text="Cabinet Sizes",icon='DRIVER_DISTANCE')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_sizes",text="Cabinet Construction",icon='MODIFIER_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_materials",text="Cabinet Materials",icon='MATERIAL_DATA')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_sizes",text="Cabinet Fronts",icon='SNAP_FACE')
        layout.popover(panel="HOME_BUILDER_PT_cabinet_sizes",text="Cabinet Moldings",icon='IPO_CONSTANT')
        layout.separator()
        layout.operator('hb_sample_cabinets.build_library',text="Build Cabinet Library")


class HOME_BUILDER_PT_cabinet_sizes(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Sizes"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 32

    def draw(self, context):
        layout = self.layout
        layout.label(text="Cabinet Sizes")
        

class HOME_BUILDER_PT_cabinet_materials(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Cabinet Materials"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 16

    def draw_library(self,layout,context,library):
        workspace = context.workspace
        wm = context.window_manager        
        activate_id = "home_builder.todo"
        drop_id = "home_builder.todo"
        if library.activate_id != "":
            activate_id = library.activate_id
        if library.drop_id != "":
            drop_id = library.drop_id

        activate_op_props, drag_op_props = layout.template_asset_view(
            "home_builder_library",
            workspace,
            "asset_library_ref",
            wm.home_builder,
            "home_builder_library_assets",
            workspace.home_builder,
            "home_builder_library_index",
            # filter_id_types={"filter_object"},
            display_options={'NO_LIBRARY'},
            # display_options={'NO_FILTER','NO_LIBRARY'},
            activate_operator=activate_id,
            drag_operator=drop_id,            
        )

    def draw(self, context):
        wm = context.window_manager        
        wm_props = wm.home_builder      
        lib = wm_props.asset_libraries["Wood Finished"]  
        layout = self.layout
        layout.label(text="Cabinet Material Library")
        # for material_pointer in lib.material_pointers:
        #     layout.label(text=material_pointer.name + " - " + material_pointer.library_path + " - " + material_pointer.material_name)

        self.draw_library(layout,context,lib)

classes = (
    HOME_BUILDER_MT_cabinet_settings,
    HOME_BUILDER_PT_cabinet_sizes,
    HOME_BUILDER_PT_cabinet_materials,
)

register, unregister = bpy.utils.register_classes_factory(classes)          