# UX audit — MondayBench v1.1 landing

Audit only. Nothing changed.

---

## 1. First pass, as someone who knows nothing

Deliberately without repo knowledge. The page opens in Spanish.

### 5 seconds
I see `// MONDAYBENCH · V1.1` and a headline: *"¿Sabría un modelo manejar tu
lunes?"* — "Could a model handle your Monday?" I understand this is **about AI
models and everyday work**, and the tone tells me it is not an academic
leaderboard. That is genuinely good: the WHAT lands.

I do **not** see a single number, model name or result.

### 15 seconds
Two paragraphs, eleven lines. I learn there are five scenarios, every model gets
the same inbox, three runs each, frozen rubric. This is a lot of reading for a
hero, but it is precise and it answers WHY.

Below it, a Gantt chart of a Monday morning: Standup, Revisión de pricing,
Escalada de cliente, Cierre de sprint, Release bloqueada. Evocative. **It
contains no benchmark output** — it is set dressing for the premise.

At 2560×~780 the first screen ends here. **Nothing measured is above the fold.**

### 30 seconds
I scroll and reach *Clasificación general*. Now I get numbers, and I read:

> **01 · Claude Opus 5 · `PROVISIONAL` · 97.07**

I conclude **Claude Opus 5 won**. The badge says "provisional" but the rank says
`01`, the row is highlighted, and every model below shows a negative delta
measured against it (`−2.00`, `−2.14`, …). Three separate visual signals say
*winner*; one small badge hedges, and nothing on screen defines it.

### Still open after 60 seconds
- What does `PROVISIONAL` mean? *(The definition is ~3,000 px further down.)*
- Is Opus the official #1 or not?
- What are `#001 Vuelta al trabajo`, `#003 Bloqueos`? The tabs name them but
  never say what they test.
- What is `PEOR LUNES`? `DISPERSIÓN ENTRE ESCENARIOS`?
- Why is there a mystery unlabelled dot on the cost chart?
- Which model should I actually use?

**The page answers all of these. It answers them 2,000–5,000 px too late.**

---

## 2. Hero

WHAT ✅ · WHY ✅ · **RESULT ❌**

The brief asks for all three in five seconds. Two of three land well.

The hero does succeed at the thing that is hardest: a reader immediately
understands these are **everyday work tasks, not another academic benchmark**,
and the "same inbox, same contradictions" line makes clear the models face
identical scenarios. The "quality only" point is *not* made here — it first
appears in the leaderboard intro.

Two structural problems:

**Eleven lines of body copy.** The brief asks for "poco texto"; this is the
densest text block on the page, in the position that can least afford it.

**The Gantt is 230 px of prime space with zero information.** It is the single
best candidate for replacement on the page — not because it is bad, but because
something far better already exists further down (the five-Monday cards, §6).

Note also that a fixed site announcement bar plus the nav consume ~85 px above
the eyebrow before MondayBench content begins.

---

## 3. Overall leaderboard — the biggest problem

Measured state of the rendered table:

| # | Model | Score | Badge |
|---|---|---|---|
| 01 | Claude Opus 5 | 97.07 | `PROVISIONAL` |
| 02 | Qwen 3.8 Flash | 95.07 | — |
| 03 | GLM 5.3 Flash | 94.93 | — |
| 04 | Fable 5.1 | 94.90 | `PROVISIONAL` |
| 05 | GLM 5.3 | 93.73 | — |
| … | … | | |
| 07 | Gemini 3.8 Flash (High) | 88.37 | `PROVISIONAL` |

**The brief's requirement is: "There must be no reasonable interpretation that
Opus is an official #1 if it is not." The page currently fails that test.**

Four compounding signals:

1. **Rank `01`.** A single continuous 01–11 sequence with provisional models
   interleaved. Rank position is the strongest ranking claim a table can make.
2. **The delta column is anchored on Opus.** Every official model is shown as
   *worse than a provisional model* — `−2.00`, `−2.14`, `−3.34`. The official
   leader's headline number is a negative.
3. **Provisional rows are visually *promoted*.** Rows 01 and 04 carry a left
   accent bar and a lighter background — the site's own "highlight" treatment.
   The rows that should be set apart are instead the ones that look featured.
4. **`PROVISIONAL` is undefined at the point of use.** Its only definition sits
   at the bottom of the efficiency block, roughly 3,000 px below.

