# Routing

## Where capabilities come from

Read them live every run, never from memory:

- **Skills**: the session's skill listing, names used exactly as listed (`plugin:skill`, `path:skill` for directory-scoped ones). With a long listing or a SearchSkills tool present, search by the ticket's keywords instead of scanning.
- **Subagents**: the Agent tool's list of agent types.
- **MCP tools**: loaded `mcp__*` tools, plus deferred ones found with ToolSearch.

| State | What to do |
|---|---|
| Needs auth | Add a flag to the page |
| Disconnected | Use the fallback, or name the gap |
| Needs setup | State the exact command to run first |
| Missing, and a step needed it | Use the fallback and name the substitution |

A skill that pins its own model or effort runs on that pin, so tag its ticket to match. A skill that forks into its own subagent returns only its result, so don't wrap it in another. When nothing installed fits a ticket a skill would make repeatable and SuggestSkills is present, make one suggestion for the whole plan.

## Shortlist

Narrow before ranking: first by **stack and platform**, the highest-leverage filter, then by **ticket shape** (build, review, plan, verify). Rank what survives and report the funnel ("14 matched; these 3 ranked highest"), never three of twenty as three of three. Sweep four angles: a domain skill, a discipline skill, a taste or direction skill, and a subagent doing the same job. Note why each runner-up lost: wrong layer, too general, overlapping, unavailable.

When a plugin-scoped and a generic skill both match, prefer a project-scoped skill from the repository (among directory-scoped names, the one whose directory holds the ticket's files), then a more specific skill whose stack matches exactly, then the generic one, and say which rule decided.

- Match on description, not name; specific beats general.
- Process comes before implementation.
- Verification-shaped work goes to a subagent over a generic skill.
- When nothing fits, attach nothing and say so.
- Communication and publishing tickets go last.

A pick is **uncontested** when one candidate has no serious runner-up, **contested** when two or more genuinely compete, **none needed** when nothing fits or the work is more direct without one.

## Routing history

`~/.claude/flightplan/history.md`, created on first write. If it's absent but `~/.claude/rebuild-prompt/history.md` exists, read that and write new rows to the new path.

```text
| date | task shape | chosen | passed over |
|---|---|---|---|
| 2026-08-11 | design refinement, canvas tool | /impeccable | /high-end-visual-design, /transitions-dev |
```

Read it once per run, before ranking a contested ticket. A matching past pick is flagged ("you chose this for a similar shape on <date>") and ranked up one place; still show the full shortlist and still ask, and the stack filter still wins. Write a row only after the user picks: task shape and capability names only, never client names, URLs, credentials or prompt text.
