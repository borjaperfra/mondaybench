# Astra challenger preflight — generation pending

Declared setting: **Astra — reasoning effort: medium (highest available)**. The user's latest instruction supersedes MAX in the continuation attachment. Medium is intentional and is not a qualification issue.

## Generation contract

PASS: frozen scenario artifacts, canonical rendered inputs, system prompt, temperature=0, omitted top_p, caching=false, unchanged scenario ceilings, two-message stateless construction, no tools, and harness semantic compatibility.

Suite v1.0 digest: `c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80`.

Frozen config group digest: `204ea2c5ebcdef8c3a04129319414ae8bdf9e75882a21bc901205c188036f9c2`. Current mutable config files differ as permitted by release policy; the canonical effective generation defaults are preserved in the offline request check.

| Scenario | Input bytes | Sources | Ceiling | Rendered SHA-256 |
|---|---:|---:|---:|---|
| monday-001 | 11664 | 5 | 32000 | ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398 |
| monday-002 | 8786 | 9 | 32000 | 740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8 |
| monday-003 | 13009 | 6 | 32000 | aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f |
| monday-004 | 24181 | 8 | 96000 | 3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99 |
| monday-005 | 19102 | 8 | 131072 | 532cd464a9b75045f808886c44e667237d6fd1b947826510643b9f8bcc30059a |

## Provider blocker

NO-GO: no authenticated Astra route and exact model ID have been verified. HELMCODE_BASE_URL / HELMCODE_API_KEY and NAN_BASE_URL / NAN_API_KEY are configured. Both GET model catalogs returned HTTP 200; neither lists Astra. Initial sandbox catalog queries encountered ConnectError; the successful queries used approved network escalation. These are catalog requests, not benchmark generations or generation retries.

No ASTRA or OPENAI model endpoint/credential variables were found in the process environment or repository .env. The app's model selector is not evidence of an API route that accepts the frozen benchmark contract. No inference requests were made.

To resume, supply a provider's exact Astra API model ID, authenticated endpoint and API format. Suggested new configuration variable names (not existing integrations): ASTRA_BASE_URL, ASTRA_API_KEY, ASTRA_MODEL_ID. Set the secret locally rather than posting it in chat. If an existing configured provider exposes Astra under an alias, identify that exact alias and provider instead.

Streaming, usage, reasoning token accounting, finish reason, request/response IDs, latency, TTFT and TTFA for Astra remain UNOBSERVABLE pending route verification. Medium is fixed as the requested reasoning effort; wire support remains to be verified with the provider. The full executable configuration cannot be frozen until the route is known.

Expected battery: 15 (three per scenario). Attempted generations: 0. Valid outputs: 0. Generation failures/retries/truncations: 0. No scores, evaluation, blind judge pack or provenance mapping exist yet. No existing tracked artifact changed; no commit or publication performed.

Evidence: preflight/generation-contract.json, preflight/provider-discovery.json, preflight/harness-drift.md. scripts/preflight.py can reproduce the offline checks; --discover queries provider catalogs only.
