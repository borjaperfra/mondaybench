# MondayBench v1.1 — product / UX audit

**Date:** 2026-09-03 · **Audit only. Nothing was changed.** No code, data, score,
benchmark artifact, cost/efficiency figure or methodology was modified, no commit
was made, and no model or judge was called.

Target: `http://localhost:4321/mondaybench`, which redirects to
`/es/mondaybench` — **Spanish is the default locale**, so the Spanish page is the
one a first-time visitor actually meets. Both languages were audited.

## Files

| File | |
|---|---|
| `ux-audit.md` | first-impression passes, section-by-section findings, the 30-second and decision tests |
| `copy-audit.md` | EN + ES copy, terminology collisions, jargon |
| `mobile-audit.md` | 390 px render, measured |
| `performance-audit.md` | measured weight and structure, with dev-server caveats |
| `recommendations.md` | **P0 / P1 / P2 / DO NOT DO**, prioritised |
| `screenshots/` | 10 captures |

## Method, and its limits

Findings come from the live rendered page: screenshots, the accessibility tree,
and DOM/CSS measurement. Where a claim is measurable it was measured rather than
eyeballed — frontier rings, font sizes, overflow widths and page weight are all
read off the real DOM, and the numbers appear in the findings.

Three limits worth stating plainly:

1. **`resize_window` does not work in this environment.** It reports success and
   the window stays at 2560 px (verified three times via `window.innerWidth`).
   The desktop pass is therefore at **2560 px**, not the 1440 px requested. The
   layout is a centred fixed-width column, so the section-level findings hold at
   1440, but **anything about whitespace at 1440 specifically is unverified**.
2. **Mobile was audited by rendering the real page in a 390 px same-origin
   iframe.** Media queries evaluate against the iframe viewport, so this is a
   real 390 px render, not a simulation — but it is not a real device, so touch
   targets and scroll feel are unverified.
3. **Performance numbers come from the dev server**, which this project's own
   notes record as degraded. Only structural findings are reported; timings are
   marked as indicative.

## Headline

The page is **rigorous and unusually well-written**, and its best sections
(the top-band cards, the five-Monday cards, the concision bars) are genuinely
good. The problems are not quality problems — they are **ordering and labelling**
problems. The page explains itself correctly, but mostly *after* the reader has
already formed the wrong impression.

Three findings are hard blockers, and two of them are rigor issues rather than
comprehension issues:

* a provisional model sits at rank **01** in the main leaderboard with every
  other model's delta measured against it;
* the cost scatter draws a **frontier ring on GLM 5.3's $99.20 point**, which is
  the point that is *dominated*, and leaves the $5.67 point unlabelled;
* the phrase **"highest measured score"** names two different models with two
  different numbers, in both languages.

**Verdict: ONE UX PASS NEEDED.** No section needs rebuilding.
