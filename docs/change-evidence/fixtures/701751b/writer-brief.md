Review packet brief — PER-128 · packet p-20261101-88dfd0 · draft 1 of 1

This is a research fixture run for PER-172 (mapping the change-evidence system), not a packet Ethan will review. Ethan approved this one writer run. Do the job exactly as you would for a live packet.

Write the packet's narrative and return it as one ```json block. Echo "packet/id": "p-20261101-88dfd0".
Contract: fx/repo/skills/engineering-manager/references/review-packet-contract.md
Worked example: fx/repo/skills/engineering-manager/tests/fixtures/summary-writer/
A reader who has never seen this system reads the result, and sends it back if they cannot explain it.

Facts:     fx/run-701751b/packet.json
Diff:      fx/run-701751b/raw.diff
Ticket:    PER-128 — Handle rebased review packets as chain breaks
Workspace: personal · project botserver-nix
Worktree:  fx/repo
Range:     701751b^ afb0c22e..701751b2 (701751b)
Stats:     10 files · 26 hunks · +164 −38

Commits:
  701751b feat(review-packet): treat a rebased follow-up as an explicit review-chain break (PER-128)

Note: this packet covers one commit, the first of the five the hand-off below describes (head 021a727). Argue only what is in this diff; anything the hand-off describes that is not in it belongs in gaps or scope.out.

Programmer's hand-off (comment 01a16075-c75b-7179-a36d-171d1451759f on PER-128):

**Rebased review packets show an explicit chain break (PER-128)** · `PER-128-handle-rebased-review-packets-chain-breaks` · `021a727`

Done locally: 5 commits on the branch, not pushed. Ready to leave the machine, so assigning to Gatekeeper.

**Intent.** When a branch is rebased after Ethan reviewed it, the next packet must say plainly that no incremental diff exists, instead of quietly showing the whole change as if nothing happened. It must also let him approve the rebased revision and, if he chooses, a force-push that can only replace the exact commit on origin.

**System context.** A review packet is a static page King Kong builds for Ethan before any code leaves the machine. `kk-review-packet build` collects the diff and facts into a bundle, `render` turns that into `review.html`, and a small service behind the page records Ethan's approval in the ticket's history. Gatekeeper later publishes only what that approval allows. A follow-up packet normally opens on `action.diff`: the diff from the last packet Ethan acted on to the new head.

**Existing problem.** After a rebase, the old reviewed head is no longer in the branch's history, so no delta can be computed. The build already fell back to a full packet, but the page only showed one muted line ("No packet-to-packet diff: the branch was rebased"). It never showed the SHAs involved, never linked the earlier review clearly, and the approval page could not grant a force-push, which a rebased branch that is already on origin needs.

**Larger objective.** Trustworthy incremental review packets (PER-56, PER-117, PER-119).

**This ticket's role.** It handles a rewrite as an explicit break and adds an approval path for it. Reconstructing a delta across the rewrite (range-diff, patch equivalence) belongs to PER-129.

**Scope boundaries.**
- In: a `chain-break` packet fact; a prominent break section on `review.html`; a force-push choice on the approval page, bound to the remote head the packet recorded; the break packet becoming the baseline for later follow-ups; tests; the packet contract and approval docs.
- Out: range-diff reconstruction (PER-129). Gatekeeper's check that refuses a force-push when origin has moved was already built (PER-102), so this ticket reuses it unchanged.

**Reading logic.**
1. Detecting the break: `scripts/kk-review-packet.sh` records `origin/<branch>` as last fetched. `review_packet/model.clj` adds `chain-break` (reason, the packet Ethan acted on, its reviewed head, the remote ref and remote head) when the chain reason is `not-descendant` or `predecessor-head-missing`. `build.clj` passes it through.
2. Showing it: `review_packet/render.clj` `break-section` sits under the packet history and before the title. It shows why there is no delta, a link to the acted-on packet with Ethan's response, and four full SHAs: last reviewed head, comparison base, current head, remote head. It then says approval covers exactly the current head and whether a force-push is on offer. The old muted line is suppressed on break packets.
3. Recording it: `kk-packet.sh` copies `chain_break`, `remote_ref` and `remote_head` into the `built` history event and tells the writer this is a fresh review of rewritten history. `lib/kk-approval.sh` and `kk-approval.sh` expose these fields in `packet_facts`.
4. Approving it: `review_feedback/approval.clj` offers a fourth choice, "Approve and force-push", only on a break where origin holds a different commit. The lease is the recorded remote head, stored with the server-side nonce, so whatever the browser sends is ignored. `kk-packet-approval.sh` accepts `force-push` only with that lease and only for that ticket's newest break packet, then calls `kk-approval decide --action force-push --lease`. Gatekeeper's existing `kk-dispatch check --step force-push` pushes with `--force-with-lease` and refuses if origin has moved.
5. The anchor needed no code change. A break packet is a full packet, so once Ethan gives feedback on it or decides it, `kk_ph_follow` uses it as the baseline and the next descendant follow-up is incremental from it. Tests prove this.
6. Supporting: `approval.cljs` shows the remote head and lease. Docs: `references/review-packet-contract.md` (new *Review-chain breaks* section and the `chain-break` fact), `packet-approval.md`, `review-feedback.md`.

