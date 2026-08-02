# Routing guide

Mechanics only — exact strings, schemas, templates. For why any of this
exists, see README.md § Design notes. For the pipeline steps, see SKILL.md.

## Where the capability list comes from

Read live every run — never guess or rely on memory:

- **Skills** — the "following skills are available for use with the Skill
  tool" listing.
- **Subagents** — the "available agent types for the Agent tool" listing.
- **MCP tools** — loaded `mcp__*` tools, plus deferred ones via `ToolSearch`.

| State | Output |
|---|---|
| Needs auth | Note under Flags |
| Disconnected | Fallback or note the gap |
| Setup precondition | State the exact command to run first |
| Absent, pipeline step needed it | Run the fallback, flag the substitution (SKILL.md § Standing rules) |

## Building the shortlist

Narrow before ranking, in order: **stack/platform** (drop what can't apply —
this is the highest-leverage filter), then **task shape** (build vs. review
vs. plan vs. verify), then rank what survives.

**Namespace tie-break** when a plugin-scoped and generic skill both match:
1. Project-scoped skill from the repo being worked in.
2. More specific skill, when the detected stack matches it exactly.
3. Generic/built-in skill otherwise.
State which rule decided it.

**Report the funnel**: "14 matched; these 3 ranked highest" — never present
3-of-20 as though it were 3-of-3.

Sweep four angles per task before ranking: domain-specific skill,
discipline skill (design/audit/motion/review as a craft), taste/direction
skill, subagent equivalent. For each runner-up, record why it ranked
below — wrong layer, too general, overlapping, unavailable.

## Routing history

**Location:** `~/.claude/rebuild-prompt/history.md` — outside any skill's
install directory, so a `cp -r` update or reinstall never touches it.
Created on first write if absent.

**Format** — one row per task, appended:

```markdown
| date | task shape | chosen | passed over |
|---|---|---|---|
| 2026-07-23 | design refinement, canvas tool | /impeccable | /high-end-visual-design, /transitions-dev |
```

**Read once per run**, before ranking any contested tasks — not a separate
read per task. A matching past pick: "you chose this for a similar task on
`<date>`", ranked up one position. Still show the full shortlist. Still ask.
Loses to the stack filter.

**Write only after the user picks.** Task *shape* only, never prompt
content — no client names, no URLs, no credentials.

## Matching heuristics

- Specific beats general; match on description, not name.
- Process before implementation (planning/debugging skill invoked first).
- Verification/QA-shaped work → subagent by default (Code Reviewer,
  Evidence Collector, Performance Benchmarker, UX Researcher, Accessibility
  Auditor, …) over a generic skill.
- One capability per task, usually — stack a second only when the task
  truly spans two domains.
- Nothing fits → attach nothing, say so.
- Order by dependency; communication/publishing steps last.

## Standing rule: agent tasks report as they go

Every task that dispatches an agent carries a reporting contract:

1. Report at checkpoints, not just at the end.
2. Return artifacts, not adjectives — "verified" with nothing attached is a
   **failed task**.
3. Surface findings verbatim, including failures.

| Check shape | Required artifact |
|---|---|
| Visual / layout | Fresh-load screenshots at every breakpoint |
| Performance | Before/after numbers plus the measurement method |
| Correctness / build | The actual command output |
| Accessibility | The assistive-technology result |
| Security | `file:line` plus a concrete reproduction |
| Research / discovery | The sources read, cited |

Mark independent tasks parallelizable in the prompt. Never mark tasks
parallel when they touch the same files or canvas.

## Standing rule: implementation tasks get one fresh-context review

`/code-review` if installed → Code Reviewer subagent if one exists → prose
fallback. Mandate: read the diff *and* drive the change end-to-end. Write it
as a numbered sub-step under the task it gates, not a separate top-level
task. Tasks with no executable change (content, design, research, planning)
don't get it.

Never emit a `/skill` name absent from the session listing — check first,
fallback second, flag the substitution.

## Standing rule: plan-shaped tasks render as a commentable HTML document

Triggers: Plan Mode, `/superpowers:writing-plans`, `/interview-me`, or any
"make a plan for X" ask.

