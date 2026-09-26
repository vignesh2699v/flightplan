#!/usr/bin/env python3
"""Fail when a rule is stated in more than one place.

Several files describe one system, and each owns a different job:

    skills/flightplan/SKILL.md                   the paths and pipeline steps
    skills/flightplan/references/*.md            mechanics, strings, templates
    docs/design-notes.md                         rationale

Any rule written into two of them will drift apart, and this one has three
times already -- the v1.7 audit caught it, then v1.11's own review caught it
twice more, the second time inside the commit that claimed to have fixed it.
Discipline did not hold, so this does it mechanically: any run of N
consecutive words appearing in two places fails the check.

Three things are excluded, because each is the pattern we want rather than
the bug:

  fenced code blocks      a template and an example of it filled in are
                          supposed to match; that is not drift
  cross-references        a file name or a section mark, with the section it
                          names, is a pointer -- pointers are the fix, so
                          that span is skipped and the rest of its line
                          is still checked
  paragraph and heading   spans never merge across a blank line or a
  boundaries              heading, so unrelated neighbours can't collide

Anything genuinely repeated on purpose goes in the allowlist, one phrase per
line, with a comment saying why.

    python3 scripts/lint-duplication.py [--shingle N] [--json]

Exits 0 when clean, 1 when a passage is duplicated, 2 on a bad invocation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SOURCES = (
    "skills/flightplan/SKILL.md",
    *sorted(
        str(path.relative_to(REPO))
        for path in (REPO / "skills/flightplan/references").glob("*.md")
    ),
    "docs/design-notes.md",
)

ALLOWLIST = "scripts/duplication-allowlist.txt"
DEFAULT_SHINGLE = 8

# Sentinel token. Shingles are never allowed to span one, which is how
# paragraph, heading, fence and pointer boundaries stay un-crossable.
BARRIER = "\x00"

POINTER = re.compile(r"references/|SKILL\.md|design-notes\.md|§")
# The pointer itself: a file name, optionally with the section it names.
# Only this span is exempt; the rest of the line is still checked, because a
# skill paragraph is one long line and exempting all of it hid real copies.
POINTER_SPAN = re.compile(
    r"`?(?:references/[\w.-]+|SKILL\.md|design-notes\.md)`?(?:\s*§\s*[^,.;:()`]+)?|§\s*[^,.;:()`]+"
)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MARKUP = re.compile(r"[`*_>|#\[\]()]+")
# Leading / keeps /skill-name intact; leading alnum drops list bullets.
TOKEN = re.compile(r"[a-z0-9/][a-z0-9/_.-]*")


def normalize(line: str) -> list[str]:
    """Reduce a line to comparable word tokens, markdown stripped."""
    text = LINK.sub(r"\1", line.lower())
    return TOKEN.findall(MARKUP.sub(" ", text))


def add_line(words: list[tuple[str, int]], raw: str, lineno: int) -> None:
    """Add a line's tokens, with a barrier where each pointer span was cut out."""
    pieces = POINTER_SPAN.split(raw) if POINTER.search(raw) else [raw]
    for number, piece in enumerate(pieces):
        if number:
            words.append((BARRIER, lineno))
        words.extend((token, lineno) for token in normalize(piece))


def tokenize(path: Path) -> list[tuple[str, int]]:
    """Return (token, line number) pairs, with barriers at every boundary.

    A fence line toggles code-block state and is matched on the raw line, so
    the zero-width-space-escaped fences nested inside the output template are
    treated as template content -- which is what they are.
    """
    words: list[tuple[str, int]] = []
    in_fence = False

    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            words.append((BARRIER, lineno))
        elif in_fence or not raw.strip():
            words.append((BARRIER, lineno))
        elif HEADING.search(raw):
            words.append((BARRIER, lineno))
            add_line(words, raw, lineno)
            words.append((BARRIER, lineno))
        else:
            add_line(words, raw, lineno)

    return words


def shingle_index(files: dict[str, list], size: int) -> dict[str, list]:
    """Map every barrier-free window of `size` words to where it occurs."""
    index: dict[str, list] = {}

    for name, words in files.items():
        for start in range(len(words) - size + 1):
            window = words[start : start + size]
            if any(token == BARRIER for token, _ in window):
                continue
            key = " ".join(token for token, _ in window)
            index.setdefault(key, []).append((name, start))

    return index


def contiguous_runs(indices: list[int]):
    """Collapse a sorted index list into (first, last) runs."""
    run_start = previous = indices[0]
    for index in indices[1:]:
        if index != previous + 1:
            yield run_start, previous
            run_start = index
        previous = index
    yield run_start, previous


