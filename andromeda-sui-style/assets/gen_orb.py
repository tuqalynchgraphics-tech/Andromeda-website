#!/usr/bin/env python3
"""Halftone particle-orb backgrounds for Andromeda (Sui-styled build).

Fibonacci-sphere point cloud, swirled, orthographically projected. Dot radius
and opacity fall off toward the back; hue lerps violet -> blue across X with a
white lift on the front. To keep files small at high point counts the dots are
bucketed by (depth, hue) and each bucket is emitted as ONE round-capped path
of zero-length segments rather than thousands of <circle> elements.
"""
import math

VIOLET = (0x6E, 0x3A, 0xE6)
BLUE = (0x3A, 0x4D, 0xF0)
WHITE = (0xFF, 0xFF, 0xFF)

DEPTH_BINS = 8
HUE_BINS = 6


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(round(lerp(c1[i], c2[i], t)) for i in range(3))


def hexc(c):
    return "#%02x%02x%02x" % c


LILAC = (0xD7, 0xC7, 0xFF)

def orb(n_points, size, swirl=2.5, seed_rot=0.5, r_base=None, back_cull=-0.55,
        palette="violet", dot_scale=1.0):
    if r_base is None:
        r_base = size / 300.0
    r_base *= dot_scale
    cx = cy = size / 2.0
    radius = size * 0.46
    golden = math.pi * (3.0 - math.sqrt(5.0))

    buckets = {}          # (di, hi) -> list of "M x y h.01"
    for i in range(n_points):
        y = 1.0 - (i / float(n_points - 1)) * 2.0
        rr = math.sqrt(max(0.0, 1.0 - y * y))
        theta = golden * i
        x = math.cos(theta) * rr
        z = math.sin(theta) * rr
        ang = seed_rot + swirl * (y * 0.5 + 0.5)
        x, z = x * math.cos(ang) - z * math.sin(ang), x * math.sin(ang) + z * math.cos(ang)
        if z < back_cull:
            continue

        px = cx + x * radius
        py = cy - y * radius
        depth = (z + 1.0) / 2.0
        hue_t = min(1.0, max(0.0, (x + 1.0) / 2.0))
        di = min(DEPTH_BINS - 1, int(depth * DEPTH_BINS))
        hi = min(HUE_BINS - 1, int(hue_t * HUE_BINS))
        buckets.setdefault((di, hi), []).append(f"M{px:.1f} {py:.1f}h.01")

    parts = [
        f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" '
        'fill="none" aria-hidden="true" focusable="false">'
    ]
    for (di, hi), segs in sorted(buckets.items()):
        depth = (di + 0.5) / DEPTH_BINS
        hue_t = (hi + 0.5) / HUE_BINS
        if palette == "light":
            col = mix(LILAC, WHITE, 0.25 + 0.6 * depth)
        else:
            col = mix(mix(VIOLET, BLUE, hue_t), WHITE, 0.30 * depth ** 2)
        dot_r = r_base * (0.28 + 0.95 * depth)
        opacity = round(0.09 + 0.72 * depth, 2)
        parts.append(
            f'<path stroke="{hexc(col)}" stroke-linecap="round" '
            f'stroke-width="{dot_r * 2:.2f}" stroke-opacity="{opacity}" d="'
            + "".join(segs) + '"/>'
        )

    # faint outer haze ring
    haze = []
    for i in range(int(n_points * 0.13)):
        t = i / float(max(1, int(n_points * 0.13)))
        a = t * math.tau * 11.0 + seed_rot
        rad = radius * (1.02 + 0.15 * ((i * 97) % 13) / 13.0)
        hx = cx + math.cos(a) * rad
        hy = cy + math.sin(a) * rad * 0.86
        haze.append(f"M{hx:.1f} {hy:.1f}h.01")
    haze_col = mix(LILAC, WHITE, 0.4) if palette == "light" else mix(VIOLET, BLUE, 0.5)
    parts.append(
        f'<path stroke="{hexc(haze_col)}" stroke-linecap="round" '
        f'stroke-width="{r_base:.2f}" stroke-opacity="0.09" d="' + "".join(haze) + '"/>'
    )
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    jobs = [
        # hero: black banner -> tiny (70% smaller) white / light-purple dots
        ("orb-hero.svg", orb(6200, 1100, swirl=2.7, seed_rot=0.4,
                             palette="light", dot_scale=0.3)),
        ("orb-mid.svg", orb(2800, 1000, swirl=2.1, seed_rot=1.1)),
        ("orb-contact.svg", orb(2400, 820, swirl=1.8, seed_rot=1.5)),
    ]
    for name, svg in jobs:
        open(name, "w").write(svg)
        print(f"wrote {name}  ({len(svg)} bytes)")
