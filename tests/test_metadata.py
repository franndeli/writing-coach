"""Release hygiene: one version everywhere, valid manifests, matching command sets, spec-compliant skill."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "writing-coach"


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


def frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "missing frontmatter"
    return m.group(1)


class MetadataTest(unittest.TestCase):
    def test_single_version_everywhere(self):
        versions = {
            "package.json": json.loads(read("package.json"))["version"],
            "plugin.json": json.loads(read(".claude-plugin/plugin.json"))["version"],
            "SKILL.md": re.search(r'version:\s*"([^"]+)"', frontmatter(read("skills/writing-coach/SKILL.md"))).group(1),
            "CHANGELOG.md": re.search(r"^## \[(\d+\.\d+\.\d+)\]", read("CHANGELOG.md"), re.M).group(1),
        }
        self.assertEqual(len(set(versions.values())), 1, versions)

    def test_marketplace_points_at_plugin(self):
        market = json.loads(read(".claude-plugin/marketplace.json"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))
        self.assertEqual([p["name"] for p in market["plugins"]], [plugin["name"]])
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_skill_frontmatter_is_spec_compliant(self):
        fm = frontmatter(read("skills/writing-coach/SKILL.md"))
        name = re.search(r"^name:\s*(\S+)", fm, re.M).group(1)
        desc = re.search(r"^description:\s*(.+)$", fm, re.M).group(1)
        self.assertEqual(name, SKILL_DIR.name)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(desc), 1024)

    def test_pi_prompts_and_claude_commands_match(self):
        prompts = sorted(p.name for p in (ROOT / "prompts").glob("*.md"))
        commands = sorted(p.name for p in (ROOT / "commands").glob("*.md"))
        self.assertEqual(prompts, commands)

    def test_commands_name_existing_workflows(self):
        skill = read("skills/writing-coach/SKILL.md")
        for folder in ("prompts", "commands"):
            for p in (ROOT / folder).glob("*.md"):
                m = re.search(r"\*\*([^*]+)\*\* workflow", p.read_text(encoding="utf-8"))
                if m:
                    self.assertIn(f"| {m.group(1)} |", skill, f"{folder}/{p.name} names unknown workflow {m.group(1)!r}")

    def test_referenced_scripts_exist(self):
        text = "\n".join(p.read_text(encoding="utf-8") for p in SKILL_DIR.rglob("*.md"))
        for script in set(re.findall(r"scripts/([a-z_]+\.py)", text)):
            self.assertTrue((SKILL_DIR / "scripts" / script).exists(), script)


if __name__ == "__main__":
    unittest.main()
