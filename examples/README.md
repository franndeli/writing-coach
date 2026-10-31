# Worked example: Alex Rivera

Alex is a **fictional** engineering manager. This folder is a small workspace that shows the whole loop, from a messy
voice dictation to a published LinkedIn post. Every word of the final post is Alex's.

```
examples/alex/
├── GOALS.md, STYLE.md                 who Alex writes for, and how Alex writes
├── journal/2026/*.md                  three dictations, verbatim
├── journal/candidates.md              what the review ruled in or out
├── drafts/meetings-tax/
│   ├── raw.md                         verbatim journal passages (verified against the journal)
│   ├── interview.md                   the coach's questions, Alex's answers
│   ├── structure-linkedin.md          outline + text built only from Alex's words + one [GAP]
│   └── final-linkedin.md              Alex's final post
└── feedback/                          accepted/rejected suggestions; one became a permanent rule
```

## 1. Capture: Alex dictates on three different days

> ok so today's thing. we had the weekly sync and I counted, eleven people in the room for forty five minutes and like
> two decisions. two. and honestly nobody's fault, it's the format. I keep thinking we are paying a meeting tax that
> nobody approved. anyway also the new hire Priya shipped her first PR, that was nice

The coach saves it **exactly** like that ([2026-03-02.md](alex/journal/2026/2026-03-02.md)), tags it `meetings,
team-process`, quietly notes two candidate quotes, and replies with one line. It says nothing about posting.

## 2. Review: "is anything worth posting?"

A week later Alex asks for a review. The coach runs `journal.py themes` (`meetings` appeared in 3 entries) and checks
each candidate against [GOALS.md](alex/GOALS.md):

> **IN, 1 idea (3 candidates merged): the meeting tax experiment.**
> Serves the goal "team process that actually changed something". Your material: "we are paying a meeting tax that
> nobody approved" (03-02), "the meeting went from forty five minutes to fifteen" (03-05), "meetings that only do
> what writing can't" (03-09). Missing: what did those fifteen minutes actually decide? Is there a downside you're leaving out?
>
> **OUT: "the new hire Priya shipped her first PR".** It's about a report (GOALS → never), and it's a feeling, not a lesson.

## 3. Promote and interview

`raw.md` is built from **verbatim** journal paragraphs and verified with
`check_words.py raw.md --sources-only --source journal/...`. The coach then asks questions instead of writing
([interview.md](alex/drafts/meetings-tax/interview.md)):

> **Q1:** The fifteen minutes went to "the one hard problem". What did you actually decide in them?
>
> we decided to drop the custom deploy script and move to the standard pipeline. we'd been circling that for a month

## 4. Restructure: Alex's words in a better order, plus one gap

[structure-linkedin.md](alex/drafts/meetings-tax/structure-linkedin.md) explains each move (hook, evidence, experiment,
objection, result, reframe), lists every cut so it can be restored, and leaves the ending as a question for Alex:

```
[GAP: the post ends on the idea but gives the reader nothing to do. What would you want another manager to try on Monday?]
```

Alex answers in the interview file: *"cancel the status part of one meeting. just one. see what is left"*.

## 5. Final and check

[final-linkedin.md](alex/drafts/meetings-tax/final-linkedin.md):

> We are paying a meeting tax that nobody approved.
>
> Eleven people in the room for forty five minutes. Two decisions. Two.
>
> And honestly nobody's fault, it's the format.
>
> So I cancelled the status part of the sync and asked everyone to write a three line update in the channel before Monday.
>
> People were suspicious. Marco said it feels like we stopped talking.
>
> Fair point actually. But the meeting went from forty five minutes to fifteen, and we spent the fifteen on the one
> hard problem: we decided to drop the custom deploy script and move to the standard pipeline. We'd been circling that for a month.
>
> We didn't stop talking. We stopped reading status out loud to each other.
>
> The fix isn't fewer meetings, it's meetings that only do what writing can't. Arguing. Deciding. Feeling the room.
>
> Cancel the status part of one meeting. Just one. See what is left.

```console
$ python3 check_words.py drafts/meetings-tax/final-linkedin.md
✅ drafts/meetings-tax/final-linkedin.md: all 150 words are yours.
```

And this is what happens when an AI "polishes" it:

```console
$ python3 check_words.py drafts/meetings-tax/polished-by-ai.md
⚠️  drafts/meetings-tax/polished-by-ai.md: 8 of 36 words not found in your text.

  line 1: Meetings are silently draining our team's productivity.
      ✗ meetings
      ✗ silently draining our team's productivity
  line 5: Here's what I learned: the fix isn't fewer meetings, it's meetings that only do what writing can't.
      ✗ here's
      ✗ learned
```

## 6. Learn

Alex rejected an earlier suggestion with *"never end with a question to the audience, it's so linkedin"*. Because Alex
said "never", it was promoted straight to [STYLE.md](alex/STYLE.md) → *Rules from feedback*. The other decisions were
logged as `post`-scoped and changed nothing permanent ([feedback](alex/feedback/posts/meetings-tax.md)).

## Try it yourself

```sh
cd examples/alex
python3 ../../skills/writing-coach/scripts/journal.py themes
python3 ../../skills/writing-coach/scripts/check_words.py drafts/meetings-tax/final-linkedin.md
```
