import bpy
import os
import sys

#IMPORT PC_LIB MODULES
text = bpy.context.space_data.text
PC_LIB_PATH = os.path.dirname(os.path.dirname(text.filepath))
sys.path.append(PC_LIB_PATH)
from pc_lib import pc_types, pc_unit

#CREATE ASSEMBLY
assembly = pc_types.Assembly()
assembly.create_assembly(assembly_name="My Python Assembly")

#SET ASSEMBLY DIMENSIONS
assembly.obj_x.location.x = pc_unit.inch(30)
assembly.obj_y.location.y = pc_unit.inch(24)
assembly.obj_z.location.z = pc_unit.millimeter(450)

#ADD PROMPTS
assembly.add_prompt(name="My Checkbox",
                    prompt_type='CHECKBOX',
                    value=False)
assembly.add_prompt(name="My Selection List",
                    prompt_type='COMBOBOX',
                    value=0,
                    combobox_items=["Option 1","Option 2","Option 3"])

#ADD EMPTY
mid_y = assembly.add_empty('Mid Y')
mid_y.empty_display_size = pc_unit.inch(1)   

#GET VARIABLES TO USE IN DRIVERS
dim_y = assembly.obj_y.pyclone.get_var('location.y','dim_y')

#ADD DRIVER TO EMPTY
mid_y.pyclone.loc_y('dim_y/2',[dim_y])
