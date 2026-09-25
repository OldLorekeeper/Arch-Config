import os

out_path = "/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-keep-2026.svg"

bulb_mask = "M166 78c0 27.13-15.434 50.381-38 62-9.591 4.938-20.47 8-32 8s-22.41-3.062-32-8c-22.566-11.619-38-34.87-38-62C26 39.34 57.34 8 96 8s70 31.34 70 70"
bulb_circle = '<circle cx="96" cy="78" r="70" fill="#ffbe00" />'
filament = '<path fill="#fff" d="M78 127c0-7.18 5.82-13 13-13h10c7.18 0 13 5.82 13 13s-5.82 13-13 13H91c-7.18 0-13-5.82-13-13" />'

base_mask = "M56 140h80v46H56z"
base_pill = "M96 56c-18.4 0-32 14.4-32 33.6v62.8c0 19.2 13.6 33.6 32 33.6s32-14.4 32-33.6V89.6C128 70.4 114.4 56 96 56"

svg_content = f"""<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <!-- Shadow Clips -->
    <clipPath id="shadowBulbClip">
      <path transform="translate(6, 7) scale(0.2708333)" d="{bulb_mask}" />
    </clipPath>
    <clipPath id="shadowBaseClip">
      <path transform="translate(6, 7) scale(0.2708333)" d="{base_mask}" />
    </clipPath>

    <!-- Main Clips -->
    <clipPath id="mainBulbClip">
      <path transform="translate(6, 6) scale(0.2708333)" d="{bulb_mask}" />
    </clipPath>
    <clipPath id="mainBaseClip">
      <path transform="translate(6, 6) scale(0.2708333)" d="{base_mask}" />
    </clipPath>
  </defs>

  <!-- Shadow Group -->
  <g opacity="0.2">
    <!-- Bulb Body Shadow -->
    <circle clip-path="url(#shadowBulbClip)" transform="translate(6, 7) scale(0.2708333)" cx="96" cy="78" r="70" fill="#000000" />
    <path clip-path="url(#shadowBulbClip)" transform="translate(6, 7) scale(0.2708333)" d="M78 127c0-7.18 5.82-13 13-13h10c7.18 0 13 5.82 13 13s-5.82 13-13 13H91c-7.18 0-13-5.82-13-13" fill="#000000" />
    
    <!-- Bulb Base Shadow -->
    <path clip-path="url(#shadowBaseClip)" transform="translate(6, 7) scale(0.2708333)" d="{base_pill}" fill="#000000" />
  </g>

  <!-- Main Group -->
  <g>
    <!-- Bulb Body Main -->
    <circle clip-path="url(#mainBulbClip)" transform="translate(6, 6) scale(0.2708333)" cx="96" cy="78" r="70" fill="#ffbe00" />
    <path clip-path="url(#mainBulbClip)" transform="translate(6, 6) scale(0.2708333)" d="M78 127c0-7.18 5.82-13 13-13h10c7.18 0 13 5.82 13 13s-5.82 13-13 13H91c-7.18 0-13-5.82-13-13" fill="#ffffff" />
    
    <!-- Bulb Base Main -->
    <path clip-path="url(#mainBaseClip)" transform="translate(6, 6) scale(0.2708333)" d="{base_pill}" fill="#f6a100" />
  </g>
</svg>
"""

with open(out_path, "w") as f:
    f.write(svg_content)

print("Keep fixed.")
