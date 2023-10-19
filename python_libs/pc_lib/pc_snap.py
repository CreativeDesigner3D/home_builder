import bpy
import math
import gpu
from . import pc_utils, pc_unit, pc_types, pc_placement_utils
# import mathutils
from mathutils import Vector
import bgl
import blf
from mathutils.geometry import intersect_line_plane
import gpu
from bpy_extras import view3d_utils
from gpu_extras.presets import draw_circle_2d
from bpy_extras.view3d_utils import location_3d_to_region_2d

RADIUS = 50
STEPS = 6

def draw_callback_px(self, context):
    if self is None: print("self is None")
    color = (0, 1, 0, 1)
    if self.hit_grid: color = (0, 0, 1, 1)

    if self.blf_text != "":
        blf.color(0, 0, 0, 0, 1.0)
        blf.size(0, 14, 72)
        blf.enable(0,blf.SHADOW)
        blf.enable(0,blf.WORD_WRAP)
        blf.word_wrap(0,1000)
        blf.position(0,self.mouse_pos[0]+10,self.mouse_pos[1]+80,0)
        blf.shadow(0,0,0,0,0,.25)
        blf.shadow_offset(0,1,-1)
        blf.draw(0,self.blf_text)
    
    if self.hit_object or self.hit_grid:
        circle_loc = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, self.hit_location)
        if circle_loc is not None:
            pass
            # gpu.state.line_width_set(1.0)
            # draw_circle_2d(circle_loc, color, RADIUS/2)

            # blf.color(0, 0, 0, 0, 1.0)
            # blf.size(0, 14, 72)
            # blf.enable(0,blf.SHADOW)
            # blf.position(0,circle_loc[0],circle_loc[1]+10,0)
            # blf.shadow(0,0,0,0,0,.25)
            # blf.shadow_offset(0,1,-1)
            # blf.draw(0,self.blf_text)

#ray_cast adding the view point in the result
def ray_cast(context, depsgraph, position,region):

    #The view point of the user
    view_point = view3d_utils.region_2d_to_origin_3d(region, region.data, position)
    #The direction indicated by the mouse position from the current view
    view_vector = view3d_utils.region_2d_to_vector_3d(region, region.data, position)

    return *context.scene.ray_cast(depsgraph, view_point, view_vector), view_point

#try to find the best hit point on the scene
def best_hit(context, depsgraph, mouse_pos,region):
    
    context.view_layer.update() 
    
    #at first we raycast from the mouse position as it is
    result, location, normal, index, object, matrix, view_point = \
        ray_cast(context, depsgraph, mouse_pos,region)

    if result:
        if 'HB_CURRENT_DRAW_OBJ' not in object:
            return result, location, index, object, view_point

    #but if we are near but outside the object surface, we need to inspect around the 
    #mouse position and keep the closest location
    best_result = False
    best_location = best_index = best_object = None
    best_distance = 0

    angle = 0
    delta_angle = 2 * math.pi / STEPS
    for i in range(STEPS):
        
        pos = mouse_pos + RADIUS * Vector((math.cos(angle), math.sin(angle)))
        result, location, normal, index, object, matrix, view_point = \
            ray_cast(context, depsgraph, pos, region)
        if object and 'HB_CURRENT_DRAW_OBJ' not in object:
            if result and (best_object is None or (view_point - location).length < best_distance):
                best_distance = (view_point - location).length
                best_result = True
                best_location = location
                best_index = index
                best_object = object
        angle += delta_angle

    return best_result, best_location, best_index, best_object, view_point

def search_edge_pos(region, region3D, mouse, v1, v2, epsilon = 0.0001):
    #dichotomic search for the nearest point along an edge, compare to the mouse position
    #not optimized, but easy to write... ;)
    while (v1 - v2).length > epsilon:
        v12D = view3d_utils.location_3d_to_region_2d(region, region3D, v1)
        v22D = view3d_utils.location_3d_to_region_2d(region, region3D, v2)
        if v12D is None: return v2
        if v22D is None: return v1
        if (v12D - mouse).length < (v22D - mouse).length:
            v2 = (v1 + v2) / 2
        else:
            v1 = (v1 + v2) / 2
    return v1

