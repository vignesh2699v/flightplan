#!/usr/bin/env python3
"""Check the skill against what installers, directories and scanners enforce.

Run before every release, alongside lint-duplication.py:

    python3 scripts/check-skill.py [skills/flightplan]

It checks five things, each of which has either broken an install or tripped
an automated audit for some published skill:

  frontmatter   only the Agent Skills fields; a name that matches its folder;
                a one-line description of at most 1024 characters with no
                angle brackets; compatibility of at most 500 characters with
                no URLs or install commands in it
  size          SKILL.md under 500 lines, so it loads in one sitting
  characters    no invisible format or control characters anywhere in the
                skill folder -- security scanners flag hidden Unicode
  pointers      every references/ or assets/ path the skill names exists
  template      the plan-page template still carries the exact anchors the
                skill tells the model to edit, declares UTF-8, and keeps its
                script ASCII so a local copy never shows garbled characters

Exits 0 when clean, 1 when a check fails.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
INSTALLISH = re.compile(r"https?://|\bnpx\b|\bcurl\b|\bpip install\b|\bgit clone\b|\bbrew install\b")
POINTER = re.compile(r"\b((?:references|assets|scripts)/[A-Za-z0-9_.-]+)")
TEMPLATE_ANCHORS = (
    "<title>Untitled plan</title>",
    '{"kind":"plan","placeholder":true}',
    "</script><!--flightplan:data-->",
    "<!--flightplan:prompts-->",
)


def frontmatter(text: str) -> tuple[dict, list[str]]:
    """Parse the small YAML subset skills use: scalars plus one nested map."""
    problems: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["SKILL.md does not open with a --- frontmatter block"]
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, ["SKILL.md frontmatter is never closed"]
    data: dict = {}
    parent = None
    for raw in text[4:end].splitlines():
        if not raw.strip():
            continue
        if raw.startswith((" ", "\t")):
            if parent is None:
                problems.append(f"indented line with no parent key: {raw.strip()}")
                continue
            key, _, value = raw.strip().partition(":")
            data[parent][key.strip()] = value.strip()
            continue
        key, sep, value = raw.partition(":")
        if not sep:
            problems.append(f"frontmatter line is not key: value: {raw}")
            continue
        key, value = key.strip(), value.strip()
        if value == "":
            data[key] = {}
            parent = key
        else:
            data[key] = value
            parent = None
    return data, problems


def check_frontmatter(skill: Path, text: str) -> list[str]:
    data, problems = frontmatter(text)
    extra = set(data) - ALLOWED_KEYS
    if extra:
        problems.append(f"frontmatter keys outside the Agent Skills spec: {', '.join(sorted(extra))}")
    name = data.get("name", "")
    if not isinstance(name, str) or not NAME.match(name) or len(name) > 64:
        problems.append(f"name {name!r} must be 1-64 lowercase letters, digits and single hyphens")
    elif name != skill.name:
        problems.append(f"name {name!r} must match its folder name {skill.name!r}")
    description = data.get("description", "")
    if not isinstance(description, str) or not description:
        problems.append("description is missing")
    else:
        if description in {">", ">-", "|", "|-"}:
            problems.append("description should be a single line, not a block scalar")
        if len(description) > 1024:
            problems.append(f"description is {len(description)} characters; the limit is 1024")
        if "<" in description or ">" in description:
            problems.append("description contains angle brackets")
        if ": " in description:
            problems.append("description contains ': ', which breaks an unquoted YAML scalar")
    compatibility = data.get("compatibility", "")
    if compatibility:
        if len(compatibility) > 500:
            problems.append(f"compatibility is {len(compatibility)} characters; the limit is 500")
        if INSTALLISH.search(compatibility):
            problems.append("compatibility names a URL or install command; scanners flag that")
    metadata = data.get("metadata", {})
    if metadata and not isinstance(metadata, dict):
        problems.append("metadata must be a map")
    return problems


def check_characters(skill: Path) -> list[str]:
    """Scan every text file character by character.

    str.splitlines() would treat several control characters (form feed,
    U+0085 and others) as line breaks and hide them, so lines are counted by
    newline only, and every file that decodes as UTF-8 is checked whatever
    its suffix.
    """
    problems = []
    for path in sorted(skill.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary asset
        seen_lines = set()
        lineno = 1
        for char in text:
            if char == "\n":
                lineno += 1
            elif char not in "\t\r" and unicodedata.category(char) in {"Cf", "Cc"} and lineno not in seen_lines:
                seen_lines.add(lineno)
                problems.append(f"{path.relative_to(REPO)}:{lineno} hidden character U+{ord(char):04X}")
    return problems


def check_pointers(skill: Path) -> list[str]:
    problems = []
    for path in [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for target in POINTER.findall(line):
                if not (skill / target.rstrip(".,;:)")).exists():
                    problems.append(f"{path.relative_to(REPO)}:{lineno} points at missing {target}")
    return problems


def check_template(skill: Path) -> list[str]:
    template = skill / "assets" / "plan-page.html"
    if not template.exists():
        return ["assets/plan-page.html is missing"]
    text = template.read_text(encoding="utf-8")
    problems = [f"template anchor {a!r} appears {text.count(a)} times; expected once"
                for a in TEMPLATE_ANCHORS if text.count(a) != 1]
    if text.find("<title>") > 8192:
        problems.append("the template's <title> is past the first 8KB, where the Artifact tool looks")
    # Opened as a local file, the page has no wrapper to declare its encoding,
    # and a misread encoding garbles every non-ASCII character it draws.
    if not text.startswith('<meta charset="utf-8">'):
        problems.append('the template must open with <meta charset="utf-8"> so a local copy decodes correctly')
    if any(ord(char) > 127 for char in text):
        problems.append("the template holds raw non-ASCII characters; use \\uXXXX escapes in its script")
    return problems


def main() -> int:
    skill = (REPO / (sys.argv[1] if len(sys.argv) > 1 else "skills/flightplan")).resolve()
    skill_md = skill / "SKILL.md"
    if not skill_md.exists():
        print(f"check-skill: no SKILL.md in {skill}", file=sys.stderr)
        return 1
    text = skill_md.read_text(encoding="utf-8")
    nested = [p for p in skill.rglob("SKILL.md") if p != skill_md]

    problems = check_frontmatter(skill, text)
    # Count newlines, not splitlines(): form feeds and U+0085 are not line breaks here.
    lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    if lines >= 500:
        problems.append(f"SKILL.md is {lines} lines; keep it under 500")
    if nested:
        problems.append("extra SKILL.md files inside the skill: " + ", ".join(str(p.relative_to(REPO)) for p in nested))
    problems += check_characters(skill)
    problems += check_pointers(skill)
    problems += check_template(skill)

    if problems:
        print(f"check-skill: {len(problems)} problem{'s' if len(problems) != 1 else ''}")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    words = sum(len(p.read_text(encoding="utf-8").split()) for p in [skill_md])
    print(f"check-skill: clean ({skill.relative_to(REPO)}, SKILL.md {lines} lines / {words} words)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
