---
name: rebuild-prompt
description: Rebuild a rough prompt into a polished, ready-to-paste one, with the best-fit installed skills, subagents and MCP tools routed to each task, plus a model and effort level per task. Use when the user runs /rebuild-prompt, or asks to rebuild, polish, or add the right skills or agents to a prompt they have written. Returns the prompt for the user to run themselves; never executes it.
---

# Rebuild Prompt

Turn a rough prompt into a polished one with the right `/skill` invocations
embedded per task. The user copies the result and runs it themselves — the
output is a prompt, never an executed task. Deliver it, then stop.

## The pipeline

### 0. Grill the premise

Run `grilling` on the raw prompt before decomposing anything. What it is for:
the goal behind the request, the context the user did not think to state, and
the assumption that would make the whole prompt point at the wrong thing. It
is not a requirements checklist — a prompt built from a stated request routes
the request, and a prompt built from the goal behind it routes the goal.

Grilling runs before the ballot, never between ballot and delivery. What it
surfaces changes how the work decomposes, and decomposition is what routing
keys off; findings that arrive after the ballot arrive too late to move
anything.

**Skip it only when the job is trivial** — one mechanical task with an obvious
capability, where the request and the goal are plainly the same thing. Say in
one line that it was skipped and why, so the user can ask for it anyway.

**When `grilling` is absent from the session listing, grill inline instead of
skipping.** This step is a behaviour, not a dependency. Ask what the user is
actually trying to achieve, what changes for them if it works, what they have
already ruled out and why, and which assumption would be most expensive to
have wrong. A handful of questions, driven by their answers rather than a
fixed list. Say that the skill was unavailable so they know what they are
getting. Naming an adjacent installed skill as an alternative is fine;
switching to one silently is not — that is the invisible routing this skill
exists to prevent, committed by the skill itself.

Done when the goal behind the request is stated, along with whatever
constraint or context the raw prompt left implicit.

### 1. Decompose, then size

Read the raw prompt, plus whatever grilling surfaced, and find the real
intent. Split multiple tasks and order them by dependency. Look up what you
can — memory, project files — rather than asking about it.

Then **size** the job, because size picks the route:

| Shape | Route |
|---|---|
| One task, one candidate no runner-up seriously threatens | Skip the ballot. Name the pick and the nearest runner-up in a line each, deliver. |
| One task, contested | One ballot question, deliver. |
| Two to four tasks | Full ballot, one prompt, every task. |
| Five or more tasks | Full ballot, deliver segment one only (step 3). |

The ballot exists to surface a real choice. A single-task prompt with one
obvious capability has no choice in it, and asking anyway turns the skill's
safeguard into a toll booth.

Done when every task has a name, a place in the order, and a route.

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

**With nothing to route to, skip the ballot and say so.** Before concluding
the field is empty, check all three sources — a session with no installed
skills still has subagents and MCP tools, and those are candidates. If it
genuinely is empty, deliver with no capability line and note that nothing
matched. A ballot holding one option is not a choice, and asking anyway wastes
the user's turn on a decision that has already been made for them.

Done when every task has a capability, chosen, waived by the size gate, or
absent because nothing matched.

### 3. Deliver

Write the prompt in the fenced-code template from
`reference/routing-guide.md`, keeping one block per task, each headed by its
own invocation. The task→skill mapping is the routing value — a multi-task
prompt collapsed under a single skill list has thrown it away.

**Lead with the model plan.** Above the prompt, a two-column table of segment
→ model and effort, so the user sees before pasting anything whether this job
runs in one session or several. When every task shares one model and effort,
say so in a line instead of drawing a table.

**Cut at every boundary and deliver one fenced block per segment.** Three
things open one: a **model or effort change** on directly-run work, a
**finding** that would rewrite what comes next, or an **irreversible step**
needing the user's approval before it runs. Task count opens nothing by
itself.

The two common boundaries close differently, and confusing them is the failure
worth naming. A model boundary closes by stating the model and effort to switch
to, with the next block already written — a direct task inherits the session's
setting, so the tag means nothing unless the prompt stops there. A finding
boundary closes by asking for the results and sending the user back to
`/rebuild-prompt`, because the next segment should be planned against what
happened rather than guessed ahead of it; handing over a pre-written block
there defeats the whole reason for cutting. Past five tasks, assume at least
one finding boundary exists and go find it.

Separate blocks rather than markers inside one block: a marker in a block the
user pastes whole is a marker the session runs straight past.

`reference/routing-guide.md` carries the exemptions that stop blocks
fragmenting, and the exact closing line for each boundary type.

Default anything ambiguous and mark it `[?]` inline with what you assumed and
why. Follow the blocks with a short "why these skills" table and any
availability flags, then stop.

The capability ballot is the only gate left — the premise was already tested
at step 0. Scope questions get a default and a `[?]`; a held-back prompt has
repeatedly produced unanswered question rounds that only delayed the one thing
the user asked for. Afterwards, offer `/interview-me` when what remains is
missing requirements rather than a questionable premise.

Done when every line of the delivered prompt passes **"would the task go
wrong without this?"** Task bodies bloat as readily as context preambles do,
and this test governs both.

