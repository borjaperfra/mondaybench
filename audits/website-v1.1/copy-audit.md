# Copy audit — EN + ES

Audit only. Nothing changed. Only findings with real UX impact are listed.

`/mondaybench` **redirects to `/es/mondaybench`** — Spanish is what a first-time
visitor gets. Both were read in full.

## Translation quality

**High.** This is not machine translation and not literal translation. The ES
copy is idiomatic and in places better than the EN:

| EN | ES | |
|---|---|---|
| "Could a model handle your Monday?" | "¿Sabría un modelo manejar tu lunes?" | Both idiomatic |
| "Models know how to stay quiet" | "Los modelos saben callar" | ES is tighter |
| "Read the room" | "Leer la sala" | Correct idiom |
| "Moving targets" | "Objetivos móviles" | Correct |

Terminology counts match across locales — `highest measured` 3 / `medida más
alta` 3, `On frontier` 3 / `En frontera` 3, `Provisional` 2 / 2. Nothing is
translated in one language and left English in the other. **No literal-translation
defects found.**

---

## P0 — "Highest measured score" names two different models

Present in **both** languages, ~1,400 px apart:

| Location | EN | ES | Model | Score |
|---|---|---|---|---|
| Leaderboard intro | "Claude Opus 5 records the **highest measured score** at 97.07" | "Claude Opus 5 registra la **nota medida más alta**, 97,07" | Opus 5 | 97.07 |
| Band card | "**Highest measured score**" | "**Mayor puntuación medida**" | Qwen 3.8 Flash | 95.07 |

The card means *highest measured among official models* / *within the band*, but
says neither. A reader who notices will conclude the page contradicts itself; one
who does not will carry away whichever they read second.

**Fix direction:** qualify the card — "Mayor puntuación oficial" / "Highest
official score", or "La más alta de la banda" / "Highest in band". The leaderboard
sentence is accurate and should stay.

---

## P1 — `PROVISIONAL` is used ~3,000 px before it is defined

Badge first appears at ~1,400 px. Definition at ~4,570 px:

> *"\* Provisional: no se pudo demostrar que la ruta de generación sea equivalente
> al harness oficial de MondayBench. Estas filas se puntúan y se clasifican con el
> resto."*

The sentence itself is good — plain, honest, close to the brief's target. It is
in the wrong place, and it is **clipped to `PROVIS…` / `PROV…` on the
capabilities page**.

The asterisk form (`Claude Opus 5*`) appears in charts and band cards with no key
in view.

---

## P1 — Decimal precision is inconsistent

| Where | Format | Example |
|---|---|---|
| Overall leaderboard | **2 decimals** | 97.07, 95.07, 94.93 |
| Band cards | 2 decimals | 95.07 / 100 |
| Cost table | 2 decimals | 93.73 |
| **Scenario pages** | **1 decimal** | 98.5, 98.0, 97.5, 92.5 |

The brief specifies two decimals unless a component has an established reason.
Scenario means of three runs land on `.5` often enough that one decimal may be
deliberate — but the reason is not recorded anywhere, and the inconsistency is
visible when moving between the overall board and a scenario page.

Worth noting: on the scenario page **two models tie at 97.5** (Fable 5.1 and GLM
5.3) and are ranked 3 and 4. Two decimals might separate them, or might confirm a
real tie — either is better than an unexplained ordering.

---

## P1 — Jargon used without definition, at first use

| Term | Where | Problem |
|---|---|---|
| `PEOR LUNES` / worst Monday | Leaderboard column | Guessable, but undefined |
| `DISPERSIÓN ENTRE ESCENARIOS` | Leaderboard column | Undefined; rendered as a bar + number |
| `RANGO DE RUNS` | Scenario pages | Undefined |
| `dispersión 45` | Capabilities | Undefined; no units |
| `En frontera` / `On frontier` | Cost chart + table | Pareto without the word — good instinct, but unexplained, and covers **two** different frontiers |
| `ref` | Cost table badge | Unexplained two-letter badge |
| `Unknown` | Cost table (Gemini) | Sits in a column of dollar figures |

The page is generally excellent at defining its own terms — the methodology and
reproducibility sections are models of clarity. The gap is that definitions live
in those sections rather than at first use.

---

## P2 — Hero density

Eleven lines of body copy in the hero, in two paragraphs. Both are well written
and factually load-bearing (identical inbox, 3 runs, frozen rubric). The brief
asks for "poco texto" in a scannable page.

The second paragraph is the more valuable of the two — it is what distinguishes
MondayBench from a generic claim. The first paragraph's list ("contexto
desordenado, decisiones que cambian, dependencias, datos de negocio y
comunicación") **restates the five scenarios**, which the five-Monday cards
already express better with verbs. That is a subtraction opportunity, not an
addition.

---

## P2 — CTA labels

`Ver la clasificación ↓` / `See the leaderboard ↓` — clear.
`Cómo funciona →` / `How it works →` — clear.

Both fine. The closing CTA ("Los benchmarks sirven / Lo que importa es
producción") is a Helmcode pitch and is appropriately placed at the end.

---

## Things that are good and should not be touched

- The five-Monday verb + question pairs. The strongest copy on the page.
- *"Tres modelos que el benchmark no puede separar."* States a statistical caveat
  in seven words with no jargon.
- *"Solo un rango de precios, no una comparación de calidad."*
- *"Ninguna entra en el Monday Score, y no existe una puntuación de eficiencia."*
- *"Léelo por filas, no por columnas"* — honest, though it hints at a layout
  problem (see `ux-audit.md` §9).
- The provisional definition's wording (its placement is the issue).
