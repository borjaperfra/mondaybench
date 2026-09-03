# MondayBench v1.1 — UX pass, implemented

**Date:** 2026-09-03 · Frontend and content only.
**Model calls: 0. Judge calls: 0. No re-judge.** No run, verdict, evaluation,
score, scenario, rubric, evaluator contract, capability dataset, pricing
snapshot or pricing calculation was touched. v1.0 and v1.1 both verify with
unchanged digests.

Implements `recommendations.md`. Every change below traces to a finding in
`ux-audit.md`, `copy-audit.md` or `mobile-audit.md`.

---

## 1. Official vs provisional — the P0

`board.ts` used to number every measured result together, on the reasoning that
`provisional` is a badge and a badge cannot change an ordinal. Sound reasoning,
wrong result: the board printed `01 Claude Opus 5 · provisional · 97.07` with
every official model showing a negative delta against it.

**The rule changed and the module's own documentation changed with it.** Rows
are still sorted by score together — a provisional model that outscored the
field still appears at the top, because that is true — but only official rows
are numbered.

The old objection to un-numbering was that a rank column with holes reads as
"disqualified". That is answered by structure, not argument: provisional rows
are lifted into their own group, above the table, headed **"Medidos, fuera de la
clasificación" / "Measured, outside the ranking"**, where the highest measured
result is stated plainly and labelled as such.

```
MEDIDOS, FUERA DE LA CLASIFICACIÓN
  MEDIDA MÁS ALTA  Claude Opus 5  provisional      97.07
                   Fable 5.1      provisional      94.90
                   Gemini 3.8 Flash (High)  prov.  88.37

CLASIFICACIÓN OFICIAL — 8 modelos en el harness oficial, ordenados
  01 Qwen 3.8 Flash    95.07        —
  02 GLM 5.3 Flash     94.93    −0.14
  03 GLM 5.3           93.73    −1.34
  04 DeepSeek V4 Flash 91.70    −3.37
  …
  08 Gemma 4           63.00   −32.07
```

The provisional group is deliberately **not table-shaped**: no ordinals, no
column headers, no score bars, and none of the accent treatments the page uses
for "official" or "top band". It renders *above* the table because the highest
measured score is the most interesting number on the page and burying it would
be its own dishonesty — its heading is what keeps that safe.

`buildScenarioBoard` follows the same rule. Scenario tables print `–` in the
rank cell for a provisional row rather than an empty cell, because a blank reads
as a rendering fault where a dash plus the tag reads as deliberate.

**Delta anchored on the official leader.** `deltaFromOfficialTop` replaces the
old top-of-board anchor. The leader's cell is empty rather than a decorative
zero, and a provisional model above the anchor now reads `+2.00` — still
visible, still interesting, no longer the yardstick. Column renamed
**`Δ oficial` / `Δ official`**.

## 2. "Highest measured" now means one thing

The identical phrase named Claude Opus 5 (97.07) and Qwen 3.8 Flash (95.07),
1,400 px apart, in both languages.

Reserved for the provisional block. The band card is now
**`Líder oficial` / `Official leader`** — and it is derived, not asserted: if a
provisional result ever tops the band, the label falls back to
`La más alta de la banda` / `Highest in band`, so the card cannot claim an
official lead that is not there.

## 3. Cost — three factual fixes

**Frontier rings follow the pricing basis.** Both GLM 5.3 points carried the
extended-frontier ring, including the $99.20 point the analysis finds
*dominated* — so the chart asserted the opposite of the finding and disagreed
with the table beside it. `pointOnPrimaryFrontier` / `pointOnRouteFrontier`
read membership back against the cost each point plots:

* the first-party frontier can only belong to a primary point;
* the route frontier belongs to the route point where a model has one, and to
  its single point otherwise — exactly the rule the harness used to compute it.

No slug is named. A model earns a route ring because it carries an `alt_cost`.

Verified in the live DOM: GLM 5.3 at $99.20 now has **no ring**; the $5.67 point
has the dashed route ring; Qwen 3.8 Flash and GLM 5.3 Flash keep the solid
first-party ring.

**The route point says its own name.** `GLM 5.3 · ruta` is printed as a `<text>`
node, not a tooltip, and stays visible at 390 px where the other labels come
off — there is no hover on touch, and without it the $5.67 dot is unresolvable
on a phone.

**The legend gained the basis it was missing and split the frontier it was
merging.** It read `Solo first-party · OpenRouter · En frontera` while the chart
drew three bases and two different frontiers, so the only available reading of
the unnamed cheap dot was that it was an OpenRouter price. Now:

```
Solo first-party · OpenRouter · Ruta de Helmcode
Mejor calidad por su precio · tarifa del vendor
Mejor calidad por su precio · ruta
```

"Pareto" stays out of the UI; the wording is literally true — nothing scores
higher for less. Each key reproduces its marker exactly, and shape carries the
distinction so it survives greyscale.

