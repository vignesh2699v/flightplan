---
name: rebuild-prompt
description: Rebuild a rough prompt into a polished, ready-to-paste one, with the best-fit installed skills, subagents and MCP tools routed to each task, plus a model and effort level per task. Use when the user runs /rebuild-prompt, or asks to rebuild, polish, or add the right skills or agents to a prompt they have written. Returns the prompt for the user to paste back into this same conversation and run themselves; never executes it.
---

# Rebuild Prompt

Turn a rough prompt into a polished one with the right `/skill` invocations
embedded per task. Deliver the finished prompt, then stop — the user pastes
it back into this same conversation and runs it.

Rationale for every rule below lives in README.md § Design notes. Mechanics,
exact strings, and templates live in `reference/routing-guide.md`. Do not
restate either here — if you're about to explain *why*, it belongs in one of
those two files, not a third copy in this one.

## Pipeline

### 0. Grill the premise

Run `grilling` on the raw prompt before decomposing anything. If `grilling`
is not installed, grill inline instead: ask what the user is actually trying
to achieve, what changes if it works, what they've already ruled out, and
which assumption would be most expensive to have wrong. Skip only for one
mechanical task with an obvious capability, and say in one line that it was
skipped and why.

When grilling turns up zero real signal — no target, symptom, or file named
at all, not even a hint — do not default to a broad speculative search
across the whole scope as if a real target were known. Narrow the first task
to diagnosis only, and mark the missing target as the `[?]` gap itself
rather than picking a plausible-looking one and committing full effort to
chasing it.

Carry the answer to the last question forward to step 3 — it's what decides
which task, if any, escalates past the default effort level.

### 1. Decompose, then classify

If the raw prompt continues a job this pipeline already ran earlier in the
same session — same topic, or explicitly the results of a prior segment —
carry forward every ballot pick, the model plan, and any settled constraints,
and print one line naming what carried. Decompose only the tasks that are
new or still open. A genuinely new topic carries nothing; say so and
classify fresh. Don't reset a running job on every turn, and don't reuse a
stale pick without naming it either.

Split the raw prompt (plus whatever grilling surfaced) into tasks, ordered by
dependency. Look up context from memory and project files rather than
asking.

For every task, classify it:

| Class | Meaning |
|---|---|
| Uncontested | One candidate; no runner-up seriously threatens it |
| Contested | 2+ real candidates in genuine competition |
| No candidate | Nothing in skills, subagents, or MCP tools fits |

This per-task classification drives step 2 — task *count* does not.

Then classify the **job** itself, once, from the resulting task list:

| Job size | Signal | Output tier |
|---|---|---|
| Single-shot | 1 task | One-line |
| Compact | 2–3 tasks, one segment | Short |
| Full | Any segment boundary, or 4+ tasks | Full |

Job size is independent of the per-task table above — a single-shot job can
still be contested; it only controls how much gets written around the
answer, not whether step 2 asks about it. Tier templates: `routing-guide.md`
§ Output tiers.

### 2. Ballot

For every **contested** task: offer 2–3 real candidates via AskUserQuestion,
top pick marked "(Recommended)", "none needed" where direct implementation
wins, max 4 questions per call. Source order: installed Skill → subagent →
MCP tool. Verification-shaped work ("check this", "confirm it works")
defaults to a subagent.

For every **uncontested** task: skip the question. State the pick and its
nearest runner-up in a line each in the delivered output — visible, not
asked.

For every **no-candidate** task: skip the capability line entirely and say
nothing matched.

Before ranking, read `~/.claude/rebuild-prompt/history.md` once — covering
every contested task this run, not a separate read per task. See
`routing-guide.md` for the read/write mechanics and schema.

Classification and the ballot's candidate list come from the same ranking
pass — narrow, then rank, once per task (see `routing-guide.md` § Building
the shortlist). Don't run a shallow pass to classify, then redo the full pass
to populate the ballot.

Done when every task has a capability, chosen, waived, or absent.

### 3. Deliver

Write at the tier step 1 selected — Single-shot, Compact, or Full, exact
templates in `routing-guide.md` § Output tiers. Full tier cuts one fenced
block per segment at every boundary; see `routing-guide.md` § Segments for
the three boundary types, their exact closing lines, and the two exemptions.

Compact and Full lead with the review header (`routing-guide.md` § Review
header) — five lines, scannable before the fenced block, never inside it.
Single-shot skips it — see `routing-guide.md` § Review header for why.

Mark ambiguity `[?]` inline rather than asking about it. Offer
`/interview-me` afterward, only when it's in the session listing and what
remains is missing requirements rather than a questionable premise.

Close every delivery, every tier, with the line from `routing-guide.md` §
Closing checklist — the user's next message becomes pass/fail per criterion,
not a fresh paragraph to re-parse.

Done when every line passes: **would the task go wrong without this?**

## Writing the prompt body

- Open every segment with the self-invocation line, verbatim, from
  `routing-guide.md`. Omit it if no task in that segment names a skill.
- One sentence of intent, up front — exempt from the pruning test below.
- No context preamble by default. Include one only for a fresh-session
  paste, or a fact that would break the task if wrong and isn't inferable
  (hard constraint, destructive-action guard, credential boundary). 2–3
  lines max; date-stamp anything sourced from memory.
- One paragraph, one unbroken line. Never hard-wrap the prompt body.
- Tag every task `[model: <id> | effort: <level>]` — current guidance and
  its verify-before-use note are in `routing-guide.md`.
- A hard constraint, destructive-action guard, or credential boundary is
  never dropped for tier — only its ceremony is. Full tier: a `<constraints>`
  tag. Compact and Single-shot: one line, folded into the body — exact slot
  in `routing-guide.md` § Output tiers. Add one `<example>` where format or
  tone is the deliverable. State the behaviour wanted, not the behaviour
  forbidden.
- Every agent-dispatched task carries the reporting contract from
  `routing-guide.md` § Standing rule: agent tasks report as they go — don't
  restate it here, apply it.
- Include the scope/delegation/reversibility guard in every prompt (exact
  wording in `routing-guide.md`).
- Route against the live session listing, exact registered names. Flag
  auth, disconnection, or setup preconditions.
- Keep the user's voice — polish structure, don't add requirements they
  never implied.
- Success criteria are mandatory, phrased so the closing checklist
  (`routing-guide.md`) can be reported against pass/fail — not prose.

## Standing rules

Applied every run, never asked about. Use the fallback for any missing
capability — skill, subagent or MCP tool — and flag the substitution in the
output. Never silently drop a pipeline step. (Rationale: README.md § Design
notes.)

- Code-writing tasks get one fresh-context review appended — fallback chain
  in `routing-guide.md` § Standing rule: implementation tasks get one
  fresh-context review. No self-checking language ("double-check",
  "re-verify", "include a verification step") in the task body itself.
- Plan/spec tasks render as a commentable HTML artifact, not a bare `.md`.
- A segment that isn't a job's last one closes with a compaction-checkpoint
  line — fallback chain in `routing-guide.md` § Standing rule: a non-final
  segment closes with a compaction checkpoint.
