import os
import copy
import xml.etree.ElementTree as ET

ET.register_namespace('', "http://www.w3.org/2000/svg")
ns = "{http://www.w3.org/2000/svg}"

in_dir = "/home/curtis/Downloads/Google-Workspace-logos"
out_dir = "/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace"

docs_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" version="1.1">
 <path style="fill:#000000;opacity:0.2" d="M 18,5 H 38 L 54,21 V 53 C 54,57.432 50.432,61 46,61 H 18 C 13.568,61 10,57.432 10,53 V 13 C 10,8.568 13.568,5 18,5 Z"/>
 <path style="fill:#3186FF" d="m 18,4 h 20 l 16,16 v 32 c 0,4.432 -3.568,8 -8,8 H 18 c -4.432,0 -8,-3.568 -8,-8 V 12 c 0,-4.432 3.568,-8 8,-8 z"/>
 <path style="fill:#76BBFF" d="M 38,4 V 16 C 38,18.216 39.784,20 42,20 H 54 Z"/>
 <path style="opacity:0.2;fill:#ffffff" d="M 18 4 C 13.568 4 10 7.568 10 12 L 10 13 C 10 8.568 13.568 5 18 5 L 38 5 L 54 21 L 54 20 L 38 4 L 18 4 z"/>
 <rect x="21" y="38" width="22" height="4" rx="2" fill="white"/>
 <rect x="21" y="48" width="16" height="4" rx="2" fill="white"/>
