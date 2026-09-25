import os

with open("/tmp/antigrav_paths.txt") as f:
    lines = [line.strip() for line in f.readlines()]

shadow = lines[1]
main = lines[3]

svg = f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <!-- Green from top left -->
    <radialGradient id="greenGlow" cx="25%" cy="40%" r="45%">
      <stop offset="0%" stop-color="#0ebc5f" />
      <stop offset="100%" stop-color="#0ebc5f" stop-opacity="0" />
    </radialGradient>
    
    <!-- Red from top right -->
    <radialGradient id="redGlow" cx="75%" cy="40%" r="45%">
      <stop offset="0%" stop-color="#fc413d" />
      <stop offset="100%" stop-color="#fc413d" stop-opacity="0" />
    </radialGradient>
    
    <!-- Slight Yellow at the top intersection -->
    <radialGradient id="yellowGlow" cx="50%" cy="15%" r="35%">
      <stop offset="0%" stop-color="#ffbe00" />
      <stop offset="100%" stop-color="#ffbe00" stop-opacity="0" />
    </radialGradient>
  </defs>

  <!-- Papirus Shadow -->
  <g opacity="0.2">
    <path fill="#000000" d="{shadow}" />
  </g>
  
  <g>
    <!-- Base Blue (from bottom up) -->
    <path fill="#3186ff" d="{main}" />
    
    <!-- Overlaid Gradients -->
    <path fill="url(#greenGlow)" d="{main}" />
    <path fill="url(#redGlow)" d="{main}" />
    <path fill="url(#yellowGlow)" d="{main}" />
  </g>
</svg>
"""

with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity.svg", "w") as f:
    f.write(svg)

print("Generated google-antigravity.svg with multi-radial intersection logic")
