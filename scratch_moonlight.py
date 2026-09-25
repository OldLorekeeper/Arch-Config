import xml.etree.ElementTree as ET
import copy

def bake_moonlight_icon():
    # Constructing the SVG elements directly
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    root = ET.Element('{http://www.w3.org/2000/svg}svg', {
        'viewBox': '0 0 64 64',
        'width': '64',
        'height': '64'
    })
    
    # 1. Master Drop Shadow for all elements
    shadow_g = ET.Element('{http://www.w3.org/2000/svg}g', {
        'fill': '#000000', 
        'opacity': '0.2', 
        'transform': 'translate(0, 1)'
    })
    
    # 2. Main group with Papirus Highlight Filter
    main_g = ET.Element('{http://www.w3.org/2000/svg}g', {
        'filter': 'url(#papirus-highlight)'
    })
    
    # Definitions for the highlight filter
    defs = ET.Element('{http://www.w3.org/2000/svg}defs')
    filter_el = ET.Element('{http://www.w3.org/2000/svg}filter', {
        'id': 'papirus-highlight',
        'x': '-10%', 'y': '-10%', 'width': '120%', 'height': '120%'
    })
    
    # Filter primitives
    feOffset = ET.Element('{http://www.w3.org/2000/svg}feOffset', {'dy': '1', 'dx': '0', 'in': 'SourceAlpha', 'result': 'offsetDown'})
    feComposite1 = ET.Element('{http://www.w3.org/2000/svg}feComposite', {'in': 'SourceAlpha', 'in2': 'offsetDown', 'operator': 'out', 'result': 'topEdge'})
    feFlood = ET.Element('{http://www.w3.org/2000/svg}feFlood', {'flood-color': '#ffffff', 'flood-opacity': '0.5', 'result': 'whiteHighlight'})
    feComposite2 = ET.Element('{http://www.w3.org/2000/svg}feComposite', {'in': 'whiteHighlight', 'in2': 'topEdge', 'operator': 'in', 'result': 'highlight'})
    
    feMerge = ET.Element('{http://www.w3.org/2000/svg}feMerge')
    feMergeNode1 = ET.Element('{http://www.w3.org/2000/svg}feMergeNode', {'in': 'SourceGraphic'})
    feMergeNode2 = ET.Element('{http://www.w3.org/2000/svg}feMergeNode', {'in': 'highlight'})
    feMerge.extend([feMergeNode1, feMergeNode2])
    
    filter_el.extend([feOffset, feComposite1, feFlood, feComposite2, feMerge])
    defs.append(filter_el)
    root.append(defs)

    # 3. Background Circle (Dark blue/night sky)
    # Papirus rules: circles are 56x56 footprint (r=28)
    bg_circle = ET.Element('{http://www.w3.org/2000/svg}circle', {
        'cx': '32',
        'cy': '32',
        'r': '28',
        'fill': '#1a2b4c' # Deep night blue
    })
    
    # 4. Crescent Moon
    # Rotated a bit for dynamic look
    moon_path = ET.Element('{http://www.w3.org/2000/svg}path', {
        # A moon shape
        'd': 'M 30 13 A 16 16 0 0 0 30 51 A 20 20 0 0 1 30 13 Z',
        'fill': '#ffeb3b',
        'transform': 'rotate(-25 32 32)'
    })
    
    # Let's combine the rotation into the path by doing it in code, or we can use svgelements later.
    # Actually, svgelements is required to bake the paths natively.
    # Let's write the unbaked SVG first and then use svgelements to bake it!
    pass

if __name__ == "__main__":
    pass
