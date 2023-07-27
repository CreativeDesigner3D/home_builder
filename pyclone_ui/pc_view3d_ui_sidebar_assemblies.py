import bpy
import math
from pc_lib import pc_types, pc_utils, pc_unit
from .. import pyclone_utils

def draw_object_transform(context,layout,obj):
    if obj.type not in {'EMPTY','CAMERA','LIGHT'}:
        if 'hb_geo_part' in obj:
            for mod in obj.modifiers:
                if mod.type == 'NODES':
                    node = mod.node_group
                    col = layout.column(align=True)
                    col.label(text="Dimensions:")
                    row = col.row(align=True)
                    row.prop(mod,'["Input_2"]',text=node.inputs[1].name)
                    row.prop(mod,'["Input_5"]',text="",icon='MOD_MIRROR')

                    row = col.row(align=True)
                    row.prop(mod,'["Input_3"]',text=node.inputs[2].name)
                    row.prop(mod,'["Input_6"]',text="",icon='MOD_MIRROR')

                    row = col.row(align=True)
                    row.prop(mod,'["Input_4"]',text=node.inputs[3].name)
                    row.prop(mod,'["Input_7"]',text="",icon='MOD_MIRROR')

        else:
            if obj.scale.x != 1 or obj.scale.y != 1 or obj.scale.z != 1:
                props = layout.operator('object.transform_apply',text="Apply Scale",icon='ERROR')
                props.location = False
                props.rotation = False
                props.scale = True

            col = layout.column(align=True)
            col.label(text='Dimensions:')
            #X
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=0,text="")
            if obj.lock_scale[0]:
                row.label(text="X: " + str(round(pc_unit.meter_to_active_unit(obj.dimensions.x),4)))
            else:
                row.prop(obj,"dimensions",index=0,text="X")
            #Y
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=1,text="")
            if obj.lock_scale[1]:
                row.label(text="Y: " + str(round(pc_unit.meter_to_active_unit(obj.dimensions.y),4)))
            else:
                row.prop(obj,"dimensions",index=1,text="Y")
            #Z
            row = col.row(align=True)
            row.prop(obj,"lock_scale",index=2,text="")
            if obj.lock_scale[2]:
                row.label(text="Z: " + str(round(pc_unit.meter_to_active_unit(obj.dimensions.z),4)))
            else:
                row.prop(obj,"dimensions",index=2,text="Z")

    if obj.type == 'CAMERA':
        cam = obj.data
        row = layout.row()
        row.label(text="Size:")
        row.prop(cam, "display_size", text="")

    if obj.type == 'EMPTY':
        row = layout.row()
        row.label(text="Size:")            
        row.prop(obj, "empty_display_size", text="")            

    col1 = layout.row()
    col2 = col1.split()
    col = col2.column(align=True)
    col.label(text='Location:')
    #X
    row = col.row(align=True)
    row.prop(obj,"lock_location",index=0,text="")
    if obj.lock_location[0]:
        row.label(text="X: " + str(round(pc_unit.meter_to_active_unit(obj.location.x),4)))
    else:
        row.prop(obj,"location",index=0,text="X")
    #Y    
    row = col.row(align=True)
    row.prop(obj,"lock_location",index=1,text="")
    if obj.lock_location[1]:
        row.label(text="Y: " + str(round(pc_unit.meter_to_active_unit(obj.location.y),4)))
    else:
        row.prop(obj,"location",index=1,text="Y")
    #Z    
    row = col.row(align=True)
    row.prop(obj,"lock_location",index=2,text="")
    if obj.lock_location[2]:
        row.label(text="Z: " + str(round(pc_unit.meter_to_active_unit(obj.location.z),4)))
    else:
        row.prop(obj,"location",index=2,text="Z")
        
    col2 = col1.split()
    col = col2.column(align=True)
    col.label(text='Rotation:')
    #X
    row = col.row(align=True)
    row.prop(obj,"lock_rotation",index=0,text="")
    if obj.lock_rotation[0]:
        row.label(text="X: " + str(round(math.degrees(obj.rotation_euler.x),4)))
    else:
        row.prop(obj,"rotation_euler",index=0,text="X")
    #Y    
    row = col.row(align=True)
    row.prop(obj,"lock_rotation",index=1,text="")
    if obj.lock_rotation[1]:
        row.label(text="Y: " + str(round(math.degrees(obj.rotation_euler.y),4)))
    else:
        row.prop(obj,"rotation_euler",index=1,text="Y")
    #Z    
    row = col.row(align=True)
    row.prop(obj,"lock_rotation",index=2,text="")
    if obj.lock_rotation[2]:
        row.label(text="Y: " + str(round(math.degrees(obj.rotation_euler.z),4)))
    else:
        row.prop(obj,"rotation_euler",index=2,text="Z")

