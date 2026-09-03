# Performance audit — lightweight

Audit only. Nothing changed. No optimisation proposed that the evidence does not
support.

## Caveat, stated first

**All timings come from the Astro dev server**, which this project's own notes
record as degraded (missing `better-sqlite3` binding, intermittent miniflare
500s, stale scoped CSS, no prefetch script in dev). Dev also serves unbundled ES
modules. **Timings below are indicative only**; structural measurements (payload
size, DOM size, dependencies) are reliable.

## Measured

| | |
|---:|---|
| HTML, uncompressed | 333,291 bytes (**325 KB**) |
| HTML, gzipped | **57,829 bytes (56 KB)** |
| DOM nodes | 1,943 |
| Inline SVG charts | 11 |
| **Third-party chart library** | **None** |
| Inline script | ~12 KB |
| External script requests | 47 (**dev artifact**) |
| CSS requests | 13 (**dev artifact**) |
| DOMContentLoaded | ~729 ms *(dev)* |
| Load | ~1,527 ms *(dev)* |

## No meaningful problems found

**No chart library.** A `d3` string match in the HTML turned out to be a
substring of the Astro scoped-class hash `astro-cid-qgd3ajik` — there is no d3,
Chart.js, Plotly, ECharts, Recharts or Highcharts. Every chart is **hand-authored
inline SVG**, server-rendered.

This is the single best performance decision on the page. A benchmark landing
with 11 charts would typically ship 100–300 KB of JS to draw them; this ships
none. It also explains why there is no chart re-render cost when switching the
Cost/Efficiency toggle — the toggle is CSS over pre-rendered SVG, so there is
nothing to redraw.

**56 KB gzipped is fine** for a page carrying a full leaderboard, 11-model cost
and efficiency datasets, a scenario matrix and 11 charts. Not worth optimising.

**1,943 DOM nodes is healthy** for this much content.

**The 47 script / 13 CSS requests are a dev-server artifact.** Astro serves
unbundled modules in dev and bundles them for production; total transferred
script was only ~19 KB. **This is not a production finding** and should not be
actioned on this evidence.

**No layout shift or slow interaction observed** during tab switching, toggling
or scrolling.

## The one real cost is length, and it is a UX issue

| | Height |
|---|---:|
| Desktop | ~12,000 px |
| Mobile (390 px) | **14,028 px** |

All of it is server-rendered eagerly. Nothing below the fold is deferred, and the
document carries the full dataset for every view — including the collapsed
`<details>` matrices and both cost bases — whether or not a reader opens them.

At 56 KB gzipped this does **not** justify code-splitting or lazy-loading; the
complexity would buy little. It is reported because it is the mechanism behind
the mobile length finding: the page is long because it renders everything, and
the fix is editorial (remove/reorder, per `recommendations.md`) rather than
technical.

## Not verified

- Production build sizes and timings.
- Real-device mobile performance (see `mobile-audit.md` on the resize limitation).
- Core Web Vitals (LCP/CLS/INP) — dev-server measurements would not be
  representative, so none are reported.

**If a production check is wanted later**, the two things worth measuring are LCP
on the hero and the production bundle count. Neither is actionable from here.

## Verdict

**No performance work needed.** The page is structurally well built for its
weight class, and the inline-SVG decision is worth keeping deliberately.