**Identity confidence surfaced.** `identity_confidence: CONTESTED` reached no
surface a reader could see, so the one disputed attribution on the site rendered
as `First-party · HIGH`. It is now emitted by the sync, typed, and shown as a
small qualifier on the *basis* — `identidad en disputa` / `identity contested` —
with a tooltip explaining that the price is real and the mapping to the route is
what is contested. `pricing_confidence` is untouched; the two answer different
questions.

Shown for **CONTESTED only**. The other values in the data — `EXACT`,
`STRONG_MATCH`, `AMBIGUOUS`, `PROVIDER_ROUTE_EXACT_RUN_AMBIGUOUS` — are ordinary
provenance, and marking four of nine rows would devalue the one row this is for.

**The insight is stated.** One derived sentence above the chart gives both
figures and the factor. It says what and never why: a test greps it for
discount / wholesale / subsidy in both languages. The factor comes from the
unrounded per-task costs (17.48 → `17.5×`), not from dividing the rounded $/1k
figures, and the figures print as `$99.20` / `$5.67` rather than the compact
`$99` / `$6`.

**The dead pricing filter is gone.** A CSS rule still hid every
`[data-basis='prov']` mark when `#mb-pv-fp` was checked. That input no longer
exists so the rule was inert — but it would have erased the $5.67 point
silently. Deleted rather than left dormant.

## 4. Hero and the five Mondays

The Gantt is **removed** and `MondayGlance.astro` deleted. It was 230 px of the
best space on the page carrying no benchmark output, and on a phone it pushed
the first result below two screens of prose.

In its place, `MondayStrip.astro` — the five Mondays compressed to number, verb
and title, each one a link:

```
CINCO ESCENARIOS DE TRABAJO REAL, UNA MAÑANA
#001 ENTENDER      Vuelta al trabajo
#002 RECONCILIAR   Objetivos móviles
#003 PLANIFICAR    Bloqueos
#004 ANALIZAR      Los números no mienten
#005 COMUNICAR     Leer la sala
```

Hero copy went from **two paragraphs (11 lines) to one**. The cut paragraph
listed "contexto desordenado, decisiones que cambian, dependencias, datos de
negocio y comunicación" — the five scenarios in prose, which the strip now names
properly with links.

**The verbs are in the tabs.** They were the key to the whole suite and lived
only in cards 4,800 px below the navigation that needed them.

The verbs and questions moved from inside `SuiteArc.astro` to
`data/mondaybench/steps.ts`, because three surfaces now need the same map and
three copies would drift invisibly.

**A regression I caused and fixed:** adding the verb made seven tabs overflow
the 1,200 px content column, and the flex row answered by shrinking every tab
until `Overall` rendered as `O…`. On desktop the tab now shows number + verb and
the **title** gives way — `#003 PLANIFICAR` describes the scenario to a newcomer
and `#003 Bloqueos` does not, which is the entire reason the verb was added.
Below 860 px the strip scroll-snaps, so the title comes back. Verified: 0 px
overflow, no ellipsis on any tab.

## 5. Efficiency — the fastest model is named

Two derived markers, a dashed ring plus a word: **fastest measured**, and
**fastest official** when they differ.

**The brief's example was wrong and the data corrected it.** §16 expected
"Claude Opus 5\*: 41.3 s, fastest measured". Measured TTFA says otherwise:

| | |
|---|---:|
| Gemma 4 | **0.6 s** |
| Qwen 3.6 | 1.0 s |
| Claude Opus 5\* | 41.3 s |

**Gemma 4 is the fastest measured, and it is official** — so both markers
resolve to the same row and only one renders. Opus is the fastest of the
high-scoring models, which is a different claim, and the section's existing
prose already makes it. Nothing was hardcoded; the brief said to check, and
checking changed the answer.

On mobile every scatter label was hidden, leaving an unlabelled chart with no
hover. The two fastest points now keep their names there.

## 6. Provisional footnote de-duplicated

The full caveat sat at the foot of the efficiency block, ~3,000 px after the
first `PROVISIONAL` badge. It now lives once, in the leaderboard group beside
the models it describes, and names the asterisk convention the charts use. The
efficiency copy of it is gone.

On the capabilities page the badge rendered as `PROVIS…` on every provisional
row of all twenty-two blocks — a caveat truncated into noise. Replaced with the
asterisk, which carries the same mark in one character; the tooltip keeps the
per-model reason and the page's own footnote keeps the sentence.

## 7. The two-model deep-dive — kept, and its default fixed

`recommendations.md` proposed compressing or removing it. **Re-inspecting it
after the other changes showed the audit had read it wrong**, and this report
says so rather than quietly acting on the mistake: it is not a two-model
write-up. It is an **interactive A/B comparator** over all ten models, showing
the six capabilities with the largest gap between the pair you choose. It is the
only place on the site where two specific models can be compared head to head,
and it answers the "does this help me choose?" question better than the
capabilities page does.

The real defect was its default. The code said *"the top two, which is the
comparison most readers arrive wanting"* and then took `models[0]` and
`models[1]` from an **alphabetically ordered** list — so 1,720 px of a useful
tool opened on **DeepSeek V4 Flash vs Gemma 4**, ranks four and eight.

