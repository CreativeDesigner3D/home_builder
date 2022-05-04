import bpy
import os
from . import hb_utils

class HOME_BUILDER_PT_library(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Home Builder"
    bl_category = "Home Builder"    
    bl_options = {'HIDE_HEADER'}

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
        layout = self.layout
        scene = context.scene
        hb_scene = scene.home_builder
        
        wm = context.window_manager        
        wm_props = wm.home_builder
        library = hb_utils.get_active_library(context)
        main_box = layout.box()

        row = main_box.row()
        row.label(text="Home Builder",icon='HOME')
        row.operator('home_builder.about_home_builder',text="Settings",icon='PREFERENCES')

        col = main_box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.prop_enum(hb_scene, "library_tabs", 'ROOMS') 
        row.prop_enum(hb_scene, "library_tabs", 'APPLIANCES') 
        row.prop_enum(hb_scene, "library_tabs", 'CABINETS') 
        row.prop_enum(hb_scene, "library_tabs", 'BUILD')
        row = col.row(align=True)
        row.scale_y = 1.2
        row.prop_enum(hb_scene, "library_tabs", 'FIXTURES') 
        row.prop_enum(hb_scene, "library_tabs", 'DECORATIONS') 
        row.prop_enum(hb_scene, "library_tabs", 'MATERIALS') 

        if hb_scene.library_tabs == 'ROOMS':
            col = main_box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop_enum(hb_scene, "room_tabs", 'WALLS', icon='MOD_BUILD') #MOD_EDGESPLIT
            row.prop_enum(hb_scene, "room_tabs", 'DOORS_WINDOWS', icon='MESH_GRID')
            if hb_scene.room_tabs == 'WALLS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3
                row.operator('home_builder.draw_multiple_walls',text="DRAW WALL",icon='GREASEPENCIL')

                col.separator()
                box = col.box()
                box.use_property_split = True
                box.use_property_decorate = False
                box.label(text="Wall Settings")
                box.prop(hb_scene,'wall_height')
                box.prop(hb_scene,'wall_thickness')
            
            if hb_scene.room_tabs == 'DOORS_WINDOWS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_door_window_library',text=library.name)                
                self.draw_library(col,context,library)
     
        if hb_scene.library_tabs == 'DECORATIONS':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_decorations',text=library.name)

            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'CABINETS':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_cabinets',text=library.name)  
            if library.library_menu_ui != '':
                row.menu(library.library_menu_ui,text="",icon='SETTINGS')
            
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'APPLIANCES':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_appliances',text=library.name)  
            if library.library_menu_ui != '':
                row.menu(library.library_menu_ui,text="",icon='SETTINGS')
            
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'FIXTURES':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_fixtures_library',text=library.name)
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'MATERIALS':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_materials_library',text=library.name)   
            row.menu('HOME_BUILDER_MT_materials_pointers',text="",icon='SETTINGS')         
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'BUILD':
            col = main_box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop_enum(hb_scene, "build_tabs", 'STARTERS') 
            row.prop_enum(hb_scene, "build_tabs", 'INSERTS')                  
            row.prop_enum(hb_scene, "build_tabs", 'PARTS') 

            if hb_scene.build_tabs == 'STARTERS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_starters_library',text=library.name)  
                self.draw_library(col,context,library)

            if hb_scene.build_tabs == 'INSERTS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_inserts_library',text=library.name)  
                if library.library_menu_ui != '':
                    row.menu(library.library_menu_ui,text="",icon='SETTINGS')
                
                self.draw_library(col,context,library)

            if hb_scene.build_tabs == 'PARTS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_parts_library',text=library.name)  
                if library.library_menu_ui != '':
                    row.menu(library.library_menu_ui,text="",icon='SETTINGS')
                self.draw_library(col,context,library)

class HOME_BUILDER_MT_door_window_library(bpy.types.Menu):
    bl_label = "Door Window Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'DOOR_WINDOWS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_cabinets(bpy.types.Menu):
    bl_label = "Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'CABINETS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_appliances(bpy.types.Menu):
    bl_label = "Appliance Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'APPLIANCES' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_decorations(bpy.types.Menu):
    bl_label = "Decoration Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'DECORATIONS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path                     

class HOME_BUILDER_MT_fixtures_library(bpy.types.Menu):
    bl_label = "Fixtures Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'FIXTURES' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_starters_library(bpy.types.Menu):
    bl_label = "Starters Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'STARTERS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_inserts_library(bpy.types.Menu):
    bl_label = "Insert Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'INSERTS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_parts_library(bpy.types.Menu):
    bl_label = "Part Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'PARTS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_materials_library(bpy.types.Menu):
    bl_label = "Materials Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'MATERIALS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_materials_pointers(bpy.types.Menu):
    bl_label = "Materials Libraries"

    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.home_builder
        library_names = []

        for pointer in scene_props.material_pointers:
            if pointer.library_name not in library_names:
                library_names.append(pointer.library_name)

        for library in library_names:
            layout.operator('home_builder.show_library_material_pointers',text=library).library_name = library


classes = (
    HOME_BUILDER_PT_library,
    HOME_BUILDER_MT_door_window_library,
    HOME_BUILDER_MT_cabinets,
    HOME_BUILDER_MT_appliances,
    HOME_BUILDER_MT_decorations,
    HOME_BUILDER_MT_fixtures_library,
    HOME_BUILDER_MT_starters_library,
    HOME_BUILDER_MT_inserts_library,
    HOME_BUILDER_MT_parts_library,
    HOME_BUILDER_MT_materials_library,
    HOME_BUILDER_MT_materials_pointers,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
