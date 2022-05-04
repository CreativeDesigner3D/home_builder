import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
import time

class Cube(pc_types.Assembly):

    def draw(self):
        start_time = time.time()
        self.create_assembly("Cube")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        obj_mesh = self.create_cube()

        print("CUBE: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Stud(pc_types.Assembly):

    def draw(self):
        start_time = time.time()
        self.create_assembly("Stud")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        quantity = self.add_prompt("Quantity",'QUANTITY',1)
        array_offset = self.add_prompt("Array Offset",'DISTANCE',pc_unit.inch(16))

        qty = quantity.get_var("qty")
        array_offset = array_offset.get_var("array_offset")

        obj_mesh = self.create_cube()

        array = obj_mesh.modifiers.new('Quantity','ARRAY')
        array.use_constant_offset = True
        array.use_relative_offset = False
        array.constant_offset_displace[0] = 0
        array.constant_offset_displace[1] = 0
        obj_mesh.pyclone.modifier(array,'count',-1,'qty',[qty])
        obj_mesh.pyclone.modifier(array,'constant_offset_displace',2,'array_offset',[array_offset])

        print("STUD: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Brick(pc_types.Assembly):

    def draw(self):
        start_time = time.time()
        self.create_assembly("Stud")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        x_quantity = self.add_prompt("X Quantity",'QUANTITY',1)
        x_offset = self.add_prompt("X Offset",'DISTANCE',pc_unit.inch(0))
        z_quantity = self.add_prompt("Z Quantity",'QUANTITY',1)
        z_offset = self.add_prompt("Z Offset",'DISTANCE',pc_unit.inch(0))

        x_quantity = x_quantity.get_var("x_quantity")
        x_offset = x_offset.get_var("x_offset")
        z_quantity = z_quantity.get_var("z_quantity")
        z_offset = z_offset.get_var("z_offset")

        obj_mesh = self.create_cube(name="Brick")

        x_array = obj_mesh.modifiers.new('X Quantity','ARRAY')
        x_array.use_constant_offset = True
        x_array.use_relative_offset = False
        x_array.constant_offset_displace[0] = 0
        x_array.constant_offset_displace[1] = 0            
        obj_mesh.pyclone.modifier(x_array,'count',-1,'x_quantity',[x_quantity])
        obj_mesh.pyclone.modifier(x_array,'constant_offset_displace',0,'x_offset',[x_offset])

        z_array = obj_mesh.modifiers.new('Z Quantity','ARRAY')
        z_array.use_constant_offset = True
        z_array.use_relative_offset = False
        z_array.constant_offset_displace[0] = 0
        z_array.constant_offset_displace[1] = 0        
        obj_mesh.pyclone.modifier(z_array,'count',-1,'z_quantity',[z_quantity])
        obj_mesh.pyclone.modifier(z_array,'constant_offset_displace',2,'z_offset',[z_offset])

        print("STUD: Draw Time --- %s seconds ---" % (time.time() - start_time))        