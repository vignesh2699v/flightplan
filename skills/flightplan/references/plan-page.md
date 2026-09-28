# The plan page

A plan is one self-contained HTML file copied from `assets/plan-page.html` in this skill's directory. The template holds all layout, styling and behaviour; a plan only adds data lines. So no step writes HTML or CSS, every page looks the same, and each update is a small edit.

## Where it lives

`~/.claude/flightplan/jobs/<slug>.html`, outside any install tree so a reinstall can't touch it. The slug is 2 to 4 kebab-case words, undated, so the plan resolves to the same file next week.

## Find the plan

1. Search `~/.claude/flightplan/jobs/` for the project key (SKILL.md § Pick the path) in `"kind":"plan"` lines. A plan is open until its file has a `"kind":"close"` line.
2. No local file, as on a new machine or a fresh cloud container: list artifacts with the Artifact tool, match the plan's title, read the match and save it to the local path.
3. Still nothing: say so, and ask whether the user has the plan's link rather than assuming there never was one.

## Create

1. Copy the template (its path is in SKILL.md § Plan) to the plan's path, creating the directory if needed.
2. Replace `<title>Untitled plan</title>` with the plan's title, and the line `{"kind":"plan","placeholder":true}` with the data lines: plan, the five context fields, flags, tickets.
3. Publish with the Artifact tool: title is the slug in Title Case, which identifies the plan later; icon `plan`; description is the outcome in one sentence.
4. Append a `url` line with the returned URL, so later sessions redeploy without searching; it goes out with the next republish.

On first publish, flag that the page holds every ticket prompt word for word and stays private until the user shares it.

## Update

The plan's whole state is the data block at the top of the file, so read only down to `</script><!--flightplan:data-->`; everything below it is the unchanging template, apart from the prompt blocks.

Every change is an append: new data lines go directly above `</script><!--flightplan:data-->`, new prompt blocks directly above `<!--flightplan:prompts-->`. Then republish to the same URL. Never edit or delete an earlier line; the latest line for a ticket wins and the older ones are its history, which keeps every edit small and its target unique.

The Artifact tool requires a session to read a page before its first republish. If the published copy has lines the local file lacks, save it over the local file before appending.

## Data lines

One JSON object per line. Strings stay on one line; escape `"` as `\"`, and write every `<` as `\u003c` so no string can end the block early.

```text
{"kind":"plan","slug":"onboarding-redesign","title":"Onboarding Redesign","project":"github.com/acme/shop","outcome":"…","approach":"…","created":"2026-09-25"}
{"kind":"context","field":"What this is","value":"…","source":"README, line 3"}
{"kind":"flag","text":"…"}
{"kind":"flag","text":"…","tech":true}
{"kind":"ticket","id":"T-01","title":"…","why":"…","done":"…","tool":"/impeccable","beat":"…","model":"opus","effort":"medium","where":"session","guards":["Read-only"]}
{"kind":"status","id":"T-01","status":"done","result":"…","evidence":"docs/audit.md","at":"2026-09-25"}
{"kind":"url","url":"…"}
{"kind":"close","summary":"…","at":"2026-09-26"}
```

- **plan**: `outcome` is one plain sentence on what done looks like; `approach` is two or three.
- **flag**: something the reader should know or act on, in plain words. A note only a developer needs, such as a missing tool or token or the routing funnel, adds `"tech":true` and sits in a collapsed Technical notes section.
- **context**: one line per field from SKILL.md § Read, in order, labelled with a capital first letter ("What this is"). A field reading couldn't settle has the value `not established`.
- **ticket**: `title` starts with a verb. `why` is one sentence on what the ticket is for, in words someone who has never seen the code would follow. `tool` and `beat` name the pick and the runner-up it beat, with the reason; omit both when nothing is needed. Omit `effort` for `haiku`. `where` is `session` or `subagent`; `guards` lists applicable constraints in a few words each. IDs run `T-01` upward and never change, since records address tickets by ID; a ticket added or re-planned later is a new `ticket` line under its ID, and a re-planned ticket also gets a `pending` status line, since a `stale` status stays until one replaces it.
- **status**: `pending` until a line says `live`, `done`, `failed`, or `stale` (a finding invalidated it). `result` is the sentence § Record in SKILL.md asks for, and `evidence` is a URL or path.
- **close**: `summary` is one sentence on what the plan produced.

## Prompts

Each served prompt is its own block, paragraphs separated by blank lines. Inside a prompt, write `</` as `<\/` and `<!--` as `<\!--`; either could otherwise end the block early, and the page turns both back when it shows the prompt:

```html
<script type="text/plain" data-prompt="T-03">
The prompt text.
</script>
```

The page shows the live prompt with a Copy button and earlier ones inside their tickets.

## Without the Artifact tool

The local file is the page. Give the user its path to open in a browser, and also put each served prompt in chat as one fenced block. Say once that a local page stands in for the published one.
