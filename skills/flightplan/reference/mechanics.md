# Mechanics

Exact strings, schemas and templates. For why any of this exists, see
`docs/design-notes.md`. For the pipeline steps, see SKILL.md.

## Where the capability list comes from

Read live every run — never guess or rely on memory:

- **Skills** — the "following skills are available for use with the Skill
  tool" listing.
- **Subagents** — the "available agent types for the Agent tool" listing.
- **MCP tools** — loaded `mcp__*` tools, plus deferred ones via `ToolSearch`.

| State | Output |
|---|---|
| Needs auth | Note under Flags |
| Disconnected | Fallback, or note the gap |
| Setup precondition | State the exact command to run first |
| Absent, a pipeline step needed it | Run the fallback, flag the substitution |

## Context fields

Five, each one line, each naming where it came from:

```markdown
- **What this is** — <one line> · *README, line 3*
- **Who it's for** — <one line> · *CLAUDE.md*
- **What exists now** — <one line> · *git log, 40 commits*
- **What success looks like** — <one line> · *you, at grilling*
- **What's out of scope** — <one line> · *you, at grilling*
```

A field reading couldn't settle says so — `*not established*` — rather than
carrying a confident guess. The source is what makes a wrong inference cheap
to spot.

## The plan page

**Path:** `~/.claude/flightplan/jobs/<slug>.html` — outside any install
tree, so a reinstall can't touch it. Slug is the project in 2–4 kebab-case
words, undated: a project picked up next week has to resolve to the same
path.

**One project, one URL, for the plan's whole life.** Publish via the
Artifact tool, titling the page with the slug and never changing it — that
title is what identifies the project later. Recover an existing plan with
the tool's `list` action, match on that title, and pass its `url` on every
redeploy. No match in the list — an older project, past the rows it
returns — means say so and file a fresh plan rather than assume there was
never one.

**Never write the URL to `history.md`**; that file stores task shape only,
deliberately.

**Structure**, in order:

1. **Header** — the five context fields, the outcome in one line, the
   approach in two or three, and a Flags line when there is anything to
   flag. First publish adds a Flags entry: the page carries every ticket
   prompt verbatim, including whatever the raw ask named, and artifacts are
   private by default.
2. **Tickets** — one block each, in dependency order: ID, title, the
   capability and what it beat, `[model | effort]`, any constraint that
   applies, its done-criterion. No prompt bodies here. IDs run `T-01`
   upward and stay fixed for the plan's life — the writeback addresses a
   ticket by ID, so renumbering breaks it.
3. **Tracker** — one row per ticket. Status, one line of outcome, evidence
   link, and on every finished row a quiet marker that a handoff is safe
   here — except the last, which says the plan is closed instead.

Status vocabulary is `pending`, `live`, `done`, and `stale` for a ticket
whose plan a finding invalidated.

Ticket blocks are commentable by the same markup contract as the standing
rule at the end of this file, with one difference it states explicitly: that
rule publishes a ticket's *deliverable* at its own URL, while these blocks
live on this page. A comment returns as a revision request against that
ticket.

**In chat alongside the URL:** one line naming which ticket is live. Nothing
else — the page holds the header and the prompt, and a second copy in chat
is the scan problem returning.

## Self-invocation

Open a ticket that names a skill with this line, verbatim:

```markdown
Invoke the skill named below via the Skill tool before doing this ticket's work. The /name is an instruction to you, not decorative text — load it yourself; I have not tagged it.
```

Omit it when the ticket names no skill.

## Ticket template

```markdown
​```
<self-invocation line, if the ticket names a skill>

<One sentence of intent — what this ticket is for and why it matters.>

Use /<skill> (and /<second> only where the ticket truly spans two domains).

<What to do, one unbroken line per paragraph. No self-checking language.>

<One line per hard constraint, destructive-action guard or credential boundary that applies. Omit when none does.>

Deliver what is asked at the scope intended; if a better approach exists, say so in a sentence and continue with the task as asked. Delegate to a subagent only for genuinely independent, sizeable tracks — never to double-check your own work. Local reversible edits proceed; anything destructive, outward-facing, or hard to undo asks first.

Done = <criterion, phrased so it can be reported pass or fail>.
<Writeback line — § Writeback.>
​```
```

## Writeback

The last line of every ticket prompt:

```markdown
When this is done, update ticket <ID> on <page URL> (source at <page path>): set its status, add one line saying what came out of it, and link the evidence. If it went off-plan, say so there and mark the tickets after it stale. Then tell me pass or fail on the done-criterion above.
```

On the plan's last ticket, the line ends differently — there is no next
ticket to hand off to:

```markdown
…and link the evidence. This is the last ticket, so close the plan on the page: mark it complete and say in one line what the whole plan produced. Then tell me pass or fail on the done-criterion above.
```

The session running the ticket reads the page source, edits that ticket's
row, and republishes to the same URL. It changes the record only — never a
ticket that hasn't run.

## One-liner

A single-outcome ask with no plan open. No page, no context phase, no
tables:

