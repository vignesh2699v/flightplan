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

## Standing rule: implementation tasks get an automatic quality gate

Any task in the rebuilt prompt that **writes or modifies code** automatically
gets two steps appended after it — no need to ask, this is a default, not a
per-run question:

1. **Code review** — `/code-review` if installed; otherwise dispatch a
   code-reviewing subagent (e.g. a "Code Reviewer" agent type) if one exists;
   otherwise state the review expectation in prose.
2. **Verification** — `/verify` if installed; otherwise state the expectation
   in prose: drive the change end-to-end and observe real behaviour, not just
   run tests/typecheck.

Never emit a `/skill` name that isn't in the current session's listing — check
first, fall back second, and flag the substitution in the Flags section.

Write these as their own numbered sub-steps directly under the implementation
task they gate, not as separate top-level tasks — they're part of "done" for
that task, not independent work. A task that's pure content, design, research,
or planning (nothing executable changes) does NOT get this pair — only tasks
that touch code.

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

```markdown
## Your rebuilt prompt

​```
<Overall goal in the user's voice, one or two sentences.>

Context: <project names, IDs, paths, prior decisions a fresh session needs>
<setup preconditions, e.g. CLI commands to run first>

## Task 1 — <task name, involves writing/modifying code>
Use /<skill-a> (and /<skill-b> if the task truly spans two domains).
<What to do, requirements, constraints.>
Then: run /code-review on the changes; then run /verify to confirm the
change actually works end-to-end, not just that tests/typecheck pass.

## Task 2 — <verification/QA-shaped task>  (after Task 1)
Dispatch the <Agent Name> agent (e.g. Code Reviewer, Evidence Collector,
Performance Benchmarker — whichever fits the check being asked for).
<What to verify/do, and the evidence required.>   ← agents/MCP tools are
                                                     named as instructions,
                                                     not slashes

## Task 3 — <plan/spec-producing task>
Use /superpowers:writing-plans (or /interview-me, whichever fits).
<What the plan needs to cover.>
When the plan is ready, publish it as an interactive HTML artifact (Artifact
tool) reusing /interview-me's commentable-preview mechanism — click-to-
comment sections + a Revise action — instead of a bare .md file. Treat
submitted comments as revision requests for the plan.

Done = <success criteria for the whole prompt — what the user reviews>.
​```

**Why these skills:**
| Task | Capability | Why |
|---|---|---|
| 1 | `/<skill-a>` | <one line> |
| 2 | <Agent Name> | <one line> |

**Flags:** <auth / setup preconditions / gaps — omit section if none>
```

**The skill names above are illustrative.** The example assumes `/code-review`,
`/verify`, `/interview-me` and a plan-writing skill are installed. Substitute
whatever the current session actually has, and use the documented fallbacks
when they're absent.

**Never collapse the mapping.** A multi-task prompt with a single skill list at
the top loses the routing — the per-task skill assignment is the core value of
this output. Single-task prompts may use a single header line instead.

Rules for the prompt body:

- Written to be pasted into a **fresh session** — include the context a new
  session won't have (IDs, paths, decisions), because memory may not surface it.
- If a subagent or MCP tool (not a slash skill) is part of the routing, name it
  as an instruction inside the body ("dispatch the Evidence Collector agent to
  verify…"), since only skills are slash-invokable.
- Success criteria are mandatory — a prompt without a definition of done is
  not polished.
- Keep it as short as completeness allows. Polish = density, not length.

## Reminders

- Deliver the **finished, template-formatted** prompt in the first response —
  not a draft, not a question round first.
- Ask before delivering only for a fork that is both genuinely binary AND
  changes which capability gets attached (max 1–2 such questions). Everything
  else defaults + gets an inline `[?]` in the delivered prompt.
- Never build a single-option AskUserQuestion. No natural choice set → plain
  text, or offer known context (recent projects, prior memories) as real
  multiple-choice options.
- `/interview-me` only when the user opts in, after delivery.
- After delivering the final prompt: stop. The user runs it themselves.
