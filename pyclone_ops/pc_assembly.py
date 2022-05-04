import bpy
from bpy.types import (
        Operator,
        Panel,
        UIList,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        FloatProperty,
        )
import os, math, sys
from .. import pyclone_utils
from ..pc_lib import pc_types, pc_utils, pc_unit

try:
    import reportlab
except ModuleNotFoundError:
    print('NOT FOUND')
    ROOT_PATH = os.path.dirname(__file__)
    PATH = os.path.join(os.path.dirname(ROOT_PATH),"python_libs")
    sys.path.append(PATH)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import legal,letter,inch
from reportlab.platypus import Image
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, Spacer, PageTemplate, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable

class Item(PropertyGroup):
    pass  

class pc_assembly_OT_create_new_assembly(Operator):
    bl_idname = "pc_assembly.create_new_assembly"
    bl_label = "Create New Assembly"
    bl_description = "This will create a new assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly = pc_types.Assembly()
        assembly.create_assembly(self.assembly_name)
        assembly.obj_x.location.x = 1
        assembly.obj_y.location.y = 1
        assembly.obj_z.location.z = 1
        assembly.obj_bp.select_set(True)
        assembly.obj_bp["PROMPT_ID"] = "pc_assembly.show_properties"
        context.view_layer.objects.active = assembly.obj_bp
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter the name of the assembly to add.")
        layout.prop(self,'assembly_name')


class pc_assembly_OT_delete_assembly(Operator):
    bl_idname = "pc_assembly.delete_assembly"
    bl_label = "Delete Assembly"
    bl_description = "This will delete the assembly"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            pc_utils.delete_object_and_children(obj_bp)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the assembly?")
        layout.label(text=self.obj_bp_name)


class pc_assembly_OT_select_base_point(Operator):
    bl_idname = "pc_assembly.select_base_point"
    bl_label = "Select Assembly Base Point"
    bl_description = "This will select the assembly base point"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            obj_bp.hide_viewport = False
            obj_bp.select_set(True)
        return {'FINISHED'}


class pc_assembly_OT_duplicate_assembly(Operator):
    bl_idname = "pc_assembly.duplicate_assembly"
    bl_label = "Duplicate Assembly"
    bl_description = "This will duplicate the assembly"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    @classmethod
    def poll(cls, context):
        return True

    def select_obj_and_children(self,obj):
        obj.hide_viewport = False
        obj.select_set(True)
        for child in obj.children:
            obj.hide_viewport = False
            child.select_set(True)
            self.select_obj_and_children(child)

    def hide_empties_and_boolean_meshes(self,obj):
        if obj.type == 'EMPTY' or obj.hide_render:
            obj.hide_viewport = True
        for child in obj.children:
            self.hide_empties_and_boolean_meshes(child)

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]

            bpy.ops.object.select_all(action='DESELECT')
            self.select_obj_and_children(obj_bp)
            bpy.ops.object.duplicate_move()
            self.hide_empties_and_boolean_meshes(obj_bp)   

            obj = context.object
            obj_bp = pc_utils.get_assembly_bp(obj)
            self.hide_empties_and_boolean_meshes(obj_bp)   
            obj_bp.hide_viewport = False
            obj_bp.select_set(True)

        return {'FINISHED'}


