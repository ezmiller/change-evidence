Survey of how sem, differential and similar tools are used on GitHub. It answers one question for PER-175: is anyone checking an AI's explanation of a change against the evidence, or do agents only get deterministic facts about the code?

**Answer.** People use sem to get facts about code. Nobody uses it to check claims. Claim-checking exists only in about a dozen small, new, single-author projects, and none of them shows outside users. That is room to build, but there is no demonstrated demand yet.

Date: 2026-11-02. Read-only. No paid calls and no model calls (subagents read local clones only).

## Method and limits

- **GitHub code search was unreachable.** No `gh` auth on this host. The API returns `401 Requires authentication`, and the web page shows "Sign in to search". So the scope's main method, searching workflow files, AGENTS.md and skills for `sem certify`, was **not run**. Substitutes:
  - unauthenticated issue/PR, commit and repository search (10 req/min);
  - GitHub dependents pages (HTML);
  - forks and issues API (60 req/hr);
  - `git clone --depth 1` of every candidate, then grep and reading.
- grep.app, Sourcegraph and crates.io are blocked by the egress filter (HTTP 000). Exa and web search were not used, so the survey stays free.
- Every query, with UTC time, status and result count, is in `github-usage-survey-queries.tsv`. The SHA of every clone is appended to that file.
- **Noise.** Issue search on "sem certify" returned 220 hits, but most are Portuguese ("sem certificado" means "without a certificate"). Owners were counted only when the title or body contains the literal command.
- **What this misses.** Repos that use sem only in files and never mention it in an issue, PR, commit or README, and private repos. Counts below are therefore a **floor**.

## Answer by scope item

### 1. sem: distribution vs adoption

The upstream repo has 3,438★ and 109 forks. 28 of the 100 newest forks were pushed after being forked. These figures come from `sem-forks.json`, which wasn't copied into the docs; see the query log.

**Distinct owners outside Ataraxy-Labs, by how they use sem**

| Use | Owners | Gates? |
|---|---|---|
| sem's GitHub Action: PR comment showing which functions changed | 4: HartBrook/wingdiff, pike00/personal-site, alycda/dotfiles, naylorb/BASS | No. The action always exits 0 (`sem/action/action.yml`, "not blocking the PR") |
| Links `sem-core` as a library | 3: mufeedvh/code2prompt (7,745★, optional entity map), rikuws/remiss (fork of sem-core, PR-review app), rill-vcs/rill (symbol search) | No |
| Bundles the sem binary | 1: backnotprop/plannotator (9,823★; `scripts/install.sh:5-6` pins sem v0.8.0 as an optional semantic-diff sidecar) | No |
| Calls the sem CLI from its own code | ~10: mineclover/context-action-documentation-tooling, calionauta/bb-plugin-stelow, TerminallyLazy/sem-review-loop-agent-zero, tomsej/pi-ext, bendrucker/claude, Jimthetaxguy/IMPULSE-rs, 0x007BA7/codebook, nolainjin/phase-skills, ericfitz/skills, dsaad68/review-with-jev | 3 gate, none on claims (below) |
| Agent skill or docs only | ~6: kevmoo/kevmoo_skills, timseriakov/sem-inspect-weave-skill, CamonZ/review-skills, gohypergiant/agent-skills, Dennis-J-Carroll/glassport, zhangwy324/better-code-review | No |
| Distribution (not adoption) | uniget-org/tools (bot), sudosubin/agents.nix, Leoguy77/pi-packages.nix, chenrui333/homebrew-tap, 6 FreeBSD-family port trees, 6 tomevault-io plugin mirrors, awesome-lists and starred-repo lists, 109 forks | — |

**`sem certify` and `sem check`: no independent use found.**
- `certify` appears outside Ataraxy only in:
  - alycda's skill, which allowlists it and tells the agent to run it (`tools/agents/skills/entity-level-git/SKILL.md:185,204`);
  - a glassport recipe;
  - zhangwy324's research doc, which tried it and **decided not to depend on sem** (`docs/research/existing-tools.md`, "Implications" item 1).
- alycda deliberately leaves `check` off the allowlist (`SKILL.md:21`).
- Neither command appears in any CI workflow among the cloned repos.

**The three projects that gate on sem output check facts, not claims.**
- **TerminallyLazy** blocks an agent from completing until its review checkpoint lists exactly the entities `sem diff` reports, bound to a diff fingerprint (`tools/sem_review_checkpoint.py:89-117`, `helpers/completion_gate.py:593`). That checks coverage only: the agent's own `pass` is accepted.
- **mineclover** exits 1 when a doc binds to an entity `sem entities` doesn't list (`binding-validation.ts:240-262`, `cli.ts:419`).
- **nolainjin** rejects changes whose `sem diff` size breaks a policy (`ripple_check.sh:67,79`).

