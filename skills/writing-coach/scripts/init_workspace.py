#!/usr/bin/env python3
"""Create (or complete) a private writing-coach workspace.

Usage:
    python3 init_workspace.py [DIR]      # default: ~/writing

Copies the workspace template into DIR. Existing files are never overwritten: missing ones are added, so the
script is safe to re-run on a workspace that already has data (e.g. to pick up new template files after an update).
Runs `git init` if DIR isn't a git repo yet. The workspace is meant to stay private.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "workspace"


def init_workspace(target: Path, template: Path = TEMPLATE, git: bool = True) -> tuple[list[Path], list[Path]]:
    """Copy missing template files into target. Returns (added, skipped) relative paths."""
    target = target.expanduser().resolve()
    if template.resolve() == target or template.resolve() in target.parents:
        raise ValueError("refusing to create a workspace inside the skill's own directory")
    added: list[Path] = []
    skipped: list[Path] = []
    for src in sorted(template.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(template)
        dst = target / rel
        if dst.exists():
            skipped.append(rel)
            continue
        # A .gitkeep is pointless if the folder already has content.
        if src.name == ".gitkeep" and dst.parent.exists() and any(dst.parent.iterdir()):
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        added.append(rel)
    if git and not (target / ".git").exists() and shutil.which("git"):
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=target, check=False)
    return added, skipped


def _utf8_stdout() -> None:
    """Windows consoles default to a legacy code page; force UTF-8 so non-ASCII output never crashes."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    _utf8_stdout()
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    target = Path(argv[0] if argv else "~/writing").expanduser()
    try:
        added, skipped = init_workspace(target)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"Workspace: {target.resolve()}")
    print(f"  added {len(added)} file(s), kept {len(skipped)} existing file(s) untouched")
    for rel in added:
        print(f"  + {rel}")
    print("\nKeep this folder private. Next: open your agent here and say 'set up my writing goals'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