class pc_assembly_OT_refresh_vertex_groups(Operator):
    bl_idname = "pc_assembly.refresh_vertex_groups"
    bl_label = "Refresh Vertex Groups"
    bl_description = "This will refresh the vertex groups from the mesh hooks"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")
    obj_mesh_name: StringProperty(name="Mesh Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            assembly = pc_types.Assembly(obj_bp)
            obj_mesh = bpy.data.objects[self.obj_mesh_name]
            for vgroup in obj_mesh.vertex_groups:
                obj_mesh.vertex_groups.remove(group=vgroup)
            assembly.update_vector_groups()
        return {'FINISHED'}


class pc_assembly_OT_add_object(Operator):
    bl_idname = "pc_assembly.add_object"
    bl_label = "Add Object to Assembly"
    bl_description = "This will add a new object to the assembly"
    bl_options = {'UNDO'}

    assembly_name: StringProperty(name="Assembly Name",default="New Assembly")

    object_name: StringProperty(name="Object Name",default="New Object")
    object_type: bpy.props.EnumProperty(name="Object Type",
                                        items=[('MESH',"Mesh","Add an Mesh Object"),
                                               ('EMPTY',"Empty","Add an Empty Object"),
                                               ('CURVE',"Curve","Add an Curve Object"),
                                               ('LIGHT',"Light","Add an Light Object")],
                                        default='MESH')
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj_bp = pc_utils.get_assembly_bp(context.object)
        assembly = pc_types.Assembly(obj_bp)
        if self.object_type == 'EMPTY':
            assembly.add_empty(self.object_name)

        if self.object_type == 'MESH':
            obj_mesh = pc_utils.create_cube_mesh(self.object_name,(assembly.obj_x.location.x,
                                                                   assembly.obj_y.location.y,
                                                                   assembly.obj_z.location.z))

            if 'PROMPT_ID' in assembly.obj_bp:
                obj_mesh['PROMPT_ID'] = assembly.obj_bp['PROMPT_ID']
            
            assembly.add_object(obj_mesh)

            # MAKE NORMALS CONSISTENT
            context.view_layer.objects.active = obj_mesh
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()

        if self.object_type == 'CURVE':
            curve = bpy.data.curves.new(self.object_name,'CURVE')
            obj_curve = bpy.data.objects.new(self.object_name,curve)
            spline = obj_curve.data.splines.new('BEZIER')
            spline.bezier_points.add(count=1)                 
            obj_curve.data.splines[0].bezier_points[0].co = (0,0,0)
            obj_curve.data.splines[0].bezier_points[1].co = (assembly.obj_x.location.x,0,0)
            assembly.add_object(obj_curve)
        if self.object_type == 'LIGHT':
            assembly.add_light(self.object_name,'POINT')
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'object_type',expand=True)
        layout.prop(self,'object_name')


class pc_assembly_OT_connect_mesh_to_hooks_in_assembly(Operator):
    bl_idname = "pc_assembly.connect_meshes_to_hooks_in_assembly"
    bl_label = "Connect Mesh to Hooks In Assembly"
    bl_description = "This connects all mesh hooks to a mesh"
    bl_options = {'UNDO'}
    
    obj_name: StringProperty(name="Object Name")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj_bp = pc_utils.get_assembly_bp(obj)
        if obj_bp:
            hooklist = []

            for child in obj_bp.children:
                if child.type == 'EMPTY' and 'obj_prompts' not in child:
                    hooklist.append(child)

            if obj.mode == 'EDIT':
                bpy.ops.object.editmode_toggle()
            
            pc_utils.apply_hook_modifiers(context,obj)
            for vgroup in obj.vertex_groups:
                for hook in hooklist:
                    if hook.name == vgroup.name:
                        pc_utils.hook_vertex_group_to_object(obj,vgroup.name,hook)

            obj.lock_location = (True,True,True)
                
        return {'FINISHED'}

class pc_assembly_OT_create_assembly_script(Operator):
    bl_idname = "pc_assembly.create_assembly_script"
    bl_label = "Create Assembly Script"
    bl_description = "This will create a script of the selected assembly. This is in development."
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        obj = context.object
        coll = pc_utils.get_assembly_collection(obj)
        assembly = pc_types.Assembly(coll)

        #Create New Script
        text = bpy.data.texts.new(coll.name)

        #Add Imports
        text.write('import bpy\n')
        #Figure out how to import bp_types
                
        #Add Class Def
        text.write('class ' + coll.name + '(bp_types.Assembly):\n')
        text.write('    def draw(self):\n')
        text.write('    self.create_assembly()\n')

        #Add Prompts
        for prompt in assembly.obj_prompts.prompt_page.prompts:
            pass

        #Add Empty Objects Except Built-in Assembly Objects
        #for obj in assembly.empty_objs:
        for obj in assembly.obj_bp.children:
            if obj.type == 'EMPTY':
                pass #Assign Drivers and Constraints

        #Add Mesh Objects This needs to be done after empties for hooks
        #for obj in assembly.mesh_objs:
        for obj in assembly.obj_bp.children:
            pass
        return {'FINISHED'}


