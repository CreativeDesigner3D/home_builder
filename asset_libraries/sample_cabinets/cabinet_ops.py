import bpy
import os
import inspect
import subprocess
import codecs
import time
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from . import cabinet_library

class Cabinet_Library_Item(bpy.types.PropertyGroup):
    library_type: StringProperty(name="Library Type")
    is_checked: BoolProperty(name="Is Checked")

class hb_sample_cabinets_OT_active_cabinet_library(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.active_cabinet_library"
    bl_label = "Active Cabinet Library"

    asset_name: StringProperty(name="Asset Name")

    def execute(self, context):
        workspace = context.workspace
        wm = context.window_manager
        asset = wm.home_builder.home_builder_library_assets[workspace.home_builder.home_builder_library_index]
        cabinet = eval("cabinet_library." + asset.file_data.name.replace(" ","_") + "()")
        cabinet.draw()      
        return {'FINISHED'}


class hb_sample_cabinets_OT_drop_cabinet_library(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.drop_cabinet_library"
    bl_label = "Drop Cabinet Library"

    product = None

    def draw_cabinet(self,context):
        workspace = context.workspace
        wm = context.window_manager
        asset = wm.home_builder.home_builder_library_assets[workspace.home_builder.home_builder_library_index]
        self.product = eval("cabinet_library." + asset.file_data.name.replace(" ","_") + "()")
        self.product.draw()

    def execute(self, context):
        self.draw_cabinet(context)
        return {'FINISHED'}


class hb_sample_cabinets_OT_build_library(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.build_library"
    bl_label = "Build Library"

    library_categories: EnumProperty(name="Library Categories",
                          items=[('APPLIANCES',"Appliances","Appliances"),
                                 ('CABINETS',"Cabinets","Cabinets"),
                                 ('CABINETS_STARTERS',"Cabinet Starters","Cabinet Starters"),
                                 ('CABINET_INSERTS',"Cabinet Inserts","Cabinet Inserts"),
                                 ('CABINET_PARTS',"Cabinet Parts","Cabinet Parts"),
                                 ('CLOSET_STARTERS',"Closet Starters","Closet Starters"),
                                 ('CLOSET_INSERTS',"Closet Inserts","Closet Inserts"),
                                 ('CLOSET_PARTS',"Closet Parts","Closet Parts")],
                          default='CABINETS')

    only_display_missing: BoolProperty(name="Only Display Missing",default=True)

    library_items: CollectionProperty(name="Library Items",type=Cabinet_Library_Item)

    def check(self, context):
        return True

    def get_library_items(self):
        for mod_name, mod in inspect.getmembers(cabinet_library):
            if "__" not in mod_name:
                item = self.library_items.add()
                item.name = mod_name.replace("_"," ")
                item.library_type = 'CABINETS'

    def invoke(self,context,event):
        for item in self.library_items:
            self.library_items.remove(0)
        self.get_library_items()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)

    def create_asset_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("bpy.ops.mesh.primitive_cube_add()\n")
        file.write("obj = bpy.context.view_layer.objects.active\n")
        file.write("obj.name = 'TEST ASSET'\n")
        file.write("obj.asset_mark()\n")
        file.write("obj.asset_generate_preview()\n")
        file.write("bpy.ops.wm.save_mainfile()\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def execute(self, context):
        scene_props = context.scene.home_builder
        workspace = context.workspace
        wm = context.window_manager        
        library_folder = os.path.join(os.path.dirname(__file__),'library','Sample Cabinets')
        library_blend = os.path.join(library_folder,'library.blend')
        for item in self.library_items:
            if item.is_checked:
                script = self.create_asset_script(item)
                command = [bpy.app.binary_path,library_blend,"-b","--python",script]
                subprocess.call(command)

        time.sleep(3)
        prefs = context.preferences
        asset_lib = prefs.filepaths.asset_libraries.get('home_builder_library')  
        asset_lib.path = library_folder            
        scene_props.library_tabs = scene_props.library_tabs
        bpy.ops.asset.library_refresh()
        for asset in wm.home_builder.home_builder_library_assets:
            print('ASSET',asset.file_data.name)                 
                # item_class = eval('cabinet_library.' + item.name.replace(" ","_") + '()')
        #         item_class.draw()
                # for mod_name, mod in inspect.getmembers(cabinet_library):
                    
                #     if "__" not in mod_name:                
                #     print(item.name)
                # pass #GET CLASS, CALL DRAW and RENDER
    
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.scale_y = 1.3
        row.prop(self,'library_categories',text="")
        row = box.row()
        row.prop(self,'only_display_missing')
        box = col.box()
        for item in self.library_items:
            if item.library_type == self.library_categories:
                box.prop(item,'is_checked',text=item.name)


classes = (
    Cabinet_Library_Item,
    hb_sample_cabinets_OT_active_cabinet_library,
    hb_sample_cabinets_OT_drop_cabinet_library,
    hb_sample_cabinets_OT_build_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                    