Sorted by score and restricted to official models, it now opens on
**Qwen 3.8 Flash vs GLM 5.3 Flash** — the two the top-band section says the
benchmark cannot separate. That section poses the question; this is where a
reader can look into it. Every model stays selectable.

**Decision: kept at full size.** It is not redundant, and it is now pointed at
the question the page actually raises.

## 8. Mobile typography — categorised, not bumped

The audit found 223 nodes at exactly 10 px. Rather than enlarge everything:

**A · decorative, left small** — the `#001` in the strip (paired with a larger
verb), the `diferencia` caption beside a large number, nav chevrons.

**B · meaningful, raised to 11 px on mobile** — chart axis values (you cannot
read a chart without them), table column headers, the basis and confidence cells
that qualify a cost figure, and the comparator's percentages, which *are* the
comparison.

**C · redundant, removed on mobile** — the reasoning-token sub-caption under
every concision bar. Ten rows of 10 px text at 0.45 opacity, publishing a figure
the component's own header says is not comparable across models. It doubled the
list's height on a phone. Kept on desktop.

Result: **223 → 112** nodes below 11 px in MondayBench content.

## 9. Dead code removed

* `MondayGlance.astro` — the Gantt, unreferenced after the hero change.
* The `method` copy block in `costvalue.ts` — nine methodology bullets, fully
  written in both languages, imported by nothing. Not wired in: the page
  deliberately removed prose of that kind, and the methodology it carried is
  already in the Methodology and Reproducibility sections.
* The `#mb-pv-fp` pricing-filter rule.

## 10. A test that encoded the old rule

`board.test.ts` asserted *"is numbered in every scenario table, alongside the
official rows"* — the behaviour this pass deliberately reversed. **Rewritten,
not deleted**, to assert the new rule: present, sorted by score, never numbered;
official positions unbroken; no provisional row holding a number.

`uxpass.test.ts` adds **33 semantic tests** across nine groups — ranking,
delta anchor, highest-measured semantics, basis-aware frontiers, route
labelling, identity confidence, one-score-two-prices, step verbs, EN/ES key
parity, and no-composite-metric.

Two of my own tests were wrong first and were fixed rather than accommodated:
one grepped `.astro` source and failed on EfficiencyView's own comment *"There
is no efficiency score, and there must not be one"* — testing prose about a rule
is not testing the rule, so it now reads the copy layer a user sees.

## 11. A repo test defect this surfaced

`tests/test_line_endings.py` failed on two audit **screenshots**: it scanned
every hashed artifact for the bytes `0D 0A`, which a JPEG or PNG contains
wherever its compressed stream happens to produce them. Not a line ending, and
git does not rewrite it — `.gitattributes` treats these as binary.

Fixed by excluding binary suffixes. The failure came from last session's
screenshots, not from this pass, and would have flagged every image ever added
to a hashed group.

## 12. Validation

| | |
|---|---|
| Site tests | **301 passed**, 17 files |
| MondayBench tests | **933 passed** |
| `astro check` | **0 errors**, 0 warnings |
| v1.0 | verified · `c056b4b4…` **unchanged** |
| v1.1 | verified · `a4d6eb6e…` **unchanged** |
| Quality artifacts changed | **none** |
| Model / judge calls | **0 / 0** |
| New dependencies | **none** |
| Chart library | **still none** |
| Page weight | 57,944 B gzipped (was 57,829) — **+115 B** |

`models.yaml` shows as modified in git; that is the GLM 5.3 model entry from the
earlier benchmark session, not this pass.

## 13. Page length — reported honestly

| | Before | After |
|---|---:|---:|
| Desktop | ~12,000 px | ~11,900 px |
| Mobile (390 px) | 14,028 px | **14,167 px** |

**Mobile got slightly longer, not shorter.** The hero lost 360 px and the
efficiency detail rows came off, but the leaderboard gained the provisional
group and the official heading — which is load-bearing, not decoration — and the
strip stacks to five rows on a phone.

The remaining large sections were examined and kept: Insights (1,214 px) carries
three decision-relevant findings and duplicates nothing; Methodology and
Reproducibility earn the 3/3 trust score and §24 protects them; `SuiteArc`
(963 px) overlaps the new hero strip but uniquely carries the verb + question
pairs, which §24 protects explicitly.

Folding the questions into the hero strip and deleting `SuiteArc` would save
~900 px on mobile. It was **not** done: it would push the strip's last items
below the 390 px fold, undoing §19, and it removes content the brief protects.
Flagged as the one substantial length reduction still available, for a decision
rather than taken unilaterally.

## 14. Screenshots

`screenshots/AFTER-01-desktop-hero.jpg` ·
`AFTER-02-leaderboard-official-vs-provisional.jpg` ·
`AFTER-03-efficiency-fastest.jpg` ·
`AFTER-04-mobile-390-first-screen.png` ·
`AFTER-05-cost-scatter-rings-legend.jpg`

BEFORE captures from the audit session are alongside them, same directory.
