#!/usr/bin/env python3
"""Check that a text uses only my words.

Usage (from your workspace; <skill> is where the writing-coach skill is installed):
    python3 <skill>/scripts/check_words.py drafts/<slug>/final-linkedin.md [--draft DIR] [--source FILE ...]

The draft directory defaults to the folder that contains the checked file. Text counts as mine if it
comes from:
  - raw.md        (everything except HTML comments)
  - interview.md  (everything except blockquote lines, which are the agent's questions, and headings)
  - brief.md      (everything except headings)
  - allow.txt     (phrases I approved; '#' comment lines are ignored)
  - any extra --source files (with --sources-only, ONLY these, e.g. to check raw.md against journal entries)

A word in the checked text is covered when one of these holds:
  * it's a glue word (glue_words.txt next to this script, or the workspace's own glue_words.txt);
  * it sits inside a run of >= MIN_RUN consecutive words that appears verbatim in my text;
  * it sits inside a shorter verbatim run that has >= 2 non-glue words;
  * it is (or forms with glue around it) a complete clause of my text, e.g. "Honestly." or "Why?"

Anything else is flagged. Leftover [GAP: ...] markers are flagged too.
Exit code: 0 when clean, 1 when anything is flagged, 2 on usage errors.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

GLUE_FILE = Path(__file__).resolve().parent / "glue_words.txt"
MIN_RUN = 3

WORD_RE = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)
# Clause boundaries: sentence and clause punctuation, plus line breaks.
CLAUSE_SPLIT_RE = re.compile(r"[.!?;:,()\[\]\"“”«»—–…\n]+")
GAP_RE = re.compile(r"\[GAP\b[^\]]*\]", re.IGNORECASE)


def load_glue(path: Path = GLUE_FILE) -> set[str]:
    if not path.exists():
        return set()
    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            words.add(line)
    return words


def normalize(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    return text.lower()


def strip_markdown(text: str) -> str:
    """Remove non-prose markdown: frontmatter, comments, links, images, URLs, emphasis markers."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?m)^\s*(?:[-*+]|\d+[.)])\s+", "\n", text)  # list markers start a new clause
    text = re.sub(r"(?m)^\s*#{1,6}\s*", "\n", text)  # heading markers
    text = re.sub(r"[*_~]+", " ", text)  # emphasis
    return text


def words(text: str) -> list[str]:
    return WORD_RE.findall(normalize(text))


def clauses(text: str) -> list[list[str]]:
    out = []
    for chunk in CLAUSE_SPLIT_RE.split(normalize(text)):
        ws = WORD_RE.findall(chunk)
        if ws:
            out.append(ws)
    return out


def _source_text(path: Path, kind: str) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = text.splitlines()
    if kind == "interview":
        lines = [l for l in lines if not l.lstrip().startswith(">") and not l.lstrip().startswith("#")]
    elif kind == "brief":
        lines = [l for l in lines if not l.lstrip().startswith("#")]
    elif kind == "allow":
        lines = [l for l in lines if not l.lstrip().startswith("#")]
    return strip_markdown("\n".join(lines))


def collect_sources(draft_dir: Path | None, extra: list[Path]) -> list[str]:
    texts = []
    if draft_dir is not None:
        for name, kind in (("raw.md", "raw"), ("interview.md", "interview"), ("brief.md", "brief"), ("allow.txt", "allow")):
            p = draft_dir / name
            if p.exists():
                texts.append(_source_text(p, kind))
    for p in extra:
        texts.append(_source_text(p, "raw"))
    return texts


@dataclass
class Source:
    stream: str  # " w1 w2 ... " with paragraph separators, for verbatim-run lookup
    clause_cores: set[tuple[str, ...]]

    def contains(self, seq: list[str]) -> bool:
        return (" " + " ".join(seq) + " ") in self.stream


def build_source(texts: list[str], glue: set[str]) -> Source:
    parts = []
    cores: set[tuple[str, ...]] = set()
    for t in texts:
        for para in re.split(r"\n\s*\n", t):
            ws = words(para)
            if ws:
                parts.append(" ".join(ws))
        for c in clauses(t):
            core = _core(c, glue)
            if core:
                cores.add(tuple(core))
    return Source(stream=" " + " ¶ ".join(parts) + " ", clause_cores=cores)


def _core(seq: list[str], glue: set[str]) -> list[str]:
    i, j = 0, len(seq)
    while i < j and seq[i] in glue:
        i += 1
    while j > i and seq[j - 1] in glue:
        j -= 1
    return seq[i:j]


