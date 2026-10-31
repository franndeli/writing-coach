import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "writing-coach" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import doctor  # noqa: E402
import init_workspace as iw  # noqa: E402


def levels(results):
    return [lvl for lvl, _ in results]


class DoctorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        iw.init_workspace(self.ws, git=False)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.ws, check=True, capture_output=True)

    def test_parse_github_urls(self):
        for url in ("https://github.com/a/b.git", "https://github.com/a/b", "git@github.com:a/b.git",
                    "ssh://git@github.com/a/b.git"):
            self.assertEqual(doctor.parse_github(url), ("a", "b"), url)
        self.assertIsNone(doctor.parse_github("https://gitlab.com/a/b.git"))

    def test_local_only_repo_is_ok(self):
        self.git("init", "-q")
        self.assertEqual(levels(doctor.check_privacy(self.ws, offline=False)), ["ok"])

    def test_public_remote_fails(self):
        self.git("init", "-q")
        self.git("remote", "add", "origin", "git@github.com:someone/writing.git")
        res = doctor.check_privacy(self.ws, offline=False, visibility=lambda o, r: "public")
        self.assertEqual(levels(res), ["FAIL"])
        self.assertIn("--visibility private", res[0][1])

    def test_private_remote_ok_and_unknown_warns(self):
        self.git("init", "-q")
        self.git("remote", "add", "origin", "https://github.com/someone/writing.git")
        self.assertEqual(levels(doctor.check_privacy(self.ws, False, lambda o, r: "private-or-missing")), ["ok"])
        self.assertEqual(levels(doctor.check_privacy(self.ws, False, lambda o, r: "unknown")), ["warn"])
        self.assertEqual(levels(doctor.check_privacy(self.ws, True, lambda o, r: "public")), ["warn"])  # offline

    def test_non_github_remote_warns(self):
        self.git("init", "-q")
        self.git("remote", "add", "backup", "https://gitlab.com/someone/writing.git")
        self.assertEqual(levels(doctor.check_privacy(self.ws, False, lambda o, r: "public")), ["warn"])

    def test_missing_template_files_detected(self):
        self.assertEqual(levels(doctor.check_template_files(self.ws)), ["ok"])
        (self.ws / "GOALS.md").unlink()
        res = doctor.check_template_files(self.ws)
        self.assertEqual(levels(res), ["warn"])
        self.assertIn("GOALS.md", res[0][1])

    def test_profiles_and_journal(self):
        res = doctor.check_profiles(self.ws)
        self.assertEqual(levels(res), ["info", "info", "info"])
        entry = self.ws / "journal" / "2026" / "2026-01-05.md"
        entry.parent.mkdir(parents=True)
        entry.write_text("---\ndate: 2026-01-05\nthemes: []\n---\n\n## 09:00\n\nhello\n", encoding="utf-8")
        cand = self.ws / "journal" / "candidates.md"
        cand.write_text(cand.read_text(encoding="utf-8").replace("Last review: never", "Last review: 2026-01-01"), encoding="utf-8")
        res = doctor.check_journal(self.ws, today=date(2026, 1, 11))
        self.assertEqual(levels(res), ["ok", "warn", "info"])
        self.assertIn("10 day(s)", res[2][1])

    def test_outside_workspace_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(doctor.find_workspace(Path(d)))
        self.assertIn("FAIL", levels(doctor.run(None)))


if __name__ == "__main__":
    unittest.main()
