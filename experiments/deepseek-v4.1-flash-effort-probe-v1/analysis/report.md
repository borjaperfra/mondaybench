# deepseek-v4.1-flash-effort-probe-v1 - phase 1 report

Prompt sha256 `672c55f3a1a2da583a43475e6b8f8f1d7a393412fb2dc8ad79bb8738c399ada7`, correct answer `15:00`, scorer: strict-distinct-times + last-time robustness check, v1.
Not a MondayBench run. No battery, leaderboard, evaluation or release was read or written.

## Calls

- phase1_slots: 60
- phase1_ok: 60
- phase1_failed: 0
- retries_total: 0
- sentinel_calls: 5
- total_api_calls: 65

## baseline vs high

| metric | baseline | high |
| --- | --- | --- |
| slots | 30 | 30 |
| completed (OK) | 30 | 30 |
| failed | 0 | 0 |
| CORRECT (strict) | 30 | 30 |
| INCORRECT (strict) | 0 | 0 |
| UNPARSEABLE (strict) | 0 | 0 |
| success rate (strict) | 1.0 | 1.0 |
| success rate (last-time check) | 1.0 | 1.0 |
| reasoning delivery observed | 30/30 (100.0%) | 30/30 (100.0%) |
| reasoning_tokens reported | 30 | 30 |
| reasoning_tokens absent (null) | 0 | 0 |
| reasoning_tokens reported as 0 | 0 | 0 |

## reasoning_tokens

| stat | baseline | high |
| --- | --- | --- |
| n | 30 | 30 |
| mean | 1343.2 | 1041.1 |
| median | 973.0 | 474.0 |
| min | 253.0 | 226.0 |
| p10 | 350.9 | 300.6 |
| p25 | 368.5 | 367.2 |
| p75 | 1441.2 | 846.2 |
| p90 | 2956.2 | 1306.4 |
| max | 5707.0 | 10631.0 |
| stdev | 1423.5 | 1951.3 |

## output_tokens

| stat | baseline | high |
| --- | --- | --- |
| n | 30 | 30 |
| mean | 1500.2 | 1132.9 |
| median | 1123.5 | 501.5 |
| min | 292.0 | 264.0 |
| p10 | 354.9 | 370.0 |
| p25 | 392.2 | 396.2 |
| p75 | 1677.2 | 964.0 |
| p90 | 3279.3 | 1419.3 |
| max | 6213.0 | 11262.0 |
| stdev | 1554.9 | 2063.0 |

## ttfa_ms

| stat | baseline | high |
| --- | --- | --- |
| n | 30 | 30 |
| mean | 11905.7 | 9183.9 |
| median | 8077.4 | 4863.2 |
| min | 2834.9 | 3087.4 |
| p10 | 2994.5 | 3718.3 |
| p25 | 3963.1 | 4180.2 |
| p75 | 15170.1 | 7483.0 |
| p90 | 27075.7 | 10580.0 |
| max | 48225.1 | 84099.7 |
| stdev | 11283.3 | 15137.8 |

## total_latency_ms

| stat | baseline | high |
| --- | --- | --- |
| n | 30 | 30 |
| mean | 12053.3 | 9303.6 |
| median | 8186.0 | 4969.5 |
| min | 2838.9 | 3139.7 |
| p10 | 3084.6 | 3789.2 |
| p25 | 4078.8 | 4268.7 |
| p75 | 15339.0 | 7598.2 |
| p90 | 27393.2 | 10655.3 |
| max | 48804.5 | 85334.2 |
| stdev | 11426.2 | 15355.7 |

## reasoning_tokens distribution

| bin | baseline | high |
| --- | --- | --- |
| 0-249 | 0  | 1 # |
| 250-499 | 10 ########## | 14 ############## |
| 500-999 | 7 ####### | 9 ######### |
| 1000-1999 | 8 ######## | 4 #### |
| 2000-3999 | 2 ## | 0  |
| 4000-7999 | 3 ### | 1 # |
| 8000-15999 | 0  | 1 # |
| >=16000 | 0  | 0  |

Sorted values (nothing removed):

- baseline: [253, 288, 350, 351, 351, 353, 365, 367, 373, 479, 538, 638, 648, 685, 952, 994, 994, 1073, 1190, 1217, 1223, 1388, 1459, 1536, 1990, 2180, 2807, 4299, 5248, 5707]
- high: [226, 284, 297, 301, 326, 336, 344, 366, 371, 377, 387, 387, 406, 408, 436, 512, 520, 533, 554, 618, 665, 835, 850, 951, 1157, 1225, 1281, 1535, 4114, 10631]

## Comparisons

