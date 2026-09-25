import os
import re

svg_dir = "/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/"

# 1. Update Gmail and Calendar transforms
# Gmail: slightly larger (scale 0.34)
# Calendar: smaller/less tall (scale 0.32)
configs = {
    'gmail-2026.svg':     {'s': 0.340, 't': -0.640},
    'google-calendar-2026.svg': {'s': 0.320, 't': 1.280},
}

for f, cfg in configs.items():
    path = os.path.join(svg_dir, f)
    if not os.path.exists(path): continue
    with open(path, 'r') as file:
        content = file.read()
    
    # Replace all transform="translate(...) scale(...)"
    new_transform = f'transform="translate({cfg["t"]:.3f}, {cfg["t"]:.3f}) scale({cfg["s"]:.3f})"'
    content = re.sub(r'transform="translate\([^)]+\)\s+scale\([^)]+\)"', new_transform, content)
    
    with open(path, 'w') as file:
        file.write(content)

print("Updated simple SVGs with new transforms.")

# 2. Update Drive in scale_paths.py
# New Drive: scale 0.34, tx -0.47, ty -1.58
scale_paths_path = "/home/curtis/Obsidian/Arch-Config/scale_paths.py"
with open(scale_paths_path, 'r') as file:
    scale_paths_content = file.read()

# Replace the specific print statements
# We know they currently have 0.385, -4.767, -7.245 (and -6.245 for shadow)
# Let's use re.sub for safety
scale_paths_content = re.sub(r'0\.385, -4\.767, -7\.245', '0.34, -0.47, -1.58', scale_paths_content)
scale_paths_content = re.sub(r'0\.385, -4\.767, -6\.245', '0.34, -0.47, -0.58', scale_paths_content)

with open(scale_paths_path, 'w') as file:
    file.write(scale_paths_content)
    
print("Updated scale_paths.py")
