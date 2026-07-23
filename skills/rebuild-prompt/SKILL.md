---
name: rebuild-prompt
description: Use when the user runs /rebuild-prompt or asks to "rebuild", "polish", "optimize", or "add the right skills/agents to" a rough prompt. Takes a vague or multi-task prompt and routes it to the best-fit installed Skills / subagents / MCP tools, then immediately RETURNS a polished ready-to-paste prompt with the /skill invocations embedded per task (unresolved ambiguity is flagged inline with a default, not gated behind questions). Code-writing tasks automatically get a trailing code-review + verify pass; plan/spec-producing tasks are routed to render as a commentable HTML artifact instead of a bare .md. It never executes the prompt — the user runs it themselves.
---

# Rebuild Prompt

Turn a rough, generic, or multi-task prompt into a **polished, ready-to-use
prompt with the right `/skill` invocations embedded**. The user copies the
result and runs it themselves — this skill's output is a prompt, never an
executed task.

## Core principles

**The deliverable is a prompt.** A single copy-paste block: the chosen
`/skill`s per task, followed by a rewritten, high-signal version of what the
user asked for — implicit intent made explicit, success criteria added,
ambiguity either defaulted-and-flagged or resolved by the rare
skill-determining question. Stop after delivering it. Do not execute it, do
not offer to execute it beyond a single closing line.

**The pasted prompt must self-invoke its skills.** Pasting text does not
fire the editor's slash-command autocomplete, and only one slash command can
lead a message — so a multi-task prompt can never be UI-tagged, by design.
Every rebuilt prompt therefore **opens with a line instructing the receiving
session to invoke each named skill itself via the Skill tool.** Use the
exact registered skill names, since that line is what turns them from inert
text into actual invocations. Never tell the user to tag skills by hand.

**Annotate each task with an effort hint** — `[effort: low|medium|high]`
after the task heading. Mechanical work is low; judgment-heavy design and
adversarial verification are high. This is a second routing axis: not just
*which* capability, but *how much care* the task warrants.

**Default to NO context preamble — go straight into the tasks.** The prompt
is normally pasted back into the same conversation, whose window already
holds the project facts. Restating them wastes tokens and, worse, ages
badly: context copied out of memory files or earlier turns is a snapshot,
and a snapshot restated as present-tense fact is a correctness risk.

