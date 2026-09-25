import os
import xml.etree.ElementTree as ET
import re

svg_dir = "/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/"

def get_bbox(path_d):
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', path_d)]
    if not nums: return None, None, None, None
    xs = nums[0::2]
    ys = nums[1::2]
    if len(xs) != len(ys):
        return None, None, None, None
    return min(xs), max(xs), min(ys), max(ys)

for f in sorted(os.listdir(svg_dir)):
    if not f.endswith('.svg'): continue
    tree = ET.parse(os.path.join(svg_dir, f))
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    xmin, xmax, ymin, ymax = 999, -999, 999, -999
    
    # We want to ignore shadows (usually opacity=0.2 or fill=#000000)
    for path in root.findall('.//svg:path', ns) + root.findall('.//svg:rect', ns) + root.findall('.//svg:circle', ns):
        parent = path.getparent() if hasattr(path, 'getparent') else None
        # super hacky just check strings
        path_str = ET.tostring(path).decode('utf-8')
        if 'opacity="0.2"' in path_str or 'fill="#000000"' in path_str:
            continue
            
        if path.tag.endswith('path'):
            d = path.get('d', '')
            if not d: continue
            # this is a dumb parser, just grabs all numbers, but since they are absolute explicit paths for Keep/Drive...
            # Wait, for others I have relative paths and arcs!
            # Let's just use a more generic way or just know roughly
            pass

# Instead of parsing SVG exactly, I'll just use a browser script with SVGRect to get the precise visual bounding box!
