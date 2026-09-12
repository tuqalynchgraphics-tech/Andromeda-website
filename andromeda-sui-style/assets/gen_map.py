#!/usr/bin/env python3
"""Animated dotted world-map for the About section.

Concept match for the graphic in andromeda.chat's "Global expertise" block:
a flat (equirectangular) world stippled in brand-violet dots, gradient arcs
between hubs, and a subset of points doing a 2s radar "ping" on a loop.

The continents here are traced from coarse real coastlines (lon/lat waypoints
projected equirectangular) rather than blobs, then flood-filled with a fine
dot grid. Motion is CSS keyframes so `prefers-reduced-motion` is honoured.
"""
import math

W, H = 900, 440
VIOLET = "#6e3ae6"
VIOLET_LT = "#c9b8ff"
DARK = "#211c30"        # land dots — dark, on the plain white section


def eq(lon, lat):
    """lon/lat -> equirectangular pixel in the WxH field."""
    return ((lon + 180.0) / 360.0 * W, (90.0 - lat) / 180.0 * H)


# --- coarse continent coastlines (lon, lat) --------------------------------
LANDS_LL = {
    "n_america": [
        (-168, 65), (-158, 71), (-140, 70), (-120, 71), (-95, 72), (-80, 73),
        (-64, 60), (-56, 51), (-52, 47), (-60, 45), (-70, 43), (-76, 35),
        (-81, 31), (-81, 25), (-90, 29), (-97, 25), (-105, 22), (-107, 24),
        (-101, 18), (-95, 16), (-92, 15), (-96, 24), (-104, 30), (-114, 32),
        (-120, 34), (-124, 40), (-125, 48), (-130, 54), (-140, 59), (-152, 59),
        (-165, 60),
    ],
    "greenland": [
        (-52, 60), (-30, 60), (-18, 70), (-22, 80), (-40, 83), (-58, 80),
        (-60, 70), (-55, 62),
    ],
    "s_america": [
        (-80, 9), (-70, 11), (-60, 10), (-52, 5), (-50, -1), (-47, -7),
        (-40, -9), (-37, -13), (-38, -22), (-44, -23), (-48, -25), (-53, -35),
        (-58, -42), (-66, -47), (-71, -52), (-74, -50), (-73, -40), (-71, -28),
        (-72, -18), (-78, -10), (-81, -3), (-81, 4),
    ],
    "africa": [
        (-16, 16), (-8, 21), (0, 30), (10, 37), (20, 33), (28, 32), (33, 30),
        (35, 22), (37, 12), (43, 11), (51, 12), (48, 3), (41, -3), (40, -12),
        (35, -22), (28, -32), (22, -34), (18, -35), (14, -28), (12, -18),
        (9, -6), (3, 4), (-6, 5), (-13, 10),
    ],
    "madagascar": [
        (43, -13), (48, -16), (50, -23), (47, -25), (44, -22), (42, -16),
    ],
    "europe": [
        (-9, 37), (-9, 43), (-2, 44), (2, 48), (-3, 49), (2, 51), (5, 54),
        (8, 58), (11, 63), (18, 69), (28, 71), (32, 66), (30, 58), (40, 56),
        (42, 47), (37, 42), (28, 41), (24, 38), (18, 40), (10, 44), (3, 43),
        (-4, 37),
    ],
    "britain": [
        (-8, 51), (-2, 50), (0, 53), (-1, 58), (-6, 58), (-9, 55),
    ],
    "asia": [
        (28, 66), (40, 68), (55, 68), (70, 73), (90, 75), (110, 74), (130, 72),
        (145, 62), (160, 61), (170, 66), (163, 55), (150, 46), (142, 45),
        (140, 35), (135, 24), (128, 16), (120, 9), (110, 10), (105, 14),
        (100, 8), (98, 12), (93, 15), (90, 22), (86, 21), (82, 8), (78, 8),
        (76, 16), (72, 22), (67, 25), (60, 25), (54, 27), (50, 32), (46, 34),
        (44, 42), (38, 46), (33, 52), (30, 58),
    ],
    "india": [
        (68, 24), (73, 25), (80, 16), (82, 8), (79, 9), (77, 8), (76, 15),
        (72, 20), (69, 21),
    ],
    "japan": [
        (130, 31), (138, 35), (143, 44), (140, 46), (133, 40), (129, 33),
    ],
    "indonesia_1": [(95, 5), (104, 3), (107, -3), (100, -5), (95, -1)],
    "indonesia_2": [(108, -1), (119, -4), (121, -8), (112, -9), (107, -4)],
    "indonesia_3": [(120, 0), (133, -2), (137, -8), (124, -9), (120, -4)],
    "new_guinea": [(131, -1), (145, -3), (151, -9), (140, -11), (132, -6)],
    "australia": [
        (114, -22), (122, -17), (131, -12), (138, -12), (145, -15), (150, -24),
        (153, -31), (148, -39), (140, -38), (131, -32), (123, -34), (115, -34),
        (113, -28),
    ],
    "new_zealand": [
        (166, -40), (173, -38), (176, -43), (173, -47), (167, -46), (165, -42),
    ],
    "cuba": [(-84, 22), (-74, 21), (-74, 23), (-84, 23)],
    "hispaniola": [(-73, 18), (-68, 18), (-68, 20), (-73, 20)],
    "iceland": [(-24, 64), (-14, 64), (-14, 67), (-24, 67)],
}

