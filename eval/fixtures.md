# Evaluation fixtures

> From v3.0, releases are measured on [`fixtures-v3.md`](fixtures-v3.md), which
> runs against a real fixture project. This file is kept unchanged as the
> baseline for the v1 results that cite it.

Ten raw prompts spanning the shapes `rebuild-prompt` handles differently.
Written 2026-08-02 for the first baseline-vs-skill comparison
(`2026-08-02-v1.11-results.md`). Reuse these unchanged for future comparisons
so results are comparable release over release — don't rewrite a fixture to
make a later version look better; add new fixtures instead if a new shape
needs covering.

| # | Shape being tested | Raw prompt |
|---|---|---|
| F1 | Trivial, single-task, uncontested | "Add a loading spinner to the submit button in checkout.tsx while the payment request is in flight." |
| F2 | Contested single-task | "This landing page looks generic and cheap. Make it feel premium." |
| F3 | Multi-task, all uncontested | "Fix the failing test in auth.test.ts, update the README to document the new AUTH_TIMEOUT_MS env var, then commit the changes." |
| F4 | Multi-task, mixed contested/uncontested | "Refactor the payment processing module for clarity, then get it reviewed for security issues before we ship it." |
| F5 | 5+ tasks, should segment at a finding boundary | "Audit our onboarding flow for UX issues, redesign the flow based on what you find, implement the redesign, write tests for the new flow, and deploy it to staging." |
| F6 | Job needing two different models — mechanical + deep-reasoning | "Rename these 40 CSS classes across the codebase to match our new BEM naming convention, then do a deep architectural review of whether our current state management approach will scale to a multi-tenant version of the product." |
| F7 | Ambiguous — grilling target | "Make the app faster." |
| F8 | Ambiguous, zero signal — grilling + `[?]` target | "Help me fix the bug." |
| F9 | Verification-shaped single task | "Check that the new signup flow actually works end to end before we tell marketing it's ready to promote." |
| F10 | Plan-shaped task | "I need a plan for migrating our REST API to GraphQL." |

## Running a fixture pair

**Baseline:** dispatch a fresh general-purpose agent with the raw prompt only, explicitly told not to invoke `rebuild-prompt` or any other named skill, and told there's no real codebase (this is a synthetic fixture) so it should treat file/context references as hypothetical and give its single-turn best answer, asking at most one clarifying question with a stated default fallback since there's no live user to answer it.

**Skill condition:** dispatch a fresh general-purpose agent instructed to invoke `rebuild-prompt` via the Skill tool on the same raw prompt, following its documented process faithfully, with two adaptations for non-interactive testing: auto-select the "(Recommended)" ballot option wherever `AskUserQuestion` would normally fire (noting every place this happened and the alternatives), and proceed using only the request's own text since there's no real project/memory context to look up.

## Judging

Dispatch a **fresh-context judge with no knowledge of which output came from which condition** — randomize which output is labeled "A" and which is "B" independently per fixture (don't always put baseline first). Score each fixture on: routing/approach accuracy, completeness (success criteria, constraints, scope guards present), and structural soundness (model/effort tagging and segmentation, where applicable). Un-blind only after scoring is complete.

**Known confound, carried into every fixture:** `rebuild-prompt`'s contract is to return a prompt for later execution, never to execute the task itself. On a small, single-shot, already-obvious task, a prepared prompt reads as a worse deliverable than a direct answer — because answering *is* the deliverable there. This isn't a flaw the eval should score away; it's baked into what's being compared. See `2026-08-02-v1.11-results.md` for how this played out and why the contract was kept as-is rather than "fixed."
