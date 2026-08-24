# flightplan

A [Claude Code](https://claude.com/claude-code) skill that reads a project,
files one plan holding its context, its tickets and a live tracker, then
hands over one ticket at a time with the right skill, agent, model and
effort attached to each.

It does **not** run the work. It hands you prompts you paste back into the
same conversation, one at a time — and each ticket updates the plan when
it's done, so the tracker fills itself in.

## The problem

You have hundreds of skills, agents and MCP tools installed. Picking the
right one per task is real work, and you mostly don't do it — so most tasks
run on nothing, or on whatever you happened to remember.

Then the work itself scatters. Plans end up in `.md` files across a dozen
folders, progress lives in your head, and halfway through a session you're
pushing changes without a clear picture of what's done, what's left, or
whether the plan still matches what you found. There's no process — just
momentum.

flightplan gives the session a spine. One page per project: what this is,
what done looks like, the tickets in order, and a tracker that updates
itself as each one finishes. You approve the plan once, then work one ticket
at a time and glance at the tracker.

## Install

```bash
git clone https://github.com/vignesh2699v/claude-flightplan.git
```

```bash
cp -r claude-flightplan/skills/flightplan ~/.claude/skills/
```

Verify — you should see `SKILL.md` and `reference/`:

```bash
ls ~/.claude/skills/flightplan
```

Start a new session and `/flightplan` is available.

**Requirements:** Claude Code, and nothing else. No `npm install`, no
`pip install`, no runtime dependencies. It routes against whatever skills,
agents and MCP tools you already have, and never invents a capability
name — with nothing installed it still produces a well-structured plan, just
with fewer skills attached.

**No other skill is a hard dependency**, including `grilling` — that one is
from [mattpocock/skills](https://github.com/mattpocock/skills):

```bash
npx -y skills add mattpocock/skills --skill grilling --agent claude-code
```

Without it, the premise gets grilled inline instead. Every substitution and
every skipped step is named in the output, because a fallback you weren't
told about is indistinguishable from the feature working.

## Usage

Run it on whatever you're about to start:

```
/flightplan redo the onboarding flow — it's losing people at signup
```

**What happens.** It reads the project first — memory, git log, README,
existing files — and infers what it can rather than asking. Then it grills
the premise: at most four questions, only on what reading couldn't settle.
Often zero.

Then it files a plan page and gives you the link. You approve it once. That
page holds:

- **Context** — what this is, who it's for, what exists now, what success
  looks like, what's out of scope, each line naming where it came from
- **Tickets** — one verifiable outcome each, in dependency order, with the
  capability chosen for each and what it beat
- **Tracker** — status, one line of outcome, evidence link, per ticket

After that you get one ticket at a time. Paste it, run it, and that session
updates the tracker itself — you never carry results back by hand. When you
return, next hour or next week, run `/flightplan` again on the same project:
it finds the page, reads the tracker, and picks up at the first unfinished
ticket.

**Small asks skip all of it.** One thing to do gets one line back with the
right skill attached — no plan page, no context phase. If a plan is already
open, it becomes a ticket on that plan instead, so the tracker stays a true
record of the session.

## More

- [Design notes](docs/design-notes.md) — the durable decisions, and why
- [Spec](docs/flightplan-spec.html) — the v2 design, settled by grilling
- [CHANGELOG.md](CHANGELOG.md) — what changed release to release

## License

MIT — see [LICENSE](LICENSE).
