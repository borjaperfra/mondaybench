# Superseded calibration runs — prompt `e19d123c`

Generated against the scenario before the "You was present for the events they
missed" fix (see `scenarios/monday-001/CHANGELOG.md`). The current prompt hash is
`ed4d7beb…`, so these runs and their evaluations are **not comparable** with
anything produced afterwards and must never be aggregated with it.

Kept because they are the evidence behind four harness defects that calibration
found: the penalty judge with no access to the sources, the judge penalising its
own "minor" findings, the 4,000-token budget that silenced glm5.3-flash, and the
26x-inflated throughput figures.

The evaluations here also predate `rubric_version` and `prompt_fingerprint`, so
they carry neither field.
