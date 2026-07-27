# prd-workflow

The PRD-to-merge workflow, packaged as a Claude Code plugin: `to-prd` →
`to-issues` → `next-prd-issue` → `work-on-prd` / `work-on-issue`, plus the
`prd-worker` agent that `work-on-prd` spawns per child issue.

`deep-grill` is deliberately **not** in this plugin — it is a plain top-level
skill in this repo and stays one.

## Layout

```
plugins/prd-workflow/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    to-prd/  to-issues/  next-prd-issue/  work-on-prd/  work-on-issue/
  agents/prd-worker.md
```

Nothing sits at the plugin root. A directory holding both a root `SKILL.md`
and a `skills/` subdirectory registers **twice** — once as a plain skill, once
as a plugin skill — and pays always-on token cost for both.

## Decisions

### No `version` in `plugin.json`

With a `version` set it becomes the install cache key, and a forgotten bump
means installs silently never see changes. Omitting it means every install
resolves fresh.

The cost is that `claude plugin validate --strict` cannot pass: a missing
`version` is a warning, and `--strict` turns warnings into errors. Plain
`claude plugin validate` passes ("Validation passed with warnings"), and the
missing `version` is the *only* warning — adding a version to an otherwise
identical manifest makes `--strict` pass clean. So the strict run is a
known, single-cause failure, not an unvalidated manifest.

### The shared reference lives at `skills/_shared`

`skills/_shared` is a symlink to the repo's single canonical `_shared/`
(`../../../_shared`). Every skill's existing `../_shared/…` reference keeps
resolving with zero rewrites, in both delivery modes: live through the symlink
in skills-dir mode, and inside the tree in marketplace mode (a marketplace
clone of this repo carries the root `_shared/` the link points at).

The alternative was `plugins/prd-workflow/_shared` plus rewriting every
reference to `../../_shared/`. It was not needed: `claude plugin details`
reports **Skills (5), Agents (1)** with the symlink in place, so a non-skill
directory under `skills/` does *not* register as a phantom component. Measured,
not assumed — later slices of PRD #16 depend on this shape.

### Compat shims

The five top-level directory names in this repo survive as symlinks into
`skills/`, so the ~22 consumer symlinks across four repos keep resolving with
no coordinated update. One of them is nested: `neonplace` and `neonplace-ios`
link `work-on-prd/agents/prd-worker.md`, so
`skills/work-on-prd/agents/prd-worker.md` is a symlink back to
`../../../agents/prd-worker.md`. Removing either shim shape is a separate,
coordinated slice.
