# BullPrint Net — bullprintnet.com

Single-page landing for BullPrint Net. Static, no build step, no framework, no
third-party requests. Deploys to Cloudflare Pages straight from the repo root.

```
.
├── index.html      the page
├── styles.css      every style (no inline <style>, anywhere)
├── reveal.js       the only client JS — ~20 lines, no dependencies
├── fonts/          Inter + JetBrains Mono, self-hosted, woff2
├── assets/         logo, OG banner, favicons
│   └── brand/      outlined vector marks — built, never hand-edited
├── brand/          the brand kit, its source masters, and build_brand.py
├── favicon.ico     real multi-size icon (16/32/48)
├── site.webmanifest
├── _headers        security + cache headers for Cloudflare Pages
├── robots.txt
└── sitemap.xml
```

## Cloudflare Pages settings

| | |
|---|---|
| build command | *(none)* |
| build output directory | `/` |
| framework preset | None |
| production branch | `main` |

Then add `bullprintnet.com` as a custom domain.

## Built from

`design_handoff_bullprint_net/` — `BullPrint Net Landing.dc.html` plus its
README. The handoff is explicit that the `.dc.html` is **a design reference, not
production code**: *"Recreate it in the target codebase's environment… this page
needs no framework — plain semantic HTML + one CSS file + ~20 lines of vanilla
JS (IntersectionObserver) is the correct implementation."* That is what this is.

Every string on the page was diffed against the design file, and all of it
carried over — including details the token list does not mention:

- **Both display headings are literal capitals** (`BUILD ON BULLPRINT NET`,
  `WHAT ARE YOU BUILDING?`), not sentence case uppercased by CSS. Both carry
  `text-wrap: balance`.
- **Every H2 has a non-breaking space before its last word** — an orphan guard,
  applied deliberately six times in the design. Carried across each one.
- The sovereignty heading runs at `line-height: 1.08`, not the 1.05 the other
  H2s use, because it is three sentences long.
- The tagline separators are double non-breaking spaces either side of each
  bullet, in both the hero kicker and the footer.

All copy is final and was not rewritten. Two content constraints from the
handoff hold and must keep holding: **no invented GPU models, specs, benchmarks,
pricing or availability**, and **no absolute security or privacy guarantees**.

## Why the fonts are self-hosted

The handoff offers a choice — preconnect to Google Fonts, or self-host. Self-hosted
is the only one consistent with the page: its own copy sells *reduced dependency
on centralized cloud* and *customer-controlled data*, and a Google Fonts request
would be the single third-party call on the document.

Self-hosting is also what lets `_headers` set a CSP with **no external origins and
no `unsafe-inline`** — `default-src 'self'` with nothing added. That header only
stays true while there is no inline `<style>`, no inline `<script>` and no
external link. If any of those get added, change the header deliberately rather
than discovering it in a console.

Inter is @fontsource (SIL OFL 1.1), latin + latin-ext at 400/500/600/700.
JetBrains Mono is the same OFL files already serving bullprintlab.com.

## Open before ship

1. **The logo is 400×400 and the hero renders it at up to 430 CSS px.** It is
   already under-resolution at 1× and roughly 2.7× short on a retina display.
   The handoff flags this too: *"Ask client for a ≥1200px master before ship."*
   The same master should then produce a real favicon and a 1200×630 OG image —
   right now both reuse the 400px JPEG, which is a placeholder, not a finish.
2. **The X handle href is a placeholder** — `https://x.com/bullprintnet`.
   Confirm the account exists before launch or drop the link.
3. **`bullnet.ai` is linked three times and has no page yet** (COMPUTE column,
   Edge CTA, footer). Those are outbound links to a domain that must resolve.
4. **A ≥1500px badge master is the merch blocker.** The circuit-bull badge is a
   400px raster rendered at up to 430 CSS px in the hero — short at 1×, ~2.7×
   short on retina. `BRAND_KIT.md` flags it too. The favicon and OG image no
   longer depend on it, so this now blocks merch and print only, not the site.

See `brand/README.md` for what was wrong with the delivered SVG masters, how
they were fixed, and the one type decision that needs brand-owner sign-off.
