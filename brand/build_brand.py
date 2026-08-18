#!/usr/bin/env python3
"""
BULLPRINT NET — brand asset builder.

    python3 brand/build_brand.py

Takes the delivered vector masters in `brand/src/` and emits shippable ones in
`assets/brand/`, plus every favicon size, by converting live type to outlines.

WHY THE DELIVERED MASTERS CANNOT SHIP AS-IS
-------------------------------------------
Three defects, all in the type, all invisible until the wrong thing renders:

  1. NO `fill` ON ANY `<text>`. SVG's initial fill is black. The three ON-DARK
     masters draw their strokes in #F3F1FA and leave the type unfilled, so the
     "B", the "BN" and the whole ring legend render BLACK ON #07060C — the mark
     is invisible and the file looks empty. This is the one that would have
     shipped silently.
  2. NO `font-family`. BRAND_KIT.md says the masters "use live Inter via
     @import", but there is no @import and no font-family in any of them, so a
     renderer falls back to its default serif. A monogram set in Times is not
     the monogram.
  3. `<textPath>` in the ring badge. BullPrint's own Print Masters sheet already
     bans it — "NO TEXTPATH — RINGS ARE ROTATED GLYPHS" — because librsvg and a
     browser disagree about it, and a seal that rasterises differently in the
     tool that rips it is not a master.

Outlining fixes all three at once and satisfies BRAND_KIT.md's own instruction:
"convert text to outlines before shipping to engravers/print vendors". Doing it
here means the shipped master IS the outlined one, so nobody has to remember.

TYPE ASSIGNMENT — AN INFERRED DECISION, FLAGGED FOR SIGN-OFF
------------------------------------------------------------
The source SVGs name no typeface, so one had to be chosen. Read off
BRAND_KIT.md's own type rules rather than invented:

  - "Inter 500-600 — display + wordmarks"  -> the BN monogram and the B glyph,
    and the BN at the centre of the ring badge.
  - "JetBrains Mono 400-600 — labels ... uppercase, track +0.12-0.32em, never
    bold" -> the ring's arc legend, which is uppercase at 0.35em and 0.53em
    tracking. That is a label, not a wordmark.

This matches the t01 seal on the BullPrint Lab Print Masters sheet, which also
sets its ring legend in JetBrains Mono. If the brand owner wants the arcs in
Inter instead, change RING_ARC_FONT and re-run — nothing else moves.
"""
from __future__ import annotations

import math
import os
import subprocess
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "brand")
FONTS = os.path.join(ROOT, "fonts")

VOID, FG = "#07060C", "#F3F1FA"

RING_ARC_FONT = ("jetbrainsmono-latin.woff2", 500)   # see the note above
DISPLAY_FONT = ("inter-latin-600.woff2", None)       # static 600, no instancing

_cache: dict = {}


def load(spec):
    """A font, instanced to a weight if it is variable."""
    name, wght = spec
    key = (name, wght)
    if key in _cache:
        return _cache[key]
    f = TTFont(os.path.join(FONTS, name))
    if wght is not None and "fvar" in f:
        f = instancer.instantiateVariableFont(f, {"wght": wght})
    _cache[key] = f
    return f


def glyph_paths(font, s: str, size: float, tracking: float = 0.0):
    """(path_d, advance) per character, scaled to `size`, plus the total width.

    Font space is Y-up and SVG is Y-down, so the glyph is emitted through a
    transform that scales and flips in one step. Tracking is added between
    glyphs only — not after the last one — so `text-anchor: middle` centres on
    the ink rather than on a trailing gap.
    """
    upm = font["head"].unitsPerEm
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    k = size / upm
    out, total = [], 0.0
    for i, ch in enumerate(s):
        cp = ord(ch)
        if cp not in cmap:
            raise SystemExit(f"{font['name'].getDebugName(4)} has no glyph for {ch!r}")
        gname = cmap[cp]
        pen = SVGPathPen(gs)
        gs[gname].draw(pen)
        adv = gs[gname].width * k
        out.append((pen.getCommands(), adv, k))
        total += adv
        if i < len(s) - 1:
            total += tracking
    return out, total


