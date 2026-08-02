# Routing guide

How to match tasks to capabilities, and the output template for the final
rebuilt prompt.

## Where the capability list comes from

Do **not** guess names or rely on memory. Every run, read what is live in the
current session:

- **Skills** — the "following skills are available for use with the Skill tool"
  listing.
- **Subagents** — the "available agent types for the Agent tool" listing.
- **MCP tools** — loaded `mcp__*` tools, plus deferred ones via `ToolSearch`.

Flag rather than assume:

| State | What to do in the output |
|---|---|
| Needs auth | Note it under Flags — the user must authorize before running the prompt |
| Disconnected | Pick a fallback or note the gap |
| Setup precondition | State the exact command to run first (e.g. a CLI setup step) |

## Building the shortlist (2–3 candidates per task)

A session can carry **hundreds of skills** (up to 500), and large plugin
packs install dozens of near-identical ones — a dozen language-specific code
reviewers, several overlapping design skills, multiple review agents. Assume
the candidate field is large and messy, and narrow it deliberately.

**Narrow before you rank — in this order:**

1. **By stack/platform first.** Detect what the project actually is, then
   drop every candidate that can't apply. Never shortlist a Python reviewer
   for a TypeScript project, or a CSS-transitions skill for canvas-based
   design work. This single filter routinely cuts a 20-candidate field to
   3–4, and is the highest-leverage step.
2. **By task shape.** Build vs. review vs. plan vs. verify.
3. **Then rank** whatever survives.

**Namespace tie-break.** When a plugin-scoped skill and a generic one both
match (e.g. `/some-plugin:code-review` vs `/code-review`), prefer:
   1. A **project-scoped** skill from the repo being worked in — it encodes
      that project's own conventions.
   2. The **more specific** skill (language/framework-specific beats
      generic) *when* the detected stack matches it exactly.
   3. The **generic/built-in** skill otherwise — fewer assumptions, and the
      user more likely knows its behaviour already.
State which rule decided it. Two skills with near-identical descriptions is
a genuine ambiguity — surface it rather than picking silently.

**Always report the funnel.** State how many plausible candidates existed
before narrowing: *"14 review skills matched; these 3 ranked highest."* A
shortlist without a denominator implies the field was only three wide.
Invisible filtering is precisely the failure this step exists to prevent —
presenting 3-of-20 as though it were 3-of-3 recreates it.

Search the listing **broadly** before ranking. The listing is long and full
of overlapping design/motion/review skills — a shortlist that only contains
the obvious pick means the search was too shallow.

For a given task, sweep for candidates across these angles:
- The **domain-specific** skill (the platform/tool the work happens in).
- The **discipline** skill (design/audit/motion/review as a craft).
- The **taste/direction** skill (how it should feel).
- The **subagent** equivalent (for anything verification- or research-shaped).

Then rank, and for each runner-up record **why it ranked below** — wrong
layer (CSS skill for canvas work), too general, overlapping with the top
pick, or unavailable. That reason is the deliverable, not a footnote: the
user is choosing between them and needs the trade-off stated.

Present as AskUserQuestion — one question per task, candidates as options,
top pick marked "(Recommended)", plus a "none needed" option where direct
implementation genuinely wins.

## Routing history — learn from what the user already chose

The shortlist step asks the user to make the same judgement call repeatedly.
Someone who picked `/impeccable` over `/high-end-visual-design` for a design
refinement three times running should not be asked a fourth time as though
the question were fresh. Past picks are a **ranking signal**.

**Where it lives.** A `routing-history.md` file alongside this skill's own
directory (`<skill-dir>/routing-history.md`). It is created on first write —
never assume it exists, and never fail if it doesn't. For a project-scoped
install, add it to `.gitignore`: it's local preference data, not shared
config.

**Format** — one row per task, appended:

```markdown
| date | task shape | chosen | passed over |
|---|---|---|---|
| 2026-07-23 | design refinement, canvas tool | /impeccable | /high-end-visual-design, /transitions-dev |
| 2026-07-23 | breakpoint QA, visual proof | Evidence Collector | /verify |
```

**Read it before shortlisting.** If a past row matches the current task
shape, mark that candidate in the shortlist — *"you chose this for a similar
task on `<date>`"* — and rank it up one position. That's all it does.

**It is a signal, never a lock-in:**
- Still present the full shortlist with runners-up and reasons. A past pick
  that stops the user from seeing alternatives recreates the silent-routing
  failure this skill exists to prevent.