**Promises.** sem's README frames these as "something an agent claims about the codebase, written down as a check" (`README.md:414`). Issue search for "sem promises" or `.sem/promises` found only the uniget bot. **Nobody is using promises.**

Confidence: **high** for "no gating use of certify or check is visible"; **medium** for the owner counts, because code search was missing.

### 2. differential (thepartly)

17★, 0 forks, no dependents on either tab. 180 issues and PRs, all by one author, gogoout, the only contributor. Every issue-search hit for "thepartly/differential" (13) and the one commit-search hit are in its own repo. Zero READMEs mention it. The stargazers API returned 401, so who starred it is unknown. **No external use.** Confidence: high.

### 3. dills122/independent-reviewer

0★, single author, cloned at `f534bbf`.

- **What it checks:** it validates an AI *reviewer's* claims (findings, evidence gaps, limitations). It does not check explanations of a change.
- **Forward:** yes, structurally.
  - Evidence must name a captured path (`src/orchestrator/response-validation.ts:179,185`).
  - Line ranges must fall inside the frozen file, and symbols must occur in it (`:142-150`).
  - Claims must cite known canonical obligations (`src/contracts/claim-scope.ts:28`).
- **Reverse:** partly.
  - It requires exact coverage of canonical inputs, meaning the requirements (`response-validation.ts:100`, `assertExactLedger :157-161`).
  - Paths the review never inspected become `UNASSESSED`, not an error (`:92-94`). Hunks are not a coverage unit.
- **Revision:** yes. Claims are bound to `snapshotDigest` + `briefDigest` (`claim-scope.ts:10-14`). Claim ids are SHA-256 over JCS canonical JSON (`docs/decisions/018-*.md`).
- **Uncertainty:** yes. `INCONCLUSIVE`, `BLOCKING_UNCERTAINTY_DEMONSTRATED` and `UNASSESSED` (ADR-016).
- **Truth:** judged by a **second, author-blind model**. The runner derives the verdict from that model's structured checks (ADR-020).
- **sem / differential:** neither is used. sem is listed only as an "architecture reference" (`docs/research/2026-09-10-git-context-library-evaluation.md:21`).

Confidence: high.

### 4. Other claim and evidence validators

Found through repository and issue search: `repo-claim-verif-review`, `repo-claims-evidence-diff`, `repo-pr-summary-verify`, `repo-hunk-coverage` and related queries in the log. Each was cloned and its validator code read.

- **Fwd:** claims must cite evidence, and unknown citations are rejected.
- **Rev:** every hunk, file or entity must be accounted for.
- **Rev-bind:** claims are bound to a SHA or digest, and stale ones are rejected.
- **Unc:** claims have a first-class unknown state.

| Project | What the AI claims | Fwd | Rev | Rev-bind | Unc | Truth judged by | Gates? | Real use |
|---|---|---|---|---|---|---|---|---|
| **Our packets** (PER-173) | change summary | yes (`hunks-exist`) | yes (`files-exact`) | yes | yes (gaps) | deterministic | yes | us |
| hokupod/utsuri | intent and hunk notes | yes (`report-model/src/validator.ts:305-334`) | **yes, each hunk once** (`report-builder/src/index.ts:319-336`) | partial (`shaMatch` recorded, not enforced) | yes (`annotations.schema.json:146`) | integrity only | refuses to build | 2★, npm, plugin listings, 1 author |
| zhangwy324/better-code-review | review plan (groups) | yes (`src/planner/validate.ts:142-159`) | yes, homeless nodes go to `ungrouped` (`:275-300`) | yes (`snapshotId`, `:112`) | yes (verified/inferred/possible) | integrity only | falls back to deterministic plan | 0★, 1 author |
| rikuws/remiss | stack plan (atom groups) | yes (`src/stacks/validation.rs:526`) | yes; omissions go to manual review (`:229-244`) and sem stacks need exact coverage (`sem_virtual.rs:685`) | partial (brief cache keyed by head) | yes (`Confidence`) | integrity only | rejects plan | 0★, 1 author; **uses sem-core** |
| joshft/correctful | change claims from diff plus LLM | yes (`internal/llmextract/llmextract.go:270`) | yes, per file (`internal/receipt/validate.go:185-212`) | **yes** (base, head, input digest, signed receipt) | yes | **tests run** | yes, on refuted claims | 0★, self-gating CI, 1 author |
| eutv2022/aibtc-review-surface-verifier | review covered files and hunks | yes (`verifier.py:138-143`) | yes (`:119-131`) | digest of diff bytes (`:116`) | no | set comparison | exit 1 | 0★, 1 commit |
| shubhamattri/reviewhound | review findings | yes: quote, symbol, calls (`checker.py:208-233`) | no | yes, superseded head (`pipeline.py:225`) | yes | AST and quotes, optional test | REQUEST_CHANGES | 0★, 1 author |
| noahogbi/urtext | review claims | partial (`src/score/reconcile.ts:136`) | analyzer coverage only | no | yes (`model` tier) | analyzers | no | 0★, 1 author |
| groundtruth-code-review | review findings | partial: quote and line (`quality_gate/gate.py:88-112`) | no | partial | no | second LLM | no | 0★, alpha |
| bobcob7/loam-refinery | review anchors | partial: anchor exists at ref (`internal/verify/verify.go:169-220`) | no | partial | no | none on truth | exit 1 | 0★, 1 author |
| AnonZ7/fact-gate | numbers and names in PR text | no (regex) | no | no | yes | deterministic | exit 1 | 0★, 1 commit |
| nexpeakcore/deepseek-harness-pr-review | PR-description claims | partial | partial | partial | yes | second LLM | no | **43★**, no CI |
| lemahq/lema-verify | PR description vs diff | closed server | ? | ? | ? | ? | no (client always exits 0) | 1★, hosted |