## Writing the prompt body

**Open with the self-invocation line.** Pasting text does not fire the
editor's slash-command autocomplete, and only one slash command can lead a
message, so a multi-task prompt is impossible to UI-tag by design. Every
prompt therefore opens by telling the receiving session to invoke each named
skill itself via the Skill tool — that line is what turns `/names` from inert
text into real invocations. Use exactly the registered names. Every segment
carries its own copy: each one is pasted into a fresh turn. Omit the line
entirely when no task names a skill — an instruction to load skills that were
never named is noise the reader has to discard.

**Say why, once.** One sentence on what the work is for and what the output
enables. This is the single line exempt from the pruning test: a model given
the reason behind a request connects it to the right context instead of
inferring intent, and that lift is worth more than the sentence costs. Intent
is not the same as background — the exemption covers why the task matters, not
a history of the project. Grilling at step 0 is where this sentence comes from.

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
guard, a credential boundary. Two or three lines is a normal block. A segment
that follows a model switch is a fresh paste by definition — carry forward the
one or two facts it cannot infer from the segment before it.

**One paragraph, one line.** Write each paragraph unbroken, however long,
breaking only between paragraphs and between tasks. A paste box reflows text
that holds no newlines; hard-wrapped text keeps its breaks and visibly wastes
half the box. (This file wraps because it is read, never pasted.)

**Tag each task `[model: <id> | effort: <level>]`.** Effort runs
`low | medium | high | xhigh | max`, with `xhigh` the right default for coding
and agentic work and `low`/`medium` the primary lever on cost and latency.
Model defaults to `claude-opus-5`; drop to `claude-sonnet-5` for
cost-sensitive or high-volume work, `claude-haiku-4-5` for mechanical work,
and reach for `claude-fable-5` only on the hardest, longest, most ambiguous
jobs. The tag **binds** on a task dispatched to a subagent, which takes its
own model and effort. On directly-run work it is advisory — a direct task
inherits the session's setting — so a tag that differs from the one before it
is only real if the prompt stops there and asks the user to switch. Tag and
boundary are the same decision.

**Structure beats emphasis.** Fence hard constraints in their own XML tag
(`<constraints>`) rather than shouting them in prose — a tagged block parses
unambiguously where bold text and capitals compete with everything else. For
any task where format, tone, or structure is the deliverable, one `<example>`
of the wanted output steers harder than a paragraph describing it. Write each
instruction as the behaviour wanted rather than the behaviour forbidden.

**Every agent task names its artifact.** A dispatched agent runs out of sight,
and a summary is where a check that never happened becomes "verified". Write
into the task: report at checkpoints, return the specific artifact for that
check shape, and surface findings verbatim, failures included. State that
"verified" with nothing attached is a failed task. Mark independent tasks
parallelizable, except where they touch the same files or canvas.

**Bound the work.** Three sentences that cost almost nothing and prevent the
three ways a good prompt goes wide. Scope: deliver what was asked at the scope
intended, say so in a sentence if a better approach exists, and continue with
the task as asked rather than quietly widening it. Delegation: delegate only
for genuinely independent, sizeable tracks, never to double-check the
session's own work, and keep spawn counts low. Reversibility: local reversible
edits proceed, and anything destructive, outward-facing, or hard to undo asks
first.

**Route against the live listing** of Skills, subagents and MCP tools in the
current session, using exact registered names. Flag whatever needs auth, sits
disconnected, or carries a setup precondition.

**Keep the user's voice.** Polish and structure what they wrote; resist
adding requirements they never implied.

Success criteria are mandatory — a prompt with no definition of done is not
yet polished.

## When capabilities are missing

Two different things degrade, and only one of them is allowed to.

**What the prompt routes to** narrows. Fewer installed capabilities means
shorter shortlists and eventually none, and the delivered prompt then carries
structure, model and effort tags, constraints and success criteria with no
`/skill` lines in it. That is a thinner output, not a failure.

**What the pipeline does** never stops. Every step has to run on a bare
install: grilling falls back to grilling inline, the ballot falls back to
skipping itself, the review rule falls back to a subagent and then to prose. A
step that quietly disappears because a skill is absent is a bug — the user
cannot ask for something back when nothing told them it was gone.

Name every substitution and every skipped step in the Flags section. An
unflagged fallback is indistinguishable from the feature working.

## Standing rules

Applied every run, never asked about. Both name specific skills: use each one
only when it is in the session listing, otherwise the fallback above, noted as
a flag.

- Tasks that write or modify code get one **fresh-context review** appended —
  `/code-review`, or a Code Reviewer subagent — whose mandate covers driving
  the change end-to-end, not only reading the diff. A separate context catches
  what self-critique misses. Write no self-checking language into the task
  itself: "double-check your answer", "re-verify before responding", and
  "include a verification step" trigger redundant verification on current
  models and buy nothing the fresh reviewer does not already cover.
- Tasks that produce a plan or spec render it as a commentable HTML artifact
  rather than a bare `.md`, where submitted comments become revisions to it.

Mechanics, fallbacks, the output template and the evidence table all live in
`reference/routing-guide.md`.