def snap_to_geometry(self, context, vertices):
    #first snap to vertices
    #loop over vertices and keep the one which is closer once projected on screen
    snap_location = None
    best_distance = 0
    for co in vertices:
        co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
        if co2D is not None:
            distance = (co2D - self.mouse_pos).length
            if distance < RADIUS and (snap_location is None or distance < best_distance):
                snap_location = co
                best_distance = distance
                
    if snap_location is not None:
        self.hit_location = snap_location
        return
    
    #then, if no vertex is found, try to snap to edges
    for co1, co2 in zip(vertices[1:]+vertices[:1], vertices):
        v = search_edge_pos(self.region, self.region.data, self.mouse_pos, co1, co2)
        v2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, v)
        if v2D is not None:
            distance = (v2D - self.mouse_pos).length
            if distance < RADIUS and (snap_location is None or distance < best_distance):
                snap_location = v
                best_distance = distance

    if snap_location is not None:
        self.hit_location = snap_location
        return

def snap_to_object(self, context, depsgraph):

    if self.hit_object.type == 'MESH':
        #the object need to be evaluated (if modifiers, for instance)
        evaluated = self.hit_object.evaluated_get(depsgraph)

        data = evaluated.data

        polygon = data.polygons[self.hit_face_index]
        matrix = evaluated.matrix_world
        
        #get evaluated vertices of the wanted polygon, in world coordinates
        vertices = [matrix @ data.vertices[i].co for i in polygon.vertices]
        
        snap_to_geometry(self, context, vertices)    

def floor_fit(v, scale):
    return math.floor(v / scale) * scale

def ceil_fit(v, scale):
    return math.ceil(v / scale) * scale

def snap_to_grid(self, context, crtl_is_pressed):

    view_point = view3d_utils.region_2d_to_origin_3d(self.region, self.region.data, self.mouse_pos)
    view_vector = view3d_utils.region_2d_to_vector_3d(self.region, self.region.data, self.mouse_pos)

    if self.region.data.is_orthographic_side_view:
        #ortho side view special case
        norm = view_vector
    else:
        #other views
        norm = Vector((0,0,1))

    #At which scale the grid is
    # (log10 is 1 for meters => 10 ** (1 - 1) = 1
    # (log10 is 0 for 10 centimeters => 10 ** (0 - 1) = 0.1
    scale = 10 ** (round(math.log10(self.region.data.view_distance)) - 1)
    #... to be improved with grid scale, subdivisions, etc.

    #here no ray cast, but intersection between the view line and the grid plane        
    max_float =1.0e+38
    co = intersect_line_plane(view_point, view_point + max_float * view_vector, (0,0,0), norm)

    if co is not None:
        self.hit_grid = True
        if crtl_is_pressed:
            #depending on the view angle, create the list of vertices for a plane around the hit point
            #which size is adapted to the view scale (view distance)
            if abs(norm.x) > 0:
                vertices = [Vector((0, floor_fit(co.y, scale), floor_fit(co.z, scale))), Vector((0, floor_fit(co.y, scale), ceil_fit(co.z, scale))), Vector((0, ceil_fit(co.y, scale), ceil_fit(co.z, scale))), Vector((0, ceil_fit(co.y, scale), floor_fit(co.z, scale)))]
            elif abs(norm.y) > 0:
                vertices = [Vector((floor_fit(co.x, scale), 0, floor_fit(co.z, scale))), Vector((floor_fit(co.x, scale), 0, ceil_fit(co.z, scale))), Vector((ceil_fit(co.x, scale), 0, ceil_fit(co.z, scale))), Vector((ceil_fit(co.x, scale), 0, floor_fit(co.z, scale)))]
            else:
                vertices = [Vector((floor_fit(co.x, scale), floor_fit(co.y, scale), 0)), Vector((floor_fit(co.x, scale), ceil_fit(co.y, scale), 0)), Vector((ceil_fit(co.x, scale), ceil_fit(co.y, scale), 0)), Vector((ceil_fit(co.x, scale), floor_fit(co.y, scale), 0))]
            #and snap on this plane
            snap_to_geometry(self, context, vertices)

        #if no snap or out of snapping, keep the co                
        if self.hit_location is None:
            self.hit_location = Vector(co)

