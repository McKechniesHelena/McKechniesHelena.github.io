"""Render the Ag Tools app icon (rising sun over furrows) to PNGs.

Draws a full-bleed square icon (iOS/Android apply their own rounded mask) at
2x supersample, then downsamples with LANCZOS for crisp anti-aliased edges.
Strokes are drawn by stamping filled circles along each path, which yields
round line caps and smooth thick curves without needing an SVG renderer.
"""
import os
import math
from PIL import Image, ImageDraw

OUT = os.path.dirname(os.path.abspath(__file__))

DESIGN = 512
S = 1024                       # supersampled master
sc = S / DESIGN

BG       = (31, 78, 43)        # #1f4e2b
AMBER    = (246, 194, 68)      # #f6c244
GREEN_LT = (167, 216, 174)     # #a7d8ae


def P(x, y):
    return (x * sc, y * sc)


def stamp(draw, points, design_width, color):
    r = design_width * sc / 2.0
    for x, y in points:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def seg_points(a, b, n=160):
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
            for i in range(n + 1)]


def quad_points(p0, c, p2, n=400):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

# sun as a cog (gear) — 12 teeth with a hollow center
SUN_C = (256, 212)


def gear_pts(c, r_root, r_tip, extra, n=12, tip_frac=0.52):
    pitch = 2 * math.pi / n
    th_half = pitch * tip_frac / 2
    pts = []
    for k in range(n):
        th = k * pitch
        rt = r_tip + extra * max(0.0, -math.sin(th))   # upper teeth stretch into rays
        for r, a in [(rt, th - th_half), (rt, th + th_half),
                     (r_root, th + th_half), (r_root, th + pitch - th_half)]:
            pts.append(P(c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return pts


d.polygon(gear_pts(SUN_C, 64, 88, 42), fill=AMBER)
bx, by = P(*SUN_C)
br = 24 * sc
d.ellipse([bx - br, by - br, bx + br, by + br], fill=BG)

# furrows
furrows = [((96, 332), (256, 280), (416, 332)),
           ((96, 390), (256, 338), (416, 390)),
           ((122, 444), (256, 400), (390, 444))]
for p0, c, p2 in furrows:
    stamp(d, quad_points(P(*p0), P(*c), P(*p2)), 23, GREEN_LT)

for name, size in [("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
    img.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name))
    print("wrote", name)
