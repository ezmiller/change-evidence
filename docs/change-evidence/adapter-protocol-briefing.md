## Adapter protocol — design briefing

Working material for Ethan to design `docs/change-evidence/adapter-protocol.md`
(PER-176). This is not that design. It collects what earlier tickets settled,
what the code does today, and the decisions still open. Anything under
**Provisional** is a sketch to argue with, not a recommendation.

Read at `origin/main` `4b45188`. The review-packet code is unchanged since
`c037bc7`, where PER-175 read it, so its line numbers hold.

Path shorthand: `ns/` = `skills/engineering-manager/scripts/review-packet/review_packet/`,
`rp/` = `skills/engineering-manager/scripts/review-packet/`,
`sh/` = `skills/engineering-manager/scripts/`.

## 0. Sources

All are local branches; none is pushed.

| Ticket | Status | Branch @ commit | Artifact | Use it for |
|---|---|---|---|---|
| PER-172 | done | `PER-172-map-current-change-evidence-system` @ `a0cc241` | `current-system-map.md`, `fixtures/{2c0f3e7,ab3a477,701751b,tamper,prod-*}/` | where Git is run and parsed today; real packets, writer docs, validation reports |
| PER-173 | done | `PER-173-compare-public-change-evidence-tools` @ `23931de` | `public-tools.md`, `evidence/public-tools/` | which outside tools are sources vs competitors; sem/differential output shapes |
| PER-174 | in progress | `PER-174-spike-sem-evidence-adapter-feasibility` @ `0f1885c` | `sem-adapter-spike.md`, `sem-samples/` | sem verdict, sem field names, failure behaviour |
| PER-175 | done | `PER-175-design-canonical-evidence-claim-model` @ `d0a0261` | `canonical-model.md`, `fixtures/synthetic/` | **the model the adapter must emit** |
| PER-181 | in progress | `PER-181-map-theoretical-foundations-evidence-constrained` @ `3b59f04` | `theoretical-foundations.md` | guarantees vs non-guarantees; provenance terms |
| PER-186 | done | `PER-186-map-claim-evidence-protocol-current-review-packets` @ `cd140de` | `current-review-packet-protocol-map.{md,svg,png}` | the narrow protocol boundary |
| PER-176 | this | `PER-176-design-evidence-adapter-protocol` | this file, `fixtures/edge-cases/` | new edge-case evidence (§6) |

All artifacts are also attached to the ticket as one archive.

## 1. Established constraints

### From the ticket

- Consumers must need no adapter-specific parsing and must validate from the
  canonical evidence document alone.
- Every current `gitdiff` use in `model` and `validate` gets a future home (§5.1).
- Cover: inputs, capabilities, output schema, provenance, versioning, errors,
  capability negotiation, sem mapping, and deterministic rename / binary /
  mode / generated / empty-file handling. Include native-Git and sem-shaped
  example outputs.

### Inherited from PER-175 (treat as fixed unless you reopen them)

| Decision | Where |
|---|---|
| Evidence, claims, attestation are separate JSON documents; `schema`, `version`, `digest`, `meta` on each | canonical-model.md "Three documents" |
| Digest = `sha256:` + hex(SHA-256(JCS(doc − {digest, meta}))) | "Canonical JSON and digests" |
| Integers only; no keywords on the wire | same |
| `subject` = `{repo (stable name, not a path), base, head}` as 40-hex | "Evidence set" |
| `sources[]` each with `id`, `tool`, `version`, `argv`, optional `classifier {id, version, classes}`, `complete` | same |
| Only `hunk` units are coverage units; `file`, `entity-change`, `dependency`, `test-link`, `test-run` are enrichment that cite hunks, never the reverse | "Unit types" |
| Hunk `kind` ∈ `text`, `binary`, `rename`/`copy`, `mode`, `empty`, split from `class` | "Hunk kinds" |
| Hunk id: v2 preimage for `text`; binary id now includes full blob ids | "Identifiers" |
| Entity id from `(path, type, name)`; sem `@L…` ids refused as identity | same |
| Aliases (`H-001`) assigned by adapter, in adapter order, rewritten before claim digest | "Aliases" |
| Adapter totality: every change is a unit or an `exclusions[]` entry; reserved reasons `size-limit`, `submodule`, `filtered` | "Exclusions" |
| `diff-violations` moves behind an adapter `verify(evidence, source) → violations` hook, code `source-mismatch` | "Three boundary decisions" #1 |
| Digest/attestation binding is in the protocol | #2 |
| Classification stays entirely in the adapter; core only checks membership in declared `classes` | #3 |
| Validator is pure; implementations agree on `ok` and the `(code, where)` multiset | "Validation" |

