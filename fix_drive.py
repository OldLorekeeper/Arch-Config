import os

out_path = "/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-drive-2026.svg"

# The original 192x192 Drive paths
clip_d = "M63.09 37c14.626-25.333 51.193-25.334 65.819 0l45.033 78c14.626 25.334-3.657 57.001-32.91 57.001H50.967c-29.253 0-47.536-31.667-32.91-57.001z"
yellow_d = "M206.905 172.02h-91.888l-19.015-32.934 45.944-79.578z"
blue_d = "M-14.919 172.006 50.04 59.494v.002L31.032 92.422h38.02L115 172.004l-129.918.001z"
green_d = "M96.007-20.085 141.954 59.5l-19.011 32.928H31.048z"

svg_content = f"""<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <!-- Shadow Clip -->
    <clipPath id="clipShadow">
      <path transform="translate(6, 7) scale(0.2708333)" d="{clip_d}" />
    </clipPath>
    <!-- Main Clip -->
    <clipPath id="clipMain">
      <path transform="translate(6, 6) scale(0.2708333)" d="{clip_d}" />
    </clipPath>
  </defs>

  <!-- Shadow Group -->
  <g opacity="0.2">
    <path clip-path="url(#clipShadow)" transform="translate(6, 7) scale(0.2708333)" fill="#000000" d="{yellow_d}" />
    <path clip-path="url(#clipShadow)" transform="translate(6, 7) scale(0.2708333)" fill="#000000" d="{blue_d}" />
    <path clip-path="url(#clipShadow)" transform="translate(6, 7) scale(0.2708333)" fill="#000000" d="{green_d}" />
  </g>

  <!-- Main Group -->
  <g>
    <path clip-path="url(#clipMain)" transform="translate(6, 6) scale(0.2708333)" fill="#fec700" d="{yellow_d}" />
    <path clip-path="url(#clipMain)" transform="translate(6, 6) scale(0.2708333)" fill="#3186ff" d="{blue_d}" />
    <path clip-path="url(#clipMain)" transform="translate(6, 6) scale(0.2708333)" fill="#0ebc5f" d="{green_d}" />
  </g>
</svg>
"""

with open(out_path, "w") as f:
    f.write(svg_content)

print("Drive fixed.")
