# Mobile audit — 390 px

Audit only. Nothing changed.

## Method, and why it is not a device test

`resize_window` is **non-functional in this environment**: it returns success and
the window stays at 2560 px, confirmed three times by reading
`window.innerWidth`. Rather than report a desktop render as mobile, the real page
was loaded in a **390 × 844 same-origin iframe**. Media queries evaluate against
an iframe's own viewport, so this is a genuine 390 px CSS render of the real
page — verified: `iframe innerWidth = 390`.

What this **cannot** tell us: touch-target ergonomics, momentum scrolling, real
device performance, iOS/Android font inflation. Those remain unverified. Tablet
(~768 px) was not separately audited for the same reason.

---

## Measured

| | |
|---|---:|
| CSS viewport | 390 px |
| Document scroll width | **378 px** |
| **Horizontal overflow** | **None** |
| Page height | **14,028 px** |
| Screens of scrolling (844 px) | **~16.6** |

---

## Good

**No horizontal page overflow.** 378 ≤ 390. The layout genuinely reflows rather
than shrinking a desktop grid — the commonest failure mode on a data-dense
benchmark page, and it is absent.

**The main leaderboard fits.** `.mb-ov-scroll` measures 330 visible / 330 content
— **0 px hidden**. The primary result table needs no sideways scrolling. This is
better than most benchmark sites manage.

**Charts reflow.** SVGs scale within the column; no fixed-width canvas.

---

## Findings

### P0 — the first screen is text only, and there is no result on it

The 844 px viewport is filled by: nav, eyebrow, headline, **two full paragraphs
of body copy**, and two stacked CTAs. Not one number, model name or score.

Desktop at least reaches the tab strip. On mobile the entire first screen is
prose, and the Gantt — itself information-free — comes *after* it. A phone reader
must scroll roughly **1.5 screens before seeing any benchmark output**, and about
**2 screens** before the leaderboard.

### P1 — 14,028 px is very long

~16.6 phone screens, ~2,000 px longer than desktop. The brief asks for a page
that is "rápida de escanear" and ideally *shorter*. Every subtraction in
`recommendations.md` helps here disproportionately.

### P1 — 223 text nodes render at exactly 10 px

Font-size distribution of leaf text nodes at 390 px:

| Size | Count |
|---|---:|
| 9 px | 1 |
| 9.6 px | 6 |
| **10 px** | **223** |
| 10.5 px | 20 |
| 11 px | 17 |
| 12 px | 98 |

**260 nodes below 11 px.** This is systematic, not accidental — 10 px is a design
token used for mono labels, badges, axis ticks and column headers, and it is part
of the page's technical aesthetic. It is not body copy.

But at 390 px it covers the leaderboard's own column headers and the chart axis
labels, i.e. the labels you need in order to read the numbers. Worth a token-level
bump on small viewports rather than per-element fixes.

### P2 — one collapsed table scrolls sideways by design

`.mb-ov-scroll` #1 measures 330 visible / 614 content — **284 px hidden**. It is
the per-scenario score matrix (`Modelo · #001 · #002 · #003 · #004 · #005 ·
Dispersión`), and it sits inside a **closed `<details>`** ("Ver las notas por
escenario").

This is acceptable: a 7-column × 11-row matrix cannot fit 390 px, it is opt-in,
and it is contained rather than breaking the page. Flagged only so it is a known
trade-off. `.mb-cost-tablewrap` hides 36 px — marginal, same pattern.

### Out of scope

`.status-bars` in the site footer hides 239 px of 417. It is a **site-wide footer
component, not MondayBench**, and is noted only so it is not mistaken for a
finding here.

---

## Touch-specific risk

Carried over from `ux-audit.md` §12, because it lands hardest on mobile:

**Critical information exists only in SVG `<title>` hover tooltips.** The
identity of the unlabelled GLM 5.3 route point at $5.67 is *only* available on
hover. **There is no hover on touch.** On a phone, that point is unresolvable —
a ringed dot with no name and no way to ask.

This makes the cost-chart labelling fix (P0-2) a mobile correctness issue, not
only a desktop clarity one.

---

## Verdict

**The responsive engineering is sound** — no overflow, the key table fits, charts
reflow. The mobile problems are the desktop problems amplified by a narrower
column: results too far down, page too long, labels too small, and one chart that
cannot be interrogated without a mouse.
