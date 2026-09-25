import re

path_d = "M 89.699204,93.694987 C 94.365903,97.195016 101.366,94.861698 94.949201,88.44499 75.699203,69.77829 79.782499,18.444981 55.8659,18.444981 c -23.916701,0 -19.833401,51.333309 -39.083399,70.000009 -6.9999897,6.999996 0.583299,8.750026 5.249998,5.249997 18.083403,-12.249992 16.9167,-33.833288 33.833401,-33.833288 16.916603,0 15.749999,21.583296 33.833304,33.833288 z"

def get_rough_bbox(d):
    nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d)]
    # This is an absolute+relative path. Let's convert to absolute.
    tokens = re.findall(r'([A-Za-z])|([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', d)
    
    xs, ys = [], []
    cx, cy = 0, 0
    cmd = ''
    i = 0
    
    def add(x, y):
        xs.append(x)
        ys.append(y)
        
    flat_tokens = []
    for t in tokens:
        if t[0]: flat_tokens.append(t[0])
        else: flat_tokens.append(float(t[1]))
        
    while i < len(flat_tokens):
        t = flat_tokens[i]
        if isinstance(t, str):
            cmd = t
            i += 1
            if cmd.upper() == 'Z': continue
        
        if cmd == 'M':
            cx, cy = flat_tokens[i], flat_tokens[i+1]
            add(cx, cy)
            i += 2
        elif cmd == 'C':
            cx, cy = flat_tokens[i+4], flat_tokens[i+5]
            add(flat_tokens[i], flat_tokens[i+1])
            add(flat_tokens[i+2], flat_tokens[i+3])
            add(cx, cy)
            i += 6
        elif cmd == 'c':
            add(cx + flat_tokens[i], cy + flat_tokens[i+1])
            add(cx + flat_tokens[i+2], cy + flat_tokens[i+3])
            cx += flat_tokens[i+4]
            cy += flat_tokens[i+5]
            add(cx, cy)
            i += 6
            
    return min(xs), max(xs), min(ys), max(ys)

xmin, xmax, ymin, ymax = get_rough_bbox(path_d)
print(f"X: {xmin} to {xmax}, Y: {ymin} to {ymax}")
print(f"Width: {xmax-xmin}, Height: {ymax-ymin}")
print(f"Center X: {(xmin+xmax)/2}, Y: {(ymin+ymax)/2}")
