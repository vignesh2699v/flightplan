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

When grilling turns up zero real signal — no target, symptom, or file named
at all, not even a hint — do not default to a broad speculative search
across the whole scope as if a real target were known. Narrow the first task
to diagnosis only, and mark the missing target as the `[?]` gap itself
rather than picking a plausible-looking one and committing full effort to
chasing it.

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

Before ranking, read `~/.claude/rebuild-prompt/history.md` once — covering
every contested task this run, not a separate read per task. See
`routing-guide.md` for the read/write mechanics and schema.

Classification and the ballot's candidate list come from the same ranking
pass — narrow, then rank, once per task (see `routing-guide.md` § Building
the shortlist). Don't run a shallow pass to classify, then redo the full pass
to populate the ballot.

Done when every task has a capability, chosen, waived, or absent.

### 3. Deliver

Write the prompt using the template in `routing-guide.md`. One fenced block
per segment — cut at every boundary. See `routing-guide.md` § Segments for
the three boundary types, their exact closing lines, and the two exemptions;
don't re-derive it here.

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
- Every agent-dispatched task carries the reporting contract from
  `routing-guide.md` § Standing rule: agent tasks report as they go — don't
  restate it here, apply it.
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

- Code-writing tasks get one fresh-context review appended — fallback chain
  in `routing-guide.md` § Standing rule: implementation tasks get one
  fresh-context review. No self-checking language ("double-check",
  "re-verify", "include a verification step") in the task body itself.
- Plan/spec tasks render as a commentable HTML artifact, not a bare `.md`.
