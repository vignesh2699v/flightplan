# flightplan

[![skills.sh](https://skills.sh/b/vignesh2699v/flightplan)](https://skills.sh/vignesh2699v/flightplan)

A [Claude Code](https://claude.com/claude-code) skill that plans a piece of
work before it starts, then hands it over one checkable ticket at a time. Each
ticket comes with the right installed skill, the right model and effort, and a
prompt written for the model that will run it. Progress lives on a plan page
anyone can follow.

It never does the work itself. You approve the plan once, paste each ticket
into the same conversation, and the session that runs it records the result
on the page and serves the next one.

![A flightplan plan page: where the plan stands, what happens now, and every step with what it is for and what came out of it](docs/images/plan-page.png)

## Install

```bash
npx skills add vignesh2699v/flightplan -a claude-code
```

Add `-g` to install it for every project instead of just this one, then start
a new Claude Code session. `/flightplan` is ready.

To install by hand instead:

```bash
git clone https://github.com/vignesh2699v/flightplan.git
cp -r flightplan/skills/flightplan ~/.claude/skills/
```

## Use it

Run it on whatever you're about to start:

```
/flightplan redo the onboarding flow, it's losing people at signup
```

1. **It reads the project first:** memory, git history, the README,
   CLAUDE.md and the code. It infers what it can instead of asking.
2. **It tests the premise** with at most four questions, only about what
   reading couldn't settle. Often none.
3. **It files a plan page** and gives you the link: what this is, what done
   looks like, and every ticket in order with its tool and model. Contested
   choices come to you as one round of multiple-choice questions.
4. **It hands over one ticket at a time.** Copy the prompt from the page and
   paste it into the same conversation. When the ticket is done, that session
   records the outcome on the page and serves the next ticket.

Come back tomorrow and run `/flightplan` again: it finds the plan and picks up
where it stopped.

**Small asks skip all of it.** One checkable change gets one routed line back,
with no page and no questions:

```
/flightplan add a loading spinner to the Pay now button while payment is in flight
```

## What it does differently

- **Prompts written for the model that runs them.** Haiku gets exact files
  and a before-and-after example. Sonnet gets its scope stated outright,
  because it follows instructions literally. Opus gets the goal and the
  constraints and chooses the method. Fable gets the full reason and the
  boundaries, never a step-by-step script, which Anthropic's guidance says
  makes its work worse.
- **Model and effort per ticket, without wasting your cache.** Each ticket
  names the smallest model that fits. It stays on your current model when
  that's enough, because switching model mid-session makes the next turn
  re-read the whole conversation at full price. Cheaper, self-contained work
  goes to a helper agent on a smaller model instead.
- **The right capability per ticket.** It routes against the skills,
  subagents and MCP tools you actually have installed, tells you how many it
  considered, and asks you only about genuinely contested picks. It
  remembers what you chose for similar work.
- **A page anyone can follow.** Every step says what it's for and what came
  out of it in plain words. Status is a word as well as a colour, and the
  page works in light and dark mode and on a phone.

## What it writes, and where

| Path | What |
|---|---|
| `~/.claude/flightplan/jobs/<plan>.html` | The plan page, one file per plan |
| `~/.claude/flightplan/history.md` | Which capability you picked for which kind of task: task shape only, never your prompts |

The plan page is published to your own claude.ai account with Claude Code's
Artifact tool, and stays private until you share it. It holds every ticket's
prompt word for word, so share it with that in mind. Nothing else leaves your
machine. Where the Artifact tool isn't available, the local HTML file is the
page and each prompt also appears in chat.

## Compatibility

Built for Claude Code. It uses the Skill, Agent, AskUserQuestion and Artifact
tools when they're present and falls back to plain text and a local page when
they're not. No other skill is required. If
[`grilling`](https://github.com/mattpocock/skills) is installed, flightplan
uses it for the premise check:

```bash
npx skills add mattpocock/skills --skill grilling -a claude-code
```

## Development

```bash
python3 scripts/check-skill.py        # frontmatter, size, hidden characters, file pointers, template anchors
python3 scripts/lint-duplication.py   # each rule stated in exactly one place
```

Both run before every release. Evaluations live in [`eval/`](eval/); the latest
compares this release with the one before it on the same fixture project.

## More

- [Design notes](docs/design-notes.md): the durable decisions, and why
- [CHANGELOG.md](CHANGELOG.md): what changed release to release
- [v2 design spec](docs/flightplan-spec.html): the design that v3 builds on

## License

MIT. See [LICENSE](LICENSE).
