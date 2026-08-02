# Changelog

This file mirrors the [GitHub releases](https://github.com/vignesh2699v/claude-rebuild-prompt/releases) for this repo. Every future release is appended here as well as published there.

## v1.11 — an outside review, taken seriously

An external reviewer read the whole repo and returned five substantive findings. All five were evaluated on their merits, not applied uniformly — one was extended rather than adopted as stated, and one was scoped as a separate follow-up rather than built in this release.

**1. The skill violated its own point-don't-paste rule, about itself.** SKILL.md and routing-guide.md hardcoded a model table — specific IDs, an effort ladder, pricing tier characterizations, and a claim about which model's safety classifiers decline which content domains. That table is stale the day a new model ships, which is exactly the "copied fact forks from its original" failure the skill's own rule warns every prompt it writes to avoid. Fixed: the guidance is now one dated line — *"as of `<date>`, verify against the live model catalog before trusting these IDs"* — not a table asserted as current.

**2. Every rule existed in three places.** SKILL.md, routing-guide.md, and README's Design notes each restated the funnel rule, the reporting contract, the boundary types, and the standing rules — routing-guide.md at one point said "don't restate them here" directly under a heading that restated them. This was a recurring failure across v1.7–v1.10: `/simplify` caught an instance of it in nearly every release, and each time it was patched locally rather than fixed at the root. This release does the actual split: **SKILL.md holds only imperative steps** (123 lines, down from 273), **routing-guide.md holds only mechanics** — exact strings, schemas, the output template (253 lines, down from ~490) — and **README's Design notes holds all rationale**, restated nowhere else. Combined SKILL.md + routing-guide.md: 767 lines → 376.

**3. `routing-history.md` lived inside the skill's own install directory.** The README's own update instruction is `cp -r <source> ~/.claude/skills/`, which can overwrite that file on a reinstall, and the gitignore-based protection only worked for someone who happens to run the skill's own directory as an untracked path — not true for anyone who version-controls their whole `~/.claude/`. Moved to `~/.claude/rebuild-prompt/history.md`, outside every skill's install path. The stale `routing-history.md` gitignore entry is removed along with it.

**4. The ballot conflated "visible" with "must block."** The stated failure mode this skill exists to prevent is silent routing — routing you can't overrule. The reviewer's point: that's satisfiable by showing the pick and letting the user overrule it, without necessarily blocking on a question every time. Taken in full, this would mean no blocking questions ever, including for genuinely contested picks — evaluated and adjusted rather than adopted as stated, because this user has used the ballot to override the recommended pick repeatedly across this session, and going to zero-block risks losing exactly that behavior. What shipped instead: the existing "uncontested → skip" rule, which v1.8 only applied to single-task jobs, now applies **per task at any job size**. A 3-task job where all 3 picks are individually obvious now delivers with zero questions; a 3-task job where only task 2 is genuinely contested asks about task 2 alone. Task *count* no longer drives the ballot — task *classification* does.

**5. Ten releases, zero measurement.** Every changelog entry to date is reasoning with no evidence attached — no fixture prompts, no baseline-vs-skill comparison, no judge scoring routing accuracy or output quality. This is the same discipline `superpowers:writing-skills` requires of every skill (RED before GREEN — watch it fail before you write the fix) and it was never applied to this skill itself. Agreed as the single highest-leverage gap, and deliberately **not** built in this release: it's a different shape of work (fixture authoring, parallel with/without runs, fresh-context judging) that deserves its own scoped pass rather than being squeezed into a documentation-and-refactor release. Flagged as a follow-up task.

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
