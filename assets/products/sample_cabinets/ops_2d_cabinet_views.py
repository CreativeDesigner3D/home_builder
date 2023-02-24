import bpy
from pc_lib import pc_utils, pc_types, pc_unit

class hb_sample_cabinets_OT_create_2d_plan_view(bpy.types.Operator):
    bl_idname = "hb_sample_cabinets.create_2d_plan_view"
    bl_label = "Create Cabinet 2D Plan Views"

    def show_all_walls(self,context):
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

    def get_wall_assemblies(self):
        walls = []
        for obj in bpy.data.objects:
            wall_bp = pc_utils.get_bp_by_tag(obj,'IS_WALL_BP')
            if wall_bp and wall_bp not in walls:
                walls.append(wall_bp)
        return walls

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
        # wall_number = wall.obj_bp.hb_cabinet.wall_number
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
        self.show_all_walls(context)
        self.model_scene = context.scene
        walls = self.get_wall_assemblies()
        scene = self.create_plan_view_layout(context,walls)
        context.window.scene = scene
        return {'FINISHED'}

classes = (
    hb_sample_cabinets_OT_create_2d_plan_view,
)

register, unregister = bpy.utils.register_classes_factory(classes)    