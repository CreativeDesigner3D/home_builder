import bpy
import math
from pc_lib import pc_types, pc_utils, pc_unit
from . import enum_doors_windows
from . import types_doors_windows
from . import const_doors_windows as const

def update_door_panel(self,context):
    self.door_panel_changed = True

def update_door_frame(self,context):
    self.door_frame_changed = True

def update_door_handle(self,context):
    self.door_handle_changed = True

class hb_sample_door_windows_OT_door_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_door_windows.door_prompts"
    bl_label = "Entry Door Prompts"

    assembly_name: bpy.props.StringProperty(name="Door Name",default="")
    door_panel_changed: bpy.props.BoolProperty(name="Door Panel Changed")
    door_frame_changed: bpy.props.BoolProperty(name="Door Frame Changed")
    door_handle_changed: bpy.props.BoolProperty(name="Door Handle Changed")

    anchor_type: bpy.props.EnumProperty(name="Anchor Type",
                                   items=[('LEFT',"Left","Anchor Left"),
                                          ('CENTER',"Center","Anchor Center"),
                                          ('RIGHT',"Right","Anchor Right")])

    entry_door_tabs: bpy.props.EnumProperty(name="Entry Door Tabs",
                                         items=[('PANEL',"Panel","Panel Options"),
                                                ('FRAME',"Frame","Frame Options"),
                                                ('HANDLE',"Handle","Handle Options")])

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Doors")])

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)
    x_location_left: bpy.props.FloatProperty(name="X Location Left",unit='LENGTH',precision=4)
    x_location_center: bpy.props.FloatProperty(name="X Location Center",unit='LENGTH',precision=4)
    x_location_right: bpy.props.FloatProperty(name="X Location Right",unit='LENGTH',precision=4)

    entry_door_panel_category: bpy.props.EnumProperty(name="Entry Door Panel Category",
        items=enum_doors_windows.enum_entry_door_panel_categories,
        update=enum_doors_windows.update_entry_door_panel_category)
    entry_door_panel: bpy.props.EnumProperty(name="Entry Door Panel",
        items=enum_doors_windows.enum_entry_door_panels_names,
        update=update_door_panel)

    entry_door_frame_category: bpy.props.EnumProperty(name="Entry Door Frame Category",
        items=enum_doors_windows.enum_entry_door_frame_categories,
        update=enum_doors_windows.update_entry_door_frame_category)
    entry_door_frame: bpy.props.EnumProperty(name="Entry Door Frame",
        items=enum_doors_windows.enum_entry_door_frame_names,
        update=update_door_frame)

    entry_door_handle_category: bpy.props.EnumProperty(name="Entry Door Handle Category",
        items=enum_doors_windows.enum_entry_door_handle_categories,
        update=enum_doors_windows.update_entry_door_handle_category)
    entry_door_handle: bpy.props.EnumProperty(name="Entry Door Handle",
        items=enum_doors_windows.enum_entry_door_handle_names,
        update=update_door_handle)

    assembly = None
    wall = None
    door_panels = []
    door_frames = []
    door_handles = []

    def update_product_size(self):
        self.assembly.obj_x.location.x = self.width
        self.assembly.obj_y.location.y = self.depth
        self.assembly.obj_z.location.z = self.height        
        if self.wall:
            if self.anchor_type == 'LEFT':
                self.assembly.obj_bp.location.x = self.x_location_left
            if self.anchor_type == 'CENTER':
                self.assembly.obj_bp.location.x = self.x_location_center - (self.width/2)
            if self.anchor_type == 'RIGHT':
                self.assembly.obj_bp.location.x = self.wall.obj_x.location.x - (self.x_location_right + self.width)

    def update_door_panel(self,context):
        if self.door_panel_changed:
            for door_panel in self.door_panels:
                pc_utils.delete_object_and_children(door_panel)

            if hasattr(self.assembly,'add_doors'):
                self.assembly.add_doors(door_panel_category=self.entry_door_panel_category,
                                        door_panel_name=self.entry_door_panel,
                                        door_handle_category=self.entry_door_handle_category,
                                        door_handle_name=self.entry_door_handle)
                
                pc_utils.hide_empties(self.assembly.obj_bp)

            self.door_panel_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_door_frame(self,context):
        if self.door_frame_changed:
            for door_frame in self.door_frames:
                pc_utils.delete_object_and_children(door_frame)

            if hasattr(self.assembly,'add_frame'):
                self.assembly.add_frame(door_frame_category=self.entry_door_frame_category,
                                        door_frame_name=self.entry_door_frame)
                
                pc_utils.hide_empties(self.assembly.obj_bp)

            self.door_frame_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_door_handle(self,context):
        if self.door_handle_changed:
            for door_handle in self.door_handles:
                pc_utils.delete_object_and_children(door_handle)

            for door_panel_bp in self.door_panels:
                door_panel = pc_types.Assembly(door_panel_bp)
                if hasattr(self.assembly,'add_door_handle'):
                    self.assembly.add_door_handle(door_panel=door_panel,
                                                  door_handle_category=self.entry_door_handle_category,
                                                  door_handle_name=self.entry_door_handle)
                
                pc_utils.hide_empties(self.assembly.obj_bp)

            self.door_handle_changed = False
            self.get_assemblies_and_set_prompts(context)

    def check(self, context):
        self.update_product_size()
        self.update_door_panel(context)
        self.update_door_frame(context)
        self.update_door_handle(context)
        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        if entry_door_swing:
            if self.door_swing == 'LEFT':
                entry_door_swing.set_value(0)
            if self.door_swing == 'RIGHT':
                entry_door_swing.set_value(1)
            if self.door_swing == 'DOUBLE':
                entry_door_swing.set_value(2)                        
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies_and_set_prompts(self,context):
        self.door_panels = []
        self.door_frames = []
        self.door_handles = []
        
        bp_door = pc_utils.get_bp_by_tag(context.object,const.ENTRY_DOOR_TAG)  
        if bp_door:
            if 'IS_SWING_DOOR' in bp_door:
                self.assembly = types_doors_windows.Swing_Door(bp_door)
            if 'IS_SLIDING_DOOR' in bp_door:
                self.assembly = types_doors_windows.Sliding_Door(bp_door)
        for child in self.assembly.obj_bp.children:
            if "IS_ENTRY_DOOR_PANEL" in child:
                self.door_panels.append(child)
                for nchild in child.children:
                    if "IS_ENTRY_DOOR_HANDLE" in nchild:
                        self.door_handles.append(nchild)
        for child in self.assembly.obj_bp.children:
            if "IS_ENTRY_DOOR_FRAME" in child:
                self.door_frames.append(child)

        if self.assembly.obj_bp.parent and 'IS_WALL_BP' in self.assembly.obj_bp.parent:
            self.wall = pc_types.Assembly(self.assembly.obj_bp.parent)
        else:
            self.wall = None

        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        if entry_door_swing:
            if entry_door_swing.get_value() == 0:
                self.door_swing = 'LEFT'
            if entry_door_swing.get_value() == 1:
                self.door_swing = 'RIGHT'
            if entry_door_swing.get_value() == 2:
                self.door_swing = 'DOUBLE'

    def invoke(self,context,event):
        self.get_assemblies_and_set_prompts(context)
        self.depth = math.fabs(self.assembly.obj_y.location.y)
        self.height = math.fabs(self.assembly.obj_z.location.z)
        self.width = math.fabs(self.assembly.obj_x.location.x)
        if self.wall:
            self.x_location_left = self.assembly.obj_bp.location.x
            self.x_location_center = self.assembly.obj_bp.location.x + (self.width/2)
            self.x_location_right = self.wall.obj_x.location.x - (self.assembly.obj_bp.location.x  + self.width)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_x):
            x = math.fabs(self.assembly.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(self.assembly.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_z):
            z = math.fabs(self.assembly.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.assembly.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_y):
            y = math.fabs(self.assembly.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.assembly.obj_y,'hide_viewport',text="")

        row = box.row()    
        row.label(text="Anchor Type:")
        row.prop(self,'anchor_type',expand=True)

        row = box.row()    
        row.label(text="Location:")
        if self.wall:
            if self.anchor_type == 'LEFT':
                row.prop(self,'x_location_left',text="Left")
            if self.anchor_type == 'CENTER':
                row.prop(self,'x_location_center',text="Center")
            if self.anchor_type == 'RIGHT':
                row.prop(self,'x_location_right',text="Right")       
        else:                 
            row.prop(self.assembly.obj_bp,'location',index=0,text="X")
        row.prop(self.assembly.obj_bp,'location',index=2,text="Z")

    def draw_prompts(self,layout,context):
        # door_reveal = self.assembly.get_prompt("Door Reveal")
        handle_vertical_location = self.assembly.get_prompt("Handle Vertical Location")
        handle_location_from_edge = self.assembly.get_prompt("Handle Location From Edge")
        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        outswing = self.assembly.get_prompt("Outswing")
        open_door = self.assembly.get_prompt("Open Door")
        turn_off_door_panels = self.assembly.get_prompt("Turn Off Door Panels")
        turn_off_handles = self.assembly.get_prompt("Turn Off Handles")

        if open_door and outswing and entry_door_swing:
            box = layout.box()
            box.label(text="Door Swing")
            row = box.row()
            open_door.draw(row,allow_edit=False)
            row = box.row(align=True)
            row.label(text="Door Swing")
            row.prop_enum(self, "door_swing", 'LEFT') 
            row.prop_enum(self, "door_swing", 'RIGHT') 
            row.prop_enum(self, "door_swing", 'DOUBLE')
            outswing.draw(row,allow_edit=False)     
            box.prop(turn_off_door_panels,'checkbox_value',text="Turn Off Door Panels")

        if handle_vertical_location and handle_location_from_edge:
            box = layout.box()
            box.label(text="Door Hardware")
            row = box.row()
            row.label(text="Pull Location:")
            row.prop(handle_vertical_location,'distance_value',text="Vertical")  
            row.prop(handle_location_from_edge,'distance_value',text="From Edge")  
            box.prop(turn_off_handles,'checkbox_value',text="Turn Off Handles")

    def draw_door_panel(self,layout,context):
        layout.prop(self,'entry_door_panel_category',text="")
        layout.template_icon_view(self,"entry_door_panel",show_labels=True)          

    def draw_door_frame(self,layout,context):
        layout.prop(self,'entry_door_frame_category',text="")
        layout.template_icon_view(self,"entry_door_frame",show_labels=True)      

    def draw_door_handle(self,layout,context):
        layout.prop(self,'entry_door_handle_category',text="")
        layout.template_icon_view(self,"entry_door_handle",show_labels=True)      

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)
        self.draw_prompts(layout,context)
        box = layout.box()
        row = box.row(align=True)
        row.prop(self,'entry_door_tabs',expand=True)
        if self.entry_door_tabs == 'PANEL':
            self.draw_door_panel(box,context)
        if self.entry_door_tabs == 'FRAME':
            self.draw_door_frame(box,context)
        if self.entry_door_tabs == 'HANDLE':
            self.draw_door_handle(box,context)                        


