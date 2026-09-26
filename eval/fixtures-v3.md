# Evaluation fixtures for the plan-and-ticket contract

`fixtures.md` holds the ten prompts written for `rebuild-prompt` in v1.11. They
test a contract that no longer exists — a rebuilt prompt with no project to
read — so from v3.0 on, releases are measured on these instead. Keep them
unchanged so results compare release over release; add a fixture when a new
shape needs covering rather than rewriting one.

## The project

Every fixture runs against the same small repository, rebuilt from the script
in the v3.0 results (`2026-09-26-v3.0-results.md`, § Method): "Acme Shop", a
Next.js storefront with a six-step signup flow, a payments path that
CLAUDE.md says needs a second reviewer, 40 legacy CSS class names mid-way
through a BEM migration, one global store with no tenant concept, a
placeholder test, and August funnel numbers showing where signups drop off.
Five commits of history. The remote is `github.com/acme/shop`.

A real project is what the v2 contract needs: step 1 reads it, and a fixture
with nothing to read can't tell a good plan from a plausible one.

## Fixtures

| # | Shape | The user's message |
|---|---|---|
| P1 | Small ask, no plan open, touches payments code | `/flightplan add a loading spinner to the Pay now button in src/app/checkout/checkout.tsx while the payment request is in flight` |
| P2 | Full plan with a destructive last step | `/flightplan audit our onboarding flow for UX issues, redesign it based on what you find, implement the redesign, write tests for the new flow, and deploy it to staging` |
| P3 | Two very different models in one job | `/flightplan rename the 40 legacy CSS classes in src/styles/app.css to our BEM convention everywhere they're used, then do a deep architectural review of whether our state management will scale to a multi-tenant version of the product` |
| P4 | No target at all | `/flightplan help me fix the bug` |
| P5 | Record a finished ticket and serve the next | Continues P2's own output: T-01 is reported finished with a stated result, and the session records it the way that version says to, then serves T-02 |

## Running a pair

Each fixture runs once per version, in a fresh general-purpose subagent, with
its own clone of the project and its own stand-in home directory so runs
can't see each other's plan files. Both versions get word-for-word the same
instructions apart from the skill path:

- follow the skill faithfully, as a real session would;
- read the project's CLAUDE.md first, since a real session has it loaded;
- don't call the Artifact tool — write the page where the skill says and
  treat it as published;
- with no live user, write each question exactly, then proceed on the
  recommended answer, or stop where the skill needs an answer first;
- never do a ticket's work;
- save the chat response, a process log (skill files read, questions,
  every tool call, anything unclear in the skill) and any page created.

Token use, tool calls and wall-clock time come from each subagent's
completion notice and are recorded straight away; nothing else keeps them.

## Judging

Checks a script can make are made by script: whether a page exists, whether
its data parses, which skill files were read, whether any Haiku ticket
carries an effort level, and whether the page renders without script errors
or sideways scrolling at phone width.

Everything else goes to a fresh-context grader that sees the two runs as "X"
and "Y", mapped at random and written down before grading starts. It grades
each run against the fixture's assertions, then picks the better run
overall. A second blind judge reads screenshots of the two plan pages as a
non-technical stakeholder would and says which one tells them what is
happening, what each step is for and what came out of it.
