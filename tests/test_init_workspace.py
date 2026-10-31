import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "writing-coach"
sys.path.insert(0, str(SKILL / "scripts"))
import init_workspace as iw  # noqa: E402

TEMPLATE = SKILL / "assets" / "workspace"


class InitWorkspaceTest(unittest.TestCase):
    def test_creates_full_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "writing"
            added, skipped = iw.init_workspace(ws, git=False)
            for rel in (".writing-coach", "AGENTS.md", "CLAUDE.md", "STYLE.md", "GOALS.md",
                        "journal/candidates.md", "templates/journal-entry.md", "templates/draft/raw.md"):
                self.assertTrue((ws / rel).exists(), rel)
            self.assertEqual(skipped, [])

    def test_never_overwrites_existing_data(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            (ws / "STYLE.md").write_text("my real style")
            (ws / "samples" / "linkedin").mkdir(parents=True)
            (ws / "samples" / "linkedin" / "post.md").write_text("mine")
            added, skipped = iw.init_workspace(ws, git=False)
            self.assertEqual((ws / "STYLE.md").read_text(), "my real style")
            self.assertIn(Path("STYLE.md"), skipped)
            self.assertFalse((ws / "samples" / "linkedin" / ".gitkeep").exists())

    def test_refuses_inside_skill(self):
        with self.assertRaises(ValueError):
            iw.init_workspace(TEMPLATE / "x", git=False)


class TemplateIsCleanTest(unittest.TestCase):
    """The public template must never contain anyone's personal writing."""

    def test_no_personal_content(self):
        for folder in ("samples/linkedin", "samples/blog", "drafts", "feedback/posts", "journal/rollups"):
            names = sorted(p.name for p in (TEMPLATE / folder).iterdir())
            self.assertEqual(names, [".gitkeep"], f"{folder} must only hold .gitkeep, found {names}")
        journal_files = sorted(p.name for p in (TEMPLATE / "journal").iterdir())
        self.assertEqual(journal_files, ["candidates.md", "rollups"])

    def test_profiles_are_unfilled(self):
        self.assertIn("Not generated yet", (TEMPLATE / "STYLE.md").read_text())
        self.assertIn("Not set yet", (TEMPLATE / "GOALS.md").read_text())
        prefs = (TEMPLATE / "feedback" / "preferences.md").read_text()
        table_rows = [l for l in prefs.splitlines() if l.startswith("|") and not l.startswith("|---") and "Key" not in l]
        self.assertEqual(table_rows, [])


if __name__ == "__main__":
    unittest.main()
