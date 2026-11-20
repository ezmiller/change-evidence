## Theoretical foundations of evidence-constrained change characterization

Background reading for the change-evidence work (PER-171). It names the field this problem belongs to, says what the literature already knows, and gives a self-paced reading order. Nothing depends on it.

**Short answer.** The problem is *attributed generation over a closed evidence set*, organised with the discipline of *assurance cases*. Attributed generation is the NLP field that makes a model's text cite its sources. An assurance case is the safety-engineering practice of arguing a claim from explicit evidence. Add requirements traceability for the both-directions check, and that covers it. The ticket's frame (argument-based assurance applied to AI-generated change comprehension) **mostly holds, with one correction**. An assurance case argues that a *system* has a property, such as "safe". Our packets argue that a *description* is faithful to a change. That is closer to attribution than to assurance. Assurance supplies the structure (claims, evidence, doubts); attribution supplies the claim type.

### How this was checked

- Shell egress from this host reaches GitHub only; every source host refused. Links were checked on 2026-11-04 through the Exa fetch/search tool. "Reached" means the tool returned the page's text. It may serve a cached copy, so this proves the page exists, not that it was live at that moment.
- **P** = primary (the work itself). **S** = secondary (someone describing it). Claims about our code cite `file:line` in this repository.
- Not read in full: the Toulmin book (publisher page only), the Jackson & Ladd paper (abstract only; no free full text found), Necula (ACM abstract only), and DO-178C itself (paywalled). Statements about them rest on those abstracts or on cited secondary sources.

### 1. Literature map

#### A. Change comprehension: what reviewers need from a change description

