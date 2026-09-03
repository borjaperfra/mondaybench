# Recommendations — prioritised

**Audit only. Nothing below is implemented.** No score, dataset, rubric or
methodology change is proposed anywhere in this file.

Priority bias, per the brief: **prefer subtraction.** Six of the eleven P0/P1
items below remove, move or rename something. Only two add copy, and both add
fewer than ten words.

---

# P0 — comprehension blockers

## P0-1 · A provisional model holds rank `01`, and the whole table is anchored on it

**PROBLEM**
The main leaderboard presents Claude Opus 5 as `01` in a continuous 01–11
sequence, with `PROVISIONAL` as a small undefined badge. Every official model's
delta is computed against it. The brief's requirement — *"no reasonable
interpretation that Opus is an official #1"* — is not met.

**EVIDENCE**
Rendered rows: `01 Claude Opus 5 PROVISIONAL 97.07` · `02 Qwen 3.8 Flash 95.07
−2.00` · `04 Fable 5.1 PROVISIONAL 94.90` · `07 Gemini 3.8 Flash (High)
PROVISIONAL 88.37`. Provisional rows additionally carry a left accent bar and a
lighter background — the site's *highlight* treatment. The definition of
"provisional" is ~3,000 px below first use. The page's own footnote concedes the
behaviour: *"Estas filas se puntúan y **se clasifican con el resto**."*

**PROPOSED CHANGE**
Presentational only — no score changes, no model removed.
1. Number **only official models** `01…08`. Render provisional rows with a
   marker (`*`) instead of a rank integer.
2. Re-anchor the delta column on the **top official** score (95.07). Opus then
   shows `+2.00`, which is both true and self-explaining.
3. Replace the "highlight" styling on provisional rows with a quieter,
   visually *set-apart* treatment.
4. Put a one-line key directly under the table, not 3,000 px away.

**EXPECTED EFFECT**
"Best official quality" moves from **1 → 3** on the 30-second test. Removes the
page's only genuinely misleading claim. Opus stays visible and interesting — it
simply stops occupying the winner's slot.

**FILES**
`src/components/mondaybench/OverallBoard.astro`, `src/data/mondaybench/board.ts`,
`overall.data.ts`, `src/data/mondaybench/provisional.ts`

---

## P0-2 · The cost scatter rings the wrong GLM 5.3 point and leaves the other unlabelled

**PROBLEM**
Both GLM 5.3 points carry the extended-frontier ring. GLM 5.3 earns that place
**because of its $5.67 route price**; ringing the $99.20 point asserts the
opposite of the audited result, where $99.20 is *dominated*. The $5.67 point has
no label. The chart therefore contradicts the table beside it, which correctly
gives GLM 5.3 no `EN FRONTERA` badge.

**EVIDENCE**
From the live DOM:
```
cx=537  ring=primary=0  label="GLM 5.3"  :: 93.73 · $99.20/1k · First-party
cx=333  ring=primary=0  label=(none)     :: 93.73 · $5.67/1k  · Helmcode route
```
`analysis/cost-value/pareto.json`: `primary.frontier = [glm5.3-flash,
qwen3.8-flash]`, GLM 5.3 in `primary.dominated`. It appears only in
`extended_provider.frontier`.

**PROPOSED CHANGE**
1. Draw the extended-frontier ring **only on the point whose basis earns it** —
   the route point. Remove it from the first-party point.
2. Label the route point (`GLM 5.3 · ruta`), or label the pair once with both
   figures. It must be identifiable **without hover** — there is no hover on
   touch.

**EXPECTED EFFECT**
Chart and table agree. Removes a screenshot that would read *"MondayBench puts
GLM 5.3 on the frontier at $99/1k."* Makes the dual-basis point legible on
mobile.

**FILES**
`src/components/mondaybench/CostView.astro` (`onExtendedFrontier`, the
`rows.filter(r => r.m.alt_cost)` block)

---

## P0-3 · The cost legend has no key for the route basis, and merges two different frontiers

**PROBLEM**
The legend reads `Solo first-party · OpenRouter · En frontera`. There is **no key
for "Helmcode route"** — the basis this release introduced. The nearest dotted key
is *OpenRouter*, so the most available reading of the unlabelled cheap dot is
that it is an OpenRouter price. Separately, `En frontera` covers **two** ring
styles that mean two different frontiers, and that distinction *is* the finding.

