import bpy
import os
import subprocess
import codecs
from . import paths_doors_windows
from . import utils_doors_windows
from pc_lib import pc_types, pc_unit, pc_utils

def get_current_view_rotation(context):
    '''
    Gets the current view rotation for creating thumbnails
    '''
    for window in context.window_manager.windows:
        screen = window.screen

        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        return space.region_3d.view_rotation

    return (0,0,0)

class doors_windows_OT_create_new_door_window_asset(bpy.types.Operator):
    bl_idname = "doors_windows.create_new_asset"
    bl_label = "Create New Asset"
    bl_description = "This will create a new asset of the specified type"

    asset_type: bpy.props.StringProperty(name="Asset Type",description="Type of Asset to Create")

    def execute(self, context):

        if self.asset_type == 'ENTRY_DOOR_FRAME':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Entry Door Frame")
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(6)
            assembly.obj_z.location.z = pc_unit.inch(90)
            assembly.obj_bp.select_set(True)
            assembly.add_prompt("Door Frame Width",'DISTANCE',pc_unit.inch(3))
            context.view_layer.objects.active = assembly.obj_bp     

        if self.asset_type == 'ENTRY_DOOR_PANEL':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Entry Door Panel")
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(1.5)
            assembly.obj_z.location.z = pc_unit.inch(90)
            assembly.obj_bp.select_set(True)
            assembly.add_prompt("Hide",'CHECKBOX',False)
            dim_x = assembly.obj_x.pyclone.get_var('location.x','dim_x')
            x1 = assembly.add_empty('X1')
            x1.empty_display_size = .01
            x1.pyclone.loc_x('IF(dim_x>0,0,dim_x)',[dim_x])
            x2 = assembly.add_empty('X2')
            x2.empty_display_size = .01
            x2.pyclone.loc_x('IF(dim_x>0,dim_x,0)',[dim_x])                
            context.view_layer.objects.active = assembly.obj_bp

        if self.asset_type == 'WINDOW_FRAME':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Window Frame")      
            # assembly.obj_bp.location.z = pc_unit.inch(48)
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(6)
            assembly.obj_z.location.z = pc_unit.inch(48)
            assembly.obj_bp.select_set(True)                  
            assembly.add_prompt("Left Window Frame Width",'DISTANCE',pc_unit.inch(3))
            assembly.add_prompt("Right Window Frame Width",'DISTANCE',pc_unit.inch(3))
            assembly.add_prompt("Top Window Frame Width",'DISTANCE',pc_unit.inch(3))
            assembly.add_prompt("Bottom Window Frame Width",'DISTANCE',pc_unit.inch(3))  
            context.view_layer.objects.active = assembly.obj_bp         

        if self.asset_type == 'WINDOW_INSERT':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Window Insert")      
            # assembly.obj_bp.location.z = pc_unit.inch(48)
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(6)
            assembly.obj_z.location.z = pc_unit.inch(48)
            assembly.obj_bp.select_set(True)   

        return {'FINISHED'}        


class doors_windows_OT_add_handle_to_scene(bpy.types.Operator):
    bl_idname = "doors_windows.add_handle_to_scene"
    bl_label = "Add Handle to Scene"
    bl_description = "This will add the current handle to the scene"

    asset_type: bpy.props.StringProperty(name="Asset Type",description="Type of Asset to Create")

    def execute(self, context):
        coll = context.view_layer.active_layer_collection.collection
        props = utils_doors_windows.get_scene_props(bpy.context.scene)
        root_path = paths_doors_windows.get_entry_door_handle_path()
        handle_path = os.path.join(root_path, props.entry_door_handle_category, props.entry_door_handle + ".blend")          
        door_handle_obj = pc_utils.get_object(handle_path)
        coll.objects.link(door_handle_obj)
        return {'FINISHED'} 


