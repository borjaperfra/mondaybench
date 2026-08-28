# Judge re-evaluations — NOT PERFORMED

This directory is intentionally empty of evaluations.

The audit asked for 3 candidate responses x 5 independent re-evaluations = 15
audit evaluations, to separate judge variance from candidate variance.

**They were not run, and cannot be, under this project's rules.**

> Using an Anthropic API key or spending Anthropic API credits is prohibited on
> this project. All judging is done by Claude Code on the user's subscription.

The only route to *independent* judge samples is a fresh-context call to the
judge model. In-session re-judging by the same session that produced the
official labels is anchored - I already have the labels in context - and would
return a near-perfect agreement rate that measures nothing. A "range 0.0" from
that exercise would look like evidence and would not be.

What was measured instead, from official artefacts only, is **judge
consistency**: across all 21 official runs, does the same behaviour receive the
same label? For the 8 volatile criteria the answer is yes, with no exceptions
found. See section 4 of `../qwen-3.8-stability-report.md`.

Judge *stochastic variance* remains unmeasured. It stays unmeasured until there
is a way to sample the judge in fresh contexts without API spend.
