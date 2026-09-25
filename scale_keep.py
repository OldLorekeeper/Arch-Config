import re

paths = [
    "M96 56c-18.4 0-32 14.4-32 33.6v62.8c0 19.2 13.6 33.6 32 33.6s32-14.4 32-33.6V89.6C128 70.4 114.4 56 96 56",
    "M78 127c0-7.18 5.82-13 13-13h10c7.18 0 13 5.82 13 13s-5.82 13-13 13H91c-7.18 0-13-5.82-13-13"
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
            elif cmd in 'Ss':
                x2, y2, x, y = [toks[idx+j][1] for j in range(4)]
                if cmd.isupper():
                    out.append(f"{x2 * scale + tx:.3f},{y2 * scale + ty:.3f} {x * scale + tx:.3f},{y * scale + ty:.3f}")
                else:
                    out.append(f"{x2 * scale:.3f},{y2 * scale:.3f} {x * scale:.3f},{y * scale:.3f}")
                idx += 4
            else:
                idx += 1
                
    return " ".join(out).replace(" ,", ",").replace("  ", " ")

print("BASE: " + transform_path(paths[0], 0.315, 1.76, 1.48))
print("PILL: " + transform_path(paths[1], 0.315, 1.76, 1.48))

print("BASE SHADOW: " + transform_path(paths[0], 0.315, 1.76, 2.48))
print("PILL SHADOW: " + transform_path(paths[1], 0.315, 1.76, 2.48))

