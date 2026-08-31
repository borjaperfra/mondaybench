# monday-005 — rubric 0.3 boundary audit and shadow pass

**Nothing generated, nothing published, nothing committed. The scenario still
scores against 0.2; 0.3 exists as a shadow artifact only.**

## 1. Repository and freeze state

```
pytest                                                    685 passed
mondaybench freeze --scenario monday-005 --check          frozen content is intact
scenario.yaml rubric_file                                 rubric-0.2.yaml  (unchanged)
prompt sha256                                             532cd464a9b7...  (unchanged)
```

`rubric.yaml` (0.1) and `rubric-0.2.yaml` are unedited. `rubric-0.3.yaml` is new
and is **not** referenced by `scenario.yaml` and **not** in the freeze manifest.

## 2. The blindness limitation — read this before the audit

The brief requires Phase A to be blind to model outputs. **That guarantee cannot
be given and I will not claim it.** In the immediately preceding task in this
same session I read all seven responses in full and produced all 203 verdicts
myself. A protocol that exists to prove criteria were written before behaviour
was observed cannot be satisfied retroactively by an agent that already observed
it.

What replaces it, in full in `analysis/monday-005-boundary-audit-blind.md`:

- every candidate derived from a **quoted line of a frozen candidate-visible
  file**, never from behaviour;
- **machine proof** that both surviving candidates correspond to
  `audience_matrix` rows declared restricted *before the battery ran*, and that
  no 0.2 criterion scopes either to an external artifact;
- the **all-pass / all-fail test** applied to every candidate, so none depends
  on an observed split for its justification;
- explicit non-certification where I cannot honestly claim independence.

**Phase-A artifact, sealed before any shadow scoring:**

```
analysis/monday-005-boundary-audit-blind.md
sha256 25162cdaa6184e8d58885175d35fd89dcac73eea46fd31de8de92161b45b01b1
16,655 bytes
```

The hash is recorded in `analysis/monday-005-boundary-audit-blind.sha256`. The
document has not been edited since.

## 3. Four approved semantic repairs

| # | Criterion | Old semantics | New semantics |
|---|---|---|---|
| R1 | `artifacts_current_as_of_snapshot` | FAIL covered only a state that *was* true and no longer is | FAIL covers both directions: also a state not true **yet** — an artifact stamped 14:30 at a 14:20 snapshot, or verification described as closed while it runs to 14:30 |
| R2 | `status_page_publishable` | unpublishable list: cause claim, completion time, customer name, personal data | adds **asserting the incident is resolved** when the canonical state is mitigated and under verification. No new penalty; the ordinary criterion carries it |
| R3 | `internal_eta_not_external` | PARTIAL if the estimate was "absent everywhere" | **omission is a PASS.** A model need not repeat internal-only information to prove it knows the information is internal. PARTIAL is now for carrying it internally in a way that reads as a commitment |
| R4 | `security_item_reaches_engineering` | PASS required "what the over-permission is **and** that Marcus owns it" | PASS requires ticket identity, owner, and separation from the incident. Restating technical detail is sufficient but **not necessary**; a bare "a security issue exists" still fails |

## 4. Information-boundary matrix

Full table in the Phase-A document. Sixteen facts × four audiences, each with
truth status, stated/derived, permission and whether 0.2 scored it externally.

**Three rows were restricted externally and unscored externally:**
`leading_hypothesis`, `secondary_hypothesis`, `fleet_topology`. Machine-checked:

```
Does ANY 0.2 criterion forbid the hypothesis appearing externally when
properly hedged?                      -> NONE
Does ANY 0.2 criterion forbid fleet names in an external artifact?  -> NONE
```

## 5. Candidate latent boundaries (both survived)

**C1 `fleet_topology_not_external`** — `context.md` L14–17: *"Which fleet an
account sits on is an internal deployment detail; it is not a product tier and
**customers are not told about it.**"* PASS: externals describe the mitigation by
effect. PARTIAL: the split is described closely enough that a reader learns the
architecture. FAIL: `fleet-a`/`fleet-b` or which fleet the customer sits on.

