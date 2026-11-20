# Change Evidence Adapter Protocol

**Status:** authoring shell; not a specification  
**Audience:** adapter authors, library implementers, and consumers of change
evidence

This document is intentionally incomplete. Its first sections are the conceptual
core to be written before schemas, bindings, and conformance machinery harden the
design. The [design briefing](adapter-protocol-briefing.md) records inherited
constraints, alternatives, and unresolved edge cases.

## 1. Purpose

<!--
In a few paragraphs: What problem does an adapter protocol solve? Why is a common
boundary needed instead of each evidence source exposing its native output?
Describe the useful result for a consumer, not the implementation mechanism.
-->

## 2. The core idea

<!--
State the design in its shortest convincing form. A useful test: after reading
only this section, can someone explain what an adapter contributes, what the core
library contributes, and what a consumer receives?
-->

## 3. Scope and non-goals

### In scope

<!-- What must independent adapters and consumers agree on? -->

### Out of scope

<!--
Name tempting responsibilities that belong elsewhere: semantic truth, human
judgement, authorization, UI, repository workflow, or a particular transport.
-->

## 4. Participants and responsibilities

<!--
Define the smallest set of roles needed to explain the system. Candidate roles
from the briefing are evidence adapter, optional enricher, composer/core, source
verifier, and consumer. Keep only roles that clarify a real boundary.
-->

## 5. The adapter boundary

<!--
Describe what crosses the boundary in each direction. Establish whether the
normative contract is a document exchange, an in-process interface, a process
protocol, or a layered combination. Avoid binding it to Clojure syntax here.
-->

### Inputs

### Outputs

### Adapter obligations

### Core obligations

## 6. Evidence production and composition

<!--
Explain one complete journey: a subject is identified, one or more adapters
observe it, evidence is composed, and a consumer receives a canonical result.
Address how optional enrichment relates to the required evidence floor.
-->

## 7. Guarantees and limits

### What conforming implementations guarantee

<!--
Start with the properties that make the protocol valuable: determinism,
traceability, stable identity, explicit completeness, and source verification.
-->

### What the protocol does not guarantee

<!--
Be explicit about semantic correctness and human judgement. A structurally valid
claim can still be false.
-->

## 8. A minimal worked example

<!--
Tell one small end-to-end story before defining every field. Prefer a one-file Git
change plus one optional enrichment fragment. Show what each participant knows and
what the consumer can verify.
-->

## 9. Core design decisions

<!--
Record only decisions that materially shape the preceding explanation. Begin with
interface style and fragment composition. Keep rejected alternatives and detailed
rationale in separate decision records rather than turning this specification into
a design diary.
-->

| Decision | Choice | Why it follows from the core idea |
|---|---|---|
| Normative adapter interface | _Open_ | |
| Whole evidence set or composable fragments | _Open_ | |
| Composition owner | _Open_ | |

## 10. Schematic specification to build from the core

The following sections should be filled in after Sections 1–9 establish the idea.
They turn the conceptual contract into an independently implementable protocol.

- Terminology and normative language
- Adapter manifest and capability declaration
- Request document
- Evidence-fragment schema
- Composition and ordering rules
- Canonical serialization and digest rules
- Completeness and gap representation
- Versioning and compatibility
- Structured errors and partial results
- Source-verification interface
- Security and resource limits
- Conformance requirements and test vectors
- Language bindings, beginning with Clojure

## 11. Supporting artifacts

Expected artifacts once the core is stable:

```text
schemas/       Machine-readable protocol documents
examples/      Complete valid and invalid exchanges
conformance/   Fixtures, expected results, and cross-implementation tests
decisions/     Rationale for consequential design choices
```

