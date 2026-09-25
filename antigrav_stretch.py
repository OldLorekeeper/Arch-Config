import re
import math

path_d = "M 89.699204,93.694987 C 94.365903,97.195016 101.366,94.861698 94.949201,88.44499 75.699203,69.77829 79.782499,18.444981 55.8659,18.444981 c -23.916701,0 -19.833401,51.333309 -39.083399,70.000009 -6.9999897,6.999996 0.583299,8.750026 5.249998,5.249997 18.083403,-12.249992 16.9167,-33.833288 33.833401,-33.833288 16.916603,0 15.749999,21.583296 33.833304,33.833288 z"

# I will write a script to transform with separate sx and sy
def transform_path(d, sx, sy, tx, ty):
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
            out.append(f"{flat_tokens[i]*sx + tx:.3f},{flat_tokens[i+1]*sy + ty:.3f}")
            i += 2
        elif cmd == 'C':
            out.append(f"{flat_tokens[i]*sx + tx:.3f},{flat_tokens[i+1]*sy + ty:.3f}")
            out.append(f"{flat_tokens[i+2]*sx + tx:.3f},{flat_tokens[i+3]*sy + ty:.3f}")
            out.append(f"{flat_tokens[i+4]*sx + tx:.3f},{flat_tokens[i+5]*sy + ty:.3f}")
            i += 6
        elif cmd == 'c':
            out.append(f"{flat_tokens[i]*sx:.3f},{flat_tokens[i+1]*sy:.3f}")
            out.append(f"{flat_tokens[i+2]*sx:.3f},{flat_tokens[i+3]*sy:.3f}")
            out.append(f"{flat_tokens[i+4]*sx:.3f},{flat_tokens[i+5]*sy:.3f}")
            i += 6
            
    return " ".join(out)

# Original bounding box: X in [9.78, 101.37], Width = 91.59
# Y in [18.44, 97.20], Height = 78.76

# Target Height: 56. Target Y center: 32.
# sy = 56 / 78.76 = 0.711
sy = 0.711
ty = 32 - (57.82 * sy)

# Target Width: 56 (max safe width). Target X center: 32.
# sx = 56 / 91.59 = 0.611
sx = 0.611
tx = 32 - (55.57 * sx)

print("SHADOW:")
print(transform_path(path_d, sx, sy, tx, ty + 1))
print("MAIN:")
print(transform_path(path_d, sx, sy, tx, ty))
