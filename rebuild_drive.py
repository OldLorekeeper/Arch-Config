import os

paths_txt = "/tmp/drive_paths.txt"
with open(paths_txt) as f:
    lines = f.readlines()

paths = {}
for line in lines:
    if ":" in line:
        k, v = line.strip().split(":", 1)
        paths[k.strip()] = v.strip()

svg = f"""<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <!-- Shadow Group -->
  <g opacity="0.2">
    <path fill="#000000" d="{paths['YELLOW SHADOW']}" />
    <path fill="#000000" d="{paths['BLUE SHADOW']}" />
    <path fill="#000000" d="{paths['GREEN SHADOW']}" />
  </g>

  <!-- Main Group -->
  <g>
    <!-- Yellow -->
    <path fill="#fec700" d="{paths['YELLOW']}" />
    <!-- Blue -->
    <path fill="#3186ff" d="{paths['BLUE']}" />
    <!-- Green -->
    <path fill="#0ebc5f" d="{paths['GREEN']}" />
  </g>
</svg>
"""
with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-drive-2026.svg", "w") as f:
    f.write(svg)

print("Updated Drive SVG")
