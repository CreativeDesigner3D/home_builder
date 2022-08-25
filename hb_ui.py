import bpy
import os
from pc_lib import pc_utils
from . import hb_utils

class HOME_BUILDER_PT_library(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Home Builder"
    bl_category = "Home Builder"    
    bl_options = {'HIDE_HEADER'}

    def draw_library(self,layout,context,library):
        if library:
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
        else:
            layout.separator()
            layout.operator('home_builder.load_library')

    def draw_custom_library(self,layout,context,library):
        if library:
            workspace = context.workspace
            wm = context.window_manager        
            activate_id = "home_builder.todo"
            drop_id = "home_builder.place_custom_cabinet"
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
        else:
            layout.separator()
            layout.operator('home_builder.load_library')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hb_scene = scene.home_builder
        
        wm = context.window_manager        
        wm_props = wm.home_builder
        library = wm_props.get_active_library(context)
        if library:
            library_name = library.name
            library_menu_id = library.library_menu_ui
        else:
            library_name = "None"
            library_menu_id = ""

        main_box = layout.box()

        row = main_box.row()
        row.label(text="Home Builder",icon='HOME')
        row.operator('home_builder.about_home_builder',text="About",icon='INFO')

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
                row.menu('HOME_BUILDER_MT_door_window_library',text=library_name)                
                self.draw_library(col,context,library)
                if library_menu_id != '':
                    row.menu(library_menu_id,text="",icon='SETTINGS')                
     
        if hb_scene.library_tabs == 'DECORATIONS':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_decorations',text=library_name)

            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'CABINETS':
            col = main_box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop_enum(hb_scene, "cabinet_tabs", 'CATALOGS',icon='ASSET_MANAGER') 
            row.prop_enum(hb_scene, "cabinet_tabs", 'CUSTOM',icon='TOOL_SETTINGS')       
            col.separator()
            if hb_scene.cabinet_tabs == 'CATALOGS':
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_cabinets',text=library_name)                  
                if library_menu_id != '':
                    row.menu(library_menu_id,text="",icon='SETTINGS')
                
                self.draw_library(col,context,library)

            else:
                if context.object:
                    obj_bp = pc_utils.get_bp_by_tag(context.object,'IS_ASSEMBLY_BP')
                    if obj_bp:
                        box = col.box()
                        if library:
                            row = box.row()
                            row.scale_y = 1.3
                            row.operator('home_builder.save_custom_cabinet',text="Save " + obj_bp.name,icon='PASTEDOWN') 
                            row.operator('pc_assembly.select_parent',text="",icon='SORT_DESC')
                        else:
                            row = box.row()
                            row.operator('home_builder.create_new_custom_library_category',text="Create Library Category",icon='ADD')                          
                    else:
                        box = col.box()
                        row = box.row()
                        row.label(text='No Assembly Selected')   
                else:
                    box = col.box()
                    row = box.row()
                    row.label(text='No Assembly Selected')  

                col.separator()                                           
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_custom_cabinets',text=library_name)
                row.operator('home_builder.create_new_custom_library_category',text="",icon='ADD')

                self.draw_custom_library(col,context,library)

        if hb_scene.library_tabs == 'APPLIANCES':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_appliances',text=library_name)  
            if library_menu_id != '':
                row.menu(library_menu_id,text="",icon='SETTINGS')
            
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'FIXTURES':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_fixtures_library',text=library_name)
            if library_menu_id != '':
                row.menu(library_menu_id,text="",icon='SETTINGS')            
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'MATERIALS':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.3                 
            row.menu('HOME_BUILDER_MT_materials_library',text=library_name)   
            row.menu('HOME_BUILDER_MT_materials_pointers',text="",icon='SETTINGS')         
            self.draw_library(col,context,library)

        if hb_scene.library_tabs == 'BUILD':
            col = main_box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop_enum(hb_scene, "build_tabs", 'STARTERS',icon='MOD_LINEART') 
            row.prop_enum(hb_scene, "build_tabs", 'INSERTS',icon='CON_SAMEVOL')                  
            row.prop_enum(hb_scene, "build_tabs", 'PARTS',icon='SNAP_FACE') 

            if hb_scene.build_tabs == 'STARTERS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_starters_library',text=library_name) 
                if library_menu_id != '':
                    row.menu(library_menu_id,text="",icon='SETTINGS')                 
                self.draw_library(col,context,library)

            if hb_scene.build_tabs == 'INSERTS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_inserts_library',text=library_name)  
                if library_menu_id != '':
                    row.menu(library_menu_id,text="",icon='SETTINGS')
                
                self.draw_library(col,context,library)

            if hb_scene.build_tabs == 'PARTS':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.3                 
                row.menu('HOME_BUILDER_MT_parts_library',text=library_name)  
                if library_menu_id != '':
                    row.menu(library_menu_id,text="",icon='SETTINGS')
                self.draw_library(col,context,library)

class HOME_BUILDER_MT_home_builder_menu(bpy.types.Menu):
    bl_label = "Home Builder"

    def draw(self, _context):
        layout = self.layout
        layout.operator('home_builder.unit_settings',text="Change Units",icon='SETTINGS')

class HOME_BUILDER_MT_door_window_library(bpy.types.Menu):
    bl_label = "Door Window Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.asset_libraries:
            if library.library_type == 'DOORS_WINDOWS' and library.enabled:
                props = layout.operator('home_builder.update_library_path',text=library.name).asset_path = library.library_path  

class HOME_BUILDER_MT_custom_cabinets(bpy.types.Menu):
    bl_label = "Custom Cabinet Libraries"

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.home_builder
        for library in props.custom_asset_libraries:
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
    HOME_BUILDER_MT_custom_cabinets,
    HOME_BUILDER_MT_cabinets,
    HOME_BUILDER_MT_appliances,
    HOME_BUILDER_MT_decorations,
    HOME_BUILDER_MT_fixtures_library,
    HOME_BUILDER_MT_starters_library,
    HOME_BUILDER_MT_inserts_library,
    HOME_BUILDER_MT_parts_library,
    HOME_BUILDER_MT_materials_library,
    HOME_BUILDER_MT_materials_pointers,
    HOME_BUILDER_MT_home_builder_menu,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
