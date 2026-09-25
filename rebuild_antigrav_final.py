import re

path_d = "M 89.699204,93.694987 C 94.365903,97.195016 101.366,94.861698 94.949201,88.44499 75.699203,69.77829 79.782499,18.444981 55.8659,18.444981 c -23.916701,0 -19.833401,51.333309 -39.083399,70.000009 -6.9999897,6.999996 0.583299,8.750026 5.249998,5.249997 18.083403,-12.249992 16.9167,-33.833288 33.833401,-33.833288 16.916603,0 15.749999,21.583296 33.833304,33.833288 z"

def transform_path(d, scale, tx, ty):
    tokens = re.findall(r'([A-Za-z])|([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', d)
    out = []
    cmd = ''
    i = 0
    flat_tokens = []
    for t in tokens:
        if t[0]: flat_tokens.append(t[0])
        else: flat_tokens.append(float(t[1]))
        
    while i < len(flat_tokens):
        t = flat_tokens[i]
        if isinstance(t, str):
            cmd = t
            out.append(cmd)
            i += 1
            if cmd.upper() == 'Z': continue
            
        if cmd == 'M':
            out.append(f"{flat_tokens[i]*scale + tx:.3f},{flat_tokens[i+1]*scale + ty:.3f}")
            i += 2
        elif cmd == 'C':
            out.append(f"{flat_tokens[i]*scale + tx:.3f},{flat_tokens[i+1]*scale + ty:.3f}")
            out.append(f"{flat_tokens[i+2]*scale + tx:.3f},{flat_tokens[i+3]*scale + ty:.3f}")
            out.append(f"{flat_tokens[i+4]*scale + tx:.3f},{flat_tokens[i+5]*scale + ty:.3f}")
            i += 6
        elif cmd == 'c':
            out.append(f"{flat_tokens[i]*scale:.3f},{flat_tokens[i+1]*scale:.3f}")
            out.append(f"{flat_tokens[i+2]*scale:.3f},{flat_tokens[i+3]*scale:.3f}")
            out.append(f"{flat_tokens[i+4]*scale:.3f},{flat_tokens[i+5]*scale:.3f}")
            i += 6
            
    return " ".join(out)

scale = 0.690
tx = 32 - (55.574 * scale)
ty = 32 - (57.820 * scale)

shadow = transform_path(path_d, scale, tx, ty + 1)
main = transform_path(path_d, scale, tx, ty)

# Use #528ff5 which is the exact lighter blue from Papirus' native google-docs.svg
svg = f"""<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <defs>
    <!-- Concentrated Green from top left -->
    <radialGradient id="greenGlow" cx="20%" cy="20%" r="35%">
      <stop offset="0%" stop-color="#0ebc5f" />
      <stop offset="100%" stop-color="#0ebc5f" stop-opacity="0" />
    </radialGradient>
    
    <!-- Concentrated Red from top right -->
    <radialGradient id="redGlow" cx="80%" cy="20%" r="35%">
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
    <!-- Predominantly Base Blue (Papirus Docs Lighter Blue) -->
    <path fill="#528ff5" d="{main}" />
    
    <!-- Overlaid Gradients only at the tip region -->
    <path fill="url(#greenGlow)" d="{main}" />
    <path fill="url(#redGlow)" d="{main}" />
    <path fill="url(#yellowGlow)" d="{main}" />
  </g>
</svg>
"""

with open("/home/curtis/Obsidian/Arch-Config/Resources/Icons/GoogleWorkspace/google-antigravity.svg", "w") as f:
    f.write(svg)

print("Generated scaled google-antigravity.svg")
