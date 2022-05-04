import os
import xml.etree.ElementTree as ET

class Pointer_XML:
    
    tree = None
    
    def __init__(self):
        pass
    
    def read_file(self,path):
        self.tree = ET.parse(path)
        return self.tree.getroot()

    def create_tree(self):
        root = ET.Element('Root',{'Application':'Blender','ApplicationVersion':'0.1'})
        self.tree = ET.ElementTree(root)
        return root
    
    def add_element(self,root,elm_name,attrib_name=""):
        if attrib_name == "":
            elm = ET.Element(elm_name)
        else:
            elm = ET.Element(elm_name,{'Name':attrib_name})
        root.append(elm)
        return elm
    
    def add_element_with_text(self,root,elm_name,text):
        field = ET.Element(elm_name)
        field.text = text
        root.append(field)
    
    def format_xml_file(self,path):
        """ This makes the xml file readable as a txt doc.
            For some reason the xml.toprettyxml() function
            adds extra blank lines. This makes the xml file
            unreadable. This function just removes
            all of the blank lines.
            arg1: path to xml file
        """
        from xml.dom.minidom import parse
        
        xml = parse(path)
        pretty_xml = xml.toprettyxml()
        
        file = open(path,'w')
        file.write(pretty_xml)
        file.close()
        
        cleaned_lines = []
        with open(path,"r") as f:
            lines = f.readlines()
            for l in lines:
                l.strip()
                if "<" in l:
                    cleaned_lines.append(l)
            
        with open (path,"w") as f:
            f.writelines(cleaned_lines)
    
    def write(self,path):
        with open(path, 'w',encoding='utf-8') as file:
            self.tree.write(file,encoding='unicode')                                                                                  

def write_xml_file(filepath,pointer_list):
    '''
    This writes the XML file from the current props. 
    This file gets written everytime a property changes.
    '''
    xml = Pointer_XML()
    root = xml.create_tree()
    for pointer_item in pointer_list:
        pointer = xml.add_element(root,'Pointer')
        xml.add_element_with_text(pointer,'Name',pointer_item[0])
        xml.add_element_with_text(pointer,'Category',pointer_item[1])
        xml.add_element_with_text(pointer,'Asset',pointer_item[2])
    
    pointer_dir = os.path.dirname(filepath)
    if not os.path.exists(pointer_dir):
        os.makedirs(pointer_dir)

    xml.write(filepath)
    xml.format_xml_file(filepath)

def update_props_from_xml_file(filepath,pointers):
    '''
    This gets read on startup and sets the pointer props
    '''
    pointer_dict = {}

    if os.path.exists(filepath):
        xml = Pointer_XML()
        root = xml.read_file(filepath)

        for elm in root.findall("Pointer"):
            name = ""
            category = ""
            item_name = ""
            items = list(elm.iter())
            for item in items:
                if item.tag == 'Name':
                    name = item.text
                if item.tag == 'Category':
                    category = item.text
                if item.tag == 'Asset':
                    item_name = item.text   

            pointer_dict[name] = (category,item_name)    

    for p_dict in pointer_dict:
        if p_dict not in pointers:
            pointer = pointers.add()
            pointer.name = p_dict
            pointer.category = pointer_dict[p_dict][0]
            pointer.item_name = pointer_dict[p_dict][1]

def get_folder_enum_previews(path,key):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the folders from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        folders = []
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)

        for i, name in enumerate(folders):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, "", 'IMAGE')
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def get_image_enum_previews(path,key,force_reload=False):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the images from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        image_paths = []
        for fn in os.listdir(path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, filepath, 'IMAGE',force_reload)
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def create_image_preview_collection():
    import bpy.utils.previews
    col = bpy.utils.previews.new()
    col.my_previews_dir = ""
    col.my_previews = ()
    return col                    