- Still ask. Never auto-apply a past choice and skip the question.
- A past pick that's now **wrong for the stack** loses to the stack filter —
  narrowing by stack/platform happens first, and history cannot override it.
- Treat the row as a snapshot: the skill it names may no longer be installed.
  Check the live session listing before offering it, same as any candidate.

**Write only after the user picks.** Append one row per task: date, a short
task-shape phrase, the chosen capability, the ones passed over.

**Never record prompt content.** Task *shape* only — "design refinement,
canvas tool", not the user's brief. Prompts routinely contain client names,
unreleased work, credentials and internal URLs; a routing log is not the
place for any of it. Anyone who can read the skill directory can read this
file.

## Matching heuristics

- **Specific beats general.** A skill built for the exact job wins (charts →
  the dedicated dataviz skill, not a general UI skill).
- **Match on description, not name.** Names are opaque; descriptions say what
  a skill actually does.
- **Process before implementation.** If the work needs planning/debugging
  discipline, that skill is invoked first in the rebuilt prompt.
- **Verification/QA-shaped work defaults to a subagent.** When a sub-step is
  "check this," "review this," "profile this," or "confirm it actually
  works," prefer a dispatched subagent (Code Reviewer, Evidence Collector,
  Performance Benchmarker, UX Researcher, Accessibility Auditor, …) over a
  generic skill — the subagent pool exists precisely for independent-
  perspective, dispatched verification work. Don't default to "no capability
  fits" for this shape of task before checking the agent list.
- **One capability per task, usually.** Stack a second only when the task truly
  spans two domains (e.g. build *and* deploy).
- **Nothing fits → attach nothing** and say so. Don't force a bad match.
- Order multi-task prompts by dependency; communication/publishing steps last.

## Standing rule: agent tasks report as they go, and return artifacts

A dispatched subagent runs out of sight. What comes back is a summary the
user cannot audit — and a summary is exactly where a check that never
happened becomes "verified". Every task in the rebuilt prompt that dispatches
an agent must therefore carry a **reporting contract**, written into the task
body:

1. **Report at checkpoints, not just at the end.** State what's being checked
   before checking it, and what was found immediately after — so a run that
   stalls or goes wrong is visible while it's happening, not after.
2. **Return artifacts, not adjectives.** Name the specific evidence the task
   must produce. "Verified", "looks good", "all working" with nothing
   attached is a **failed task, not a passed one** — say so in the prompt.
3. **Surface findings verbatim.** The session that dispatched the agent
   reports what came back, including the parts that failed. Never compress an
   agent's failures into a clean summary line.

**What counts as evidence, by check shape:**

| Check shape | Required artifact |
|---|---|
| Visual / layout | Fresh-load screenshots at every breakpoint — not one viewport, not a cached load |
| Performance | Before/after numbers plus the measurement method |
| Correctness / build | The actual command output, not a claim that it passed |
| Accessibility | The assistive-technology result, not a checklist ticked from source |
| Security | `file:line` plus a concrete reproduction |
| Research / discovery | The sources read, cited — not just the conclusion |