Include a shared context block ONLY when one of these is true:
- The user says (or it's evident) they're pasting into a **fresh session**.
- A fact is **costly to get wrong** and not inferable — a hard constraint
  ("don't publish, it goes straight to production"), a destructive-action
  guard, or a credential/permission boundary.

When included, apply the pruning test to every single line: **"would the
task break, or go wrong, without this?"** IDs, paths, hard constraints and
non-obvious gotchas pass. Project history, what-was-built-when narrative,
and background recap do not. Two or three lines is a normal context block;
a paragraph of history is a failure of this test.

Anything restated from **memory files or compacted earlier turns** — rather
than freshly read this turn — must be marked as a snapshot ("as of <date>,
verify"), never asserted as current fact.

**Route only against what exists.** The available Skills, subagent types, and
MCP tools are listed in your current session context. Match against that live
list — **never invent a capability name.** Flag anything that needs auth, is
disconnected, or has a setup precondition (e.g. a CLI that must run first).

**Deliver fast, with one gate.** The only thing that gates delivery is the
user's choice of capability per task (step 2) — never a requirements
interview. Present shortlists, get the picks, write the prompt. Scope
ambiguity is defaulted-and-flagged inline, not asked about.

**Show your routing reasoning.** Never silently exclude a plausible skill.
If a capability was considered and passed over, that belongs in the
shortlist with the reason — the user cannot overrule reasoning they can't
see, and invisible routing decisions are this skill's main failure mode.

**Never construct a single-option question.** AskUserQuestion requires ≥2 real
options and will error otherwise. If there's no natural discrete choice set —
e.g. "which project?" with nothing inferable from the session — either ask in
plain text (no tool call), or, if there's known relevant context (recent
projects, prior memories), offer those as multiple-choice options ("Other" is
always available as the escape hatch). Never pass a single fabricated option
just to satisfy the tool's shape.

## The pipeline

### 1. Understand & decompose
Read the raw prompt. Identify the real intent(s). If it holds multiple tasks,
split them and order by dependency. Pull in relevant context you already have
(memory, project files) — don't ask about things you can look up.

### 2. Shortlist candidates per task — then let the user choose
Do **not** silently pick one capability per task. For each task, surface a
ranked shortlist of **2–3 real candidates** from the live session listing,
then let the user choose before the prompt is written.

For each task present:
- **The candidates**, ranked, each with a one-line *what it would bring*.
- **Why the top pick leads** — and, critically, **why each runner-up was
  ranked below it**. A silently-excluded skill is the failure mode this step
  exists to prevent; the user must be able to overrule the ranking.

Then ask via AskUserQuestion — **one question per task, the candidates as the
options** (max 4 questions per call; batch across calls if there are more
tasks). Mark the top pick "(Recommended)". Include a "none needed" option
when direct implementation genuinely beats forcing a skill.

Sourcing the shortlist: prefer specific installed Skill → specialized
subagent → MCP tool. Verification/QA-shaped sub-steps ("check this," "review
this," "confirm it works") should shortlist **subagents**, not generic
skills. Search the listing broadly before ranking — near-miss skills that got
considered and rejected still belong in the shortlist with the reason, since
that reasoning is exactly what the user wants to see.

**Sessions can carry hundreds of skills** (up to 500), with plugin packs
installing dozens of near-duplicates. Narrow the field **by stack/platform
first**, then by task shape, and only then rank — a Python reviewer is not a
candidate for a TypeScript project. Apply the namespace tie-break for
overlapping scoped/generic skills, and **always report the funnel** ("14
matched; these 3 ranked highest") so the shortlist reads as a filter, not as
the whole field. Full mechanics in `reference/routing-guide.md`.

**This is the one step that gates delivery.** Scope and requirement
ambiguity still gets defaulted-and-flagged inline (never a question round) —
but *which capability runs each task* is the user's call, because that
decision is the whole point of this skill.

Two standing rules apply automatically here, every run (not conditional on a
question). Both name specific skills — apply each **only if that skill is in
the current session's listing**; otherwise use the stated fallback and note
it as a flag.
- **Any task that writes/modifies code** gets a trailing code-review +
  verification pair appended as sub-steps — a standing quality gate.
  Preferred: `/code-review` then `/verify`. Fallback if absent: dispatch a
  code-reviewing subagent, and state the verification expectation in prose
  ("drive the change end-to-end and observe real behaviour, not just tests").
- **Any task that produces a plan/spec** (Plan Mode, a plan-writing skill, or
  any "make a plan for X" ask) gets instructed to render the finished plan as
  an interactive HTML artifact with click-to-comment sections, instead of a
  bare `.md` file — submitted comments are treated as revisions to the plan.
  Preferred: reuse an existing commentable-preview mechanism if one is
  installed (e.g. `/interview-me`'s). Fallback if absent: publish via the
  Artifact tool with `class="commentable"` + `data-id` on each block-level
  section.

Full mechanics for both in `reference/routing-guide.md`.

### 3. Deliver the final prompt — using the user's chosen capabilities
Write the rebuilt prompt in the **exact fenced-code template** from
`reference/routing-guide.md` — never a prose sketch or a looser approximation.
This is mandatory on every run, no exceptions. **The prompt must keep the
per-task structure from step 2**: shared context first, then one block per
task, each headed by its own `/skill` invocation (or named agent/tool). Never
collapse a multi-task prompt under one skill list — the task→skill mapping IS
the routing value.

For anything genuinely ambiguous, default sensibly and mark it inline as
`[?]` with a one-line note on what was assumed and why — do not leave a gap
unfilled or block delivery on it. Follow the code block with a short "why
these skills" table and any availability flags, then stop.

**Requirements interviewing stays off the default path.** The capability
shortlist (step 2) is the only pre-delivery gate. Do NOT additionally hold
the prompt back for a round of scope/requirement questions — that pattern
has repeatedly produced unanswered or low-value question rounds that only
delayed the one thing the user asked for. Scope details, content
preferences, and minor ambiguity get a sensible default plus an inline
`[?]`, resolved in the delivered prompt.

If the user wants deeper refinement after seeing the delivered prompt, they
can ask for it, or opt into the full `/interview-me` treatment — offer that
only as a follow-up, never as part of the default path.

## Guardrails

- The output is a prompt, not an executed plan. Never begin executing it.
- Every prompt opens with the self-invocation line so pasted `/skill` names
  actually load. Never instruct the user to tag skills manually — pasting
  can't trigger autocomplete, and multi-task prompts can't be UI-tagged.
- Every task carries an `[effort: low|medium|high]` hint.
- Narrow candidates by stack before ranking, and report the funnel — a
  session may hold up to 500 skills, most of them irrelevant.
- No context preamble by default — go straight into the tasks. Add one only
  for a fresh-session paste, or a costly-to-get-wrong constraint. Never
  restate project history.
- Context taken from memory or compacted turns is a snapshot: mark it
  "as of <date>, verify", never state it as current fact.
- Always shortlist 2–3 candidates per task and let the user pick. Never
  silently choose one — and always state why each runner-up ranked lower.
- The capability choice is the ONLY pre-delivery gate. No requirements
  interview on top of it.
- Never construct a single-option AskUserQuestion — plain text or a
  multiple-choice with real context-derived options instead.
- Unresolved scope ambiguity gets a sensible default + inline `[?]` note, not
  a blocked delivery. `/interview-me` only on explicit user opt-in, after
  delivery.
- Never name a capability absent from the current session listing.
- Embedded `/skill` names must be exactly as listed (slash + registered name).
- Preserve the user's intent and voice — polish and structure it, don't inflate
  it with requirements they never implied.
- Code-writing tasks always get a trailing code-review + verify pair —
  automatic, not conditional on being asked. Use `/code-review` + `/verify`
  when installed; otherwise the subagent/prose fallback.
- Plan/spec-producing tasks always get routed to render as a commentable HTML
  artifact, never a bare `.md`.
- These two rules name specific skills. Apply the named skill only when it is
  in the current session's listing — never emit a `/skill` the user doesn't
  have. This skill must degrade gracefully in any environment.