class pc_assembly_OT_select_parent_assembly(bpy.types.Operator):
    bl_idname = "pc_assembly.select_parent"
    bl_label = "Select Parent Assembly"
    bl_description = "This selects the parent assembly"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj_bp = pc_utils.get_assembly_bp(context.object)
        if obj_bp and obj_bp.parent:    
            return True
        else:
            return False

    def select_children(self,obj):
        obj.select_set(True)
        for child in obj.children:
            child.select_set(True)
            self.select_children(child)

    def execute(self, context):
        obj_bp = pc_utils.get_assembly_bp(context.object)
        assembly = pc_types.Assembly(obj_bp)

        if assembly:
            if assembly.obj_bp.parent:
                assembly.obj_bp.parent.select_set(True)
                context.view_layer.objects.active = assembly.obj_bp.parent

                self.select_children(assembly.obj_bp.parent)

        return {'FINISHED'}


class pc_assembly_OT_create_assembly_layout(Operator):
    bl_idname = "pc_assembly.create_assembly_layout"
    bl_label = "Create Assembly Layout"
    bl_description = "This will create a new scene and link the assembly to that scene"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")
    
    view_name: StringProperty(name="View Name",default="New Layout View")

    include_front_view: BoolProperty(name="Include Front View",default=True)
    include_top_view: BoolProperty(name="Include Top View")
    include_side_view: BoolProperty(name="Include Side View")

    @classmethod
    def poll(cls, context):
        return True

    def get_unique_collection_name(self,name):
        if name not in bpy.data.collections:
            return name    
        counter = 1
        while name + " " + str(counter) in bpy.data.collections:
            counter += 1    
        return name + " " + str(counter)

    def execute(self, context):
        if self.obj_bp_name in bpy.data.objects:
            model_scene = context.scene
            obj_bp = bpy.data.objects[self.obj_bp_name]

            assembly = pc_types.Assembly(obj_bp)
            a_width = math.fabs(assembly.obj_x.location.x)
            a_depth = math.fabs(assembly.obj_y.location.y)
            a_height = math.fabs(assembly.obj_z.location.z)
            view_gap = .5

            obj_front = None
            obj_side = None
            obj_top = None

            collection_name = self.get_unique_collection_name(self.view_name)
            collection = assembly.create_assembly_collection(collection_name)
            bpy.ops.scene.new(type='EMPTY')
            context.scene.name = collection_name
            assembly_layout = pc_types.Assembly_Layout(context.scene)
            assembly_layout.setup_assembly_layout()
            if self.include_front_view:
                obj_front = assembly_layout.add_assembly_view(collection)
                obj_front.name = collection.name + " - Front"
            if self.include_side_view:
                obj_side = assembly_layout.add_assembly_view(collection)
                obj_side.name = collection.name + " - Side"
                # obj_side.location = (a_width + a_depth + view_gap,0,0)
                obj_side.rotation_euler = (0,0,math.radians(-90))
            if self.include_top_view:
                obj_top = assembly_layout.add_assembly_view(collection)     
                obj_top.name = collection.name + " - Top"          
                # obj_top.location = (0,0,a_height + a_depth + view_gap)     
                obj_top.rotation_euler = (math.radians(90),0,0)    

            assembly_layout.add_layout_camera()
            assembly_layout.scene.world = model_scene.world
            assembly_layout.camera.parent = assembly.obj_bp   

            context.scene.pyclone.fit_to_paper = False
            context.scene.pyclone.page_scale_unit_type = 'METRIC'
            context.scene.pyclone.metric_page_scale = '1:30'  

            bpy.ops.object.select_all(action='DESELECT')
            if obj_front:
                obj_front.select_set(True)
            if obj_side:
                obj_side.select_set(True)
                obj_side.location = (a_width*obj_side.scale.x + a_depth*obj_side.scale.y + view_gap*obj_side.scale.x,0,0)
            if obj_top:
                obj_top.select_set(True)      
                obj_top.location = (0,0,a_height*obj_side.scale.z + a_depth*obj_side.scale.y + view_gap*obj_side.scale.x)                            
            context.view_layer.objects.active = obj_front
            bpy.ops.view3d.camera_to_view_selected()          

            context.scene.pyclone.metric_page_scale = '1:30'                    
        return {'FINISHED'}

    def invoke(self,context,event):
        obj_bp = bpy.data.objects[self.obj_bp_name]
        assembly = pc_types.Assembly(obj_bp)    
        self.view_name = assembly.obj_bp.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'view_name')
        box = layout.box()
        box.label(text="What views of the assembly do you want to include?")
        row = box.row()
        row.prop(self,'include_front_view',text="Front")
        row.prop(self,'include_top_view',text="Top")
        row.prop(self,'include_side_view',text="Side")
        

