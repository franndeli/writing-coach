#!/usr/bin/env python3
"""Health and privacy check for a writing-coach workspace.

Usage:
    python3 doctor.py [--offline]        # run from anywhere inside the workspace

Checks Python version, the workspace marker, missing template files, unfilled STYLE.md/GOALS.md, sample count,
untagged journal entries, journal review age, and, most importantly, whether any git remote is a PUBLIC GitHub
repository. That check uses GitHub's unauthenticated API; --offline skips it.

Exit code: 1 if any check FAILs (e.g. a public remote), otherwise 0.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Callable, List, Optional, Tuple

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "workspace"
OK, WARN, FAIL, INFO = "ok", "warn", "FAIL", "info"

Result = Tuple[str, str]  # (level, message)

GITHUB_RE = re.compile(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")


def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def find_workspace(start: Optional[Path] = None) -> Optional[Path]:
    here = (start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        if (d / ".writing-coach").exists():
            return d
    return None


def parse_github(url: str) -> Optional[Tuple[str, str]]:
    m = GITHUB_RE.search(url.strip())
    return (m.group(1), m.group(2)) if m else None


def github_visibility(owner: str, repo: str, timeout: float = 5.0) -> str:
    """Return 'public', 'private-or-missing', or 'unknown'."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers={"User-Agent": "writing-coach-doctor", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return "private-or-missing" if data.get("private") else "public"
    except urllib.error.HTTPError as e:
        return "private-or-missing" if e.code == 404 else "unknown"
    except (urllib.error.URLError, OSError, ValueError):
        return "unknown"


def git_remotes(ws: Path) -> Optional[List[Tuple[str, str]]]:
    """List (name, url) remotes, or None if ws isn't a git repo or git is missing."""
    try:
        out = subprocess.run(["git", "remote", "-v"], cwd=ws, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    seen = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and (parts[0], parts[1]) not in seen:
            seen.append((parts[0], parts[1]))
    return seen


def check_privacy(ws: Path, offline: bool, visibility: Callable[[str, str], str] = github_visibility) -> List[Result]:
    if not (ws / ".git").exists():
        return [(WARN, "not a git repo: run `git init` so your style history is versioned (keep it local or private)")]
    remotes = git_remotes(ws)
    if remotes is None:
        return [(WARN, "could not run git to inspect remotes")]
    if not remotes:
        return [(OK, "no git remotes: the workspace is local only")]
    results: List[Result] = []
    for name, url in remotes:
        gh = parse_github(url)
        if not gh:
            results.append((WARN, f"remote '{name}' ({url}) isn't on GitHub, so visibility can't be verified. Make sure it's private"))
        elif offline:
            results.append((WARN, f"remote '{name}' is github.com/{gh[0]}/{gh[1]}; visibility not checked (--offline)"))
        else:
            vis = visibility(*gh)
            if vis == "public":
                results.append((FAIL, f"remote '{name}' github.com/{gh[0]}/{gh[1]} is PUBLIC. Your drafts and journal are exposed. "
                                      f"Make it private: gh repo edit {gh[0]}/{gh[1]} --visibility private --accept-visibility-change-consequences"))
            elif vis == "private-or-missing":
                results.append((OK, f"remote '{name}' github.com/{gh[0]}/{gh[1]} is not publicly visible"))
            else:
                results.append((WARN, f"remote '{name}' github.com/{gh[0]}/{gh[1]}: couldn't reach GitHub to check visibility"))
    return results


def check_template_files(ws: Path, template: Path = TEMPLATE) -> List[Result]:
    missing = [
        p.relative_to(template).as_posix()
        for p in template.rglob("*")
        if p.is_file() and p.name != ".gitkeep" and not (ws / p.relative_to(template)).exists()
    ]
    if not missing:
        return [(OK, "all template files present")]
    return [(WARN, f"{len(missing)} template file(s) missing ({', '.join(sorted(missing)[:5])}{'…' if len(missing) > 5 else ''}). "
                   f"Run init_workspace.py on this folder to add them; existing files are never touched")]


def check_profiles(ws: Path) -> List[Result]:
    out: List[Result] = []
    style, goals = ws / "STYLE.md", ws / "GOALS.md"
    if not style.exists() or "Not generated yet" in style.read_text(encoding="utf-8"):
        out.append((INFO, "STYLE.md not generated yet: add samples, then ask for the Bootstrap workflow"))
    else:
        out.append((OK, "STYLE.md generated"))
    if not goals.exists() or "Not set yet" in goals.read_text(encoding="utf-8"):
        out.append((INFO, "GOALS.md not set yet: ask 'set up my writing goals' (needed for journal reviews)"))
    else:
        out.append((OK, "GOALS.md set"))
    n = sum(1 for _ in (ws / "samples").glob("*/*.md")) if (ws / "samples").exists() else 0
    out.append((OK if n >= 10 else INFO, f"{n} writing sample(s){'' if n >= 10 else ' (10–20 recommended for a reliable STYLE.md)'}"))
    return out


def check_journal(ws: Path, today: Optional[date] = None) -> List[Result]:
    today = today or date.today()
    entries = sorted((ws / "journal").glob("[0-9][0-9][0-9][0-9]/*.md")) if (ws / "journal").exists() else []
    if not entries:
        return [(INFO, "journal is empty")]
    untagged = [p.stem for p in entries if re.search(r"(?m)^themes:\s*\[\s*\]\s*$", p.read_text(encoding="utf-8"))]
    out: List[Result] = [(OK, f"{len(entries)} journal entr{'y' if len(entries) == 1 else 'ies'}")]
    if untagged:
        out.append((WARN, f"{len(untagged)} untagged entr{'y' if len(untagged) == 1 else 'ies'} ({', '.join(untagged[-3:])}): reviews rely on themes"))
    cand = ws / "journal" / "candidates.md"
    if cand.exists():
        m = re.search(r"(?m)^Last review:\s*(\S+)", cand.read_text(encoding="utf-8"))
        last = m.group(1) if m else "never"
        try:
            age = (today - date.fromisoformat(last)).days
            out.append((INFO, f"last journal review {age} day(s) ago ({last})"))
        except ValueError:
            out.append((INFO, "journal never reviewed yet"))
    return out


def run(ws: Optional[Path], offline: bool = False) -> List[Result]:
    results: List[Result] = []
    v = sys.version_info
    results.append((OK if v >= (3, 9) else FAIL, f"Python {v.major}.{v.minor}{'' if v >= (3, 9) else ' (3.9+ required)'}"))
    if ws is None:
        results.append((FAIL, "not inside a writing-coach workspace (no .writing-coach marker). Create one with init_workspace.py"))
        return results
    results.append((OK, f"workspace: {ws}"))
    for check in (lambda: check_privacy(ws, offline), lambda: check_template_files(ws),
                  lambda: check_profiles(ws), lambda: check_journal(ws)):
        results.extend(check())
    return results


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Health and privacy check for a writing-coach workspace.")
    ap.add_argument("--offline", action="store_true", help="skip the GitHub visibility check")
    args = ap.parse_args(argv)
    _utf8_stdout()
    results = run(find_workspace(), args.offline)
    for level, msg in results:
        print(f"[{level:^4}] {msg}")
    failed = any(level == FAIL for level, _ in results)
    print("\nPrivacy problem found. Fix it before writing anything else." if failed else "\nAll good.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
