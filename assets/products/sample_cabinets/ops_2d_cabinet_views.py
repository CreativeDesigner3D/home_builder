import bpy
import math
from pc_lib import pc_utils, pc_types, pc_unit
from . import const_cabinets as const

def get_wall_assemblies():
    walls = []
    for obj in bpy.data.objects:
        wall_bp = pc_utils.get_bp_by_tag(obj,'IS_WALL_BP')
        if wall_bp and wall_bp not in walls:
            walls.append(wall_bp)
    return walls

def show_all_walls(context):
    walls = []
    for obj in context.scene.objects:
        if 'IS_WALL_BP' in obj:
            wall_is_hidden = False
            for child in obj.children:
                if child.type == 'MESH' and child.hide_get():
                    wall_is_hidden = True
            if wall_is_hidden:
                walls.append(obj)
    
    for wall in walls:
        bpy.ops.home_builder.show_hide_walls(wall_obj_bp=wall.name)

class hb_sample_cabinets_OT_create_2d_plan_view(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.create_2d_plan_view"
    bl_label = "Create Cabinet 2D Plan View"

    def get_center_of_room(self,context):
        wall_groups = []
        height = 0

        wall_assemblies = []
        wall_bps = []
        for obj in context.visible_objects:
            if obj.parent and 'IS_WALL_BP' in obj.parent and obj.parent not in wall_bps:
                wall_bps.append(obj.parent)
                wall_assemblies.append(pc_types.Assembly(obj.parent))

        first_wall = wall_assemblies[0]
        if first_wall:
            largest_x = first_wall.obj_bp.matrix_world[0][3]
            largest_y = first_wall.obj_bp.matrix_world[1][3]
            smallest_x = first_wall.obj_bp.matrix_world[0][3]
            smallest_y = first_wall.obj_bp.matrix_world[1][3]
            tallest_wall = first_wall.obj_z.location.z

        for assembly in wall_assemblies:
            start_point = (assembly.obj_bp.matrix_world[0][3],assembly.obj_bp.matrix_world[1][3],0)
            end_point = (assembly.obj_x.matrix_world[0][3],assembly.obj_x.matrix_world[1][3],0)
            if assembly.obj_z.location.z > tallest_wall:
                tallest_wall = assembly.obj_z.location.z
            
            if start_point[0] > largest_x:
                largest_x = start_point[0]
            if start_point[1] > largest_y:
                largest_y = start_point[1]
            if start_point[0] < smallest_x:
                smallest_x = start_point[0]
            if start_point[1] < smallest_y:
                smallest_y = start_point[1]
            if end_point[0] > largest_x:
                largest_x = end_point[0]
            if end_point[1] > largest_y:
                largest_y = end_point[1]
            if end_point[0] < smallest_x:
                smallest_x = end_point[0]
            if end_point[1] < smallest_y:
                smallest_y = end_point[1]

        if largest_x > smallest_x:
            x = (largest_x - smallest_x)/2 + smallest_x
        else:
            x = (smallest_x - largest_x)/2 + largest_x

        if largest_y > smallest_y:
            y = (largest_y - smallest_y)/2 + smallest_y
        else:
            y = (smallest_y - largest_y)/2 + largest_y

        z = tallest_wall - pc_unit.inch(.01)

        width = largest_x - smallest_x
        depth = largest_y - smallest_y
        if width > depth:
            size = width
        else:
            size = depth
        return x,y,z,size        

    def add_title_block(self,view_layout,description,number,scale):
        title_block = pc_types.Title_Block()
        title_block.create_title_block(view_layout,title_block_name="Title Block")

    def create_text_annotation(self,view_layout,parent,x_loc,y_loc,z_loc,text):
        font_curve = bpy.data.curves.new(type="FONT", name=text)
        font_curve.body = text
        font_curve.align_x = 'CENTER'
        font_curve.align_y = 'CENTER'
        font_curve.size = .15
        font_obj = bpy.data.objects.new(name="Font Object", object_data=font_curve)
        view_layout.dimension_collection.objects.link(font_obj) 
        font_obj.parent = parent 
        font_obj.location.x = x_loc
        font_obj.location.y = y_loc
        font_obj.location.z = z_loc
        font_obj.display.show_shadows = False
        font_obj.color = [0.000000, 0.000000, 0.000000, 1.000000]
        pc_utils.assign_pointer_to_object(font_obj,"Dimensions")
        return font_obj

    def create_wall_width_dim(self,view_layout,parent,y_loc,z_loc,width):
        dim = pc_types.Dimension()
        dim.create_dimension(view_layout)
        dim.obj_bp['PLAN_VIEW'] = True
        dim.obj_bp.rotation_euler.x = 0
        dim.obj_bp.rotation_euler.y = 0
        dim.obj_y.location.y = .2
        dim.obj_bp.parent = parent
        dim.obj_bp.location.y = y_loc
        dim.obj_bp.location.z = z_loc
        dim.obj_x.location.x = width
        dim.update_dim_text()
        return dim

    def add_wall_labels(self,wall_bp,view_layout):
        wall = pc_types.Assembly(wall_bp)
        wall_height = wall.obj_z.location.z + pc_unit.inch(3)
        wall_length = wall.obj_x.location.x
        wall_depth = wall.obj_y.location.y
        label = self.create_text_annotation(view_layout,wall.obj_bp,wall_length/2,wall_depth/2,wall_height,wall_bp.name)

    def add_wall_dimensions(self,wall_bp,view_layout):
        wall = pc_types.Assembly(wall_bp)
        wall_height = wall.obj_z.location.z + pc_unit.inch(3)
        wall_length = wall.obj_x.location.x
        wall_depth = wall.obj_y.location.y
        label = self.create_wall_width_dim(view_layout,wall.obj_bp,wall_depth,wall_height,wall_length)

    def create_plan_view_layout(self,context,walls):
        x,y,z,size = self.get_center_of_room(context)

        bpy.ops.object.select_all(action='DESELECT')
        longest_wall = pc_types.Assembly(walls[0]).obj_x.location.x
        for wall in walls:
            wall_assembly = pc_types.Assembly(wall)
            if wall_assembly.obj_x.location.x > longest_wall:
                longest_wall = wall_assembly.obj_x.location.x            
            for child in wall.children:
                if child.type == 'MESH':
                    child.hide_select = False
                    child.hide_viewport = False
                    child.select_set(True)                
            pc_utils.select_object_and_children(wall)     

        bpy.ops.collection.create(name="PLAN VIEW")

        obj = bpy.data.objects.new("PLAN EMPTY",None)
        collection = bpy.data.collections["PLAN VIEW"]  
        collection.pyclone.assembly_bp = obj

        bpy.ops.scene.new(type='EMPTY')
        layout = pc_types.Assembly_Layout(context.scene)
        layout.setup_assembly_layout()
        layout.scene.name = "00 Plan View"
        wall_view = layout.add_assembly_view(collection)

        for wall in walls:
            self.add_wall_labels(wall,layout)
            self.add_wall_dimensions(wall,layout)

        layout.add_layout_camera()
        layout.scene.world = self.model_scene.world
        layout.camera.rotation_euler = (0,0,0)
        layout.camera.location.x = x
        layout.camera.location.y = y
        layout.camera.location.z = z + pc_unit.inch(10)

        layout.scene.pyclone.numeric_page_scale = size * 2

        layout.scene.world.node_tree.nodes['Background'].inputs[1].default_value = 15
        layout.scene.render.film_transparent = True
        self.add_title_block(layout,"Plan View","1","")
        return layout.scene

    def execute(self, context):
        show_all_walls(context)
        self.model_scene = context.scene
        walls = get_wall_assemblies()
        scene = self.create_plan_view_layout(context,walls)
        context.window.scene = scene
        return {'FINISHED'}


class hb_sample_cabinets_OT_create_2d_elevation_views(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.create_2d_elevation_views"
    bl_label = "Create Cabinet 2D Elevation Views"

    def unlink_plan_view_annotations(self,collection,wall):
        plan_annotations = []
        for obj in collection.objects:
            if 'PLAN_VIEW' in obj:
                plan_annotations.append(obj)
                for child in obj.children:
                    plan_annotations.append(child)
            wall_bp = pc_utils.get_bp_by_tag(obj,'IS_WALL_BP')
            if ('IS_DIMENSION' not in obj) and ('IS_ANNOTATION' not in obj):
                continue
            if wall_bp.name != wall.obj_bp.name:
                plan_annotations.append(obj)
                for child in obj.children:
                    plan_annotations.append(child)                
        for anno in plan_annotations:
            if anno.name in collection.objects:
                collection.objects.unlink(anno)

    def get_wall_cabinets(self,wall,loc_sort='X'):
        """ This returns a sorted list of all of the assemblies base points
            parented to the wall
        """
        list_obj_bp = []
        for child in wall.obj_bp.children:
            cabinet_bp = pc_utils.get_bp_by_tag(child,const.CABINET_TAG)
            if cabinet_bp:
                list_obj_bp.append(child)
        if loc_sort == 'X':
            list_obj_bp.sort(key=lambda obj: obj.location.x, reverse=False)
        if loc_sort == 'Y':
            list_obj_bp.sort(key=lambda obj: obj.location.y, reverse=False)            
        if loc_sort == 'Z':
            list_obj_bp.sort(key=lambda obj: obj.location.z, reverse=False)
        return list_obj_bp

    def link_children_with_collection(self,obj,collection):
        if 'IS_HOLD_OUT' not in obj:     
            collection.objects.link(obj)
            for child in obj.children:
                self.link_children_with_collection(child,collection)

    def create_width_dim(self,view_layout,parent,length,leader_length):
        dim = pc_types.Dimension()
        dim.create_dimension(view_layout)
        dim.obj_bp.rotation_euler.x = math.radians(-90)
        dim.obj_bp.rotation_euler.y = 0
        dim.obj_y.location.y = leader_length
        dim.obj_bp.parent = parent
        dim.obj_x.location.x = length
        dim.flip_y()
        dim.update_dim_text()
        return dim

    def create_elevation_layout(self,context,wall):
        for scene in bpy.data.scenes:
            if not scene.pyclone.is_view_scene:
                context.window.scene = scene
                break
        collection = wall.create_assembly_collection(wall.obj_bp.name)
        left_wall_bp =  pc_utils.get_connected_left_wall_bp(wall)
        right_wall_bp =  pc_utils.get_connected_right_wall_bp(wall)

        if left_wall_bp:
            left_wall = pc_types.Assembly(left_wall_bp)
            for child in left_wall.obj_bp.children:
                if 'IS_ASSEMBLY_BP' in child:
                    assembly = pc_types.Assembly(child)
                    if child.location.x >= (left_wall.obj_x.location.x - assembly.obj_x.location.x - pc_unit.inch(10)):
                        self.link_children_with_collection(child,collection)

        if right_wall_bp:
            right_wall = pc_types.Assembly(right_wall_bp)
            for child in right_wall.obj_bp.children:
                if 'IS_ASSEMBLY_BP' in child:               
                    if child.location.x <= pc_unit.inch(10):
                        self.link_children_with_collection(child,collection)

        self.unlink_plan_view_annotations(collection,wall)
        bpy.ops.scene.new(type='EMPTY')
        layout = pc_types.Assembly_Layout(context.scene)
        layout.setup_assembly_layout()

        layout.scene.name = wall.obj_bp.name
        wall_view = layout.add_assembly_view(collection)

        layout.add_layout_camera()   
        layout.scene.world = self.model_scene.world
        layout.camera.parent = wall.obj_bp

        layout.scene.world.node_tree.nodes['Background'].inputs[1].default_value = 15
        layout.scene.render.film_transparent = True

        if wall.obj_x.location.x <= pc_unit.inch(150):
            layout.scene.pyclone.numeric_page_scale = 5
        else:
            layout.scene.pyclone.numeric_page_scale = 10

        layout.camera.location.x = wall.obj_x.location.x/2
        layout.camera.location.z = wall.obj_z.location.z/2
        layout.camera.location.y = -2.0573
        layout.camera.rotation_euler.x = math.radians(90)
        layout.camera.rotation_euler.y = 0
        layout.camera.rotation_euler.z = 0

        cabinet_bps = self.get_wall_cabinets(wall,loc_sort='X')
        for cabinet_bp in cabinet_bps:
            cabinet = pc_types.Assembly(cabinet_bp)
            dim = self.create_width_dim(layout,cabinet.obj_bp,cabinet.obj_x.location.x,.15)
            dim.obj_bp.location.y = cabinet.obj_y.location.y/2
        self.create_width_dim(layout,wall.obj_bp,wall.obj_x.location.x,.25)

        title_block = pc_types.Title_Block()
        title_block.create_title_block(layout,title_block_name="Title Block") 

    def execute(self, context):
        show_all_walls(context)

        self.model_scene = context.scene
        walls = get_wall_assemblies()

        for wall in walls:
            self.create_elevation_layout(context,pc_types.Assembly(wall))

        context.window_manager.pyclone.scene_index = len(bpy.data.scenes) - 1

        return {'FINISHED'}
    
classes = (
    hb_sample_cabinets_OT_create_2d_plan_view,
    hb_sample_cabinets_OT_create_2d_elevation_views
)

register, unregister = bpy.utils.register_classes_factory(classes)    