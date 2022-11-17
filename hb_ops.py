import bpy
import os
import time
import math
import inspect
import sys
import codecs
import subprocess
from pc_lib import pc_utils, pc_unit, pc_types
from . import addon_updater_ops
from . import hb_utils
from . import pyclone_utils
from . import hb_utils
from . import hb_paths
from .walls import wall_library

class home_builder_OT_about_home_builder(bpy.types.Operator):
    bl_idname = "home_builder.about_home_builder"
    bl_label = "About Home Builder"
    bl_description = "Show the about home builder interface"

    tabs: bpy.props.EnumProperty(name="Library Tabs",
                       items=[('VERSION',"Version","Show the Home Builder Version"),
                              ('INSTALLED_LIBRARIES',"Installed Libraries","Show the Installed Libraries"),
                              ('TRAINING',"Training","Show the Training Videos")],
                       default='VERSION')

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def execute(self, context):  
        return {'FINISHED'}

    def get_library_icon(self,library):
        if library.library_type == 'DOORS_WINDOWS':
            return  'MESH_GRID'
        if library.library_type == 'PRODUCTS':
            return  'META_CUBE'
        if library.library_type == 'DECORATIONS':
            return  'SCENE_DATA'
        if library.library_type == 'STARTERS':
            return  'STICKY_UVS_LOC'
        if library.library_type == 'INSERTS':
            return  'STICKY_UVS_VERT'
        if library.library_type == 'PARTS':
            return  'STICKY_UVS_DISABLE'
        if library.library_type == 'BUILD_LIBRARY':
            return  'USER'            
        if library.library_type == 'MATERIALS':
            return  'MATERIAL_DATA'
        return 'BLANK1'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager        
        wm_props = wm.home_builder
        
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop_enum(self, "tabs", 'VERSION',icon='INFO')
        row.prop_enum(self, "tabs", 'INSTALLED_LIBRARIES',icon='ASSET_MANAGER')
        row.prop_enum(self, "tabs", 'TRAINING',icon='QUESTION')

        if self.tabs == 'VERSION':
            main_box = layout.box()
            version = hb_utils.addon_version
            row = main_box.row()
            row.label(text="Home Builder Version " + str(version[0]) + "." + str(version[1])+ "." + str(version[2]) + " (BETA)")
            if addon_updater_ops.updater.update_ready == True:
                row.separator()
                addon_updater_ops.update_notice_box_ui(self,context,row)        
            else:
                row.separator()
                row.operator('home_builder.updater_check_now',text="Check for Updates",icon='FILE_REFRESH')

        if self.tabs == 'INSTALLED_LIBRARIES':
            main_box = layout.box()
            row = main_box.row()
            row.label(text="Installed Libraries")
            row.label(text=" ")
            row.operator('home_builder.add_external_library',text="Add Library",icon='IMPORT')
            
            row = main_box.row()
            row.alignment = 'LEFT'
            row.prop(wm_props,'show_built_in_asset_libraries',text="Built-In Libraries",icon='DISCLOSURE_TRI_DOWN' if wm_props.show_built_in_asset_libraries else 'DISCLOSURE_TRI_RIGHT',emboss=False)
            if wm_props.show_built_in_asset_libraries:
                col = main_box.column(align=True)
                for lib in wm_props.asset_libraries:
                    row = col.row()
                    print(lib.library_type)
                    row.label(text="",icon=self.get_library_icon(lib))
                    row.prop(lib,'enabled',text=lib.name)

            for ex_lib in wm_props.library_packages:
                row = main_box.row()
                if os.path.exists(ex_lib.package_path):
                    dir_name = os.path.dirname(ex_lib.package_path) 
                    folder_name = os.path.basename(dir_name)                    
                    row.alignment = 'LEFT'
                    row.prop(ex_lib,'expand',text="",icon='DISCLOSURE_TRI_DOWN' if ex_lib.expand else 'DISCLOSURE_TRI_RIGHT',emboss=False)
                    row.prop(ex_lib,'enabled',text=folder_name)
                else:
                    row.prop(ex_lib,'expand',text="",icon='DISCLOSURE_TRI_DOWN' if ex_lib.expand else 'DISCLOSURE_TRI_RIGHT',emboss=False)
                    row.prop(ex_lib,'enabled',text="")
                    row.prop(ex_lib,'package_path',text="Set Path")
                if ex_lib.expand:
                    row = main_box.row()
                    row.label(text="",icon='BLANK1')
                    row.prop(ex_lib,'package_path',text="Set Path")

        if self.tabs == 'TRAINING':
            main_box = layout.box()
            main_box.label(text="TODO: Training Videos Comming Soon")


