import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_words as cw  # noqa: E402

GLUE = cw.load_glue()

RAW = """I quit my job last year. Honestly, it was terrifying.

Most managers think meetings are productive. They are not.
The real cost is context switching, not the hour itself.
Why? Because deep work dies in fragments.
"""


def run(final, *sources):
    src = cw.build_source([cw.strip_markdown(s) for s in (sources or (RAW,))], GLUE)
    findings, total, flagged = cw.check_text(final, src, GLUE)
    return findings, flagged


class CheckWordsTest(unittest.TestCase):
    def test_reordered_sentences_pass(self):
        final = "Deep work dies in fragments.\n\nThe real cost is context switching, not the hour itself."
        findings, flagged = run(final)
        self.assertEqual(flagged, 0, findings)

    def test_merge_with_glue_passes(self):
        final = "Most managers think meetings are productive, but they are not."
        self.assertEqual(run(final)[1], 0)

    def test_short_whole_clause_passes(self):
        final = "Why? Honestly, it was terrifying."
        self.assertEqual(run(final)[1], 0)

    def test_invented_transition_flagged(self):
        final = "Here's the thing nobody tells you: deep work dies in fragments."
        findings, flagged = run(final)
        self.assertGreater(flagged, 0)
        self.assertIn("here's", findings[0].flagged[0])

    def test_synonym_swap_flagged(self):
        final = "Most managers believe meetings are productive."
        findings, flagged = run(final)
        self.assertGreaterEqual(flagged, 1)
        self.assertTrue(any("believe" in s for s in findings[0].flagged))

    def test_word_salad_from_my_vocabulary_flagged(self):
        # Single words of mine glued together are not my sentences.
        final = "Managers quit meetings."
        self.assertGreater(run(final)[1], 0)

    def test_unfilled_gap_flagged(self):
        final = "Deep work dies in fragments. [GAP: what changed your mind?]"
        findings, _ = run(final)
        self.assertTrue(any("unfilled" in s for s in findings[0].flagged))

    def test_markdown_and_curly_quotes_ignored(self):
        final = "## Deep work dies in fragments\n\n- **Honestly**, it was terrifying.\n- They’re not… wait: they are not."
        findings, flagged = run(final, RAW.replace("They are not.", "They are not. They're not."))
        # "wait" is not mine
        self.assertEqual(flagged, 1, findings)

    def test_interview_questions_not_counted_but_answers_are(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "raw.md").write_text("Meetings kill focus.\n")
            (d / "interview.md").write_text("> Q1: What is the hidden cost nobody measures?\n\nThe cost is attention.\n")
            src = cw.build_source(cw.collect_sources(d, []), GLUE)
            ok = cw.check_text("Meetings kill focus. The cost is attention.", src, GLUE)
            bad = cw.check_text("What is the hidden cost nobody measures?", src, GLUE)
            self.assertEqual(ok[2], 0)
            self.assertGreater(bad[2], 0)

    def test_allow_txt_counts_as_mine(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "raw.md").write_text("I quits my job.\n")
            (d / "allow.txt").write_text("# approved fixes\nI quit my job\n")
            src = cw.build_source(cw.collect_sources(d, []), GLUE)
            self.assertEqual(cw.check_text("I quit my job.", src, GLUE)[2], 0)

    def test_section_only_checks_text(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "raw.md").write_text(RAW)
            (d / "structure-linkedin.md").write_text(
                "## Outline\nHook first because invented rationale.\n\n"
                "## Text\nDeep work dies in fragments.\n\n"
                "## Suggestions\n1. Lead with the cost.\n"
            )
            f = str(d / "structure-linkedin.md")
            self.assertEqual(cw.main([f, "--section", "Text"]), 0)
            self.assertEqual(cw.main([f]), 1)
            self.assertEqual(cw.main([f, "--section", "Missing"]), 2)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "raw.md").write_text(RAW)
            (d / "final.md").write_text("Deep work dies in fragments.\n")
            self.assertEqual(cw.main([str(d / "final.md")]), 0)
            (d / "final.md").write_text("Deep work truly dies in tiny fragments.\n")
            self.assertEqual(cw.main([str(d / "final.md")]), 1)


if __name__ == "__main__":
    unittest.main()