class pc_assembly_OT_create_render_view(Operator):
    bl_idname = "pc_assembly.create_render_view"
    bl_label = "Create Render View"
    bl_description = "This will create a new render view"
    bl_options = {'UNDO'}

    view_name: StringProperty(name="View Name",default="New Layout View")

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'view_name')

    def execute(self, context):
        model_scene = context.scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.collection.create(name=self.view_name)

        collection = bpy.data.collections[self.view_name]

        bpy.ops.scene.new(type='EMPTY')
        context.scene.name = self.view_name
        assembly_layout = pc_types.Assembly_Layout(context.scene)
        assembly_layout.scene.world = model_scene.world
        assembly_layout.setup_assembly_layout()

        obj = assembly_layout.add_assembly_view(collection)

        assembly_layout.add_3d_layout_camera()

        return {'FINISHED'}


class pc_assembly_OT_delete_assembly_layout(Operator):
    bl_idname = "pc_assembly.delete_assembly_layout"
    bl_label = "Delete Assembly Layout"
    bl_description = "This will delete the layout scene"
    bl_options = {'UNDO'}

    view_name: StringProperty(name="View Name",default="New Layout View")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        model_scene = context.scene
        scene = bpy.data.scenes[self.view_name]
        bpy.data.scenes.remove(scene)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the view layout?")
        layout.label(text="Layout Name - " + self.view_name)


class pc_assembly_OT_create_assembly_dimension(bpy.types.Operator):
    bl_idname = "pc_assembly.create_assembly_dimension"
    bl_label = "Create Assembly Dimension"
    bl_description = "This creates an assembly dimension"
    bl_options = {'UNDO'}

    add_x_dimension: BoolProperty(name="Add X Dimension")
    add_y_dimension: BoolProperty(name="Add Y Dimension")
    add_z_dimension: BoolProperty(name="Add Z Dimension")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self,context,event):
        dim_bp = pc_utils.get_assembly_bp(context.object)
        self.dimension = pc_types.Dimension(dim_bp)  
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def get_selected_collection(self,context):
        sel_obj = context.object
        if sel_obj.instance_type == 'COLLECTION':
            return sel_obj.instance_collection

    def get_assembly_collection(self,collection):
        obj_bp = collection.pyclone.assembly_bp
        assembly = pc_types.Assembly(obj_bp)
        return assembly

    def execute(self, context):
        sel_obj = context.object
        collection = self.get_selected_collection(context)
        assembly = self.get_assembly_collection(collection)
        assembly_layout = pc_types.Assembly_Layout(context.scene)

        if self.add_x_dimension:
            dim = pc_types.Dimension()
            dim.create_dimension(assembly_layout)
            dim.obj_bp.rotation_euler.x = math.radians(-90)
            dim.obj_bp.rotation_euler.y = 0
            dim.obj_y.location.y = .2
            dim.obj_bp.parent = sel_obj
            dim.obj_bp.location = assembly.obj_bp.location
            dim.obj_x.location.x = assembly.obj_x.location.x
            dim.flip_y()
            dim.update_dim_text()

        if self.add_y_dimension:
            dim = pc_types.Dimension()
            dim.create_dimension(assembly_layout)
            dim.obj_bp.rotation_euler.x = math.radians(-90)
            dim.obj_bp.rotation_euler.y = math.radians(0)
            dim.obj_bp.rotation_euler.z = math.radians(-90)
            dim.obj_y.location.y = .2
            dim.obj_bp.parent = sel_obj
            dim.obj_bp.location = assembly.obj_bp.location
            dim.obj_x.location.x = math.fabs(assembly.obj_y.location.y)
            dim.flip_y()
            dim.flip_x()
            dim.update_dim_text()

        if self.add_z_dimension:
            dim = pc_types.Dimension()
            dim.create_dimension(assembly_layout)
            dim.obj_bp.rotation_euler.x = math.radians(90)
            dim.obj_bp.rotation_euler.y = math.radians(-90)
            dim.obj_y.location.y = .2
            dim.obj_bp.parent = sel_obj
            dim.obj_bp.location = assembly.obj_bp.location
            dim.obj_x.location.x = assembly.obj_z.location.z
            dim.update_dim_text()            
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'add_x_dimension')
        layout.prop(self,'add_y_dimension')
        layout.prop(self,'add_z_dimension')      


