#!/usr/bin/env python3
"""Validate the published catalog: marketplace, plugin manifests, skill frontmatter.

A malformed marketplace.json or a skill missing frontmatter breaks `plugin install`
for everyone who has added this marketplace, so these checks run on every PR.

Standard library only, by design — this repo has no dependency manifest and should
not grow one. Run it locally the same way CI does:

    python3 .github/scripts/validate_skills.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOP_KEY = re.compile(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$")
SHARED_REF = re.compile(r"_shared/([A-Za-z0-9._-]+\.md)")
BLOCK_SCALARS = {">", "|", ">-", "|-", ">+", "|+"}
# `../_shared/x.md` is this repo's shorthand for "some shared doc" (see CLAUDE.md),
# not a real filename. Prose uses it; don't try to resolve it.
SHARED_PLACEHOLDERS = {"x.md"}

errors: list[str] = []


def fail(where: Path | str, message: str) -> None:
    rel = os.path.relpath(where, ROOT) if isinstance(where, Path) else where
    errors.append(f"{rel}: {message}")


def walk_files(start: Path, name: str) -> list[Path]:
    """Find files named `name` under `start`, never descending into symlinked dirs."""
    found = []
    for dirpath, dirnames, filenames in os.walk(start, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        if name in filenames:
            found.append(Path(dirpath) / name)
    return sorted(found)


def read_frontmatter(path: Path) -> dict[str, str] | None:
    """Parse the leading YAML block. Returns None when there is no frontmatter."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return None

    fields: dict[str, str] = {}
    current: str | None = None
    for raw in lines[1:end]:
        match = TOP_KEY.match(raw) if not raw[:1].isspace() else None
        if match:
            current, value = match.group(1), match.group(2).strip()
            fields[current] = "" if value in BLOCK_SCALARS else value
        elif current and raw.strip():
            fields[current] = f"{fields[current]} {raw.strip()}".strip()
    return fields


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(path, "missing")
    except json.JSONDecodeError as exc:
        fail(path, f"invalid JSON — {exc}")
    return None


def check_marketplace() -> list[Path]:
    """Validate the catalog and return the plugin directories it points at."""
    manifest_path = ROOT / ".claude-plugin" / "marketplace.json"
    manifest = load_json(manifest_path)
    if manifest is None:
        return []

    for field in ("name", "description", "owner", "plugins"):
        if not manifest.get(field):
            fail(manifest_path, f"missing required field `{field}`")

    plugin_dirs: list[Path] = []
    seen: set[str] = set()
    for index, entry in enumerate(manifest.get("plugins") or []):
        label = entry.get("name") or f"plugins[{index}]"
        for field in ("name", "description", "source"):
            if not entry.get(field):
                fail(manifest_path, f"{label}: missing required field `{field}`")
        if entry.get("name") in seen:
            fail(manifest_path, f"{label}: duplicate plugin name")
        seen.add(entry.get("name", ""))

        source = entry.get("source")
        if not source:
            continue
        directory = (ROOT / source).resolve()
        if not directory.is_dir():
            fail(manifest_path, f"{label}: source `{source}` is not a directory")
            continue
        if directory.name != entry["name"]:
            fail(manifest_path, f"{label}: source directory is `{directory.name}`")
        plugin_dirs.append(directory)

    return plugin_dirs


def check_plugin_manifests(plugin_dirs: list[Path]) -> None:
    for directory in plugin_dirs:
        path = directory / ".claude-plugin" / "plugin.json"
        plugin = load_json(path)
        if plugin is None:
            continue
        for field in ("name", "description"):
            if not plugin.get(field):
                fail(path, f"missing required field `{field}`")
        if plugin.get("name") != directory.name:
            fail(path, f"name `{plugin.get('name')}` != directory `{directory.name}`")


def check_skills() -> None:
    """Every SKILL.md needs name + description, and names must be globally unique.

    Two skills sharing a name is the exact failure the plugins migration existed to
    end — the same skill discoverable under two routes.
    """
    owners: dict[str, Path] = {}
    for path in walk_files(ROOT, "SKILL.md"):
        fields = read_frontmatter(path)
        if fields is None:
            fail(path, "no YAML frontmatter block")
            continue
        for field in ("name", "description"):
            if not fields.get(field):
                fail(path, f"frontmatter missing or empty `{field}`")

        name = fields.get("name")
        if not name:
            continue
        if name != path.parent.name:
            fail(path, f"frontmatter name `{name}` != directory `{path.parent.name}`")
        if name in owners:
            other = os.path.relpath(owners[name], ROOT)
            fail(path, f"skill name `{name}` already claimed by {other}")
        owners[name] = path


def check_agents() -> None:
    """Agent frontmatter is what `subagent_type` resolves against.

    A missing or misnamed agent does not error at runtime — it degrades silently to
    general-purpose — so a broken agent file is invisible until behaviour is wrong.
    """
    seen: set[Path] = set()
    for plugin_dir in sorted((ROOT / "plugins").glob("*")):
        if not plugin_dir.is_dir():
            continue
        for path in sorted((plugin_dir / "agents").glob("*.md")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            fields = read_frontmatter(path)
            if fields is None:
                fail(path, "no YAML frontmatter block")
                continue
            for field in ("name", "description"):
                if not fields.get(field):
                    fail(path, f"frontmatter missing or empty `{field}`")
            if fields.get("name") and fields["name"] != path.stem:
                fail(path, f"frontmatter name `{fields['name']}` != filename `{path.stem}`")


def check_symlinks() -> None:
    """No broken links, nothing escaping the repo, and no top-level plugin shims."""
    for dirpath, dirnames, filenames in os.walk(ROOT, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for entry in dirnames + filenames:
            path = Path(dirpath) / entry
            if not path.is_symlink():
                continue
            if not path.exists():
                fail(path, f"broken symlink -> {os.readlink(path)}")
                continue
            resolved = path.resolve()
            if not resolved.is_relative_to(ROOT):
                fail(path, f"symlink escapes the repo -> {resolved}")
            elif path.parent == ROOT and resolved.is_relative_to(ROOT / "plugins"):
                fail(path, "top-level symlink into plugins/ — makes one skill "
                           "discoverable under two names (see CLAUDE.md)")


def check_shared_references() -> None:
    """`../_shared/x.md` pointers must resolve — a dead one silently drops guidance."""
    available = {p.name for p in (ROOT / "_shared").glob("*.md")}
    for path in walk_files(ROOT, "SKILL.md"):
        referenced = set(SHARED_REF.findall(path.read_text(encoding="utf-8")))
        for missing in sorted(referenced - available - SHARED_PLACEHOLDERS):
            fail(path, f"references _shared/{missing}, which does not exist")


def main() -> int:
    check_plugin_manifests(check_marketplace())
    check_skills()
    check_agents()
    check_symlinks()
    check_shared_references()

    if errors:
        print(f"✗ {len(errors)} problem(s) found:\n", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("✓ catalog, plugins, skills, agents, symlinks and _shared refs all valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
