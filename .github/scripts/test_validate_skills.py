#!/usr/bin/env python3
"""Fixture-driven tests for the checks `validate_skills.py` owns.

Standard library only — `unittest`, `tempfile`, `json` — for the same reason the validator
is: this repo has no dependency manifest and does not grow one to test itself.

    python3 .github/scripts/test_validate_skills.py

Each case builds a throwaway plugin tree in a temp directory and runs one check against it,
so a rule is asserted against a manifest that deliberately breaks it rather than against
whatever the real tree happens to contain today. The last case runs the guard over the real
plugins, which is the other half of the same question: the rule rejects what it should, and
this repo passes it.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate_skills.py"
_spec = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
assert _spec and _spec.loader
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)


def write_plugin(root: Path, name: str, version: str, skills: dict[str, str | None]) -> Path:
    """A throwaway plugin: one manifest, one SKILL.md per entry in `skills`.

    A skill's value is its `metadata.version`, or None for a skill carrying no metadata
    block at all — the shape almost every skill in this repo actually has.
    """
    directory = root / "plugins" / name
    (directory / ".claude-plugin").mkdir(parents=True)
    (directory / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": name, "description": "fixture", "version": version}),
        encoding="utf-8",
    )
    for skill_name, skill_version in skills.items():
        skill_dir = directory / "skills" / skill_name
        skill_dir.mkdir(parents=True)
        metadata = ""
        if skill_version is not None:
            metadata = f'metadata:\n  author: fixture\n  version: "{skill_version}"\n'
        skill_dir.joinpath("SKILL.md").write_text(
            "---\n"
            f"name: {skill_name}\n"
            "description: >\n"
            "  A fixture skill. Note the colon here: it must not confuse the parser.\n"
            f"{metadata}"
            "---\n\n"
            "Body.\n",
            encoding="utf-8",
        )
    return directory


class SkillVersionGuard(unittest.TestCase):
    """`metadata.version` must never exceed the plugin's `plugin.json` version."""

    def setUp(self) -> None:
        validate.errors.clear()
        self.addCleanup(validate.errors.clear)
        self.tmp = Path(tempfile.mkdtemp())
        self.runs = 0

    def run_guard(self, version: str, skills: dict[str, str | None]) -> list[str]:
        # A fresh sub-root per call, so a test may run the guard twice without the second
        # fixture landing on top of the first.
        self.runs += 1
        root = self.tmp / f"run-{self.runs}"
        directory = write_plugin(root, "fixture-plugin", version, skills)
        validate.check_skill_versions([directory])
        return list(validate.errors)

    def test_skill_ahead_of_plugin_is_rejected(self) -> None:
        errors = self.run_guard("1.2.0", {"drifted": "2.0.0"})
        self.assertEqual(len(errors), 1, errors)
        message = errors[0]
        # The message has to be actionable from the failure line alone: which skill, and
        # both versions. Reading two files to find out is the manual step this replaces.
        self.assertIn("drifted", message)
        self.assertIn("2.0.0", message)
        self.assertIn("1.2.0", message)
        self.assertIn("marketplace.json", message)

    def test_drift_in_any_component_is_rejected(self) -> None:
        # Not a string comparison: "1.10.0" > "1.9.0" numerically and "<" as text.
        self.assertEqual(len(self.run_guard("1.9.0", {"minor": "1.10.0"})), 1)
        validate.errors.clear()
        self.assertEqual(len(self.run_guard("1.2.3", {"patch": "1.2.4"})), 1)

    def test_equal_versions_pass(self) -> None:
        self.assertEqual(self.run_guard("1.8.0", {"pinned": "1.8.0"}), [])

    def test_skill_behind_plugin_passes(self) -> None:
        # A skill that simply hasn't changed since an unrelated bump is not drift.
        self.assertEqual(self.run_guard("2.0.0", {"trailing": "1.8.0"}), [])

    def test_skill_without_metadata_passes(self) -> None:
        self.assertEqual(self.run_guard("1.0.0", {"unstamped": None}), [])

    def test_only_the_drifted_skill_is_reported(self) -> None:
        errors = self.run_guard(
            "1.5.0", {"fine": "1.5.0", "ahead": "1.6.0", "unstamped": None}
        )
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("ahead", errors[0])
        self.assertNotIn("fine", errors[0])

    def test_unparseable_skill_version_is_reported(self) -> None:
        errors = self.run_guard("1.0.0", {"vague": "1.0"})
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("MAJOR.MINOR.PATCH", errors[0])

    def test_unparseable_plugin_version_is_reported_not_skipped(self) -> None:
        # A guard that silently disables itself reads exactly like one that passed.
        errors = self.run_guard("v1.0", {"stamped": "1.0.0"})
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("plugin.json", errors[0])
        self.assertIn("nothing to compare", errors[0])

    def test_unparseable_plugin_version_is_ignored_when_no_skill_is_stamped(self) -> None:
        # Nothing to guard, so nothing to say — `check_plugin_manifests` owns the manifest.
        self.assertEqual(self.run_guard("v1.0", {"unstamped": None}), [])

    def test_the_real_plugins_pass(self) -> None:
        plugin_dirs = sorted(
            d for d in (validate.ROOT / "plugins").glob("*") if d.is_dir()
        )
        self.assertTrue(plugin_dirs, "no plugins found — is ROOT resolved correctly?")
        validate.check_skill_versions(plugin_dirs)
        self.assertEqual(validate.errors, [])


class MetadataParsing(unittest.TestCase):
    """`read_metadata` reads the nested block without disturbing `read_frontmatter`."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def test_block_scalar_description_is_not_read_as_metadata(self) -> None:
        directory = write_plugin(self.tmp, "p", "1.0.0", {"s": "1.0.0"})
        path = directory / "skills" / "s" / "SKILL.md"
        self.assertEqual(validate.read_metadata(path), {"author": "fixture", "version": "1.0.0"})
        # The folded description survives as one string, colon and all.
        fields = validate.read_frontmatter(path)
        assert fields is not None
        self.assertIn("must not confuse the parser", fields["description"])

    def test_no_frontmatter_is_empty_not_an_error(self) -> None:
        path = self.tmp / "plain.md"
        path.write_text("# Just a document\n", encoding="utf-8")
        self.assertEqual(validate.read_metadata(path), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