def straight_text(s: str, cx: float, baseline: float, size: float,
                  colour: str, spec, tracking: float = 0.0) -> str:
    """Outlined text, centred on cx — the equivalent of text-anchor:middle."""
    font = load(spec)
    glyphs, total = glyph_paths(font, s, size, tracking)
    x = cx - total / 2.0
    parts = []
    for d, adv, k in glyphs:
        if d.strip():
            parts.append(
                f'<path transform="translate({x:.3f} {baseline:.3f}) '
                f'scale({k:.6f} {-k:.6f})" d="{d}"/>')
        x += adv + tracking
    return f'<g fill="{colour}">' + "".join(parts) + "</g>"


def arc_text(s: str, cx: float, cy: float, r: float, size: float, colour: str,
             spec, tracking: float, *, top: bool) -> str:
    """Outlined text on a circular arc — rotated glyphs, never a textPath.

    Reproduces what the source achieved with `<textPath startOffset="50%">` and
    `text-anchor="middle"`: the run is centred on the arc's midpoint, which is
    the top of the circle for the upper legend and the bottom for the lower one.
    Each glyph is rotated about its own centre so its baseline lies along the
    tangent.
    """
    font = load(spec)
    glyphs, total = glyph_paths(font, s, size, tracking)
    # Angle subtended per unit of arc length.
    per = 1.0 / r
    # Midpoint: 270 deg is the top of the circle in SVG's y-down space, 90 the
    # bottom. The upper legend runs with increasing angle, the lower with
    # decreasing, so both read left to right.
    mid = math.radians(270.0 if top else 90.0)
    sign = 1.0 if top else -1.0

    parts = []
    run = 0.0
    for d, adv, k in glyphs:
        centre = run + adv / 2.0 - total / 2.0    # signed distance from midpoint
        th = mid + sign * centre * per
        px = cx + r * math.cos(th)
        py = cy + r * math.sin(th)
        # Tangent, in the direction the text runs.
        tx, ty = -math.sin(th) * sign, math.cos(th) * sign
        deg = math.degrees(math.atan2(ty, tx))
        if d.strip():
            parts.append(
                f'<path transform="translate({px:.3f} {py:.3f}) rotate({deg:.3f}) '
                f'translate({-adv / 2.0:.3f} 0) scale({k:.6f} {-k:.6f})" d="{d}"/>')
        run += adv + tracking
    return f'<g fill="{colour}">' + "".join(parts) + "</g>"


def svg(vb: int, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb} {vb}" '
            f'width="{vb}" height="{vb}">{body}</svg>\n')


# ------------------------------------------------------------------- the marks
def ring_badge(c: str) -> str:
    """Geometry verbatim from the source; only the type is rebuilt."""
    return svg(200,
        f'<circle cx="100" cy="100" r="95" fill="none" stroke="{c}" stroke-width="2.5"/>'
        f'<circle cx="100" cy="100" r="86" fill="none" stroke="{c}" stroke-width="1"/>'
        # r=62 and r=70 are the two arc radii the source drew its textPaths on.
        + arc_text("BULLPRINT", 100, 100, 62, 17, c, RING_ARC_FONT, 6, top=True)
        + arc_text("— NET —", 100, 100, 70, 15, c, RING_ARC_FONT, 8, top=False)
        + straight_text("BN", 100, 112, 38, c, DISPLAY_FONT, -1)
        + f'<g stroke="{c}" stroke-width="1">'
          f'<line x1="58" y1="100" x2="72" y2="100"/>'
          f'<line x1="128" y1="100" x2="142" y2="100"/></g>'
          f'<circle cx="55" cy="100" r="2.4" fill="{c}"/>'
          f'<circle cx="145" cy="100" r="2.4" fill="{c}"/>')