class pc_assembly_OT_add_title_block(bpy.types.Operator):
    bl_idname = "pc_assembly.add_title_block"
    bl_label = "Add Title Block"
    bl_description = "This adds a title block to the current layout"
    bl_options = {'UNDO'}

    title_blocks: CollectionProperty(name="Title Blocks",type=Item)
    title_block_index: IntProperty(name="Title Block Index")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self,context,event):
        PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),'pc_lib','assets','Title Blocks')
        files = os.listdir(PATH)
        for file in files:
            filename, ext = os.path.splitext(file)
            tb = self.title_blocks.add()
            tb.name = filename
        if len(self.title_blocks) == 1:
            self.add_title_block(context)
            return {'FINISHED'}
        else:
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=200)

    def add_title_block(self,context):
        tb = self.title_blocks[self.title_block_index]
        assembly_layout = pc_types.Assembly_Layout(context.scene)
        title_block = pc_types.Title_Block()
        title_block.create_title_block(assembly_layout,tb.name)

    def execute(self, context):
        self.add_title_block(context)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.template_list("PC_UL_combobox"," ", self, "title_blocks", self, "title_block_index",rows=5,type='DEFAULT')


class pc_assembly_OT_add_annotation(bpy.types.Operator):
    bl_idname = "pc_assembly.add_add_annotation"
    bl_label = "Add Annotation"
    bl_description = "This adds an annotation to the current layout"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        assembly_layout = pc_types.Assembly_Layout(context.scene)

        annotation = pc_types.Annotation()
        annotation.create_annotation(assembly_layout)
        annotation.obj_bp.rotation_euler.x = math.radians(90)
        if context.object:
            annotation.obj_bp.parent = context.object
            for child in annotation.obj_bp.children:
                if child.type == 'EMPTY':
                    child.hide_viewport = True
                    child.hide_viewport = True
            annotation.obj_x.hide_viewport = False
        return {'FINISHED'}


class pc_assembly_OT_show_dimension_properties(Operator):
    bl_idname = "pc_assembly.show_dimension_properties"
    bl_label = "Show Dimension Properties"
    bl_description = "This will show the dimension properties"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    update_all_dimensions: BoolProperty(name="Update All Dimensions")

    dimension = None

    def execute(self, context):
        self.dimension.update_dim_text()
        if self.update_all_dimensions:
            dimensions = []
            for obj in context.scene.objects:
                if 'IS_DIMENSION' in obj and obj not in dimensions:
                    dimensions.append(obj)

            for obj in dimensions:
                dim = pc_types.Dimension(obj)
                font_size = dim.get_prompt("Font Size")
                line_thickness = dim.get_prompt("Line Thickness")
                arrow_height = dim.get_prompt("Arrow Height")
                arrow_length = dim.get_prompt("Arrow Length")
                if font_size:
                    font_size.set_value(self.dimension.get_prompt("Font Size").get_value())
                if line_thickness:
                    line_thickness.set_value(self.dimension.get_prompt("Line Thickness").get_value())
                if arrow_height:
                    arrow_height.set_value(self.dimension.get_prompt("Arrow Height").get_value())
                if arrow_length:
                    arrow_length.set_value(self.dimension.get_prompt("Arrow Length").get_value())               

        return {'FINISHED'}

    def check(self, context):
        self.dimension.update_dim_text()
        return True

    def invoke(self,context,event):
        dim_bp = pc_utils.get_assembly_bp(context.object)
        self.dimension = pc_types.Dimension(dim_bp)  
        self.dimension.update_dim_text()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        self.dimension.draw_ui(context,layout)
        layout.prop(self,'update_all_dimensions')


