---
name: rebuild-prompt
description: Rebuild a rough prompt into a polished, ready-to-paste one, with the best-fit installed skills, subagents and MCP tools routed to each task it contains. Use when the user runs /rebuild-prompt, or asks to rebuild, polish, or add the right skills or agents to a prompt they have written. Returns the prompt for the user to run themselves; never executes it.
---

# Rebuild Prompt

Turn a rough prompt into a polished one with the right `/skill` invocations
embedded per task. The user copies the result and runs it themselves — the
output is a prompt, never an executed task. Deliver it, then stop.

## The pipeline

### 1. Decompose

Read the raw prompt and find the real intent. Split multiple tasks and order
them by dependency. Look up what you can — memory, project files — rather
than asking about it.

Done when every task the user implied has a name and a place in the order.

### 2. Put the candidates on a ballot

For each task, offer 2–3 real candidates from the live session listing and
let the user choose. The shortlist is a **ballot**, not a recommendation:
every plausible candidate appears on it, each runner-up carries the reason it
ranked lower, and the user's pick decides. Routing the user cannot see is
routing the user cannot overrule — the failure this skill exists to prevent.

Sessions carry up to 500 skills, most of them irrelevant here. Narrow by
stack and platform, then by task shape, then rank — and report the funnel
("14 matched; these 3 ranked highest") so the ballot reads as a filter rather
than as the whole field.

Source candidates in this order: installed Skill → specialized subagent →
MCP tool. Verification-shaped work ("check this", "confirm it works") belongs
to subagents.

Ask via AskUserQuestion — one question per task, candidates as options, top
pick marked "(Recommended)", four questions per call at most. Offer "none
needed" wherever direct implementation beats forcing a skill. Every question
carries at least two real options; where the session affords no discrete
choice set, ask in plain text instead.

Read `routing-history.md` beside this skill before ranking. A past pick for a
matching task shape gets surfaced ("you chose this on `<date>`") and ranked up
one place. It stays a signal: the ballot still shows every candidate, still
asks, and the stack filter still overrides it. Append one row per task once
the user picks, recording task *shape* and capability names only — prompts
carry client names and internal URLs, and this file holds neither. Create it
if it is absent.

Done when the user has picked a capability for every task.

### 3. Deliver

Write the prompt in the fenced-code template from
`reference/routing-guide.md`, keeping one block per task, each headed by its
own invocation. The task→skill mapping is the routing value — a multi-task
prompt collapsed under a single skill list has thrown it away.

Default anything ambiguous and mark it `[?]` inline with what you assumed and
why. Follow the block with a short "why these skills" table and any
availability flags, then stop.

The capability ballot is the only gate. Scope questions get a default and a
`[?]` — a held-back prompt has repeatedly produced unanswered question rounds
that only delayed the one thing the user asked for. Offer `/interview-me`
afterwards if they want more depth.

Done when every line of the delivered prompt passes **"would the task go
wrong without this?"** Task bodies bloat as readily as context preambles do,
and this test governs both.

## Writing the prompt body

**Open with the self-invocation line.** Pasting text does not fire the
editor's slash-command autocomplete, and only one slash command can lead a
message, so a multi-task prompt is impossible to UI-tag by design. Every
prompt therefore opens by telling the receiving session to invoke each named
skill itself via the Skill tool — that line is what turns `/names` from inert
text into real invocations. Use exactly the registered names.

**The prompt is never a second source of truth.** Every fact already has a
home: the conversation window, a playbook, a README, the code itself. Point
at the home and let the session read it. A fact copied into the prompt forks
from its original and ages independently, and a stale copy asserted as
current is worse than a pointer. One rule, governing three habits — skip the
context preamble when the prompt is pasted back into the same conversation,
reference files by path instead of reproducing them, and date-stamp anything
drawn from memory or a compacted turn ("as of `<date>`, verify").

Carry a context block only for a fresh-session paste, or for a fact that is
costly to get wrong and not inferable: a hard constraint, a destructive-action
guard, a credential boundary. Two or three lines is a normal block.

**One paragraph, one line.** Write each paragraph unbroken, however long,
breaking only between paragraphs and between tasks. A paste box reflows text
that holds no newlines; hard-wrapped text keeps its breaks and visibly wastes
half the box. (This file wraps because it is read, never pasted.)

**Tag each task `[effort: low|medium|high]`.** Mechanical work is low;
judgment-heavy design and adversarial verification are high. A second routing
axis alongside which capability runs it.

**Every agent task names its artifact.** A dispatched agent runs out of sight,
and a summary is where a check that never happened becomes "verified". Write
into the task: report at checkpoints, return the specific artifact for that
check shape, and surface findings verbatim, failures included. State that
"verified" with nothing attached is a failed task. Mark independent tasks
parallelizable, except where they touch the same files or canvas.

**Route against the live listing** of Skills, subagents and MCP tools in the
current session, using exact registered names. Flag whatever needs auth, sits
disconnected, or carries a setup precondition.

**Keep the user's voice.** Polish and structure what they wrote; resist
adding requirements they never implied.

Success criteria are mandatory — a prompt with no definition of done is not
yet polished.

## Standing rules

Applied every run, never asked about. Both name specific skills: use each one
only when it is in the session listing, otherwise the documented fallback,
noted as a flag. This skill has to degrade gracefully in any environment.

- Tasks that write or modify code get a trailing code-review and verification
  pair (`/code-review`, then `/verify`).
- Tasks that produce a plan or spec render it as a commentable HTML artifact
  rather than a bare `.md`, where submitted comments become revisions to it.

Mechanics, fallbacks, the output template and the evidence table all live in
`reference/routing-guide.md`.
