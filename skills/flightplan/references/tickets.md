# Writing a ticket

## Template

```text
<Self-invocation line, only when the ticket names a skill.>

<One sentence of intent: what this ticket is for, and why it matters.>

<The work, written for the model that runs it (§ Write for the model).>

<One line per hard constraint, destructive-action guard or credential boundary that applies, each with its reason.>

<The model's standing line.> Local reversible edits proceed; anything destructive, outward-facing or hard to undo asks first.

Done = <criterion, reportable as pass or fail>.
When the done-criterion is met or clearly missed, invoke /flightplan with `record T-NN` so the plan page records the result.
```

Write each paragraph as one unbroken line; a paste box only reflows text without hard breaks. No context preamble: the page holds the context and the conversation already has it. Point at files rather than pasting their contents, which go stale. Describe the behaviour wanted and keep prohibitions for real constraints. Number sub-steps only where order matters, such as a review after the change.

## Self-invocation

Pasted text can't trigger a slash command, so a ticket whose main work uses a skill opens with this line, verbatim. A review sub-step names its own skill where it runs instead.

```text
Load /<skill> with the Skill tool before you start; the name is an instruction to you, not decoration.
```

## Write for the model

Shape the work paragraph for the model in the ticket's tag, and use its standing line.

**haiku** is fast and literal, best on narrow work with nothing to infer. It runs as a subagent without this conversation, so give it everything: the exact files, the exact change, one before-and-after example, and the command whose output proves it worked. One task, no judgement calls.
Standing line: `Change only what is listed. If something doesn't match these instructions, stop and report it instead of improvising.`

**sonnet** takes instructions literally, more so at lower effort: it won't extend a rule from one item to the rest or infer a request you didn't make. State the scope outright ("every file under src/styles, not just the first"), put intent and constraints up front, and for an open design choice give the concrete spec or ask for options before it builds. For a review, ask for every issue with a confidence and a severity; an "only important issues" filter makes it drop real findings.
Standing line: `Deliver exactly what is asked, at the scope stated here. If you see a better approach, mention it in one sentence and still do what was asked.`

**opus** plans well and checks its own work unasked; left alone it widens scope and delegates. Give it the goal, the reason, the constraints and the done-criterion, and leave the method to it. Asking it to double-check, or adding a verifier, causes over-verification. Reviews follow the sonnet rule. For visual work, name the specific styles to avoid, since "avoid a generic look" just swaps one default for another.
Standing line: `Deliver what is asked at the scope intended, and finish the whole task; if a better approach exists, say so in a sentence and carry on as asked. Use subagents only for independent, sizeable tracks, never to check your own work.`

**fable** is the most capable and runs long, and step-by-step instructions written for earlier models make its work worse. Give the reason in full (who it's for, what they need), the outcome, the boundaries and the done-criterion, then let it plan. It can take adjacent actions nobody asked for, so name what it must not touch; let it delegate independent subtasks.
Standing line: `When you have enough information to act, act, and add nothing beyond what this needs. Report only progress you can point to evidence for. Delegate independent subtasks and keep working while they run.`

For every model: no emphasis words in capitals, no "think step by step", no request to double-check. Current models reason and verify by default, and emphasis makes them over-apply a rule.

## Agent tickets

A ticket that dispatches an agent names it and its model ("Run this in a subagent, Agent tool, model: haiku") and carries this reporting contract:

1. Report at checkpoints, not only at the end.
2. Return artifacts, not adjectives: "verified" with nothing attached is a failed ticket.
3. Surface findings verbatim, failures included.

| Check | Artifact to return |
|---|---|
| Visual or layout | Fresh-load screenshots at every breakpoint |
| Performance | Before and after numbers, and how they were measured |
| Correctness or build | The command output itself |
| Accessibility | The assistive-technology result |
| Security | `file:line` and a concrete reproduction |
| Research | The sources read, cited |

## Review

The review is the ticket's last numbered sub-step: `/code-review` at the ticket's effort when installed, else a code-reviewer subagent, else an instruction to review the diff in a fresh subagent. The reviewer reads the diff and runs the change end to end. No executable change, no review.

## Plan deliverables

A ticket whose output is a plan or spec (Plan Mode, `/superpowers:writing-plans`, "make a plan for X") publishes it with the Artifact tool at its own URL, separate from the plan page, using an installed skill or tool for commentable documents when there is one. Otherwise each block-level section gets `class="commentable"` and a unique `data-id`, plus a Revise action that collects comments and redeploys to the same URL.
