---
name: writing-coach
description: Coach me through turning raw ideas into LinkedIn posts and blog articles while keeping every word mine. Use for building STYLE.md from samples, starting a draft, interviewing, restructuring, challenging, checking words, logging accept/reject feedback, updating STYLE.md, or publishing a final into samples.
---

# Writing Coach workflows

`AGENTS.md` rules apply at every step, above all **Rule 1: my words only**. Paths are relative to the repo
root. `<slug>` is the draft folder name under `drafts/`.

Always read `STYLE.md` before coaching. If it still says "Not generated yet", say so and offer to run Bootstrap
first. Pick 2–4 relevant samples (same platform, similar topic) and read them for evidence.

---

## Bootstrap — generate STYLE.md

1. List `samples/linkedin/` and `samples/blog/`. If there are fewer than ~10 samples, warn me but continue if I agree.
2. Read **all** samples. Weight them equally, whatever their date.
3. Fill every section of `STYLE.md`. Each claim must:
   - be descriptive ("you open with a personal admission"), not prescriptive ("you should…");
   - cite at least one sample by path, with a short verbatim quote;
   - be something you can see across several samples, not a one-off.
4. "Words & phrases I'd never use": infer this only from clear absences (e.g. no corporate buzzwords anywhere) and mark it *(inferred)*.
5. In "LinkedIn vs blog", compare length, hooks, paragraphing, formatting, endings, and hashtags/emojis.
6. Show me the result as a diff and write it only after I approve. Keep the existing "Rules from feedback" section intact.

## New draft

1. Create `drafts/<slug>/` from `templates/draft/` (raw.md, brief.md, interview.md, allow.txt).
2. Tell me to write my brain dump in `raw.md` and fill in `brief.md`. Don't write in either file yourself.
   If I paste a brain dump into the chat, save it to `raw.md` **verbatim**, without fixing typos.

## Interview — get more of my words

1. Read `raw.md`, `brief.md` and the existing `interview.md`.
2. Find what's missing: the concrete example, the "so what", the stakes, the counter-argument, the moment
   I changed my mind, the specific number or name.
3. Append 3–5 questions to `interview.md`, each as a blockquote (`> Q<n>: …`). Ask one thing per question.
   Keep them open, never leading, and never offering wording.
4. Ask me to answer below each question as plain text, or in the chat. If I answer in the chat, paste my answers
   **verbatim** under the matching question.

## Restructure — build the post from my words

Input: `<slug>` and a platform (`linkedin` | `blog`).

1. Read `raw.md`, `brief.md`, `interview.md`, `STYLE.md` and 2–4 same-platform samples.
2. Decide the structure first and show it as a short outline: hook → argument beats → close. Explain each choice
   with evidence from `STYLE.md` or samples (AGENTS.md rule 3).
3. Build the text **only** from operations allowed by Rule 1. Where a beat has no material of mine, insert a `[GAP: question]`.
4. Write `drafts/<slug>/structure-<platform>.md` with these sections:
   - `## Outline` — beats and rationale
   - `## Text` — the restructured text with `[GAP]`s
   - `## Cuts` — what I cut and why, quoted, so I can restore anything
   - `## Grammar fixes` — every non-glue change, as `original → changed`, for my approval
   - `## Suggestions` — numbered, each with what, why, and evidence
5. Run `python3 tools/check_words.py drafts/<slug>/structure-<platform>.md --section Text` and report.
   Unfilled `[GAP]`s are expected at this stage. Any other flagged span is a Rule 1 violation: fix it before
   showing me, unless it's listed under Grammar fixes.
6. Show me the outline, the gaps, and the suggestion numbers. Don't produce a second alternative unless I ask.

## Challenge — critique the argument

1. Read the latest text: `final-*.md` if it exists, otherwise `structure-*.md`, otherwise `raw.md`.
2. Act as a skeptical target reader (from `brief.md`). Write `drafts/<slug>/review.md` with numbered points covering:
   - the core claim in one line, quoted from my words; if you can't find one, that's point 1;
   - unsupported claims, logical gaps, missing counter-arguments;
   - the buried lead, too many ideas, a weak close, a mismatch with the platform;
   - where it sounds unlike me compared to `STYLE.md` (cite samples).
3. Each point is a question or an observation, never replacement prose.

## Check — verify the words

Run `python3 tools/check_words.py drafts/<slug>/final-<platform>.md` and show the output. If a flagged span is a
grammar fix I approved, offer to add it to `allow.txt`. Never edit `final-*.md` yourself.

## Learn — log feedback

When I accept, reject or modify suggestions (e.g. "accept 1 and 3, reject 2: too salesy"):

1. Append one entry per decision to `feedback/posts/<slug>.md`, using `templates/feedback-entry.md`. Put my reason in **verbatim**.
2. Set the scope:
   - `preference` only if I say always/never/generally, or the reason is clearly about my writing in general;
   - otherwise `post`;
   - if you can't tell, ask me with one short question.
3. For `preference` entries, update `feedback/preferences.md`. Reuse an existing key if it's the same preference
   and increase its count, or add a new key with count 1. A contradicting decision resets the count to 0.
4. If a key reaches **3**, or I said always/never, tell me it's ready for promotion. Don't touch `STYLE.md` yet.

## Update style

1. Read `feedback/preferences.md`, plus any samples added since `STYLE.md` was last changed (`git log -1 -- STYLE.md`).
2. Propose a diff to `STYLE.md`: promote ready keys to "Rules from feedback" with links to the evidence, and
   refine descriptions with the new samples.
3. After I approve, apply the change and set those keys' status to `promoted` in `preferences.md`.
   Suggest a commit message like `style: <what changed>`.

## Publish

Input: `<slug>` and a platform.

1. Run Check. Refuse to publish if anything is flagged, unless I explicitly override.
2. Copy `drafts/<slug>/final-<platform>.md` to `samples/<platform>/<YYYY-MM-DD>-<slug>.md`, with frontmatter from
   `templates/sample.md`. Ask me for the URL if there is one.
3. Suggest committing the draft folder, the feedback, and the new sample together.
