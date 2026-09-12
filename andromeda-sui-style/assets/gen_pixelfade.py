#!/usr/bin/env python3
"""Broken-pixel ombre band that bridges the black hero into the paper section.

A stochastic dot-dither: near the top almost every cell carries a black dot
(reads solid), fading to none at the bottom (reads paper). All dots go in one
round-capped path. preserveAspectRatio="none" so it stretches to the band.
"""
import random

W, H = 1200, 260
COLS, ROWS = 150, 34
BLACK = "#000000"
PAPER = "#f3f1ec"


def build():
    rnd = random.Random(4242)
    cw, ch = W / COLS, H / ROWS
    segs = []
    for r in range(ROWS):
        # probability of a black pixel: ~1 at top row, ~0 near the bottom
        frac = r / (ROWS - 1)
        p = max(0.0, 1.0 - frac ** 1.35) * 0.96
        for c in range(COLS):
            if rnd.random() < p:
                x = round(c * cw + cw / 2 + rnd.uniform(-1, 1), 1)
                y = round(r * ch + ch / 2 + rnd.uniform(-1, 1), 1)
                segs.append(f"M{x} {y}h.01")
    dot = min(cw, ch) * 0.92
    svg = (
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        'preserveAspectRatio="none" aria-hidden="true">'
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
        f'<path stroke="{BLACK}" stroke-linecap="round" stroke-width="{dot:.1f}" '
        'd="' + "".join(segs) + '"/>'
        '</svg>'
    )
    open("pixel-fade.svg", "w").write(svg)
    print(f"wrote pixel-fade.svg  ({len(svg)} bytes, {len(segs)} pixels)")


if __name__ == "__main__":
    build()
