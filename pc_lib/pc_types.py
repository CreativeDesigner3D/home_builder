import bpy
import os, math
from . import pc_utils, pc_unit

class Assembly:

    coll = None
    obj_bp = None
    obj_x = None
    obj_y = None
    obj_z = None
    obj_prompts = None
    prompts = {}

    def __init__(self,obj_bp=None,filepath=""):
        if obj_bp:
            self.coll = bpy.context.view_layer.active_layer_collection.collection
            self.obj_bp = obj_bp
            for child in obj_bp.children:
                if "obj_x" in child:
                    self.obj_x = child
                if "obj_y" in child:
                    self.obj_y = child           
                if "obj_z" in child:
                    self.obj_z = child
                if "obj_prompts" in child:
                    self.obj_prompts = child    

        if filepath:
            self.coll = bpy.context.view_layer.active_layer_collection.collection

            with bpy.data.libraries.load(filepath, False, False) as (data_from, data_to):
                data_to.objects = data_from.objects

            for obj in data_to.objects:
                if "obj_bp" in obj and obj["obj_bp"] == True:
                    self.obj_bp = obj
                if "obj_x" in obj and obj["obj_x"] == True:
                    self.obj_x = obj
                if "obj_y" in obj and obj["obj_y"] == True:
                    self.obj_y = obj
                if "obj_z" in obj and obj["obj_z"] == True:
                    self.obj_z = obj
                if "obj_prompts" in obj and obj["obj_prompts"] == True:
                    self.obj_prompts = obj
                
                self.coll.objects.link(obj)

    def update_vector_groups(self):
        """ 
        This is used to add all of the vector groups to 
        an assembly this should be called everytime a new object
        is added to an assembly.
        """
        vgroupslist = []
        objlist = []
        
        for child in self.obj_bp.children:
            if child.type == 'EMPTY' and 'obj_prompts' not in child:
                vgroupslist.append(child.name)
            if child.type == 'MESH':
                objlist.append(child)
        
        for obj in objlist:
            for vgroup in vgroupslist:
                if vgroup not in obj.vertex_groups:
                    obj.vertex_groups.new(name=vgroup)

    def create_assembly(self,assembly_name="New Assembly"):
        """ 
        This creates the basic structure for an assembly.
        This must be called first when creating an assembly from a script.
        """
        bpy.ops.object.select_all(action='DESELECT')

        self.coll = bpy.context.view_layer.active_layer_collection.collection

        self.obj_bp = bpy.data.objects.new(assembly_name,None)
        self.obj_bp.location = (0,0,0)
        self.obj_bp["obj_bp"] = True
        self.obj_bp.empty_display_type = 'ARROWS'
        self.obj_bp.empty_display_size = .1           
        self.coll.objects.link(self.obj_bp)
        self.obj_bp['IS_ASSEMBLY_BP'] = True

        self.obj_x = bpy.data.objects.new("OBJ_X",None)
        self.obj_x.location = (0,0,0)
        self.obj_x.parent = self.obj_bp
        self.obj_x["obj_x"] = True
        self.obj_x.empty_display_type = 'SPHERE'
        self.obj_x.empty_display_size = .1  
        self.obj_x.lock_location[0] = False       
        self.obj_x.lock_location[1] = True
        self.obj_x.lock_location[2] = True
        self.obj_x.lock_rotation[0] = True     
        self.obj_x.lock_rotation[1] = True   
        self.obj_x.lock_rotation[2] = True      
        self.coll.objects.link(self.obj_x)

        self.obj_y = bpy.data.objects.new("OBJ_Y",None)
        self.obj_y.location = (0,0,0)
        self.obj_y.parent = self.obj_bp
        self.obj_y["obj_y"] = True
        self.obj_y.empty_display_type = 'SPHERE'
        self.obj_y.empty_display_size = .1     
        self.obj_y.lock_location[0] = True       
        self.obj_y.lock_location[1] = False
        self.obj_y.lock_location[2] = True
        self.obj_y.lock_rotation[0] = True     
        self.obj_y.lock_rotation[1] = True   
        self.obj_y.lock_rotation[2] = True                    
        self.coll.objects.link(self.obj_y)      

        self.obj_z = bpy.data.objects.new("OBJ_Z",None)
        self.obj_z.location = (0,0,0)
        self.obj_z.parent = self.obj_bp
        self.obj_z["obj_z"] = True
        self.obj_z.empty_display_type = 'SINGLE_ARROW'
        self.obj_z.empty_display_size = .2     
        self.obj_z.lock_location[0] = True
        self.obj_z.lock_location[1] = True
        self.obj_z.lock_location[2] = False
        self.obj_z.lock_rotation[0] = True     
        self.obj_z.lock_rotation[1] = True   
        self.obj_z.lock_rotation[2] = True               
        self.coll.objects.link(self.obj_z)

        self.obj_prompts = bpy.data.objects.new("OBJ_PROMPTS",None)
        self.obj_prompts.location = (0,0,0)
        self.obj_prompts.parent = self.obj_bp
        self.obj_prompts.empty_display_size = 0      
        self.obj_prompts.lock_location[0] = True
        self.obj_prompts.lock_location[1] = True
        self.obj_prompts.lock_location[2] = True
        self.obj_prompts.lock_rotation[0] = True     
        self.obj_prompts.lock_rotation[1] = True   
        self.obj_prompts.lock_rotation[2] = True           
        self.obj_prompts["obj_prompts"] = True
        self.coll.objects.link(self.obj_prompts)

    def create_assembly_collection(self,name):
        bpy.ops.object.select_all(action='DESELECT')
        pc_utils.select_object_and_children(self.obj_bp)
        bpy.ops.collection.create(name=name)

        collection = bpy.data.collections[name]
        collection.pyclone.assembly_bp = self.obj_bp
        return collection

    def create_cube(self,name="Cube",size=(0,0,0)):
        """ This will create a cube mesh and assign mesh hooks
        """
        # When assigning vertices to a hook 
        # the transformation is made so the size must be 0     
        obj_mesh = pc_utils.create_cube_mesh("Cube",size)
        self.add_object(obj_mesh)

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([2,3,6,7])

        hook = obj_mesh.modifiers.new('YHOOK','HOOK')
        hook.object = self.obj_y
        hook.vertex_indices_set([1,2,5,6])

        hook = obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

        return obj_mesh

    def add_prompt(self,name,prompt_type,value,combobox_items=[]):
        prompt = self.obj_prompts.pyclone.add_prompt(prompt_type,name)
        prompt.set_value(value)
        if prompt_type == 'COMBOBOX':
            for item in combobox_items: 
                i = prompt.combobox_items.add()
                i.name = item
        return prompt

    def add_empty(self,obj_name):
        obj = bpy.data.objects.new(obj_name,None)
        self.add_object(obj)
        return obj

    def add_light(self,obj_name,light_type):
        light = bpy.data.lights.new(obj_name,light_type)
        obj = bpy.data.objects.new(obj_name,light)
        self.add_object(obj)
        return obj

    def add_object(self,obj):
        obj.location = (0,0,0)
        obj.parent = self.obj_bp
        self.coll.objects.link(obj)
        self.update_vector_groups()

    def add_assembly(self,assembly):
        if assembly.obj_bp is None:
            if hasattr(assembly,'draw'):
                assembly.draw()
        assembly.obj_bp.location = (0,0,0)
        assembly.obj_bp.parent = self.obj_bp
        return assembly

    def add_assembly_from_file(self,filepath):
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects

        obj_bp = None

        for obj in data_to.objects:
            if not obj.parent:
                obj_bp = obj
            self.coll.objects.link(obj)

        obj_bp.parent = self.obj_bp
        return obj_bp

    def add_object_from_file(self,filepath):
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            self.coll.objects.link(obj)
            obj.parent = self.obj_bp
            return obj

    def set_name(self,name):
        self.obj_bp.name = name

    def get_prompt(self,name):
        if name in self.obj_prompts.pyclone.prompts:
            return self.obj_prompts.pyclone.prompts[name]
        
        for calculator in self.obj_prompts.pyclone.calculators:
            if name in calculator.prompts:
                return calculator.prompts[name]

    def get_calculator(self,name):
        if name in self.obj_prompts.pyclone.calculators:
            return self.obj_prompts.pyclone.calculators[name]

    def update_calculators(self):
        for calculator in self.obj_prompts.pyclone.calculators:
            calculator.calculate()

    def set_prompts(self):
        for key in self.prompts:
            if key in self.obj_prompts.pyclone.prompts:
                if key in self.obj_prompts.pyclone.prompts:
                    prompt = self.obj_prompts.pyclone.prompts[key]
                    prompt.set_value(self.prompts[key])

    def get_prompt_dict(self):
        prompt_dict = {}
        for prompt in self.obj_prompts.pyclone.prompts:
            prompt_dict[prompt.name] = prompt.get_value()
        return prompt_dict

    def loc_x(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_bp.location.x = value
        else:
            self.obj_bp.pyclone.loc_x(expression,variables)

    def loc_y(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_bp.location.y = value
        else:
            self.obj_bp.pyclone.loc_y(expression,variables)

    def loc_z(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_bp.location.z = value
        else:
            self.obj_bp.pyclone.loc_z(expression,variables)           

    def rot_x(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_bp.rotation_euler.x = value
        else:
            self.obj_bp.pyclone.rot_x(expression,variables)             

    def rot_y(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_bp.rotation_euler.y = value
        else:
            self.obj_bp.pyclone.rot_y(expression,variables)      

    def rot_z(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_bp.rotation_euler.z = value
        else:
            self.obj_bp.pyclone.rot_z(expression,variables)      

    def dim_x(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_x.location.x = value
        else:
            self.obj_x.pyclone.loc_x(expression,variables)          

    def dim_y(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_y.location.y = value
        else:
            self.obj_y.pyclone.loc_y(expression,variables)    

    def dim_z(self,expression="",variables=[],value=0):
        if expression == "":
            self.obj_z.location.z = value
        else:
            self.obj_z.pyclone.loc_z(expression,variables)                                                                      


class Assembly_Layout():

    VISIBLE_LINESET_NAME = "Visible Lines"
    HIDDEN_LINESET_NAME = "Hidden Lines"
    HIDDEN_LINE_DASH_PX = 10
    HIDDEN_LINE_GAP_PX = 10

    scene = None
    camera = None
    dimension_collection = None

    def __init__(self,scene=None):
        self.scene = scene
        self.camera = scene.camera
        for collection in self.scene.collection.children:
            if collection.pyclone.is_dimension_collection:
                self.dimension_collection = collection
                break

    def create_linestyles(self):
        linestyles = bpy.data.linestyles
        linestyles.new(self.VISIBLE_LINESET_NAME)
        
        hidden_linestyle = linestyles.new(self.HIDDEN_LINESET_NAME)
        hidden_linestyle.use_dashed_line = True
        hidden_linestyle.dash1 = self.HIDDEN_LINE_DASH_PX
        hidden_linestyle.dash2 = self.HIDDEN_LINE_DASH_PX
        hidden_linestyle.dash3 = self.HIDDEN_LINE_DASH_PX
        hidden_linestyle.gap1 = self.HIDDEN_LINE_GAP_PX
        hidden_linestyle.gap2 = self.HIDDEN_LINE_GAP_PX
        hidden_linestyle.gap3 = self.HIDDEN_LINE_GAP_PX

    def create_linesets(self):
        f_settings = self.scene.view_layers[0].freestyle_settings
        linestyles = bpy.data.linestyles
        
        visible_lineset = f_settings.linesets.new(self.VISIBLE_LINESET_NAME)
        visible_lineset.linestyle = linestyles[self.VISIBLE_LINESET_NAME]
        visible_lineset.select_by_collection = True
        visible_lineset.collection_negation = 'EXCLUSIVE'
        visible_lineset.collection = self.dimension_collection

        hidden_lineset = f_settings.linesets.new(self.HIDDEN_LINESET_NAME)
        hidden_lineset.linestyle = linestyles[self.HIDDEN_LINESET_NAME]
        
        hidden_lineset.select_by_visibility = True
        hidden_lineset.visibility = 'HIDDEN'
        hidden_lineset.select_by_edge_types = True
        hidden_lineset.select_by_face_marks = False
        hidden_lineset.select_by_collection = True
        hidden_lineset.select_by_image_border = False
        
        hidden_lineset.select_silhouette = True
        hidden_lineset.select_border = False
        hidden_lineset.select_contour = False
        hidden_lineset.select_suggestive_contour = False
        hidden_lineset.select_ridge_valley = False
        hidden_lineset.select_crease = False
        hidden_lineset.select_edge_mark = True
        hidden_lineset.select_external_contour = False
        hidden_lineset.select_material_boundary = False
        hidden_lineset.collection_negation = 'EXCLUSIVE'
        hidden_lineset.collection = self.dimension_collection

    def clear_unused_linestyles(self):
        for linestyle in bpy.data.linestyles:
            if linestyle.users == 0:
                bpy.data.linestyles.remove(linestyle)

    def setup_assembly_layout(self):
        self.create_linestyles()

        self.dimension_collection = bpy.data.collections.new(self.scene.name + ' DIM')
        self.dimension_collection.pyclone.is_dimension_collection = True
        bpy.context.view_layer.active_layer_collection.collection.children.link(self.dimension_collection)

        props = self.scene.pyclone
        props.is_view_scene = True
        self.scene.render.use_freestyle = True
        view_settings = self.scene.view_settings
        view_settings.view_transform = 'Standard'
        view_settings.look = 'High Contrast'

        self.create_linesets()

    def add_assembly_view(self,collection):
        obj = bpy.data.objects.new(collection.name,None)
        obj.instance_type = 'COLLECTION'
        obj.instance_collection = collection
        obj.empty_display_size = .01
        obj.location = (0,0,0)
        obj.rotation_euler = (0,0,0)
        self.scene.view_layers[0].active_layer_collection.collection.objects.link(obj)  
        obj.select_set(True)
        obj.pyclone.is_view_object = True
        return obj

    def add_layout_camera(self):
        cam = bpy.data.cameras.new('Camera ' + self.scene.name)
        cam.type = 'ORTHO'
        self.camera = bpy.data.objects.new('Camera ' + self.scene.name,cam)
        self.camera.location.x = 0.13951
        self.camera.location.y = -2.0573
        self.camera.location.z = 0.10793
        self.camera.rotation_euler.x = math.radians(90)
        self.camera.rotation_euler.y = 0
        self.camera.rotation_euler.z = 0
        self.scene.view_layers[0].active_layer_collection.collection.objects.link(self.camera)  
        self.scene.render.resolution_x = 1920
        self.scene.render.resolution_y = 1486
        self.scene.camera = self.camera

        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'window': window, 'screen': screen, 'area': area}
                    bpy.ops.view3d.view_camera(override)
                    bpy.ops.view3d.view_center_camera(override)   
                    break          

    def add_3d_layout_camera(self):
        spd = bpy.context.space_data
        bpy.ops.object.camera_add(align='VIEW')
        camera = bpy.context.active_object
        camera["PROMPT_ID"] = "camera_presets.camera_properties"   
        bpy.ops.view3d.camera_to_view()
        camera.data.clip_start = spd.clip_start
        camera.data.clip_end = spd.clip_end
        camera.data.ortho_scale = 200.0
        camera.data.sensor_width = 72  
        camera.data.lens = spd.lens
        spd.region_3d.view_camera_offset = [0,0]
        spd.region_3d.view_camera_zoom = 29.0746         

        self.scene.render.resolution_x = 1920
        self.scene.render.resolution_y = 1486
  

class Title_Block(Assembly):

    obj_drawing_title = None
    obj_description = None
    obj_scale = None
    obj_drawn_by = None
    obj_drawing_number = None
    obj_revision_number = None
    obj_original_date = None
    obj_revision_date = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if self.obj_bp:
            for child in obj_bp.children:
                if "IS_DRAWING_TITLE" in child:
                    self.obj_drawing_title = child
                if "IS_DESCRIPTION" in child:
                    self.obj_description = child         
                if "IS_SCALE" in child:
                    self.obj_scale = child         
                if "IS_DRAWN_BY" in child:
                    self.obj_drawn_by = child         
                if "IS_DRAWING_NUMBER" in child:
                    self.obj_drawing_number = child        
                if "IS_REVISION_NUMBER" in child:
                    self.obj_revision_number = child          
                if "IS_ORIGINAL_DATE" in child:
                    self.obj_original_date = child             
                if "IS_REVISION_DATE" in child:
                    self.obj_revision_date = child                  
                if child.type == 'FONT':
                    self.obj_text = child   

    def create_title_block(self,layout_view,title_block_name="Title Block"):
        collection = layout_view.dimension_collection

        PATH = os.path.join(os.path.dirname(__file__),'assets','Title Blocks',title_block_name + ".blend")

        with bpy.data.libraries.load(PATH, False, False) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            if "obj_bp" in obj:
                self.obj_bp = obj            
            if "obj_x" in obj:
                self.obj_x = obj
            if "obj_y" in obj:
                self.obj_y = obj           
            if "obj_z" in obj:
                self.obj_z = obj
            if "obj_prompts" in obj:
                self.obj_prompts = obj       
            if "IS_DRAWING_TITLE" in obj:
                self.obj_drawing_title = obj
            if "IS_DESCRIPTION" in obj:
                self.obj_description = obj         
            if "IS_SCALE" in obj:
                self.obj_scale = obj         
            if "IS_DRAWN_BY" in obj:
                self.obj_drawn_by = obj         
            if "IS_DRAWING_NUMBER" in obj:
                self.obj_drawing_number = obj        
            if "IS_REVISION_NUMBER" in obj:
                self.obj_revision_number = obj          
            if "IS_ORIGINAL_DATE" in obj:
                self.obj_original_date = obj             
            if "IS_REVISION_DATE" in obj:
                self.obj_revision_date = obj  
            obj["PROMPT_ID"] = 'pc_assembly.show_title_block_properties'                           
            collection.objects.link(obj)

        self.obj_bp.parent = layout_view.camera
        if bpy.context.scene.pyclone.page_size == 'LETTER':
            self.obj_bp.location.x = -0.13959
            self.obj_bp.location.y = -0.108
            if layout_view.camera.type == 'ORTHO':
                self.obj_bp.location.z = -1.001
            else:
                self.obj_bp.location.z = -0.19328
            self.obj_x.location.x = pc_unit.inch(11)
            self.obj_y.location.y = pc_unit.inch(8.5)
        else:
            self.obj_bp.location.x = -0.177502
            self.obj_bp.location.y = -0.108
            self.obj_bp.location.z = -1.001
            self.obj_x.location.x = pc_unit.inch(14)
            self.obj_y.location.y = pc_unit.inch(8.5)

        for child in self.obj_bp.children:
            if child.type == 'EMPTY':
                child.hide_viewport = True

    def draw_ui(self,context,layout):
        row = layout.row()
        row.label(text="Drawing Title:")
        row.prop(self.obj_drawing_title.data,'body',text="")

        row = layout.row()
        row.label(text="Description:")
        row.prop(self.obj_description.data,'body',text="")

        row = layout.row()
        row.label(text="Scale:")
        row.prop(self.obj_scale.data,'body',text="")

        row = layout.row()
        row.label(text="Drawn By:")
        row.prop(self.obj_drawn_by.data,'body',text="")

        row = layout.row()
        row.label(text="Drawing Number:")
        row.prop(self.obj_drawing_number.data,'body',text="")

        row = layout.row()
        row.label(text="Revision Number:")
        row.prop(self.obj_revision_number.data,'body',text="")

        row = layout.row()
        row.label(text="Original Date:")
        row.prop(self.obj_original_date.data,'body',text="")                                                

        row = layout.row()
        row.label(text="Revision Date:")
        row.prop(self.obj_revision_date.data,'body',text="")  

class Annotation(Assembly):

    obj_text = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if self.obj_bp:
            for child in obj_bp.children:
                if child.type == 'FONT':
                    self.obj_text = child   

    def create_annotation(self,layout_view=None):
        PATH = os.path.join(os.path.dirname(__file__),'assets',"Annotation_Arrow.blend")

        with bpy.data.libraries.load(PATH, False, False) as (data_from, data_to):
            data_to.objects = data_from.objects

        if layout_view:
            collection = layout_view.dimension_collection
        else:
            collection = bpy.context.view_layer.active_layer_collection.collection

        for obj in data_to.objects:
            if "obj_bp" in obj:
                self.obj_bp = obj     
                self.obj_bp['IS_ANNOTATION'] = True         
            if "obj_x" in obj:
                self.obj_x = obj
            if "obj_y" in obj:
                self.obj_y = obj           
            if "obj_z" in obj:
                self.obj_z = obj
            if "obj_prompts" in obj:
                self.obj_prompts = obj         
            if obj.type == 'FONT':
                self.obj_text = obj     
            obj["PROMPT_ID"] = 'pc_assembly.show_annotation_properties'                       
            collection.objects.link(obj)

    def draw_ui(self,context,layout):
        arrow_height = self.get_prompt("Arrow Height")
        arrow_length = self.get_prompt("Arrow Length")
        line_thickness = self.get_prompt("Line Thickness")

        row = layout.row()
        row.label(text="Annotation Text:")
        row.prop(self.obj_text.data,'body',text="")

        row = layout.row() 
        row.label(text="Arrow Size:")
        row.prop(arrow_height,'distance_value',text="Height")     
        row.prop(arrow_length,'distance_value',text="Length")  

        row = layout.row()
        row.label(text="Line Thickness:")
        row.prop(line_thickness,'distance_value',text="")   

        row = layout.row()
        row.label(text="Flip Text:")
        row.prop(self.obj_text.pyclone,'flip_x',text="X")            
        row.prop(self.obj_text.pyclone,'flip_y',text="Y")     
        
class Dimension(Assembly):

    obj_text = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if self.obj_bp:
            for child in obj_bp.children:
                if child.type == 'FONT':
                    self.obj_text = child     

    def flip_x(self):
        self.obj_text.scale.x = -1

    def flip_y(self):
        self.obj_text.scale.y = -1

    def create_dimension(self,layout_view=None):
        PATH = os.path.join(os.path.dirname(__file__),'assets',"Dimension_Arrow.blend")

        with bpy.data.libraries.load(PATH, link=False, relative=False) as (data_from, data_to):
            data_to.objects = data_from.objects

        if layout_view:
            collection = layout_view.dimension_collection
        else:
            collection = bpy.context.view_layer.active_layer_collection.collection
        for obj in data_to.objects:
            if "obj_bp" in obj:
                self.obj_bp = obj          
                self.obj_bp['IS_DIMENSION'] = True  
            if "obj_x" in obj:
                self.obj_x = obj
            if "obj_y" in obj:
                self.obj_y = obj           
            if "obj_z" in obj:
                self.obj_z = obj
            if "obj_prompts" in obj:
                self.obj_prompts = obj    
            if obj.type == 'FONT':
                self.obj_text = obj            
            obj["PROMPT_ID"] = "pc_assembly.show_dimension_properties"
            collection.objects.link(obj)

        self.get_prompt("Font Size").set_value(.07)
        self.get_prompt("Horizontal Line Location").set_value(.05)
        self.get_prompt("Line Thickness").set_value(.002)
        self.get_prompt("Arrow Height").set_value(.03)
        self.get_prompt("Arrow Length").set_value(.03)

    def update_dim_text(self):
        #TODO: Setup all unit types
        if bpy.context.scene.unit_settings.system == 'METRIC':
            text = str(round(pc_unit.meter_to_millimeter(self.obj_x.location.x),2))
            self.obj_text.data.body = text + 'mm'
        else:
            text = str(round(pc_unit.meter_to_inch(self.obj_x.location.x),2))
            self.obj_text.data.body = text + '"'
        bpy.context.view_layer.update()

        div_factor = 1
        if self.obj_bp.parent:
            div_factor = self.obj_bp.parent.scale.x

        self.obj_bp.hide_viewport = False
        self.obj_x.hide_viewport = False
        self.obj_y.hide_viewport = False
        self.obj_z.hide_viewport = False
        text_width = self.get_prompt("Text Width")
        text_width.set_value((self.obj_text.dimensions.x/div_factor) + .05)
        for child in self.obj_bp.children:
            if child.type == 'EMPTY':
                child.empty_display_size = .00001
                # child.hide_viewport = True
        # if self.obj_y.location.y < 0:
        #     hll = self.get_prompt('Horizontal Line Location')
        #     hll.set_value(hll.get_value()*-1)

    def draw_ui(self,context,layout):
        arrow_height = self.get_prompt("Arrow Height")
        arrow_length = self.get_prompt("Arrow Length")
        extend_first_line_amount = self.get_prompt("Extend First Line Amount")
        extend_second_line_amount = self.get_prompt("Extend Second Line Amount")
        line_thickness = self.get_prompt("Line Thickness")

        row = layout.row()
        row.label(text="Dimension Length:")
        row.prop(self.obj_x,'location',index=0,text="")

        row = layout.row()
        row.label(text="Leader Length:")
        row.prop(self.obj_y,'location',index=1,text="")   

        row = layout.row() 
        row.label(text="Arrow Size:")
        row.prop(arrow_height,'distance_value',text="Height")     
        row.prop(arrow_length,'distance_value',text="Length")      

        row = layout.row() 
        row.label(text="Extend Line:")
        row.prop(extend_first_line_amount,'distance_value',text="Line 1")     
        row.prop(extend_second_line_amount,'distance_value',text="Line 2")     

        row = layout.row()
        row.label(text="Line Thickness:")
        row.prop(line_thickness,'distance_value',text="")   

        row = layout.row()
        row.label(text="Flip Text:")
        row.prop(self.obj_text.pyclone,'flip_x',text="X")            
        row.prop(self.obj_text.pyclone,'flip_y',text="Y")               