The prose *is* correct — "Claude Opus 5 registra la nota medida más alta, 97,07.
Es provisional…" — but it is grey secondary text beside a giant `01`. Prose
loses to layout.

To be explicit about scope: **no score should change and no model should be
removed.** The fix is presentational — separate the official ranking sequence
from provisional entries, and stop anchoring deltas on a provisional row.

---

## 4. Top performance band

Rendered as three cards under *"Tres modelos que el benchmark no puede separar"*
("Three models the benchmark cannot separate"):

| Label | Model | Score |
|---|---|---|
| Mayor puntuación medida | Qwen 3.8 Flash | 95.07 |
| El más barato de la banda | GLM 5.3 Flash | 94.93 |
| El más conciso del top | Claude Fable 5.1\* | 94.90 |

**This is the best section on the page.** The headline states the finding in
plain language, and each card gives a model a *reason to exist* rather than a
rank. This is exactly what the brief asks for in §5, and it needs no methodology
to understand.

Three issues:

**(a) Terminology collision — P0.** The first card is labelled *"Mayor puntuación
medida"* / *"Highest measured score"* — the **identical phrase** used ~1,400 px
above for Claude Opus 5 at 97.07. Same words, two models, two numbers, both
languages. The card presumably means *highest among official models*, but does
not say so.

**(b) The band silently includes a provisional model.** Fable 5.1\* is one of the
three cards. The brief describes the official band as Qwen 3.8 Flash + GLM 5.3
Flash. The asterisk is the only marker.

**(c) The 0.14-point separation is never stated as a number.** The headline says
the benchmark "cannot separate" them and the intro mentions measurement noise,
but the concrete, memorable fact — *0.14 points apart* — is absent.

On the label itself: **"Top performance band" / "Banda de máximo rendimiento" is
acceptable but abstract.** The section headline already does the work better than
the term does. Alternatives worth considering: *"Empate técnico"* / *"Technical
tie"*, or *"Demasiado cerca para ordenar"* / *"Too close to rank"*. Not
implemented.

---

## 5. The five Mondays

**The explanatory section is excellent — and it is 4,800 px below the tabs.**

At ~5,959 px, *"Tu lunes, en cinco pruebas"* renders five linked cards:

| | Verb | Title | Question |
|---|---|---|---|
| #001 | **ENTENDER** | Vuelta al trabajo | ¿Sabe distinguir lo que de verdad importa? |
| #002 | **RECONCILIAR** | Objetivos móviles | ¿Sabe qué ha cambiado por debajo? |
| #003 | **PLANIFICAR** | Bloqueos | ¿Encuentra el camino entre las dependencias? |
| #004 | **ANALIZAR** | Los números no mienten | ¿Razona sobre datos de negocio sucios? |
| #005 | **COMUNICAR** | Leer la sala | ¿Le cuenta lo mismo a cuatro personas distintas? |

The verbs are the key that makes the whole suite legible, and the `→` connectors
convey that this is one morning taken apart rather than five unrelated exams.

**But the tab strip near the top shows only `#001 Vuelta al trabajo`** — title
without verb. Alone, the titles are evocative and *not* self-explanatory:
"Bloqueos" and "Leer la sala" do not tell you what is being tested. So the
navigation is opaque while the explanation, which already exists and is good,
sits far below.

**They are not tabs.** Clicking `#001` performs a **full page navigation** to
`/es/mondaybench/001` — new URL, new document title, scroll position lost. The
brief asks for tabs that feel *clickable, interactive, fast, distinct*; these are
page loads. On the scenario page you land at "01 EL RESULTADO" with no reminder
of what the scenario tests.

Whether to make them real tabs is a bigger call than this audit should make —
separate URLs are good for sharing and SEO. But **the verb belongs in the tab
label** regardless, and that is cheap.

Also: the scenario pages show Monday Score to **one decimal** (98.5, 98.0, 97.5)
while the overall board uses **two** (97.07, 95.07). See `copy-audit.md`.

---

## 6. Cost — the dual-basis rendering

This is where the audit found the most serious rigor defect.

### What is right

The **table** handles it well. The GLM 5.3 row reads:

```
GLM 5.3    93.73    $99.20            [First-party]
                    $5.67 · ruta      [Helmcode route]
```

