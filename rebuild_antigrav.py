import os

with open("/tmp/antigrav_paths.txt") as f:
    lines = [line.strip() for line in f.readlines()]

shadow = lines[1]
main = lines[3]

svg = f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <radialGradient id="topGlow" cx="50%" cy="15%" r="55%">
      <stop offset="0%" stop-color="#fbbc04" />
      <stop offset="35%" stop-color="#fc413d" />
      <stop offset="100%" stop-color="#fc413d" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="leftGlow" cx="20%" cy="50%" r="55%">
      <stop offset="0%" stop-color="#00b95c" />
      <stop offset="100%" stop-color="#00b95c" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="rightGlow" cx="80%" cy="50%" r="55%">
      <stop offset="0%" stop-color="#8b5cf6" />
      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0" />
    </radialGradient>
  </defs>

  <g opacity="0.2">
    <path fill="#000000" d="{shadow}" />
  </g>
  <g>
    <path fill="#3186ff" d="{main}" />
    <path fill="url(#leftGlow)" d="{main}" />
    <path fill="url(#rightGlow)" d="{main}" />
    <path fill="url(#topGlow)" d="{main}" />
  </g>
</svg>
"""

with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity.svg", "w") as f:
    f.write(svg)

print("Generated google-antigravity.svg")
