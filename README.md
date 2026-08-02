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

1. **Grills the premise first** — what you're actually trying to achieve, not
   just what you asked for. Skipped for trivial one-task prompts.
2. **Decomposes** it into ordered tasks with dependencies.
3. **Shortlists 2–3 real candidate skills/agents per task** — ranked, each
   with *why it ranked there*, including why the runners-up lost.
4. **Lets you choose** which capability runs each task.
5. **Returns a finished prompt** with your chosen skills embedded per task,
   a model and effort level on each, success criteria written in, and any
   unresolved scope marked inline.

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

- **Code-writing tasks** get an automatic fresh-context review appended — you
  don't have to remember to ask. One reviewer, in a separate context, that
  both reads the diff and drives the change end-to-end.
- **Plan/spec tasks** are routed to render as an interactive HTML document
  with click-to-comment sections, instead of a bare `.md` file, so review
  comments become plan revisions.
- **Verification-shaped work** ("check this", "confirm it works") routes to
  a subagent rather than a generic skill — and every agent task states what
  artifact it must return. "Verified" with nothing attached is a failed task.
- **Every prompt self-invokes its skills** — it opens with a line telling the
  receiving session to load each named skill itself via the Skill tool.
- **Every task carries a model and effort hint**
  (`[model: claude-opus-5 | effort: xhigh]`) — two more routing axes alongside
  *which* capability runs it. Binding on subagent tasks, which take their own
  model and effort; advisory on direct work, where it tells you which session
  to paste the round into.
- **One task, one obvious capability → no questions.** The shortlist only
  appears when there's a real choice in it. Asking you to confirm an
  uncontested pick is the same friction the skill exists to remove.
- **Prompts arrive one segment at a time, one fenced block each.** A block
  ends wherever the next task needs a different model, wherever a finding
  would change what follows, or wherever an irreversible step needs your
  approval — not at a fixed task count.
- **A model switch is a hard stop, not a suggestion.** If segment two needs a
  different model than segment one, segment one ends by naming the exact model
  and effort to switch to before you paste the next block. Subagent tasks are
  exempt: a dispatched agent carries its own model, so it never interrupts you.
- **Every delivery opens with a model plan** — how many sessions this job
  takes and which model runs each, before you paste anything.
- **It remembers what you picked.** Past choices are recorded per task shape
  and surface in later shortlists as a ranking signal — never as a decision
  made on your behalf.

Both standing rules name specific skills (`/code-review` and a
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

- **It grills you, but it doesn't interview you.** An early version ran a
  requirements interview before delivering, and it produced unanswered
  question rounds that just delayed the thing you asked for — so it was cut,
  and the rule became "prompt before questions." That rule has now been
  partly reversed, deliberately: a stress-test of the *premise* runs first,
  because it's a different animal from a requirements checklist. An interview
  asks what you want built; grilling asks whether you're pointed at the right
  problem, and the answer changes how the work decomposes — which changes what
  gets routed. So it has to run before the shortlist, not after. Requirements
  ambiguity is still handled the old way: a sensible default plus an inline
  `[?]` in the delivered prompt, never a question round.
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
- **Point, don't paste.** If a fact lives in a file the executing session can
  open — a playbook, a README, a config, the code itself — the prompt names
  the path instead of copying the contents in. Inlining a documented list of
  gotchas doesn't just make the prompt longer; it forks the fact, so the copy
  in the prompt ages while the original moves on. A stale copy asserted as
  current is worse than a pointer. Same reasoning as the context-preamble
  rule, one level deeper: that one says don't restate what the conversation
  holds, this one says don't restate what the filesystem holds.
- **The prompt body is never hard-wrapped.** An earlier version wrote each
  paragraph as manually broken ~70-80-character lines, matching how this
  guide's own prose is formatted. That's fine for docs that are only ever
  read — but the delivered prompt gets pasted into a text box, and a real
  newline in the text is not the same as a soft wrap: the box can only
  reflow text that has none. Hard-wrapped output pastes ragged and visibly
  wastes half the box no matter how wide it is. Now every paragraph in the
  delivered prompt is one unbroken line; breaks appear only between
  paragraphs and tasks.
- **The ballot became a toll booth for small jobs.** Every run went through
  decompose → shortlist → AskUserQuestion → deliver, regardless of size. For
  a one-task prompt where a single capability obviously fits, that's a
  question with one real answer — the exact friction this skill was built to
  remove, pointed the other way. Now a size gate at step one routes it: one
  uncontested task skips the ballot entirely and gets the pick plus its
  nearest runner-up in a line each, so you can still overrule without being
  stopped to confirm.
- **A six-task prompt is stale by task three.** The later tasks were written
  before the earlier ones ran, so they encode assumptions the work has
  already disproved. Checkpoint gates inside one prompt don't fix that —
  they pause execution but the stale instructions are still sitting there.
  So past ~5 tasks the skill now delivers round one only, cut at the first
  point where a finding would change what follows, and hands back a re-entry
  line: run it, return with results, and round two gets *planned* against
  them rather than guessed ahead of them.
- **Model choice and block boundaries are the same decision.** A per-task
  model tag is only enforceable where a model boundary exists. Subagents take
  their own model and effort, so it binds there; a directly-run task inherits
  the session's model, and one message runs on one model. That makes "route
  this to Sonnet" and "cut the prompt here" the same instruction — the tag was
  decoration until the cut existed to keep its promise.
- **Stop markers inside a block don't stop anything.** The first design put
  "switch models here" markers inside one long prompt. A session handed the
  whole instruction set has no reason to honour a line telling it to wait —
  it can see what comes next, so it does it. Physical separation into
  one-block-per-segment is the only version that holds, and it costs you a
  paste per segment.
- **Anthropic's own guidance broke a flagship feature.** The published model
  guidance says explicitly that telling a session to verify its own work
  causes over-verification and buys nothing. The skill's headline standing
  rule appended exactly that shape: `/code-review` **then** `/verify`, where
  the second step was the same session re-checking itself. Fresh-context
  verification is the documented exception that still pays, so the pair
  collapsed into one reviewer whose mandate covers both halves, and
  re-checking language was banned from task bodies outright.
- **Conciseness was fighting a documented practice.** The pruning test —
  "would the task go wrong without this?" — was killing the sentence
  explaining *why* the work matters, alongside the background it was meant to
  cut. But intent isn't background: a model given the reason behind a request
  connects it to the right context instead of inferring it. That one sentence
  is now the single line exempt from the test.
- **Not every task needs a skill.** Forcing one onto straightforward work
  in a well-patterned codebase makes the output worse. "None needed" is
  always an option.

## License

MIT