class Union:
    """Just enough union-find to group spans that share a shingle."""

    def __init__(self) -> None:
        self.parent: dict[int, int] = {}

    def find(self, item: int) -> int:
        self.parent.setdefault(item, item)
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def join(self, left: int, right: int) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def load_allowlist(path: Path) -> list[str]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.append(" ".join(normalize(stripped)))
    return [entry for entry in entries if entry]


def find_duplicates(files: dict[str, list], size: int, allowed: list[str]) -> list[dict]:
    index = shingle_index(files, size)
    duplicated = {key: places for key, places in index.items() if len(places) > 1}
    if not duplicated:
        return []

    # Every word index touched by a duplicated window, per file.
    covered: dict[str, set[int]] = {name: set() for name in files}
    for places in duplicated.values():
        for name, start in places:
            covered[name].update(range(start, start + size))

    # Merge those indices into maximal spans, one entry per contiguous run.
    spans: list[dict] = []
    span_at: dict[tuple[str, int], int] = {}
    for name, indices in covered.items():
        if not indices:
            continue
        words = files[name]
        for first, last in contiguous_runs(sorted(indices)):
            span_id = len(spans)
            spans.append(
                {
                    "file": name,
                    "start_line": words[first][1],
                    "end_line": words[last][1],
                    "words": last - first + 1,
                    "text": " ".join(token for token, _ in words[first : last + 1]),
                }
            )
            for index in range(first, last + 1):
                span_at[(name, index)] = span_id

    # Spans sharing a duplicated window belong to the same finding.
    union = Union()
    for places in duplicated.values():
        span_ids = [span_at[(name, start)] for name, start in places]
        for other in span_ids[1:]:
            union.join(span_ids[0], other)

    clusters: dict[int, list[dict]] = {}
    for span_id, span in enumerate(spans):
        clusters.setdefault(union.find(span_id), []).append(span)

    findings = []
    for members in clusters.values():
        if len(members) < 2:
            continue
        longest = max(members, key=lambda span: span["words"])
        if any(entry in longest["text"] for entry in allowed):
            continue
        findings.append(
            {
                "words": longest["words"],
                "text": longest["text"],
                "places": sorted(
                    (
                        {
                            "file": span["file"],
                            "start_line": span["start_line"],
                            "end_line": span["end_line"],
                        }
                        for span in members
                    ),
                    key=lambda place: (place["file"], place["start_line"]),
                ),
            }
        )

    return sorted(findings, key=lambda finding: -finding["words"])


def format_place(place: dict) -> str:
    if place["start_line"] == place["end_line"]:
        return f"{place['file']}:{place['start_line']}"
    return f"{place['file']}:{place['start_line']}-{place['end_line']}"


def report(findings: list[dict], size: int) -> None:
    if not findings:
        print(f"lint-duplication: clean ({size}-word windows, {len(SOURCES)} files)")
        return

    noun = "passage" if len(findings) == 1 else "passages"
    print(f"lint-duplication: {len(findings)} duplicated {noun}\n")

    for number, finding in enumerate(findings, 1):
        print(f"{number}. {finding['words']} words in {len(finding['places'])} places")
        for place in finding["places"]:
            print(f"     {format_place(place)}")
        excerpt = finding["text"]
        if len(excerpt) > 220:
            excerpt = excerpt[:217] + "..."
        print(f"     {excerpt}\n")

    print(
        "State each rule once, in the file that owns it, and point at it from\n"
        "the others -- the pointer itself is exempt. Repetition that\n"
        f"is genuinely intended goes in {ALLOWLIST}, with a reason."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail when a rule is stated in more than one source file."
    )
    parser.add_argument(
        "--shingle",
        type=int,
        default=DEFAULT_SHINGLE,
        metavar="N",
        help=f"consecutive words that count as a duplicate (default {DEFAULT_SHINGLE})",
    )
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args()

    if args.shingle < 3:
        print("lint-duplication: --shingle must be at least 3", file=sys.stderr)
        return 2

    files = {}
    for name in SOURCES:
        path = REPO / name
        if not path.exists():
            print(f"lint-duplication: missing source file {name}", file=sys.stderr)
            return 2
        files[name] = tokenize(path)

    findings = find_duplicates(files, args.shingle, load_allowlist(REPO / ALLOWLIST))

    if args.json:
        print(json.dumps({"shingle": args.shingle, "findings": findings}, indent=2))
    else:
        report(findings, args.shingle)

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
