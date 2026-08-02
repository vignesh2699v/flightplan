---
name: rebuild-prompt
description: Rebuild a rough prompt into a polished, ready-to-paste one, with the best-fit installed skills, subagents and MCP tools routed to each task, plus a model and effort level per task. Use when the user runs /rebuild-prompt, or asks to rebuild, polish, or add the right skills or agents to a prompt they have written. Returns the prompt for the user to run themselves; never executes it.
---

# Rebuild Prompt

Turn a rough prompt into a polished one with the right `/skill` invocations
embedded per task. The user copies the result and runs it themselves — the
output is a prompt, never an executed task. Deliver it, then stop.

## The pipeline

### 1. Decompose, then size

Read the raw prompt and find the real intent. Split multiple tasks and order
them by dependency. Look up what you can — memory, project files — rather
than asking about it.

Then **size** the job, because size picks the route:

| Shape | Route |
|---|---|
| One task, one candidate no runner-up seriously threatens | Skip the ballot. Name the pick and the nearest runner-up in a line each, deliver. |
| One task, contested | One ballot question, deliver. |
| Two to four tasks | Full ballot, one prompt, every task. |
| Five or more tasks | Full ballot, deliver round one only (step 3). |

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

Done when every task has a capability, chosen or waived by the size gate.

### 3. Deliver

Write the prompt in the fenced-code template from
`reference/routing-guide.md`, keeping one block per task, each headed by its
own invocation. The task→skill mapping is the routing value — a multi-task
prompt collapsed under a single skill list has thrown it away.

**At five tasks or more, deliver one round.** Round one runs up to the first
point where a finding would change what comes after it. Write those tasks in
full, outline the remainder in a line each, and close the round by telling the
session to report its results and telling the user to re-run `/rebuild-prompt`
with them to get round two. A task written before the work that informs it has
run is a guess; re-planning it against what actually happened is the whole
reason to cut the prompt there. A round is also where a model can change — one
message runs on one session model, so the round boundary is the only place
routing to a different one takes effect.

Default anything ambiguous and mark it `[?]` inline with what you assumed and
why. Follow the block with a short "why these skills" table and any
availability flags, then stop.

The capability ballot is the only gate. Scope questions get a default and a
`[?]` — a held-back prompt has repeatedly produced unanswered question rounds
that only delayed the one thing the user asked for. Afterwards, offer
`grilling` when the premise deserves stress-testing, or `/interview-me` when
the gap is missing requirements rather than a questionable premise.

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

**Say why, once.** One sentence on what the work is for and what the output
enables. This is the single line exempt from the pruning test: a model given
the reason behind a request connects it to the right context instead of
inferring intent, and that lift is worth more than the sentence costs. Intent
is not the same as background — the exemption covers why the task matters, not
a history of the project.

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

**Tag each task `[model: <id> | effort: <level>]`.** Effort runs
`low | medium | high | xhigh | max`, with `xhigh` the right default for coding
and agentic work and `low`/`medium` the primary lever on cost and latency.
Model defaults to `claude-opus-5`; drop to `claude-sonnet-5` for
cost-sensitive or high-volume work, `claude-haiku-4-5` for mechanical work,
and reach for `claude-fable-5` only on the hardest, longest, most ambiguous
jobs. The tag **binds** on a task dispatched to a subagent, which takes its
own model and effort. On a task the session runs directly it is advisory — it
tells the user which session to paste the round into, which is why a model
change and a round boundary are the same event.

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

## Standing rules

Applied every run, never asked about. Both name specific skills: use each one
only when it is in the session listing, otherwise the documented fallback,
noted as a flag. This skill has to degrade gracefully in any environment.

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
