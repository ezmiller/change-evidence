## sem as an evidence adapter — spike

This spike decides whether the evidence library (PER-171) can treat sem as a source of
evidence beyond hunks. It informs the canonical model (D), which prefers to follow it.

## Verdict

**No — not as a primary adapter. Yes — as an optional enrichment layer over Git hunks.**

sem's named-entity diff is deterministic, covers every hunk on our fixtures, and detects
renames and moves. But four things it emits cannot be trusted as evidence on their own:

1. **Ids are line-dependent where it matters.** Orphan (top-level) regions and duplicate
   names, such as repeated Markdown headings, get `@L…` suffixes that move when unrelated
   lines are inserted above.
2. **Impact silently drops entities.** `impact --diff` skips orphans with a stderr line
   and still exits 0.
3. **Affected tests are blind here.** Our tests drive scripts as processes, and sem does not
   extract Clojure `deftest` forms. Every fixture reports `noTestReaches: true`.
4. **No provenance or schema version in the output.** `sem diff` sets `commitSha: null`;
   no output carries the sem version.

Use Git hunks as the evidence floor. Add sem entities as a second evidence type that
**points at hunk ids**, never replaces them, and wrap sem with provenance it lacks.

## What was run

| | |
|---|---|
| sem | 0.29.0, `sem-linux-x86_64.tar.gz` from the GitHub release, sha256 `30fa7ab7…22dc3` matches `checksums.txt` |
| Date | 2026-11-01 |
| Environment | isolated `HOME`; telemetry off; no cloud login; `SEM_NO_NETWORK=1` gives byte-identical certify output |
| Inputs | fixtures `2c0f3e7`, `ab3a477`, `701751b` in a scratch clone; a synthetic repo for rename, move, binary, mode change, empty file, multimethods, duplicate headings, tests |
| Samples | `docs/change-evidence/sem-samples/` (content fields clipped) |
| Paths | `review_packet/…` is under `skills/engineering-manager/scripts/review-packet/` on `main` |

## Capability, by evidence unit

| Unit | Machine-readable? | Robust? | Evidence |
|---|---|---|---|
| Changed entities | Yes: `sem diff --format json` → `changes[]` with `entityId`, `changeType`, `entityType`, line ranges, before/after content, `structuralChange` | Partly. Named functions/vars stable; shell top level and headings are line-ranged orphans | `sem-samples/diff-701751b-model.json`, `diff-2c0f3e7.json` |
| Renames / moves | Yes: `changeType` `renamed`/`moved`, `oldEntityName`, `oldFilePath` | Yes on the synthetic case. A move that also edits the body reports only `moved`; the edit shows as `structuralChange: true` | `sem-samples/diff-synthetic.json` |
| Dependencies / callers | Yes: `impact --json` (`dependencies`, `dependents`, `possibleCallers`), `graph --json` (2,184 entities, 1,898 edges) | Honest but noisy. `callersComplete` and `incompleteBecause` flag gaps; possible callers are name matches, e.g. 33 files for `lease`, mostly Markdown | `sem-samples/impact-701751b-model.json` |
| Impact / blast radius | Yes: `impact.entities` (depth 2 default), `certify.cone`, `untouchedCallers` | No as a completeness claim: orphans dropped (7 of 27 on `701751b`), static graph only (`limits` field says so) | `certify-701751b-excerpt.json` |
| Affected tests | Yes: `tests[]`, `noTestReaches`, `certify.affectedTests` | Python test found transitively. Clojure `deftest` not extracted (`find --in test/core_test.clj` → `[]`). This repo: zero on every fixture, though `run-tests.sh` exercises `kk-review-packet` | `impact-tests-synthetic.jsonl` |
| Range identity / provenance | Only `certify` (`base`, `head` full SHAs) | No. `diff` has `commitSha: null`, `author: null`; `impact` JSONL has no range; nothing carries sem's version or flags | all samples |

Other omissions, from the synthetic repo: **mode changes and added empty files do not
appear at all** (git: 6 files; sem `fileCount`: 4). Binary changes appear with no hashes.
Our model gives each of these a synthetic hunk (`review_packet/model.clj:240-254`).

## One result mapped by hand

`701751b`, file `review_packet/model.clj`. Packet hunk ids from the existing
`gitdiff`/`model` code (`sem-samples/packet-hunks-701751b-model.json`); entities from
`sem diff` and `sem certify`.

| sem entity (`…/model.clj::`) | change | lines new (old) | packet hunks | sem extra |
|---|---|---|---|---|
| `var::key-order` | modified | 309-324 | H-020 `h:b9a201e6` | untouched caller `ordered` |
| `var::fact-keys` | modified | 343-349 | H-021 `h:20d49c70` | untouched caller `facts-digest` |
| `var::rewrites` | added | 411-413 | H-022 `h:9fd36116` | — |
| `function::chain-break` | added | 415-423 | H-022 `h:9fd36116` | — |
| `function::build-packet` | modified | 425-508 (411-493) | H-022, H-023 `h:62962ed7` | caller `run` in `build.clj`, `callersComplete: false` |

What the mapping shows:

- **The relation is many-to-many.** One hunk (H-022) spans three entities; one entity
  (`build-packet`) spans two hunks. Entities cannot replace hunks as the coverage unit.
  They are a second axis, joined by `(path, line range) ∩ hunk range`.
- **sem adds something hunks cannot.** `fact-keys → facts-digest` is real: `fact-keys`
  feeds the digest (`model.clj:380`). That is exactly the dependency a reviewer needs.