- success rate difference: 0.0 pp absolute, 0.0% relative

| quantity | point | 95% CI | includes 0 |
| --- | --- | --- | --- |
| median reasoning_tokens (high - baseline) | -499.0 | [-812.0, 5.5] | True |
| median total latency ms (high - baseline) | -3216.6 | [-7237.1, 687.3] | True |
| success rate (high - baseline) | 0.0 | [0.0, 0.0] | True |
| Cliff's delta, reasoning_tokens | -0.2733 | [-0.5556, 0.0134] | True |

Bootstrap: 10000 resamples, seed 424242, percentile method, no outliers removed.

| permutation test | observed | p (two-sided) |
| --- | --- | --- |
| median reasoning_tokens | -499.0 | 0.0253 |
| Cliff's delta reasoning_tokens | -0.2733 | 0.0725 |
| median total latency | -3216.6 | 0.041 |
| success rate | 0.0 | 1.0 |

## Tail sensitivity check (not a headline number)

- top 3 reasoning_tokens values dropped from each variant - is the shift carried by an extreme tail?
- baseline median 685.0, p25 366.0
- high median 408.0, p25 355.0
- median still higher: False; p25 still higher: False

## reasoning_tokens vs correctness

- **pooled**: CORRECT n=60 median=586.0
- **baseline**: CORRECT n=30 median=973.0
- **high**: CORRECT n=30 median=474.0

## Decision gate

- A (quality): success_rate(high) - success_rate(baseline) >= +10 pp -> 0.0 pp -> **NOT MET**
- B (compute): median higher False, p25 higher False, tail check False, Cliff's delta CI excludes 0 False -> **NOT MET**
- **outcome: STOP - no observable high-effort effect large enough to justify a MondayBench battery**
- max executed: False

## Input-token accounting (byte-identical input)

- distinct prompt_token counts: [72, 98, 151]
- byte-identical input was billed as 72, 98, 151 prompt tokens across the 60 samples, and the reasoning-token distribution differs sharply between those groups. The variants do not map one-to-one onto the groups, but neither are they independent of them.
- **consequence**: the baseline-vs-high reasoning-token comparison is confounded: a sample's prompt-token group predicts its reasoning tokens at least as well as its variant does. No causal reading of the variant difference is available from this data.

| prompt_tokens | n | baseline | high | reasoning median | reasoning p25 | reasoning p75 |
| --- | --- | --- | --- | --- | --- | --- |
| 72 | 21 | 21 | 0 | 1217.0 | 952.0 | 1990.0 |
| 98 | 17 | 9 | 8 | 377.0 | 353.0 | 533.0 |
| 151 | 22 | 0 | 22 | 516.0 | 338.0 | 925.8 |

## Limitations

- **byte-identical input was counted as 3 different prompt-token totals [72, 98, 151]**: the samples were not all answered under one accounting, and reasoning tokens differ by group, so the baseline/high difference cannot be attributed to reasoning_effort. See input_token_accounting.
- **success rate is saturated at 1.0 in both variants**: gate A could not have fired whatever reasoning_effort does. This prompt cannot discriminate quality, so 'no quality effect' is NOT established - it was not measurable. The zero-width bootstrap CI on the success-rate difference is an artefact of that ceiling, not precision.
- **the two procedures disagree on the median reasoning-token difference at the 5% threshold** (permutation p=0.0253, bootstrap 95% CI [-812.0, 5.5] (includes zero: True)): neither is treated as a finding. Four tests were run and no multiplicity correction was applied, so a single p-value near 0.05 is not evidence of an effect.
- **scope**: one prompt, one route, one model, one session, calls issued sequentially. Interleaving controls for slow backend drift, not for load at the moment of a call. Nothing here generalises to other prompts or to MondayBench scenarios.
- **observable behaviour only**: request-id shapes, token counters and stream events are descriptions of responses. They establish nothing about how the provider routes or serves a request internally.

## Sentinel: reasoning_effort="banana" (outside the statistics)

- n: 5
- n_ok: 5
- http_statuses: [200]
- request_id_shapes: {'chatcmpl-hex': 5}
- reasoning_tokens_field_present: 5
- reasoning_tokens_field_absent: 0
- reasoning_stream_observed_true: 0
- output_tokens: [6, 6, 6, 6, 6]
- total_latency_ms: [564.2, 6341.0, 526.1, 480.1, 481.7]
- scores_strict: ['INCORRECT', 'INCORRECT', 'INCORRECT', 'INCORRECT', 'INCORRECT']
- answers: ['17:00', '14:00', '14:00', '17:00', '17:00']
- in_statistics: False
- note: observable behaviour only; this says nothing about how the provider routes requests internally
