"""The validator on a minimal marketplace, then on the ways a change breaks it."""

from __future__ import annotations

import json
import shutil
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


def minimal_marketplace(root: Path) -> None:
    skill = root / "plugins" / "demo" / "skills" / "demo-integration"
    (skill / "references").mkdir(parents=True)
    (root / ".claude-plugin").mkdir()
    (root / "plugins" / "demo" / ".claude-plugin").mkdir()
    (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
        "name": "demo", "owner": {"name": "Demo"},
        "plugins": [{"name": "demo", "source": "./plugins/demo", "description": DESCRIPTION,
                     "version": "0.1.0", "category": "integration"}],
    }))
    manifest = {"name": "demo", "version": "0.1.0", "description": DESCRIPTION}
    (root / "plugins" / "demo" / "plugin.json").write_text(
        json.dumps({"$schema": validate.AGENT_PLUGINS_SCHEMA, **manifest}))
    (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest))
    (skill / "SKILL.md").write_text(
        "---\nname: demo-integration\ndescription: " + DESCRIPTION + "\nmetadata:\n  version: \"0.1.0\"\n---\n"
        "# Demo\n\nLee [la guía](references/guide.md) y usa `sk_live_...` como placeholder.\n")
    (skill / "references" / "guide.md").write_text("# Guía\n\nVuelve a [SKILL.md](../SKILL.md).\n")


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

    def test_placeholder_key_is_allowed(self) -> None:
        (self.skill / "references" / "guide.md").write_text("X-API-Key: sk_live_...\n")
        self.assertEqual(self.run_validator(), 0)


if __name__ == "__main__":
    unittest.main()