class home_builder_OT_update_library_xml(bpy.types.Operator):
    bl_idname = "home_builder.update_library_xml"
    bl_label = "Update Library XMl"
    bl_description = "This updates the library xml that stores information about what libraries are active"

    def execute(self, context):
        wm_props = context.window_manager.home_builder
        file_path = hb_utils.get_library_path_xml()
        xml = pc_types.HB_XML()
        root = xml.create_tree()
        paths = xml.add_element(root,'LibraryPaths')
        packages = xml.add_element(paths,'Packages')
        for ex_lib in wm_props.library_packages:
            if os.path.exists(ex_lib.package_path):
                lib_package = xml.add_element(packages,'Package',ex_lib.package_path)
                xml.add_element_with_text(lib_package,'Enabled',str(ex_lib.enabled))

        xml.write(file_path)
        return {'FINISHED'}


class home_builder_OT_todo(bpy.types.Operator):
    bl_idname = "home_builder.todo"
    bl_label = "TODO"
    bl_description = "This command has not been implemented yet"

    def execute(self, context):
        print("NOT IMPLEMENTED: TODO")
        return {'FINISHED'}


class home_builder_OT_load_library(bpy.types.Operator):
    bl_idname = "home_builder.load_library"
    bl_label = "Reload Library"

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def execute(self, context):
        hb_utils.load_libraries(context)
        hb_utils.load_custom_driver_functions()
        return {'FINISHED'}

    def draw(self, context):
        prefs = context.preferences
        paths = prefs.filepaths

        layout = self.layout
        layout.label(text="Auto Run Python Scripts needs to be enabled for Home Builder Library Data.")
        layout.label(text="Check the box below and click OK to continue.")
        layout.prop(paths, "use_scripts_auto_execute")


class home_builder_OT_add_external_library(bpy.types.Operator):
    bl_idname = "home_builder.add_external_library"
    bl_label = "Add External Library"
    bl_description = "Add a new library"

    def execute(self, context):
        wm_props = context.window_manager.home_builder
        lib = wm_props.library_packages.add()
        return {'FINISHED'}


class home_builder_OT_update_library_path(bpy.types.Operator):
    bl_idname = "home_builder.update_library_path"
    bl_label = "Update Library Path"
    bl_description = "Change the active library category"

    asset_type: bpy.props.StringProperty(name="Asset Type")
    asset_path: bpy.props.StringProperty(name="Asset Path")
    asset_folder: bpy.props.StringProperty(name="Asset Path")

    def execute(self, context):
        wm_props = context.window_manager.home_builder
        scene_props = context.scene.home_builder

        sel_library = None

        for library in wm_props.asset_libraries:
            if library.library_path == self.asset_path:
                sel_library = library
                break

        prefs = context.preferences
        asset_lib = prefs.filepaths.asset_libraries.get("home_builder_library")  

        if scene_props.library_tabs == 'PRODUCTS':
            wm_props.active_product_library_name = sel_library.name

        if scene_props.library_tabs == 'BUILD':
            if scene_props.build_tabs == 'STARTERS':
                wm_props.active_starter_library_name = sel_library.name
            if scene_props.build_tabs == 'INSERTS':
                wm_props.active_insert_library_name = sel_library.name
            if scene_props.build_tabs == 'PARTS':
                wm_props.active_part_library_name = sel_library.name
            if scene_props.build_tabs == 'LIBRARY':
                wm_props.active_build_library_name = sel_library.name

        if scene_props.library_tabs == 'DECORATIONS':
            wm_props.active_decorations_library_name = sel_library.name
            
        if scene_props.library_tabs == 'MATERIALS':
            wm_props.active_materials_library_name = sel_library.name 
        
        asset_lib.path = os.path.join(self.asset_path)
        bpy.ops.asset.library_refresh()
        return {'FINISHED'}

class home_builder_OT_show_library_material_pointers(bpy.types.Operator):
    bl_idname = "home_builder.show_library_material_pointers"
    bl_label = "Library Material Pointers"
    bl_description = "Show the material pointers for the library"

    library_name: bpy.props.StringProperty(name="Library Name")

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=550)

    def execute(self, context):  
        return {'FINISHED'}

    def draw(self, context):
        wm_props = context.window_manager.home_builder
        # asset = wm_props.get_active_asset(context)

        layout = self.layout
        scene_props = context.scene.home_builder
        box = layout.box()
        # row = box.row()
        # row.label(text=self.library_name)
        # row.label(text="Selected Material: " + asset.file_data.name)
        col = box.column(align=True)
        for pointer in scene_props.material_pointers:
            if pointer.library_name == self.library_name:
                row = col.row()
                # row.alignment = 'LEFT'
                # props = row.operator('home_builder.assign_material_to_pointer',text=pointer.name)
                # props.pointer_name = pointer.name     
                row.label(text=pointer.name,icon='DOT')
                row.label(text=pointer.category_name,icon='FILEBROWSER')
                row.label(text=pointer.material_name,icon='MATERIAL')
                # row.label(text=pointer.category_name + " - " + pointer.material_name,icon='MATERIAL')             
        

