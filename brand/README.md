# Brand assets

`brand/src/` holds the delivered vector masters, untouched. `assets/brand/`
holds the shippable ones, built from them by `build_brand.py`:

```
python3 brand/build_brand.py
```

Nothing in `assets/brand/` is hand-edited. Change the builder and re-run.

## The delivered masters could not ship as-is

Three defects, all in the type, all invisible until the wrong thing renders.

**1 · No `fill` on any `<text>`.** SVG's initial fill is black. The three
on-dark masters draw their strokes in `#F3F1FA` and leave the type unfilled, so
the "B", the "BN" and the entire ring legend rendered **black on `#07060C`** —
the mark was invisible and the file looked empty. This is the one that would
have shipped silently, because a transparent-looking SVG reads as "still
loading" rather than as broken.

**2 · No `font-family`.** `BRAND_KIT.md` says the masters "use live Inter via
@import", but there is no `@import` and no `font-family` in any of the five
files. A renderer falls back to its default serif, and a monogram set in Times
is not the monogram.

**3 · `<textPath>` in the ring badge.** BullPrint's own Print Masters sheet
already bans it — *"NO TEXTPATH — RINGS ARE ROTATED GLYPHS"* — because librsvg
and a browser disagree about it. A seal that rasterises differently in the tool
that rips it is not a master.

## Outlining fixes all three, and closes the print note

`BRAND_KIT.md` says to *"convert text to outlines before shipping to engravers
/ print vendors"*. Doing that at build time means **the shipped master is
already the outlined one**, so nobody has to remember to do it, and the same
file is correct for the web, the laser and a print vendor. There is no live
type and no font dependency left anywhere in `assets/brand/`.

The ring legend is set as individually rotated glyphs on the arc — the method
the Print Masters sheet mandates — rather than as a `textPath`. Geometry
(circles, nodes, radii, stroke weights) is carried across verbatim; only the
type was rebuilt.

## One inferred decision that needs sign-off

The source SVGs name no typeface, so one had to be chosen. Both readings come
from `BRAND_KIT.md`'s own type rules rather than from preference:

| element | typeface | the rule it follows |
|---|---|---|
| BN monogram, B glyph, ring centre "BN" | **Inter 600** | *"Inter 500–600 — display + wordmarks"* |
| ring arc legend "BULLPRINT" / "— NET —" | **JetBrains Mono 500** | *"JetBrains Mono 400–600 — labels … uppercase, track +0.12–0.32em"* — the legend is uppercase at 0.35em and 0.53em tracking, which is a label, not a wordmark |

This also matches the t01 seal on the BullPrint Lab Print Masters sheet, which
sets its ring legend in JetBrains Mono. **If the brand owner wants the arcs in
Inter, change `RING_ARC_FONT` and re-run — nothing else moves.**

## How the marks are applied, and two corrections

`BRAND_KIT.md` assigns each mark a role and a size floor. Two placements in the
page as first shipped broke those rules:

| surface | size | was | now | why |
|---|---|---|---|---|
| nav | 30px | circuit-bull badge | **BN monogram** | the badge has a **48px minimum**; the monogram's range is 24–48px |
| footer | 36px | circuit-bull badge | **BN monogram** | same rule |
| hero | ≤430px | circuit-bull badge | unchanged | primary identity, dark ground, above the floor |
| favicon | 16–48px | 400px JPEG | **B glyph** | *"B glyph — ≤32px, favicons 16/32"* |

The favicon is the B glyph on its own `#07060C` tile rather than on
transparency: a favicon is composited over browser chrome nobody controls, so
it carries its own ground.

`favicon.ico` is a real multi-size icon (16/32/48) for the clients and crawlers
that still request `/favicon.ico` at the root regardless of what the document
declares.

## Still open

- **A ≥1500px badge master is the merch blocker**, and remains unresolved. The
  circuit-bull badge in this repo is a **400px raster**, which the hero renders
  at up to 430 CSS px — short at 1× and roughly 2.7× short on a retina display.
  `BRAND_KIT.md` marks it too: *"⚠ Request ≥1200px master before any print /
  merch use."* Nothing here fixes that; only a new master from the client does.
- **`og-banner.png` is 1804×950**, not the 1200×630 `BRAND_KIT.md` claims. Both
  are ~1.9:1 so it serves correctly as an `og:image` and the higher resolution
  is an improvement — but the kit's own figure is wrong, and someone will
  eventually build to it.
- **The X handle is unverified** — `x.com/bullprintnet`.
- **`bullnet.ai` is linked three times and has no page.** `BRAND_KIT.md`
  confirms it: *"bullnet.ai landing page (not yet designed)"*, and that the
  sub-brand has no separate mark and is always subordinate.
