import os

paths_txt = "/tmp/keep_paths.txt"
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
  <g opacity="0.2" fill="#000000">
    <path d="{paths['BASE SHADOW']}" />
    <circle cx="32" cy="27.05" r="22.05" />
  </g>

  <!-- Main Group -->
  <g>
    <!-- Deeper orange base -->
    <path fill="#f6a100" d="{paths['BASE']}" />
    
    <!-- Yellow circle -->
    <circle cx="32" cy="26.05" r="22.05" fill="#ffbe00" />
    
    <!-- White Pill -->
    <path fill="#ffffff" d="{paths['PILL']}" />
  </g>
</svg>
"""
with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-keep-2026.svg", "w") as f:
    f.write(svg)

print("Updated Keep SVG")