class home_builder_OT_assign_material_to_pointer(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_to_pointer"
    bl_label = "Assign Material to Pointer"
    bl_description = "This assigns a material to the pointer and will update all of the materials in the scene"

    library_name: bpy.props.StringProperty(name="Library Name")
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):  
        wm_props = context.window_manager.home_builder
        library = wm_props.get_active_library(context)
        asset = wm_props.get_active_asset(context)

        scene_props = context.scene.home_builder
        for pointer in scene_props.material_pointers:
            if pointer.name == self.pointer_name:
                pointer.material_name = asset.file_data.name
                pointer.category_name = library.name
                pointer.library_path = os.path.join(library.library_path)
                bpy.ops.home_builder.update_materials_for_pointer(pointer_name=self.pointer_name)                
        return {'FINISHED'}


class home_builder_OT_update_materials_for_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_materials_for_pointer"
    bl_label = "Update Materials for Pointer"
    bl_description = "This updates all of the materials in the scene from the pointers"

    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def get_material(self,library_path,material_name):
        if material_name in bpy.data.materials:
            return bpy.data.materials[material_name]

        if os.path.exists(library_path):

            with bpy.data.libraries.load(library_path) as (data_from, data_to):
                for mat in data_from.materials:
                    if mat == material_name:
                        data_to.materials = [mat]
                        break    
            
            for mat in data_to.materials:
                return mat

    def execute(self, context):  
        scene_props = context.scene.home_builder
        selected_pointer = None
        for pointer in scene_props.material_pointers:
            if pointer.name == self.pointer_name:
                selected_pointer = pointer

        for obj in bpy.data.objects:
            scene_props = bpy.context.scene.home_builder  
            for index, p in enumerate(obj.pyclone.pointers):
                if p.pointer_name == self.pointer_name:
                    if index + 1 <= len(obj.material_slots):
                        slot = obj.material_slots[index]
                        slot.material = self.get_material(selected_pointer.library_path,selected_pointer.material_name)    

        return {'FINISHED'}


class home_builder_OT_disconnect_constraint(bpy.types.Operator):
    bl_idname = "home_builder.disconnect_constraint"
    bl_label = "Disconnect Constraint"
    bl_description = "This disconnects the constraint to allow you to move the object"
    
    obj_name: bpy.props.StringProperty(name="Base Point Name")

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.constraints.clear()
        return {'FINISHED'}


class home_builder_OT_unit_settings(bpy.types.Operator):
    bl_idname = "home_builder.unit_settings"
    bl_label = "Change Units"
    bl_description = "This will show the unit settings"
    bl_options = {'UNDO'}
    
    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        
    def draw(self, context):
        layout = self.layout
        unit = context.scene.unit_settings

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(unit, "system")

        col = layout.column()
        col.prop(unit, "system_rotation", text="Rotation")
        subcol = col.column()
        subcol.enabled = unit.system != 'NONE'
        subcol.prop(unit, "length_unit", text="Length")
        subcol.prop(unit, "temperature_unit", text="Temperature")

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_delete_assembly(bpy.types.Operator):
    bl_idname = "home_builder.delete_assembly"
    bl_label = "Delete Assembly"
    bl_description = "This deletes the assembly"
    
    obj_name: bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        obj_bp = bpy.data.objects[self.obj_name]
        pc_utils.delete_object_and_children(obj_bp)
        return {'FINISHED'}


