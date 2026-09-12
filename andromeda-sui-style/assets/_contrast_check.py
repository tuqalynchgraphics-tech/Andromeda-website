#!/usr/bin/env python3
"""WCAG contrast audit for the Sui-styled Andromeda palette."""


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def L(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    la, lb = L(a), L(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


P = dict(
    paper="#f3f1ec", panel="#e8e3da", ink="#0b0a12", inkcard="#15131f",
    text_ink="#16121f", text_body="#2b2740", text_muted="#565064",
    on_dark="#edeaf4", on_dark_muted="#b4abd0",
    violet="#6e3ae6", violet_strong="#5a2cc0", violet_on_dark="#c9b8ff",
    focus="#8a5cff", field_bg="#1c1733", field_border="#5a4a92", ph="#a79dce",
)


def hx(k):
    return P.get(k, k)


CHECKS = [
    ("body on paper", "text_body", "paper", 4.5),
    ("body on panel", "text_body", "panel", 4.5),
    ("muted on paper", "text_muted", "paper", 4.5),
    ("muted on panel", "text_muted", "panel", 4.5),
    ("heading ink on paper", "text_ink", "paper", 3.0),
    ("kicker violet_strong on paper", "violet_strong", "paper", 4.5),
    ("kicker box: violet_strong on #ede6fb", "violet_strong", "#ede6fb", 4.5),
    ("link/panel-num violet_strong on panel", "violet_strong", "panel", 4.5),
    ("white on violet btn square", "#ffffff", "violet", 4.5),
    ("white on violet_strong (hover)", "#ffffff", "violet_strong", 4.5),
    ("-- dark --", "on_dark", "ink", 4.5),
    ("on_dark_muted on ink", "on_dark_muted", "ink", 4.5),
    ("on_dark on inkcard", "on_dark", "inkcard", 4.5),
    ("on_dark_muted on inkcard", "on_dark_muted", "inkcard", 4.5),
    ("violet_on_dark (kicker/num/ticks) on ink", "violet_on_dark", "ink", 4.5),
    ("violet_on_dark on inkcard", "violet_on_dark", "inkcard", 4.5),
    ("kicker--light box violet_on_dark on ~#1b1733", "violet_on_dark", "#1b1733", 4.5),
    ("stack idx on_dark_muted on inkcard", "on_dark_muted", "inkcard", 4.5),
    ("btn-line label on_dark on ink", "on_dark", "ink", 4.5),
    ("interstitial label #fff on rgba(11,10,18,.55) over bars ~#241a55", "#ffffff", "#191436", 4.5),
    ("form input #fff on field_bg", "#ffffff", "field_bg", 4.5),
    ("placeholder on field_bg", "ph", "field_bg", 4.5),
    ("field border on ink (3:1)", "field_border", "ink", 3.0),
    ("field border on ink vs inkcard section? contact bg=ink", "field_border", "ink", 3.0),
    ("focus ring on paper (3:1)", "focus", "paper", 3.0),
    ("focus ring on ink (3:1)", "focus", "ink", 3.0),
    ("footer legal on ink", "on_dark_muted", "ink", 4.5),
    ("marquee text on_dark_muted on ink", "on_dark_muted", "ink", 4.5),
    ("promo #fff on violet", "#ffffff", "violet", 4.5),
]

print(f"{'check':58} {'ratio':>7} {'min':>4}  result")
print("-" * 84)
fails = 0
for label, fg, bg, mn in CHECKS:
    if "--" in label and fg == "on_dark":
        print(f"\n{label}")
    r = ratio(hx(fg), hx(bg))
    ok = r >= mn
    fails += (not ok)
    print(f"{label:58} {r:7.2f} {mn:4.1f}  {'PASS' if ok else 'XX FAIL'}")
print("-" * 84)
print("FAILURES:", fails)