**Risks and edge cases.**
- `remote/head` is whatever the worktree last fetched, because the build never touches the network. If it is stale, Ethan approves a stale lease and Gatekeeper refuses. That is safe but needs a new decision.
- With no `origin/<branch>`, the page says an ordinary push publishes it, and no force-push is offered.
- If origin already holds the head, no force-push is offered, and a forged one is refused (409).
- `base-moved` without a rewrite is not treated as a break. Its handling is unchanged.
- `packet_facts` gained three fields. Anything that compares that object exactly needs updating; the one test that did is updated.

**Tests run.**
```
skills/engineering-manager/tests/run-tests.sh      (branch, 021a727)
1542 passed, 8 failed
skills/engineering-manager/tests/run-tests.sh      (origin/main, afb0c22, baseline)
1530 passed, 8 failed
```
- The 8 failures are the same on both, so none comes from this change: kk-graph ×2; PER-102 kk-dispatch force-push ×5 (the test helper `fp_decisions` reads the history without unpacking it); one PER-95 watch check.
- New section *review-chain breaks (PER-128)*, 8 checks:
  - a rebase after feedback records `chain-break` with the acted-on packet, its head and origin's head;
  - the break section comes before the title, with the reason, the link and Ethan's response;
  - all four SHAs are shown in full;
  - the approval wording names the exact head and the lease;
  - the page is the whole diff against main;
  - a reviewed head missing from the repository is also a break, and with no origin branch the page says an ordinary push publishes it;
  - feedback or a decision on the break packet makes it the anchor;
  - the next descendant packet is incremental from it, with an exact `action.diff`.
- Approval (PER-78 section), 4 new checks:
  - `kk-packet-approval` refuses a wrong lease, a missing lease, and a lease without force-push, and grants force-push with the recorded lease, giving a `force-push`-only job at that lease;
  - the page offers the fourth choice with the right consequence text;
  - posting it records that lease even when the page sends another one, and dispatches;
  - a remote already at the head gets no choice, and a forced post is refused.
- Two existing rebased-page assertions now expect the break section.
- Not run: shellcheck (not on PATH here; the nix build enforces it); the browser and Squint checks (no `REVIEW_FEEDBACK_SQUINT`), so the `approval.cljs` change is untested in a browser.

**Known gaps.**
- The approval page's new fields and lease line in `approval.cljs` were not exercised in a browser.
- The new writer-brief line for break packets in `kk-packet.sh` has no direct test.

Test evidence:
**Tests run.**
```
skills/engineering-manager/tests/run-tests.sh      (branch, 021a727)
1542 passed, 8 failed
skills/engineering-manager/tests/run-tests.sh      (origin/main, afb0c22, baseline)
1530 passed, 8 failed
```
- The 8 failures are the same on both, so none comes from this change: kk-graph ×2; PER-102 kk-dispatch force-push ×5 (the test helper `fp_decisions` reads the history without unpacking it); one PER-95 watch check.
- New section *review-chain breaks (PER-128)*, 8 checks:
  - a rebase after feedback records `chain-break` with the acted-on packet, its head and origin's head;
  - the break section comes before the title, with the reason, the link and Ethan's response;
  - all four SHAs are shown in full;
  - the approval wording names the exact head and the lease;
  - the page is the whole diff against main;
  - a reviewed head missing from the repository is also a break, and with no origin branch the page says an ordinary push publishes it;
  - feedback or a decision on the break packet makes it the anchor;
  - the next descendant packet is incremental from it, with an exact `action.diff`.
- Approval (PER-78 section), 4 new checks:
  - `kk-packet-approval` refuses a wrong lease, a missing lease, and a lease without force-push, and grants force-push with the recorded lease, giving a `force-push`-only job at that lease;
  - the page offers the fourth choice with the right consequence text;
  - posting it records that lease even when the page sends another one, and dispatches;
  - a remote already at the head gets no choice, and a forced post is refused.
- Two existing rebased-page assertions now expect the break section.
- Not run: shellcheck (not on PATH here; the nix build enforces it); the browser and Squint checks (no `REVIEW_FEEDBACK_SQUINT`), so the `approval.cljs` change is untested in a browser.


Return the JSON as a comment on this issue. Do not edit any file.