</svg>"""

def strip_attributes_recursive(el, attrs):
    for a in attrs:
        if a in el.attrib:
            del el.attrib[a]
    for child in el:
        strip_attributes_recursive(child, attrs)

def get_gradient_colors(root):
    colors = {}
    defs = root.find(f".//{ns}defs")
    if defs is not None:
        for grad in defs:
            if grad.tag in (f"{ns}linearGradient", f"{ns}radialGradient"):
                stops = grad.findall(f"{ns}stop")
                if stops:
                    colors[grad.attrib['id']] = stops[0].attrib.get('stop-color', '#000000')
    return colors

for f in os.listdir(in_dir):
    if not f.endswith(".svg"): continue
    
    if "docs" in f:
        with open(os.path.join(out_dir, f), 'w') as out_f:
            out_f.write(docs_svg)
        continue

    tree = ET.parse(os.path.join(in_dir, f))
    root = tree.getroot()
    gradient_colors = get_gradient_colors(root)
    
    # Base setup
    new_root = ET.Element(f"{ns}svg")
    new_root.attrib['width'] = '64'
    new_root.attrib['height'] = '64'
    new_root.attrib['viewBox'] = '0 0 64 64'
    new_root.attrib['fill'] = 'none'
    
    defs = ET.Element(f"{ns}defs")
    
    main_elements = []

    if "gmail" in f:
        old_defs = root.find(f".//{ns}defs")
        if old_defs is not None:
            new_root.append(old_defs)
        for child in list(root):
            if child.tag != f"{ns}defs":
                main_elements.append(copy.deepcopy(child))
                
    elif "drive" in f or "keep" in f:
        # Engine for Drive and Keep (ClipPath + Flat overrides)
        parent_map = {c: p for p in root.iter() for c in p}
        
        # Move masks to defs as clipPaths
        for mask in root.findall(f".//{ns}mask"):
            parent = parent_map.get(mask)
            if parent is not None: parent.remove(mask)
            mask.tag = f"{ns}clipPath"
            for attr in ['mask-type', 'maskUnits', 'x', 'y', 'width', 'height', 'style']:
                if attr in mask.attrib: del mask.attrib[attr]
            strip_attributes_recursive(mask, ['fill', 'stroke', 'opacity', 'style'])
            defs.append(mask)

        # Remove filter groups from Keep (glow shards)
        if "keep" in f:
            for g in root.findall(f".//{ns}g"):
                if 'filter' in g.attrib:
                    p = parent_map.get(g)
                    if p is not None: p.remove(g)

        # Apply flat colors and clip-paths
        for el in root.iter():
            if 'mask' in el.attrib:
                el.attrib['clip-path'] = el.attrib['mask']
                del el.attrib['mask']
            if 'filter' in el.attrib:
                del el.attrib['filter']

            if 'fill' in el.attrib and el.attrib['fill'].startswith('url(#'):
                gid = el.attrib['fill'][5:-1]
                if "drive" in f:
                    if gid == 'b': el.attrib['fill'] = '#fec700'
                    elif gid == 'c': el.attrib['fill'] = '#3186ff'
                    elif gid == 'd': el.attrib['fill'] = '#0ebc5f'
                    else: el.attrib['fill'] = gradient_colors.get(gid, '#000000')
                elif "keep" in f:
                    if gid == 'c': el.attrib['fill'] = '#ffbe00' # bulb top
                    else: el.attrib['fill'] = gradient_colors.get(gid, '#000000')
                else:
                    el.attrib['fill'] = gradient_colors.get(gid, '#000000')

        for child in list(root):
            if child.tag != f"{ns}defs" and child.tag != f"{ns}mask":
                main_elements.append(copy.deepcopy(child))
                
    else:
        # FLAT EXTRACTOR for Calendar, Sheets, Slides, Meet
        if "calendar" in f:
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == '#bbe2ff':
                    main_elements.append(copy.deepcopy(path))
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == '#3c90ff':
                    main_elements.append(copy.deepcopy(path))
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == '#fff':
                    main_elements.append(copy.deepcopy(path))
                    
        elif "slides" in f:
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == 'url(#a)':
                    p = copy.deepcopy(path)
                    p.attrib['fill'] = '#ffdb0f'
                    main_elements.append(p)
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == 'url(#b)':
                    p = copy.deepcopy(path)
                    p.attrib['fill'] = '#ffbe00'
                    main_elements.append(p)
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == '#fff':
                    main_elements.append(copy.deepcopy(path))
                    
        elif "sheets" in f:
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == '#009954':
                    main_elements.append(copy.deepcopy(path))
            for mask in root.findall(f".//{ns}mask"):
                if mask.attrib.get('id') == 'a':
                    for rect in mask.findall(f".//{ns}rect"):
                        r = copy.deepcopy(rect)
                        r.attrib['fill'] = '#0ebc5f'
                        main_elements.append(r)
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('stroke') == '#fff':
                    main_elements.append(copy.deepcopy(path))
                    
        elif "meet" in f:
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == 'url(#a)':
                    p = copy.deepcopy(path)
                    p.attrib['fill'] = gradient_colors.get('a', '#f6a100')
                    main_elements.append(p)
            for path in root.findall(f".//{ns}path"):
                if path.attrib.get('fill') == 'url(#b)':
                    p = copy.deepcopy(path)
                    p.attrib['fill'] = gradient_colors.get('b', '#ffe921')
                    main_elements.append(p)
            for circle in root.findall(f".//{ns}circle"):
                if circle.attrib.get('fill') == '#fff':
                    main_elements.append(copy.deepcopy(circle))

    # Deduplicate elements
    main_elements_dedup = []
    seen = set()
    for el in main_elements:
        xml_str = ET.tostring(el, encoding='unicode')
        if xml_str not in seen:
            seen.add(xml_str)
            main_elements_dedup.append(el)

    if len(defs) > 0 and "gmail" not in f:
        new_root.append(defs)
    
    main_g = ET.Element(f"{ns}g")
    main_g.attrib['transform'] = "translate(6, 6) scale(0.2708333)"
    for el in main_elements_dedup:
        main_g.append(el)
        
    shadow_g = copy.deepcopy(main_g)
    strip_attributes_recursive(shadow_g, ['fill', 'stroke'])
    shadow_g.attrib['transform'] = "translate(6, 7) scale(0.2708333)"
    shadow_g.attrib['fill'] = "#000000"
    shadow_g.attrib['opacity'] = "0.2"
    
    new_root.append(shadow_g)
    new_root.append(main_g)
    
    new_tree = ET.ElementTree(new_root)
    new_tree.write(os.path.join(out_dir, f), xml_declaration=True, encoding='utf-8')

print("Applied perfect shapes for Keep and Drive.")
