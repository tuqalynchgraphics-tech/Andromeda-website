# Andromeda — homepage, sui.io design language

Same **content** and **brand tokens** (Cabinet Grotesk + Erode, cosmic-violet
palette) as `../andromeda-rebrand/`, restyled in the visual + interaction
language of <https://www.sui.io>. The original v1 is untouched.

## Run

```bash
cd andromeda-sui-style
python3 -m http.server 4174
# http://localhost:4174
```

No build step. One external dependency: the Fontshare CDN for the two brand
typefaces. System fallbacks are declared.

## Files

| Path | Purpose |
|---|---|
| `index.html` | Markup — semantic landmarks, one `<h1>`, `<h2>` section openers, inline SVG sprite (icons + isometric line-art). |
| `assets/styles.css` | All styling. Tokens at the top. |
| `assets/main.js` | Progressive enhancement: promo dismiss, header scroll state, full-screen overlay nav (focus-contained, Esc, `inert`), the expertise accordion, scroll reveal, client-side form feedback. Page is fully usable without JS (footer nav is the no-JS fallback for the menu; the first accordion item is open by default). |
| `assets/orb-hero.svg`, `assets/orb-mid.svg`, `assets/orb-contact.svg` | Generated halftone particle-sphere backgrounds (v1's "old" orb, denser point counts: 2400 / 1900 / 1500). |
| `assets/gen_orb.py` | Regenerates them. |
| `assets/_contrast_check.py` | WCAG audit of the palette. |
| `assets/favicon.svg` | Brand mark (copied from v1). |

## Revision (round 2)

- **Side margins reduced** to ~30 px (`--gutter: clamp(20px, 4vw, 30px)`); content column widened to 1680 px so bands sit close to the viewport edge.
- **Moving background** swapped from the warp-streak field back to v1's halftone particle sphere, with the point count roughly doubled — on the hero, the "Solutions as unique as your business" interstitial, and the contact band. Slow rotation, disabled under `prefers-reduced-motion`.
- **Corners sharpened** a few px across the board (`--r` 14 → 10; button squares 6 → 3; inputs, toggles, chips, menu buttons pulled in to match).
- **Eyebrow boxes removed.** The kicker labels ("Bespoke AI automation", "01 / The bespoke difference", …) and the interstitial label lost their tinted background pills — now plain uppercase micro-labels with a small solid square marker (devolfs style).
- **"Why cookie-cutter solutions don't work"** rebuilt to match the *OUR EXPERTISE* section on <https://www.devolfs.com>: unboxed eyebrow → two-line heading with a line-mask reveal → a short bold-left rule that draws in on scroll → a numbered accordion (`/ 01`–`/ 04`, big titles, +/− toggles, hairline dividers, per-item description + tag chips). Single-open, first item open by default, rows stagger in on scroll. Keyboard operable (`<button aria-expanded aria-controls>`), collapses to first item with no JS.

## What was taken from sui.io

Analysed the homepage plus `/about`. Adapted patterns:

- **Hero** — full-bleed near-black, oversized **weight-500** headline with tight
  negative tracking (`-0.038em`) and `line-height: 1`, a radiating **warp/streak**
  background (sui.io's hyperspace hero; doubles as a galaxy for Andromeda), one
  short sub-line, twin CTAs.
- **Kicker tags** — small uppercase label in a faint tinted highlight box
  (sui.io's monospace `[ tag ]` treatment, rendered here in Cabinet Grotesk to
  keep the two-font brand rule).
- **Numbered principle panels** — light rounded panels, number in a bordered
  square, title, full-width **dashed divider**, large gap, muted description
  (sui.io `/about` values list) → "Our approach", the 4-phase process, the 4
  commitments. Dark variant for the dark bands.
- **Dark stack cards** with a mono index and **isometric wireframe line-art**
  (sui.io's protocol-stack cards) → "What we build".
- **Corner-bracket (⌐) bullet lists** → the technology categories, the about
  facts panel, the footer link columns.
- **Square arrow-button + label** as the primary CTA unit.
- **Tech-name marquee**, full-bleed **spectrum interstitial** band, **giant
  grainy wordmark** cropped at the footer edge, **hamburger → full-screen
  overlay nav** at every breakpoint, always-dark sticky header, top promo
  marquee bar.
- **Alternating near-black / warm-paper bands** with big vertical rhythm.

Not taken: sui.io's blue (kept Andromeda violet as the single accent),
scroll-pinned/scrolljacked sections (kept native scrolling for accessibility),
partner-logo wall, TVL-style metrics (Andromeda's copy has none — none were
invented).

## Guardrails (typeui-fundamentals)

One `<h1>`; `<h2>` opens every section at `line-height: 1` + 32px; 4-pt spacing
scale; 1200px content column; WCAG AA contrast (audit: 0 failures; see
`_contrast_check.py`); skip link; visible `:focus-visible` rings; overlay nav is
`inert` + focus-contained when closed/open; `prefers-reduced-motion` disables the
warp drift, marquees, interstitial pan and all reveal animation; `rem`-based
type; no horizontal scroll at 320 px.

### Documented deviations

- **Repeating-component titles are `<h3>`** (panels, stack cards) rather than
  `<h4>+`, to avoid skipping a heading level under the section `<h2>` — a WCAG
  1.3.1 / 2.4.10 issue, and accessibility outranks the anti-inflation guideline.
  They're sized by role, not tag.
- **Hamburger nav at all widths.** typeui prefers visible primary nav on
  desktop; this is a deliberate match to sui.io. Mitigations: the footer carries
  the full section list (works with no JS), the overlay is keyboard-operable
  (Esc, focus trap, `inert`), and the sticky header keeps a "Book a call" CTA
  visible ≥ 560 px.

## Not included

Static homepage only. The contact form validates and confirms locally but is not
wired to a backend.
