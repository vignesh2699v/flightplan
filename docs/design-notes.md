# Design notes

The durable decisions behind how flightplan works, and why. The skill files
point here rather than restating any of it. For what changed release to
release, see [CHANGELOG.md](../CHANGELOG.md).

- **It grills you, but it doesn't interview you.** An interview asks *what
  you want built*; grilling asks *whether you're pointed at the right
  problem*. The answer to the second question changes how the work
  decomposes, which changes what gets routed — so it has to run before the
  shortlist, not after. And it runs *after* reading the project, so it can
  push against what's actually there rather than against nothing — four
  questions at most, only on what reading couldn't settle, often zero.
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
  loads the skill itself. Any ticket naming a skill therefore opens with a
  line saying exactly that.
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
  failures.
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
- **A prompt written early goes stale before you reach it.** A later ticket
  drafted up front encodes assumptions the earlier work may have already
  disproved, and pausing doesn't help — the stale instructions are still
  sitting there waiting to be pasted. So a ticket's full prompt is written
  only when it goes live, against what actually happened, and the plan page
  carries titles and done-criteria until then.
- **One ticket per paste makes the model tag enforceable.** A tag on
  directly-run work only binds where the prompt physically stops, and a
  session handed a whole instruction set has no reason to honour a line
  telling it to wait — it can see what comes next, so it does it. Serving
  one ticket at a time stops every time, which is why v2 could delete the
  segment machinery that used to arrange those stops by hand.
- **The plan page is state, not a record.** It holds the context, the picks
  and the constraints, and the pipeline reads it back when you return. That
  is what makes a compaction, a new session or a reboot survivable —
  compaction summarises and can't know which sentence mattered, but a page
  loses nothing. Every finished ticket says a handoff is safe there.
- **The ticket updates the plan, so you never carry the message.** A tracker
  that needed you to paste each result back would be a worse chore than the
  one it replaced. The running session writes its own status, outcome and
  evidence link — and if it went off-plan it says so and marks what follows
  stale, without rewriting work you approved.
- **Not every task needs a skill.** Forcing one onto straightforward work
  in a well-patterned codebase makes the output worse. "None needed" is
  always an option.
- **A prompt built to be read isn't built to be pasted.** The delivered text
  is written for the model that will execute it, not for a human editorial
  pass — but the eval's own confound and direct feedback agreed on the same
  fix from two directions: a big job is genuinely hard to glance at before
  pasting. Output size now tracks job size instead of defaulting to the full
  template regardless of how small the ask was.
- **The plan and the prompt stop sharing a surface.** Shrinking the text
  only narrowed that conflict; a big job still has to say enough to execute.
  A real project publishes a page instead: the plan on top, written to be
  read, and each ticket's prompt in a copy block, written to be run. You
  review the plan once and copy the prompts without reading them — which is
  what finally makes prompt length stop costing you anything. A single
  outcome still gets no page: that would be scaffolding around a single
  paste. That distinction came from measurement, not argument — the trigger
  had already been reasoned into two different positions before a fixture
  run settled it.
- **One page per project, not one per delivery.** It redeploys to the same
  URL every time the plan moves, so the next ticket arrives on the page you
  already have open and the last one flips to done. Keyed by an undated
  slug, so a project picked up next week resolves to the same page instead
  of quietly starting a second one. A single-outcome ask gets no page at
  all — there is no second delivery for one to survive to.
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

