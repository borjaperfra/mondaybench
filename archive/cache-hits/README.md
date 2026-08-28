# Discarded: gateway cache hits, not independent runs

These `run-003.json` files are byte-identical in `response` to the `run-002.json`
of the same model, and returned in under ~1.2 seconds against 30-140 seconds for
a real generation.

They are gateway cache hits. Both Helmcode and NaN cache a response for an
identical prompt, so the second of two back-to-back requests was served from
store rather than generated.

A cached duplicate is not a second sample. Counting one would deflate `run_range`
and the standard deviation to zero for that pair, and the entire point of three
official runs is to measure exactly that variance.

Kept rather than deleted, as evidence for the defect. The fix is
`extra_body: {caching: false}` in `models.yaml`, which suppresses the cache
without altering a single byte of the prompt - the hash stays `ed4d7beb`.
Run qualification now also rejects any run whose response duplicates another run
of the same model, so this cannot silently recur.