class home_builder_OT_save_assembly_to_build_library(bpy.types.Operator):
    bl_idname = "home_builder.save_assembly_to_build_library"
    bl_label = "Save Assembly to Build Library"
    bl_description = "This will save the assembly to the build library"
    bl_options = {'UNDO'}

    assembly_bp_name: bpy.props.StringProperty(name="Collection Name")

    assembly = None
    assembly_name = ""

    @classmethod
    def poll(cls, context):
        assembly_bp = pc_utils.get_bp_by_tag(context.object,'IS_ASSEMBLY_BP')
        if assembly_bp:
            return True
        else:
            return False

    def check(self, context):    
        return True

    def invoke(self,context,event):
        assembly_bp = pc_utils.get_bp_by_tag(context.object,'IS_ASSEMBLY_BP')
        self.assembly = pc_types.Assembly(assembly_bp)
        self.assembly_name = self.assembly.obj_bp.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        path = self.get_path(context)
        files = os.listdir(path) if os.path.exists(path) else []

        layout.label(text="Assembly Name: " + self.assembly_name)

        if self.assembly_name + ".blend" in files or self.assembly_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")

    def select_assembly_objects(self,coll):
        for obj in coll.objects:
            obj.select_set(True)
        for child in coll.children:
            self.select_collection_objects(child)

    def get_path(self,context):
        return hb_paths.get_build_library_path()

    def create_assembly_thumbnail_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "') as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")    

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    obj.select_set(True)\n")
        
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        file.write("render = bpy.context.scene.render\n")
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = r'" + os.path.join(source_dir,assembly_name) + "'\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_assembly_save_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "') as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")        

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    mat.asset_clear()\n")

        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,assembly_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def create_asset_script(self,asset_name,thumbnail_path):
        file = codecs.open(os.path.join(bpy.app.tempdir,"asset_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("bpy.ops.mesh.primitive_cube_add()\n")
        file.write("obj = bpy.context.view_layer.objects.active\n")
        file.write("obj.name = '" + asset_name + "'\n")
        file.write("obj.asset_mark()\n")
        file.write("override = bpy.context.copy()\n")
        file.write("override['id'] = obj\n")
        file.write("test_path = r'" + thumbnail_path + "'\n")
        file.write("with bpy.context.temp_override(**override):\n")
        file.write("    bpy.ops.ed.lib_id_load_custom_preview(filepath=test_path)\n")
        file.write("bpy.ops.wm.save_mainfile()\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'asset_temp.py')

    def create_empty_library_script(self,library_path):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_library_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")

        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + library_path + "')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_library_temp.py')

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp.name)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def get_thumbnail_path(self):
        return os.path.join(os.path.dirname(__file__),'thumbnail.blend')

    def execute(self, context):
        wm_props = context.window_manager.home_builder

        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))

        library = wm_props.get_active_library(context)

        custom_library_dir = self.get_path(context)
        directory_to_save_to = os.path.join(custom_library_dir,library.name,'assets')
        if not os.path.exists(directory_to_save_to):
            os.makedirs(directory_to_save_to)

        obj_list = []
        obj_list = self.get_children_list(self.assembly.obj_bp,obj_list)

        if not os.path.exists(library.library_path):
            library_script_path = self.create_empty_library_script(library.library_path)
            create_library_command = [bpy.app.binary_path,"-b","--python",library_script_path]
            subprocess.call(create_library_command)

        thumbnail_script_path = self.create_assembly_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.assembly_name, obj_list)
        save_script_path = self.create_assembly_save_script(directory_to_save_to, bpy.data.filepath, self.assembly_name, obj_list)
        asset_script_path = self.create_asset_script(self.assembly_name,os.path.join(directory_to_save_to,self.assembly_name + ".png"))

        tn_command = [bpy.app.binary_path,self.get_thumbnail_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]
        asset_command = [bpy.app.binary_path,library.library_path,"-b","--python",asset_script_path]

        subprocess.call(tn_command)
        subprocess.call(save_command)
        subprocess.call(asset_command)

        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        os.remove(asset_script_path)

        bpy.ops.asset.library_refresh()
        return {'FINISHED'}


class home_builder_OT_create_new_build_library_category(bpy.types.Operator):
    bl_idname = "home_builder.create_new_build_library_category"
    bl_label = "Create New Build Library Category"
    bl_description = "This will create a new category in the build library"
    bl_options = {'UNDO'}

    category_name: bpy.props.StringProperty(name="Category Name")

    def check(self, context):    
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'category_name')

    def execute(self, context):
        wm_props = context.window_manager.home_builder

        library_path = hb_paths.get_build_library_path()
        new_path = os.path.join(library_path,self.category_name)
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        asset_lib = wm_props.asset_libraries.add()
        asset_lib.name = self.category_name
        asset_lib.library_type = 'BUILD_LIBRARY'
        asset_lib.library_path = os.path.join(new_path,"library.blend")

        bpy.ops.home_builder.update_library_path(asset_path=asset_lib.library_path)
        return {'FINISHED'}

classes = (
    home_builder_OT_about_home_builder,
    home_builder_OT_update_library_xml,
    home_builder_OT_todo,
    home_builder_OT_load_library,
    home_builder_OT_add_external_library,
    home_builder_OT_update_library_path,
    home_builder_OT_show_library_material_pointers,
    home_builder_OT_assign_material_to_pointer,
    home_builder_OT_update_materials_for_pointer,
    home_builder_OT_disconnect_constraint,
    home_builder_OT_unit_settings,
    home_builder_OT_delete_assembly,
    home_builder_OT_save_assembly_to_build_library,
    home_builder_OT_create_new_build_library_category
)

register, unregister = bpy.utils.register_classes_factory(classes)        
