import re

paths = [
    "M96.002,139.086l45.92295,-79.54155l32.01705,55.45555c14.626,25.334 -3.657,57.001 -32.91,57.001h-26.02597z",
    "M69.052,92.422l45.94627,79.579h-64.03127c-29.253,0 -47.536,-31.667 -32.91,-57.001l13.03532,-22.578z",
    "M122.943,92.428l-91.85414,0l32.00114,-55.428c14.626,-25.333 51.193,-25.334 65.819,0l13.01764,22.54738z"
]

def transform_path(path_str, scale, tx, ty):
    tokens = re.findall(r'([A-Za-z])|([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', path_str)
    out = []
    cmd = ''
    toks = []
    for t in tokens:
        if t[0]: toks.append(('CMD', t[0]))
        if t[1]: toks.append(('NUM', float(t[1])))
        
    idx = 0
    while idx < len(toks):
        if toks[idx][0] == 'CMD':
            cmd = toks[idx][1]
            out.append(cmd)
            idx += 1
        else:
            if cmd in 'MmLlTt':
                x = toks[idx][1]
                y = toks[idx+1][1]
                if cmd.isupper():
                    out.append(f"{x * scale + tx:.3f},{y * scale + ty:.3f}")
                else:
                    out.append(f"{x * scale:.3f},{y * scale:.3f}")
                idx += 2
            elif cmd in 'Hh':
                x = toks[idx][1]
                if cmd.isupper():
                    out.append(f"{x * scale + tx:.3f}")
                else:
                    out.append(f"{x * scale:.3f}")
                idx += 1
            elif cmd in 'Vv':
                y = toks[idx][1]
                if cmd.isupper():
                    out.append(f"{y * scale + ty:.3f}")
                else:
                    out.append(f"{y * scale:.3f}")
                idx += 1
            elif cmd in 'Cc':
                x1, y1, x2, y2, x, y = [toks[idx+j][1] for j in range(6)]
                if cmd.isupper():
                    out.append(f"{x1 * scale + tx:.3f},{y1 * scale + ty:.3f} {x2 * scale + tx:.3f},{y2 * scale + ty:.3f} {x * scale + tx:.3f},{y * scale + ty:.3f}")
                else:
                    out.append(f"{x1 * scale:.3f},{y1 * scale:.3f} {x2 * scale:.3f},{y2 * scale:.3f} {x * scale:.3f},{y * scale:.3f}")
                idx += 6
            else:
                idx += 1
                
    return " ".join(out).replace(" ,", ",").replace("  ", " ")

print("YELLOW: " + transform_path(paths[0], 0.34, -0.47, -1.58))
print("BLUE: " + transform_path(paths[1], 0.34, -0.47, -1.58))
print("GREEN: " + transform_path(paths[2], 0.34, -0.47, -1.58))

print("YELLOW SHADOW: " + transform_path(paths[0], 0.34, -0.47, -0.58))
print("BLUE SHADOW: " + transform_path(paths[1], 0.34, -0.47, -0.58))
print("GREEN SHADOW: " + transform_path(paths[2], 0.34, -0.47, -0.58))
