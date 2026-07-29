# rebuild-prompt

A [Claude Code](https://claude.com/claude-code) skill that turns a rough,
half-formed prompt into a polished, ready-to-paste prompt — with the right
skills and agents already routed to each task.

It does **not** run the prompt. It hands you one you can paste into a fresh
session yourself.

## The problem

You have dozens of skills installed. You type "make my dashboard less
generic and check the performance" and get a generic response, because
nothing routed that to the dedicated data-viz skill, the de-slop skill, and
a performance-benchmarking agent.

The capability was installed. It just never got picked.

## What it does

Given a rough prompt, `rebuild-prompt`:

1. **Decomposes** it into ordered tasks with dependencies.
2. **Shortlists 2–3 real candidate skills/agents per task** — ranked, each
   with *why it ranked there*, including why the runners-up lost.
3. **Lets you choose** which capability runs each task.
4. **Returns a finished prompt** with your chosen skills embedded per task,
   success criteria written in, and any unresolved scope marked inline.

The shortlist step is the point. Routing decisions made silently are
routing decisions you can't overrule.

## Example

**In:**

```
this app feels slow and the UI looks kind of boring, can you fix it up
```

**Out:**

```
The <project> dashboard has two problems, in order.

Context: the slowness hasn't been isolated yet — diagnose before assuming.

## Task 1 — Diagnose and fix performance
Dispatch the Performance Benchmarker agent.
Profile the app first (load/render vs. action/data-layer) rather than guessing the category. Report what was slow and what changed, with before/after numbers.

## Task 2 — De-genericize the UI   (after Task 1)
Use /kill-ai-slop.
The app currently reads as visually generic. Remove the tells without touching the performance fix from Task 1.

Done = profiling data shows the bottleneck fixed with before/after numbers, and the UI no longer reads as templated.
```

...plus a table showing which capabilities were considered and why each was
picked or passed over.

## Install

Clone into your personal skills directory:

```bash
git clone https://github.com/vignesh2699v/claude-rebuild-prompt.git /tmp/claude-rebuild-prompt
mkdir -p ~/.claude/skills
cp -r /tmp/claude-rebuild-prompt/skills/rebuild-prompt ~/.claude/skills/
```

Or for a single project only, copy into that project's `.claude/skills/`
instead.

No build step, no dependencies — it's markdown. Claude Code discovers it on
the next session.

Verify it registered:

```bash
ls ~/.claude/skills/rebuild-prompt
# SKILL.md  reference/
```

## Usage

```
/rebuild-prompt <your rough prompt>
```

You'll get a shortlist of candidate capabilities per task, pick one for
each, then receive the finished prompt.

It also activates on natural phrasing like "rebuild this prompt", "polish
this prompt", or "add the right skills to this".

## Built-in defaults

- **Code-writing tasks** get an automatic code-review + verification pass
  appended — you don't have to remember to ask.
- **Plan/spec tasks** are routed to render as an interactive HTML document
  with click-to-comment sections, instead of a bare `.md` file, so review
  comments become plan revisions.
- **Verification-shaped work** ("check this", "confirm it works") routes to
  a subagent rather than a generic skill — and every agent task states what
  artifact it must return. "Verified" with nothing attached is a failed task.
- **Every prompt self-invokes its skills** — it opens with a line telling the
  receiving session to load each named skill itself via the Skill tool.
- **Every task carries an effort hint** (`[effort: low|medium|high]`) — a
  second routing axis alongside *which* capability runs it.
- **It remembers what you picked.** Past choices are recorded per task shape
  and surface in later shortlists as a ranking signal — never as a decision
  made on your behalf.

Both standing rules name specific skills (`/code-review`, `/verify`, and a
commentable-preview skill). Each is applied **only if installed**, with a
documented fallback otherwise — the skill degrades gracefully in any
environment.

## Requirements

- Claude Code (any recent version — nested `.claude/skills/` discovery).
- No runtime dependencies. No `npm install`, no `pip install`.
- Routes against whatever skills, agents, and MCP tools you already have.
  It never invents a capability name — with nothing installed, it still
  produces a well-structured prompt, just with fewer skills attached.

## Design notes

A few decisions that came out of testing it against real prompts:

- **It doesn't interview you.** An earlier version ran a requirements
  interview before delivering. In practice that produced unanswered
  question rounds that just delayed the thing you asked for. Scope
  ambiguity now gets a sensible default plus an inline `[?]` flag in the
  delivered prompt. The only gate is your choice of capability.
- **It never collapses the task→skill mapping.** A multi-task prompt with
  one skill list at the top loses the routing, which is the whole value.
- **No context preamble by default.** An earlier version opened every
  prompt with a block restating project IDs, paths and history. But the
  prompt usually gets pasted back into the same conversation, which already
  holds all of it — and context copied out of memory files is a *snapshot*,
  so restating it as present-tense fact is a correctness risk, not just
  verbosity. Now it goes straight into the tasks. A context line survives
  only if the task would break or go wrong without it (a hard constraint, a
  setup command, a non-obvious gotcha), and anything sourced from memory is
  marked "as of `<date>`, verify" rather than asserted.
- **Pasted prompts can't be tagged by hand — so they tag themselves.**
  Pasting text doesn't fire the editor's slash-command autocomplete, and
  only one slash command can ever lead a message, so a six-task prompt with
  six skills is impossible to UI-tag *by design*. The mechanism that works
  is the Skill tool: the model reads "Use /impeccable" as an instruction and
  loads the skill itself. Every rebuilt prompt therefore opens with a line
  saying exactly that. It makes invocation reliable, not guaranteed — it's
  an instruction the model follows, not a hard mechanism — but it beats
  tagging six skills one at a time, which was never going to work anyway.
- **Shortlists report their denominator.** A session can now hold up to 500
  skills, and plugin packs install dozens of near-duplicates — a dozen
  language-specific code reviewers alone. Candidates get narrowed by
  stack/platform *before* ranking, and the output states the funnel ("14
  matched; these 3 ranked highest"). Presenting 3-of-20 as though it were
  3-of-3 would recreate the exact invisible-filtering problem the shortlist
  step exists to prevent.
- **A dispatched agent runs out of sight.** What comes back is a summary you
  can't audit — and a summary is exactly where a check that never happened
  becomes "verified". So every agent task now carries a reporting contract:
  report at checkpoints rather than only at the end, return the specific
  artifact for that check shape (fresh-load screenshots at *every*
  breakpoint, before/after numbers with method, actual command output, cited
  sources), and surface findings verbatim including failures. Independent
  tasks get marked parallelizable — but never ones touching the same files,
  where concurrent edits conflict and the time saved isn't worth it.
- **Routing history is a signal, not a preference lock.** The shortlist step
  asks you the same judgement call repeatedly — pick `/impeccable` over
  `/high-end-visual-design` three times and the fourth ask is noise. So
  picks are logged per task shape in a local `routing-history.md` beside the
  skill, and a matching past pick gets flagged and ranked up one position.
  It never auto-applies, never hides a runner-up, and always loses to the
  stack filter. The log stores task *shape* and capability names only —
  never your prompt text, since prompts routinely carry client names,
  unreleased work and internal URLs. For a project-scoped install, gitignore
  it: it's local preference data, not shared config.
- **The prompt body is never hard-wrapped.** An earlier version wrote each
  paragraph as manually broken ~70-80-character lines, matching how this
  guide's own prose is formatted. That's fine for docs that are only ever
  read — but the delivered prompt gets pasted into a text box, and a real
  newline in the text is not the same as a soft wrap: the box can only
  reflow text that has none. Hard-wrapped output pastes ragged and visibly
  wastes half the box no matter how wide it is. Now every paragraph in the
  delivered prompt is one unbroken line; breaks appear only between
  paragraphs and tasks.
- **Not every task needs a skill.** Forcing one onto straightforward work
  in a well-patterned codebase makes the output worse. "None needed" is
  always an option.

## License

MIT
