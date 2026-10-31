# writing-coach

**An AI writing coach that changes the structure, never your words.**

Most AI writing help makes posts sound like AI. This coach does the opposite. It works on what to lead with,
what to cut, where the argument is thin, and which questions you haven't answered yet. Every word in the result
comes from you. When the structure needs something you haven't written, it asks you instead of writing it:

```
[GAP: bridge from the cost problem to the solution — what made you change your mind?]
```

A small checker script (`check_words.py`) verifies this mechanically. It flags any phrase in a final text that you
didn't write.

It also keeps a **journal**. Dictate your day and the coach saves it word for word. When you ask, it goes through
everything critically and rules post ideas **in or out** against your goals. "Nothing worth posting this week" is a
perfectly good answer.

It's an [Agent Skill](https://agentskills.io): plain Markdown plus dependency-free Python scripts. It works with
Claude Code, Codex, Cursor, Pi, OpenCode, Gemini CLI and any other agent that supports skills.

## How it works

```
public  ── this repo: the skill (rules, workflows, scripts, templates)
private ── your workspace, e.g. ~/writing (STYLE.md, GOALS.md, samples, drafts, feedback, journal)
```

Your writing never lives in this repo. Your workspace is a separate local git repo that only you control.

| File in your workspace | What it is |
|---|---|
| `STYLE.md` | How you write (tone, rhythm, vocabulary, structure, LinkedIn vs blog), with citations from your samples |
| `GOALS.md` | Why you post, audience, topics you post about and never post about |
| `samples/` | Your published posts. This is the style evidence. |
| `drafts/<slug>/` | `raw.md` (your brain dump, never edited), `interview.md`, `structure-*.md`, your `final-*.md` |
| `feedback/` | Accepted/rejected suggestions, scoped as **post** or **preference**, so one rejection doesn't become a rule |
| `journal/` | Your dictations, verbatim, plus candidate quotes and monthly digests |

## Install

**Any agent** (Claude Code, Codex, Cursor, …) via the [skills CLI](https://skills.sh):

```sh
npx skills add franndeli/writing-coach -g
```

**Pi** as a package. This also adds slash commands like `/journal`, `/review-journal`, `/restructure`:

```sh
pi install git:github.com/franndeli/writing-coach
```

**Manually**: copy `skills/writing-coach/` into your agent's skills folder (e.g. `~/.claude/skills/`, `~/.codex/skills/`).

## Get started

```sh
python3 <path-to-skill>/scripts/init_workspace.py ~/writing   # or ask your agent: "create my writing workspace"
cd ~/writing
```

Open your agent in `~/writing` and talk to it:

1. **"Set up my writing goals"**: a short interview that fills in `GOALS.md`.
2. Put 10–20 of your published posts in `samples/linkedin/` and `samples/blog/`, then say **"Analyze my samples and generate STYLE.md"**.
3. Every day (or whenever): **"Journal:"** followed by your dictation.
4. Weekly: **"Review my journal, is anything worth posting?"**
5. For an idea that's ruled in: **"Promote it to a draft"**, then **"Interview me"**, **"Restructure for LinkedIn"**, **"Challenge it"**.
6. Write the final yourself (filling the gaps), then **"Check my words"** and **"Publish"**.
7. Accept or reject suggestions by number. The coach learns, and proposes `STYLE.md` updates only after repeated, consistent feedback.

## Design decisions

- **Your words only.** Allowed operations: reorder, cut, split, merge, promote a line to a hook or title, and use a short list of glue words (`and`, `but`, `so`…). Everything else becomes a `[GAP]` question.
- **Style ≠ coaching.** `STYLE.md` describes how you write. The skill's `rules.md` describes how the coach behaves. Either can improve without touching the other.
- **No vector database.** Journal entries are compressed when you record them (tags, candidate quotes, monthly digests) and searched with plain text search. At around 600 tokens a day, that holds up for a long time. An index could come later, built from the Markdown and rebuildable.
- **Markdown + Git.** Portable across AI providers, and the history shows how your style evolves.

## Privacy

Your workspace stays on your machine unless you push it somewhere. Keep any remote **private**. Whatever model
provider your agent uses will read the files it works on. Your journal is the most sensitive part, so choose a
provider (or a local model) you're comfortable with.

## Development

```sh
python3 -m unittest discover -s tests
```

Contributions are welcome. Never include real personal writing in issues, PRs or the template (a test enforces this for the template).

## License

MIT
