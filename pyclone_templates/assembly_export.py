import bpy
import os
import sys
import codecs

#IMPORT PC_LIB MODULES
text = bpy.context.space_data.text
path = os.path.dirname(os.path.dirname(text.filepath))
sys.path.append(path)
from pc_lib import pc_types, pc_unit

#GET ASSEMBLIES IN THE SCENE
assembly_list = []
for obj in bpy.data.objects:
    if 'IS_ASSEMBLY_BP' in obj:
        assembly_list.append(pc_types.Assembly(obj))

#CREATE EXPORT TEXT FILE
export_filepath = os.path.join(bpy.app.tempdir,"assembly_export.txt")
file = codecs.open(export_filepath,'w',encoding='utf-8')

#WRITE ASSEMBLY DATA TO FILE
for assembly in assembly_list:
    name = assembly.obj_bp.name
    x_dim = str(round(assembly.obj_x.location.x,3))
    y_dim = str(round(assembly.obj_y.location.y,3))
    z_dim = str(round(assembly.obj_z.location.z,3))
    prompt_dict = {}
    for prompt in assembly.obj_prompts.pyclone.prompts:
        prompt_dict[prompt.name] = str(prompt.get_value())
    file.write(name + "," + x_dim + "," + y_dim + "," + z_dim + "," + str(prompt_dict) + "\n")

#CLOSE AND OPEN FILE
file.close()
bpy.ops.text.open(filepath=export_filepath)