- **Signature changes are over-reported for Clojure.** sem treats the head of a form,
  docstring included, as its signature, so `css` and `fact-keys` count as signature changes.
- Coverage: every zero-context Git hunk (`git diff -U0`) overlaps some sem entity —
  `2c0f3e7` 2/2, `ab3a477` 70/70, `701751b` 41/41. All 26 packet hunks of `701751b` do too.

Candidate evidence units this suggests for D:

```json
{"type": "entity-change",
 "id": "e:<sha256(path, entityType, entityName, changeType)>[:8]",
 "path": "…/review_packet/model.clj",
 "entity": {"type": "function", "name": "build-packet"},
 "change": "modified",
 "hunks": ["h:9fd36116", "h:62962ed7"],
 "source": {"tool": "sem", "version": "0.29.0", "argv": ["diff", "--commit", "701751b", "--json"]}}

{"type": "dependency",
 "from": "…/model.clj::function::facts-digest", "to": "…/model.clj::var::fact-keys",
 "complete": true,
 "source": {"tool": "sem", "version": "0.29.0"}}
```

Orphan regions should not become entity evidence; their hunks already cover them.

## Identifier stability

| Id form | Stable under line shift? | Stable under file move? | Evidence |
|---|---|---|---|
| `path::function::name` | Yes | No (path is part of id) | 701751b ids unchanged by position |
| `path::orphan::modified@L283-341` | **No**: 5 lines inserted above → `@L288-346` | No | re-run of `2c0f3e7` on a padded parent |
| duplicate names, e.g. `doc.md::heading::Notes@L5` | **No** | No | synthetic repo |
| `path::method::area/:circle` (defmethod) | Yes | No | synthetic repo |

Our hunk id hashes content, not position (`review_packet/model.clj:86-87`), so a packet id
survives a shift that changes sem's. The library should derive its own entity id from
`(path, type, name)` and refuse sem's `@L` forms as identity.

Field names differ by verb: `diff` uses `entityId`, `filePath`; `graph` uses `id`;
`find` uses `file`, `start_line`. An adapter must normalize per verb.

## Versioning

- 0.x with 68 releases since 2026-02-05; latest v0.29.0 on 2026-10-30
  ([releases](https://github.com/Ataraxy-Labs/sem/releases)).
- No schema version in any JSON output. The CHANGELOG states CLI `--json` stayed unchanged
  through the 0.27 verb consolidation and the MCP shape changes in 0.28.2, so `--json` is
  treated as a compatibility surface in practice, not by contract.
- Determinism: repeated runs were byte-identical (`diff` on `ab3a477` and the synthetic repo; `certify` on `701751b`).
- **Pin the binary by hash.** `sem config update` self-updates; the `update-check.json`
  cache shows it contacts the release server. nixpkgs `sem` is an unrelated package
  (Semaphore CI CLI); upstream ships its own `flake.nix` / `package.nix`.

## Licensing

`MIT OR Apache-2.0` (`Cargo.toml` at v0.29.0; repo has `LICENSE-MIT` and `LICENSE-APACHE`).
GitHub's API reports only Apache-2.0; the website says MIT. Both are permissive; invoking a
binary carries no obligation. Adoption: 3,436 stars, 108 forks (GitHub API, 2026-11-01).

## Cost

On this repo (208 files, ~52k lines), cold cache:

| Command | Wall | Peak RSS |
|---|---|---|
| `diff --commit` | 0.03-0.37s | 27-109 MB |
| `impact --diff` | ~1.0s | 60-264 MB |
| `certify` | ~0.47s | ~300 MB |
| `graph` | 0.35s | ~247 MB |

Binary is 94 MB. Cache lives under `$HOME/.cache/sem` (~10 MB here); nothing is written
into the repository.

## Failure behavior

| Case | Result |
|---|---|
| Unknown ref | exit 1, `Error: git error: revspec … not found` |
| Not a git repo | exit 1, `Error: not a git repository` |
| Unknown entity | exit 1 |
| Bad certify range | exit 2 |
| Orphans in `impact --diff` | **exit 0**, stderr `Entity ID … not found`; report omits them |
| Cloud consent on | diff uploaded after printing (opt-in per repo; off by default) |

An adapter must treat any stderr from `impact` as incomplete evidence, and set
`SEM_NO_NETWORK=1`, `SEM_NO_UPDATE_CHECK=1`, `SEM_NO_TELEMETRY=1`.

## What remains if sem is not used

- **Hunks, renames, binary, mode, empty files**: the native Git adapter already produces
  all of these with content-hash ids (`review_packet/model.clj:208-264`).
- **Entities and dependencies for Clojure**: next best candidate is **clj-kondo analysis
  output** (var definitions and usages with positions, EDN/JSON). It is in nixpkgs
  (2026.01.19). Unverified for this use: not run in this spike.
- **Affected tests**: no static tool sees our process-level tests. That evidence needs a
  test→script map maintained in the repo, or coverage recorded at test time.

## Effect on the plan

- Node **S** is now verified; `D prefers S` can stay soft.
- D should model entity evidence as an optional type that cites hunk ids, with a
  per-source `complete` flag. Coverage stays defined over hunks.
- If an sem adapter is built later, it needs: pinned binary hash, offline env vars, its own
  ids, provenance (`base`, `head`, version, argv) added by the wrapper, and stderr treated as
  failure.
