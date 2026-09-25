import os

with open("/tmp/antigrav_paths.txt") as f:
    lines = [line.strip() for line in f.readlines()]

shadow = lines[1]
main = lines[3]

svg = f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <linearGradient id="mainGrad" x1="50%" y1="100%" x2="50%" y2="0%">
      <stop offset="0%" stop-color="#3186ff" />
      <stop offset="50%" stop-color="#3186ff" />
      <stop offset="70%" stop-color="#0ebc5f" />
      <stop offset="85%" stop-color="#ffbe00" />
      <stop offset="100%" stop-color="#fc413d" />
    </linearGradient>
  </defs>

  <g opacity="0.2">
    <path fill="#000000" d="{shadow}" />
  </g>
  <g>
    <path fill="url(#mainGrad)" d="{main}" />
  </g>
</svg>
"""

with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity.svg", "w") as f:
    f.write(svg)

print("Generated google-antigravity.svg with linear gradient")
