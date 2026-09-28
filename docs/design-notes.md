# Design notes

The durable decisions behind how flightplan works, and why. The skill files
state rules with a short reason; the longer argument for each lives here. For
what changed release to release, see [CHANGELOG.md](../CHANGELOG.md).

## Planning

- **It grills you, but it doesn't interview you.** An interview asks *what
  you want built*; grilling asks *whether you're pointed at the right
  problem*. The answer to the second question changes how the work
  decomposes, which changes what gets routed — so it has to run before the
  shortlist, not after. And it runs *after* reading the project, so it can
  push against what's actually there rather than against nothing — four
  questions at most, only on what reading couldn't settle, often zero.
- **It never collapses the task→skill mapping.** A multi-task prompt with
  one skill list at the top loses the routing, which is the whole value.
- **A prompt written early goes stale before you reach it.** A later ticket
  drafted up front encodes assumptions the earlier work may have already
  disproved, and pausing doesn't help — the stale instructions are still
  sitting there waiting to be pasted. So a ticket's full prompt is written
  only when it goes live, against what actually happened, and the plan page
  carries titles and done-criteria until then.
- **A job in progress is state, not a fresh question.** Resetting on every
  turn would force re-answering ballot questions already settled a message
  ago — the friction the routing-history log exists to reduce. Carrying
  forward what's decided and re-deriving only the task list keeps a session
  from drifting without re-litigating picks that didn't change.
- **Not every task needs a skill.** Forcing one onto straightforward work
  in a well-patterned codebase makes the output worse. "None needed" is
  always an option.

## Routing

- **Shortlists report their denominator.** A session can hold hundreds of
  skills, and plugin packs install dozens of near-duplicates. Candidates get
  narrowed by stack/platform *before* ranking, and the output states the
  funnel ("14 matched; these 3 ranked highest"). Presenting 3-of-20 as though
  it were 3-of-3 would recreate the exact invisible-filtering problem the
  shortlist step exists to prevent.
- **Routing history is a signal, not a preference lock.** The shortlist step
  asks you the same judgement call repeatedly for contested tasks. Picks are
  logged per task shape in `~/.claude/flightplan/history.md` — outside any
  skill's install directory, so a reinstall or update never touches it — and
  a matching past pick gets flagged and ranked up one position. It never
  auto-applies, never hides a runner-up, and always loses to the stack
  filter. The log stores task *shape* and capability names only — never your
  prompt text. Rows written by the old `rebuild-prompt` path are still read.
- **The skill system changed, so discovery did too.** Skill names now carry
  their scope (`plugin:skill`, `path:skill`), a skill can pin its own model
  and effort, and some skills fork into their own subagent. Routing uses the
  exact listed name, tags a ticket to match a skill's pinned model, and never
  wraps a forking skill in a second subagent. With a long listing, keyword
  search beats reading every description.

## Models

- **Each prompt is written for the model that runs it.** The same ticket
  reads differently to each model, and Anthropic's own guidance says so:
  Sonnet follows instructions literally and won't generalise a rule from one
  item to the next, so its tickets state scope outright; Opus plans and
  verifies on its own and over-verifies when told to, so its tickets give
  the goal and leave the method; Fable does measurably worse with the
  step-by-step scaffolding written for earlier models, so its tickets carry
  the reason and the boundaries instead; Haiku does best with nothing left
  to infer, so its tickets name the exact files and show one example.
- **Models are named by alias, read from the session.** A model name is a
  capability that changes over time, and a dated table in a skill is stale
  the day a model ships. `opus` resolves to the current Opus in Claude Code;
  the set a session actually has is in the Agent tool's options. Asking the
  user which models they have — the old default — was friction the session
  could answer itself.
- **A model switch has a price.** Changing model or effort mid-session
  invalidates the prompt cache, so the next turn re-reads the whole
  conversation uncached. On a long session that costs more than a smaller
  model saves on one ticket. So a ticket stays on the session's model
  whenever that model is enough, moves to a stronger model when the work
  demands it, and reaches a smaller one only through a subagent, whose fresh context has no cache
  to lose and whose model binds regardless of the session's.
- **The default effort should track what's actually at stake.** Every task
  defaulting to the top of the ladder prices a typo fix the same as a
  payment-path rewrite. Grilling already asks which assumption is costliest
  to get wrong — that answer drives the one dial that controls both cost and
  latency. Effort support differs by model: Haiku has none, and Opus 5.5
  defaults a level lower than Opus 5 did, so the table carries a per-model
  default rather than one ladder for all.
- **One ticket per paste makes the model tag enforceable.** A tag on
  directly-run work only binds where the prompt physically stops, and a
  session handed a whole instruction set has no reason to honour a line
  telling it to wait — it can see what comes next, so it does it. Serving
  one ticket at a time stops every time, which is where a switch can happen.

## Prompts