**EVIDENCE**
Legend nodes: `["Solo first-party", "OpenRouter", "En frontera"]`. The chart
renders `ring primary=1` (official first-party frontier: Qwen 3.8 Flash, GLM 5.3
Flash) and `ring primary=0` (extended provider frontier) with one shared key.
`c.basisTip` already contains a correct `'Helmcode route'` tooltip — it simply
has no legend entry.

**PROPOSED CHANGE**
Add a fourth key for the route basis, and split `En frontera` into its two real
meanings (e.g. *"En frontera (oficial)"* / *"En frontera (por ruta)"*). Copy for
both bases already exists in `costvalue.ts`.

**EXPECTED EFFECT**
Kills false claim #2 (route price read as OpenRouter). Makes the official vs
route frontier distinction visible instead of inferable.

**FILES**
`src/components/mondaybench/CostView.astro` (legend), `src/data/mondaybench/costvalue.ts` (EN + ES)

---

## P0-4 · The one contested price on the site is labelled `HIGH` confidence

**PROBLEM**
The cost table's `CONFIANZA` column shows **HIGH** for GLM 5.3. That column
renders `pricing_confidence` (confidence in the arithmetic, legitimately HIGH).
But `identity_confidence` is **CONTESTED** — the whole qualification of this
publication — and it never reaches the page. A reader sees
`GLM 5.3 · $99.20 · First-party · HIGH`.

**EVIDENCE**
`publication-data.json` for `glm5.3`: `pricing_confidence: HIGH`,
`identity_confidence: CONTESTED`, `first_party_pricing_identity: CONTESTED`.
`grep -rn identity_confidence src/ scripts/` → **no matches**. The rendered page
contains **zero** occurrences of "contested" / "contestado".
`CostView.astro:393` renders `r.m.pricing_confidence`.

**PROPOSED CHANGE**
Surface `identity_confidence` where it is not `EXACT` — as a small qualifier on
the basis badge, with the existing tooltip wording. Do **not** overwrite the
arithmetic-confidence value; these are two different facts and the audit is
explicit that they must not be conflated.

**EXPECTED EFFECT**
The page stops asserting high confidence in the one attribution the project
formally disputes. Brings the site in line with artifacts that were careful about
exactly this.

**FILES**
`scripts/sync-mondaybench.mjs` (field is not currently emitted),
`src/data/mondaybench/types.ts`, `CostView.astro`, `costvalue.ts`

---

## P0-5 · "Highest measured score" names two different models

**PROBLEM**
The identical phrase, in both languages, ~1,400 px apart, labels Claude Opus 5
(97.07) and Qwen 3.8 Flash (95.07).

**EVIDENCE**
EN: *"Claude Opus 5 records the highest measured score at 97.07"* and band card
*"Highest measured score → Qwen 3.8 Flash 95.07 / 100"*. ES identically:
*"la nota medida más alta, 97,07"* and *"Mayor puntuación medida"*.

**PROPOSED CHANGE**
Qualify the **card** (the leaderboard sentence is accurate): *"Mayor puntuación
oficial"* / *"Highest official score"*, or *"La más alta de la banda"* /
*"Highest in band"*.

**EXPECTED EFFECT**
Removes a self-contradiction, and reinforces P0-1 by making "official" a phrase
the reader has already met.

**FILES**
`src/components/mondaybench/TopBand.astro`, `src/data/mondaybench/board.ts` (EN + ES)

---

# P1 — meaningful improvements

## P1-1 · Replace the hero Gantt with the five-Monday cards

**PROBLEM**
Two problems, one fix. The hero's 230 px Gantt is information-free set dressing
in the page's most valuable space, and the five-Monday explainer — the key to the
whole suite — is stranded at 5,959 px, sixth in document order.

**EVIDENCE**
Section map: hero 135 px (h 1,071, contains the Gantt), five Mondays at 5,959
(h 701). The cards carry verbs (`ENTENDER`, `RECONCILIAR`, `PLANIFICAR`,
`ANALIZAR`, `COMUNICAR`) plus a one-line question each. The Gantt renders
Standup / Revisión de pricing / Escalada de cliente / Cierre de sprint / Release
bloqueada — none of it measured.

**PROPOSED CHANGE**
Move `SuiteArc` (or a condensed variant) into the hero, in place of
`MondayGlance`. **Net removal of one component.**

