# rebuild-prompt

A [Claude Code](https://claude.com/claude-code) skill that turns a rough,
half-formed prompt into a polished, ready-to-paste prompt — with the right
skills, agents, models, and effort levels already routed to each task.

It does **not** run the prompt. It hands you one you paste back into this
same conversation yourself — why, and the rare exception, in § Design notes.

## Example

**In:**

```
audit this API's error handling, then redesign the client-facing error messages
```

**Out:**

**Model plan** — 2 sessions.

| Segment | Model | Effort |
|---|---|---|
| 1 — audit current error handling | `claude-sonnet-5` | `medium` |
| 2 — redesign error messages | `claude-opus-5` | `high` |

*(Segment 2 is provisional until Task 1's results come back.)*

```
As you reach each task below, invoke the skill named in it via the Skill tool before doing that task's work. The /names are instructions to you, not decorative text — load each one yourself; I have not tagged them.

I want the API's error handling audited and its client-facing messages redesigned, so support stops fielding "something went wrong" tickets that a clearer message would have resolved on its own.

Deliver what is asked at the scope intended; if a better approach exists, say so in a sentence and continue with the task as asked. Delegate to a subagent only for genuinely independent, sizeable tracks — never to double-check your own work — and keep spawn counts low. Local reversible edits proceed; anything destructive, outward-facing, or hard to undo asks first.

## Task 1 — Audit current error handling   [model: claude-sonnet-5 | effort: medium]
Dispatch the Code Reviewer agent.
Trace every error path from the API layer to what the client actually displays.
Report each error path before tracing it and what you found immediately after, then return the full list of error codes, trigger conditions, and current user-facing messages. "Audited" with nothing attached is a failed task. Surface every path checked verbatim, including any that don't map cleanly to a code.

Report back with: the full list of error codes, trigger conditions, and current messages.
Then re-run /rebuild-prompt with those results to get the next segment.
```

**Remaining segments (provisional):** Task 2 — redesign the error messages against the audit findings, routed to a UX-copy or design skill, `claude-opus-5`.

...plus a table showing which capabilities were considered and why each was
picked or passed over.

That's the **Full** tier — this job has a finding boundary between the audit
and the redesign, so it earns the full treatment. A smaller ask doesn't:

**In:** `fix the off-by-one in the pagination loop, file's in the ticket`

**Out:**

```
Use /debugging, `claude-sonnet-5` at `medium`. Fix the off-by-one in the pagination loop referenced in the ticket, and confirm the last page no longer drops or repeats a row. Done = paginated list matches the total row count exactly, first and last page verified manually.
When you've run this, tell me pass or fail — I'll flag any gap and fix the prompt if one exists.
```
**Why:** `/debugging` — no real runner-up for a one-file logic fix.

One task, one line, no table, no model-plan header — the **Single-shot**
tier. Job size drives output size; see § Design notes.

## The problem

You have dozens of skills installed. You type "make my dashboard less
generic and check the performance" and get a generic response, because
nothing routed that to the dedicated data-viz skill, the de-slop skill, and
a performance-benchmarking agent.

The capability was installed. It just never got picked.

## What it does

Given a rough prompt, `rebuild-prompt`:

1. **Grills the premise first** — what you're actually trying to achieve, not
   just what you asked for. Skipped for one trivial, obvious task.
2. **Decomposes** it into ordered tasks with dependencies, and classifies
   each one as uncontested (one obvious capability) or contested (a real
   choice between 2+).
3. **Shortlists 2–3 real candidates for every contested task** — ranked,
   each with *why it ranked there*, including why the runners-up lost. An
   uncontested task's pick is stated in the output instead of asked about —
   this applies task-by-task, not by how many tasks the job has.
4. **Lets you choose** which capability runs each contested task.
5. **Returns a finished prompt** — one fenced block per segment, each task
   tagged with a model and effort level, success criteria written in, and any
   unresolved scope marked inline. If a task needs a different model than the
   one before it, the segment ends there and tells you exactly what to switch
   to before pasting the next one.

The shortlist step is the point. Routing decisions made silently are
routing decisions you can't overrule.

**No other skill is a hard dependency** — see
[Requirements](#requirements) for how each step degrades when one's missing.

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

You'll get a shortlist of candidate capabilities for each contested task,
pick one for each, then receive the finished prompt.

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
  to paste the segment into.
- **An uncontested pick never blocks you, at any job size.** Whether the
  prompt has one task or five, a capability with no real runner-up is stated
  in the output, not asked about. Only a genuinely contested task pauses for
  a question.
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
- **Output size tracks job size.** A one-task fix returns one fenced line —
  no model-plan table, no "why these skills" grid. A 2–3 task job gets a
  five-line scannable header and one short block. Only a job with a real
  segment boundary, or four-plus tasks, gets the full treatment.
- **Effort defaults to `medium`, not the top of the ladder.** It escalates
  only where step 0's own findings say the stakes justify it — stated in
  the header's cost band, not silently applied.
- **A running job continues instead of resetting.** Ask again mid-job and it
  carries the picks, model plan, and constraints already settled, decomposing
  only what's new — and says on-screen exactly what it carried forward.
- **Every delivery closes with a checklist, not a paragraph.** One line per
  success criterion, meant to be answered pass/fail after you've run it.

Both standing rules name specific skills (`/code-review` and a
commentable-preview skill). Each is applied **only if installed**, with a
documented fallback otherwise — see Requirements below.

## Requirements

- Claude Code (any recent version — nested `.claude/skills/` discovery).
- No runtime dependencies. No `npm install`, no `pip install`.
- Routes against whatever skills, agents, and MCP tools you already have.
  It never invents a capability name — with nothing installed, it still
  produces a well-structured prompt, just with fewer skills attached.
- **No other skill is a hard dependency**, including `grilling` — that one
  comes from [mattpocock/skills](https://github.com/mattpocock/skills)
  (`npx -y skills add mattpocock/skills --skill grilling --agent claude-code`),
  but you don't need it: without it the pipeline grills inline instead.
  What the prompt *routes to* thins out as you install less, down to a
  prompt with no `/skill` lines at all — structure, model and effort tags,
  constraints and success criteria still intact. What the pipeline *does*
  never stops: missing `grilling` means the premise gets grilled inline
  instead; an empty candidate field means the shortlist step skips itself
  rather than asking you to pick from one option. Every substitution and
  every skipped step is named in the Flags section, because a fallback you
  weren't told about is indistinguishable from the feature working.

## Design notes

The durable decisions behind how this skill works. For what changed release
to release, see [CHANGELOG.md](CHANGELOG.md).

- **It grills you, but it doesn't interview you.** An interview asks *what
  you want built*; grilling asks *whether you're pointed at the right
  problem*. The answer to the second question changes how the work
  decomposes, which changes what gets routed — so it has to run before the
  shortlist, not after. Requirements ambiguity is handled differently: a
  sensible default plus an inline `[?]` in the delivered prompt, never a
  question round.
- **It never collapses the task→skill mapping.** A multi-task prompt with
  one skill list at the top loses the routing, which is the whole value.
- **No context preamble by default.** The prompt gets pasted back into this
  same conversation by default — a fresh session only when the job is
  genuinely unrelated, or this one is spent — so it already holds the
  project facts, and
  context copied out of memory files is a *snapshot*, so restating it as
  present-tense fact is a correctness risk, not just verbosity. A context
  line survives only if the task would break or go wrong without it, and
  anything sourced from memory is marked "as of `<date>`, verify" rather
  than asserted.
- **Model IDs are a snapshot, not a fact.** The skill's own model/effort
  guidance is a fact that lives outside it — Anthropic ships new models
  faster than this repo gets updated. So the guidance is one dated line,
  explicitly flagged for re-verification, not a table asserted as current.
  Same discipline the skill demands of every prompt it writes, applied to
  itself.
- **Intent isn't background.** The pruning test — "would the task go wrong
  without this?" — would strip the sentence explaining *why* the work
  matters along with everything else that doesn't change the mechanics. But
  a model given the reason behind a request connects it to the right context
  instead of inferring one; that's why one sentence of intent is exempt from
  the test, delivered once, up front.
- **Pasted prompts can't be tagged by hand — so they tag themselves.**
  Pasting text doesn't fire the editor's slash-command autocomplete, and
  only one slash command can ever lead a message, so a six-task prompt with
  six skills is impossible to UI-tag *by design*. The mechanism that works
  is the Skill tool: the model reads "Use /impeccable" as an instruction and
  loads the skill itself. Every rebuilt prompt therefore opens with a line
  saying exactly that.
- **Shortlists report their denominator.** A session can hold up to 500
  skills, and plugin packs install dozens of near-duplicates. Candidates get
  narrowed by stack/platform *before* ranking, and the output states the
  funnel ("14 matched; these 3 ranked highest"). Presenting 3-of-20 as though
  it were 3-of-3 would recreate the exact invisible-filtering problem the
  shortlist step exists to prevent.
- **A dispatched agent runs out of sight.** What comes back is a summary you
  can't audit — and a summary is exactly where a check that never happened
  becomes "verified". So every agent task carries a reporting contract:
  report at checkpoints rather than only at the end, return the specific
  artifact for that check shape, and surface findings verbatim including
  failures. Independent tasks get marked parallelizable — but never ones
  touching the same files, where concurrent edits conflict.
- **Self-verification doesn't verify.** Telling a session to double-check
  its own output causes over-verification without catching more — a model
  re-reading its own reasoning tends to confirm it, not challenge it.
  Fresh-context review is the exception that still pays, so code-writing
  tasks get exactly one reviewer, in a separate context, and re-checking
  language is banned from the task body itself.
- **Routing history is a signal, not a preference lock.** The shortlist step
  asks you the same judgement call repeatedly for contested tasks. Picks are
  logged per task shape in `~/.claude/rebuild-prompt/history.md` — outside
  any skill's install directory, so a reinstall or update never touches it —
  and a matching past pick gets flagged and ranked up one position. It never
  auto-applies, never hides a runner-up, and always loses to the stack
  filter. The log stores task *shape* and capability names only — never your
  prompt text.
- **Point, don't paste.** If a fact lives in a file the executing session can
  open — a playbook, a README, a config, the code itself — the prompt names
  the path instead of copying the contents in. Copying a fact forks it: the
  copy in the prompt ages while the original moves on, and a stale copy
  asserted as current is worse than a pointer.
- **The prompt body is never hard-wrapped.** A hard line break is a real
  newline, and a paste box only reflows text that has none — so every
  paragraph in the delivered prompt is one unbroken line, breaking only
  between paragraphs and tasks.
- **A long prompt goes stale before it's finished.** Later tasks are written
  before the earlier ones run, so they encode assumptions the work may
  already have disproved. Pausing mid-prompt doesn't fix this — the stale
  instructions are still sitting there waiting to be pasted. So a boundary
  at a finding closes by asking for results and sending you back to the
  skill, so the next segment gets planned against what actually happened
  rather than guessed ahead of it.
- **Model choice and segment boundaries are the same decision.** A per-task
  model tag is only enforceable where a boundary exists to keep its promise.
  Subagents take their own model and effort, so the tag binds there; work
  you run directly executes on whatever model the session already has, and
  one message runs on one model. That makes "route this to Sonnet" and "cut
  the prompt here" the same instruction.
- **Stop markers inside a block don't stop anything.** A session handed the
  whole instruction set has no reason to honour a line telling it to wait —
  it can see what comes next, so it does it. Physical separation into
  one-block-per-segment is the version that holds, and it costs you a paste
  per segment.
- **A boundary is also where carried state is most exposed.** Everything a
  later segment depends on — the model plan, the picks already made — lives
  in this session's own text, not in any file. A generic auto-compact has no
  way to know that text matters more than the rest of the transcript, so a
  boundary is exactly where an uncontrolled compaction is most likely to
  drop it. Naming what to keep, at the moment it's most at risk, is cheaper
  than losing it.
- **Not every task needs a skill.** Forcing one onto straightforward work
  in a well-patterned codebase makes the output worse. "None needed" is
  always an option.
- **A prompt built to be read isn't built to be pasted.** The delivered text
  is written for the model that will execute it, not for a human editorial
  pass — but the eval's own confound and direct feedback agreed on the same
  fix from two directions: a big job is genuinely hard to glance at before
  pasting. Output size now tracks job size instead of defaulting to the full
  template regardless of how small the ask was.
- **The default effort should track what's actually at stake.** Every task
  defaulting to the top of the ladder prices a typo fix the same as a
  payment-path rewrite. Grilling already asks which assumption is costliest
  to get wrong — that answer was being thrown away instead of driving the
  one dial that controls both cost and latency.
- **A job in progress is state, not a fresh question.** Resetting on every
  turn would force re-answering ballot questions already settled a message
  ago — the friction the routing-history log exists to reduce. Carrying
  forward what's decided and re-deriving only the task list keeps a session
  from drifting without re-litigating picks that didn't change.
- **A closing line only works if it asks for a verdict.** "Let me know how
  it goes" gets prose back that has to be re-read in full. A pass/fail line
  per criterion gets a verdict back — which is also the only way to know
  whether the delivered prompt produced what was actually asked for.

## Development

Three files describe one system — SKILL.md holds the imperative steps,
`reference/routing-guide.md` holds the mechanics and exact strings, README.md
holds the rationale. A rule written into two of them drifts, and this one has
drifted three times: the v1.7 audit caught it, then v1.11's review caught it
twice more, the second time inside the commit that claimed to have fixed it.

Discipline didn't hold, so a check does:

```bash
python3 scripts/lint-duplication.py
```

It fails on any run of 8 consecutive words appearing in two places. Code
blocks are exempt (the worked example above is meant to mirror the template),
and so is any line that names another file or a `§` section — pointing at a
rule is the pattern that fixes this, not the bug. Genuine repeats go in
`scripts/duplication-allowlist.txt` with a reason. Run it before every
release; `--shingle N` tightens or loosens the window, `--json` for tooling.

## License

MIT
