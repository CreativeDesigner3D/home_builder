import math
import gpu
from . import pc_utils
# import mathutils
from mathutils import Vector
# import bgl
# import blf
from mathutils.geometry import intersect_line_plane
import gpu
from bpy_extras import view3d_utils
from gpu_extras.presets import draw_circle_2d

RADIUS = 20
STEPS = 12

def draw_callback_px(self, context):
    

    if self is None: print("self is None")
    color = (0, 1, 0, 1)
    if self.hit_grid: color = (0, 0, 1, 1)

    if self.hit_object or self.hit_grid:
        region = pc_utils.get_3d_view_region(context)
        region3D = region.data
        circle_loc = view3d_utils.location_3d_to_region_2d(region, region3D, self.hit_location)
        if circle_loc is not None:
            gpu.state.line_width_set(4.0)
            draw_circle_2d(circle_loc, color, RADIUS)
           
#ray_cast adding the view point in the result
def ray_cast(context, depsgraph, position):
    region = pc_utils.get_3d_view_region(context)
    region3D = region.data

    #The view point of the user
    view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, position)
    #The direction indicated by the mouse position from the current view
    view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, position)

    return *context.scene.ray_cast(depsgraph, view_point, view_vector), view_point

#try to find the best hit point on the scene
def best_hit(context, depsgraph, mouse_pos):
    
    #at first we raycast from the mouse position as it is
    result, location, normal, index, object, matrix, view_point = \
        ray_cast(context, depsgraph, mouse_pos)

    if result:
        print("RESULT FOUND EARLY",object)
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
            ray_cast(context, depsgraph, pos)
        if result and (best_object is None or (view_point - location).length < best_distance):
            best_ditance = (view_point - location).length
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
    region = pc_utils.get_3d_view_region(context)
    region3D = region.data

    #first snap to vertices
    #loop over vertices and keep the one which is closer once projected on screen
    snap_location = None
    best_distance = 0
    for co in vertices:
        co2D = view3d_utils.location_3d_to_region_2d(region, region3D, co)
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
        v = search_edge_pos(region, region3D, self.mouse_pos, co1, co2)
        v2D = view3d_utils.location_3d_to_region_2d(region, region3D, v)
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
    region = pc_utils.get_3d_view_region(context)
    region3D = region.data

    view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
    view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)

    if region3D.is_orthographic_side_view:
        #ortho side view special case
        norm = view_vector
    else:
        #other views
        norm = Vector((0,0,1))

    #At which scale the grid is
    # (log10 is 1 for meters => 10 ** (1 - 1) = 1
    # (log10 is 0 for 10 centimeters => 10 ** (0 - 1) = 0.1
    scale = 10 ** (round(math.log10(region3D.view_distance)) - 1)
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

def main(self, crtl_is_pressed, context,exclude_object):
    self.hit_location = None
    self.hit_grid = False
    
    depsgraph = context.evaluated_depsgraph_get()

    result, location, index, object, view_point = \
        best_hit(context, depsgraph, self.mouse_pos)
    
    self.hit_location = location
    self.hit_face_index = index
    self.hit_object = object
    self.view_point = view_point
    
    if self.hit_object is not exclude_object:
        if result and crtl_is_pressed:
            snap_to_object(self, context, depsgraph)
        elif not result:
            snap_to_grid(self, context, crtl_is_pressed)
        