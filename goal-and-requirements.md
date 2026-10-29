---
id: writing-coach
type: goal-and-requirements
title: Writing Coach
status: draft
---

# Writing Coach

An AI coach that restructures my ideas into stronger LinkedIn posts and blog articles. It changes the structure, never the words.

## Overview

A private Git repo of Markdown files that an agentic CLI (Pi) works on. I dump raw ideas. The agent
interviews me, challenges weak arguments, and proposes a better *structure* built only from my own
sentences. Accepted and rejected suggestions are logged, and over time they refine a written profile of
how I write.

## Problem

General-purpose AI rewriting makes my posts sound like AI. I want help with argument and structure: what
to lead with, what to cut, where the logic is thin. But I want every published word to be mine.

## Principles

- **The words are always mine.** The agent can reorder, cut, split, merge, and promote my sentences, and
  it can use a small whitelist of grammatical glue. Anything else it needs becomes a `[GAP: …]` question
  that I answer in my own words. A checker script verifies this mechanically. It is not left to the
  model's discipline.
- **Style is separate from coaching.** `STYLE.md` describes how I write. `AGENTS.md` describes how the agent
  behaves. Either can change without touching the other.
- **Style is descriptive, not prescriptive.** The profile records how I write today, including phrases I'd
  never use, and it may evolve. All samples count equally; older posts still sound like me.
- **Post feedback ≠ preference.** Every feedback entry is scoped `post` or `preference`. Something only
  becomes a `STYLE.md` rule after repeated consistent decisions or an explicit "always/never" from me, and
  only through a diff I approve.
- **Raw drafts are immutable.** The agent never edits `raw.md`. Git diffs show exactly what it did.

## Capabilities

- **Bootstrap**: analyze `samples/` and generate `STYLE.md`, citing examples.
- **Interview**: ask probing questions so that I supply missing material in my own words.
- **Restructure**: propose a LinkedIn and/or blog structure from `raw.md` plus my interview answers, with `[GAP]`s.
- **Challenge**: critique arguments and structure, explaining each suggestion.
- **Verify**: `tools/check_words.py` flags any word sequence in a final text that I didn't write.
- **Learn**: log accept/reject decisions with scope, and propose `STYLE.md` updates from accumulated preferences.
- **Publish**: copy approved finals into `samples/` as new style evidence.

## Non-Goals

- No vector database, embeddings, orchestration framework, fine-tuning, or standalone app.
- No ghost-writing: the agent never produces publishable prose of its own.
- No auto-posting to LinkedIn or the blog.

## Tech Notes

Markdown and Git, private repo. Pi is the agent: a project skill in `.agents/skills/writing-coach/`, prompt
commands in `.pi/prompts/`, and `AGENTS.md` loaded automatically. The checker is dependency-free Python 3.
Everything stays portable across AI providers.