| Source | P/S | What it says | Why it matters here | Link status |
|---|---|---|---|---|
| Tao, Dang, Xie, Zhang, Kim, "How Do Software Engineers Understand Code Changes? An Exploratory Study in Industry", FSE 2012. [doi](https://doi.org/10.1145/2393596.2393656), [pdf](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/howdosoftwareengineersunderstandcodechanges_fse2012.pdf) | P | A Microsoft survey with interviews. Engineers rank a change's *rationale* as the most important information. Risk and completeness are hard to judge, and "composite" changes (several purposes in one check-in) need decomposing. | It is the empirical case for a structured characterization: rationale, risk and decomposition are exactly what our narrative sections and collapsed groups carry. It also warns that a diff alone cannot supply the rationale. | Both reached |
| Jackson & Ladd, "Semantic Diff: A Tool for Summarizing the Effects of Modifications", ICSM 1994. [doi](https://doi.org/10.1109/ICSM.1994.336770), [author page](https://www.cs.cmu.edu/~Compose/paper_abstracts/dnj/semantic_diff.html) | P (abstract only) | It reports differences between two versions of a procedure as changes in input-output behaviour rather than syntax. So meaning-preserving edits, such as renaming locals, are reported as having no effect. | It is the earliest mechanical *characterization* of a change, and it shows that "what changed" can be computed rather than narrated. That makes it the reference point for evidence units beyond hunks (PER-175). | DOI fetch failed; abstract reached via the CMU author page and Semantic Scholar |
| Barnett, Bird, Brunet, Lahiri, "Helping Developers Help Themselves: Automatic Decomposition of Code Review Changesets", ICSE 2015. [doi](https://doi.org/10.1109/ICSE.2015.35), [MSR page](https://www.microsoft.com/en-us/research/publication/helping-developers-help-themselves-automatic-decomposition-of-code-review-changesets/) | P (abstract only) | ClusterChanges automatically splits a changeset into independent clusters of related diff regions. | It mechanises Tao's decomposition need. *Unverified:* whether its clusters partition every diff region exactly once; full text not read. | Reached |
| Miriyala, Goodman, Vasu, Heydarnoori, "Diff-Grounded Pull Request Description Generation with Structured Evidence", ICSME 2026. [program page](https://conf.researchr.org/details/icsme-2026/icsme-2026-papers/16/Diff-Grounded-Pull-Request-Description-Generation-with-Structured-Evidence) | P (abstract only) | A prompt-only pipeline grounds LLM pull-request descriptions in the diff and judges them with an evidence-scoped LLM judge. The remaining errors are "mainly driven by descriptions missing key changes". | It is the closest academic neighbour. Its dominant failure (omission) is exactly what our reverse-coverage rule catches mechanically, while they measure it with a model judge. | Reached |

#### B. Assurance cases: arguing a claim from evidence

| Source | P/S | What it says | Why it matters here | Link status |
|---|---|---|---|---|
| Rushby, "The Interpretation and Evaluation of Assurance Cases", SRI-CSL-15-01, 2015. [pdf](https://www.csl.sri.com/~rushby/papers/sri-csl-15-1-assurance-cases.pdf) | P | An assurance case is an explicit argument from evidence to a claim. Rushby splits steps into *evidential* steps (evidence weighed until a subclaim counts as settled) and *reasoning* steps (which should be deductive). He reviews arguments by proposing *defeaters*, reasons the argument might be wrong. | It is the best single map of the field. The evidential/reasoning split is the line between what a mechanical validator can check and what needs judgment (§4). | Reached |
| Toulmin, *The Uses of Argument*, 1958 (2nd ed. 2003). [doi](https://doi.org/10.1017/CBO9780511840005) | P (publisher page only) | It models practical argument as claim, data, warrant, backing, qualifier and rebuttal, rather than as formal logic. | It is the ancestor of assurance-case notations. Rushby calls its influence "unfortunate", because it gives up logic's separation of reasoning from subject matter (S: Rushby 2015, summary). Read Toulmin for the vocabulary and Rushby for the critique. | Publisher page reached; text not read |
| GSN Community Standard v3, Assurance Case Working Group, 2021. [doi](https://doi.org/10.65391/r1386), [hub](https://scsc.uk/gsn) | P | It is the normative definition of Goal Structuring Notation: goals (claims), strategies, solutions (evidence), context and assumptions, and how claims are ultimately supported by evidence. CC-BY licensed. | It is the de facto schema vocabulary for claim-evidence graphs, so our claim and evidence types should be mappable to it. | Both reached |
| Kelly & Weaver, "The Goal Structuring Notation – A Safety Argument Notation", 2004. [pdf](https://scsc.uk/documents/acwg/tpk/The_goal_structuring_notation-a_safety_argument_no.pdf) | P | The original readable introduction to GSN, with patterns, modular cases and maintenance under change. | It is shorter than the standard. Its §4.1 asks how a change affects an existing argument, which is our revision-binding question. | Reached |
| Hawkins, Kelly, Knight, Graydon, "A New Approach to creating Clear Safety Arguments", SSS 2011. [pdf](https://www-users.york.ac.uk/~rdh2/papers/HawkinsSSS11.pdf), [doi](https://doi.org/10.1007/978-0-85729-133-2_1) | P | It separates the *argument* (why the claim holds) from a *confidence argument* (why we trust that argument), and names residual gaps "assurance deficits", or blind spots. | This is the same split as our Writer (claims) and Reader (comprehension verdict). "Assurance deficit" is a ready-made term for our `gaps`. | Both reached |
| Bloomfield & Rushby, "Assessing Confidence with Assurance 2.0", 2022/2024. [arXiv](https://arxiv.org/abs/2205.04522) | P | Confidence comes from positive evidence, recorded defeaters with their resolution, and residual doubts, not from one number. | It supports recording doubts as structured data, not prose. | Reached |

#### C. Traceability and provenance

| Source | P/S | What it says | Why it matters here | Link status |
|---|---|---|---|---|
| Gotel & Finkelstein, "An Analysis of the Requirements Traceability Problem", ICRE 1994. [pdf](http://www.gotel.net/research/GOTEL94%20An%20Analysis%20of%20the%20Requirements%20Traceability%20Problem.pdf), [doi](https://doi.org/10.1109/ICRE.1994.292398) | P | It defines requirements traceability as following a requirement's life "in both a forwards and backwards direction". | It is the origin of the bidirectional idea (§5). | Author PDF reached via search; DOI fetch failed |
| NASA Software Engineering Handbook, SWE-052 "Bidirectional Traceability" (NPR 7150.2). [page](https://swehb.nasa.gov/spaces/SWEHBVC/pages/50888903/SWE-052+-+Bidirectional+Traceability) | P (NASA requirement) | It requires bi-directional traces between requirements, design, code and tests, so that "all requirements are addressed and … only what is required is developed". | It is a working, mandated two-way completeness check, and the nearest precedent for reverse coverage. | Reached via Exa (direct fetch refused) |
| Rapita Systems, "Efficient verification through the DO-178C life cycle" (white paper). [pdf](https://www.rapitasystems.com/files/MC-WP-011%20DO-178C%20Verification_2.pdf) | S | DO-178C requires bi-directional traceability. Downstream traces show that all intended function is implemented; upstream traces show that every implementation element exists for an intended function. | It is the aviation version of the same rule. Untraced items must be justified as "derived requirements", which is how our collapsed groups account for a hunk without citing it in the argument. | Reached; DO-178C itself not checked |
| W3C PROV-DM, 2013. [rec](https://www.w3.org/TR/prov-dm/) | P | It is a standard model of provenance: entities, the activities that produce them, and the agents responsible. | It is a borrowed vocabulary for "who or what produced this claim, from which evidence". | Reached |
| Torres-Arias et al., "in-toto: Providing farm-to-table guarantees for bits and bytes", USENIX Security 2019. [page](https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias) | P | It records signed metadata for every supply-chain step, so a consumer can verify that each step was done, by whom, and in order. | It is prior art for revision binding and attestation: claims tied to exact artifacts by hash. | Reached |

#### D. Attributed generation: making model text cite its evidence

| Source | P/S | What it says | Why it matters here | Link status |
|---|---|---|---|---|
| Gao, Yen, Yu, Chen, "Enabling Large Language Models to Generate Text with Citations" (ALCE), EMNLP 2023. [anthology](https://aclanthology.org/2023.emnlp-main.398/), [arXiv](https://arxiv.org/abs/2305.14627) | P | It is a benchmark scoring LLM answers on fluency, correctness and *citation quality*, measured with entailment models. Even the best models lacked complete citation support 50% of the time on ELI5. | It supplies the standard metrics. Both of them judge whether a citation *supports* a claim, which our validator deliberately does not do (§4). | Both reached |
| Liu, Zhang, Liang, "Evaluating Verifiability in Generative Search Engines", 2023. [arXiv](https://arxiv.org/abs/2304.09848) | P | It defines *citation recall* (every statement fully supported by its citations) and *citation precision* (every citation supports its statement). In audits, 51.5% of sentences were fully supported and 74.5% of citations supported their sentence. | It is the clearest definition of the two claim-side directions. Neither checks that every source is used (§5). | Reached |
| Rashkin et al., "Measuring Attribution in Natural Language Generation Models" (AIS), *Computational Linguistics* 2023. [arXiv](https://arxiv.org/abs/2112.12870) | P | It defines "Attributable to Identified Sources" with a human test: is it accurate to say "according to P, s"? | It is the precise meaning of "this claim is supported by this evidence", the judgment our Reader makes and our validator cannot. | Reached |
| Schreieder, Schopf, Färber, "Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with LLMs", ACL 2026. [anthology](https://aclanthology.org/2026.acl-long.1430/), [arXiv](https://arxiv.org/abs/2508.15396) | S (survey) | It surveys 134 papers and 300 metrics, finds the field fragmented in terminology and evaluation, and offers a unified taxonomy. | It is the entry point to the whole AI-side literature and the "evidence-based text generation survey" the ticket names. | Both reached |

#### E. Checkable certificates: why "proof-carrying" is tempting

| Source | P/S | What it says | Why it matters here | Link status |
|---|---|---|---|---|
| Necula, "Proof-Carrying Code", POPL 1997. [doi](https://doi.org/10.1145/263699.263712) | P (abstract only) | Untrusted code arrives with a formal safety proof. The host checks the proof quickly and can then "determine with certainty" that the code obeys a safety policy. | It is the source of the "untrusted producer, cheap trusted checker" shape we copy, and of the word we should not borrow (§3). | Reached |
| McConnell, Mehlhorn, Näher, Schweitzer, "Certifying Algorithms", *Computer Science Review* 2011. [pdf](https://people.mpi-inf.mpg.de/~mehlhorn/ftp/CertifyingAlgorithms.pdf), [doi](https://doi.org/10.1016/j.cosrev.2010.09.009) | P | A certifying algorithm returns its output plus a witness. A simple checker confirms the witness proves the output correct, so the user need not trust the algorithm. | It is the closest formal analogue to our validator, and a precise statement of the bar we do *not* reach: our checker confirms structure, not correctness. | Both reached |

#### F. AI governance and the current AI-specific conversation

| Source | P/S | What it says | Why it matters here | Link status |
|---|---|---|---|---|
| NIST AI 600-1, *Generative AI Profile*, July 2024. [pdf](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), [doi](https://doi.org/10.6028/NIST.AI.600-1) | P | It names *confabulation* as a generative-AI risk, including "confabulated logic or citations that purport to justify or explain the system's answer" (§2.2). It defines high-integrity information as "linked to the original source(s) with appropriate evidence" with "a clear chain of custody" (§2.8). Action MS-2.5-003: "Review and verify sources and citations in GAI system outputs." | It is the governance reason this work exists: model-written citations must themselves be checked. | Reached. §2.2 and §2.8 text read in the PDF; the MS-2.5-003 wording and ID were confirmed only via two secondary transcriptions ([1](https://reliablecontext.com/articles/nist-ai-600-1-generative-ai-profile-confabulation-information-integrity), [2](https://github.com/lawve-ai/awesome-legal-skills/blob/main/skills/nist-ai-rmf-rafal-fryc/references/gai-profile/actions-measure.md)) |
| Murphy et al. (Chechik group), "AssureCode: Structured Justification for Trustworthy Agentic Coding", 2026. [arXiv](https://arxiv.org/abs/2610.29758) | P (preprint) | It adapts GSN-style assurance cases into "justification rationales" for agent-written code. Tool evidence is kept separate from human-resolved "obligations". | It is direct evidence that the assurance-case frame is being applied to AI code now. It differs from ours: it justifies that the *code* matches intent, where we justify that the *description* matches the diff. | Reached |
| Bloomfield, "Understanding: reframing automation and assurance", 2026. [arXiv](https://arxiv.org/abs/2604.05662) | P (preprint) | It warns that AI-generated artefacts "may produce outputs that appear coherent without supporting genuine human comprehension". It proposes making understanding an explicit, assessable part of decisions. | It is the assurance community naming the risk our comprehension verdict addresses. | Reached |

Practitioner work (grey literature, not peer-reviewed). It is useful as evidence of convergence, but it is not foundational.

- Tiwari, Vass, Singh, "Assay: Claims That Decay With the Code", 2026 ([arXiv](https://arxiv.org/abs/2609.36170)). It binds each agent claim to a hash of the code it covers, so the claim goes stale when that code changes. Reached.
- "Evidence-Carrying Changes", rmax.ai, 2026-07-13 ([note](https://rmax.ai/notes/evidence-carrying-changes/)). Reached; it matters for naming (§3).
- AkaraChen/guided-review ([repo](https://github.com/AkaraChen/guided-review)). It requires every claim to cite diff lines and labels claims *observed* or *synthesis*. The README describes a forward check only. Reached.

### 2. Reading ladder

Four tiers. Each one stands alone: stop at any tier and what you have read is complete for that purpose. Free, readable sources come first; paywalled or dense texts come last. Times are estimates for careful reading.

#### Tier 1 — Orientation (45–60 min)

**Goal:** be able to say what field this is and what the validator does and does not promise.

| # | Read | Why | Stop when |
|---|---|---|---|
| 1 | This document: "Short answer" and §4 | Our own summary, in our own terms. | End of §4. (10 min) |
| 2 | Rushby 2015, abstract and executive summary | The assurance-case idea in its author's plainest words: claims, evidence, defeaters, evidential versus reasoning steps. | Chapter 1 begins. (20 min) |
| 3 | Liu, Zhang, Liang 2023, abstract and introduction | Defines citation recall and precision, and shows how often AI citations fail. | Methods begin. (15 min) |
| 4 | Tao et al. 2012, abstract and conclusion | What engineers actually need from a change description: rationale, risk, decomposition. | End of conclusion. (10 min) |

**You understand enough when** you can explain, in one sentence each: what an assurance case is; the two directions in "citation recall and precision"; and why a checked packet can still be wrong.

#### Tier 2 — Working understanding (2–3 h, after Tier 1)

**Goal:** be able to judge a PER-175 canonical-model draft.

| # | Read | Why | Stop when |
|---|---|---|---|
| 5 | Kelly & Weaver 2004, §1–3, then §4.1 and §4.4 | GSN's parts (goal, strategy, solution, context) are the reference vocabulary for claim and evidence types. §4.1 covers arguments under change. | End of §4.4. (40 min) |
| 6 | Hawkins et al. 2011, up to the running example; skim the example | It separates the argument from confidence in it (our Writer and Reader) and defines "assurance deficit" (our `gaps`). | You can say what a confidence argument is for. (40 min) |
| 7 | Gotel & Finkelstein 1994, §1 and §5.1–5.2; then NASA SWE-052, sections 1–3 | Where checking in both directions comes from, and how NASA requires it in practice. | End of SWE-052 "Guidance". (35 min) |
| 8 | Rashkin et al. (AIS), §3 | The exact test for "this evidence supports this claim": the judgment the validator leaves to a reader. | End of §3. (30 min) |
| 9 | This document §5–6, beside the PER-175 description | Applies 5–8 to the model. | End of §6. (15 min) |

**You understand enough when** you can check a PER-175 draft against five questions:

1. Does each claim type map to a GSN goal, and each evidence type to a GSN solution?
2. Is every evidence unit either cited or excluded with a typed reason?
3. Is "evidence supports claim" kept out of the validator?
4. Are gaps structured items rather than prose?
5. Are facts and claims bound to the revision by digest?

#### Tier 3 — Optional deepening modules (pick by topic; each 1–3 h)

| Module | Read | Why | You understand when | Stop when |
|---|---|---|---|---|
| A. Assurance in depth | Rushby 2015, ch. 1–3; Bloomfield & Rushby 2022; GSN Standard v3, Part 0 | How confidence is assessed and doubts recorded. | You can explain why Rushby wants reasoning steps to be deductive. | End of Part 0. (3–4 h) |
| B. Measuring AI citations | ALCE (Gao et al. 2023); Schreieder et al. survey, taxonomy section | How support is scored automatically, and the field's vocabulary. | You know what an entailment-based citation check can and cannot catch. | End of the survey's taxonomy section. (2 h) |
| C. Certificates and checkers | McConnell et al. §1 and §6; then the Necula abstract | The witness-and-checker pattern, and why our checker is weaker than a proof checker. | You can say why "proof-carrying" overclaims. | End of McConnell §6. (1 h) |
| D. Provenance and binding | W3C PROV-Overview; in-toto (USENIX 2019); Assay preprint | How claims are tied to exact artifacts and producers. | You can describe the entity, activity and agent roles for a generated claim. | End of the in-toto design section. (2 h) |
| E. AI governance and current work | NIST AI 600-1 §2.2, §2.8, App. A.1.6; AssureCode; Bloomfield 2026 | The policy language, and where the assurance community is taking AI code. | You can place our validator against "confabulated citations". | End of the AssureCode approach section. (2 h) |
| F. Change comprehension | Tao et al. 2012 in full; Barnett et al. and ICSME 2026 abstracts; Jackson & Ladd abstract | The software-engineering lineage of describing changes. | You know why decomposition and omission are the recurring problems. | End of Tao §6. (1.5 h) |

#### Tier 4 — Full path (~15 h)

Everything, in order. Items already read in a lower tier can be skipped.

| # | Read | Why now | Stop when | Time |
|---|---|---|---|---|
| 1 | Tao et al. 2012 | What people need from a change description. | End of paper. | 45 min |
| 2 | Liu, Zhang, Liang 2023 | Citation recall and precision, and failure rates. | End of results. | 30 min |
| 3 | Rushby 2015, executive summary and ch. 1–3 | The assurance-case idea and the evidential/reasoning split. | End of ch. 3. | 2–3 h |
| 4 | Kelly & Weaver 2004 | GSN, shown concretely in a short paper. | End of paper. | 45 min |
| 5 | Hawkins et al. 2011 | The argument versus confidence in it. | End of paper. | 1 h |
| 6 | Gotel & Finkelstein 1994, §1 and §5; NASA SWE-052 | Where "both directions" comes from. | End of SWE-052 "Guidance". | 1 h |
| 7 | ALCE (Gao et al. 2023) | Automatic citation scoring and its limits. | End of the evaluation-metrics section. | 1 h |
| 8 | Rashkin et al. (AIS), §1–4 | What "supported by" means. | End of §4. | 1.5 h |
| 9 | Necula 1997, introduction; McConnell et al. §1 and §6 | Certificates and checkers. | End of McConnell §6. | 1.5 h |
| 10 | NIST AI 600-1, §2.2, §2.8, App. A.1.6 | The policy language. | End of A.1.6. | 45 min |
| 11 | AssureCode 2026; Bloomfield 2026 | Where the field is heading. | End of each paper's approach section. | 1.5 h |
| 12 | Schreieder et al. survey, taxonomy | A map for going deeper on the AI side. | End of the taxonomy section. | 1 h |
| 13 | Toulmin, chapter on the layout of arguments (optional) | The original vocabulary, read after Rushby's critique. | End of chapter. | 1.5 h |

Deferred on purpose:
- Toulmin is a paywalled book. *Unverified:* the chapter number.
- Necula's full paper is on ACM; only the abstract was checked for free access.
- Jackson & Ladd has no free full text found; its abstract (5 min) is enough until PER-175 needs semantic evidence units.
- DO-178C is paywalled; the Rapita summary covers it.
- Section numbers given above for Tao, Rashkin, Hawkins, ALCE and AssureCode come from page structure seen while checking links. *Unverified:* where a cited section boundary falls exactly.

### 3. Terminology

**Recommend: "evidence-constrained change characterization".**

- *Characterization*, not "summary": it describes and partitions the whole change, which a summary is free not to do.
- *Evidence-constrained* says what the validator enforces. Every claim cites known evidence, and every piece of evidence is placed somewhere. It promises nothing more.
- **"Evidence-carrying" is already taken, and its meaning is broader.** rmax.ai's 2026 note uses "evidence-carrying changes" for a change that ships with tests, scans, provenance and a policy decision about whether it is *acceptable*. That is a different object from a faithful *description*. "Evidence-carrying" also suggests a package that a remote consumer checks, which invites the proof-carrying comparison below.

**Not "proof-carrying".** In Necula's proof-carrying code, the attached certificate is a formal proof, and checking it shows "with certainty" that the code meets a safety policy (Necula 1997, abstract). A certifying algorithm's checker likewise establishes that the output is *correct* (McConnell et al., §1). Our validator establishes no truth about any claim. It checks that references resolve and coverage is total, so the cited evidence may still fail to support the sentence. In Rushby's terms, evidence is *weighed*, not proved (Rushby 2015, summary). "Proof" would overstate the guarantee to exactly the reader most likely to trust it.

### 4. Guarantees and non-guarantees

**What a mechanical validator can establish**, with where ours does it:

| Guarantee | Plain meaning | Ours |
|---|---|---|
| Reference integrity | Every cited id names real evidence. | `reference-violations`, `skills/engineering-manager/scripts/review-packet/review_packet/validate.clj:580` |
| Forward citation | Every claim cites at least one piece of evidence. | Contract rule 8, `skills/engineering-manager/references/review-packet-contract.md:238` |
| Reverse coverage | Every piece of evidence is placed exactly once, either cited in the argument or set aside with a stated reason. | `coverage-violations`, `validate.clj:599` |
| Revision binding | The evidence belongs to one exact base and head, and has not been edited since. | `:range` is a fact key (`.../review_packet/model.clj:349`); the facts digest (`model.clj:375`) is recomputed and compared (`validate.clj:485`). The verdict is bound to the narrative's digest (`validate.clj:955`). |
| Explicit uncertainty | The document has a place for what was not checked or not known. | `gaps` is a writer key (`review-packet-contract.md:226`). *Not checked:* whether the validator requires it to be non-empty. |

**What it cannot establish:**

- **That a claim is true, or that its evidence supports it.** Deciding whether "according to this hunk, X" is accurate is a judgment (Rashkin et al., AIS). Automated versions use entailment models and are themselves fallible (Gao et al. 2023).
- **That the interpretation is the right one.** A correctly cited sentence can still mislead by emphasis or omission *inside* a hunk it cites.
- **Why the change was made.** The diff records what changed, not why (Tao et al. 2012, on DeltaDoc's limits).
- **That the risks and gaps lists are complete.** Defeaters are found by deliberate search, not by checking structure (Rushby 2015; Bloomfield & Rushby 2022).

In one sentence: the validator proves the description is *about the whole change and only the change*; whether it is *right* stays with a reader, which is why the comprehension verdict exists as a separate, digest-bound step.

### 5. Prior art on bidirectional completeness

Bidirectional completeness means checking both claim→evidence and evidence→claim.

- **Requirements engineering: yes, both directions, mechanically.** Bidirectional traceability is defined by Gotel & Finkelstein (1994), mandated by NASA SWE-052, and required by DO-178C (S: Rapita). Code with no parent requirement must be justified, and every requirement must reach code. It differs from ours in that traces need only *exist*; they need not be *exactly once*. Whether a link is correct is still judged by people.
- **Attributed generation: claim side only.** Citation recall and precision (Liu et al. 2023; ALCE) both start from the claims. A closer reverse measure is KaLMA's citation recall over a gold "minimum knowledge set" ("Towards Verifiable Generation", 2023, [arXiv 2310.05634](https://arxiv.org/abs/2310.05634), reached via search). It covers a hand-picked subset, not every evidence unit. **I found no work requiring every evidence unit to be cited or explicitly excluded.**
- **Change description: measured, not enforced.** ICSME 2026 finds omission is the main error but detects it with an LLM judge. guided-review's README describes forward citation only.
- **Assurance cases: conceptual only.** Hawkins et al.'s "assurance deficits" are identified blind spots, a reverse question asked by people, not checked by a program.

**Conclusion:** two-way traceability is old and standard. Exactly-once partition of a mechanically derived evidence set across claims and reasoned exclusions (`validate.clj:599`) has no precedent I could find. This was a search of roughly 15 queries, not a systematic review.

### 6. Implications for the canonical model (PER-175)

1. **Keep evidential and reasoning links distinct.** A claim either cites evidence or is built from other claims (Rushby 2015). The validator checks the first kind, and a reader judges both.
2. **Make reverse coverage a named invariant with typed exclusions.** Every evidence unit is cited or set aside with a reason, as DO-178C does for derived requirements. Collapsed groups are the current form.
3. **Label each claim observed or inferred.** Separate what was read directly from what was concluded (guided-review; Hawkins's argument/confidence split).
4. **Make gaps and defeaters structured items, not prose,** each tied to the claims it threatens (Hawkins "assurance deficits"; Bloomfield & Rushby).
5. **Record claim provenance in PROV terms:** the claim as an entity, the generation run as an activity, and the model and prompt version as an agent (W3C PROV-DM; NIST AI 600-1 App. A.1.6).
6. **Bind both facts and claims to the revision by digest,** so a claim goes stale when its evidence changes (current facts digest; Assay).
7. **Leave "does this evidence support this claim" out of the core.** It needs judgment (AIS) and belongs in a separately recorded, digest-bound verdict.

### Not checked

- The full text of Toulmin, Jackson & Ladd, Necula and DO-178C (see "How this was checked").
- Whether ClusterChanges partitions every diff region (§1A).
- The Toulmin chapter number (§2).
- Whether our validator rejects an empty `gaps` (§4).
- Systematic coverage of the attribution literature: the §5 negative result rests on targeted search, not a full review.