**Mark independent tasks as parallelizable.** When two tasks have no
dependency, say so in the prompt (*"Tasks 2 and 3 are independent — dispatch
both"*), so the executing session runs them concurrently instead of serially.
Do **not** mark tasks parallel when they touch the same files or the same
canvas: concurrent edits to shared state conflict, and the time saved is not
worth the corruption. Dependency ordering always wins over parallelism.

## Standing rule: implementation tasks get one fresh-context review

Any task in the rebuilt prompt that **writes or modifies code** gets exactly
one step appended after it — no need to ask, this is a default, not a per-run
question:

**A fresh-context review** — `/code-review` if installed; otherwise dispatch a
code-reviewing subagent (e.g. a "Code Reviewer" agent type) if one exists;
otherwise state the expectation in prose. Its mandate is both halves of the
job: read the diff *and* drive the change end-to-end to observe real
behaviour, rather than accepting that tests and typecheck passed.

**One reviewer, not two, and never a self-check.** Anthropic's model guidance
is explicit that instructions telling a session to verify its own work —
"double-check your answer", "re-verify before responding", "include a final
verification step" — trigger redundant verification on current models and cost
tokens without improving the result. Fresh-context verification is the
exception that still pays: a separate context catches what self-critique
cannot see. So the appended review reads as a handoff to a different reader,
and the task body itself carries no re-checking language. This replaces the
older `/code-review` **plus** `/verify` pair, whose second step was a
same-session self-check.

Never emit a `/skill` name that isn't in the current session's listing — check
first, fall back second, and flag the substitution in the Flags section.

Write the review as its own numbered sub-step directly under the
implementation task it gates, not as a separate top-level task — it's part of
"done" for that task, not independent work. A task that's pure content,
design, research, or planning (nothing executable changes) does NOT get it —
only tasks that touch code.

## Standing rule: plan-shaped tasks render as a commentable HTML document

Whenever a task's shape matches **producing an implementation plan or spec**
(Plan Mode, `/superpowers:writing-plans`, `/interview-me`, or any "make a plan
for X" ask), the rebuilt prompt must instruct the executing session to render
the finished plan as an **interactive HTML artifact**, not a bare `.md` file:

- Publish via the Artifact tool.
- **Prefer reusing an installed commentable-preview mechanism** rather than
  inventing one. If `/interview-me` is in the session listing, reuse its
  Phase 3 Interactive Spec Preview (`STYLE_PRESETS.md`) verbatim.
- Fallback when no such skill is installed: build it directly — every
  block-level section gets `class="commentable"` + a unique `data-id`, plus a
  Revise action that collects the comments.
- Either way: a Revise action collects comments and feeds them back as edits
  to the same document (redeploy to the same URL) — comments are treated as
  **revision requests for the plan**, not a new task.

This is a default for any plan-shaped task, not conditional on a question —
state it in the task's instructions every time one of these tasks appears.

## Output template — the final prompt

The deliverable is ONE fenced code block the user can copy verbatim. It keeps
the task decomposition visible: shared context up top, then **one block per
task, each headed by its own skill invocation**:

Every rebuilt prompt **must open with the self-invocation line** below,
verbatim, before anything else. Without it a pasted prompt's `/skill`
mentions are inert text: pasting does not fire the editor's slash-command
autocomplete, and only one slash command can ever lead a message — so a
multi-task prompt is impossible to UI-tag by design. The line tells the
receiving session to invoke each named skill itself via the Skill tool,
which is the mechanism that actually works.

```markdown
## Your rebuilt prompt

​```
As you reach each task below, invoke the skill named in it via the Skill tool before doing that task's work. The /names are instructions to you, not decorative text — load each one yourself; I have not tagged them.

<Overall goal in the user's voice, one or two sentences — on ONE unbroken line — ending with why it matters and what the output enables. That reason is the one line exempt from the pruning test.>

<NO context block by default — the prompt is normally pasted back into the same conversation, which already holds these facts. Include one ONLY for a fresh-session paste, or for a fact that is costly to get wrong and not inferable. When included, keep it to a few lines that pass "would the task break without this?" — IDs, paths, non-obvious gotchas. Never project history. Mark anything from memory as "as of <date>, verify" rather than as fact.>

<constraints>
<hard constraints, destructive-action guards, credential boundaries — one per line, in the user's own words. Omit the whole block if there are none.>
</constraints>

<setup preconditions, e.g. CLI commands to run first — keep, these are actionable, not background>

Deliver what is asked at the scope intended; if a better approach exists, say so in a sentence and continue with the task as asked. Delegate to a subagent only for genuinely independent, sizeable tracks — never to double-check your own work — and keep spawn counts low. Local reversible edits proceed; anything destructive, outward-facing, or hard to undo asks first.

## Task 1 — <task name, involves writing/modifying code>   [model: claude-opus-5 | effort: xhigh]
Use /<skill-a> (and /<skill-b> if the task truly spans two domains).
<What to do, requirements — one unbroken line per paragraph. No "double-check" or "verify before responding" language: the review step below is the check.>
Then: hand the change to /code-review as a fresh reader — it reads the diff and drives the change end-to-end to see real behaviour, not just that tests and typecheck passed.

## Task 2 — <verification/QA-shaped task>  (after Task 1)   [model: claude-opus-5 | effort: xhigh]
Dispatch the <Agent Name> agent (e.g. Code Reviewer, Evidence Collector, Performance Benchmarker — whichever fits the check being asked for). ← agents/MCP tools are named as instructions, not slashes
<What to verify/do.>
Report each check before running it and its result immediately after, then return <the specific artifact: fresh-load screenshots at every breakpoint / before-after numbers with method / actual command output>. "Verified" with nothing attached is a failed task. Surface whatever comes back verbatim, failures included.

## Task 3 — <plan/spec-producing task>   [model: claude-sonnet-5 | effort: high]
Use /superpowers:writing-plans (or /interview-me, whichever fits).
<What the plan needs to cover.>
When the plan is ready, publish it as an interactive HTML artifact (Artifact tool) reusing /interview-me's commentable-preview mechanism — click-to-comment sections + a Revise action — instead of a bare .md file. Treat submitted comments as revision requests for the plan.

Done = <success criteria for the whole prompt — what the user reviews>.
​```

<A segment that ends at a model or effort switch closes with this line INSIDE the block, and the next segment is delivered as its own separate fenced block, repeating the self-invocation line:>
​```
Stop here. Switch this session to claude-opus-5 at xhigh before continuing, then paste the next block.
​```

<A segment that ends at a finding closes with these two lines instead — the next block is NOT pre-written:>
​```
Report back with: <the results that decide the next segment>.
Then re-run /rebuild-prompt with those results to get the next one.
​```
**Remaining segments (provisional):** <one line each — task name + expected capability + model>.

**Why these skills:**
| Task | Capability | Why |
|---|---|---|
| 1 | `/<skill-a>` | <one line> |
| 2 | <Agent Name> | <one line> |

**Flags:** <auth / setup preconditions / gaps — omit section if none>
```

**The skill names above are illustrative.** The example assumes `/code-review`,
`/interview-me` and a plan-writing skill are installed. Substitute whatever the
current session actually has, and use the documented fallbacks when they're
absent.

**Never collapse the mapping.** A multi-task prompt with a single skill list at
the top loses the routing — the per-task skill assignment is the core value of
this output. Single-task prompts may use a single header line instead.

**Single-task shortcut.** When the prompt holds one task and one capability no
runner-up seriously threatens, the ballot is skipped (see SKILL.md step 1).
The output shrinks to match: the fenced block with one header line, then two
lines instead of the "why these skills" table — the pick and its reason, and
the nearest runner-up and why it lost. The user can still overrule; they just
aren't stopped to confirm a choice that wasn't contested.

## Model and effort annotations

Tag each task `[model: <id> | effort: <level>]` after its heading — two more
routing axes alongside *which* capability runs it.

**Effort** runs the full ladder, not three levels:

| Level | Use for |
|---|---|
| `low` | Mechanical, well-specified work with a clear right answer — renames, formatter fixes, applying an approved plan step. Also the primary lever when latency matters. |
| `medium` | Normal implementation and design work; the cost-saving step down from the default. |
| `high` | The API default. Judgment-heavy work: architecture decisions, structural design refinement, checks that must actually catch problems. |
| `xhigh` | The recommended setting for the hardest coding and agentic work — not an exotic escalation. |
| `max` | Maximum capability, no token constraint. Can overthink simpler tasks; reserve it for correctness-over-cost cases. |

Lower effort is the main control on cost and latency, and current models hold
quality well at `low` and `medium` — sweep downward rather than defaulting
high out of caution. Effort steers thinking depth, **not** visible response
length; prompt for brevity separately if the output runs long.

**Model** defaults to `claude-opus-5`:

| Model | Route here when |
|---|---|
| `claude-opus-5` | The default. Complex agentic coding, multi-file features, refactors, review, long-horizon work. |
| `claude-sonnet-5` | Coding and agentic work where cost or volume matters more than the last increment of capability. |
| `claude-haiku-4-5` | Simple, mechanical, speed-critical steps. |
| `claude-fable-5` | The hardest, longest, most genuinely ambiguous jobs only — premium pricing, and its safety classifiers decline cybersecurity and life-sciences work. |

**Binding versus advisory.** A task dispatched to a subagent takes its own
model and effort, so the tag is executable there. A task the session runs
directly inherits the session's model — one message runs on one model — so the
tag is advisory and tells the user which session to paste this round into.
That asymmetry is why a model change and a round boundary are the same event:
splitting the prompt is the only way a per-task model choice takes effect for
direct work.

## Rules for the prompt body

These are mechanics. The rules themselves — point-don't-paste, never
hard-wrap, say-why-once, structure-beats-emphasis, bound-the-work — live in
SKILL.md under *Writing the prompt body*; don't restate them here.

- Put hard constraints in a `<constraints>` block near the top rather than
  bolding them inline. Where format or tone is the deliverable, add one
  `<example>` of the wanted output — it steers harder than describing it.
- Written to be pasted back into the **same conversation** by default, so it
  assumes the window already holds the project facts — no context preamble.
  Only for an explicit fresh-session paste does it carry the context a new
  session would lack, and even then only what passes the pruning test.
- If a subagent or MCP tool (not a slash skill) is part of the routing, name it
  as an instruction inside the body ("dispatch the Evidence Collector agent to
  verify…"), since only skills are slash-invokable.
- Success criteria are mandatory — a prompt without a definition of done is
  not polished.
- Keep it as short as completeness allows. Polish = density, not length.

## Segments — where a prompt gets cut

A rebuilt prompt is delivered as **one fenced block per segment**, not one
block for the whole job. Three things open a segment boundary. Any one of them
is enough; task count alone is not.

### Boundary 1 — a model or effort switch

A directly-run task inherits whatever model the session is set to. One message
runs on one model, so a task tagged for a different model than the task before
it **does not get that model** unless the prompt stops and the user changes the
setting. The tag is a promise the block boundary keeps.

Close the segment with the switch instruction, naming both values explicitly:

```
Stop here. Switch this session to <model> at <effort> before continuing, then paste the next block.
```

Name the model in full (`claude-sonnet-5`, not "Sonnet") — the user is about to
select it from a list, and the exact string is what they are matching against.

Two exemptions, so blocks do not fragment for no gain:

- **Subagent tasks never force a stop.** A dispatched agent carries its own
  model and effort, set at dispatch. A task routed to a subagent can name any
  model without the session needing to change.
- **A one-rung effort change inside the same model stays in the block.** Tag it
  (`[model: claude-opus-5 | effort: medium]` after a `high` task) and note it in
  a clause, but do not break the block — the cost of an extra paste exceeds
  what one rung buys. Two rungs or more, or any model change, breaks it.

### Boundary 2 — a finding that changes what follows

The first point where a result would rewrite the next task: the end of a
diagnosis, an audit, a spike, a design decision. Everything before that cut is
writable now; everything after it is a guess dressed as a plan. Past five
tasks, assume at least one such boundary exists and go find it.

Close the segment with:

```
Report back with: <the specific results that decide the next segment>.
Then re-run /rebuild-prompt with those results to get the next one.
```

This boundary differs from a model switch in what the user does next. A switch
says *change a setting and paste the block I already gave you*; a finding says
*come back to the skill so the next block can be written against what actually
happened*. Never write the finding boundary as a switch — handing over a
pre-written next block defeats the entire reason for cutting there.

### Boundary 3 — an approval only the user can give

A destructive, outward-facing, or irreversible step starts a segment rather
than sitting buried mid-block where the session reaches it unattended.

### Why separate blocks, not markers

A stop marker inside a block the user pastes whole is a marker the session runs
straight past — it has the whole instruction set in front of it and no reason
to honour a line telling it to wait. Physical separation is the only version
that holds.

### The outline that follows

After the last delivered block, list the remaining segments **one line each** —
task name plus the capability and model expected — so the user sees the whole
arc without receiving stale instructions for it. Mark it provisional. For a
finding boundary it genuinely is provisional; re-planning against real results
is the point of cutting there.

## The model plan

Every delivery leads with a model plan, above the first fenced block, so the
user knows the shape before pasting anything:

```markdown
**Model plan** — 2 sessions.

| Segment | Model | Effort |
|---|---|---|
| 1 — audit the current schema | `claude-sonnet-5` | `medium` |
| 2 — implement the migration | `claude-opus-5` | `xhigh` |
```

When every task shares one model and effort, drop the table and say it in a
line: *"Model plan: one session, `claude-opus-5` at `xhigh` throughout — no
switching."* The reassurance is the useful part; a one-row table is noise.

State the session count in the heading. "3 sessions" tells the user what they
are committing to more directly than three table rows do.

## Reminders

- Deliver the **finished, template-formatted** prompt in the first response —
  not a draft, not a question round first.
- Ask before delivering only for a fork that is both genuinely binary AND
  changes which capability gets attached (max 1–2 such questions). Everything
  else defaults + gets an inline `[?]` in the delivered prompt.
- A single task with an uncontested capability skips the ballot entirely.
  Asking a question with one real answer is the same friction the skill was
  built to remove, pointed the other way.
- Never build a single-option AskUserQuestion. No natural choice set → plain
  text, or offer known context (recent projects, prior memories) as real
  multiple-choice options.
- `grilling` runs at step 0, before decomposition — not as a post-delivery
  offer. Skip it only for a trivial single mechanical task, and say in one
  line that it was skipped so the user can ask for it anyway.
- Offer `/interview-me` after delivery when what remains is missing
  requirements rather than a questionable premise. The premise was already
  tested at step 0, so this is a narrower offer than it used to be.
- The deliverable is one fenced block **per segment**, each repeating the
  self-invocation line, with the model plan above the first block. Never
  deliver a multi-segment job as one block with stop markers inside it.
- After delivering the final prompt: stop. The user runs it themselves.