```markdown
​```
Use /<skill-or-agent>, `<model>` at `<effort>`. <One-sentence instruction, folding in the requirement and why it matters.> <One-sentence hard constraint — only when a real one applies; omit entirely otherwise.> Done = <criterion>.
Tell me pass or fail — I'll flag any gap.
​```
**Why:** <the pick, and its nearest runner-up if the choice was contested.>
```

## Building the shortlist

Narrow before ranking, in order: **stack/platform** (drop what can't apply —
the highest-leverage filter), then **ticket shape** (build vs. review vs.
plan vs. verify), then rank what survives.

**Namespace tie-break** when a plugin-scoped and a generic skill both match:
1. Project-scoped skill from the repo being worked in.
2. More specific skill, when the detected stack matches it exactly.
3. Generic or built-in skill otherwise.

State which rule decided it.

**Report the funnel**: "14 matched; these 3 ranked highest" — never present
3-of-20 as though it were 3-of-3.

Sweep four angles per ticket before ranking: domain-specific skill,
discipline skill, taste/direction skill, subagent equivalent. For each
runner-up, record why it ranked below — wrong layer, too general,
overlapping, unavailable.

## Matching heuristics

- Specific beats general; match on description, not name.
- Process before implementation.
- Verification-shaped work → subagent by default over a generic skill.
- Nothing fits → attach nothing, say so.
- Order by dependency; communication and publishing tickets last.

## Routing history

**Location:** `~/.claude/rebuild-prompt/history.md`, created on first write
if absent. Deliberately outside the install tree.

```markdown
| date | task shape | chosen | passed over |
|---|---|---|---|
| 2026-08-11 | design refinement, canvas tool | /impeccable | /high-end-visual-design, /transitions-dev |
```

**Read once per run**, before ranking any contested ticket. A matching past
pick: "you chose this for a similar shape on `<date>`", ranked up one
position. Still show the full shortlist. Still ask. Loses to the stack
filter.

**Write only after the user picks.** Task *shape* only — no client names, no
URLs, no credentials, no prompt content.

## Model and effort annotations

Tag each ticket `[model: <id> | effort: <level>]`.

**Effort** is a fixed ladder: `low | medium | high | xhigh | max`. `medium`
is the default — except a pure clarification, which defaults to `low`:
there's execution risk in acting on a wrong guess, not in asking one
question. Escalate one rung at a time, and only when the *ticket itself*
costs more to get wrong: the one grilling flagged as the costliest
assumption, or a ticket whose own shape demands it (a large diff, a security
or payment path, deep multi-file reasoning). An unresolved premise isn't on
that list. `max` only when correctness matters more than cost.

**Model** — a model name is a capability that changes over time and this
file can't check it live. Default action: ask which models the session
actually has. Fall back to the dated snapshot only when asking isn't
practical — *as of 2026-08-02*, treat it as a stale reference rather than a
lookup: `claude-opus-5` default; `claude-sonnet-5` for cost-sensitive or
high-volume work; `claude-haiku-4-5` for mechanical work; `claude-fable-5`
only for the hardest, longest, most ambiguous jobs.

**Binding vs advisory.** A ticket dispatched to a subagent takes its own
model and effort — the tag binds. A directly-run ticket inherits the
session's model, so the tag tells the user what to switch to. One ticket per
paste means the switch always has somewhere to happen.

## Standing rule: agent tickets report as they go

Every ticket that dispatches an agent carries a reporting contract:

1. Report at checkpoints, not just at the end.
2. Return artifacts, not adjectives — "verified" with nothing attached is a
   **failed ticket**.
3. Surface findings verbatim, including failures.

| Check shape | Required artifact |
|---|---|
| Visual / layout | Fresh-load screenshots at every breakpoint |
| Performance | Before/after numbers plus the measurement method |
| Correctness / build | The actual command output |
| Accessibility | The assistive-technology result |
| Security | `file:line` plus a concrete reproduction |
| Research / discovery | The sources read, cited |

## Standing rule: code tickets get one fresh-context review

`/code-review` if installed → a Code Reviewer subagent if one exists → prose
fallback. Mandate: read the diff *and* drive the change end-to-end. Write it
as a numbered sub-step inside the ticket it gates, never as its own ticket.
Tickets with no executable change don't get it.

Never emit a `/skill` name absent from the session listing — check first,
fall back second, flag the substitution.

## Standing rule: plan-shaped tickets render as a commentable document

Triggers: Plan Mode, `/superpowers:writing-plans`, `/interview-me`, or any
"make a plan for X" ticket.

- Publish via the Artifact tool, at its own URL, separate from the plan
  page. (The plan page's own ticket blocks reuse the markup below; only the
  destination differs.)
- Reuse an installed commentable-preview mechanism if one exists.
- Fallback: build it directly — every block-level section gets
  `class="commentable"` and a unique `data-id`, plus a Revise action.
- A Revise action collects comments and redeploys to the same URL.

## Reminders

- Deliver the live ticket in the first response — not a draft, not a
  question round first.
- Never build a single-option AskUserQuestion. No natural choice set → plain
  text, or offer known context as real options.