def check_clause(clause: list[str], src: Source, glue: set[str], min_run: int = MIN_RUN) -> list[bool]:
    n = len(clause)
    covered = [w in glue for w in clause]
    for i in range(n):
        for j in range(i + 1, n + 1):
            span = clause[i:j]
            if not src.contains(span):
                break  # longer spans from i can't match either
            non_glue = sum(1 for w in span if w not in glue)
            core = tuple(_core(span, glue))
            if len(span) >= min_run or non_glue >= 2 or (core and core in src.clause_cores):
                for k in range(i, j):
                    covered[k] = True
    return covered


@dataclass
class Finding:
    line_no: int
    line: str
    flagged: list[str]


def check_text(text: str, src: Source, glue: set[str], min_run: int = MIN_RUN) -> tuple[list[Finding], int, int]:
    findings: list[Finding] = []
    total = flagged_total = 0
    body = re.sub(r"\A---\n.*?\n---\n", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)
    body = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), body, flags=re.DOTALL)
    for line_no, raw_line in enumerate(body.splitlines(), start=1):
        flagged: list[str] = []
        for gap in GAP_RE.findall(raw_line):
            flagged.append(f"unfilled {gap}")
        line = GAP_RE.sub(" ", raw_line)
        for clause in clauses(strip_markdown(line)):
            cov = check_clause(clause, src, glue, min_run)
            total += len(clause)
            run: list[str] = []
            for w, ok in zip(clause, cov):
                if ok:
                    if run:
                        flagged.append(" ".join(run))
                        run = []
                else:
                    run.append(w)
                    flagged_total += 1
            if run:
                flagged.append(" ".join(run))
        if flagged:
            findings.append(Finding(line_no, raw_line.strip(), flagged))
    return findings, total, flagged_total


def extract_section(text: str, heading: str) -> str | None:
    """Return the body of the markdown section titled `heading`, with other lines blanked so line numbers stay."""
    lines = text.splitlines()
    out = [""] * len(lines)
    level = None
    found = False
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m and level is not None and len(m.group(1)) <= level:
            level = None
        if m and m.group(2).strip().lower() == heading.strip().lower():
            level = len(m.group(1))
            found = True
            continue
        if level is not None:
            out[i] = line
    return "\n".join(out) if found else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify a text uses only my words.")
    ap.add_argument("file", type=Path, help="text to check, e.g. drafts/<slug>/final-linkedin.md")
    ap.add_argument("--draft", type=Path, help="draft dir with raw.md etc. (default: the file's folder)")
    ap.add_argument("--source", type=Path, action="append", default=[], help="extra source file(s) of my words")
    ap.add_argument("--sources-only", action="store_true", help="ignore the draft folder; use only --source files (e.g. to verify raw.md against the journal)")
    ap.add_argument("--glue", type=Path, help="glue-word list (default: ./glue_words.txt if present, else the bundled one)")
    ap.add_argument("--section", help="only check the markdown section with this heading, e.g. Text")
    ap.add_argument("--min-run", type=int, default=MIN_RUN, help=f"verbatim run length that always counts (default {MIN_RUN})")
    args = ap.parse_args(argv)

    if not args.file.exists():
        print(f"error: {args.file} not found", file=sys.stderr)
        return 2
    draft_dir = None if args.sources_only else (args.draft or args.file.parent)
    if args.sources_only and not args.source:
        print("error: --sources-only needs at least one --source", file=sys.stderr)
        return 2
    if draft_dir is not None and not (draft_dir / "raw.md").exists() and not args.source:
        print(f"error: no raw.md in {draft_dir} and no --source given", file=sys.stderr)
        return 2

    glue_file = args.glue or (Path("glue_words.txt") if Path("glue_words.txt").exists() else GLUE_FILE)
    glue = load_glue(glue_file)
    src = build_source(collect_sources(draft_dir, args.source), glue)
    text = args.file.read_text(encoding="utf-8")
    if args.section:
        text = extract_section(text, args.section)
        if text is None:
            print(f"error: no '{args.section}' section in {args.file}", file=sys.stderr)
            return 2
    findings, total, flagged = check_text(text, src, glue, args.min_run)

    if not findings:
        print(f"✅ {args.file}: all {total} words are yours.")
        return 0
    print(f"⚠️  {args.file}: {flagged} of {total} words not found in your text.\n")
    for f in findings:
        print(f"  line {f.line_no}: {f.line}")
        for span in f.flagged:
            print(f"      ✗ {span}")
    print("\nIf a flagged span is yours (e.g. an approved grammar fix), add it to allow.txt in the draft folder.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