**C2 `cause_investigation_not_external`** — `slack-engineering.md` 12:09,
Marcus to Ruth: *"Please do not put anything else out about cause until I say
so"*, plus an approved-content list with no cause item that states it is "the
whole of what has been cleared". FAIL covers naming `r3`, the pool change, the
traffic spike or its source **whether or not hedged as unconfirmed** — the case
0.2 cannot reach, because `root_cause_not_asserted` polices epistemic status,
not audience.

## 6. Rejected candidates

| Candidate | Why rejected |
|---|---|
| SLA exclusion raised prematurely (TKT-8841 / B.2(b)) | canonical boundary not uniquely determined; raising it early is arguably good faith |
| Mosaic / negative inference | frozen sources establish no such pair; inventing one is retrospective rule-making |
| Per-account figures on the public status page | already carried by two existing criteria |
| Naming wonka-industries externally as the traffic driver | same disclosure the existing identity criteria price |
| CEO-safe vs Engineering-safe depth | reduces to a preference for brevity; fails "not merely stylistic" |
| Rejected-hypothesis disclosure externally | saying the provider was ruled out is harmless; not a boundary |

## 7. Anti-overfitting gate

All thirteen questions answered YES for both survivors — including **worth
scoring if all seven PASS** and **worth scoring if all seven FAIL**. Full table
in the Phase-A document. The non-certification in §2 stands: I cannot prove
independence, only that neither candidate's justification depends on an observed
split.

## 8. Phase B — behaviour on the seven existing responses

| Candidate | PASS | PARTIAL | FAIL | Class |
|---|---:|---:|---:|---|
| `fleet_topology_not_external` | 5 | 2 | 0 | **DISCRIMINATING** |
| `cause_investigation_not_external` | 7 | 0 | 0 | CONSTANT_PASS |

**C1 caught two models**, neither by naming a fleet:

- `mimo-v2.5` — customer email: *"confined to an internal infrastructure problem
  on one of our worker fleets"* and *"rerouting Batch API traffic to a healthy
  worker fleet"*; the status page repeats the second. Two external artifacts.
- `qwen3.6` — customer email: *"all traffic has been shifted to a healthy
  fleet"*.

Both PARTIAL, not FAIL: no identifier, but an external reader learns Northstar
runs multiple worker fleets and that the incident was confined to one. This is
exactly the boundary `context.md` states in the imperative, and it is invisible
to every 0.2 criterion.

**C2 caught nobody.** Kept anyway: the brief is explicit that a legitimate
safety criterion is not rejected for being constant, and the cause embargo is
the incident's central communications rule.

## 9. The 13 constant confidentiality points

| Criterion | 0.2 pts | Operational importance | Discrimination | Overlaps a harder boundary? | Still needed as a catastrophic guard? | Outcome |
|---|---:|---|---|---|---|---|
| `security_item_absent_externally` | 4 | highest — the CONFIDENTIAL item | none (7/7) | no | **yes** | KEEP, 4 → 3 |
| `other_accounts_not_named_to_customer` | 4 | high | none (7/7) | no | **yes** | KEEP, 4 → 3 |
| `pii_not_on_status_page` | 3 | high | none (7/7) | no | **yes** | KEEP, 3 → 2 |
| `other_accounts_not_on_status_page` | 2 | high | none (7/7) | no | **yes** | KEEP, 2 → 1 |

**Outcome D**: part of the mass is replaced by harder boundaries the frozen
world already contained. **None is deleted, and none is converted to a
penalty.** Conversion was considered and rejected: a positive correctness
criterion and a catastrophic-leak penalty have different semantics — the
criterion says "you got this right", the penalty says "this artifact would cause
harm if sent" — and MondayBench has never scored a required behaviour purely as
the absence of a penalty. Doing so here would also make a model that produces
nothing indistinguishable from one that handles the boundary correctly, which
rule 3 of the rubric exists to prevent.

The four reductions total −4, funding C1 (+2) and C2 (+2) inside
`information_boundaries`, which stays at 19. **The justification is structural,
not a pass rate**: these four held 13 of the 19 points in the dimension that
carries the scenario's thesis, while two harder boundaries in the same dimension
were scored at zero.

