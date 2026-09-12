#!/usr/bin/env python3
"""Full-bleed halftone section backgrounds.

Procedural scene (a glowing sphere with radial streaks and a floor reflection
for the blue band; a spiral bloom for the pink band) sampled on a grid; each
cell gets a dot whose radius tracks the local brightness -> a halftone image.
Dots are bucketed by brightness and emitted as a handful of round-capped paths.
"""
import math
import random

W, H = 1200, 820
STEP = 10.0


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(round(lerp(c1[i], c2[i], t)) for i in range(3))


def hexc(c):
    return "#%02x%02x%02x" % c


def scene_blue(nx, ny):
    cx, cy = 0.52, 0.4
    dx, dy = nx - cx, (ny - cy) * 1.05
    d = math.hypot(dx, dy) / 0.30
    ang = math.atan2(dy, dx)
    body = clamp(1.18 - d) * 0.85
    rim = math.exp(-((d - 1.0) * 3.6) ** 2) * 0.75
    streak = (0.5 + 0.5 * math.sin(ang * 28 + d * 2.5)) * clamp(1.5 - d) * 0.55
    floor_y = 0.72
    floor = clamp((ny - floor_y) * 4) * 0.30 * (0.45 + 0.55 * math.sin(nx * 46))
    refl = 0.0
    if ny > floor_y:
        my = 2 * floor_y - ny
        rdx, rdy = nx - cx, (my - cy) * 1.05
        rd = math.hypot(rdx, rdy) / 0.30
        refl = clamp(1.18 - rd) * 0.22 * clamp(1.5 - (ny - floor_y) * 5)
    top = (1 - ny) * 0.12
    return clamp(body + rim + streak + floor + refl + top)


def scene_pink(nx, ny):
    cx, cy = 0.5, 0.42
    dx, dy = nx - cx, (ny - cy) * 1.02
    r = math.hypot(dx, dy) / 0.32
    ang = math.atan2(dy, dx)
    petals = 0.5 + 0.5 * math.sin(ang * 5.0 + r * 4.6)
    swirl = 0.5 + 0.5 * math.sin(ang * 3.0 - r * 3.0 + 1.4)
    bloom = clamp(1.22 - r) * (0.35 + 0.4 * petals + 0.3 * swirl)
    rim = math.exp(-((r - 1.0) * 3.8) ** 2) * 0.55
    floor_y = 0.74
    floor = clamp((ny - floor_y) * 4) * 0.24 * (0.45 + 0.55 * math.sin(nx * 50))
    refl = 0.0
    if ny > floor_y:
        my = 2 * floor_y - ny
        rr = math.hypot(nx - cx, (my - cy) * 1.02) / 0.32
        refl = clamp(1.22 - rr) * 0.2 * clamp(1.5 - (ny - floor_y) * 5)
    return clamp(bloom + rim + floor + refl + (1 - ny) * 0.08)


BINS = 9


def halftone(scene, bg, dark, name, seed=1):
    rnd = random.Random(seed)
    buckets = {i: [] for i in range(BINS)}
    y = STEP / 2
    while y < H:
        x = STEP / 2
        while x < W:
            v = scene(x / W, y / H)
            v = clamp(v + rnd.uniform(-0.04, 0.04))
            if v > 0.03:
                bi = min(BINS - 1, int(v * BINS))
                jx = round(x + rnd.uniform(-1.2, 1.2), 1)
                jy = round(y + rnd.uniform(-1.2, 1.2), 1)
                buckets[bi].append(f"M{jx} {jy}h.01")
            x += STEP
        y += STEP

    parts = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        'preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
        f'<rect width="{W}" height="{H}" fill="{hexc(bg)}"/>'
    ]
    for bi in range(BINS):
        segs = buckets[bi]
        if not segs:
            continue
        v = (bi + 0.5) / BINS
        col = mix(dark, (255, 255, 255), v ** 0.8)
        dot = STEP * (0.18 + 0.72 * v)
        op = round(0.35 + 0.6 * v, 2)
        parts.append(
            f'<path stroke="{hexc(col)}" stroke-linecap="round" '
            f'stroke-width="{dot:.2f}" stroke-opacity="{op}" d="' + "".join(segs) + '"/>'
        )
    parts.append("</svg>")
    svg = "".join(parts)
    open(name, "w").write(svg)
    print(f"wrote {name}  ({len(svg)} bytes)")


if __name__ == "__main__":
    halftone(scene_blue, (0x2f, 0x43, 0xf0), (0x1a, 0x1b, 0x8a), "bg-build.svg", 7)
    halftone(scene_pink, (0xf0, 0x15, 0x7e), (0xa8, 0x08, 0x55), "bg-contact.svg", 11)