def main(self, crtl_is_pressed, context):
    self.hit_location = None
    self.hit_grid = False
    
    depsgraph = context.evaluated_depsgraph_get()

    result, location, index, object, view_point = \
        best_hit(context, depsgraph, self.mouse_pos,self.region)
    
    self.hit_location = location
    self.hit_face_index = index
    self.hit_object = object
    self.view_point = view_point

    if result and crtl_is_pressed:
        snap_to_object(self, context, depsgraph)
    elif not result:
        snap_to_grid(self, context, crtl_is_pressed)
        

class Drop_Operator(bpy.types.Operator):

    #USED FOR PLACEMENT
    snap_cursor_to_cabinet: bpy.props.BoolProperty(name="Snap Cursor to Cabinet",default=False)
    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    region = None
    hit_location = (0,0,0)
    mouse_pos = Vector()
    hit_grid = False
    hit_object = None
    snap_line = None
    blf_text = ""
    typed_value = ""

    calculators = []

    def setup_drop_operator(self,context):
        self.region = pc_utils.get_3d_view_region(context)
        self.mouse_pos = Vector()
        self.hit_object = None

        if self.snap_cursor_to_cabinet:
            if self.obj_bp_name != "":
                obj_bp = bpy.data.objects[self.obj_bp_name]
            else:
                obj_bp = self.cabinet.obj_bp            
            region = context.region
            co = location_3d_to_region_2d(region,context.region_data,obj_bp.matrix_world.translation)
            region_offset = Vector((region.x,region.y))
            context.window.cursor_warp(*(co + region_offset))  

        curve = bpy.data.curves.new('SNAPLINE','CURVE')
        spline = curve.splines.new('BEZIER')
        spline.bezier_points.add(1)
        self.snap_line = bpy.data.objects.new('SNAPLINE',curve)
        self.snap_line.rotation_euler.y = math.radians(-90)
        self.snap_line.data.bevel_depth = pc_unit.inch(.25)
        self.snap_line.color = (0,0,0,1)
        self.snap_line.show_in_front = True
        self.snap_line['IS_WALL_SNAP_POINT'] = True
        context.view_layer.active_layer_collection.collection.objects.link(self.snap_line)

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

    def get_view_orientation_from_quaternion(self):
        view_quat = self.region.data.view_rotation
        r = lambda x: round(x, 3)
        view_rot = view_quat.to_euler()

        orientation_dict = {(0.0, 0.0, 0.0) : 'TOP',
                            (r(math.pi), 0.0, 0.0) : 'BOTTOM',
                            (r(math.pi/2), 0.0, 0.0) : 'FRONT',
                            (r(math.pi/2), 0.0, r(math.pi)) : 'BACK',
                            (r(math.pi/2), 0.0, r(-math.pi/2)) : 'LEFT',
                            (r(math.pi/2), 0.0, r(math.pi/2)) : 'RIGHT'}

        return orientation_dict.get(tuple(map(r, view_rot)), 'UNDEFINED')
    
    def get_calculators(self,obj):
        for calculator in obj.pyclone.calculators:
            self.calculators.append(calculator)
        for child in obj.children:
            self.get_calculators(child)

    def get_snap_location(self,selected_point):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        x = math.ceil(selected_point[0]/sv)
        y = math.ceil(selected_point[1]/sv)
        z = math.ceil(selected_point[2]/sv)
        return x*sv, y*sv, z*sv
    
    def get_snap_value(self,value):
        sv = bpy.context.scene.home_builder.wall_distance_snap_value
        return math.ceil(value/sv)*sv
    
    def set_type_value(self,event):
        if event.value == 'PRESS':
            if event.type == "ONE" or event.type == "NUMPAD_1":
                self.typed_value += "1"
            if event.type == "TWO" or event.type == "NUMPAD_2":
                self.typed_value += "2"
            if event.type == "THREE" or event.type == "NUMPAD_3":
                self.typed_value += "3"
            if event.type == "FOUR" or event.type == "NUMPAD_4":
                self.typed_value += "4"
            if event.type == "FIVE" or event.type == "NUMPAD_5":
                self.typed_value += "5"
            if event.type == "SIX" or event.type == "NUMPAD_6":
                self.typed_value += "6"
            if event.type == "SEVEN" or event.type == "NUMPAD_7":
                self.typed_value += "7"
            if event.type == "EIGHT" or event.type == "NUMPAD_8":
                self.typed_value += "8"
            if event.type == "NINE" or event.type == "NUMPAD_9":
                self.typed_value += "9"
            if event.type == "ZERO" or event.type == "NUMPAD_0":
                self.typed_value += "0"
            if event.type == "PERIOD" or event.type == "NUMPAD_PERIOD":
                last_value = self.typed_value[-1:]
                if last_value != ".":
                    self.typed_value += "."
            if event.type == 'BACK_SPACE':
                if self.typed_value != "":
                    self.typed_value = self.typed_value[:-1]

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and 'IS_OPENING_MESH' not in obj:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def set_child_properties(self,obj,parent):
        if not self.is_from_build_library:
            pc_utils.update_id_props(obj,parent)
        # home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'             
        for child in obj.children:
            self.set_child_properties(child,parent)

    def get_left_snap_point(self,snap_points):
        for index, sp in enumerate(snap_points):
            if sp.name == self.snap_line.name and index != 0:
                return snap_points[index-1]
        return None

    def get_right_snap_point(self,snap_points):
        for index, sp in enumerate(snap_points):
            if sp.name == self.snap_line.name and index != len(snap_points)-1:
                return snap_points[index+1]
        return None
    
    def wall_is_inside_corner(self,wall,direction='LEFT'):
        if direction == 'LEFT':
            left_angle = int(math.degrees(wall.get_prompt('Left Angle').get_value()))
            if left_angle == -45 or left_angle == 135:
                return True
        if direction == 'RIGHT':
            right_angle = int(math.degrees(wall.get_prompt('Right Angle').get_value()))
            if right_angle == 45 or right_angle == -135:
                return True
        return False

    def get_left_collision_info(self,wall):
        search_point_left = (self.snap_line.location.x,0,self.hit_location[2])
        left_assembly = pc_placement_utils.get_left_wall_collision_assembly_from_selected_point(wall,search_point_left,ignore_assembly = self.cabinet)
        snap_points = pc_placement_utils.get_snap_points(wall)
        left_sp = self.get_left_snap_point(snap_points)
        offset_amount = 0
        adj_assembly = None

        #GET LEFT SNAP LOCATION
        cal_left_x_snap = 0
        if left_assembly and left_sp:
            left_assembly_x_snap = left_assembly.obj_bp.location.x + left_assembly.obj_x.location.x
            left_snap_location = left_sp.location.x
            if left_assembly_x_snap > left_snap_location:
                cal_left_x_snap = left_assembly_x_snap
            else:
                cal_left_x_snap = left_snap_location
        elif left_assembly:
            cal_left_x_snap = left_assembly.obj_bp.location.x + left_assembly.obj_x.location.x
        elif left_sp:
            cal_left_x_snap = left_sp.location.x
        else:
            #CHECK NEXT WALL
            left_wall_bp = pc_utils.get_connected_left_wall_bp(wall)
            found_left_x = 0
            if left_wall_bp:
                left_wall = pc_types.Assembly(left_wall_bp)
                if self.wall_is_inside_corner(wall,'LEFT'):
                    left_assemblies = pc_placement_utils.get_wall_assemblies(left_wall)
                    left_assemblies.reverse()
                    #LOOK FOR ASSEMBLY ON NEXT WALL
                    for assembly_bp in left_assemblies:
                        assembly = pc_types.Assembly(assembly_bp)
                        if self.hit_location[2] > assembly.obj_bp.location.z and self.hit_location[2] < (assembly.obj_bp.location.z + assembly.obj_z.location.z):
                            if (assembly.obj_bp.location.x + assembly.obj_x.location.x) > left_wall.obj_x.location.x - math.fabs(self.cabinet.obj_y.location.y):
                                found_left_x = math.fabs(assembly.obj_y.location.y)
                                adj_assembly = assembly
                                break
                    #IF NO ASSEMBLY SET WALL OFFSET                
                    if found_left_x == 0:
                        offset_amount = pc_unit.inch(.5)

            cal_left_x_snap = found_left_x

        return cal_left_x_snap, offset_amount, adj_assembly 

    def get_right_collision_info(self,wall):
        wall_length = wall.obj_x.location.x
        if self.fill_on:
            search_point_right = (self.snap_line.location.x,0,self.hit_location[2])
        else:
            search_point_right = (self.snap_line.location.x+self.cabinet.obj_x.location.x+pc_unit.inch(3),0,self.hit_location[2])
        right_assembly = pc_placement_utils.get_right_wall_collision_assembly_from_selected_point(wall,search_point_right,ignore_assembly = self.cabinet)
        snap_points = pc_placement_utils.get_snap_points(wall)
        right_sp = self.get_right_snap_point(snap_points)
        offset_amount = 0
        adj_assembly = None

        cal_right_x_snap = 0
        if right_assembly and right_sp:
            if right_assembly.obj_bp.location.x < right_sp.location.x:
                cal_right_x_snap = right_assembly.obj_bp.location.x
            else:
                cal_right_x_snap = right_sp.location.x
        elif right_assembly:
            if round(right_assembly.obj_bp.rotation_euler.z,3) == round(math.radians(-90),3):
                cal_right_x_snap = right_assembly.obj_bp.location.x - math.fabs(right_assembly.obj_y.location.y)
            else:
                cal_right_x_snap = right_assembly.obj_bp.location.x
        elif right_sp:
            cal_right_x_snap = right_sp.location.x
        else:
            #CHECK NEXT WALL
            right_wall_bp = pc_utils.get_connected_right_wall_bp(wall)
            found_right_x = wall_length
            if right_wall_bp:      
                right_wall = pc_types.Assembly(right_wall_bp)
                if self.wall_is_inside_corner(wall,'RIGHT'):
                    right_assemblies = pc_placement_utils.get_wall_assemblies(right_wall)
                    #LOOK FOR ASSEMBLY ON RIGHT WALL
                    for assembly_bp in right_assemblies:
                        assembly = pc_types.Assembly(assembly_bp)
                        if self.hit_location[2] > assembly.obj_bp.location.z and self.hit_location[2] < (assembly.obj_bp.location.z + assembly.obj_z.location.z):
                            if assembly.obj_bp.location.x < math.fabs(self.cabinet.obj_y.location.y):
                                found_right_x = wall_length - math.fabs(assembly.obj_y.location.y)
                                adj_assembly = assembly
                                break
                    #IF NO ASSEMBLY SET WALL OFFSET
                    if found_right_x == wall_length:
                        offset_amount = pc_unit.inch(.5)
            cal_right_x_snap = found_right_x

        return cal_right_x_snap, offset_amount, adj_assembly
    
    def cancel_drop(self,context,obj_bp):
        pc_utils.delete_object_and_children(obj_bp)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW') 
        context.workspace.status_text_set(text=None)     
        return {'CANCELLED'}        