### From the other studies

- **sem is enrichment, not a floor** (PER-174 verdict). No range provenance,
  no schema version, `impact` drops orphans with exit 0, mode changes and empty
  files absent, binary changes without hashes.
- **The real Git boundary is wider than `gitdiff`** (PER-172 "The real Git
  boundary"): range selection lives in Bash (`sh/kk-review-packet.sh`), and
  three more diff parsers sit downstream (`ns/anchor.cljc:21-68`,
  `ns/render.clj:181-201`, review-feedback via `anchor/diff-lines`).
- **Narrowest honest boundary** (PER-186): the protocol owns ids, fingerprints,
  citation/coverage checks, and attestation binding. It never judges truth,
  writes prose, approves, or pushes.
- **Validation guarantees structure, not truth** (PER-181 §4). The adapter is
  where facts come from, so its determinism and provenance are what the
  guarantee rests on. PER-181 §6.5 suggests PROV terms: evidence as entity,
  adapter run as activity, tool + version as agent.
- **Production already isolates global Git config**: `sh/kk-packet-build.sh:144-148`
  sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`. Repo-local
  config still applies (see D-14).

## 2. Provisional sketches

**Provisional.** Shapes to react to. Field names follow PER-175 where it
already named them.

### 2.1 Interface — two candidate styles

A. **Process adapter.** One executable per adapter; JSON in on stdin, JSON out
on stdout; exit code classifies failure. Language-neutral, matches how sem
must be run anyway.

```
adapter describe                → manifest
adapter extract  < request      → evidence-fragment | error
adapter verify   < {evidence, source-ref} → {violations: [...]}
```

B. **In-process library.** A function set per language.

```clojure
(describe)                       ; → manifest
(extract request)                ; → evidence-fragment, or throws ex-info {:code …}
(verify evidence source)         ; → [violation …]
```

Both could share one wire schema; B can wrap A, or A can be B's CLI.

### 2.2 Manifest

```json
{"schema": "change-evidence/adapter-manifest", "version": 1,
 "adapter": {"id": "git", "version": "1.0.0", "protocol": 1},
 "provides": ["hunk", "file"],
 "kinds": ["text", "binary", "rename", "copy", "mode", "empty"],
 "requires": [],
 "classifier": {"id": "review-packet.model", "version": 2,
                "classes": ["code", "formatting-only", "generated", "lockfile",
                            "binary", "rename", "mode-change"]},
 "exclusion-reasons": ["size-limit", "submodule", "filtered"],
 "verify": true}
```

An sem manifest would say `"provides": ["entity-change", "dependency", "test-link"]`,
`"requires": ["hunk"]`, `"verify": false`.

### 2.3 Request

```json
{"schema": "change-evidence/adapter-request", "version": 1,
 "subject": {"repo": "github.com/ezmiller/botserver-nix",
             "base": "<40-hex>", "head": "<40-hex>"},
 "workdir": "/path/to/clone",
 "want": ["hunk", "file"],
 "options": {"find-renames": 50, "unified": 3, "exclude": []},
 "upstream": null}
```

`upstream` would carry the Git fragment to an enrichment adapter that must
join on hunk ranges (sem).

### 2.4 Native-Git fragment, from `fixtures/synthetic` (PER-175) and `fixtures/edge-cases`

Ids are the real v2 ids from the captured packets except the binary one,
which PER-175 changes; it is elided.

```json
{"schema": "change-evidence/evidence-fragment", "version": 1,
 "source": {"id": "git", "tool": "git", "version": "2.53.0",
            "adapter": {"id": "git", "version": "1.0.0", "protocol": 1},
            "argv": ["diff", "--no-color", "--no-ext-diff", "--no-textconv",
                     "--find-renames", "--unified=3", "<base>", "<head>"],
            "classifier": {"id": "review-packet.model", "version": 2, "classes": ["…"]},
            "complete": true},
 "units": [
  {"id": "f:empty.txt", "type": "file", "path": "empty.txt", "status": "added",
   "binary": false, "hunks": ["h:50a1e315"]},
  {"id": "h:50a1e315", "type": "hunk", "kind": "empty", "class": "code",
   "file": "f:empty.txt", "status": "added", "old": null, "new": null,
   "stats": {"added": 0, "removed": 0}, "patch": "new file mode 100644\n"},
  {"id": "h:…", "type": "hunk", "kind": "binary", "class": "binary",
   "file": "f:logo.png", "blobs": {"old": "346d7bb4…", "new": "a7dc397…"},
   "patch": "Binary files a/logo.png and b/logo.png differ\n"},
  {"id": "h:eb466354", "type": "hunk", "kind": "rename", "class": "rename",
   "file": "f:renamed.txt", "from": "old.txt", "similarity": 100},
  {"id": "h:b7a56849", "type": "hunk", "kind": "mode", "class": "mode-change",
   "file": "f:tool.sh", "mode": {"from": "100644", "to": "100755"}},
  {"id": "h:22625719", "type": "hunk", "kind": "text", "class": "code",
   "file": "f:moved-sub", "old": {"start": 1, "count": 1}, "new": {"start": 1, "count": 1},
   "patch": "@@ -1 +1 @@\n-Subproject commit 9c3b58d9…\n+Subproject commit …\n"}],
 "exclusions": []}
```

The last unit is what a submodule bump becomes **today** (§6.1), not a
proposal.

### 2.5 sem-shaped fragment, from PER-174's hand mapping of `701751b`

```json
{"schema": "change-evidence/evidence-fragment", "version": 1,
 "source": {"id": "sem", "tool": "sem", "version": "0.29.0",
            "binary/sha256": "30fa7ab7…22dc3",
            "argv": ["diff", "--commit", "701751b", "--format", "json"],
            "env": {"SEM_NO_NETWORK": "1", "SEM_NO_UPDATE_CHECK": "1", "SEM_NO_TELEMETRY": "1"},
            "complete": false,
            "incomplete": [{"capability": "dependency", "reason": "impact-dropped-orphans", "count": 7}]},
 "units": [
  {"id": "e:…", "type": "entity-change", "file": "f:…/review_packet/model.clj",
   "entity": {"type": "function", "name": "build-packet"}, "change": "modified",
   "hunks": ["h:9fd36116", "h:62962ed7"], "complete": false},
  {"id": "d:…", "type": "dependency",
   "from": "…/model.clj::function::facts-digest", "to": "…/model.clj::var::fact-keys",
   "relation": "uses", "complete": true}],
 "exclusions": []}
```

`incomplete[]` is not in PER-175; it is one option for D-6.

### 2.6 Error document

```json
{"schema": "change-evidence/adapter-error", "version": 1,
 "code": "source-ambiguous", "adapter": {"id": "git", "version": "1.0.0"},
 "message": "diff and --raw disagree on how many files changed (2 patch blocks, 1 records)",
 "where": "link-me", "retryable": false}
```

That message is the real one from `fixtures/edge-cases/typechange.txt`.

## 3. Decisions to make

Each lists options and what they cost. None is pre-chosen.

**D-1 Interface style** (§2.1). *Process*: one contract for Clojure, TypeScript
and sem; costs a process per run and JSON for every exchange. *Library*: cheap
and testable in-process; needs one implementation per language or a wrapper
for external tools anyway. *Both*: one wire schema, two bindings; most to
specify.

**D-2 Who resolves the range.** Today Bash chooses base/head
(`sh/kk-review-packet.sh:367-500`: merge-base, parent branch, follow-up
ancestry). *Adapter takes resolved 40-hex only*: simplest, keeps policy out,
but leaves range policy in Bash. *Adapter resolves refs and records both ref
and SHA*: one place, but range policy (merge-base vs explicit) becomes
protocol. *Separate "subject resolver" step*: clean, one more contract.

**D-3 One adapter or composed fragments.** *Single adapter emits the whole
evidence set*: simple, but sem enrichment would live inside the Git adapter.
*Fragments plus a composer*: Git floor + optional enrichers; needs rules for
alias order across sources, id collisions, and a dependency order (sem needs
hunk ranges). Who owns the composer — core or consumer?

**D-4 How enrichment joins hunks.** PER-174 joins sem entities to hunks by
`(path, line range) ∩ hunk range`. *Enricher receives the Git fragment
(`upstream`)*: enricher does the join; must be deterministic per adapter.
*Composer joins*: one join rule for all enrichers; enrichers emit raw ranges.

**D-5 Capability negotiation.** *Declare-only*: adapter says what it provides;
consumer checks. *Request/response*: consumer sends `want`, adapter answers
with what it did. *Required vs optional*: a missing required capability is an
error; a missing optional one is a `gap`, a warning, or silence. Also: is a
claim of type `test` with no `test-run` source a profile matter or core?

**D-6 Completeness granularity.** PER-175 has `complete` per source and per
unit. *Keep that*: simple, but "incomplete" says nothing about what. *Add
per-capability reasons* (§2.5 `incomplete[]`): more useful to the
`cites-incomplete` warning; more vocabulary to version.

**D-7 What is digested.** PER-175 puts `sources[]` (tool version, argv) inside
the digest. Consequence: upgrading git from 2.53 to 2.54 changes the evidence
digest even when every unit is identical, which invalidates attestations.
*Keep*: provenance is bound, attestations go stale on tool change. *Move tool
version to `meta`*: digests survive upgrades; provenance is no longer bound.
*Digest argv and classifier, not tool version*: middle ground.

**D-8 Versioning scheme.** At least four things version independently:
protocol, adapter, classifier, underlying tool. Decide which bump forces what:
a classifier change can reclassify hunks (ids survive, digest changes); an id
preimage change breaks every citation. Options: one integer per thing (PER-175
style) or semver per adapter with a protocol integer.

**D-9 Error model.** Today `gitdiff` throws `ex-info {:exit 4}` for any git
failure (`ns/gitdiff.clj:18-19`, `:29-31`, `:169-172`); `rp/build.clj` exits 7
on an empty range and 1 if the bundle exists. Options: *exit codes only*;
*structured error document* (§2.6); *partial output with errors* (an
enricher's partial result is still useful). Is an empty range an error, or
an evidence set with zero units?

**D-10 What `verify` gets as "source".** *Raw bytes* (today: `raw.diff` kept
in the bundle, `ns/export.clj`): verify is offline and exact. *Repo + range*:
re-run git; needs the repo and identical git behaviour. *Source digest only*:
detects change but cannot say where. Also: is `verify` mandatory? sem has no
raw source to compare.

**D-11 Patch fidelity.** `patch` should reassemble `raw.diff` (PER-175). It
does not for CRLF files: `split-blocks` uses `str/split-lines`, which drops
`\r` (§6.6). Options: *store exact bytes* (CR kept; JSON escapes it); *declare
`patch` normalised* and have verify normalise too (today's de facto
behaviour); *store raw byte offsets* into the source instead of text.

**D-12 Line records in evidence.** Three downstream parsers exist because the
evidence lacks per-line data (PER-172). *Add per-line records* (kind,
old/new line number) to hunks: consumers stop parsing; evidence grows.
*Ship a canonical parser of `patch` in the library*: smaller evidence, but
consumers still parse (just one way). *Leave it to consumers*: violates the
"no adapter-specific parsing" done-criterion.

**D-13 Ordering.** Units in git's order (what aliases follow today) or sorted
by id/path? Git order depends on git's diff queue (and `-O` orderfile config);
sorting is portable but changes alias assignment from today.

**D-14 Git configuration isolation.** Global config is isolated in production;
repo-local `.git/config` (`diff.algorithm`, `diff.renames`,
`diff.renameLimit`) is not. Options: pass every behaviour-changing flag
explicitly (`--diff-algorithm=myers`, `-M50%`, `-l<n>`) and record them in
`argv`; or run with `GIT_CONFIG_NOSYSTEM` plus an empty repo config. Unverified
whether any current repo sets these.

**D-15 to D-20** are the edge cases in §6, each a decision.

## 4. Required properties

### 4.1 Invariants the adapter must guarantee

From PER-175 unless marked.

1. Every changed path is in exactly one `file` unit or one exclusion.
2. Every `file` has ≥ 1 hunk; every hunk belongs to exactly one file.
3. `id` recomputes from its preimage; ids and aliases are unique.
4. Every hunk `class` is in the declared `classes`.
5. `stats` counts the patch's `+`/`-` lines.
6. Enrichment units cite only hunk/file ids in the same set.
7. Same subject + same adapter version + same options → byte-identical
   canonical output (determinism). Holds today for hunk ids across rebuilds
   (`fixtures/edge-cases` built twice, same ids and facts digest).
8. *(open, D-11)* header lines + every `patch` reassemble the source exactly.
9. *(new)* An adapter never emits a partially paired result: if two of its own
   streams disagree it fails (today's `changed-files` refusal,
   `ns/gitdiff.clj:169-172`).

### 4.2 Provenance

What PER-175 records per source: `tool`, `version`, `argv`, `classifier`,
`complete`; sem adds `binary/sha256` and `env`. Open: adapter id/version
separate from tool version (D-8); repo-local config (D-14); what goes to `meta`
(PER-175 moves build time, host, packet id/URL, repo path there). PER-174:
the sem wrapper must supply `base`/`head`, since sem's `diff` reports
`commitSha: null`.

### 4.3 Versioning

See D-8. Fixed by PER-175: `version` integer on every document; validator
reports `{impl, version, registry}`; a packet from an older model is rebuilt,
not reinterpreted (`packet-version` rule, `ns/validate.clj:81`, `:474`).

### 4.4 Capability negotiation

See D-5, D-6. Constraints: coverage never depends on an enricher (only hunks
cover); a high-confidence claim citing an incomplete unit warns
(`cites-incomplete`).

### 4.5 Source-verification hooks

`verify(evidence, source) → violations`, code `source-mismatch` (PER-175).
Today's checks to carry over, all from `diff-violations`
(`ns/validate.clj:338-399`): file-block count equals file count; per file, `@@`
count equals real-hunk count; a file with no `@@` has exactly one synthetic
hunk and a file with `@@` has none; each real hunk's patch text equals the
source text. Open: D-10, D-11.

### 4.6 Error codes

Today: exit 4 (git failed or streams disagree), 7 (empty range), 1 (bundle
exists, packet-specific), 5 (validation failed, validator CLI). A provisional
adapter vocabulary to start from:

| Code | Meaning | Today |
|---|---|---|
| `subject-unresolved` | base/head not found | git exit → 4 |
| `source-failed` | tool exited non-zero | 4 |
| `source-ambiguous` | streams disagree; refused | 4 (`changed-files`) |
| `empty-subject` | nothing changed | 7 |
| `capability-unavailable` | a requested capability cannot be produced | — |
| `unsupported-change` | a change shape the adapter cannot represent | — (type change hits `source-ambiguous`) |
| `tool-version-unsupported` | pinned version/hash mismatch | — (sem needs it) |

### 4.7 Conformance expectations

Extends PER-175's list for PER-178:

1. Each fixture below yields byte-identical canonical evidence in both
   implementations and on two runs.
2. One vector per kind and per edge case in §6, including the type change.
3. `verify` passes on the pristine fixture and fires `source-mismatch` on each
   tamper: drop a hunk, duplicate a hunk, edit one patch byte, add a synthetic
   hunk to a file with `@@`.
4. Every adapter error code fired alone.
5. Capability: an enricher absent, incomplete, and present give the same
   coverage result.
6. Config sensitivity: a repo with `diff.algorithm=patience` gives the same
   evidence (if D-14 chooses isolation).

Fixtures on hand: `2c0f3e7`, `ab3a477`, `701751b` (PER-172), `synthetic`
(PER-175), `edge-cases` (this branch), PER-172 `tamper/`, and sem samples
(PER-174 `sem-samples/`).

## 5. Mappings

### 5.1 Every `gitdiff` use, with candidate homes (provisional)

| Use | Where | What it does | Candidate home |
|---|---|---|---|
| `diff-to-file` | `rp/build.clj:143-144` | writes `raw.diff` (and `action.diff` for follow-ups) | Git adapter `extract`; raw source kept for `verify` |
| `changed-files` | `rp/build.clj:149-150` | pairs `--raw -z` records with blocks | Git adapter internals |
| `dirty?` | `rp/build.clj:159` | dirty-worktree warning | adapter warning, or consumer (packet build); not evidence |
| `hunk-header-re` | `ns/model.clj:77` (`norm-heading`) | heading for the id preimage | Git adapter id function |
| `hunk-header-re` | `ns/model.clj:152` (`generated-marker?`) | `@generated` must be in a hunk at new line 1 | Git adapter classifier |
| `parse-block` | `ns/model.clj:212` | header vs `@@` hunks | Git adapter |
| `binary-block?` | `ns/model.clj:213` | binary detection from header text | Git adapter (or from `--numstat` `-\t-`) |
| `mode-change` | `ns/model.clj:214` | chmod from raw record | Git adapter |
| `changed-lines` | `ns/model.clj:218` | `+`/`-` lines for ids, stats, class | Git adapter |
| `hunk-header-re` | `ns/model.clj:221` | line ranges | Git adapter → `old`/`new` fields |
| `split-blocks` | `ns/validate.clj:351` | re-split raw.diff | Git adapter `verify` |
| `parse-block` | `ns/validate.clj:360` | re-parse each block | Git adapter `verify` |

Non-`gitdiff` parsers that the done-criterion also reaches: `ns/anchor.cljc:21-68`
(own `@@` regex, path from `diff --git`), `ns/render.clj:181-201`,
review-feedback (`packets.clj:29-30`, `ui.cljs:120`). Their home depends on D-12.

### 5.2 Git → canonical evidence

| Git output | Canonical field |
|---|---|
| raw record `status` letter A/C/D/M/R/T/U/X (`ns/gitdiff.clj:60-62`) | `file.status`; T and U unresolved (§6.2) |
| raw `R083` score | `file.similarity`, `hunk.similarity` for rename kind |
| raw `old-mode`/`new-mode` | `hunk.mode` (kind `mode`), `000000` = create/delete |
| raw old/new sha (dropped today, `:77`; abbreviated, `:167`) | `hunk.blobs` for binary; needs `--no-abbrev` |
| raw path, path/from | `file.path`, `file.from` (never from `diff --git`, `ns/gitdiff.clj:54-58`) |
| `@@ -a,b +c,d @@ heading` | `hunk.old`, `hunk.new`, `hunk.heading` |
| `+`/`-` lines | `stats`, id preimage, class |
| `Binary files … differ` / `GIT binary patch` | kind `binary` |
| no `@@`, status R/C | kind `rename`/`copy` |
| no `@@`, mode change | kind `mode` |
| no `@@`, A/D | kind `empty` |
| `160000` modes, `Subproject commit` lines | **today: kind `text`, class `code`** (§6.1) |

### 5.3 sem → canonical evidence (from PER-174)

| sem | Canonical | Note |
|---|---|---|
| `diff` `changes[].entityId` | not used as id | `@L…` moves on line shift |
| `filePath`, `entityType`, `entityName` | `entity-change.file`, `entity.type`, `entity.name`; id from these | field names differ per verb (`graph` `id`, `find` `file`) |
| `changeType` (added/modified/deleted/renamed/moved) | `entity-change.change` | move+edit reports only `moved` plus `structuralChange: true` |
| `oldEntityName`, `oldFilePath` | rename/move detail | |
| line ranges | join to hunks (D-4) | |
| `impact` `dependencies`/`dependents` | `dependency` units | orphans dropped, exit 0 → `complete: false` |
| `possibleCallers`, `callersComplete`, `incompleteBecause` | `dependency.complete`, reason (D-6) | name matches; noisy |
| `tests[]`, `noTestReaches` | `test-link` | zero on this repo |
| `certify` `base`, `head` | provenance cross-check | `diff` has `commitSha: null` |
| (absent) mode changes, empty files, binary hashes | none; Git floor covers them | |
| (absent) version in output | wrapper adds `version`, `binary/sha256`, `argv`, `env` | |

### 5.4 Future adapters (from PER-173, PER-174)

| Candidate | Would provide | Floor or enricher | Note |
|---|---|---|---|
| clj-kondo analysis | Clojure var definitions/usages → `entity-change`, `dependency` | enricher | in nixpkgs; not run (PER-174) |
| differential pre-LLM document | reading-plan classes, frozen JSON schema v3 | enricher, maybe floor | could not build (PER-173) |
| test runner wrapper | `test-run` units (command, revision, result, log digest) | enricher | needed for `test-agrees` |
| repo test→script map | `test-link` | enricher | static tools miss process-level tests (PER-174) |
| `git check-attr linguist-generated` | `generated` class from attributes at head | inside Git adapter | suggested in `ns/model.clj:143-148` |
| another VCS (jj, hg) | hunks, files | floor | tests whether the protocol is really Git-free |

## 6. Unresolved cases

Each was run through the existing tooling unless marked. Fixture:
`fixtures/edge-cases/` (`build.sh` reproduces it; `packet.json`, `raw.diff`,
`raw-records.txt`, `typechange.txt` are captured).

**6.1 Submodules (D-15).** PER-175 left this unverified. Observed: an added or
bumped submodule becomes an ordinary `text` hunk of class `code` whose lines
are `Subproject commit <sha>` (H-006 `h:22625719` bump, H-007 `h:f8e5948c`
add); `.gitmodules` is its own `code` hunk (H-001). The `160000` mode appears
only in the raw record and is not kept. Options: keep as text; new kind
`submodule` with `{from, to}` commits; exclusion reason `submodule`
(PER-175 reserved it); recurse into the submodule as a nested subject.

**6.2 Type change, file → symlink (D-16). New: the build refuses it.** `--raw`
gives one `T` record; the patch gives two blocks (delete + add), so
`changed-files` exits 4: "diff and --raw disagree on how many files changed (2
patch blocks, 1 records)" (`typechange.txt`). Any range containing a type
change cannot be packeted today. Options: pair the two blocks with the one `T` record by path; new kind
`type-change` with `{from-mode, to-mode}`; split into a delete and an add unit.
Unmerged (`U`) not tested.

**6.3 Renames (D-17).** Pure rename: synthetic `rename` hunk (synthetic H-003).
Rename **with** edit: only the real hunk (edge-cases H-005, `kept.txt`, R083);
the rename appears only on the file unit, which is not a coverage unit, so a
characterization can cover the edit and never mention the move. Hunk ids hash
the **new** path, so a renamed file's unchanged hunks get new ids across
ranges. Options: always emit a rename hunk; keep file-level only; hash old
path. Also undecided: rename threshold (`--find-renames` default 50%), copy
detection (off today; `C` is mapped but never requested).

**6.4 Binary (D-18).** PER-175 settled the id (include full blob ids, needs
`--no-abbrev`; `raw-records.txt` here is captured with it). Open: binary
detection relies on git's header text, which depends on `.gitattributes`
(`binary`, `-diff`) at head; is attribute state provenance? Size of a binary
change is not recorded.

**6.5 Mode changes.** Lone chmod: synthetic `mode` hunk (synthetic H-004).
Chmod plus edit: mode lives only on the file unit, as with renames (not run;
follows from `ns/model.clj:236-254`, where synthetic hunks exist only when
there is no `@@`). Same decision as 6.3.

**6.6 Empty files and CRLF.** Added empty: kind `empty`, class `code` (PER-175
splits kind from class). **Deleted** empty: same shape, status `deleted`
(edge-cases H-004 `h:de4a8dce`). CRLF-only change classifies
`formatting-only` (H-002 `h:6adad910`), correct, but **its `patch` lost the
CRs**: `raw.diff` holds 2 `\r` bytes, the packet's patch none. `verify` passes
only because it re-splits the same way. Feeds D-11.

**6.7 Exclusions (D-19).** None are emitted today. Open: who configures them
(request `options.exclude`, repo file, adapter default); whether a size limit
belongs here or in consumers (`ns/externalize.clj` already cards oversized
hunks after the fact); whether exclusions are digested (PER-175: they are in
the evidence set); closed or open reason vocabulary; whether a claim may
`exclude` an exclusion (no — it is not a unit — but say so).

**6.8 Classification vocabulary (D-20).** Today's closed list
(`ns/model.clj:108-109`) mixes content classes (`code`, `formatting-only`,
`generated`, `lockfile`) with shape classes (`binary`, `rename`, `mode-change`)
that PER-175's `kind` now carries. Open: drop shape classes now that `kind`
exists, or keep them so `exclude` reasons stay the same; add `docs` (PER-172:
`ab3a477` is 34 `code` hunks); add `submodule`, `vendored`; precedence when two
apply (today: lockfile > generated > formatting-only > code); one classifier
per adapter or pluggable classifiers; the generated heuristic's known false
negative (`ns/model.clj:143-148`).

**6.9 Paths.** A space in a path works (H-008 `with space.txt`); paths come
from `--raw -z`. `anchor.cljc:38` still reads paths from `diff --git`, which
git quotes for such names (PER-172). Non-UTF-8 path bytes: not tested; JSON
strings must be valid Unicode, so the protocol must say what happens.

## 7. Suggested order

1. **D-1, D-3** — interface and composition. Everything else attaches to these.
2. **D-7, D-8** — digest scope and versioning. They decide whether provenance
   changes break attestations.
3. **D-11, D-12, D-10** — patch fidelity, line records, verify input. These
   decide the done-criterion ("no adapter-specific parsing").
4. **§6 edge cases** (D-15 to D-20), starting with the type change (a live
   bug) and rename/mode-with-edit (a coverage hole).
5. **D-5, D-6, D-4** — capabilities and the sem join, with §5.3 open beside you.
6. **D-2, D-9, D-13, D-14** — range resolution, errors, ordering, config.
7. Re-check the §5.1 table: every row has a home.
