import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "writing-coach" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import init_workspace as iw  # noqa: E402
import journal as jr  # noqa: E402

DICTATION = """so um today was weird I'm not sure "quotes" stay... the meeting with the CTO
it's like we spend 80% of time aligning and 20% doing, que locura

and another thing $HOME `backticks` * stars"""


class JournalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        iw.init_workspace(self.ws, git=False)
        self.cwd = os.getcwd()
        os.chdir(self.ws / "drafts")  # commands work from any subfolder

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def run_cli(self, *argv, stdin=""):
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                code = jr.main(list(argv))
        finally:
            sys.stdin = old
        return code, out.getvalue()

    def test_add_is_verbatim_and_appends(self):
        self.run_cli("add", "--date", "2026-01-05", "--time", "09:10", stdin=DICTATION)
        self.run_cli("add", "--date", "2026-01-05", "--time", "18:30", stdin="second thought")
        text = (self.ws / "journal/2026/2026-01-05.md").read_text(encoding="utf-8")
        self.assertIn("## 09:10\n\n" + DICTATION + "\n", text)
        self.assertIn("## 18:30\n\nsecond thought\n", text)
        self.assertLess(text.index("09:10"), text.index("18:30"))

    def test_add_from_file_is_verbatim_and_deletes(self):
        tricky = "line one\nENTRY\n'@ \"@ `$env:HOME` caf\u00e9 \u2014 \u201cquoted\u201d\n"
        f = self.ws / "dictation.txt"
        f.write_bytes(("\ufeff" + tricky).encode("utf-8"))  # BOM, as Windows Notepad writes it
        code, out = self.run_cli("add", "--date", "2026-01-07", "--time", "07:00", "--file", str(f), "--delete")
        self.assertEqual(code, 0)
        self.assertFalse(f.exists())
        raw = (self.ws / "journal/2026/2026-01-07.md").read_bytes().decode("utf-8")
        self.assertIn("## 07:00\n\n" + tricky, raw)
        self.assertNotIn("\r", raw)
        self.assertNotIn("\ufeff", raw)

    def test_empty_add_refused(self):
        with self.assertRaises(SystemExit):
            self.run_cli("add", stdin="   \n")

    def test_tag_merges_and_keeps_body(self):
        self.run_cli("add", "--date", "2026-01-05", "--time", "09:10", stdin=DICTATION)
        self.run_cli("tag", "--date", "2026-01-05", "--themes", "meetings,leadership", "--people", "cto")
        self.run_cli("tag", "--date", "2026-01-05", "--themes", "meetings,focus")
        text = (self.ws / "journal/2026/2026-01-05.md").read_text(encoding="utf-8")
        meta, body = jr.read_frontmatter(text)
        self.assertEqual(meta["themes"], ["meetings", "leadership", "focus"])
        self.assertEqual(meta["people"], ["cto"])
        self.assertIn(DICTATION, body)

    def test_themes_counts_and_filters(self):
        for d, themes in (("2026-01-05", "meetings,focus"), ("2026-01-12", "meetings"), ("2026-02-02", "career")):
            self.run_cli("add", "--date", d, "--time", "08:00", stdin="x")
            self.run_cli("tag", "--date", d, "--themes", themes)
        rows = jr.theme_counts(self.ws)
        self.assertEqual(rows[0][:2], ("meetings", 2))
        self.assertEqual([t for t, _, _ in jr.theme_counts(self.ws, month="2026-02")], ["career"])
        self.assertEqual([t for t, _, _ in jr.theme_counts(self.ws, since=date(2026, 1, 10))], ["career", "meetings"])

    def test_candidates_filter(self):
        c = self.ws / "journal/candidates.md"
        c.write_text(c.read_text(encoding="utf-8").replace(
            "|---|---|---|---|---|",
            "|---|---|---|---|---|\n| 2026-01-05 | \"80% aligning\" | [e](2026/2026-01-05.md) | meetings | open |\n"
            "| 2026-01-06 | \"meh\" | [e](2026/2026-01-06.md) | misc | out (too thin) |"))
        self.assertEqual(len(jr.candidate_rows(self.ws)), 2)
        self.assertEqual(len(jr.candidate_rows(self.ws, "open")), 1)
        self.assertEqual(len(jr.candidate_rows(self.ws, "out")), 1)

    def test_outside_workspace_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SystemExit):
                jr.find_workspace(Path(d))


if __name__ == "__main__":
    unittest.main()
