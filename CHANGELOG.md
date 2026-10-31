# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/).

## [0.1.1] - 2026-10-31

### Changed
- README: npm and Pi package badges; Pi install now uses `pi install npm:writing-coach`.
- The npm package excludes Python cache files and runs the test suite before publishing.

## [0.1.0] - 2026-10-31

First public release.

### Added
- **The writing-coach skill**, a portable [Agent Skill](https://agentskills.io) that restructures a writer's own words into
  LinkedIn posts and blog articles. It never adds words of its own; missing material becomes `[GAP: question]`s.
- **`check_words.py`**: verifies mechanically that a text uses only the writer's words (verbatim runs, whole clauses,
  a glue-word whitelist, `allow.txt`, `--section`, `--sources-only`).
- **Journal**: verbatim, append-only capture of voice dictations (`journal.py`), theme tagging, quietly noted
  candidates, monthly digests, and a critical **review** that rules ideas IN or OUT against `GOALS.md`.
- **Writing workflows**: bootstrap STYLE.md from samples, goals interview, new draft, interview, restructure,
  challenge, check, learn (feedback scoped `post` vs `preference`), update style, publish.
- **Private workspace**: `init_workspace.py` creates one (default `~/writing`) and never overwrites existing files.
- **`doctor.py`**: workspace health and privacy check. It fails if a git remote is a public GitHub repository.
- **Install paths**: `npx skills add` (Claude Code, Codex, Cursor and more), a Claude Code plugin and marketplace with
  15 slash commands, and a Pi package with the same commands.
- **Worked example** of a fictional writer covering the whole loop, kept honest by tests.
- Windows, macOS and Linux support, tested on Python 3.9 and 3.13.

[0.1.1]: https://github.com/franndeli/writing-coach/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/franndeli/writing-coach/releases/tag/v0.1.0
