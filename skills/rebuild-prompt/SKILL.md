---
name: rebuild-prompt
description: Rebuild a rough prompt into a polished, ready-to-paste one, with the best-fit installed skills, subagents and MCP tools routed to each task, plus a model and effort level per task. Use when the user runs /rebuild-prompt, or asks to rebuild, polish, or add the right skills or agents to a prompt they have written. Returns the prompt for the user to run themselves; never executes it.
---

# Rebuild Prompt

Turn a rough prompt into a polished one with the right `/skill` invocations
embedded per task. Deliver the finished prompt, then stop — the user runs it.

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

### 1. Decompose, then classify

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

Read `~/.claude/rebuild-prompt/history.md` before ranking a contested task —
see `routing-guide.md` for the read/write mechanics and schema.

Done when every task has a capability, chosen, waived, or absent.

### 3. Deliver

Write the prompt using the template in `routing-guide.md`. One fenced block
per segment. A boundary opens at any of: a model or effort change on
directly-run work, a finding that would change what follows, or an
irreversible step needing approval.

- **Model/effort boundary** closes by naming the exact model and effort to
  switch to; the next block is already written.
- **Finding boundary** closes by asking for results and telling the user to
  re-run `/rebuild-prompt`; the next block is deliberately not pre-written.
- Subagent tasks never force a boundary. A one-rung effort change inside the
  same model stays in the current block.

Lead every delivery with a model plan (format in `routing-guide.md`).

Mark ambiguity `[?]` inline rather than asking about it. Offer
`/interview-me` afterward, only when it's in the session listing and what
remains is missing requirements rather than a questionable premise.

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
- Hard constraints go in a `<constraints>` tag. Add one `<example>` where
  format or tone is the deliverable. State the behaviour wanted, not the
  behaviour forbidden.
- Every agent-dispatched task: report at checkpoints, name the artifact,
  state "verified" with nothing attached is a failed task, surface findings
  verbatim. Mark independent tasks parallelizable, except where they share
  files or a canvas.
- Include the scope/delegation/reversibility guard in every prompt (exact
  wording in `routing-guide.md`).
- Route against the live session listing, exact registered names. Flag
  auth, disconnection, or setup preconditions.
- Keep the user's voice — polish structure, don't add requirements they
  never implied.
- Success criteria are mandatory.

## Standing rules

Applied every run, never asked about. Use the fallback for any missing
skill and flag the substitution in the output — never silently drop a step.
What the prompt *routes to* thins out as capabilities are missing; what the
*pipeline does* never stops.

- Code-writing tasks get one fresh-context review appended — `/code-review`,
  a Code Reviewer subagent, or a prose fallback. No self-checking language
  ("double-check", "re-verify", "include a verification step") in the task
  body itself.
- Plan/spec tasks render as a commentable HTML artifact, not a bare `.md`.