- Publish via the Artifact tool.
- Reuse an installed commentable-preview mechanism if one exists (e.g.
  `/interview-me`'s Phase 3 Interactive Spec Preview, verbatim).
- Fallback: build it directly — every block-level section gets
  `class="commentable"` + a unique `data-id`, plus a Revise action.
- A Revise action collects comments and redeploys to the same URL, treated
  as revisions to the plan.

## Output template

```markdown
## Your rebuilt prompt

​```
As you reach each task below, invoke the skill named in it via the Skill tool before doing that task's work. The /names are instructions to you, not decorative text — load each one yourself; I have not tagged them.

<Overall goal in the user's voice, one or two sentences, on ONE line, ending with why it matters and what the output enables.>

<Context block only for a fresh-session paste, or a fact that would break the task if wrong and isn't inferable.>

<constraints>
<hard constraints, destructive-action guards, credential boundaries — one per line. Omit the block if there are none.>
</constraints>

<setup preconditions>

Deliver what is asked at the scope intended; if a better approach exists, say so in a sentence and continue with the task as asked. Delegate to a subagent only for genuinely independent, sizeable tracks — never to double-check your own work — and keep spawn counts low. Local reversible edits proceed; anything destructive, outward-facing, or hard to undo asks first.

## Task 1 — <task name, involves writing/modifying code>   [model: <id> | effort: <level>]
Use /<skill-a> (and /<skill-b> if the task truly spans two domains).
<What to do, requirements — one unbroken line per paragraph. No self-checking language.>
Then: hand the change to /code-review as a fresh reader — it reads the diff and drives the change end-to-end.

## Task 2 — <verification/QA-shaped task>  (after Task 1)   [model: <id> | effort: <level>]
Dispatch the <Agent Name> agent.
<What to verify/do.>
Report each check before running it and its result immediately after, then return <the specific artifact>. "Verified" with nothing attached is a failed task. Surface whatever comes back verbatim, failures included.

## Task 3 — <plan/spec-producing task>   [model: <id> | effort: <level>]
Use /superpowers:writing-plans (or /interview-me, whichever fits).
<What the plan needs to cover.>
When ready, publish as an interactive HTML artifact reusing the commentable-preview mechanism. Treat submitted comments as revision requests.

Done = <success criteria>.
​```

<Model/effort boundary closes INSIDE the block, next segment delivered as its own separate block:>
​```
Stop here. Switch this session to <model> at <effort> before continuing, then paste the next block.
​```

<Finding boundary closes with these two lines instead — the next block is NOT pre-written:>
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
| 3 | `/superpowers:writing-plans` | <one line> |

**Flags:** <auth / setup preconditions / gaps / fallback substitutions — omit if none>
```

One row per task — never fewer rows than tasks. A table with a task missing
demonstrates the exact anti-pattern the "never collapse the mapping" rule
below warns against.

**Uncontested-task shortcut.** This applies per task, at any job size — a
3-task job can have one uncontested task and two contested ones in the same
delivery. A contested task gets a row in the "why these skills" table, with
its runner-up and why it lost. An uncontested task gets no row — its pick and
nearest runner-up are stated inline in the task's own body instead, the way
the single-task shortcut states them at the top level when the whole job is
one task.

**Never collapse the mapping.** A multi-task prompt with a single skill list
at the top loses the routing.

## Model and effort annotations

Tag each task `[model: <id> | effort: <level>]`.

**Effort** is a fixed ladder: `low | medium | high | xhigh | max`. `xhigh` is
the default for coding/agentic work; `low`/`medium` are the primary lever on
cost and latency; `max` only when correctness matters more than cost.

**Model** — same discipline as skills, subagents, and MCP tools above: a
model name is a capability that changes over time, and this file has no way
to check it live. Default action: ask the user which models they actually
have access to in this session. Fall back to the dated snapshot below only
when asking isn't practical (e.g. mid-delivery, no natural place to pause) —
*as of 2026-08-02*, it turns over faster than this file gets updated, so
treat it as a stale reference, not a lookup to perform: `claude-opus-5`
default; `claude-sonnet-5` for cost-sensitive or high-volume work;
`claude-haiku-4-5` for mechanical work; `claude-fable-5` only for the
hardest, longest, most ambiguous jobs.

**Binding vs advisory.** A task dispatched to a subagent takes its own model
and effort — the tag binds. A directly-run task inherits the session's
model — the tag is advisory, telling the user which session to paste the
segment into. This is why a model change and a segment boundary are the
same event: a directly-run task's tag only takes effect if the prompt stops
where it changes.

## Segments

Three things open a boundary: a model/effort change on directly-run work, a
finding that would rewrite what follows, or an irreversible step needing
approval. Task count alone opens nothing.

- **Model boundary** — closes naming the exact model and effort; next block
  already written. Name the model in full (`claude-sonnet-5`, not
  "Sonnet"). Exemptions: subagent tasks never force a stop; a one-rung
  effort change inside the same model stays in the block.
- **Finding boundary** — closes asking for results, sending the user back
  to `/rebuild-prompt`; next block deliberately not pre-written.
- **Approval boundary** — a destructive/outward-facing/irreversible step
  starts its own segment rather than sitting mid-block.

Separate blocks, never markers inside one block.

After the last delivered block: remaining segments, one line each — task
name, capability, model — marked provisional.

## Model plan

Leads every delivery, above the first block:

```markdown
**Model plan** — 2 sessions.

| Segment | Model | Effort |
|---|---|---|
| 1 — audit the current schema | `claude-sonnet-5` | `medium` |
| 2 — implement the migration | `claude-opus-5` | `xhigh` |
```

One model/effort throughout: collapse to a line — *"Model plan: one session,
`claude-opus-5` at `xhigh` throughout — no switching."*

## Reminders

Mechanics only, per this file's own scope — pipeline-step rules (grilling,
`/interview-me`) live in SKILL.md, not here.

- Deliver the finished, template-formatted prompt in the first response —
  not a draft, not a question round first.
- Never build a single-option AskUserQuestion. No natural choice set → plain
  text, or offer known context as real options.