def draw_object_view_properties(context,layout,obj):
    col = layout.column(align=True)
    col.label(text="View Options:")
    row = col.row()
    row.prop(obj,'display_type',expand=True)
    row = col.row()
    # row.prop(obj,'hide_select')
    row.prop(obj,'hide_viewport')
    row.prop(obj,'hide_render')        

def draw_curve_properties(context,layout,obj):
    layout.label(text="Curve Options:")
    curve = obj.data
    row = layout.row()
    row.label(text="Type")
    row.prop(curve, "dimensions", expand=True)

    row = layout.row(align=True)
    row.label(text="Resolution")
    row.prop(curve, "resolution_u", text="Preview")
    row.prop(curve, "render_resolution_u", text="Render")  

    # layout.label(text="Geometry")    
    row = layout.row()
    row.label(text="Extrude")    
    row.prop(curve, "extrude",text="")
    row = layout.row()
    row.label(text="Offset")           
    row.prop(curve, "offset",text="")

    row = layout.row(align=True)
    row.label(text="Bevel")
    row.prop(curve, "bevel_depth", text="Depth")
    row.prop(curve, "bevel_resolution", text="Resolution")

    row = layout.row(align=True)
    row.label(text="Start/End")
    row.prop(curve, "bevel_factor_start", text="Start")
    row.prop(curve, "bevel_factor_end", text="End")

    row = layout.split(factor=0.5)
    row.label(text="Taper Object")
    row.prop(curve, "taper_object",text="")

    row = layout.split(factor=0.5)
    row.label(text="Bevel Object")        
    row.prop(curve, "bevel_object", text="")

    if curve.bevel_object is not None:
        row = layout.row()
        row.alignment = 'RIGHT'
        row.prop(curve, "use_fill_caps")

    row = layout.row()
    row.label(text="Fill Mode")
    row.prop(curve, "fill_mode",expand=True)
    row = layout.row()
    row.alignment = 'RIGHT'
    row.prop(curve, "use_fill_deform")

def draw_object_properties(context,layout,obj):
    # row = layout.row(align=True)
    # row.prop(obj.pyclone,'object_tabs',expand=True)

    if obj.pyclone.object_tabs == 'MAIN':
        layout.prop(obj,'name')
        draw_object_transform(context,layout,obj)
        draw_object_view_properties(context,layout,obj)


    if obj.pyclone.object_tabs == 'DATA':
        if obj.type == 'MESH':
            layout.label(text="Edit Mode Options",icon='EDITMODE_HLT')
            if obj.mode == 'EDIT':
                layout.operator('pc_object.toggle_edit_mode',text="Exit Edit Mode",icon='X').obj_name = obj.name
                vcol = layout.column(align=True)
                for vgroup in obj.vertex_groups:
                    count = 0
                    for vert in context.active_object.data.vertices:
                        for group in vert.groups:
                            if group.group == vgroup.index:
                                count += 1
                    vcol.operator('pc_object.assign_verties_to_vertex_group',text="Assign to - " + vgroup.name + " (" + str(count) + ")").vertex_group_name = vgroup.name
                vcol.separator()
                vcol.operator('pc_assembly.connect_meshes_to_hooks_in_assembly',text='Connect Hooks',icon='HOOK').obj_name = context.active_object.name
                props = vcol.operator('pc_assembly.refresh_vertex_groups',text="Refresh Vertex Groups",icon='FILE_REFRESH')
                props.obj_bp_name = obj.parent.name
                props.obj_mesh_name = obj.name
                vcol.operator('pc_object.clear_vertex_groups',text='Clear All Vertex Group Assignments',icon='X').obj_name = context.active_object.name   
            else:
                layout.operator('pc_object.toggle_edit_mode',text="Enter Edit Mode",icon='EDITMODE_HLT').obj_name = obj.name
        
        if obj.type == 'CURVE':
            layout.label(text="Edit Mode Options",icon='EDITMODE_HLT')
            if obj.mode == 'EDIT':
                layout.operator('pc_object.toggle_edit_mode',text="Exit Edit Mode",icon='X').obj_name = obj.name
                layout.operator('object.hook_add_selob',text="Hook to Selected Object",icon='HOOK').use_bone = False
            else:
                layout.operator('pc_object.toggle_edit_mode',text="Enter Edit Mode",icon='EDITMODE_HLT').obj_name = obj.name
                draw_curve_properties(context,layout,obj)

    if obj.pyclone.object_tabs == 'MATERIAL':

        layout.label(text="Material Assignment Options",icon='MATERIAL_DATA')     

        row = layout.row()
        row.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=3)

        col = row.column(align=True)
        col.operator("pc_material.add_material_slot", icon='ADD', text="").object_name = obj.name
        col.operator("object.material_slot_remove", icon='REMOVE', text="")

        slot = None
        if len(obj.material_slots) >= obj.active_material_index + 1:
            slot = obj.material_slots[obj.active_material_index]

        if slot:
            row = layout.row()
            if len(obj.pyclone.pointers) >= obj.active_material_index + 1:
                pointer_slot = obj.pyclone.pointers[obj.active_material_index]
                row.prop(pointer_slot,'name')
                row = layout.row()
                row.prop(pointer_slot,'pointer_name',text="Pointer")
            else:
                row.operator('pc_material.add_material_pointers').object_name = obj.name

        if obj.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")  

