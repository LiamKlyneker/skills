#!/usr/bin/env python3
"""Validate the published catalog: marketplace, plugin manifests, skill frontmatter.

A malformed marketplace.json or a skill missing frontmatter breaks `plugin install`
for everyone who has added this marketplace, so these checks run on every PR.

Standard library only, by design — this repo has no dependency manifest and should
not grow one. Run it locally with:

    python3 .github/scripts/validate_skills.py --base origin/main

One check needs a second commit to look at: `--base <ref>` (or `VALIDATE_BASE_REF`,
which is how the workflow passes the pull request's base SHA) switches on the
version-bump check, comparing each plugin's contents against that ref and demanding a
changed manifest `version` when they differ. With no base ref that one check reports
itself skipped and every other check still runs — which is what happens on a
`push: [main]` or `workflow_dispatch` run, where there is no base branch to compare to.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOP_KEY = re.compile(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$")
NESTED_KEY = re.compile(r"^\s+([A-Za-z0-9_-]+):[ \t]*(.*)$")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
SHARED_REF = re.compile(r"_shared/([A-Za-z0-9._-]+\.md)")
BLOCK_SCALARS = {">", "|", ">-", "|-", ">+", "|+"}
# `../_shared/x.md` is this repo's shorthand for "some shared doc" (see CLAUDE.md),
# not a real filename. Prose uses it; don't try to resolve it.
SHARED_PLACEHOLDERS = {"x.md"}

errors: list[str] = []


def relpath(path: Path) -> str:
    return os.path.relpath(path, ROOT)


def fail(where: Path | str, message: str) -> None:
    errors.append(f"{relpath(where) if isinstance(where, Path) else where}: {message}")


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


def read_metadata(path: Path) -> dict[str, str]:
    """The `metadata:` sub-block of a SKILL.md's frontmatter, as key → value.

    `read_frontmatter` deliberately folds every indented line into the key above it —
    that is what makes a `description: >` block read as one string — so a genuinely
    nested mapping needs its own small parse rather than a cleverer shared one, which
    would start splitting any description that happens to contain a colon.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return {}

    fields: dict[str, str] = {}
    inside = False
    for raw in lines[1:end]:
        if not raw[:1].isspace():
            inside = raw.strip() == "metadata:"
            continue
        match = NESTED_KEY.match(raw) if inside else None
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return fields


def parse_version(raw: str) -> tuple[int, int, int] | None:
    """`1.8.0` → `(1, 8, 0)`. Anything that is not a plain numeric triple → None."""
    match = SEMVER.match(raw.strip())
    if not match:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(path, "missing")
    except json.JSONDecodeError as exc:
        fail(path, f"invalid JSON — {exc}")
    return None