Two figures, two badges, both tooltipped, never merged, no range. A reader who
reaches the table is well served.

### What is wrong — P0

**The scatter draws the frontier ring on the wrong point.** Measured from the
DOM, both GLM 5.3 points carry the extended-frontier ring:

```
cx=537  ring=primary=0  label="GLM 5.3"   :: 93.73 · $99.20/1k · First-party
cx=333  ring=primary=0  label=(none)      :: 93.73 · $5.67/1k  · Helmcode route
```

`primary=0` is the "on the extended provider frontier" marker. GLM 5.3 earns
that place **because of its $5.67 route price**. Ringing the $99.20 point states
the opposite of the audited result: at $99.20 GLM 5.3 is *dominated* by both
frontier models. The table agrees with the audit — it gives GLM 5.3 no
`EN FRONTERA` badge — so **the chart and the table on the same screen contradict
each other.**

**The $5.67 point has no label.** Only a hover tooltip. Scanning, a reader sees a
nameless ringed dot at ~$5.70 and a labelled "GLM 5.3" at ~$99.

**The legend does not mention the route basis.** It reads: `Solo first-party` ·
`OpenRouter` · `En frontera`. There is **no key for "Helmcode route"** — the very
basis this release introduced. The nearest dotted key is *OpenRouter*, so the
most available inference for the unlabelled cheap dot is that it is an
**OpenRouter** price. It is not.

**`En frontera` conflates two different frontiers.** The chart draws two ring
styles — solid (`primary=1`, official first-party frontier: Qwen 3.8 Flash, GLM
5.3 Flash) and dotted (`primary=0`, extended provider frontier) — under one
legend key. The difference between those two sets is the entire GLM 5.3 finding.

### Could a screenshot produce a false claim?

**Yes — three of them:**

1. *"MondayBench puts GLM 5.3 on the cost-efficiency frontier at $99/1k."*
   The ring says so. The audit says it is dominated.
2. *"GLM 5.3 costs about $5.70 via OpenRouter."* The legend invites it.
3. *"MondayBench rates GLM 5.3's first-party price high-confidence."* — see below.

### The confidence column — P0

The table's `CONFIANZA` column shows **HIGH** for GLM 5.3.

That column renders `pricing_confidence` (confidence in the *arithmetic*), which
is legitimately HIGH. But `identity_confidence` is **CONTESTED** — the entire
qualification of this publication — and it is **never surfaced on the page**.
Verified: no source file references `identity_confidence`, and the rendered page
contains zero occurrences of "contested"/"contestado".

So the one number on the site whose SKU attribution is explicitly disputed is
displayed as `First-party · HIGH`. The artifacts are careful; the page is not.

### Cost insight

The brief asks whether *"same model, same quality, very different economics
depending on route"* emerges naturally. **Currently: no.**

The section headline is *"Calidad frente a coste"* and the standfirst is about
**Opus**, not about the dual basis. The dual basis is visible only as an
unexplained doubled dot. The genuinely interesting result of this release is
present in the data and absent from the narrative.

The `De $0.44 a $456 por 1.000 tareas · Más de 1037× de diferencia` callout is
good and correctly cautions it is a price range, not a quality comparison.

---

## 7. Pareto

The word "Pareto" **does not appear in the UI at all** — only `En frontera` /
`On frontier`, plus rings on the chart and a badge in the table. A prior decision
deliberately removed three paragraphs of Pareto prose from this view.

Against the brief's scale: **B — understandable after a tooltip**, sliding toward
C for the extended frontier.

- The *concept* is fine. Rings on the cheap-and-good models in a quality-vs-cost
  chart are close to self-explanatory, and avoiding the word "Pareto" was right.
- The *execution* is not, for the reason in §6: one legend key covers two
  different frontiers, and the ring is on the wrong GLM 5.3 point.

"En frontera" is more opaque than it needs to be. Something closer to
**"Mejor calidad por su precio" / "Best quality for the price"** would carry the
meaning without mathematics. The caution: that phrasing edges toward a
recommendation, and the current label's neutrality is deliberate. A middle option
is *"Nadie mejor por menos" / "Nothing better for less"*, which states the
dominance rule directly. Not implemented.

**It is not unnecessary complexity** — it is the main landing's most decision-useful
element. It should be clarified, not removed.

---

## 8. Efficiency