def draw_assembly_properties(context, layout, assembly):
    unit_system = context.scene.unit_settings.system
    scene_props = pyclone_utils.get_scene_props(context.scene)

    col = layout.column(align=True)
    box = col.box()
    row = box.row()
    row.label(text="Assembly Name: " + assembly.obj_bp.name)
    row.menu('VIEW3D_MT_assembly_menu',text="",icon='DOWNARROW_HLT')

    row = box.row(align=True)
    row.prop(scene_props,'assembly_tabs',expand=True)
    box = col.box()
    if scene_props.assembly_tabs == 'MAIN':
        box.prop(assembly.obj_bp,'name')

        col = box.column(align=True)
        col.label(text="Dimensions:")

        row1 = col.row(align=True)
        row1.prop(assembly.obj_x,'lock_location',index=0,text="")
        if assembly.obj_x.lock_location[0]:
            x = math.fabs(assembly.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))                 
            row1.label(text='X: ' + value)
        else:
            row1.prop(assembly.obj_x,'location',index=0,text="X")
            row1.prop(assembly.obj_x,'hide_viewport',text="")

        row1 = col.row(align=True)
        row1.prop(assembly.obj_y,'lock_location',index=1,text="")  
        if assembly.obj_y.lock_location[1]:
            y = math.fabs(assembly.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Y: ' + value)
        else:
            row1.prop(assembly.obj_y,'location',index=1,text="Y")
            row1.prop(assembly.obj_y,'hide_viewport',text="")

        row1 = col.row(align=True)
        row1.prop(assembly.obj_z,'lock_location',index=2,text="")              
        if assembly.obj_z.lock_location[2]:
            z = math.fabs(assembly.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))                 
            row1.label(text='Z: ' + value)
        else:
            row1.prop(assembly.obj_z,'location',index=2,text="Z")      
            row1.prop(assembly.obj_z,'hide_viewport',text="")                  

        col = box.column()
        s_col = col.split()
        s_col.prop(assembly.obj_bp,'location')
        s_col.prop(assembly.obj_bp,'rotation_euler',text="Rotation")

    if scene_props.assembly_tabs == 'PROMPTS':
        assembly.obj_prompts.pyclone.draw_prompts(box)

    if scene_props.assembly_tabs == 'OBJECTS':

        skip_names = {assembly.obj_bp.name,assembly.obj_x.name,assembly.obj_y.name,assembly.obj_z.name,assembly.obj_prompts.name}

        row = box.row()
        row.scale_y = 1.3
        row.label(text="Objects",icon='OUTLINER_OB_MESH')
        row.operator('pc_assembly.add_object',text="Add Object",icon='ADD')

        mesh_col = box.column(align=True)

        for child in assembly.obj_bp.children:
            if child.name not in skip_names:
                # if context.mode == 'EDIT_MESH' and child != context.active_object:
                #     continue

                row = mesh_col.row(align=True)
                if child == context.object:
                    row.label(text="",icon='RADIOBUT_ON')
                elif child in context.selected_objects:
                    row.label(text="",icon='DECORATE')
                else:
                    row.label(text="",icon='RADIOBUT_OFF')
                row.operator('pc_object.select_object',text=child.name,icon=pc_utils.get_object_icon(child)).obj_name = child.name
                row.prop(child.pyclone,'show_object_props',text="",icon='DISCLOSURE_TRI_DOWN' if child.pyclone.show_object_props else 'DISCLOSURE_TRI_RIGHT')
                if child.pyclone.show_object_props:
                    row = mesh_col.row()
                    row.label(text="",icon='BLANK1')
                    col = row.column(align=True)
                    box = col.box()
                    row = box.row()
                    row.prop(child.pyclone,'object_tabs',expand=True)
                    box = col.box()
                    draw_object_properties(context,box,child)
                   
    if scene_props.assembly_tabs == 'LOGIC':
        row = box.row()
        row.scale_y = 1.3
        row.prop(scene_props,'driver_tabs',text='')
        if scene_props.driver_tabs == 'LOC_X':
            box.prop(assembly.obj_bp,'location',index=0,text="Location X")
            drivers = pyclone_utils.get_drivers(assembly.obj_bp)
            for driver in drivers:
                if driver.data_path == 'location' and driver.array_index == 0:
                    pyclone_utils.draw_driver(layout,assembly.obj_bp,driver)    

        if scene_props.driver_tabs == 'LOC_Y':
            box.prop(assembly.obj_bp,'location',index=1,text="Location Y")
            drivers = pyclone_utils.get_drivers(assembly.obj_bp)
            for driver in drivers:
                if driver.data_path == 'location' and driver.array_index == 1:
                    pyclone_utils.draw_driver(layout,assembly.obj_bp,driver)  

        if scene_props.driver_tabs == 'LOC_Z':
            box.prop(assembly.obj_bp,'location',index=2,text="Location Z")
            drivers = pyclone_utils.get_drivers(assembly.obj_bp)
            for driver in drivers:
                if driver.data_path == 'location' and driver.array_index == 2:
                    pyclone_utils.draw_driver(layout,assembly.obj_bp,driver)  

        if scene_props.driver_tabs == 'ROT_X':
            box.prop(assembly.obj_bp,'rotation_euler',index=0,text="Rotation X")
            drivers = pyclone_utils.get_drivers(assembly.obj_bp)
            for driver in drivers:
                if driver.data_path == 'rotation_euler' and driver.array_index == 0:
                    pyclone_utils.draw_driver(layout,assembly.obj_bp,driver)  

        if scene_props.driver_tabs == 'ROT_Y':
            box.prop(assembly.obj_bp,'rotation_euler',index=1,text="Rotation Y")
            drivers = pyclone_utils.get_drivers(assembly.obj_bp)
            for driver in drivers:
                if driver.data_path == 'rotation_euler' and driver.array_index == 1:
                    pyclone_utils.draw_driver(layout,assembly.obj_bp,driver)  

        if scene_props.driver_tabs == 'ROT_Z':
            box.prop(assembly.obj_bp,'rotation_euler',index=2,text="Rotation Z")
            drivers = pyclone_utils.get_drivers(assembly.obj_bp)
            for driver in drivers:
                if driver.data_path == 'rotation_euler' and driver.array_index == 2:
                    pyclone_utils.draw_driver(layout,assembly.obj_bp,driver)  

        if scene_props.driver_tabs == 'DIM_X':
            box.prop(assembly.obj_x,'location',index=0,text="Dimension X")
            drivers = pyclone_utils.get_drivers(assembly.obj_x)
            for driver in drivers:
                if driver.data_path == 'location' and driver.array_index == 0:
                    pyclone_utils.draw_driver(layout,assembly.obj_x,driver)  

        if scene_props.driver_tabs == 'DIM_Y':
            box.prop(assembly.obj_y,'location',index=1,text="Dimension Y")
            drivers = pyclone_utils.get_drivers(assembly.obj_y)
            for driver in drivers:
                if driver.data_path == 'location' and driver.array_index == 1:
                    pyclone_utils.draw_driver(layout,assembly.obj_y,driver)  

        if scene_props.driver_tabs == 'DIM_Z':
            box.prop(assembly.obj_z,'location',index=2,text="Dimension Z")
            drivers = pyclone_utils.get_drivers(assembly.obj_z)
            for driver in drivers:
                if driver.data_path == 'location' and driver.array_index == 2:
                    pyclone_utils.draw_driver(layout,assembly.obj_z,driver)  

        if scene_props.driver_tabs == 'PROMPTS':
            if len(assembly.obj_prompts.pyclone.prompts) == 0:
                box.label(text='No Prompts')  
                return    

            box.template_list("PC_UL_prompts"," ", assembly.obj_prompts.pyclone, "prompts", assembly.obj_prompts.pyclone, "prompt_index",rows=5,type='DEFAULT')
            if assembly.obj_prompts.pyclone.prompt_index + 1 > len(assembly.obj_prompts.pyclone.prompts):
                return 

            prompt = assembly.obj_prompts.pyclone.prompts[assembly.obj_prompts.pyclone.prompt_index]

            if prompt:
                drivers = pyclone_utils.get_drivers(assembly.obj_prompts)

                box.operator('pc_driver.add_driver')
                box.operator('pc_driver.remove_driver')
                for driver in drivers:
                    if driver.data_path == prompt.get_data_path():
                        pyclone_utils.draw_driver(box,assembly.obj_prompts,driver)  

        if scene_props.driver_tabs == 'CALCULATORS':
            if len(assembly.obj_prompts.pyclone.calculators) == 0:
                box.label('No Calculators')  
                return

            box.template_list("PC_UL_calculators"," ", assembly.obj_prompts.pyclone, "calculators", assembly.obj_prompts.pyclone, "calculator_index",rows=5,type='DEFAULT')
            if assembly.obj_prompts.pyclone.calculator_index + 1 > len(assembly.obj_prompts.pyclone.calculators):
                return 
            
            calculator = assembly.obj_prompts.pyclone.calculators[assembly.obj_prompts.pyclone.calculator_index]

            if calculator:
                drivers = pyclone_utils.get_drivers(calculator.distance_obj)
                if len(drivers) == 0:
                    box.operator('pc_driver.add_calculator_driver')
                else:
                    box.operator('pc_driver.remove_calculator_driver')                
                for driver in drivers:
                    pyclone_utils.draw_driver(layout,calculator.distance_obj,driver) 

        if scene_props.driver_tabs == 'SELECTED_OBJECT':
            obj = context.object
            if obj:
                box.label(text="Current Object: " + context.object.name,icon=pc_utils.get_object_icon(obj))
                drivers = pyclone_utils.get_drivers(obj)
                for driver in drivers:
                    pyclone_utils.draw_driver(layout,obj,driver)
                    

