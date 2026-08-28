# qwen3.8-flash — runs 003, 004, 005 and 006 are INVALIDATED

Four consecutive attempts refused by `qualify_run` as
**REASONING_NOT_DELIVERED**. They are kept, not deleted: a serving defect that
gets deleted cannot be counted later. None of them contributes to any published
statistic.

| | run-001 | run-002 | run-003 | run-004 | run-005 | run-006 |
|---|---:|---:|---:|---:|---:|---:|
| input tokens | 3,791 | 3,791 | **3,755** | **3,755** | **3,755** | **3,755** |
| reasoning tokens | 23,510 | 46,603 | **0** | **0** | **0** | **0** |
| output tokens | 25,761 | 49,968 | 1,685 | 1,638 | 1,986 | 1,697 |
| TTFA | 250.0s | 454.1s | **2.1s** | **3.8s** | **1.7s** | **2.7s** |
| qualifies | yes | yes | no | no | no | no |

## Why this is a serving defect and not a shorter answer

The candidate prompt is frozen at
`aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f` and did not
change between any of these five requests. **The input-token count moved anyway**,
from 3,791 to 3,755, and then stayed there. A byte-identical prompt that
tokenises differently is a different serving path, not a different answer.

Two further indicators agree:

- **Reasoning tokens went to exactly zero** on a model whose `capabilities`
  declare reasoning and whose first two runs spent 23,510 and 46,603.
- **Time to first *answer* token collapsed onto time to first token.** Runs 001
  and 002 show a 250-second and a 454-second thinking phase before the first
  answer token. Runs 003–005 show none at all.

This is the same defect recorded for monday-002/qwen3.8-flash and for the
monday-003 v0.1 calibration, where two of three attempts failed the same way.
The difference here is that it is **persistent rather than intermittent**: four
attempts in a row over roughly forty minutes, and the input-token count has not
returned to 3,791 once.

## Consequence

The official battery for monday-003 is incomplete. qwen3.8-flash has two
qualifying runs against a required three, so `publish` refuses the whole
leaderboard rather than ranking six models beside one measured differently.
That refusal is correct and was not overridden.