LANDS = {k: [eq(lon, lat) for lon, lat in pts] for k, pts in LANDS_LL.items()}


def in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def on_land(x, y):
    for poly in LANDS.values():
        if in_poly(x, y, poly):
            return True
    return False


# dot lattice — every dot sits exactly on (X0 + i*STEP, Y0 + j*STEP)
STEP = 5.0
X0, Y0 = 11.0, 15.0


def snap(px, py):
    return (round(round((px - X0) / STEP) * STEP + X0, 1),
            round(round((py - Y0) / STEP) * STEP + Y0, 1))


HUBS_LL = [
    ("New York", -74.0, 40.7), ("Los Angeles", -118.2, 34.0),
    ("Sao Paulo", -46.6, -23.5), ("London", -0.1, 51.5),
    ("Gibraltar", -5.35, 36.1), ("Frankfurt", 8.7, 50.1),
    ("Lagos", 3.4, 6.5), ("Dubai", 55.3, 25.2), ("Mumbai", 72.9, 19.1),
    ("Singapore", 103.8, 1.35), ("Tokyo", 139.7, 35.7), ("Sydney", 151.2, -33.9),
]
HUBS = [snap(*eq(lon, lat)) for _, lon, lat in HUBS_LL]
ARCS = [(3, 4), (4, 0), (0, 2), (4, 6), (6, 7), (7, 8), (8, 9),
        (9, 11), (7, 10), (3, 5), (0, 1), (9, 10)]


def build():
    import random
    rnd = random.Random(20260907)

    # strict lattice — no jitter, so every dot aligns both axes
    dots = []
    ny = int((H - 6 - Y0) // STEP) + 1
    nx = int((W - 4 - X0) // STEP) + 1
    for j in range(ny):
        y = round(Y0 + j * STEP, 1)
        for i in range(nx):
            x = round(X0 + i * STEP, 1)
            if on_land(x, y):
                dots.append((x, y))

    rnd.shuffle(dots)
    ping_idx = set(range(min(46, len(dots))))

    # trim the empty margins top/bottom so the map sits tight (no gap band)
    ys = [y for _, y in dots]
    vb_top = max(0.0, min(ys) - 8)
    vb_h = (max(ys) + 8) - vb_top

    p = []
    p.append(
        f'<svg viewBox="0 {vb_top:.0f} {W} {vb_h:.0f}" xmlns="http://www.w3.org/2000/svg" '
        'fill="none" role="img" preserveAspectRatio="xMidYMid meet" '
        'aria-label="Stylised world map of dots with pulsing points marking '
        'where Andromeda works, linked by arcs">'
    )
    p.append(
        '<defs><linearGradient id="am-arc" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{VIOLET}" stop-opacity="0.7"/>'
        f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>'
        '</linearGradient></defs>'
    )
    p.append(
        '<style>'
        '.am-ping{transform-box:fill-box;transform-origin:center;'
        'animation:am-ping 2s ease-out infinite}'
        '@keyframes am-ping{0%{transform:scale(1);opacity:.75}'
        '70%,100%{transform:scale(5);opacity:0}}'
        '.am-arc{stroke-dasharray:3 7;animation:am-flow 3s linear infinite}'
        '@keyframes am-flow{to{stroke-dashoffset:-40}}'
        '@media (prefers-reduced-motion:reduce){'
        '.am-ping{animation:none;opacity:0}.am-arc{animation:none}}'
        '</style>'
    )

    p.append('<g stroke="url(#am-arc)" stroke-width="1" stroke-linecap="round">')
    for a, b in ARCS:
        x1, y1 = HUBS[a]
        x2, y2 = HUBS[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * 0.26 - 22
        p.append(f'<path class="am-arc" d="M{x1:.0f} {y1:.0f} Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}"/>')
    p.append('</g>')

    # all base dots as one path (round-capped zero-length segments) — keeps the
    # file small even at a few thousand points
    p.append(
        f'<path fill="none" stroke="{DARK}" stroke-linecap="round" '
        'stroke-width="1.7" stroke-opacity="0.55" d="'
    )
    p.append("".join(f"M{x} {y}h.01" for x, y in dots))
    p.append('"/>')

    p.append(f'<g fill="{VIOLET}">')
    for i in ping_idx:
        x, y = dots[i]
        delay = round(-(i * 0.173) % 2.0, 2)
        p.append(f'<circle class="am-ping" cx="{x}" cy="{y}" r="1.2" style="animation-delay:{delay}s"/>')
        p.append(f'<circle cx="{x}" cy="{y}" r="1" opacity="0.95"/>')
    for j, (x, y) in enumerate(HUBS):
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.1"/>')
        p.append(f'<circle class="am-ping" cx="{x:.1f}" cy="{y:.1f}" r="2.4" style="animation-delay:{round(-(j*0.27)%2.0,2)}s"/>')
    p.append('</g>')

    p.append('</svg>')
    svg = "".join(p)
    with open("about-map.svg", "w") as f:
        f.write(svg)
    print(f"wrote about-map.svg  ({len(svg)} bytes, {len(dots)} dots, "
          f"{len(ping_idx)} pinging, {len(ARCS)} arcs)")


if __name__ == "__main__":
    build()
