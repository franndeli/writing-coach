# Developing writing-coach

This repo is the **public, open-source tool**. It never holds anyone's personal writing.

- The skill lives in `skills/writing-coach/` and must stay self-contained (portable Agent Skill):
  `SKILL.md` (router), `references/` (rules + workflows), `scripts/` (dependency-free Python 3), `assets/workspace/` (template).
- `prompts/` (Pi) and `commands/` (Claude Code, `$ARGUMENTS` only) are slash commands. They only point at skill workflows and must stay in sync.
- `.claude-plugin/` makes the repo root a Claude Code plugin and its own marketplace. Validate with `claude plugin validate . --strict`.
- `examples/alex/` is a fictional worked example. `tests/test_examples.py` keeps it passing the coach's own checks.
- Versions: package.json, plugin.json, SKILL.md `metadata.version` and CHANGELOG must match (`tests/test_metadata.py`).
- The product spec is `goal-and-requirements.md`. Update it when capabilities or principles change.
- Personal data (samples, drafts, feedback, journal, a filled STYLE.md/GOALS.md) belongs in a private workspace
  created by `scripts/init_workspace.py`, never here. `tests/test_init_workspace.py` enforces that the template stays clean.
- Run tests: `python3 -m unittest discover -s tests`.
