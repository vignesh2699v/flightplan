# Changelog

This file mirrors the [GitHub releases](https://github.com/vignesh2699v/claude-rebuild-prompt/releases) for this repo. Every future release is appended here as well as published there.

## v1.13 — output size tracks job size, cost defaults down, jobs don't reset

Direct feedback, not a review pass: too much of the delivered output went
unread — a big prompt only gets a glance before pasting — effort defaulted
to the top of the ladder regardless of what a task was actually worth, and
it was unclear whether a follow-up message inside the same job should
re-litigate everything already decided.

**Three output tiers, selected by job size, not written by hand each time.**
A one-task fix now returns one fenced line — no model-plan table, no "why
these skills" grid (**Single-shot**). A 2–3 task job gets a five-line
scannable header (Intent / Capabilities / Model plan / Cost band / Flags)
and one short block (**Compact**). Only a job with a real segment boundary,
or four-plus tasks, gets the full segmented treatment that shipped before
(**Full**). Templates for all three: `routing-guide.md` § Output tiers.

**Effort now defaults to `medium`, escalating only where step 0 says the
stakes justify it.** Grilling already asks which assumption is costliest to
get wrong — that answer was being asked and then discarded. It now drives
the one dial that decides both cost and latency, stated in the header's cost
band rather than applied silently.

**A job in progress carries its decisions instead of resetting.** A
follow-up message inside the same session that's plainly a continuation —
same topic, or the results of a prior segment — now carries forward every
ballot pick, the model plan, and settled constraints, decomposing only what's
new, and prints one line naming what carried. A genuinely new topic still
gets a fresh classification. This was the direct answer to "should it reset
every turn": no — full reset would force re-answering ballot questions
already settled a message ago, which is the exact friction the routing-
history log exists to reduce.

**Every delivery closes with a checklist, not an open-ended sign-off.** One
pass/fail line per success criterion, so the user's next message is a
verdict the skill can act on, not prose to re-read — the direct answer to
"check with me if I received what I wanted."

**Caught by the duplication lint before anything shipped:** the new
templates initially repeated the closing-checklist line verbatim four times,
and restructuring the output-template section into three subsections dropped
the zero-width-space escaping that keeps nested example fences from closing
the outer one early — a rendering bug, not just a lint finding. Both fixed
in this release; `scripts/lint-duplication.py` (added this session) is now
part of the pre-release check.

## v1.12 — the first real measurement, and one bug it found

v1.11's fix 5 spun off a dedicated evaluation harness as separate follow-up work rather than building it in the same release as a documentation refactor. This is that follow-up, landing the same day. Ten releases had shipped on reasoning alone; this is the first one with evidence attached. Full method and results: [`eval/2026-08-02-v1.11-results.md`](eval/2026-08-02-v1.11-results.md), fixtures in [`eval/fixtures.md`](eval/fixtures.md).

**Method:** 10 fixture prompts spanning the shapes the skill handles differently, each run twice (a plain baseline response, and the skill's rebuilt-prompt output), scored by fresh-context judges blind to which output came from which condition.

**Result: skill preferred in 5, baseline in 4, toss-up in 1 — not the clean win ten optimistic changelog entries would suggest.** The skill won decisively wherever real dependency chains, subjective claims needing verification, or high-stakes scope guards were load-bearing (a 5-task onboarding job, a payment-module refactor, a "make it premium" redesign). It lost on small, single-shot, already-obvious asks — but that loss traces to a **known confound in how this comparison was built**, not a discovery that routing or segmentation is broken: the skill's contract is to return a prompt for later execution, never to answer directly, and on a trivial task a prepared prompt is a worse deliverable than an answer, because answering *is* the deliverable there. Raised explicitly and decided: the contract stays as-is. Preparing prompts for other sessions is the product, not an accident, and losing this specific comparison on trivial asks is an accepted tradeoff.

**One finding survived the confound and is a real bug.** Given "help me fix the bug" with zero information, baseline asked what the bug was. The skill's inline-grilling fallback instead authorized an xhigh-effort speculative search across logs/tests/recent diffs for "the most likely candidate," committing full effort to a guessed target — the exact behavior grilling exists to prevent. Fixed: when grilling turns up zero real signal, the skill now narrows to diagnosis-only and marks the missing target as the `[?]` gap, instead of picking a plausible one and chasing it.

## v1.11 — an outside review, taken seriously

An external reviewer read the whole repo and returned five substantive findings. All five were evaluated on their merits, not applied uniformly — one was extended rather than adopted as stated, and one was scoped as a separate follow-up rather than built in this release.

**1. The skill violated its own point-don't-paste rule, about itself.** SKILL.md and routing-guide.md hardcoded a model table — specific IDs, an effort ladder, pricing tier characterizations, and a claim about which model's safety classifiers decline which content domains. That table is stale the day a new model ships, which is exactly the "copied fact forks from its original" failure the skill's own rule warns every prompt it writes to avoid. Fixed in two passes: the pricing and safety-classifier claims are deleted outright rather than compressed. The first attempt at compressing the ID list itself — a dated line saying "verify against the live model catalog before trusting these IDs" — was caught by the follow-up `/simplify` pass as still asserting the same specifics as fact, and as phrasing ambiguous enough to read as "perform an external lookup on every run" rather than the intended zero-cost fallback. Reworded: the skill already treats skills/subagents/MCP tools as "read live, never hardcode" (routing-guide.md § Where the capability list comes from) — models get the same discipline now, with **asking the user which models they have** as the default action and the dated snapshot demoted to a fallback reference, not a lookup to perform.

**2. Every rule existed in three places.** SKILL.md, routing-guide.md, and README's Design notes each restated the funnel rule, the reporting contract, the boundary types, and the standing rules — routing-guide.md at one point said "don't restate them here" directly under a heading that restated them. This was a recurring failure across v1.7–v1.10: `/simplify` caught an instance of it in nearly every release, and each time it was patched locally rather than fixed at the root. This release does the split: **SKILL.md holds only imperative steps** (121 lines, down from 273), **routing-guide.md holds only mechanics** — exact strings, schemas, the output template (266 lines, down from ~490).

A second `/simplify` pass on this exact commit (4 fresh review agents, not a self-check) found the split wasn't complete on the first attempt — the segment-boundary rule, the agent reporting contract, and the fresh-context-review fallback chain were still fully duplicated between SKILL.md and routing-guide.md, and routing-guide.md's own "Reminders" section restated two pipeline-step rules in direct violation of its stated "mechanics only" scope. All fixed in the same release, before anything was pushed: SKILL.md now points at routing-guide.md for each of these instead of restating them. Combined SKILL.md + routing-guide.md: 767 lines → 387.

**3. `routing-history.md` lived inside the skill's own install directory.** The README's own update instruction is `cp -r <source> ~/.claude/skills/`, which can overwrite that file on a reinstall, and the gitignore-based protection only worked for someone who happens to run the skill's own directory as an untracked path — not true for anyone who version-controls their whole `~/.claude/`. Moved to `~/.claude/rebuild-prompt/history.md`, outside every skill's install path. The stale `routing-history.md` gitignore entry is removed along with it.

**4. The ballot conflated "visible" with "must block."** The stated failure mode this skill exists to prevent is silent routing — routing you can't overrule. The reviewer's point: that's satisfiable by showing the pick and letting the user overrule it, without necessarily blocking on a question every time. Taken in full, this would mean no blocking questions ever, including for genuinely contested picks — evaluated and adjusted rather than adopted as stated, because this user has used the ballot to override the recommended pick repeatedly across this session, and going to zero-block risks losing exactly that behavior. What shipped instead: the existing "uncontested → skip" rule, which v1.8 only applied to single-task jobs, now applies **per task at any job size**. A 3-task job where all 3 picks are individually obvious now delivers with zero questions; a 3-task job where only task 2 is genuinely contested asks about task 2 alone. Task *count* no longer drives the ballot — task *classification* does.

**5. Ten releases, zero measurement.** Every changelog entry to date is reasoning with no evidence attached — no fixture prompts, no baseline-vs-skill comparison, no judge scoring routing accuracy or output quality. This is the same discipline `superpowers:writing-skills` requires of every skill (RED before GREEN — watch it fail before you write the fix) and it was never applied to this skill itself. Agreed as the single highest-leverage gap, and deliberately **not** built in this release: it's a different shape of work (fixture authoring, parallel with/without runs, fresh-context judging) that deserves its own scoped pass rather than being squeezed into a documentation-and-refactor release. Flagged as a follow-up task.

**Also from the follow-up review:** the "why these skills" output-template example showed one row for a three-task template, demonstrating the exact collapsed-mapping anti-pattern the adjacent rule warns against — expanded to one row per task. The "Single-task shortcut" section was misnamed after finding 4 above made it apply per-task rather than per-job — renamed to "Uncontested-task shortcut," with the previously-unspecified mixed-job case now stated (a contested task gets a table row; an uncontested one states its pick inline in the task body instead). The history-file read was ambiguous between once-per-run and once-per-task now that classification is per-task — clarified to once per run. And a pre-v1.11 heuristic ("past five tasks, assume a finding boundary exists") was dropped during the segments rewrite without being mentioned — correct under the new "task count opens nothing" doctrine, but should have been stated rather than left silent; stated here now.

**Minor:** `grilling` is confirmed as a personal, unpublished skill with no public source — README now says so explicitly rather than implying a link exists. The worked Example now leads the README instead of appearing after two sections of prose.

## v1.10 — no other skill is a hard dependency

Fixes a regression shipped in v1.9, plus two adjacent gaps — all found by asking a single question: **what happens when someone installs this and has no other skills?**

**The regression.** v1.9 moved `grilling` into the pipeline at step 0 with no fallback documented. The degradation clause existed, but it was scoped to the Standing rules section, so step 0 sat outside it. On a session without `grilling` installed, the step was undefined: it would either fail to invoke or silently vanish — taking the feature with it and giving no signal that it was gone.

**The underlying error.** Two categories got blurred. Capabilities the skill *routes to* can thin out to nothing — the output is just less rich, still structured, still tagged with model and effort, only without `/skill` lines. Capabilities the skill *runs itself* cannot thin out, because a missing one breaks the skill's own behaviour rather than the output's richness. `grilling` crossed that line without being given a fallback.

**Fixes:**
- Step 0 grills inline when `grilling` is absent, with a defined shape: what you're actually trying to achieve, what changes if it works, what you've ruled out and why, which assumption would be most expensive to have wrong. Naming an adjacent installed skill is allowed; silently switching to one is not.
- Step 2 skips the ballot when the candidate field is empty, after checking all three sources (skills, subagents, MCP tools). A ballot holding one option is not a choice.
- The self-invocation line is omitted when no task names a skill.
- `/interview-me` is only offered when it's actually in the session listing.

New section *"When capabilities are missing"* states the invariant once: routing narrows, the pipeline never stops, and every substitution or skipped step is named in Flags.

SKILL.md 235 → 273 lines.

## v1.9 — grilling at step 0, model plan, switch points as block boundaries

Three changes, all from one observation: **a per-task model tag was decoration until something enforced it.**

**`grilling` moves to step 0.** It now runs before decomposition rather than being offered after delivery. What it surfaces changes how the work splits, and the split is what routing keys off — findings that land after the ballot land too late to move anything. This partly reverses the "draft prompt before any questions" rule set in v1.1 after a six-question `/interview-me` round; the distinction is real — an interview asks *what to build*, grilling asks *whether the premise holds*.

**Model plan.** Every delivery opens with one: session count, plus a segment → model → effort table. Collapses to a single line when one model covers everything.

**Switch points become block boundaries.** A prompt is delivered as one fenced block per segment, not one block for the whole job. Three things open a boundary: a model or effort change on directly-run work, a finding that would rewrite what follows, or an irreversible step needing approval. A model boundary closes by naming the exact model and effort to switch to, with the next block already written. A finding boundary closes by asking for results and sending you back to `/rebuild-prompt` — the next block should be planned against what happened, not guessed ahead of it. Two exemptions keep blocks from fragmenting: subagent tasks carry their own model and effort so they never force a stop, and a one-rung effort change inside the same model is tagged without breaking the block.

Stop markers inside a single block were considered and rejected (see [Design notes](README.md#design-notes)).

SKILL.md 194 → 235 lines.

## v1.8 — size gate, rounds, model routing, best-practices alignment

Four changes, from a review against Anthropic's published prompt-engineering guidance plus two long-standing friction points.

**Size gate.** A one-task prompt with one obviously-fitting capability skips the ballot — pick and nearest runner-up in a line each, still overrulable.

**Rounds.** Past ~5 tasks, deliver round one only, cut at the first point where a finding would change what follows. Checkpoint gates inside a single prompt were considered and rejected: they pause execution, but stale later instructions are still sitting there.

**Model and effort routing.** Tasks carry `[model: <id> | effort: <level>]`. Effort extends to the real ladder — `low | medium | high | xhigh | max` — since the previous three-level scale capped every prompt one notch below Anthropic's recommended default of `xhigh` for coding and agentic work. Model defaults to `claude-opus-5`, with documented routes to `claude-sonnet-5`, `claude-haiku-4-5`, and `claude-fable-5`.

**`grilling` replaces `/interview-me`** as the post-delivery depth offer.

**Best-practices alignment** against the four Anthropic prompt-engineering docs: the `/code-review` + `/verify` pair collapses to one fresh-context review (self-verification instructions cause over-verification and buy nothing); one sentence of intent is now exempt from the pruning test ("say why, once"); hard constraints go in a `<constraints>` block; every prompt gets a scope/delegation/reversibility guard.

SKILL.md 135 → 194 lines.

## v1.7 — structural rewrite, no behaviour change

252 lines to 135, with every one of the twenty-one Guardrails meanings preserved elsewhere in the file.

**The duplication.** The Guardrails section was twenty-one bullets, of which twenty restated a Core Principle or a pipeline step verbatim in meaning. It accumulated because every release since v1.2 added its rule to *both* the principles and the guardrails — duplication doesn't harden a rule, it inflates its rank and creates three places to edit when it changes.

Two leading words replaced argued-out clusters: the shortlist is a **ballot**, not a recommendation; and the prompt is **never a second source of truth** for a fact, collapsing three separately argued rules into one principle with three habits. Negations dropped from thirty-five to seven. The description shrank from ~90 words to ~55.

## v1.6 — point, don't paste

The skill said "keep it as short as completeness allows" — too weak to act on. The concrete rule now: before inlining any fact, ask where it already lives, and point at it instead of copying it in. Same forking risk as the v1.1 no-context-preamble rule, one level deeper — see [Design notes](README.md#design-notes).

## v1.5 — never hard-wrap a paragraph

The prompt template wrote each paragraph as manually broken ~70–80-character lines. A hard line break is a real newline, and a paste box only reflows text that has none — so every rebuilt prompt pasted visibly ragged, wasting roughly half the box regardless of window size. Every paragraph in the delivered prompt is now one unbroken line.

## v1.0 – v1.4 — foundation

- **v1.0** — first release: decompose, shortlist with visible runner-ups, embed chosen skills per task, automatic code-review + verification, plan/spec tasks rendered as commentable HTML.
- **v1.1** — no context preamble by default; a rebuilt prompt is pasted back into the same conversation, which already holds the facts, and stale memory snapshots restated as present-tense fact were a correctness risk, not just verbosity.
- **v1.2** — self-invoking prompts (the Skill-tool trick that makes pasted `/names` real invocations, since pasting doesn't fire slash-command autocomplete); per-task `[effort: low|medium|high]` hints; routing that narrows a 500-skill session by stack/platform before ranking and reports the funnel.
- **v1.3** — `routing-history.md`: past picks for a matching task shape are surfaced and ranked up one place, never auto-applied, task shape only (never prompt content).
- **v1.4** — every agent-routed task carries a reporting contract: checkpoints, a named artifact per check shape, findings surfaced verbatim; independent tasks marked parallelizable except where they touch the same files.
