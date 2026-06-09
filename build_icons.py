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

# sun (circle)
SUN_C, SUN_R = (256, 212), 72
cx, cy, r = P(*SUN_C)[0], P(*SUN_C)[1], SUN_R * sc
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)

# rays — evenly spaced across the upper half, each the same distance from the sun's edge
ray_inner, ray_outer = SUN_R + 28, SUN_R + 56
for deg in (0, 45, 90, 135, 180):
    rad = math.radians(deg)
    dx, dy = math.cos(rad), -math.sin(rad)
    a = (SUN_C[0] + ray_inner * dx, SUN_C[1] + ray_inner * dy)
    b = (SUN_C[0] + ray_outer * dx, SUN_C[1] + ray_outer * dy)
    stamp(d, seg_points(P(*a), P(*b)), 15, AMBER)

# furrows
furrows = [((96, 332), (256, 280), (416, 332)),
           ((96, 390), (256, 338), (416, 390)),
           ((122, 444), (256, 400), (390, 444))]
for p0, c, p2 in furrows:
    stamp(d, quad_points(P(*p0), P(*c), P(*p2)), 23, GREEN_LT)

for name, size in [("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
    img.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name))
    print("wrote", name)