class pc_assembly_OT_show_annotation_properties(Operator):
    bl_idname = "pc_assembly.show_annotation_properties"
    bl_label = "Show Annotation Properties"
    bl_description = "This will show the annotation properties"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    update_all_annotations: BoolProperty(name="Update All Dimensions")

    annotation = None

    def execute(self, context):
        if self.update_all_annotations:
            annotations = []
            for obj in context.scene.objects:
                if 'IS_ANNOTATION' in obj and obj not in annotations:
                    annotations.append(obj)

            for obj in annotations:
                dim = pc_types.Dimension(obj)
                font_size = dim.get_prompt("Font Size")
                line_thickness = dim.get_prompt("Line Thickness")
                arrow_height = dim.get_prompt("Arrow Height")
                arrow_length = dim.get_prompt("Arrow Length")
                if font_size:
                    font_size.set_value(self.annotation.get_prompt("Font Size").get_value())
                if line_thickness:
                    line_thickness.set_value(self.annotation.get_prompt("Line Thickness").get_value())
                if arrow_height:
                    arrow_height.set_value(self.annotation.get_prompt("Arrow Height").get_value())
                if arrow_length:
                    arrow_length.set_value(self.annotation.get_prompt("Arrow Length").get_value())               
        
        return {'FINISHED'}

    def check(self, context):
        return True

    def invoke(self,context,event):
        dim_bp = pc_utils.get_assembly_bp(context.object)
        self.annotation = pc_types.Annotation(dim_bp)  
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        self.annotation.draw_ui(context,layout)
        layout.prop(self,'update_all_annotations')


class pc_assembly_OT_show_title_block_properties(Operator):
    bl_idname = "pc_assembly.show_title_block_properties"
    bl_label = "Show Title Block Properties"
    bl_description = "This will show the title block properties properties"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    title_block = None

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        return True

    def invoke(self,context,event):
        dim_bp = pc_utils.get_assembly_bp(context.object)
        self.title_block = pc_types.Title_Block(dim_bp)  
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        self.title_block.draw_ui(context,layout)


class pc_assembly_OT_make_assembly_static(Operator):
    bl_idname = "pc_assembly.make_assembly_static"
    bl_label = "Make Assembly Static"
    bl_description = "This will apply all modifers and drivers for the assembly"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    update_all_assemblies: BoolProperty(name="Update All Assemblies")

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def execute(self, context):
        obj_list = []
        if self.update_all_assemblies:
            obj_list = context.view_layer.objects
        else:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            obj_list = self.get_children_list(obj_bp,obj_list)

        for obj in obj_list:
            if obj.animation_data:
                for driver in obj.animation_data.drivers:
                    obj.driver_remove(driver.data_path)
            obj.select_set(True)
            context.view_layer.objects.active = obj

            if obj.type == 'MESH':
                if obj.data.shape_keys:
                    bpy.ops.object.shape_key_add(from_mix=True)
                    for index, key in enumerate(obj.data.shape_keys.key_blocks):
                        obj.active_shape_key_index = 0
                        bpy.ops.object.shape_key_remove(all=False)                    
                    
            if obj.type == 'CURVE':
                bpy.ops.object.convert(target='MESH')
                
            for mod in obj.modifiers:
                if mod.type == 'HOOK':
                    bpy.ops.object.modifier_apply(modifier=mod.name)

            obj.lock_location = (False,False,False)
            obj.lock_scale = (False,False,False)
            obj.lock_rotation = (False,False,False)

        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'update_all_assemblies')


