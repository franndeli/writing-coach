# Journal & goals workflows

`rules.md` applies throughout. Run scripts from the workspace root. `<skill>` is the skill directory.
`J` is short for `python3 <skill>/scripts/journal.py`.

How memory scales: entries are **compressed when they're captured** (frontmatter tags, candidate quotes, monthly
digests), so later reviews read small files and open only the specific entries they need, using `rg` (or `grep`).
Never load the whole journal into context.

| Layer | File | Who writes it |
|---|---|---|
| Raw entries | `journal/YYYY/YYYY-MM-DD.md` (body) | the writer, verbatim, immutable |
| Tags | each entry's frontmatter | you, via `J tag` |
| Candidates | `journal/candidates.md` | you: short verbatim quotes plus links |
| Digests | `journal/rollups/YYYY-MM.md` | you, in your own words. Internal only, never quoted in posts. |

---

## Goals — set up GOALS.md

1. Read `GOALS.md`. If it's already set, ask what changed instead of starting over.
2. Interview in 2–3 short rounds. Infer and confirm rather than asking open questions where you can (STYLE.md and samples are evidence):
   - why they post, and what would make it worth the effort;
   - who they want to reach (roles, not demographics);
   - 3–5 topics they want to be known for, and topics they never post about (employer details, family, politics…);
   - per platform: the goal and a cadence they're comfortable with. Say explicitly that "rarely" is fine;
   - what success looks like (a conversation, an opportunity, clarity of thought, …).
3. Write `GOALS.md` concisely, using their phrasing where possible. Show it and save it after they confirm.

## Capture — record a dictation

1. Take the dictation exactly as given. Voice transcripts are messy (no punctuation, misheard words, filler).
   **Don't fix anything**: no typos, no punctuation, no removed filler.
2. Append it with a quoted heredoc so nothing gets altered:
   ```sh
   python3 <skill>/scripts/journal.py add <<'ENTRY'
   <dictation exactly as given>
   ENTRY
   ```
   This creates today's file if needed and adds a `## HH:MM` heading. Use `--date YYYY-MM-DD` for a past day.
3. Tag it. Run `J themes` to see existing theme names and **reuse them**. Only add a new theme when nothing fits.
   Then run `J tag --themes a,b --people x --projects y` (add `--date` if it isn't today). Keep themes short, kebab-case, 1–4 per entry.
4. Quietly note candidates. If a passage holds a concrete story, a lesson, a strong opinion, a surprising
   observation, or something that fits a topic in `GOALS.md`, add a row to `journal/candidates.md`: date, a short
   verbatim quote (≤ 30 words), a link to the entry, themes, status `open`. Most entries have **zero** candidates. That's normal.
5. Reply in one line: where it was saved and the themes. **Don't mention post ideas or candidates**, and don't suggest posting.
6. Monthly digest: if a previous month has entries but no `journal/rollups/YYYY-MM.md`, write one now (see Digest).

## Digest — monthly rollup

Write `journal/rollups/YYYY-MM.md`, starting with the line `> Internal digest written by the coach. Not the writer's words; never quote in posts.`
Include: the output of `J themes --month YYYY-MM`, 5–10 bullet summaries of what mattered (each linking to its entry),
recurring threads across weeks, and any candidates from that month. Keep it under ~400 words.

## Review journal — rule ideas IN or OUT

Input: a period (default: since `Last review` in `candidates.md`, otherwise the last 30 days).

1. If `GOALS.md` isn't set, say so and run Goals first. Read `GOALS.md` and the `STYLE.md` summary.
2. Gather small context first: `J candidates --status open`, `J themes --since <period>`, and digests that overlap the period.
3. Look for patterns: a theme that appears in ≥ 3 entries in the period is a signal. Use `rg` to open those entries
   and look for candidates that capture missed. Add them to `candidates.md`.
4. Judge each open candidate **strictly**. The default is OUT. It's IN only if **all** of these hold:
   - it serves a goal in `GOALS.md` and isn't in a "never" topic;
   - there's enough of the writer's own raw material (a concrete story, example or opinion, not just a vague feeling);
   - it sounds like something they'd post (`STYLE.md`) and repeats nothing already in `samples/` (check with `rg`);
   - a skeptical reader from their audience would care.
   Rule IN at most ~3 per review. Several weak candidates on the same theme can merge into one IN.
5. Report with numbered items:
   - **IN**: the goal it serves, 2–4 verbatim quotes with entry links, why it works, and what's missing, phrased
     as questions. Never write post prose or headlines.
   - **OUT**: a one-line reason each (off-goal, too thin, already posted, too private, not you…).
   - If nothing qualifies, say **"Nothing worth posting this period"** plainly, with the closest call and what would make it work.
6. Update each row's status in `candidates.md` (`in` / `out (<reason>)`) and set `Last review: YYYY-MM-DD` at the top.
7. The writer can overrule any verdict. Log that as feedback in `feedback/preferences.md` if it reveals a preference (e.g. key `journal-rule-in-<topic>`).

## Promote — candidate to draft

1. Create `drafts/<slug>/` (see `writing.md` → New draft).
2. Build `raw.md` only from **verbatim** passages of the linked journal entries: copy whole relevant paragraphs,
   not fragments. Put `<!-- from journal/YYYY/YYYY-MM-DD.md -->` above each passage.
3. Verify faithfulness: `python3 <skill>/scripts/check_words.py drafts/<slug>/raw.md --sources-only --source journal/YYYY/YYYY-MM-DD.md [...]`.
   It must pass with zero flags. If it doesn't, you altered the text: recopy.
4. Ask the writer to fill in `brief.md`. You may suggest which goal it serves, but they write it.
5. Set the candidate status to `in (draft: <slug>)`. Continue with Interview or Restructure (`writing.md`).
