# install-skills

The one plugin in this marketplace a stranger actually needs. `prd-workflow` and
`ado-workflow` both read `<repo-root>/.claude/project/adapter.md` and cannot run
without it — and nothing in a plugin install writes that file, because it holds
facts only the project knows. This plugin is what writes it.

Two modes, and only two, because these are the two jobs no distribution
mechanism can do for you:

- **`install <bundle>`** — bootstrap `<repo-root>/.claude/project/`: the adapter,
  the interview that fills it, and any gate the bundle offers.
- **`doctor`** — say when an install has rotted, in the failure classes that fail
  silently: a forked copy that looks like an install, a project-owned `_shared/`
  shadowing canonical, an adapter still carrying template placeholders, a gate
  pointer nobody wrote.

It **does not place skills.** The platform does that, and does it better.

## Layout

```
plugins/install-skills/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    install -> ../../../install        # symlink, see below
    install-skills/
      SKILL.md
      references/interview.md          # the adapter interview
      scripts/doctor.sh                # the repo's only executable
```

One skill, no agents, nothing at the plugin root. The inventory is **discovered
from the directory**, not listed in the manifest.

## Decisions

### It is its own plugin, not a skill inside a personal grab-bag

Every other skill here is Liam's. This one is the entry point for anyone adopting
the workflow, so requiring an `lk` install to reach it would have been wrong. It
earns its own catalog entry for the same reason it is the only skill in the repo
that ships an executable: it is infrastructure, not taste.

### `skills/install` is a symlink, exactly like `skills/_shared`

`SKILL.md` reaches its templates by relative path — `../install/bundles.md`,
`../install/adapter.template.md`, `../install/README.md` — and `doctor.sh`
reaches the same tree by inferring `<script>/../..` and appending `install/`.
Under the old top-level layout both resolved to the repo root's `install/`.

Packaging broke that twice over: `../install/` from
`plugins/install-skills/skills/install-skills/` would point at a directory that
does not exist, and in a plugin **cache copy** the repo's `install/` is not
present at all. The installer would have refused every bundle with a `BUNDLE`
error and `doctor` would have silently lost its templates.

The fix is `skills/install -> ../../../install`, mirroring what `skills/_shared`
already does. A symlinked directory inside `skills/` is **dereferenced into the
install cache**, so `../install/…` keeps resolving unchanged from the working
tree *and* from a cache copy. Not one path reference was rewritten.

`install/` stays at the repo root as the canonical copy this symlink points at,
the same way `_shared/` does. It is not moved and not duplicated.

### `doctor.sh` stays the only executable, and stays one script

Mechanical checks have to be deterministic; a check that gets paraphrased
differently on each run is not a check. Everything else in this repo is prose,
and stays prose.

Likewise the skill stays a **single generic engine**. Per-bundle data lives in
`install/bundles.md` and is read at runtime — there is no per-plugin installer,
and adding a bundle means editing that manifest, not forking this skill.

### The invocation is namespaced

A plugin namespaces every component it provides, so this reads
**`/install-skills:install-skills`**. The stutter is the cost of the plugin
name matching the skill name, and the plugin name is the one a stranger types
into `/plugin install` — so it wins.