Two charts: **VELOCIDAD** (score vs median time to first answer) and
**CONCISIÓN** (mean output tokens, sorted).

Strong points:
- Seconds, not milliseconds. Axis `0s…300s`. Correct and readable.
- *"Ninguna entra en el Monday Score, y no existe una puntuación de eficiencia"*
  — the rigor line, present and clear.
- The concision bars are the most scannable graphic on the page: sorted, one row
  per model, absolute values on the right.

Against the brief's questions:

| Question | Answer |
|---|---|
| Which is fastest? | **Difficult.** Opus (~41 s) is leftmost but rendered **grey**; the purple emphasis goes to the 94.9–95.1 band. The fastest model is de-emphasised, and no callout names it. |
| Which produces least output? | **Immediately obvious.** Gemma 4, ~0.9k, top of a sorted list. |
| Expensive but fast? | **Difficult** — requires holding the cost chart in mind while reading the speed chart. |
| Slower but cheaper? | **Difficult**, same reason. |

Two concrete defects:

**Label collision in the top-right of the speed chart.** `Qwen 3.8 Flash`,
`GLM 5.3 Flash` and `GLM 5.3` cluster at 253–278 s with overlapping labels — the
three models a reader most wants to compare are the least legible.

**Grey means two different things.** Grey = "outside the measured-quality band",
but reads as "less important". Applied to Opus, the highest-scoring model on the
page, it is actively misleading.

Every efficiency figure matches the canonical data (GLM 5.3: 93.73, 253.3 s,
~21.3k; Opus: 97.07, 41.3 s, ~9.2k; Fable: 94.90, 50.9 s, ~8.2k; Qwen 3.8:
95.07, 258.9 s, ~31.7k; GLM 5.3 Flash: 94.93, 278.2 s, ~20.1k). No discrepancy.

---

## 9. Capabilities

Reached via a **full page navigation** to `/es/mondaybench/capacidades`.

**The brief's worry is already handled**: capability names are human-readable —
*criterio de negocio*, *planificación* — not raw IDs like
`cross_source_reconciliation`. Each has a plain-language definition. Grouped into
four families (Ejecución y criterio, Razonamiento, Manejo de información,
Comunicación) with an anchor nav.

But the answer to *"does this help me choose a model?"* is **not really — it
feels like another benchmark chart.** It is ~22 capabilities × 11 models ≈ 240
bars in one vertical stack. The top bar is highlighted, so each block does say
"best at X" — but there is **no per-model summary**. To learn what GLM 5.3 Flash
is good and bad at, you must scan 22 charts and mentally transpose.

The page's own opening line — *"Léelo por filas, no por columnas"* ("read it by
rows, not by columns") — is an instruction that exists because the layout fights
the question most readers arrive with.

Defects:
- **Provisional badges are clipped**: `PROVIS…`, `PROV…`.
- **Rounding hides real differences**: three models all labelled `98%` render
  visibly different bar lengths.
- `dispersión 45` appears without explanation.

---

## 10. Provisional models

The definition, in full:

> *\* Provisional: no se pudo demostrar que la ruta de generación sea equivalente
> al harness oficial de MondayBench. Estas filas se puntúan y se clasifican con
> el resto.*

**The wording is good** — close to the brief's target sentence, and honest that
these rows *are* ranked with the rest. The problem is placement and consequence:

- It sits at the **bottom of the efficiency block (~4,570 px)**; the first
  `PROVISIONAL` badge appears at **~1,400 px**. ~3,000 px of unexplained badge.
- On the capabilities page it is **truncated to `PROVIS…`**.
- The asterisk convention (`Claude Opus 5*`) is used in charts and the band cards
  with no nearby key.
- "Se clasifican con el resto" is the honest description of current behaviour —
  and is precisely what makes rank `01` a problem (§3).

Three models carry it: Claude Opus 5\*, Claude Fable 5.1\*, Gemini 3.8 Flash
(High)\*.

---

## 11. Information hierarchy

Measured document order and heights:

| px | Section | Height |
|---|---|---|
| 135 | Hero | 1,071 |
| 1,259 | Overall leaderboard | 1,396 |
| 2,655 | Top band + Cost/Efficiency views | 2,468 |
| 5,123 | Insights — "Tres cosas que la clasificación no dice" | 836 |
| 5,959 | **Five Mondays explained** | 701 |
| 6,660 | Finding — "Los modelos saben callar" | 855 |
| 7,515 | Comparison — "Dos modelos, dónde se diferencian" | 1,720 |
| 9,235 | Methodology | 968 |
| 10,203 | Reproducibility | 1,280 |
| 11,482 | CTA | 532 |

