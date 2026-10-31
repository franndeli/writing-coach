"""Keep the worked example honest: it must pass the same checks the coach enforces."""
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "writing-coach" / "scripts"))
import check_words as cw  # noqa: E402

ALEX = ROOT / "examples" / "alex"
DRAFT = ALEX / "drafts" / "meetings-tax"
ENTRIES = sorted((ALEX / "journal" / "2026").glob("*.md"))


def check(*argv):
    with redirect_stdout(io.StringIO()) as out:
        code = cw.main([str(a) for a in argv])
    return code, out.getvalue()


class ExampleTest(unittest.TestCase):
    def test_final_uses_only_alexs_words(self):
        code, out = check(DRAFT / "final-linkedin.md")
        self.assertEqual(code, 0, out)

    def test_raw_is_verbatim_from_journal(self):
        args = [DRAFT / "raw.md", "--sources-only"]
        for e in ENTRIES:
            args += ["--source", e]
        code, out = check(*args)
        self.assertEqual(code, 0, out)

    def test_structure_text_only_flags_the_gap(self):
        code, out = check(DRAFT / "structure-linkedin.md", "--section", "Text")
        self.assertEqual(code, 1)
        self.assertIn("0 of", out)
        self.assertIn("unfilled [GAP", out)

    def test_example_is_fictional_and_marked(self):
        self.assertTrue((ALEX / ".writing-coach").exists())
        self.assertIn("fictional", (ROOT / "examples" / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
