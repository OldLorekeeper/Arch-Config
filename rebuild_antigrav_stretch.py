import os

with open("/tmp/antigrav_stretch.txt") as f:
    lines = [line.strip() for line in f.readlines()]

shadow = lines[1]
main = lines[3]

svg = f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <!-- Concentrated Green from top left -->
    <radialGradient id="greenGlow" cx="25%" cy="20%" r="35%">
      <stop offset="0%" stop-color="#0ebc5f" />
      <stop offset="100%" stop-color="#0ebc5f" stop-opacity="0" />
    </radialGradient>
    
    <!-- Concentrated Red from top right -->
    <radialGradient id="redGlow" cx="75%" cy="20%" r="35%">
      <stop offset="0%" stop-color="#fc413d" />
      <stop offset="100%" stop-color="#fc413d" stop-opacity="0" />
    </radialGradient>
    
    <!-- Slight Yellow exactly at the top tip -->
    <radialGradient id="yellowGlow" cx="50%" cy="5%" r="25%">
      <stop offset="0%" stop-color="#ffbe00" />
      <stop offset="100%" stop-color="#ffbe00" stop-opacity="0" />
    </radialGradient>
  </defs>

  <!-- Papirus Shadow -->
  <g opacity="0.2">
    <path fill="#000000" d="{shadow}" />
  </g>
  
  <g>
    <!-- Predominantly Base Blue -->
    <path fill="#3186ff" d="{main}" />
    
    <!-- Overlaid Gradients only at the tip region -->
    <path fill="url(#greenGlow)" d="{main}" />
    <path fill="url(#redGlow)" d="{main}" />
    <path fill="url(#yellowGlow)" d="{main}" />
  </g>
</svg>
"""

with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity.svg", "w") as f:
    f.write(svg)

print("Generated stretched google-antigravity.svg")