class pc_assembly_OT_convert_to_object(Operator):
    bl_idname = "pc_assembly.convert_to_object"
    bl_label = "Convert to Object"
    bl_description = "This will apply all modifers and drivers for the assembly and create one object"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    update_all_assemblies: BoolProperty(name="Update All Assemblies")

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def execute(self, context):
        obj_list = []
        if self.update_all_assemblies:
            obj_list = context.view_layer.objects
        else:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            obj_list = self.get_children_list(obj_bp,obj_list)

        for obj in obj_list:
            if obj.animation_data:
                for driver in obj.animation_data.drivers:
                    obj.driver_remove(driver.data_path)
            obj.select_set(True)
            context.view_layer.objects.active = obj

            if obj.type == 'MESH':
                if obj.data.shape_keys:
                    bpy.ops.object.shape_key_add(from_mix=True)
                    for index, key in enumerate(obj.data.shape_keys.key_blocks):
                        obj.active_shape_key_index = 0
                        bpy.ops.object.shape_key_remove(all=False)                    
                    
            if obj.type == 'CURVE':
                if obj.data.bevel_mode == 'OBJECT' and obj.data.bevel_object != None:
                    context.view_layer.objects.active = obj
                    bpy.ops.object.convert(target='MESH')
                
            for mod in obj.modifiers:
                try:
                    context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except:
                    print("ERROR APPLYING MODIFIER",mod,obj)

            obj.lock_location = (False,False,False)
            obj.lock_scale = (False,False,False)
            obj.lock_rotation = (False,False,False)

        bpy.ops.object.select_all(action='DESELECT')

        empty_list = []
        bp_list = []
        for obj in obj_list:
            if obj.type == 'MESH':
                if obj.hide_viewport:
                    empty_list.append(obj)
                elif 'IS_OPENING_MESH' in obj:
                    empty_list.append(obj)
                else:
                    context.view_layer.objects.active = obj
                    obj.select_set(True)
            if obj.type == 'EMPTY' and 'obj_bp' not in obj:
                empty_list.append(obj)
            if obj.type == 'EMPTY' and 'obj_bp' in obj:
                bp_list.append(obj)
        
        bpy.ops.object.join()

        mesh_obj = context.active_object

        mat = mesh_obj.matrix_world.copy()

        pc_utils.delete_obj_list(empty_list)
        pc_utils.delete_obj_list(bp_list)

        mesh_obj.matrix_world = mat

        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'update_all_assemblies')


class pc_assembly_OT_return_to_model_view(Operator):
    bl_idname = "pc_assembly.return_to_model_view"
    bl_label = "Return to Model View"
    bl_description = "This will return to model space"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    dimension = None

    def execute(self, context):
        for index, scene in enumerate(bpy.data.scenes):
            if not scene.pyclone.is_view_scene:
                context.window.scene = scene
                context.window.scene.pyclone.scene_index = index

        return {'FINISHED'}


class pc_assembly_OT_create_assembly_view(Operator):
    bl_idname = "pc_assembly.create_assembly_view"
    bl_label = "Create Assembly View"
    bl_description = "This will create an assembly view"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    view: bpy.props.EnumProperty(name="View",
                                 items=[('TOP',"Top","Create Top View"),
                                        ('FRONT',"Front","Create Front View"),
                                        ('SIDE',"Side","Create Side View")],
                                 default='TOP')

    dimension = None

    @classmethod
    def poll(cls, context):
        if context.object:
            if context.object.pyclone.is_view_object:
                return True
        return False

    def execute(self, context):
        assembly_layout = pc_types.Assembly_Layout(context.scene)
        view_obj = context.object

        assembly_bp = context.object.instance_collection.pyclone.assembly_bp
        assembly = pc_types.Assembly(assembly_bp)
        
        obj = assembly_layout.add_assembly_view(context.object.instance_collection)
        obj.location = view_obj.location
        obj.scale = view_obj.scale

        if self.view == 'TOP':
            offset_dim = (assembly.obj_z.location.z + math.fabs(assembly.obj_y.location.y) + pc_unit.inch(10)) * view_obj.scale.z
            obj.location.z += offset_dim
            obj.rotation_euler.x = math.radians(90)
            
        if self.view == 'FRONT':
            pass

        if self.view == 'SIDE':
            offset_dim = (assembly.obj_x.location.x + math.fabs(assembly.obj_y.location.y) + pc_unit.inch(10)) * view_obj.scale.x
            obj.location.x += offset_dim
            obj.rotation_euler.z = math.radians(-90)

        return {'FINISHED'}


