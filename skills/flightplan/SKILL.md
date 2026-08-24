---
name: flightplan
description: Read a project, test the premise, then file one plan holding its context, its tickets and a live tracker — and hand over one ticket at a time with the best-fit installed skill, subagent or MCP tool attached to each. Use when the user runs /flightplan, or asks to plan, scope, kick off or set up a piece of work. Returns prompts for the user to paste back into this same conversation and run themselves; never executes the work.
---

# Flightplan

Read a project, file a plan, serve one ticket at a time. Deliver the ticket,
then stop — the user pastes it back into this same conversation and runs it.

Rationale for every rule below lives in `docs/design-notes.md`. Templates,
exact strings and page anatomy live in `reference/mechanics.md`. Do not
restate either here — if you're about to explain *why*, it belongs in one of
those two files, not a third copy in this one.

## Pipeline

### 0. Size the ask

| The ask | Path |
|---|---|
| One verifiable outcome, no plan open | One-liner (`mechanics.md` § One-liner), then stop |
| One verifiable outcome, plan already open (`mechanics.md` § The plan page — recover it before deciding) | One new ticket on that plan, then stop |
| Anything larger | Steps 1–6 below |

Never run steps 1–6 on a single-outcome ask. A direct answer beats a filed
plan there, which is measured rather than assumed.

### 1. Read

Establish the five context fields (`mechanics.md` § Context fields) from
memory, git log, README, CLAUDE.md, package manifests and the files
themselves. Record where each one came from.

Infer rather than ask. A question you could have answered by reading is the
failure this step exists to prevent.

If a plan already exists for this project, read it instead of starting
over — see § 5.

### 2. Grill

Run `grilling` on the premise, now that reading has given it something to
push against. If `grilling` isn't installed, grill inline.

Four questions maximum, in one round, on gaps only — never on anything
reading already settled. Zero questions is the correct outcome when reading
covered everything; say so in a line rather than manufacturing one.

Spend questions on "what success looks like" and "what's out of scope"
first: those are the two fields reading rarely settles.

Carry the answer to the costliest-assumption question into step 5 — it
decides which ticket, if any, escalates past the default effort.

### 3. File the plan

Publish one page per project (`mechanics.md` § The plan page): context with
its source trail, the outcome, the approach, and the ticket list.

Split the work into tickets, each **one verifiable outcome** — the smallest
thing that can be reported pass or fail. Order by dependency. A real project
lands at 8–15.

Any destructive, outward-facing or irreversible step gets its own ticket and
says so in its own body. Ticket size alone does not isolate it.

Classify each ticket's capability:

| Class | Meaning |
|---|---|
| Uncontested | One candidate; no runner-up seriously threatens it |
| Contested | 2+ real candidates in genuine competition |
| None needed | Nothing fits, or the work is more direct without one |

At most one capability per ticket. Add a second only where the ticket
genuinely spans two domains, and say why both. "None needed" is always a
valid answer.

### 4. Ballot

One round, at approval, covering every contested ticket — top pick marked
"(Recommended)", max 4 per AskUserQuestion call. More than four contested
tickets take a second call; four is the tool's limit, not a decision that
the fifth doesn't matter.

Uncontested and none-needed tickets are never asked about. Their pick and
nearest runner-up are stated on the page instead.

Before ranking, read `~/.claude/rebuild-prompt/history.md` once, covering
every contested ticket this run. Schema and write rules in `mechanics.md`.

Done when every ticket has a capability — chosen, waived or absent — and the
user has approved the plan.

### 5. Serve one ticket

Write the live ticket's full prompt now, against what the tickets before it
actually produced. Never pre-write a later ticket: it would encode
assumptions the earlier work may disprove.

Mark the ticket `live` on the page. Deliver the prompt and nothing else —
one fenced block, ready to paste.

Resuming a project: read its page and continue from the first ticket marked
`pending`. Re-read the project first, since anything may have changed. Say
in one line what the tracker held and what you re-read. A `stale` ticket is
never served as-is — its instructions were invalidated by a finding, so
re-plan it with the user before it goes live.

### 6. Write back

Every ticket prompt ends with the writeback line (`mechanics.md` §
Writeback). The session that runs the ticket updates the page itself:
status, one line of outcome, a link to the evidence.

When a ticket reports going off-plan, update the record immediately and mark
the tickets after it stale. Do not rewrite them — a plan the user approved
changes only when the user is asked.

Done when the last ticket is `done` and the page says the plan is closed.

## Writing a ticket

- One sentence of intent, up front.
- Name the capability as an instruction, not decoration — `mechanics.md`
  § Self-invocation.
- Tag it `[model: <id> | effort: <level>]` — ladder and defaults in
  `mechanics.md`.
- Hard constraints, destructive-action guards and credential boundaries are
  never dropped for brevity — one line each, in the ticket they apply to.
- One paragraph, one unbroken line. Never hard-wrap a prompt body.
- No context preamble: the page holds the context, and the user is pasting
  into the conversation that already has it.
- Route against the live session listing, exact registered names. Flag auth,
  disconnection and setup preconditions.
- State the behaviour wanted, not the behaviour forbidden.
- A done-criterion is mandatory, phrased so the writeback can report it pass
  or fail.

## Standing rules

Applied every run, never asked about. Use the fallback for any missing
capability — skill, subagent or MCP tool — and flag the substitution. Never
silently drop a pipeline step.

- Code-writing tickets get one fresh-context review appended — fallback
  chain in `mechanics.md`. No self-checking language in the ticket body.
- Plan- or spec-producing tickets render as a commentable HTML artifact at
  their own URL, separate from the plan page.
- Every agent-dispatched ticket carries the reporting contract from
  `mechanics.md` § Agent tickets report as they go.