**EXPECTED EFFECT**
"What does it measure" is answered above the fold instead of on screen seven.
Page gets ~230 px shorter. The scenario tabs immediately below become meaningful,
because the reader has just met the five verbs.

**FILES**
`src/pages/_mondaybench.astro`, `MondayGlance.astro` (removed from hero),
`SuiteArc.astro`

---

## P1-2 · Put the scenario verb in the tab label

**PROBLEM**
Tabs read `#001 Vuelta al trabajo`, `#003 Bloqueos`, `#005 Leer la sala`. Alone
the titles are evocative but not self-explanatory. The verb that makes each
legible already exists — 4,800 px below.

**EVIDENCE**
Tab strip vs. the `SuiteArc` cards, which pair each title with `ENTENDER`,
`RECONCILIAR`, `PLANIFICAR`, `ANALIZAR`, `COMUNICAR`.

**PROPOSED CHANGE**
`#001 · Entender — Vuelta al trabajo`, or the verb as a second line. Rename only;
**scenario IDs unchanged**.

**EXPECTED EFFECT**
Navigation becomes self-describing at the point of use. Complements P1-1 rather
than duplicating it — one is discovery, the other navigation.

**FILES**
`src/components/mondaybench/ScenarioTabs.astro`, `src/data/mondaybench/index.ts`

---

## P1-3 · Move the provisional definition to first use

**PROBLEM**
`PROVISIONAL` first appears at ~1,400 px; its definition sits at ~4,570 px. On
the capabilities page the badge is clipped to `PROVIS…`.

**EVIDENCE**
Definition: *"\* Provisional: no se pudo demostrar que la ruta de generación sea
equivalente al harness oficial de MondayBench…"*, rendered at the foot of the
efficiency block. Capabilities rows render `PROVIS…` / `PROV…`.

**PROPOSED CHANGE**
Move the existing sentence — unchanged, it is well written — directly under the
leaderboard. Keep the footnote or drop it as duplication. Fix the clipping.

**EXPECTED EFFECT**
With P0-1, the two changes together resolve the provisional question completely.
No new copy is written.

**FILES**
`OverallBoard.astro`, `EfficiencyView.astro`, `CapabilityProfile.astro`,
`provisional.ts`

---

## P1-4 · Say the cost insight, and stop leading the section with Opus

**PROBLEM**
The genuinely interesting result — *same model, same quality, ~17× apart
depending on route* — is present in the data and absent from the narrative. The
Cost section's standfirst is about Opus instead.

**EVIDENCE**
Heading *"Calidad frente a coste"*, standfirst *"Opus registra la calidad medida
más alta, pero en un punto de precio muy distinto…"*. The dual basis appears only
as an unexplained doubled dot. Canonical: $99.20 vs $5.67, ratio **17.48×**.

**PROPOSED CHANGE**
One analytical sentence near the GLM 5.3 row — e.g. *"El precio del modelo y el
precio de la ruta pueden contar historias muy distintas: 17,48× en este caso."*
State the ratio; do not explain it. **No marketing tone, no recommendation, no
speculation about why the meter differs** — the publication brief forbids
inferring the commercial mechanism, and this must not smuggle it back in.

**EXPECTED EFFECT**
The reader learns the finding instead of decoding a doubled dot. Depends on P0-2
and P0-3 to be legible.

**FILES**
`CostView.astro`, `costvalue.ts` (EN + ES)

---

## P1-5 · Name the fastest model, and stop greying it out

**PROBLEM**
"Which is fastest?" scores 1/3. Opus (~41 s) is leftmost on the speed chart but
rendered **grey**, because purple marks the 94.9–95.1 quality band. The
page's fastest model is visually de-emphasised and never named.

**EVIDENCE**
Speed chart: Opus 5\* and Fable 5.1\* at ~41 s / ~51 s in grey; Qwen 3.8 Flash,
GLM 5.3 Flash purple at 259 s / 278 s. Labels for `Qwen 3.8 Flash`,
`GLM 5.3 Flash` and `GLM 5.3` overlap in the top-right cluster.

**PROPOSED CHANGE**
Add a "fastest" marker on the chart (the band cards already prove the pattern
works), and resolve the three-label collision. Consider whether band-purple is
the right encoding on a chart whose subject is speed, not quality.

