---
id: writing-coach
type: goal-and-requirements
title: Writing Coach
status: draft
---

# Writing Coach

An open-source AI coach that restructures a writer's ideas into stronger LinkedIn posts and blog articles. It changes the structure, never the words. It also keeps a voice-dictated journal and mines it critically for post ideas.

## Overview

A portable Agent Skill (Markdown rules and workflows plus dependency-free Python scripts) that works in any
skills-capable coding agent: Claude Code, Codex, Cursor, Pi, and others. The writer dictates their days and ideas.
The coach saves them verbatim, rules post ideas in or out against the writer's goals, interviews them, challenges
weak arguments, and proposes a better *structure* built only from their own sentences. Accepted and rejected
suggestions refine a written profile of how they write.

## Problem

General-purpose AI rewriting makes posts sound like AI. Writers want help with what to post, what to lead with,
what to cut, and where the logic is thin, while every published word stays theirs. Good material also sits unused
in daily experience because nobody records it or checks it against what the writer actually wants to say.

## Principles

- **The words are always the writer's.** The coach can reorder, cut, split, merge, and promote their sentences,
  and it can use a small whitelist of grammatical glue. Anything else becomes a `[GAP: …]` question. `check_words.py`
  verifies this mechanically. It is not left to the model's discipline.
- **The tool is public, the workspace is private.** The repo holds only the skill. Each writer's data (style, goals,
  samples, drafts, feedback, journal) lives in a separate private workspace that the tool never commits or publishes.
  A test keeps the bundled workspace template free of personal content.
- **Style is separate from coaching.** `STYLE.md` describes how the writer writes. The skill's `rules.md` (plus personal
  overrides in the workspace `AGENTS.md`) describes how the coach behaves. Either can change without touching the other.
- **Style is descriptive, not prescriptive.** The profile records how the writer writes, including phrases they'd
  never use. All samples count equally; older posts still represent the writer.
- **Post feedback ≠ preference.** Every feedback entry is scoped `post` or `preference`. Something only becomes a
  `STYLE.md` rule after 3 consistent decisions or an explicit "always/never", and only through an approved diff.
- **A critical filter, not an idea machine.** The journal is captured silently. Only when the writer asks does the
  review rule candidates IN (strict criteria, ~3 at most) or OUT. "Nothing worth posting" is an expected answer, and
  the coach never pushes to post more.
- **Raw text is immutable.** The coach never edits a draft's `raw.md` or a journal entry's body. Journal capture is
  append-only and verbatim, with no cleanup of dictation. Promoted drafts are verified verbatim against the journal.
- **Compress when capturing, not when searching.** Journal memory is layered: verbatim entries, frontmatter tags,
  a candidates list of short quotes, and monthly digests the coach writes (internal, never quoted in posts). Reviews
  read the small layers and open specific entries with text search. No vector database or embeddings: at about 600
  tokens a day, layered Markdown plus grep holds up, and any future index must be rebuildable from the Markdown.

## Capabilities

- **Init**: create or complete a private workspace from the template, without ever overwriting existing files.
- **Doctor**: check workspace health and privacy. It fails when a git remote is a public GitHub repo, and runs after init and before every journal review.
- **Goals**: interview the writer into `GOALS.md` (why they post, audience, topics they post about and never post about, per-platform cadence).
- **Capture**: save a dictation verbatim to the day's journal entry, tag its themes, and quietly note candidate quotes.
- **Review journal**: on request, rule candidates and recurring themes IN or OUT against `GOALS.md`, with verbatim quotes and reasons.
- **Promote**: turn an IN candidate into a draft whose `raw.md` holds verbatim journal passages.
- **Bootstrap**: analyze `samples/` and generate `STYLE.md`, citing examples.
- **Interview**: ask probing questions so that the writer supplies missing material in their own words.
- **Restructure**: propose a LinkedIn or blog structure from the writer's words, with `[GAP]`s.
- **Challenge**: critique arguments and structure, explaining each suggestion.
- **Verify**: `check_words.py` flags any word sequence the writer didn't write.
- **Learn**: log accept/reject decisions with scope, and propose `STYLE.md` updates from accumulated preferences.
- **Publish**: copy approved finals into `samples/` as new style evidence.
- **Worked example**: `examples/alex/`, a fictional writer covering the whole loop, kept honest by tests that run the same checks the coach enforces.

## Non-Goals

- No ghost-writing: the coach never produces publishable prose of its own.
- No auto-posting to LinkedIn or a blog.
- No standalone app, orchestration framework, or fine-tuning. It runs inside existing coding agents.
- No hosted service: nothing leaves the writer's machine except what their chosen model provider reads.

## Tech Notes

- **Distribution**: `skills/writing-coach/` follows the Agent Skills format (`SKILL.md` router, `references/`,
  `scripts/`, `assets/workspace/`). Install paths:
  - `npx skills add franndeli/writing-coach` (any agent);
  - the Claude Code plugin: the repo root is both the plugin and its own marketplace (`.claude-plugin/`, source `./`), and `commands/` use `$ARGUMENTS`;
  - `pi install git:github.com/franndeli/writing-coach`, which loads `prompts/` through the `pi` key in `package.json`;
  - a manual copy.
  Both command sets only point at skill workflows, and a test keeps them in sync. One version string lives in
  package.json, plugin.json, the SKILL.md `metadata.version` and the CHANGELOG, also enforced by a test.
- **Workspace**: found by its `.writing-coach` marker. Its `AGENTS.md` (plus a `CLAUDE.md` that imports it) tells
  any agent to load the skill. Created by `scripts/init_workspace.py`, default `~/writing`, local git.
- **Scripts**: Python 3.9+ with no dependencies, on macOS, Linux and Windows (CI covers all three). `check_words.py` (verbatim-run plus clause
  matching, glue whitelist, `allow.txt`, `--section`, `--sources-only`), `journal.py` (append-only `add`, `tag`, `themes`,
  `candidates`), `init_workspace.py`, and `doctor.py` (GitHub visibility via the unauthenticated API: 200 means public, 404 means private or missing).
  Scripts force UTF-8 output, accept a BOM, and write LF.
- **Capture goes through a file**: the agent writes the dictation with its own file-write tool, then runs `journal.py add --file
  <tmp> --delete`. This keeps the text exact on every OS. Heredocs were rejected because they break in PowerShell and when a
  dictation contains the delimiter line. Pi slash commands never take a dictation as an argument, because Pi's shell-like
  argument parsing would strip quotes and apostrophes. Claude Code passes `$ARGUMENTS` through unparsed, so inline dictation works there.
- MIT licensed. Tests: `python3 -m unittest discover -s tests`. Contributor rules are in CONTRIBUTING.md.