def bn_monogram(c: str) -> str:
    return svg(96,
        straight_text("BN", 48, 62, 40, c, DISPLAY_FONT, -1.5)
        + f'<line x1="48" y1="72" x2="48" y2="80" stroke="{c}" stroke-width="1.2"/>'
          f'<circle cx="48" cy="83" r="2.6" fill="{c}"/>')


def b_glyph(c: str) -> str:
    # The source centres the B on x=44, not 48, to leave room for the node.
    return svg(96,
        straight_text("B", 44, 66, 56, c, DISPLAY_FONT)
        + f'<line x1="62" y1="30" x2="62" y2="44" stroke="{c}" stroke-width="1.6"/>'
          f'<circle cx="62" cy="26" r="3.2" fill="{c}"/>')


MARKS = {
    "ring-badge-on-dark":   ring_badge(FG),
    "ring-badge-on-light":  ring_badge(VOID),
    "bn-monogram-on-dark":  bn_monogram(FG),
    "bn-monogram-on-light": bn_monogram(VOID),
    "b-glyph-on-dark":      b_glyph(FG),
    # Not in the delivered kit. Derived because a favicon has to survive a light
    # browser chrome, and the B glyph is what BRAND_KIT.md assigns to favicons.
    "b-glyph-on-light":     b_glyph(VOID),
}

# Favicon raster sizes. BRAND_KIT.md: "Favicon .ico + apple-touch-icon derived
# from B glyph."
RASTER = [("favicon-16.png", 16), ("favicon-32.png", 32), ("favicon-48.png", 48),
          ("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    print("BULLPRINT NET — brand assets")

    for name, doc in MARKS.items():
        # The defect that would have shipped: type with no fill is black type.
        assert "<text" not in doc, f"{name}: live text survived outlining"
        assert "textPath" not in doc, f"{name}: textPath survived"
        assert "font-family" not in doc, f"{name}: still depends on a font"
        if name.endswith("on-dark"):
            assert VOID not in doc, f"{name}: carries the dark colour"
            assert FG in doc, f"{name}: nothing is drawn in the light colour"
        p = os.path.join(OUT, name + ".svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"  {name + '.svg':28s} {len(doc):6d} B")

    # The favicon is the B glyph on dark, on its own #07060C tile — a favicon is
    # composited over browser chrome we do not control, so it carries its own
    # ground rather than relying on transparency.
    tile = svg(96, f'<rect width="96" height="96" fill="{VOID}"/>'
                   + b_glyph(FG).split(">", 1)[1].rsplit("</svg>", 1)[0])
    tile_p = os.path.join(OUT, "favicon-tile.svg")
    with open(tile_p, "w", encoding="utf-8") as f:
        f.write(tile)

    if not shutil_which("rsvg-convert"):
        print("  rsvg-convert not found — SVGs written, rasters skipped")
        return

    for fn, px in RASTER:
        dest = os.path.join(ROOT, "assets", fn)
        subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px),
                        "-o", dest, tile_p], check=True)
        print(f"  {fn:28s} {px}x{px}  {os.path.getsize(dest):6d} B")

    # A real .ico, for the browsers and crawlers that still ask for /favicon.ico.
    try:
        from PIL import Image
        imgs = [Image.open(os.path.join(ROOT, "assets", f"favicon-{s}.png")).convert("RGBA")
                for s in (16, 32, 48)]
        imgs[0].save(os.path.join(ROOT, "favicon.ico"), format="ICO",
                     sizes=[(16, 16), (32, 32), (48, 48)],
                     append_images=imgs[1:])
        print(f"  {'favicon.ico':28s} 16/32/48  "
              f"{os.path.getsize(os.path.join(ROOT, 'favicon.ico')):6d} B")
    except Exception as e:                                   # pragma: no cover
        print(f"  favicon.ico SKIPPED — {type(e).__name__}: {e}")


def shutil_which(x):
    from shutil import which
    return which(x)


if __name__ == "__main__":
    sys.exit(main())