def update_window_frame(self,context):
    self.window_frame_changed = True

def update_window_insert(self,context):
    self.window_insert_changed = True


class hb_sample_door_windows_OT_window_prompts(bpy.types.Operator):
    bl_idname = "hb_sample_door_windows.window_prompts"
    bl_label = "Window Prompts"

    assembly_name: bpy.props.StringProperty(name="Window Name",default="")
    window_frame_changed: bpy.props.BoolProperty(name="Window Frame Changed")
    window_insert_changed: bpy.props.BoolProperty(name="Window Insert Changed")

    window_tabs: bpy.props.EnumProperty(name="Window Tabs",
                                        items=[('FRAME',"Frame","Frame Options"),
                                               ('INSERT',"Insert","Insert Options")])

    anchor_type: bpy.props.EnumProperty(name="Anchor Type",
                                   items=[('LEFT',"Left","Anchor Left"),
                                          ('CENTER',"Center","Anchor Center"),
                                          ('RIGHT',"Right","Anchor Right")])
    
    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)
    x_location_left: bpy.props.FloatProperty(name="X Location Left",unit='LENGTH',precision=4)
    x_location_center: bpy.props.FloatProperty(name="X Location Center",unit='LENGTH',precision=4)
    x_location_right: bpy.props.FloatProperty(name="X Location Right",unit='LENGTH',precision=4)

    window_frame_category: bpy.props.EnumProperty(name="Window Frame Category",
        items=enum_doors_windows.enum_window_frame_categories,
        update=enum_doors_windows.update_window_frame_category)
    window_frame: bpy.props.EnumProperty(name="Window Frame",
        items=enum_doors_windows.enum_window_frame_names,
        update=update_window_frame)

    window_insert_category: bpy.props.EnumProperty(name="Window Insert Category",
        items=enum_doors_windows.enum_window_insert_categories,
        update=enum_doors_windows.update_window_insert_category)
    window_insert: bpy.props.EnumProperty(name="Window Insert",
        items=enum_doors_windows.enum_window_insert_names,
        update=update_window_insert)

    wall = None
    assembly = None
    window_frame_bp = None
    window_insert_bp = None

    def update_product_size(self):
        self.assembly.obj_x.location.x = self.width
        self.assembly.obj_y.location.y = self.depth
        self.assembly.obj_z.location.z = self.height
        if self.wall:
            if self.anchor_type == 'LEFT':
                self.assembly.obj_bp.location.x = self.x_location_left
            if self.anchor_type == 'CENTER':
                self.assembly.obj_bp.location.x = self.x_location_center - (self.width/2)
            if self.anchor_type == 'RIGHT':
                self.assembly.obj_bp.location.x = self.wall.obj_x.location.x - (self.x_location_right + self.width)

    def update_window_frame(self,context):
        if self.window_frame_changed:
            if self.window_frame_bp:
                pc_utils.delete_object_and_children(self.window_frame_bp)

            if hasattr(self.assembly,'add_window_frame'):
                self.assembly.add_window_frame(category=self.window_frame_category,
                                               assembly_name=self.window_frame)
                
                pc_utils.hide_empties(self.assembly.obj_bp)

            self.window_frame_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_window_insert(self,context):
        if self.window_insert_changed:
            if self.window_insert_bp:
                pc_utils.delete_object_and_children(self.window_insert_bp)

            if hasattr(self.assembly,'add_window_insert'):
                self.assembly.add_window_insert(category=self.window_insert_category,
                                                assembly_name=self.window_insert)
                
                pc_utils.hide_empties(self.assembly.obj_bp)

            self.window_insert_changed = False
            self.get_assemblies_and_set_prompts(context)

    def check(self, context):
        self.update_product_size()
        self.update_window_frame(context)
        self.update_window_insert(context)                   
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies_and_set_prompts(self,context):
        self.window_frame_bp = None
        self.window_insert_bp = None

        bp_window = pc_utils.get_bp_by_tag(context.object,const.WINDOW_TAG)
        if bp_window:
            self.assembly = types_doors_windows.Standard_Window(bp_window)

        if self.assembly.obj_bp.parent and 'IS_WALL_BP' in self.assembly.obj_bp.parent:
            self.wall = pc_types.Assembly(self.assembly.obj_bp.parent)
        else:
            self.wall = None

        for child in self.assembly.obj_bp.children:
            if "IS_WINDOW_FRAME" in child:
                self.window_frame_bp = child
        for child in self.assembly.obj_bp.children:
            if "IS_WINDOW_INSERT" in child:
                self.window_insert_bp = child

    def invoke(self,context,event):
        self.get_assemblies_and_set_prompts(context)
        self.depth = math.fabs(self.assembly.obj_y.location.y)
        self.height = math.fabs(self.assembly.obj_z.location.z)
        self.width = math.fabs(self.assembly.obj_x.location.x)
        if self.wall:
            self.x_location_left = self.assembly.obj_bp.location.x
            self.x_location_center = self.assembly.obj_bp.location.x + (self.width/2)
            self.x_location_right = self.wall.obj_x.location.x - (self.assembly.obj_bp.location.x  + self.width)        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_x):
            x = math.fabs(self.assembly.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(self.assembly.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_z):
            z = math.fabs(self.assembly.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.assembly.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_y):
            y = math.fabs(self.assembly.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.assembly.obj_y,'hide_viewport',text="")

        row = box.row()    
        row.label(text="Anchor Type:")
        row.prop(self,'anchor_type',expand=True)

        row = box.row()    
        row.label(text="Location:")
        if self.wall:
            if self.anchor_type == 'LEFT':
                row.prop(self,'x_location_left',text="Left")
            if self.anchor_type == 'CENTER':
                row.prop(self,'x_location_center',text="Center")
            if self.anchor_type == 'RIGHT':
                row.prop(self,'x_location_right',text="Right")       
        else:                 
            row.prop(self.assembly.obj_bp,'location',index=0,text="X")        
        row.prop(self.assembly.obj_bp,'location',index=2,text="Z")

    def draw_prompts(self,layout,context):
        window_quantity = self.assembly.get_prompt("Window Quantity")
        x_offset = self.assembly.get_prompt("X Offset")

        if window_quantity and x_offset:
            box = layout.box()
            box.label(text="Window Quantity")
            row = box.row()
            row.prop(window_quantity,'quantity_value',text="Quantity")  
            row.prop(x_offset,'distance_value',text="Offset")  

    def draw_window_frame(self,layout,context):
        layout.prop(self,'window_frame_category',text="")
        layout.template_icon_view(self,"window_frame",show_labels=True)          

    def draw_window_insert(self,layout,context):
        layout.prop(self,'window_insert_category',text="")
        layout.template_icon_view(self,"window_insert",show_labels=True)       

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)
        self.draw_prompts(layout,context)
        box = layout.box()
        row = box.row(align=True)
        row.prop(self,'window_tabs',expand=True)
        if self.window_tabs == 'FRAME':
            self.draw_window_frame(box,context)
        if self.window_tabs == 'INSERT':
            self.draw_window_insert(box,context)           


classes = (
    hb_sample_door_windows_OT_door_prompts,
    hb_sample_door_windows_OT_window_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()