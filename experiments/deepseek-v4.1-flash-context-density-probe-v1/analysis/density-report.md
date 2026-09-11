# deepseek-v4.1-flash-context-density-probe-v1 - phase 1c report

Answer key `16:00`, identical in all three levels. Baseline only - no treatment was sent.
Not a MondayBench run.

## Calls

- slots: 15
- attempted: 15
- infrastructure_failures: 0
- retries_total: 0
- api_attempts: 15

## Density curve

| density | prompt bytes | prompt tokens | success | rate | reasoning median | latency median ms |
| --- | --- | --- | --- | --- | --- | --- |
| compact | 2341 | [558] | 3/5 | 0.6 | 2562.0 | 13792.0 |
| medium | 10105 | [1840] | 4/5 | 0.8 | 11660.0 | 81997.4 |
| dense | 21297 | [3939] | 4/5 | 0.8 | 11261.5 | 80039.8 |

## Outcomes, never merged

| density | CORRECT | INCORRECT | UNPARSEABLE | BUDGET_EXHAUSTED | infra failures | wrong answers given |
| --- | --- | --- | --- | --- | --- | --- |
| compact | 3 | 0 | 0 | 2 | 0 | [] |
| medium | 4 | 0 | 0 | 1 | 0 | [] |
| dense | 4 | 0 | 0 | 1 | 0 | [] |

## Deltas

| step | success rate delta | reasoning median delta | latency median delta ms | budget exhausted delta |
| --- | --- | --- | --- | --- |
| compact -> medium | 20.0 pp | 9098.0 | 68205.4 | -1 |
| medium -> dense | 0.0 pp | -398.5 | -1957.6 | 0 |
| compact -> dense | 20.0 pp | 8699.5 | 66247.8 | -1 |

## reasoning_tokens (secondary)

| stat | compact | medium | dense |
| --- | --- | --- | --- |
| n | 3 | 4 | 4 |
| min | 2177.0 | 10546.0 | 9870.0 |
| p25 | 2369.5 | 11377.8 | 10485.0 |
| median | 2562.0 | 11660.0 | 11261.5 |
| p75 | 2891.5 | 12386.8 | 11944.8 |
| max | 3221.0 | 14552.0 | 12280.0 |
| mean | 2653.3 | 12104.5 | 11168.2 |
| stdev | 528.0 | 1714.1 | 1094.2 |

## total latency ms (secondary)

| stat | compact | medium | dense |
| --- | --- | --- | --- |
| n | 3 | 4 | 4 |
| min | 12949.9 | 74247.7 | 67665.2 |
| p25 | 13371.0 | 80027.1 | 74401.8 |
| median | 13792.0 | 81997.4 | 80039.8 |
| p75 | 15384.5 | 85714.1 | 84515.5 |
| max | 16977.1 | 96732.7 | 87765.8 |
| mean | 14573.0 | 83743.8 | 78877.6 |
| stdev | 2124.2 | 9398.4 | 8764.2 |

## TTFA ms (secondary)

| stat | compact | medium | dense |
| --- | --- | --- | --- |
| n | 3 | 4 | 4 |
| min | 12365.5 | 72675.7 | 66189.7 |
| p25 | 12798.7 | 78201.4 | 73097.0 |
| median | 13231.9 | 80189.9 | 78649.6 |
| p75 | 14871.0 | 83879.3 | 82929.1 |
| max | 16510.1 | 94507.9 | 86016.9 |
| mean | 14035.8 | 81890.8 | 77376.4 |
| stdev | 2186.1 | 9127.6 | 8644.3 |

## output_tokens (secondary)

| stat | compact | medium | dense |
| --- | --- | --- | --- |
| n | 3 | 4 | 4 |
| min | 2300.0 | 10681.0 | 9918.0 |
| p25 | 2483.5 | 11503.8 | 10518.0 |
| median | 2667.0 | 11779.5 | 11320.0 |
| p75 | 3006.5 | 12504.8 | 12038.2 |
| max | 3346.0 | 14676.0 | 12387.0 |
| mean | 2771.0 | 12229.0 | 11236.2 |
| stdev | 530.7 | 1711.6 | 1125.6 |

## Reasoning delivery

- compact: 3 observed (100.0%)
- medium: 4 observed (100.0%)
- dense: 4 observed (100.0%)

## prompt_tokens against prompt bytes

| level | bytes | tokens observed | varies within level | bytes/token |
| --- | --- | --- | --- | --- |
| compact | 2341 | [558] | False | 4.2 |
| medium | 10105 | [1840] | False | 5.49 |
| dense | 21297 | [3939] | False | 5.41 |

- varies for byte-identical input within any level: **False**
- each level's prompt is byte-identical across its samples, so any spread within a level is the accounting behaviour first seen in phase 1a. Observable behaviour only; nothing here establishes anything about the provider's internals.

## Degradation assessment

- success_rate_falls_with_density: **False**
- monotone_fall: **False**
- latency_rises_with_density: **True**
- reasoning_tokens_rise_with_density: **True**
- budget_exhaustions_appear_with_density: **False**
- variability_rises_with_density: **True**
- reasoning_delivery_changes: **False**
- n=5 per level. A single sample moves a rate by 20 points, so the shape of this curve is a direction to investigate, not an estimate. No causal claim is made from reasoning tokens.

- H1 (reasoning deficit): argued against, not by this phase alone but with phase 1b's 24/24 on compact problems plus whatever compact scores here
- H2 (constraint persistence under context): supported only if compact stays high while a denser level falls

## Decision gate

- compact 0.6, medium 0.8, dense 0.8
- candidate levels in the 20-80% band: ['medium', 'dense']
- cases matched: ['CASE 1 (compact below 80%)', 'CASE 4 (the only failures are budget exhaustion)']
- first match in my test order: **CASE 1** (first match in my implementation's test order; the specification did not fix a precedence)
- **outcome: STOP - compact is below 80%, so the instrument probably raised the underlying logical difficulty rather than isolating context density. Degradation cannot be attributed to density.**
- NOTE: CASE 1 reads a low compact score as the instrument having raised the logical difficulty. That reading requires wrong answers, and there were 0 incorrect and 0 unparseable responses in the whole run. Where CASE 4 also holds, it is the better description of what happened. Both recommend STOP, so nothing about the outcome turns on which is quoted.
- **recommendation: STOP**
- treatment executed: False; max executed: False
- no treatment is run by this script under any outcome. baseline-vs-high is phase 1d and needs explicit authorisation.
