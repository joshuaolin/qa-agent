"""Measure a Figma SVG export: rect geometry plus per-path and per-line bounding boxes of outlined text.

usage: python -I measure_svg.py <export.svg> <out.json>
Bounding boxes use path control points, so curves can overshoot by a fraction of a px.
"""
import json
import re
import sys

src, out = sys.argv[1], sys.argv[2]
svg = open(src, encoding="utf-8").read()
root = re.search(r'<svg[^>]*width="([\d.]+)"[^>]*height="([\d.]+)"', svg)

TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?")
ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def subpaths(d):
    """Yield the points of each subpath (split on M/m) in absolute coordinates."""
    toks = TOKEN.findall(d)
    i, cmd, x, y, sx, sy = 0, None, 0.0, 0.0, 0.0, 0.0
    cur = []
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                x, y = sx, sy
                continue
        n = ARGS[cmd.upper()]
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        rel = cmd.islower()
        up = cmd.upper()
        if up == "M":
            if cur:
                yield cur
            x, y = (x + vals[0], y + vals[1]) if rel else (vals[0], vals[1])
            sx, sy, cur = x, y, [(x, y)]
            cmd = "l" if rel else "L"  # implicit lineto after moveto
            continue
        if up == "H":
            x = x + vals[0] if rel else vals[0]
            cur.append((x, y))
        elif up == "V":
            y = y + vals[0] if rel else vals[0]
            cur.append((x, y))
        elif up == "A":
            x, y = (x + vals[5], y + vals[6]) if rel else (vals[5], vals[6])
            cur.append((x, y))
        else:
            pts = list(zip(vals[0::2], vals[1::2]))
            pts = [(x + px, y + py) for px, py in pts] if rel else pts
            cur.extend(pts)
            x, y = pts[-1]
    if cur:
        yield cur


def bbox(points):
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return {"x": round(min(xs), 2), "y": round(min(ys), 2), "w": round(max(xs) - min(xs), 2),
            "h": round(max(ys) - min(ys), 2), "right": round(max(xs), 2), "bottom": round(max(ys), 2)}


rects = [dict(re.findall(r'(\w+)="([^"]*)"', m)) for m in re.findall(r"<rect\b([^>]*)/?>", svg)]
paths = []
for m in re.finditer(r'<path\b[^>]*d="([^"]+)"[^>]*fill="([^"]+)"', svg):
    subs = [bbox(sp) for sp in subpaths(m.group(1)) if len(sp) > 1]
    # group glyph subpaths into text lines by vertical overlap
    lines = []
    for b in sorted(subs, key=lambda b: b["y"]):
        mid = b["y"] + b["h"] / 2
        for ln in lines:
            if ln["y"] - 2 <= mid <= ln["bottom"] + 2:
                ln["glyphs"].append(b)
                ln["y"], ln["bottom"] = min(ln["y"], b["y"]), max(ln["bottom"], b["bottom"])
                break
        else:
            lines.append({"y": b["y"], "bottom": b["bottom"], "glyphs": [b]})
    line_boxes = [bbox([(g["x"], g["y"]) for g in ln["glyphs"]] + [(g["right"], g["bottom"]) for g in ln["glyphs"]])
                  for ln in lines]
    paths.append({"fill": m.group(2), "bbox": bbox([(b["x"], b["y"]) for b in subs] + [(b["right"], b["bottom"]) for b in subs]),
                  "subpaths": len(subs), "lines": line_boxes})

result = {"source": src, "frame": {"width": float(root.group(1)), "height": float(root.group(2))},
          "outlinedText": "<text" not in svg, "rects": rects, "paths": paths}
json.dump(result, open(out, "w", encoding="utf-8"), indent=2)
print(json.dumps({**result, "paths": [{k: v for k, v in p.items()} for p in paths]}, indent=1))
