# writing-coach

A private writing coach that runs on [Pi](https://github.com/earendil-works/pi). It restructures my ideas into
LinkedIn posts and blog articles. **It changes the structure, never the words.**

> Keep this repo **private**. It contains unpublished drafts and personal writing.

## Layout

| Path | What it is |
|---|---|
| `AGENTS.md` | How the agent behaves (coaching rules). Auto-loaded by Pi. |
| `STYLE.md` | How I write: tone, rhythm, vocabulary, structure, LinkedIn vs blog. |
| `samples/linkedin/`, `samples/blog/` | My published writing. This is the style evidence. |
| `drafts/<slug>/` | Work in progress: `raw.md` (immutable), `brief.md`, `interview.md`, `structure.md`, finals. |
| `feedback/preferences.md` | Permanent writing preferences (candidates → promoted to STYLE.md). |
| `feedback/posts/<slug>.md` | Post-specific accept/reject log. |
| `tools/check_words.py` | Verifies a final text uses only my words. |
| `templates/` | Templates for drafts, samples and feedback. |
| `.agents/skills/writing-coach/` | The coaching workflows (Pi skill). |
| `.pi/prompts/` | Slash commands. |
| `goal-and-requirements.md` | Product spec for this repo. |

## Workflow

1. **Bootstrap**: drop 10–20 posts into `samples/` (see `templates/sample.md`), then run `/bootstrap-style`.
2. **Write**: run `/new-draft my-slug`, paste your brain dump into `drafts/my-slug/raw.md`, and fill in `brief.md`.
3. **Interview**: run `/interview my-slug`. Answer the questions in your own words.
4. **Restructure**: run `/restructure my-slug linkedin` (or `blog`). You get a structure built only from your sentences, plus `[GAP]` questions.
5. **Challenge**: run `/challenge my-slug` for a critique of the argument and structure.
6. **Finalize**: fill the gaps yourself and save `final-linkedin.md` / `final-blog.md`. Then run `/check my-slug`.
7. **Learn**: say "accept 2, reject 3: too corporate" (or run `/learn my-slug ...`). Every so often, run `/update-style`.
8. **Publish**: run `/publish my-slug linkedin` to copy the approved final into `samples/`.

Commands are prompt templates. Pi asks you to trust the project the first time you open it.

## Check words manually

```sh
python3 tools/check_words.py drafts/my-slug/final-linkedin.md --source drafts/my-slug
```
