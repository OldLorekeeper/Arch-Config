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
            # relative coordinates only scale, no translation!
            out.append(f"{flat_tokens[i]*scale:.3f},{flat_tokens[i+1]*scale:.3f}")
            out.append(f"{flat_tokens[i+2]*scale:.3f},{flat_tokens[i+3]*scale:.3f}")
            out.append(f"{flat_tokens[i+4]*scale:.3f},{flat_tokens[i+5]*scale:.3f}")
            i += 6
            
    return " ".join(out)

# Scale = 0.611, tx = -1.95, ty = -3.33
print("SHADOW:")
print(transform_path(path_d, 0.611, -1.95, -2.33)) # Y + 1
print("MAIN:")
print(transform_path(path_d, 0.611, -1.95, -3.33))
