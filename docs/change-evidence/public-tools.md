# Public change-evidence tools, compared

This decides which outside tools the change-evidence library (PER-171) should
read from, and which ones it competes with. It feeds the canonical
evidence/claim model (node D in the PER-171 plan).

Research date: **2026-11-01** for adoption and offline runs, and
**2026-11-03** for the model-backed runs Ethan approved that day. Every
excerpt is cut from a file under `evidence/public-tools/`, which holds the
output the tool actually wrote.

## Bottom line

| Tool | Class | Ran on our fixtures? | Verdict |
|---|---|---|---|
| Our review packets | evidence adapter + claim validator + review product | yes, offline | the reference |
| [sem](https://github.com/Ataraxy-Labs/sem) | semantic differ, plus impact/test evidence | yes, offline | **integration target** |
| [differential](https://github.com/thepartly/differential) | reading-plan generator | no — could not build | competitor for reading plans; its pre-LLM document is a possible second adapter |
| [semantic-diff](https://github.com/alankyshum/semantic-diff) (Rust) | reading-plan generator | no — could not build | ignore: 1 star, no commit since May |
| [semantic-diff](https://github.com/tkenaz/semantic_diff) (PyPI) | review product | yes — `analyze`, live | ignore: 7 stars; good prose, no checkable citations |
| [PR-Agent](https://github.com/The-PR-Agent/pr-agent) | review product | yes — describe/review/improve, live | downstream competitor, not a source |

Three findings shape the library:

1. **Only two tools check an AI's claims against the diff: ours and differential.**
   Ours rejects bad citations and incomplete coverage outright. Differential
   back-fills classes the model dropped and counts hallucinated ones. sem makes
   no AI claims. PR-Agent and both semantic-diffs parse the model's answer and
   show it. In the live runs, PR-Agent's 4 line citations all happened to land
   inside real hunks. Nothing checked them, and semantic_diff's risks cite no
   lines at all.
2. **sem is the evidence we lack.** It gives named entities, signature changes,
   callers left untouched, and tests that reach a change, all as JSON with no
   model call. Our packets stop at hunks.
3. **No tool has an id that is both stable and content-addressed for an entity.**
   sem's `entityId` is `path::type::name` — stable, but it changes on rename.
   differential's `h<N>` is positional, with a separate content `digest`. Ours
   is `h:xxxxxxxx` from content. The library must say how a sem entity id and a
   hunk id refer to each other.

## Fixtures

The three from PER-171, each built as `<sha>~1..<sha>`:

| Fixture | What it is | Files | Hunks (ours) |
|---|---|---|---|
| `2c0f3e7` | one-file shell fix | 1 | 2 |
| `ab3a477` | mechanical rename across 13 files | 13 | 34 |
| `701751b` | 10-file Clojure feature | 10 | 26 |

## Adoption

All from the GitHub REST API on 2026-11-01 (`evidence/public-tools/adoption/`),
plus npm for sem.

| Repo | Stars | Licence | Latest release | Last push | Machine-readable output |
|---|---|---|---|---|---|
| [Ataraxy-Labs/sem](https://github.com/Ataraxy-Labs/sem) | 3,436 | Apache-2.0 (README says MIT) | v0.29.0, 2026-10-30 | 2026-10-31 | `--format json` on every verb, MCP server, `--html`. npm `@ataraxy-labs/sem`: 16,995 downloads, 2026-09-30 to 10-29 |
| [thepartly/differential](https://github.com/thepartly/differential) (was gogoout/) | 17 | Apache-2.0 / MIT | v0.14.1, 2026-10-25 (crates.io only, no binaries) | 2026-10-25 | frozen JSON schema v3 (`spec/json-contract.md`), `dfr findings` JSON, `dfr check --json` |
| [alankyshum/semantic-diff](https://github.com/alankyshum/semantic-diff) | 1 | MIT | v0.9.0, 2026-03-19 (macOS binaries only) | 2026-05-07 | `result.json` (schema_version 2) |
| [tkenaz/semantic_diff](https://github.com/tkenaz/semantic_diff) | 7 | MIT | v0.7.0, 2026-10-30 | 2026-10-30 | `--json` (model output) |
| [The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent) (was qodo-ai/) | 13,856 | MIT | v0.49.0, 2026-10-25 | 2026-11-01 | `--json-output` for `review` in plain-diff mode; otherwise markdown |

Maintenance: sem and PR-Agent ship weekly; differential is active, with a
single maintainer; alankyshum/semantic-diff has stalled.

Not compared, for scale: [difftastic](https://github.com/wilfred/difftastic)
(26,120★) is a syntax-aware differ with no machine-readable output. Its README
says the output is for humans. Seen but not run, all with 0–23★:
[intentdiff](https://github.com/harivilasp/intentdiff) (deterministic JSON
with a confidence for each classification), [symtrace](https://github.com/symtrace/symtrace),
[saga](https://github.com/JakeBeresford/saga), [diffdad](https://github.com/nicknisi/diffdad),
[dyff](https://github.com/dyffs/dyff). "ReviewBrief" from the PER-171 brief is a
closed Grok bot ([listing](https://aiagents.org/grok-bots/review-brief)), so it
cannot be reproduced.

## The same small fix, four ways (`2c0f3e7`)

**Ours: a hunk is the unit.** Content-addressed id, display id, raw patch
(`packets/2c0f3e7.packet.json`):

```json
"h:67c919ec": {
  "classification": "code",
  "display/id": "H-002",
  "file": "skills/engineering-manager/scripts/kk-packet.sh",
  "lines": {"new": {"count": 9, "start": 942}, "old": {"count": 8, "start": 941}},
  "patch": "@@ -941,8 +942,9 @@ start|ensure)\n ...",
  "stats": {"added": 3, "removed": 2}
}
"facts/digest": "sha256:a5691338dba7318c70ad63ee731c36be2113edf5ed09b2eb80657eab16b64291"
```

**sem: an entity is the unit.** Shell code outside a function is reported as
an "orphan" (`sem/2c0f3e7.json`, `sem/2c0f3e7.certify.md`):

```text
# sem certificate 5c41816df660..2c0f3e741bce
1 files, 2 entities changed (0 added, 2 modified, 0 deleted, 0 renamed, 0 moved).
## Entities changed
(2 module-level fragment(s) or text chunk(s) also changed, not listed)
## Tests that statically reach the change
NO TEST REACHES THIS CHANGE: it is unverified. No test file has a static reference path to any changed entity.
```

The test claim is wrong for this repo: `tests/run-tests.sh` runs `kk-packet`
as a command, not through a static reference. sem states the limit in its own
output (`"limits": "static reference graph only …"`). The library should carry
that field rather than drop it.

**PR-Agent: the hunk as prompt text.** No ids. New-side line numbers are
printed inline, and old and new are split into blocks
(`pr-agent/2c0f3e7.review.request.json`, user message):

```text
## File: 'skills/engineering-manager/scripts/kk-packet.sh'

@@ -941,8 +942,9 @@ start|ensure)
__new hunk__
942    if [ "$external" = true ]; then
945 +    if ! { is_sha "$review_head" && is_sha "$review_base"; }; then
...
__old hunk__
-    is_sha "$review_head" && is_sha "$review_base" \
```

The model is asked for YAML whose issues cite `relevant_file` +
`start_line`/`end_line`. Nothing checks those lines against the diff.

**differential and semantic-diff:** not run (see *Gated*).

## The mechanical rename (`ab3a477`)

**sem** treats the rename as 26 modifications, not a rename: `renamed: 0`.
That is correct, because what changed was a string inside functions
(`restack_prepared` → `restack_unpushed`), not an entity name
(`sem/ab3a477.json`):

```json
{"entityId": "skills/engineering-manager/scripts/kk-dispatch.sh::function::settle_restack",
 "changeType": "modified", "structuralChange": true,
 "beforeContent": "... jq -c '.restack_prepared // empty ...",
 "afterContent":  "... jq -c '.restack_unpushed // empty ..."}
```

sem has no "same edit repeated N times" signal. Our Writer's `collapsed`
groups provide it as a claim, and differential's `pure_substitution` provides
it as a computed fact. Ours, from the real packet `p-20261029-96bc9a`, whose
range `de1dd44..ab3a477` is wider than the fixture
(`packets/ab3a477.writer-reader.p-20261029-96bc9a.json`):

```json
{"hunks": ["H-003", "H-005"], "representative": "H-003",
 "reason": "repeated-pattern", "similar": "conceptual",
 "note": "Each StackManager copy adds one `--keep-local` line to its list of kk-restack commands."}
```

**PR-Agent** sends all 34 hunks as one 51,817-character prompt
(`pr-agent/ab3a477.review.request.json`). It has no grouping step.

## The feature (`701751b`)

**sem certify** is the richest deterministic output of any tool
(`sem/701751b.certify.md`, 400 KB as JSON):

```text
10 files, 27 entities changed (6 added, 21 modified, 0 deleted, 0 renamed, 0 moved).
## Signature changes
- `choices` (…/review_feedback/approval.clj:27)
  static callers at head: 2 (2 modified in this change, 0 NOT modified by this change)
  INCOMPLETE caller set: 1 string literal equal to the name …; 12 name used as a value …
  possible callers the static graph did not resolve, NOT modified by this change: 10
    - skills/engineering-manager/tests/approval-ui.mjs:0 `<module level>` (L137 string_key)
```

It also lists 9 signature changes and 11 untouched callers, and names the
8 files outside the change that statically depend on it. Our packet for
the same range has 26 hunks and no notion of callers.

`sem impact --diff` writes JSONL, one report per entity. It fails on shell
"orphans" when the range is not the working tree (`sem/701751b.impact.err`:
`Entity ID '…kk-packet.sh::orphan::modified@L925-1083' not found`). The sem
adapter (node S) must use `certify --json`, not `impact --diff`, for past
ranges.

**Our Writer and Reader** for this fixture ran under PER-172, and its outputs
are reused here rather than run twice. See PER-172 commit `a0cc241`,
`docs/change-evidence/fixtures/701751b/`. That packet validated `VALID — 2
warning(s)`, and the Reader passed it with 3 advisory findings. It used two
runs on `claude-opus-5-5[1m]`: the Writer wrote 13,897 output tokens and the
Reader 4,760 (`usage.json` there).

## Claim checking, side by side

The one property that separates evidence-constrained tools from review
products.

**Ours** rejects. The real Writer document from the on-disk `2c0f3e7` packet
covers a wider range (45 hunks). Validated against the single-commit packet,
with one invented citation added, it fails with 61 violations and exit 5
(`packets/2c0f3e7.validate-rejection.txt`):

```text
p-20261101-96b9b7  PER-173  INVALID — 61 violation(s)
  [files-exact] agents/gatekeeper.md: is not a file in the facts
  [hunks-exist] narrative.sections[0] import-pins-the-pr body[2]: cites "H-999", which is not a hunk in this packet
```

Counts by rule: `hunks-exist` 44, `files-exact` 15, `packet-id-matches` 1,
`limits` 1. A passing packet records `{"ok": true, "violations": [], "validator/version": 4}`,
and the Reader's verdict is bound to `narrative/digest`
(`packets/ab3a477.writer-reader.*.json`).

**differential** audits its own model output. From `spec/json-contract.md`:
`coverage`, `classes_missing`, `classes_duplicated` and `classes_hallucinated`
are recorded, and a class the model omits is back-filled into a `focus` group,
never dropped. Its grouping prompt forbids inventing ids
(`differential/upstream-prompt-v6.head.txt`):

```text
Rules:
- Every class id must appear in exactly one group. Do not invent class ids.
```

It audits coverage of classes, not claims about hunks. It has no equivalent
of our `files-exact` or facts-digest immutability.

**semantic-diff (Rust)** records the model's review sections and nothing about
their validity. Its own fixture
(`semantic-diff/upstream-fixture-sample-with-issues.json`) is hand-written:
`cli_argv` says `--no-llm`, yet it carries `VERDICT` findings.

**PR-Agent** parses YAML. When parsing fails it retries, then falls back to
other models. Its claims cite `relevant_file` + line ranges, but nothing
checks them against the diff. Checked afterwards (`scripts/cite_check.py`),
all 4 citations in the live runs fall inside real new-side hunks: 1 review
issue and 3 improve suggestions, all on `701751b`. That shows the model was
right this time, not that the tool guarantees it.

**semantic_diff (PyPI)** cites nothing checkable. Its risks and impacts name
areas in prose ("kk-packet.sh import command"), with no file:line field. Its
only uncertainty field is one `intent.confidence` number for each run.

## Model-backed runs (2026-11-03)

Ethan approved these on 2026-11-03.

**How the model was reached.** This host has no readable API key: the
provider keys under `/run/secrets` belong to other service users. It does
have a logged-in Claude Code CLI. `scripts/claude-gateway.py` is a local
OpenAI-compatible endpoint that forwards each tool's own system and user
messages to `claude -p`, with the CLI's system prompt replaced, its tools
removed, and settings, CLAUDE.md and hooks off. The CLI still adds a measured
~430 input tokens per call. Temperature, `max_tokens` and seed are not
forwarded, and a request that needs tools is refused rather than answered
without them. The model is **`claude-sonnet-5`** for every call. That is the
model the gateway was asked for, and it is what the CLI reported in
`modelUsage`.

**Usage** (`pr-agent-live/usage.jsonl`, `semantic_diff-live/usage.jsonl`).
Costs are the CLI's `total_cost_usd` at list price (`costBasis: list`); the
account's actual billing may differ.

| Tool | Calls | Input tokens (incl. cache) | Output tokens | Cost |
|---|---|---|---|---|
| PR-Agent 0.49.0, 3 fixtures × describe/review/improve | 12 | 162,670 | 69,262 | $1.19 |
| semantic_diff 0.7.0 `analyze`, 3 fixtures | 3 | 32,960 | 14,745 | $0.28 |

PR-Agent used 12 calls, not 9:

- **2 were wasted.** On `701751b`, review and improve took 168 s and 188 s.
  PR-Agent's client timed out first, closed the connection, and asked again.
  The wasted calls are `007` and `009`; the retries `008` and `010` produced
  the outputs used.
- **1 is by design.** improve makes a second "self-reflection" call that
  scores each suggestion and assigns its line range (call `011`).

PR-Agent ran from 12:48 to 12:58 UTC and semantic_diff from 12:58 to 13:01 UTC.

**What they said.** For the small fix, `2c0f3e7`, PR-Agent describe wrote
(`pr-agent-live/2c0f3e7.describe.md`):

```text
### **PR Type**
Bug fix
### **Description**
- Refactor `is_sha` validation checks to use explicit `if` blocks
- Avoid relying on `||` short-circuit after compound `&&` conditions
```

| Fixture | PR-Agent review effort / tests / issues | PR-Agent improve | semantic_diff risk / confidence |
|---|---|---|---|
| `2c0f3e7` | 1 / No / 0 | no suggestions | low / 0.95 |
| `ab3a477` | 2 / Yes / 0 | no suggestions | medium / 0.95 |
| `701751b` | 4 / No / 1 | 3 suggestions, scores 3–6 | high / 0.90 |

PR-Agent's one review issue on `701751b` (`pr-agent-live/701751b.review.md`):

```text
Hardcoded Name: The generated brief text for a chain-break packet hardcodes the
name `Ethan` ("the last packet Ethan acted on") instead of referencing the actual
reviewer/actor for the ticket.
```

semantic_diff on the rename, `ab3a477` (`semantic_diff-live/ab3a477.analyze.json`):

```json
{"question": "Is there any ticket currently holding a `restack_prepared` metadata key written by the old kk-restack binary before this deploy? If so, how will it be migrated to `restack_unpushed` (or will kk-dispatch/kk-packet temporarily read both keys)?"}
```

That is a real migration question, and none of the deterministic tools can
raise it. It shows where the review products earn their place: downstream of
evidence, asking about intent.

## Classification

- **Evidence adapter:** produces deterministic facts about a change. Ours
  (`gitdiff` + `model`); sem; differential's pre-grouping document
  (`groups: null`, stages `enumerate, classify`).
- **Semantic differ:** facts at the level of entities, not lines. sem.
- **Reading-plan generator:** an AI orders and groups the change for a human.
  differential (`reading_plan`, `focus/skim/noise`); alankyshum/semantic-diff
  (groups + WHY/WHAT/HOW/VERDICT).
- **Review product:** an AI judges the change and posts it. PR-Agent;
  tkenaz/semantic_diff; our packet's render, feedback and approval layer.

## Integration targets versus competitors

**Integrate:**

- **sem `certify --json` and `diff --format json`.** These are the evidence
  units beyond hunks that PER-171 Q3 asks about: entity, signature change,
  untouched caller, affected test, static cone, and `limits`. 3.4k★, weekly
  releases, Linux binary, works offline. Map `entityId` and line spans onto
  hunk ids; keep `limits` and `callerSetsIncomplete` as uncertainty, not as
  fact.
- **differential's schema v3, as a design reference, not a dependency.**
  `digest` as the stable anchor beside positional ids, `pure_substitution`
  computed and never claimed, and `generator.stages` saying which stages ran
  are worth copying into our model. Too small (17★) and unbuildable here
  without crates.io to depend on.

**Competitors downstream (consumers of evidence, not sources):**

- PR-Agent: the adoption leader by far (13.9k★). Its diff encoding is a prompt
  format with no ids. A later integration could hand it our evidence through
  `extra_instructions`; nothing from it feeds the library.
- differential's reading plan, and both semantic-diffs: they compete with our
  Writer + Reader, not with the evidence library.

## Still unresolved

| What | Blocked by | To unblock |
|---|---|---|
| differential, offline and grouping | crates.io is unreachable from this host (`index.crates.io`, `static.crates.io` refused; npm, PyPI and GitHub work); no prebuilt binaries. Model use is approved, but there is no binary to run | allow crates.io egress, or build `dfr` elsewhere and copy it in. Infrastructure was left unchanged on purpose |
| alankyshum/semantic-diff, offline and reviews | the same crates.io block; macOS binaries only | the same |
| tkenaz/semantic_diff `review` (agentic mode) | it needs tool calling, which the CLI gateway refuses | a real Anthropic or OpenAI-compatible API key that this user can read |

The 2026-11-01 offline captures in `pr-agent/` remain: requests sent to a stub
that answered 503 (`scripts/record-stub.py`). They show PR-Agent's input
encoding.

## Caveats

- Our packets were built from this branch's code at `d041660`, with ticket
  `PER-173`, so their `facts/digest` differs from the on-disk packets for the
  same commits. That is expected: facts include the ticket, the URL and the
  chain (`review_packet/model.clj:343-349`).
- PR-Agent's tokenizer could not download its vocabulary, so the token count
  was patched to bytes/4 (`scripts/run-pr-agent.py`). The patch only changes
  how a diff is trimmed near the context limit, and the largest prompt here is
  about 52k characters, far below it.
- Writer and Reader excerpts for `2c0f3e7` and `ab3a477` come from earlier
  real packets whose ranges are wider than the fixture; each excerpt names its
  packet id. `701751b` is exact (PER-172).
- The live runs went through a CLI, not the provider API, so sampling settings
  were the CLI's defaults, not the tools'. One run per call: these are single
  samples, not a measure of how consistent the tools are.
- Star counts are a weak signal for a tool created in 2026; npm downloads are
  given for sem as a second signal.

## Evidence index

All paths are under `docs/change-evidence/evidence/public-tools/`.

- `packets/<fx>.packet.json`: our deterministic packet, built offline.
- `packets/*.writer-reader.*.json`: real Writer narrative, validation and
  Reader verdict, taken from `/var/lib/review-packets`.
- `packets/2c0f3e7.validate-rejection.txt`, `2c0f3e7.stale-writer-doc.json`:
  the rejected claim document.
- `sem/<fx>.{json,md,txt,certify.json,certify.md,impact.json,impact.err,arch.html}`:
  sem 0.29.0 output.
- `pr-agent/<fx>.diff`, `<fx>.{describe,review,improve}.request.json`: the
  exact request PR-Agent sends (first try; its five retries were
  byte-identical).
- `differential/`, `semantic-diff/`: upstream fixtures and prompt, copied from
  the repositories at `982c5d6` and `edd5914`.
- `pr-agent-live/<fx>.{describe,review,improve}.md`, `<fx>.review.result.json`:
  PR-Agent's live output. `gateway/NNN.{request,claude,response}.json` hold
  each call as sent, the raw CLI result with its usage, and what was
  returned. `usage.jsonl` is the ledger.
- `semantic_diff-live/<fx>.analyze.json`, `gateway/`, `usage.jsonl`: the same
  for semantic_diff.
- `adoption/*.jsonl`: raw GitHub API fields.
- `scripts/`: the recording stub, the PR-Agent wrapper, the Claude gateway,
  and the citation check.

## Reproduce

```sh
sem diff --commit <fx> --format json
sem certify <fx>~1..<fx> --json
kk-review-packet build --ticket PER-173 --base <fx>~1 --head <fx>
git diff <fx>~1 <fx> > fx.diff
python3 scripts/record-stub.py 18765 requests/ &
CONFIG__MODEL=openai/gpt-4o OPENAI__KEY=stub OPENAI__API_BASE=http://127.0.0.1:18765/v1 \
  python scripts/run-pr-agent.py --diff-file fx.diff --output out.md review
# live, through the Claude CLI:
python3 scripts/claude-gateway.py 18766 gateway/ &
CONFIG__MODEL=openai/claude-sonnet-5 CONFIG__FALLBACK_MODELS='[]' CONFIG__CUSTOM_MODEL_MAX_TOKENS=200000 \
  OPENAI__KEY=gateway OPENAI__API_BASE=http://127.0.0.1:18766/v1 \
  python scripts/run-pr-agent.py --diff-file fx.diff --output out.md review
SEMANTIC_DIFF_PROVIDER=openai SEMANTIC_DIFF_API_KEY=gateway SEMANTIC_DIFF_BASE_URL=http://127.0.0.1:18766/v1 \
  semantic-diff analyze <fx> --model claude-sonnet-5 --json
```
