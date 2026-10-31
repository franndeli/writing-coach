#!/usr/bin/env python3
"""Journal helpers for a writing-coach workspace. Run from anywhere inside the workspace.

Commands:
  path [--date D]                              print (and create) the entry file for a day (default today)
  add  [--date D] [--time HH:MM]               append stdin VERBATIM under a "## HH:MM" heading
  tag  [--date D] [--themes a,b] [--people x] [--projects y]
                                               merge tags into the entry's frontmatter (body untouched)
  themes [--since 30d|YYYY-MM-DD] [--month YYYY-MM]
                                               theme frequency across entries, most frequent first
  candidates [--status open|in|out|used]       list rows from journal/candidates.md

Entries live in journal/YYYY/YYYY-MM-DD.md. Only the frontmatter is ever rewritten. The body is append-only.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

LIST_KEYS = ("themes", "people", "projects")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def find_workspace(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        if (d / ".writing-coach").exists():
            return d
    raise SystemExit("error: not inside a writing-coach workspace (no .writing-coach marker found)")


def parse_date(s: str | None) -> date:
    return date.fromisoformat(s) if s else date.today()


def entry_path(ws: Path, d: date) -> Path:
    return ws / "journal" / f"{d.year:04d}" / f"{d.isoformat()}.md"


def new_entry_text(d: date) -> str:
    return f"---\ndate: {d.isoformat()}\nthemes: []\npeople: []\nprojects: []\n---\n"


def ensure_entry(ws: Path, d: date) -> Path:
    p = entry_path(ws, d)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(new_entry_text(d), encoding="utf-8")
    return p


def read_frontmatter(text: str) -> tuple[dict[str, list[str] | str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, list[str] | str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.split("#", 1)[0].strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        else:
            meta[key] = val
    return meta, text[m.end():]


def write_frontmatter(meta: dict[str, list[str] | str], body: str) -> str:
    lines = []
    for k, v in meta.items():
        lines.append(f"{k}: [{', '.join(v)}]" if isinstance(v, list) else f"{k}: {v}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def cmd_add(ws: Path, d: date, time: str | None, text: str) -> Path:
    if not text.strip():
        raise SystemExit("error: nothing to add (stdin was empty)")
    p = ensure_entry(ws, d)
    stamp = time or datetime.now().strftime("%H:%M")
    current = p.read_text(encoding="utf-8")
    sep = "" if current.endswith("\n\n") else ("\n" if current.endswith("\n") else "\n\n")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"{sep}## {stamp}\n\n{text.rstrip(chr(10))}\n")
    return p


def cmd_tag(ws: Path, d: date, tags: dict[str, list[str]]) -> Path:
    p = entry_path(ws, d)
    if not p.exists():
        raise SystemExit(f"error: no entry for {d.isoformat()}")
    meta, body = read_frontmatter(p.read_text(encoding="utf-8"))
    meta.setdefault("date", d.isoformat())
    for key in LIST_KEYS:
        existing = list(meta.get(key) or []) if isinstance(meta.get(key, []), list) else []
        for t in tags.get(key, []):
            t = t.strip()
            if t and t not in existing:
                existing.append(t)
        meta[key] = existing
    p.write_text(write_frontmatter(meta, body), encoding="utf-8")
    return p


def iter_entries(ws: Path):
    for p in sorted((ws / "journal").glob("[0-9][0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md")):
        try:
            d = date.fromisoformat(p.stem)
        except ValueError:
            continue
        yield d, p


def parse_since(s: str | None) -> date | None:
    if not s:
        return None
    m = re.fullmatch(r"(\d+)d", s)
    if m:
        return date.today() - timedelta(days=int(m.group(1)))
    return date.fromisoformat(s)


def theme_counts(ws: Path, since: date | None = None, month: str | None = None) -> list[tuple[str, int, list[str]]]:
    seen: dict[str, list[str]] = defaultdict(list)
    for d, p in iter_entries(ws):
        if since and d < since:
            continue
        if month and d.isoformat()[:7] != month:
            continue
        meta, _ = read_frontmatter(p.read_text(encoding="utf-8"))
        themes = meta.get("themes") or []
        for t in themes if isinstance(themes, list) else []:
            seen[t].append(d.isoformat())
    return sorted(((t, len(ds), ds) for t, ds in seen.items()), key=lambda x: (-x[1], x[0]))


def candidate_rows(ws: Path, status: str | None = None) -> list[str]:
    p = ws / "journal" / "candidates.md"
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Date"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if status and (not cells or not cells[-1].lower().startswith(status.lower())):
            continue
        rows.append(line)
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Journal helpers for a writing-coach workspace.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_path = sub.add_parser("path")
    p_path.add_argument("--date")
    p_add = sub.add_parser("add")
    p_add.add_argument("--date")
    p_add.add_argument("--time")
    p_tag = sub.add_parser("tag")
    p_tag.add_argument("--date")
    for k in LIST_KEYS:
        p_tag.add_argument(f"--{k}", default="")
    p_th = sub.add_parser("themes")
    p_th.add_argument("--since")
    p_th.add_argument("--month")
    p_c = sub.add_parser("candidates")
    p_c.add_argument("--status")
    args = ap.parse_args(argv)

    ws = find_workspace()
    if args.cmd == "path":
        print(ensure_entry(ws, parse_date(args.date)).relative_to(ws))
    elif args.cmd == "add":
        p = cmd_add(ws, parse_date(args.date), args.time, sys.stdin.read())
        print(f"saved: {p.relative_to(ws)}")
    elif args.cmd == "tag":
        tags = {k: [t for t in getattr(args, k).split(",") if t.strip()] for k in LIST_KEYS}
        p = cmd_tag(ws, parse_date(args.date), tags)
        print(f"tagged: {p.relative_to(ws)}")
    elif args.cmd == "themes":
        rows = theme_counts(ws, parse_since(args.since), args.month)
        if not rows:
            print("no themes yet")
        for t, n, ds in rows:
            print(f"{n:>3}  {t:<28} {', '.join(ds[-5:])}{' …' if n > 5 else ''}")
    elif args.cmd == "candidates":
        rows = candidate_rows(ws, args.status)
        print("\n".join(rows) if rows else "no candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