class VIEW3D_MT_assembly_menu(bpy.types.Menu):
    bl_label = "Assembly Menu"

    def draw(self, context):
        layout = self.layout
        if context.object:
            assembly_bp = pc_utils.get_assembly_bp(context.object)
            layout.operator('pc_assembly.select_parent',text="Select Parent Assembly",icon='SORT_DESC')
            layout.operator('pc_assembly.select_base_point',text="Select Base Point",icon='DECORATE').obj_bp_name = assembly_bp.name
            layout.operator('pc_assembly.duplicate_assembly',text="Duplicate Assembly",icon='DUPLICATE').obj_bp_name = assembly_bp.name
            layout.operator('pc_assembly.create_assembly_layout',text="Create Assembly Layout",icon='CAMERA_DATA').obj_bp_name = assembly_bp.name
            layout.operator('pc_assembly.make_assembly_static',text="Make Assembly Static",icon='LOCKED').obj_bp_name = assembly_bp.name
            layout.operator('pc_assembly.convert_to_object',text="Convert to Object",icon='MESH_CUBE').obj_bp_name = assembly_bp.name
            layout.operator('pc_assembly.delete_assembly',icon='X').obj_bp_name = assembly_bp.name


class VIEW3D_PT_pc_assembly_properties(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Assembly"
    bl_category = "Item"    
    # bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.object and pc_utils.get_assembly_bp(context.object):
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        assembly = pc_types.Assembly(assembly_bp)   
        draw_assembly_properties(context,layout,assembly)     


class pc_assembly_OT_show_properties(bpy.types.Operator):
    bl_idname = "pc_assembly.show_properties"
    bl_label = "Assembly Properties"
    bl_description = "This show the assembly properties"
    bl_options = {'UNDO'}

    assembly = None

    def check(self, context):
        for child in self.assembly.obj_bp.children:
            child["PROMPT_ID"] = self.assembly.obj_bp["PROMPT_ID"]
        return True

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        self.assembly = pc_types.Assembly(assembly_bp)  
        #Blender crashes if dialog opens with list view.
        #If Objects > Material tab is displayed then Blender crashes
        context.scene.pyclone.assembly_tabs = 'MAIN'        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        draw_assembly_properties(context,layout,self.assembly)  

classes = (
    VIEW3D_MT_assembly_menu,
    VIEW3D_PT_pc_assembly_properties,
    pc_assembly_OT_show_properties,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()                