class pc_assembly_OT_create_pdf_of_assembly_views(bpy.types.Operator):
    bl_idname = "pc_assembly.create_pdf_of_assembly_views"
    bl_label = "Create PDF of assembly views"
    bl_description = "Create PDF of assembly views"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def render_scene(self,context,scene):
        context.window.scene = scene
        filepath = os.path.join(bpy.app.tempdir,scene.name + " View")
        render = bpy.context.scene.render
        render.use_file_extension = True
        render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return filepath

    def create_pdf(self,context,images):
        
        filepath = os.path.join(bpy.app.tempdir,"2D Views.PDF")
        filename = "2D Views.PDF"
        if context.scene.pyclone.page_size == 'LETTER':
            c = canvas.Canvas(filepath, pagesize=landscape(letter))
            width, height = landscape(letter)
        else:
            c = canvas.Canvas(filepath, pagesize=landscape(legal))
            width, height = landscape(legal)

        for image in images:
            c.drawImage(image,0,0,width=width, height=height, mask='auto',preserveAspectRatio=True)  
            c.showPage()
        c.save()

        os.system('start "Title" /D "' + bpy.app.tempdir + '" "' + filename + '"')

    def execute(self, context):
        images = []
        for scene in bpy.data.scenes:
            if scene.pyclone.is_view_scene:
                file_path = self.render_scene(context,scene)
                images.append(file_path + ".png")

        self.create_pdf(context,images)
        return {'FINISHED'}

class pc_assembly_OT_show_global_dimension_properties(Operator):
    bl_idname = "pc_assembly.show_global_dimension_properties"
    bl_label = "Show Global Dimension Properties"
    bl_description = "This will update all of the dimensions properties in the current scene"
    bl_options = {'UNDO'}

    obj_bp_name: StringProperty(name="Base Point Name")

    update_all_assemblies: BoolProperty(name="Update All Assemblies")

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def execute(self, context):
        obj_list = []
        if self.update_all_assemblies:
            obj_list = bpy.data.objects
        else:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            obj_list = self.get_children_list(obj_bp,obj_list)

        for obj in obj_list:
            if obj.animation_data:
                for driver in obj.animation_data.drivers:
                    obj.driver_remove(driver.data_path)
            obj.select_set(True)
            context.view_layer.objects.active = obj

            if obj.type == 'MESH':
                if obj.data.shape_keys:
                    bpy.ops.object.shape_key_add(from_mix=True)
                    for index, key in enumerate(obj.data.shape_keys.key_blocks):
                        obj.active_shape_key_index = 0
                        bpy.ops.object.shape_key_remove(all=False)                    
                    
            if obj.type == 'CURVE':
                bpy.ops.object.convert(target='MESH')
                
            for mod in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod.name)

            obj.lock_location = (False,False,False)
            obj.lock_scale = (False,False,False)
            obj.lock_rotation = (False,False,False)

        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'update_all_assemblies')

classes = (
    Item,
    pc_assembly_OT_create_new_assembly,
    pc_assembly_OT_delete_assembly,
    pc_assembly_OT_select_base_point,
    pc_assembly_OT_duplicate_assembly,
    pc_assembly_OT_refresh_vertex_groups,
    pc_assembly_OT_add_object,
    pc_assembly_OT_connect_mesh_to_hooks_in_assembly,
    pc_assembly_OT_create_assembly_script,
    pc_assembly_OT_select_parent_assembly,
    pc_assembly_OT_create_assembly_layout,
    pc_assembly_OT_delete_assembly_layout,
    pc_assembly_OT_create_assembly_dimension,
    pc_assembly_OT_show_annotation_properties,
    pc_assembly_OT_show_dimension_properties,
    pc_assembly_OT_show_title_block_properties,
    pc_assembly_OT_add_title_block,
    pc_assembly_OT_add_annotation,
    pc_assembly_OT_make_assembly_static,
    pc_assembly_OT_convert_to_object,
    pc_assembly_OT_return_to_model_view,
    pc_assembly_OT_create_assembly_view,
    pc_assembly_OT_create_render_view,
    pc_assembly_OT_create_pdf_of_assembly_views
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()