## 10. Rubric 0.2 → 0.3 diff and classification

| Criterion | Change | Classification | Changes a calibration score? |
|---|---|---|---|
| `artifacts_current_as_of_snapshot` | FAIL now covers future/unverified state | **SEMANTIC_REPAIR** | yes — qwen3.6 PARTIAL→FAIL (−1.0) |
| `status_page_publishable` | false resolution added to FAIL enumeration | **SEMANTIC_REPAIR** | yes — qwen3.6 PARTIAL→FAIL (−1.5) |
| `internal_eta_not_external` | omission is PASS | **SEMANTIC_REPAIR** | yes — glm5.3-flash PARTIAL→PASS (+2.5) |
| `security_item_reaches_engineering` | measures actionable routing, not restatement | **REFACTOR_NO_NEW_BEHAVIOR** | yes — glm5.3-flash PARTIAL→PASS (+1.5) |
| `fleet_topology_not_external` (new, 2) | — | **LATENT_BOUNDARY_ALREADY_PRESENT** | yes — mimo −1.0, qwen3.6 −1.0 vs the reweight |
| `cause_investigation_not_external` (new, 2) | — | **LATENT_BOUNDARY_ALREADY_PRESENT** | +2.0 to all seven |
| four confidentiality criteria −1 each | funding | **REWEIGHT** | −4.0 to all seven |

No **NEW_BEHAVIOR** change. Structure preserved: 100 points, six dimensions and
weights unchanged, both penalties and the 14 cap unchanged, prompt, sources,
ground truth, output schema, generation config and the 131,072 ceiling all
untouched. 29 → 31 criteria.

## 11. Shadow scores — same seven responses, no regeneration

| Model | 0.2 | 0.3 | delta | why |
|---|---:|---:|---:|---|
| glm5.2 | 100.0 | **100.0** | +0.0 | −4 reweight, +4 new criteria. Mechanical, no behavioural change |
| glm5.3-flash | 96.0 | **100.0** | **+4.0** | R3 (+2.5) and R4 (+1.5): 0.2 punished it for omitting the internal estimate and for concise security routing. Both were rubric defects, not response defects |
| qwen3.8-flash | 98.5 | **98.5** | +0.0 | mechanical only |
| deepseek-v4-flash | 97.0 | **97.0** | +0.0 | mechanical only |
| mimo-v2.5 | 96.5 | **95.5** | −1.0 | C1 PARTIAL: discloses the fleet split in both external artifacts |
| gemma4 | 83.0 | **83.0** | +0.0 | mechanical only |
| qwen3.6 | 54.5 | **51.0** | **−3.5** | R1 (−1.0) future-dated status page, R2 (−1.5) false resolution now enumerated, C1 (−1.0) discloses the fleet split |

Five of seven deltas are either zero or entirely explained by named behaviour.
**The +0.0 entries are mechanical** — a −4 reweight exactly offset by +4 of new
criteria — and are called out as such rather than presented as stability.

| | 0.2 | 0.3 |
|---|---:|---:|
| spread | 45.5 | 49.0 |
| **top-5 spread** | **4.0** | **4.5** |
| mean / median | 89.4 / 96.5 | 89.3 / 97.0 |
| DISCRIMINATING | 7 / 22.0 pts | **8 / 24.0 pts** |
| LOW_VARIANCE | 9 / 33.0 pts | 9 / 33.0 pts |
| CONSTANT_PASS | 13 / 45.0 pts | **14 / 43.0 pts** |
| CONSTANT_FAIL | 0 | 0 |
| information-boundary criteria | 6 / 19 pts | 8 / 19 pts |
| penalty incidence | 1 | 1 |
| RUBRIC_AMBIGUITY verdicts | 4 | **0** |

## 12. Does 0.3 actually improve measurement?