- **No context preamble by default.** The prompt gets pasted back into this
  same conversation, so it already holds the project facts, and context
  copied out of memory files is a *snapshot*: restating it as present-tense
  fact is a correctness risk, not just verbosity.
- **Intent isn't background.** A model given the reason behind a request
  connects it to the right context instead of inferring one; that's why one
  sentence of intent opens every ticket, even though a pruning pass would
  otherwise cut it.
- **Point, don't paste.** If a fact lives in a file the executing session can
  open, the prompt names the path instead of copying the contents. Copying a
  fact forks it: the copy in the prompt ages while the original moves on.
- **Pasted prompts can't be tagged by hand — so they tag themselves.**
  Pasting text doesn't fire the slash-command autocomplete, and only one
  slash command can lead a message. The mechanism that works is the Skill
  tool: a ticket naming a skill opens with a line telling the model to load
  it.
- **The prompt body is never hard-wrapped.** A hard line break is a real
  newline, and a paste box only reflows text that has none.
- **Emphasis is not a volume knob.** Current models follow instructions
  closely; capitals and "CRITICAL" make them apply a rule too broadly, and
  "think step by step" or "double-check" duplicate what they already do. The
  prompts say what's wanted at normal volume, with the reason.
- **A closing line only works if it asks for a verdict.** "Let me know how
  it goes" gets prose back that has to be re-read. A pass/fail line on the
  done-criterion gets a verdict — and the only direct signal of whether the
  prompt produced what was asked for.

## Verification

- **A dispatched agent runs out of sight.** What comes back is a summary you
  can't audit — and a summary is exactly where a check that never happened
  becomes "verified". So every agent ticket carries a reporting contract:
  checkpoints, the specific artifact for that kind of check, and findings
  verbatim, failures included.
- **Review is sized to the model and the stakes.** Telling a session to
  double-check its own output causes over-verification without catching
  more. A separate fresh-context reviewer still pays where the executing
  model is smaller or the code is high-stakes, so those tickets get exactly
  one. Opus and Fable check their own work unprompted, and a verifier added
  on top of that mostly buys cost, so their other tickets don't.

## The plan page

- **The plan and the prompt don't share a surface.** A real project publishes
  a page: the plan written to be read, and each ticket's prompt in a copy
  block, written to be run. You review the plan once and copy the prompts
  without reading them — which is what makes prompt length stop costing you
  anything. A single outcome still gets no page: that would be scaffolding
  around a single paste, and a fixture run settled it rather than argument.
- **The page is a template plus a log.** Earlier versions had the model write
  each page's HTML from a description, which cost thousands of output tokens
  per plan, looked different every time, and made every writeback an edit
  to markup the next session had to re-read. Now the look and behaviour ship
  once in `assets/`, and a plan only appends one-line JSON records — a
  ticket, a status change, a result. Appending never needs the old text
  reproduced, so the edit is small and can't be ambiguous; the latest line
  wins, and the older ones are the history for free.
- **Written for someone who has never seen the code.** The people who glance
  at a plan are often not the people running it. Every step says what it's
  for and what came out of it in a plain sentence, status is a word as well
  as a colour, and the page explains its own vocabulary. The details a
  developer wants — tool, model, prompt — sit one click down.
- **The page is state, not a record.** It holds the context, the picks and
  the constraints, and the pipeline reads it back when you return. That is
  what makes a compaction, a new session or a reboot survivable —
  compaction summarises and can't know which sentence mattered, but a page
  loses nothing.
- **One page per plan, keyed to the project.** It redeploys to the same URL
  every time the plan moves, and the page records which repository it
  belongs to, so a plan picked up next week resolves to the same page
  instead of quietly starting a second one.
- **The session that ran a ticket records it, through the skill.** A tracker
  that needed you to paste each result back would be a worse chore than the
  one it replaced. Each ticket ends by invoking `/flightplan record`, so the
  recording procedure lives in one place instead of being copied into every
  prompt, and the same turn serves the next ticket against the result it
  just recorded. If a ticket went off-plan, the tickets after it are marked
  stale without being rewritten: a plan you approved changes only when
  you're asked.
- **No tool is a hard dependency.** Everything the skill routes to can thin
  out to nothing and the output stays well-formed. Tools the skill *runs
  itself* get a fallback: without AskUserQuestion the ballot is a numbered
  list, and without the Artifact tool the local HTML file is the page and
  the prompt also goes in chat. Every substitution is named, because a
  fallback you weren't told about is indistinguishable from the feature
  working.

## Distribution

- **Only the standard frontmatter.** The skill is installed by more than one
  tool and indexed by directories that validate against the Agent Skills
  spec, which rejects unknown keys. Claude Code-only fields would buy a menu
  hint at the cost of failing validation, so the frontmatter sticks to the
  spec and the version lives under `metadata`.
- **Scanner-clean before the first install.** Directory security audits run
  on first sight and rarely re-run. Hidden characters, install commands and
  URLs in skill files are what they flag, so `scripts/check-skill.py` rejects
  all three before a release goes out.
