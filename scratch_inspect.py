import os
import xml.etree.ElementTree as ET

path = "/home/curtis/Downloads/Google-Workspace-logos"
for f in os.listdir(path):
    if f.endswith(".svg"):
        print("---", f)
        tree = ET.parse(os.path.join(path, f))
        root = tree.getroot()
        print("ns:", root.tag.split('}')[0] + '}')
        for mask in root.findall(".//{http://www.w3.org/2000/svg}mask"):
            print("Mask found:", mask.attrib)
        for g in root.findall(".//{http://www.w3.org/2000/svg}g"):
            print("G found:", g.attrib)
