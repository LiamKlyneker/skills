# ado-workflow

The ADO half of the PRD workflow, packaged as a Claude Code plugin: `to-spec` →
`to-spec-tasks` → `next-task-to-implement` → `work-on-spec`, plus the
`spec-worker` agent that `work-on-spec` spawns per `[TASK]`.

This scaffold ships the plugin's shape — manifest, README, and the shared
reference — with no skills yet. Subsequent slices of PRD #31 land the four
skills and the agent; this issue exists so the plugin route can be exercised
(namespacing, install, validation) before there is much to install.

## Layout

```
plugins/ado-workflow/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    to-spec/  to-spec-tasks/  next-task-to-implement/  work-on-spec/  # land in later issues
  agents/spec-worker.md                # lands in a later issue
```

Nothing sits at the plugin root. A directory holding both a root `SKILL.md`
and a `skills/` subdirectory registers **twice** — once as a plain skill, once
as a plugin skill — and pays always-on token cost for both.

## Decisions

### No `version` in `plugin.json`

With a `version` set it becomes the install cache key, and a forgotten bump
means installs silently never see changes. Omitting it means every install
resolves fresh — exactly as `prd-workflow` and `figma-tools` already do.

The cost is that `claude plugin validate --strict` cannot pass: a missing
`version` is a warning, and `--strict` turns warnings into errors. Plain
`claude plugin validate` passes ("Validation passed with warnings"), and the
missing `version` is the *only* warning expected here.

### The shared reference lives at `skills/_shared`

`skills/_shared` is a symlink to the repo's single canonical `_shared/`
(`../../../_shared`), the same target and the same relative depth as the two
existing plugins. Every future skill's `../_shared/…` reference resolves with
zero rewrites, in both delivery modes: live through the symlink in
skills-dir mode, and inside the tree in marketplace mode.

### Names carry no `-ado` suffix

A plugin namespaces every component it provides, so skills invoke as
`ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`,
`ado-workflow:next-task-to-implement`, `ado-workflow:work-on-spec`, and the
agent resolves as `subagent_type: ado-workflow:spec-worker`. `work-on-spec` is
the exact sibling of `work-on-prd` — same shape, different tracker — so it
carries no tracker-specific prefix of its own.
