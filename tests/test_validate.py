"""The validator on a minimal marketplace, then on the ways a change breaks it."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402

DESCRIPTION = "Integra el servicio de ejemplo. Usar para probar el validador."
# Length of a key body that the validator treats as real; the key itself is built at
# runtime so nothing key-shaped sits in this file or in its bytecode.
KEY_BODY = 24


def write_plugin(root: Path, name: str, skills: tuple[str, ...], version: str = "0.1.0") -> None:
    plugin = root / "plugins" / name
    (plugin / ".claude-plugin").mkdir(parents=True)
    manifest = {"name": name, "version": version, "description": DESCRIPTION}
    (plugin / "plugin.json").write_text(json.dumps({"$schema": validate.AGENT_PLUGINS_SCHEMA, **manifest}))
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest))
    for skill_name in skills:
        skill = plugin / "skills" / skill_name
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: " + skill_name + "\ndescription: " + DESCRIPTION + "\nmetadata:\n  version: \"" + version
            + "\"\n---\n# Demo\n\nLee [la guía](references/guide.md) y usa `sk_live_...` como placeholder.\n")
        (skill / "references" / "guide.md").write_text("# Guía\n\nVuelve a [SKILL.md](../SKILL.md).\n")


def minimal_marketplace(root: Path) -> None:
    """The platform plugin, with two skills, and one product."""
    (root / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "demo", "owner": {"name": "Demo"},
        "plugins": [
            {"name": "platform", "source": "./plugins/platform", "description": DESCRIPTION,
             "version": "0.1.0", "category": "platform"},
            {"name": "demo", "source": "./plugins/demo", "description": DESCRIPTION,
             "version": "0.1.0", "category": "integration"},
        ],
    }))
    write_plugin(root, "platform", ("platform-overview", "platform-recipes"))
    write_plugin(root, "demo", ("demo-integration",))


class ValidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        minimal_marketplace(self.root)
        self.skill = self.root / "plugins" / "demo" / "skills" / "demo-integration"

    def tearDown(self) -> None:
        shutil.rmtree(self.root)

    def run_validator(self) -> int:
        return validate.main(["--root", str(self.root)])

    def test_minimal_marketplace_is_valid(self) -> None:
        self.assertEqual(self.run_validator(), 0)

    def test_missing_metadata_version_fails(self) -> None:
        skill_md = self.skill / "SKILL.md"
        skill_md.write_text(skill_md.read_text().replace("metadata:\n  version: \"0.1.0\"\n", ""))
        self.assertEqual(self.run_validator(), 1)

    def test_version_disagreement_fails(self) -> None:
        manifest = self.root / "plugins" / "demo" / "plugin.json"
        manifest.write_text(manifest.read_text().replace("0.1.0", "0.2.0"))
        self.assertEqual(self.run_validator(), 1)

    def test_broken_link_in_a_reference_fails(self) -> None:
        (self.skill / "references" / "guide.md").write_text("Ver [nada](missing.md).\n")
        self.assertEqual(self.run_validator(), 1)

    def test_credential_in_a_skill_fails(self) -> None:
        fake_key = "sk_live_" + "a" * KEY_BODY
        (self.skill / "references" / "guide.md").write_text(f"X-API-Key: {fake_key}\n")
        self.assertEqual(self.run_validator(), 1)

    def catalogue(self) -> dict:
        return json.loads((self.root / ".claude-plugin" / "marketplace.json").read_text())

    def write_catalogue(self, value: dict) -> None:
        (self.root / ".claude-plugin" / "marketplace.json").write_text(json.dumps(value))

    def test_skill_not_named_after_its_plugin_fails(self) -> None:
        renamed = self.skill.parent / "other-integration"
        self.skill.rename(renamed)
        skill_md = renamed / "SKILL.md"
        skill_md.write_text(skill_md.read_text().replace("demo-integration", "other-integration"))
        self.assertEqual(self.run_validator(), 1)

    def test_unknown_category_fails(self) -> None:
        catalogue = self.catalogue()
        catalogue["plugins"][1]["category"] = "tools"
        self.write_catalogue(catalogue)
        self.assertEqual(self.run_validator(), 1)

    def test_product_with_platform_category_fails(self) -> None:
        catalogue = self.catalogue()
        catalogue["plugins"][1]["category"] = "platform"
        self.write_catalogue(catalogue)
        self.assertEqual(self.run_validator(), 1)

    def test_missing_platform_plugin_fails(self) -> None:
        catalogue = self.catalogue()
        catalogue["plugins"] = catalogue["plugins"][1:]
        self.write_catalogue(catalogue)
        shutil.rmtree(self.root / "plugins" / "platform")
        self.assertEqual(self.run_validator(), 1)

    def test_every_skill_of_a_plugin_carries_its_version(self) -> None:
        skill_md = self.root / "plugins" / "platform" / "skills" / "platform-recipes" / "SKILL.md"
        skill_md.write_text(skill_md.read_text().replace("0.1.0", "0.2.0"))
        self.assertEqual(self.run_validator(), 1)

    def test_preview_status_is_allowed(self) -> None:
        skill_md = self.skill / "SKILL.md"
        skill_md.write_text(skill_md.read_text().replace("metadata:\n", "metadata:\n  status: \"preview\"\n"))
        self.assertEqual(self.run_validator(), 0)

    def test_unknown_status_fails(self) -> None:
        skill_md = self.skill / "SKILL.md"
        skill_md.write_text(skill_md.read_text().replace("metadata:\n", "metadata:\n  status: \"beta\"\n"))
        self.assertEqual(self.run_validator(), 1)

    def test_placeholder_key_is_allowed(self) -> None:
        (self.skill / "references" / "guide.md").write_text("X-API-Key: sk_live_...\n")
        self.assertEqual(self.run_validator(), 0)


class InstallTests(unittest.TestCase):
    """scripts/install.sh from a local checkout: the repository itself."""

    def setUp(self) -> None:
        self.dest = Path(tempfile.mkdtemp())
        self.repo = Path(__file__).resolve().parent.parent

    def tearDown(self) -> None:
        shutil.rmtree(self.dest)

    def install(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["sh", str(self.repo / "scripts" / "install.sh"), "--from", str(self.repo), "--dest", str(self.dest), *args],
            capture_output=True, text=True)

    def test_installs_every_skill_of_a_plugin(self) -> None:
        self.assertEqual(self.install("platform").returncode, 0)
        for skill in (self.repo / "plugins" / "platform" / "skills").iterdir():
            self.assertTrue((self.dest / skill.name / "SKILL.md").is_file(), skill.name)

    def test_all_installs_every_plugin(self) -> None:
        self.assertEqual(self.install("all").returncode, 0)
        expected = {p.parent.name for p in (self.repo / "plugins").glob("*/skills/*/SKILL.md")}
        self.assertEqual({p.name for p in self.dest.iterdir()}, expected)

    def test_reinstall_drops_files_removed_upstream(self) -> None:
        self.install("accounts")
        stale = self.dest / "accounts-integration" / "stale.md"
        stale.write_text("old")
        self.install("accounts")
        self.assertFalse(stale.exists())

    def test_unknown_plugin_fails(self) -> None:
        self.assertNotEqual(self.install("nope").returncode, 0)

    def test_path_in_plugin_name_fails(self) -> None:
        self.assertNotEqual(self.install("../plugins").returncode, 0)


if __name__ == "__main__":
    unittest.main()
