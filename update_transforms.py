import os
import re

svg_dir = "/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/"

# 1. Update the transform for the basic SVGs
configs = {
    'gmail-2026.svg':     {'s': 0.318, 't': 1.472},
    'google-calendar-2026.svg': {'s': 0.361, 't': -2.656},
    'google-meet-2026.svg': {'s': 0.341, 't': -0.736},
    'google-sheets-2026.svg': {'s': 0.350, 't': -1.600},
    'google-slides-2026.svg': {'s': 0.333, 't': 0.032},
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
