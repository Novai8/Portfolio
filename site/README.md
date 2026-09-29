# 5Star Auto — Cinematic Hero Demo

An independent **demo/concept website** for 5Star Auto (North Austin, TX), built around a
cinematic, layered, interactive automotive hero. No build step, no dependencies —
plain HTML, CSS and ~250 lines of vanilla JS.

## Run

```bash
node server.js 3000      # from the repository root
# → http://localhost:3000
```

Any static host works too (`/estimate/` and `/services/` are real directories with
`index.html`, so clean URLs resolve everywhere).

## Files

```
site/
  index.html           homepage (hero + 01 Why + 02 Services)
  estimate/index.html  /estimate  — primary CTA target
  services/index.html  /services  — secondary CTA target
  styles/base.css      tokens, theme, header/footer, shared buttons
  styles/hero.css      the cinematic hero (all 10 layers)
  styles/home.css      homepage + inner page sections
  scripts/hero.js      entrance stages, pointer parallax, cursor light,
                       hotspots, scroll choreography, theme, reveals
  assets/              background plates + isolated vehicle cut-outs (dark + light)
```

## Hero layer stack

| z | Layer | Notes |
|---|---|---|
| 1 | Background plate | blurred, darkened workshop; slow scroll + pointer drift |
| 2 | Cinematic scrim | directional gradient + vignette for text contrast |
| 3 | Film grain | canvas-generated, inlined as a data URI (no extra request) |
| 4 | Atmosphere | soft red glow, cool workshop glow, two light streaks |
| 5 | Technical overlay | coordinate grid, alignment markers, measurement ticks, labels |
| 6 | Vehicle | isolated PNG, ±7px translate / ±1.6° rotate, contact shadow |
| 7 | Hotspots | alignment · diagnostics · body panel (hover on desktop, tap on touch) |
| 8 | Cursor spotlight | 210px interpolated radial light, `screen` (dark) / `multiply` (light) |
| 9 | Hero → section fade | gradient seam into `01 / WHY 5 STAR AUTO` |
| 10 | Typography + chrome | headline, CTAs, metadata strip, scroll indicator |

All movement is driven by four CSS custom properties (`--px`, `--py`, `--mx`, `--my`)
plus a scroll progress value (`--sp`), interpolated in a single rAF loop that parks
itself as soon as everything settles. Only `transform`, `opacity` and `filter`
animate — no layout shift.

## Graceful degradation

* **No JS** → `html.no-js` rules show the full composition, static and readable.
* **Vehicle asset fails** → `no-vehicle` class drops the stage and sharpens the plate.
* **`prefers-reduced-motion: reduce`** → no cursor, no parallax, no stagger, no scroll motion.
* **Coarse pointer / narrow viewport / ≤2 cores or ≤2 GB RAM** → pointer effects never initialise.
* **Mobile** → restructured stack: label → headline → copy → estimate → call → vehicle → cue.

## Content accuracy

Only verifiable business facts are shown: North Austin location (904 Prairie Trl,
Austin, TX 78758), phone (512) 821-1360, family owned, established 2009, Mon–Fri
9:00–5:00, free estimates, alignments from $60. The status chip reads
`● SERVICE EXPERIENCE` — decorative only. **No fake live business data** (no
"3 vehicles in the bay", no invented availability). The estimate form is clearly
labelled as not connected to a backend.
