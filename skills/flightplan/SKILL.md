---
name: flightplan
description: Plans a piece of work before it starts and hands it over one checkable ticket at a time. Reads the project, tests the premise with at most four questions, then files a live plan page anyone can follow; each ticket gets the best installed skill, subagent or MCP tool and a prompt written for the model and effort it should run on. Use when the user runs /flightplan, asks to plan, scope, kick off, break down or sequence work, or wants to resume a plan, even without saying plan. A single small ask gets one routed line instead. Never does the work itself.
license: MIT
allowed-tools: Read(~/.claude/flightplan/**) Edit(~/.claude/flightplan/**)
compatibility: Built for Claude Code. Uses the Skill, Agent, AskUserQuestion and Artifact tools when present, and falls back to plain text and a local HTML page when they are not.
metadata:
  version: "3.0"
---

# Flightplan

Plan the work, then hand it over one ticket at a time. The user approves the plan once; after that each ticket is a prompt they paste back into this conversation, and when it finishes, that session logs the outcome on the plan page. You plan, route and write prompts, and never do a ticket's work yourself: the pause between tickets is where the user checks the result and, when it pays, changes model.

Read the files beside this one only at the step that names them. The small-ask path needs none.

## Pick the path

First check for an open plan: search `~/.claude/flightplan/jobs/` for this project's key, which is its git remote without protocol or `.git` (`github.com/acme/shop`), or its path when there is no remote. A matching file is open unless it has a `"kind":"close"` line.

| Situation | Path |
|---|---|
| `/flightplan record T-NN`, after a ticket ran | § Record |
| `/flightplan` with nothing new to plan | § Resume |
| The ask names no target ("fix the bug") | Ask which one, offering the candidates a quick read turns up, then pick the path |
| Plan open, ask is one checkable outcome | Add it as the plan's next ticket (§ Plan), then § Serve |
| Plan open, ask is bigger | Ask whether to extend that plan or start a separate one |
| No plan open, ask is one checkable outcome | § One-liner, then stop |
| Anything else | § Read, § Grill, § Plan, § Approve, § Serve |

A single checkable outcome never gets a page; the evals showed a routed line beats a filed plan there.

## One-liner

One fenced block, so it copies cleanly, then a line of why:

```text
Use /<skill-or-agent>[ on <model> at <effort> effort]. <Instruction, folding in the requirement and why it matters.> <Hard constraint, only when one applies.> Done = <criterion>. Tell me pass or fail.
```

**Why:** <the pick, and its runner-up if the choice was close.>

Pick the capability from the session's listing by what its description says it does, and drop "Use /…" when nothing fits. Name a model only when the ask needs a stronger one than the session's (§ Models). Nothing is recorded afterwards; a one-liner has no page.

## Read

Establish five context fields: what this is, who it's for, what exists now, what success looks like, what's out of scope. Take them from memory, the git log, README, CLAUDE.md or AGENTS.md, the manifest, the code, and a connected issue tracker when the ask points at an issue, issuing these independent reads together in one turn. Note each field's source, so a wrong inference is caught in seconds. Infer rather than ask: a question reading could have answered is the failure this step exists to prevent.

## Grill

Test the premise against what reading found, with the `grilling` skill if it's installed, otherwise inline. At most four questions, in one round (AskUserQuestion where available, numbered options otherwise), only on gaps reading couldn't close; offer the likely answers reading turned up as options, and spend the questions first on success and scope, which reading rarely settles. When reading covered everything, ask nothing and say so. Never plan work around a guessed target: when the target is unclear, asking is the step. Note which assumption is costliest to get wrong: it decides which ticket, if any, gets more effort.

## Plan

Split the work into tickets, each one checkable outcome, in dependency order; a real project lands at 5 to 15. Anything destructive, outward-facing or irreversible gets its own ticket that says so, since size alone doesn't isolate it. Per ticket, settle:

- **Capability**: at most one skill, subagent or MCP tool, chosen per `references/routing.md`; "none needed" is valid, and a second one needs a stated reason.
- **Model and effort**: § Models.
- **Where it runs**: this session by default, since it holds the context; a subagent when the ticket is self-contained and suits a smaller model, or is verification-shaped.
- **Done =**: reportable as pass or fail.

Create the page from `${CLAUDE_SKILL_DIR}/assets/plan-page.html`, the template in this skill's `assets` folder (`references/plan-page.md` § Create). Give the user its link in a short message: the outcome, the ticket count, how many picks are contested, and any flag they must act on.

## Approve

Put the contested picks to the user in one round of AskUserQuestion, top pick marked "(Recommended)". A call holds four questions, so a fifth contested pick takes a second call; that's the tool's limit, not a judgement. Uncontested picks aren't asked about; the page shows each pick and what it beat. Without AskUserQuestion, list numbered options with the default marked. When nothing is contested, say so and ask for go. Until the user says go, change the page in place.

## Serve

Write the live ticket's prompt now, against what the earlier tickets actually produced; a prompt written ahead encodes assumptions the earlier work may disprove. Follow `references/tickets.md`. Append the ticket's `live` status and prompt to the page (`references/plan-page.md` § Update) and republish.

Then tell the user in two lines at most which ticket is live and where to copy it, plus any switch as `/model <alias>` and `/effort <level>`, each sent on its own before pasting. The prompt stays on the page, not in chat, unless there's no page viewer (`references/plan-page.md` § Without the Artifact tool). Then stop. A `stale` ticket is never served as written; re-plan it with the user first.

## Record

Runs in the session that just did a ticket. Append its status (`done`, or `failed` when the done-criterion wasn't met), one plain sentence on what came out of it, and the evidence's link or path (`references/plan-page.md` § Update). If the work went off-plan, say so there and mark each later ticket `stale` without rewriting it; an approved plan changes only when the user is asked. Tell the user pass or fail, then § Serve the next ticket in the same turn, or after the last one, close the plan with one sentence on what it produced. When the ticket's deliverable needs the user's sign-off before later work builds on it, such as a spec, a design or a plan, ask for that sign-off instead and serve once it's given.

## Resume

Find the plan (`references/plan-page.md` § Find the plan) and say in one line where it stands. In a new session, re-read what the finished tickets touched first, since it may have changed. Then serve the first ticket not done, or re-plan it with the user if it's stale.

## Models

Name models by alias (`haiku`, `sonnet`, `opus`, `fable`) so tags outlive releases, and read what's available from the session, the Agent tool's `model` options and the `/model` aliases, rather than asking.

| Ticket | Smallest model that fits | Effort |
|---|---|---|
| Mechanical and fully specified: rename, move, reformat, bump | `haiku` | none; Haiku has no effort setting |
| Everyday build, fix or test with a clear spec | `sonnet` | `high`, or `medium` when routine |
| Multi-file change, unknown cause, design judgement, review | `opus` | `medium`; `high` on the costliest-assumption ticket |
| Hardest, longest, most ambiguous: architecture, security, money | `fable` if available, else `opus` | `high`; `xhigh` or `max` only when correctness outweighs cost |

Changing model or effort mid-session resets the prompt cache, and the next turn re-reads the whole conversation at full price. So run a ticket on the session's own model whenever it is at least the one the table names (the order is `haiku`, `sonnet`, `opus`, `fable`), switch up only when the ticket needs more, and go smaller only through a subagent, which binds its own model without touching this session. Without a subagent to hand it to, a ticket that suits a smaller model runs on the session's model and is tagged that way. Tag `fable` only when the session shows it's available; otherwise tag `opus` and flag that `fable` would suit it.

This session runs at `${CLAUDE_EFFORT}` effort (unknown if that reads as a placeholder). Effort follows the same cache rule: ask for a change only when a ticket needs more than the session runs at, never to save a little on one ticket; if the session runs well above what the remaining tickets need, suggest one change for the rest of the plan. A pure clarification runs at `low`. Raise effort one rung at a time, only for what the ticket itself costs to get wrong.

## Standing rules

Applied to every ticket, never asked about; a one-liner carries only its own constraint. When a capability a step relies on is missing, use the fallback and name the substitution; never drop a step silently.

- A code-writing ticket on `haiku` or `sonnet`, or touching payments, auth, data migration or security, ends with one fresh-context review (`references/tickets.md` § Review). Other `opus` and `fable` tickets rely on the model's own checking; asking for more only inflates it.
- A ticket that produces a plan or spec publishes it as a commentable page at its own URL (`references/tickets.md` § Plan deliverables).
- A ticket that dispatches an agent carries the reporting contract (`references/tickets.md` § Agent tickets).
- Name only capabilities present in this session, by their exact registered names.
