import os
import re

svg_dir = "/home/curtis/Downloads/Google-Workspace-logos/"

for f in sorted(os.listdir(svg_dir)):
    if not f.endswith('-2026.svg'): continue
    with open(os.path.join(svg_dir, f)) as file:
        content = file.read()
    
    # Extract all numbers from all paths and rects to get a rough bounding box
    # We remove masks and clip paths first? Just look at all numbers
    # Actually, the easiest way is to look at viewBox and width/height.
    # But we want the visual bounding box of the paths.
    nums = []
    
    # Just to avoid mask paths throwing us off, let's remove masks
    content = re.sub(r'<mask.*?>.*?</mask>', '', content, flags=re.DOTALL)
    
    # Find all path d="..." and rect x,y,width,height
    for match in re.finditer(r'd="([^"]+)"', content):
        d = match.group(1)
        tokens = re.findall(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', d)
        nums.extend([float(x) for x in tokens])
        
    for match in re.finditer(r'<rect([^>]+)>', content):
        rect = match.group(1)
        x = float(re.search(r'x="([^"]+)"', rect).group(1)) if re.search(r'x="([^"]+)"', rect) else 0
        y = float(re.search(r'y="([^"]+)"', rect).group(1)) if re.search(r'y="([^"]+)"', rect) else 0
        w = float(re.search(r'width="([^"]+)"', rect).group(1)) if re.search(r'width="([^"]+)"', rect) else 0
        h = float(re.search(r'height="([^"]+)"', rect).group(1)) if re.search(r'height="([^"]+)"', rect) else 0
        nums.extend([x, y, x+w, y+h])
        
    if nums:
        xs = [n for n in nums if 0 <= n <= 192]
        if xs:
            xmin = min(xs)
            xmax = max(xs)
            # This is a very rough heuristic but might give a sense
            print(f"{f}: approx min={xmin}, max={xmax}")