class doors_windows_OT_save_asset_to_library(bpy.types.Operator):
    bl_idname = "doors_windows.save_asset_to_library"
    bl_label = "Save Current Asset to Library"
    bl_description = "This will save the current file to the active library"
    bl_options = {'UNDO'}

    asset_type: bpy.props.StringProperty(name="Asset Type",description="Type of Asset to Save")

    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def create_thumbnail_script(self,asset_path,asset_name,view_rotation):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("import sys\n")
        # file.write("import " + __package__ + "\n")

        file.write("path = r'" + os.path.join(asset_path,asset_name)  + "'\n")

        file.write("bpy.ops.object.select_all(action='DESELECT')\n")

        file.write("with bpy.data.libraries.load(r'" + os.path.join(asset_path,asset_name + ".blend") + "') as (data_from, data_to):\n")
        file.write("    data_to.objects = data_from.objects\n")

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        # file.write("    " + __package__ + ".home_builder_pointers.assign_materials_to_object(obj)\n")
        file.write("    obj.select_set(True)\n")

        file.write("bpy.context.scene.camera.rotation_euler = " + str(view_rotation) + "\n") 
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #RENDER
        file.write("render = bpy.context.scene.render\n")    
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def create_save_object_script(self,save_dir,asset):
        source_file = bpy.data.filepath
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "') as (data_from, data_to):\n")
        file.write("    data_to.objects = ['" + asset.name + "']\n")
        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        # file.write("    obj.select_set(True)\n")
        # file.write("    if obj.type == 'CURVE':\n")
        # file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
        # file.write("        obj.data.dimensions = '2D'\n")
        # file.write("    bpy.context.view_layer.objects.active = obj\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(save_dir,asset.name) + ".blend')\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def create_save_assembly_script(self,save_dir,asset):
        source_file = bpy.data.filepath
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "') as (data_from, data_to):\n")
        file.write("    data_to.objects = data_from.objects\n")
        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(save_dir,asset.name) + ".blend')\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def get_library_path(self,context):
        props = utils_doors_windows.get_scene_props(context.scene)
        if self.asset_type == 'ENTRY_DOOR_PANEL':
            return os.path.join(paths_doors_windows.get_entry_door_panel_path(),props.entry_door_panel_category)
        if self.asset_type == 'ENTRY_DOOR_FRAME':
            return os.path.join(paths_doors_windows.get_entry_door_frame_path(),props.entry_door_frame_category)
        if self.asset_type == 'ENTRY_DOOR_HANDLE':
            return os.path.join(paths_doors_windows.get_entry_door_handle_path(),props.entry_door_handle_category)
        if self.asset_type == 'WINDOW_FRAME':
            return os.path.join(paths_doors_windows.get_window_frame_path(),props.window_frame_category)
        if self.asset_type == 'WINDOW_INSERT':
            return os.path.join(paths_doors_windows.get_window_insert_path(),props.window_insert_category)

    def get_thumbnail_path(self):
        return os.path.join(os.path.dirname(__file__),"thumbnail.blend")

    def execute(self, context):     

        current_rotation = get_current_view_rotation(context)
        rotation = (current_rotation.to_euler().x,current_rotation.to_euler().y,current_rotation.to_euler().z)

        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))

        path = self.get_library_path(context)

        if self.asset_type in {'ENTRY_DOOR_PANEL','ENTRY_DOOR_FRAME','WINDOW_FRAME','WINDOW_INSERT'}:
            save_script_path = self.create_save_assembly_script(path, self.get_asset(context))
            command = [bpy.app.binary_path,"-b","--python",save_script_path]
            subprocess.call(command)      
            tn_script_path = self.create_thumbnail_script(path,self.get_asset(context).name,rotation)
            command = [bpy.app.binary_path,self.get_thumbnail_path(),"-b","--python",tn_script_path]
            subprocess.call(command)             

        if self.asset_type == 'ENTRY_DOOR_HANDLE':
            save_script_path = self.create_save_object_script(path, self.get_asset(context))
            command = [bpy.app.binary_path,"-b","--python",save_script_path]
            subprocess.call(command)
            tn_script_path = self.create_thumbnail_script(path,self.get_asset(context).name,rotation)
            command = [bpy.app.binary_path,self.get_thumbnail_path(),"-b","--python",tn_script_path]
            subprocess.call(command)  

        return {'FINISHED'}

    def get_asset(self,context):
        if self.asset_type in {'ENTRY_DOOR_PANEL','ENTRY_DOOR_FRAME','WINDOW_FRAME','WINDOW_INSERT'}:
            return pc_utils.get_bp_by_tag(context.object,'IS_ASSEMBLY_BP')

        if self.asset_type == 'ENTRY_DOOR_HANDLE':
            return context.object

    def draw(self, context):
        layout = self.layout
        path = self.get_library_path(context)

        files = os.listdir(path) if os.path.exists(path) else []
        
        asset_name = self.get_asset(context).name

        layout.label(text="Asset Name: " + asset_name)
        
        if asset_name + ".blend" in files or asset_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")   


classes = (
    doors_windows_OT_create_new_door_window_asset,
    doors_windows_OT_save_asset_to_library,
    doors_windows_OT_add_handle_to_scene,
)

register, unregister = bpy.utils.register_classes_factory(classes)                                