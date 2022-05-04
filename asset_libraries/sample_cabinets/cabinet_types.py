from .pc_lib import pc_types, pc_unit
from . import cabinet_assemblies

class Standard_Cabinet(pc_types.Assembly):
    
    width = pc_unit.inch(18)
    height = pc_unit.inch(34)
    depth = pc_unit.inch(21)

    def __init__(self):
        pass

    def draw(self):
        self.create_assembly("Base Cabinet")

        self.obj_x.location.x = self.width
        self.obj_y.location.y = -self.depth
        self.obj_z.location.z = self.height

        self.add_prompt("Toe Kick Height",'DISTANCE',pc_unit.inch(4))
        self.add_prompt("Toe Kick Setback",'DISTANCE',pc_unit.inch(4))

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')  
        tkh = self.get_prompt("Toe Kick Height").get_var('tkh') 
        tk_setback = self.get_prompt("Toe Kick Setback").get_var('tk_setback') 

        carcass = cabinet_assemblies.add_design_carcass(self)
        carcass.set_name("Design Carcass")
        carcass.dim_x('width',[width])
        carcass.dim_y('depth',[depth])
        carcass.dim_z('height-tkh',[height,tkh])
        carcass.loc_z('tkh',[tkh])

        base_assembly = cabinet_assemblies.add_base_assembly(self)
        base_assembly.set_name("Base Assembly")
        base_assembly.dim_x('width',[width])
        base_assembly.dim_y('depth+tk_setback',[depth,tk_setback])
        base_assembly.dim_z('tkh',[height,tkh])        