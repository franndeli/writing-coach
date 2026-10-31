# Contributing

Thanks for helping! This project is small on purpose: Markdown instructions plus a few dependency-free Python scripts.

## Ground rules

1. **The core rule is sacred:** the coach never adds words of its own. Changes that weaken it (synonyms, "light
   polishing", generated hooks) won't be merged, even as options.
2. **Never include real personal writing**: not in issues, PRs, tests, or the template. Use invented text, like
   the fictional writer in `examples/alex/`. A test fails if the workspace template contains real content.
3. **No runtime dependencies.** Scripts run on a stock Python 3.9+ on macOS, Linux and Windows.
4. **Agent-agnostic.** Instructions must work in any skills-capable agent. Pi (`prompts/`) and Claude Code
   (`commands/`) commands only point at skill workflows, and both sets must stay in sync (a test enforces it).

## Layout

| Path | What it is |
|---|---|
| `skills/writing-coach/SKILL.md` | Router: find the workspace, load the rules, pick a workflow |
| `skills/writing-coach/references/` | `rules.md` (coaching rules), `writing.md` and `journal.md` (workflows) |
| `skills/writing-coach/scripts/` | `check_words.py`, `journal.py`, `init_workspace.py`, `doctor.py` |
| `skills/writing-coach/assets/workspace/` | Template copied into a new private workspace |
| `prompts/`, `commands/` | Pi and Claude Code slash commands |
| `examples/alex/` | Worked example (fictional) |
| `goal-and-requirements.md` | Product spec: principles and capabilities. Update it when they change. |

## Development

```sh
python3 -m unittest discover -s tests        # all tests
claude plugin validate . --strict            # if you touch .claude-plugin/
```

Try the skill against a scratch workspace:

```sh
python3 skills/writing-coach/scripts/init_workspace.py /tmp/ws
cd /tmp/ws && claude --plugin-dir /path/to/writing-coach   # or: pi -e /path/to/writing-coach
```

## Pull requests

- Keep each PR focused, and describe the behavior change from the writer's point of view.
- Update `CHANGELOG.md` (Unreleased section) and, if a principle or capability changes, `goal-and-requirements.md`.
- For a release, bump the version in `package.json`, `.claude-plugin/plugin.json`, the SKILL.md `metadata.version`,
  and `CHANGELOG.md`. A test checks they match.
