# Change Evidence

Change Evidence is an experimental Clojure library and language-neutral model for
describing source-code changes with structured evidence, attributed claims,
explicit gaps, attestations, and machine-checkable validation.

## Status

This repository is at the design stage. The canonical model is drafted; the
adapter contract is still being decided. Documents labelled as briefings or
proposals are inputs to that decision, not stable public specifications.

## Start here

1. [`canonical-model.md`](docs/change-evidence/canonical-model.md) — the proposed
   evidence, claim, gap, attestation, and validation model.
2. [`adapter-protocol-briefing.md`](docs/change-evidence/adapter-protocol-briefing.md)
   — inherited constraints, provisional interfaces, and open decisions.
3. [`theoretical-foundations.md`](docs/change-evidence/theoretical-foundations.md)
   — progressive background reading.
4. [`PROVENANCE.md`](docs/change-evidence/PROVENANCE.md) — where the imported
   research and fixtures came from.

Research, captured outputs, and fixtures remain under
`docs/change-evidence/` so citations from the original documents continue to
resolve.

## Development

The repository contains a dependency-free Clojure skeleton while the public API
and runtime strategy are being designed.

```sh
clojure -X:test
```

No license has been selected yet.