**Takeaways**
- Nobody pairs sem facts with claim validation except remiss, which validates only *grouping*. It does not check what the brief's prose says.
- No other project has all four checks. correctful comes closest, but it covers files, not hunks.
- Several projects reached the same contract independently: "the model emits ids and prose; deterministic code owns the diff". zhangwy324 notes the same thing (`existing-tools.md`, cross-cutting item 4).
- Projects only on the board, not checked: tell, CodeRabbit Change Stack (closed source), stupify. GitHub lists stupify as a sem dependent, but sem isn't at its HEAD.

Confidence: **high** per row (code was read); **low** that this list is complete.

### 5. sem README: main vs v0.29.0

**No change.** `git diff v0.29.0 HEAD -- README.md` is empty. The only commit since the tag is `4392514` (#540, 2026-10-31): intent search now ranks with BM25, and the edit hook no longer blocks writes to scratch files. So certificate, promises and the `check` exit codes (0 pass / 1 fail / 2 could not decide, `README.md:99,275`) are as PER-174 tested them. Confidence: high.

## What this means for PER-175 (canonical model)

1. **Treat claim and evidence as separate first-class records, and keep coverage defined over hunks.** Every peer that checks coverage uses a hunk or atom set (utsuri, better-code-review, remiss). sem's entities don't cover a change completely, as PER-174 found.
2. **Add an "unaccounted" state rather than failing on omissions.** better-code-review (`ungrouped`) and remiss (manual review) both route omitted units into a visible bucket instead of rejecting the plan. Decide in the model which omissions fail and which only get routed.
3. **Bind to a digest, not just a SHA.** correctful and independent-reviewer hash the canonical input, and independent-reviewer derives claim ids from content. That beats our facts digest only if claims need to keep their identity across rewording. Decide that explicitly.
4. **Keep three tiers of trust in the schema:** verified, inferred and possible (better-code-review, urtext). sem already says `callersComplete`, so its entity facts can't all be marked verified.
5. **Leave semantic truth out of the model.** Every project that judges whether a claim is *true* uses either tests (correctful) or a second LLM (independent-reviewer, groundtruth). The deterministic checks everyone shares are integrity and coverage.

## Demand

**Reading: real room to build, low demand.**
- The supply side is crowded and recent: at least 12 projects, mostly created between August and October 2026, with 0–2★ and one author each.
- The demand side is empty:
  - no dependents on any of them;
  - no issues from anyone but their authors (checked for differential; for the others only the single-commit history was read);
  - the most-starred project of this kind (43★) only posts comments and doesn't block.
- sem shows people want deterministic facts for agents (4 CI users, 3 library users, a 9.8k★ bundler), but nobody adds claim-checking on top of them.

**What would settle it**
1. Authenticated code search, to confirm the "no independent use" result: `"sem certify" path:.github/workflows`, `"sem check" path:.github`, `".sem/promises"`, and AGENTS.md/CLAUDE.md mentions. That needs a `gh` token on this host.
2. Issues or PRs from people other than the authors on utsuri, correctful and remiss. That is about 3 API calls each, not yet run.
3. Whether CodeRabbit or other hosted reviewers ship claim-to-evidence validation. Those products are closed, so this can only come from their docs.

## Not checked

- **Code search** of workflows, AGENTS.md, CLAUDE.md and skill files: blocked, see Method.
- **sem forks:** 9 of 109 weren't fetched, and none were diffed against upstream.
- **Who starred sem or differential:** the stargazers API returned 401.
- **Non-author issues on the scope-4 projects:** only differential's and sem's were counted. sem had 18 issues from accounts with no repo association out of 100 fetched.
- **sem dependents:** only the first page of each of the 8 package tabs was parsed. Every tab had 7 or fewer dependents, so one page covered each.
- **Repos not read in depth:** IMPULSE-rs, codebook, ericfitz/skills and review-with-jev. They were classified by grep only.
