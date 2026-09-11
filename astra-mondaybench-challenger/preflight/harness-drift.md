# Harness semantic comparison

Baseline: git commit `bea927f`. Each of the ten baseline file contents was hashed and matched against the v1.0 release index before comparison with HEAD.

Classification is relative to candidate generation, not evaluator generation.

| Changed file | Class | Effect |
|---|---|---|
| mondaybench/capabilities.py | A | Selects versioned evaluation directories; outside generation. |
| mondaybench/cli.py | A | Adds suite-aware reporting, migration, and judge-contract inspection commands; candidate generation commands unchanged. |
| mondaybench/cli_official.py | A | Adds suite selection to publication and arithmetic checks; outside generation. |
| mondaybench/config.py | A | Adds external judge-instruction resolution helpers; ModelConfig and model loading unchanged. |
| mondaybench/evaluator.py | A, B | Versioned evaluation paths, judge contract selection and provenance fields; outside candidate generation. |
| mondaybench/judge.py | A | Changes evaluator instruction overrides and penalty schema selection; never called for candidate generation. |
| mondaybench/leaderboard.py | A, B | Versioned paths, comparison fingerprints, suite metadata, CSV LF endings; outside generation. |
| mondaybench/overall.py | A, B | Suite selection and metadata, CSV LF endings; outside generation. |
| mondaybench/schemas.py | B | Optional judge/evaluation metadata; BenchmarkRun generation schema unchanged. |
| mondaybench/suite.py | A | Separates mutable pricing files and handles groups absent from older releases; no candidate request changes. |

No C (provider-support) or D (candidate generation-contract) change was found in these ten files. The candidate runner, prompt builder, scenario loader, adapters, reasoning classifier and qualification implementation match the frozen v1.0 file hashes exactly. No compatibility rewrite is needed.

All five rendered prompts match the release manifest. Generation-only rendering uses frozen scenario metadata, template and ordered sources, without loading rubric or ground-truth content. Exact byte lengths, full hashes, source lists and request keys are in generation-contract.json.

The proposed request has two fresh messages: the fixed system prompt and rendered user content. Parameters are temperature=0, scenario-specific frozen max_tokens ceiling, stream=true, stream_options.include_usage=true, caching=false, and the user's declared reasoning_effort=medium. top_p and tools are omitted. This is an offline payload check, not proof that an unresolved Astra provider accepts those parameters.

Existing preprocessing is preserved: UTF-8 text reads with universal newlines; source boundary strip; placeholder substitution or fixed heading/separator appending. No additional normalization or model-specific instructions.

Tests: 86 passed across test_prompt_builder.py, test_openai_compatible.py, and test_reasoning_qualification.py. Pytest reported a cache write permission warning; no tests failed. No evaluation was performed.