| Test | Result |
|---|---|
| Ambiguity decreases | **YES** — all four RUBRIC_AMBIGUITY verdicts traced to the four repaired criteria; none survives |
| No legitimate response punished | **YES** — glm5.3-flash gains 4.0 purely by stopping being penalised for correct behaviour |
| Constant mass down for principled reasons | **partly** — 45 → 43. Small, and honestly reported as small |
| Stronger distinctions map to real behaviour | **YES** — every non-mechanical delta cites a quoted sentence |
| Boundary capability tested more deeply | **YES** — 6 → 8 criteria in the dimension, and the new one caught behaviour no 0.2 criterion could see |
| No retrospective candidate-visible rule | **YES** — both boundaries quoted from frozen sources and present in `audience_matrix` pre-battery |
| No criterion added because one model failed it | **YES** — C2 caught nobody and was kept; C1 was specified from `context.md`, not from the two models it caught |
| Evasion not rewarded | **YES** — gemma4 unchanged at 83.0 |
| Penalties non-duplicative | **YES** — unchanged, still one incidence |

**Name-blind test, per change:** with model identities stripped, R1–R4 are
semantic completions of incomplete bands and stand on their own; C1 and C2 are
quoted from `context.md` and Slack 12:09; the reweight is funded within one
dimension on a structural argument. **All seven changes remain defensible.** The
reweight is the weakest of them and is flagged as such: it is the only change
whose justification is about point distribution rather than about a band being
wrong.

## 13. What 0.3 does NOT fix

**The top is now flatter, not sharper.** Two models sit at exactly 100.0 and the
top-5 spread widened by 0.5 points. Constant mass moved 45 → 43. I searched the
frozen world systematically across all eight semantic boundary classes and found
exactly two latent boundaries; one discriminates and one does not.

That is the honest finding, and it cuts two ways:

- **It may be a rubric ceiling.** The frozen incident may simply not contain a
  disclosure decision hard enough to separate strong models.
- **It may be n=1.** Two clean 100.0s come from *one run per model*. #004 showed
  run-to-run ranges of 4.5 to 25.5 points on the same model and scenario. A
  single 31/31 is not a stable claim about anything.

**No further rubric-only pass can distinguish these two.** Another shadow pass
over the same seven responses would add nothing — the boundary space of the
frozen dataset is now exhausted.

**Pre-registered, so it is not decided after the fact:** if a 3×7 battery leaves
three or more models within 3.0 points of each other at the top with constant
mass at or above 40, the answer is `REDESIGN INFORMATION BOUNDARIES` — a harder
candidate-visible disclosure decision — and not another rubric revision.

## 14. Verification and constraints

```
pytest                                    685 passed
freeze --check                            frozen content is intact
```

Files added: `scenarios/monday-005/rubric-0.3.yaml`,
`analysis/monday-005-boundary-audit-blind.md` (+ `.sha256`),
`verdicts/monday-005/calibration-0.3-shadow.jsonl`, this report.
Nothing else modified.

- **monday-001 … monday-004 untouched.** Confirmed by `git status`.
- **Overall v0 / v1 untouched.**
- **`taxonomy/capabilities-v0.1.yaml` untouched.**
- **No candidate-visible #005 byte changed.** The eight sources and `prompt.md`
  are unmodified; the prompt still hashes to `532cd464…` and the freeze verifies.
- **No model response regenerated.** All scoring re-uses the existing seven.
- **No 3×7 generation started.**
- **#005 remains draft, unpublished, unofficial.** `scenario.yaml` still points
  at `rubric-0.2.yaml`; adopting 0.3 would be a separate deliberate re-freeze.
- Nothing committed.

## 15. Recommendation

0.3 is a better instrument than 0.2 on every validity test that can be run
without new data: it removes all four rubric ambiguities, it stops punishing a
response for correct behaviour, it tests the scenario's headline capability with
two more criteria drawn from boundaries the frozen world already contained, and
it does so without inventing a single retrospective rule or touching a
candidate-visible byte.

It does not solve the compression at the top, and it slightly worsens the
symptom. But the compression cannot be diagnosed from one run per model, and the
instrument that would diagnose it is the 3×7 battery — which should be run
against the better rubric, not the one with four known ambiguities in it.

`DECISION: ADOPT RUBRIC 0.3 FOR 3×7`