**EXPECTED EFFECT**
"Fastest" moves **1 → 3**. Fixes the most crowded labels on the page.

**FILES**
`EfficiencyView.astro`, `QualitySpeed.astro`

---

## P1-6 · Give capabilities a per-model summary

**PROBLEM**
~22 capabilities × 11 models ≈ 240 bars in one vertical stack, with no per-model
view. The page's own opening instruction — *"Léelo por filas, no por columnas"* —
exists because the layout fights the question readers arrive with.

**EVIDENCE**
Four families, 6+5+6+5 capabilities, every block listing all 11 models. No
"strongest / weakest at" summary anywhere.

**PROPOSED CHANGE**
A compact per-model strip — *strongest at X, weakest at Y* — derived from
existing scores. Frame as observations, **not** winner claims, and keep it inside
the same capability, since the page correctly warns that two capabilities are not
comparable within a model.

**EXPECTED EFFECT**
Turns a reference chart into a selection aid — the brief's §11 goal.

**FILES**
`CapabilityProfile.astro`, `CapabilityCompare.astro`, `capabilities.ts`

---

# P2 — polish

- **Decimal consistency.** Scenario pages use 1 decimal (98.5), everywhere else
  uses 2 (97.07). Either align to 2 or record why scenario means differ. Two
  models currently tie at 97.5 and are ranked 3 / 4 with nothing to separate them.
  *(`[number].astro`, `00N.data.ts`)*
- **10 px type on mobile.** 223 leaf nodes at exactly 10 px, 260 below 11 px —
  systematic, including leaderboard headers and axis labels. A token bump at
  small viewports, not per-element fixes.
- **Clipped provisional badges** on capabilities (`PROVIS…`).
- **Capability rounding**: three models labelled `98%` render visibly different
  bars.
- **Undefined jargon at first use**: `PEOR LUNES`, `DISPERSIÓN ENTRE ESCENARIOS`,
  `RANGO DE RUNS`, `dispersión 45`, the `ref` badge.
- **Hero copy**: the first paragraph restates the five scenarios, which the cards
  express better. Cut it if P1-1 lands.
- **`Unknown`** in the cost column for Gemini 3.8 sits oddly among dollar values;
  the em-dash used in the basis column is cleaner.
- **`method` copy block in `costvalue.ts` is dead** — fully written in EN and ES,
  rendered nowhere. Either render it or delete it; leaving it invites drift.

---

# DO NOT DO

Changes that would make the page worse or less rigorous.

| | Why not |
|---|---|
| **Add GLM 5.3 to the top performance band** | 93.73 is 1.20 below Qwen 3.8 Flash — an order of magnitude wider than the 0.14 separating the band. The band's credibility comes from being a measurement-noise claim. |
| **Publish a `$5.67–$99.20` range** | Two bases are not a range. This is the exact category error the cost audit rejected. |
| **Show one GLM 5.3 price and hide the other** | A pricing toggle was already removed for hiding half the field. The page's principle is *label, don't filter*. |
| **Promote `$5.67` to the headline figure** | It is `GATEWAY_METERED` with `CONTESTED` identity. First-party list is the comparable basis for a first-party column. |
| **Remove provisional models** | They are among the most interesting results (Opus fastest *and* highest measured). Separate them from the official ranking; do not delete them. |
| **Say "Pareto" in the UI** | Removing it was right. Fix the legend (P0-3), don't reintroduce the jargon. |
| **Turn the cost insight into marketing copy** | Credibility is this page's strongest asset (30-second test: 3/3 on trust). State the ratio; assert no mechanism. |
| **Explain *why* Helmcode metering differs from list** | Explicitly out of scope, and unresolvable from client-side evidence. |
| **Add an Efficiency Score or Value Score** | Repeatedly and deliberately excluded. The page says so; keep it. |
| **Delete the methodology / reproducibility sections to shorten the page** | They earn the 3/3 trust score. Shorten by removing *duplication*, not rigor. |
| **Chase the 47-request script count** | A dev-server artifact. Production bundles; total script was ~19 KB. |
| **Add a chart library** | 11 hand-authored inline SVGs, zero JS chart dependency, no re-render cost on toggle. Best technical decision on the page. |
| **Rewrite the ES copy** | It is idiomatic and occasionally better than the EN. Only the P0-5 label is wrong. |
