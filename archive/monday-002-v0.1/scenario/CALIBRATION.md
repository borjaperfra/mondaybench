# Calibration plan — MondayBench #002

## Goal
Add difficulty through new reasoning, not just more context.

Primary capabilities:
- temporal supersession
- current-state reconstruction
- dependency/blocker reasoning
- changing ownership
- genuine unresolved conflicts
- business-data reconciliation

## First pass
Run 1 calibration run each on:
- #001 leader
- another frontier model
- one mid-tier model
- one smaller/faster model

Inspect:
1. criteria everyone passes;
2. criteria everyone fails;
3. ambiguity in ground truth;
4. judge consistency;
5. double-counting;
6. penalty conservatism;
7. whether simple chronological summary can score too highly;
8. whether `accounts.csv` is actually required for full data credit;
9. whether Orion rewards refusing to guess;
10. whether dependency scoring distinguishes partial from correct planning.

## Headroom heuristic
If the best model repeatedly scores ~95–100, inspect saturation before freezing.

Desired rough calibration shape only:
- frontier: 80–90
- good: 65–85
- smaller/older: 40–70

Do not tune to force rankings.

## Anti-gaming
"Check everything", "verify all statuses", or "follow up with everyone" must not score highly.
Full credit requires committing where evidence is sufficient and reserving uncertainty for genuinely unresolved facts.

## Freeze
Only after calibration:
- freeze scenario/prompt/ground truth/rubric;
- compute exact rendered-prompt hash;
- freeze evaluator separately;
- archive calibration runs;
- run 3 official runs/model.