def git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run git inside the repo. `subprocess` is stdlib — nothing new gets depended on."""
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False
    )


def owning_plugin(path: Path) -> str | None:
    """Which `plugins/<name>` this path belongs to, or None if it is outside them."""
    if not path.is_relative_to(ROOT / "plugins"):
        return None
    parts = path.relative_to(ROOT / "plugins").parts
    return parts[0] if parts else None


def check_marketplace() -> list[tuple[Path, dict]]:
    """Validate the catalog and return (plugin directory, catalog entry) per plugin."""
    manifest_path = ROOT / ".claude-plugin" / "marketplace.json"
    manifest = load_json(manifest_path)
    if manifest is None:
        return []

    for field in ("name", "description", "owner", "plugins"):
        if not manifest.get(field):
            fail(manifest_path, f"missing required field `{field}`")

    entries: list[tuple[Path, dict]] = []
    seen: set[str] = set()
    for index, entry in enumerate(manifest.get("plugins") or []):
        label = entry.get("name") or f"plugins[{index}]"
        # `version` is required on both sides — it is the install cache key, and the
        # bump-or-fail check below has nothing to compare when it is absent.
        for field in ("name", "description", "source", "version"):
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
        entries.append((directory, entry))

    return entries


def check_plugin_manifests(entries: list[tuple[Path, dict]]) -> None:
    for directory, catalog_entry in entries:
        path = directory / ".claude-plugin" / "plugin.json"
        plugin = load_json(path)
        if plugin is None:
            continue
        for field in ("name", "description", "version"):
            if not plugin.get(field):
                fail(path, f"missing required field `{field}`")
        if plugin.get("name") != directory.name:
            fail(path, f"name `{plugin.get('name')}` != directory `{directory.name}`")
        # The catalog is what `plugin install` reads; the manifest is what the installed
        # copy reports back. When they disagree it is not knowable which one a consumer
        # is actually pinned to, so a bump has to land in both.
        catalog_version = catalog_entry.get("version")
        if plugin.get("version") and catalog_version and plugin["version"] != catalog_version:
            fail(path, f"version `{plugin['version']}` != marketplace.json "
                       f"`{catalog_version}` — a bump lands in both or neither")


def check_skills() -> None:
    """Every SKILL.md needs name + description, and names unique *within a plugin*.

    A skill is invoked namespaced — `prd-workflow:triage` — so the plugin is part of the
    name and two plugins may both ship a `triage` without ambiguity. What this rule
    protects is a *single* plugin's inventory: two directories inside one plugin claiming
    the same name give that plugin two skills reachable by one identifier, and which of
    them a session loads is undefined.

    It used to be global, justified as ending "the same skill discoverable under two
    routes". That is a symlink shape, not a name collision, and `check_symlinks` is what
    actually catches it — a top-level shim into `plugins/`, or a link under
    `.claude/skills/`. Globally-unique names only ever stopped two genuinely different
    skills, in different plugins, from picking the same obvious word.
    """
    # A SKILL.md outside `plugins/` has no owning plugin. Those share one bucket, so a
    # stray pair still collides with each other rather than crashing on a `None` key.
    # CLAUDE.md says no such skill exists here; this is what makes an accident report.
    outside = "\0outside-plugins"
    owners: dict[tuple[str, str], Path] = {}
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
        scope = owning_plugin(path) or outside
        if (scope, name) in owners:
            other = os.path.relpath(owners[(scope, name)], ROOT)
            where = f"plugin `{scope}`" if scope != outside else "outside `plugins/`"
            fail(path, f"skill name `{name}` already claimed by {other} — skill names "
                       f"must be unique within {where}")
        owners[(scope, name)] = path


def check_skill_versions(plugin_dirs: list[Path]) -> None:
    """A skill's `metadata.version` may never run ahead of the plugin that ships it.

    A consumer installs the *plugin*, at the plugin's `version`, and receives the skill
    files inside that one cache copy — so a skill stamped newer than its plugin describes
    a release nobody can install, and it does it silently. This repo has already had that
    drift once: a skill sat at 1.8.0 inside a plugin still claiming 1.4.0, and it was
    found by a human reading two files rather than by anything mechanical (#105).

    Equal is fine and is the common case. Older is fine too — a skill may simply not have
    changed since. Only *ahead* is a contradiction.
    """
    for directory in plugin_dirs:
        manifest = directory / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            continue  # check_plugin_manifests already reported the missing manifest
        try:
            declared = (json.loads(manifest.read_text(encoding="utf-8")) or {}).get("version") or ""
        except (json.JSONDecodeError, OSError):
            continue  # ditto — one problem, reported once

        stamped: list[tuple[Path, str]] = []
        for path in walk_files(directory, "SKILL.md"):
            version = read_metadata(path).get("version")
            if version:
                stamped.append((path, version))
        if not stamped:
            continue  # most skills carry no version of their own; nothing to compare

        plugin_version = parse_version(declared)
        if plugin_version is None:
            # Reported rather than skipped: a guard that quietly disables itself on a
            # malformed version is indistinguishable from one that passed.
            fail(manifest, f"version `{declared}` is not a numeric MAJOR.MINOR.PATCH — the "
                           f"skill-version guard has nothing to compare against")
            continue

        for path, raw in stamped:
            skill_version = parse_version(raw)
            if skill_version is None:
                fail(path, f"metadata.version `{raw}` is not a numeric MAJOR.MINOR.PATCH")
            elif skill_version > plugin_version:
                fail(path, f"skill `{path.parent.name}` metadata.version `{raw}` is ahead of "
                           f"plugin `{directory.name}` version `{declared}` — a skill ships "
                           f"inside its plugin, so the plugin's version is the one a consumer "
                           f"installs; bump `{directory.name}` (here and in marketplace.json) "
                           f"or lower the skill")


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
    """Packaging links are legal; links that make a skill *load* are not.

    Two different things get called a symlink here (ADR 0010):

    - **Packaging** — `plugins/*/skills/_shared`, `install-skills`' `skills/install`,
      and `figma-to-spec`'s agent link. Install dereferences these into each cache
      copy; they are build mechanics and they are required.
    - **Delivery** — a link that makes a plugin or skill load. Two shapes of it have
      existed here and both are now illegal: a *top-level* shim into `plugins/` (one
      skill discoverable under two names, #26), and a link under `.claude/skills/`
      into `plugins/` (this repo self-hosting itself, retired in favour of
      `claude --plugin-dir`). Prose alone would let either back in by habit.
    """
    claude_skills = ROOT / ".claude" / "skills"
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
            source, target = owning_plugin(path), owning_plugin(resolved)
            if not resolved.is_relative_to(ROOT):
                fail(path, f"symlink escapes the repo -> {resolved}")
            elif path.parent == ROOT and resolved.is_relative_to(ROOT / "plugins"):
                fail(path, "top-level symlink into plugins/ — makes one skill "
                           "discoverable under two names (see CLAUDE.md)")
            elif path.is_relative_to(claude_skills) and resolved.is_relative_to(ROOT / "plugins"):
                fail(path, "symlink under .claude/skills/ into plugins/ — the retired "
                           "self-host route; author with `claude --plugin-dir "
                           f"{relpath(resolved)}` instead (ADR 0010)")
            elif source and target and source != target:
                # Install dereferences the link, so this would publish one plugin's files
                # inside another — and edits to `target` would need `source` bumped too.
                fail(path, f"symlink from plugin `{source}` into plugin `{target}` — "
                           f"cross-plugin links make one edit change two published "
                           f"plugins; share via _shared/ instead")


def check_shared_references() -> None:
    """`../_shared/x.md` pointers must resolve — a dead one silently drops guidance."""
    available = {p.name for p in (ROOT / "_shared").glob("*.md")}
    for path in walk_files(ROOT, "SKILL.md"):
        referenced = set(SHARED_REF.findall(path.read_text(encoding="utf-8")))
        for missing in sorted(referenced - available - SHARED_PLACEHOLDERS):
            fail(path, f"references _shared/{missing}, which does not exist")


def plugin_pathspecs(directory: Path) -> list[str]:
    """Every path whose contents land inside this plugin's *installed* copy.

    A plugin's `skills/_shared` — and `install-skills`' second link, `skills/install` —
    is a symlink that install dereferences into the cache. So editing `_shared/` changes
    what every consumer receives, while `git diff` only ever names `_shared/…` and never
    the plugin. Those targets count as the plugin's own contents for the bump rule; the
    alternative is a shared-doc edit that silently ships to nobody.
    """
    specs = {relpath(directory)}
    for dirpath, dirnames, filenames in os.walk(directory, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for entry in dirnames + filenames:
            path = Path(dirpath) / entry
            if not path.is_symlink() or not path.exists():
                continue
            resolved = path.resolve()
            if resolved.is_relative_to(ROOT) and not resolved.is_relative_to(directory):
                specs.add(relpath(resolved))
    return sorted(specs)


def check_version_bumps(plugin_dirs: list[Path], base_ref: str) -> None:
    """Changed plugin contents must arrive with a changed manifest `version`.

    `version` is the install cache key. Observed on this repo: `claude plugin install`
    at a version already cached prints "already installed" and re-copies nothing, so a
    forgotten bump does not delay an update — it strands the consumer on stale files
    until they uninstall by hand. An unenforced bump rule is therefore worse than having
    no version at all, which is why this check is the thing that lets versions exist.
    """
    if not base_ref:
        # No base branch exists on a `push: [main]` or `workflow_dispatch` run, and
        # diffing a merged commit against itself means nothing. Skip out loud.
        print("⊘ version bumps: skipped — no base ref to compare against (pass "
              "--base <ref> or set VALIDATE_BASE_REF; a push or manual run has none)",
              flush=True)
        return

    resolved = git("rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}")
    if resolved.returncode != 0:
        fail("version bumps", f"base ref `{base_ref}` does not resolve to a commit — "
                              f"is the clone deep enough? (CI needs fetch-depth: 0)")
        return
    base = resolved.stdout.strip()
    # The fork point, not the base branch tip: if the base branch moved on after this
    # branch left it, its later commits are not this branch's changes to answer for.
    fork_point = git("merge-base", base, "HEAD")
    if fork_point.returncode == 0 and fork_point.stdout.strip():
        base = fork_point.stdout.strip()

    bumped: list[str] = []
    newly_versioned: list[str] = []
    unchanged: list[str] = []
    stale: list[str] = []
    for directory in plugin_dirs:
        manifest = directory / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            continue  # check_plugin_manifests already reported the missing manifest
        specs = plugin_pathspecs(directory)
        diff = git("diff", "--name-only", base, "--", *specs)
        if diff.returncode != 0:
            fail(manifest, f"could not diff against {base[:8]} — {diff.stderr.strip()}")
            continue
        # `git diff <commit> -- <paths>` compares the commit to the *working tree*, so an
        # uncommitted edit counts; untracked files are invisible to it and get added here.
        untracked = git("ls-files", "--others", "--exclude-standard", "--", *specs)
        changed = sorted({p for p in (diff.stdout + untracked.stdout).splitlines() if p})
        if not changed:
            unchanged.append(directory.name)
            continue

        current = (load_json(manifest) or {}).get("version")
        if not current:
            continue  # check_plugin_manifests already reported the missing version
        at_base = git("show", f"{base}:{relpath(manifest)}")
        if at_base.returncode != 0:
            newly_versioned.append(f"{directory.name}@{current} (new)")
            continue
        try:
            base_version = (json.loads(at_base.stdout) or {}).get("version")
        except json.JSONDecodeError:
            base_version = None
        if not base_version:
            newly_versioned.append(f"{directory.name}@{current} (unversioned at base)")
        elif base_version == current:
            stale.append(directory.name)
            preview = ", ".join(changed[:3])
            if len(changed) > 3:
                preview += f", +{len(changed) - 3} more"
            fail(manifest, f"plugin `{directory.name}` changed since {base[:8]} but "
                           f"`version` is still `{current}` — bump it in this manifest "
                           f"and in marketplace.json (changed: {preview})")
        else:
            bumped.append(f"{directory.name} {base_version}→{current}")

    def detail(names: list[str]) -> str:
        return f" ({', '.join(names)})" if names else ""

    mark = "✗" if stale else "✓"
    print(f"{mark} version bumps vs {base[:8]}: {len(bumped)} bumped{detail(bumped)} · "
          f"{len(newly_versioned)} exempt{detail(newly_versioned)} · "
          f"{len(unchanged)} unchanged · {len(stale)} missing a bump{detail(stale)}",
          flush=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--base",
        default=os.environ.get("VALIDATE_BASE_REF", ""),
        help="git ref to compare plugin contents against for the version-bump check; "
             "omit (or pass empty) to skip that one check",
    )
    args = parser.parse_args(argv)

    entries = check_marketplace()
    plugin_dirs = [directory for directory, _ in entries]
    check_plugin_manifests(entries)
    check_skills()
    check_skill_versions(plugin_dirs)
    check_agents()
    check_symlinks()
    check_shared_references()
    check_version_bumps(plugin_dirs, args.base)

    if errors:
        print(f"✗ {len(errors)} problem(s) found:\n", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("✓ catalog, plugins, skills, skill versions, agents, symlinks and _shared refs "
          "all valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
