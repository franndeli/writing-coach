# Security & privacy

writing-coach handles very personal material: drafts and daily journal entries. Privacy bugs are treated as security bugs.

## What counts

- Anything that could make the coach write workspace content outside the workspace (into the skill folder, the tool repo, logs, or a remote).
- `doctor.py` failing to flag a public remote.
- Scripts that alter journal entries or `raw.md` instead of appending verbatim.
- Command injection through file names or dictation content.

## Reporting

Please **don't open a public issue**. Use GitHub's [private vulnerability reporting](https://github.com/franndeli/writing-coach/security/advisories/new).
You should get a response within a week.

## What this project can't protect

Your coding agent sends the files it reads to its model provider. Choose a provider (or a local model) you trust
with your journal, and keep your workspace's git remote private (`doctor.py` checks this).