**Total ~12,000 px desktop / ~14,000 px mobile.**

Prominent but strategically secondary:

1. **The hero Gantt (230 px, top of page)** — highest-value real estate, zero
   information.
2. **"Dos modelos, dónde se diferencian" (1,720 px)** — the single largest
   section on the page is a two-model deep-dive, larger than the leaderboard and
   more than twice the five-Monday explainer.
3. **Reproducibility (1,280 px)** — important for credibility, but it outweighs
   the scenarios explainer by nearly 2:1.

Under-weighted relative to importance:

1. **The five Mondays (701 px, at 5,959)** — item 3 in the brief's priority,
   sits 6th, and is the key to the whole suite.
2. **Efficiency** — no section of its own; nested inside a radio toggle.

The brief's expected priority is broadly right. The page's *content* matches it;
the page's *order* does not.

---

## 12. Interaction

| Interaction | State |
|---|---|
| Cost / Efficiency toggle | **Works**, styled as tabs; they are radio inputs. Programmatic `.click()` on the input did not switch the view; clicking the visible label did. Worth a manual check with keyboard and screen reader. |
| Scenario "tabs" | Full page navigations, not tabs (§5). |
| Capabilities "tab" | Full page navigation. |
| Sticky tab strip | **Good** — stays available while scrolling. |
| Chart hover tooltips | Work — `<title>` elements. But they are the **only** carrier of critical facts (the $5.67 point's identity), and `<title>` is unavailable on touch. |
| `<details>` disclosures | Good progressive disclosure; used for the per-scenario matrix, technical detail, cost-at-scale. |
| Table row expanders | Present on scenario pages (chevrons). |

**The main interaction risk is tooltip-only information on touch devices**, which
is where the unlabelled cost point becomes unresolvable.

No layout shift or slow interaction was observed.

---

## 13. The 30-second test

*"I use LLMs for real work. There are too many models. Tell me which one I should
use."* — 0 impossible · 1 difficult · 2 understandable · 3 immediately obvious.

| Question | Score | Why |
|---|---|---|
| Best measured quality | **3** | `01 · Claude Opus 5 · 97.07`, top of the table. Unmissable. |
| Best **official** quality | **1** | Requires knowing `PROVISIONAL` excludes Opus *and* Fable, with the definition 3,000 px away and rank `01` arguing the opposite. |
| Best quality/price | **2** | The band cards ("el más barato de la banda → GLM 5.3 Flash") answer it well; the chart muddies it with the mis-ringed GLM 5.3 points. |
| Fastest | **1** | Readable from the chart's x-axis, but the fastest model is greyed out and nothing names it. |
| Best open-model option | **2** | Effectively answered by the band cards, but "open" is never a filter or a label — the reader must know which names are open. |
| Why trust it | **3** | Frozen rubric, 3 runs, dispersion columns, methodology and reproducibility sections, plus honest provisional disclosure. A real strength. |

**Total 12/18.** Trust and raw-quality read excellently; every *decision* question
underperforms.

---

## 14. Decision test

What does the page actually lead a reader toward?

| If I care about | The page leads me to | Correct? |
|---|---|---|
| **Quality** | **Claude Opus 5** (rank 01, 97.07) | **Misleading.** Highest measured, but provisional. The official answer is Qwen 3.8 Flash. |
| **Quality + cost** | **GLM 5.3 Flash** ($10.71/1k, "el más barato de la banda", solid frontier ring) | **Correct**, and well communicated — the page's best outcome. |
| **Speed** | Nothing in particular | **Under-communicated.** Opus (~41 s) and Fable (~51 s) are ~5× faster than the leaders; both are grey, both provisional, and neither is named as fastest. |
| **Open models** | Qwen 3.8 Flash / GLM 5.3 Flash, by inference | **Accidentally correct.** The top band happens to be open models, but the page never says so, and open-vs-closed is never a visible dimension despite the scenario page title using the phrase "8 modelos abiertos". |

The quality row is the one to fix. It is the most likely question a first-time
visitor has, and the page currently answers it with a provisional model.
