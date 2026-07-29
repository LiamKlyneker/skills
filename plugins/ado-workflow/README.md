# ado-workflow

The ADO half of the PRD workflow, packaged as a Claude Code plugin: `to-spec` →
`to-spec-tasks` → `next-task-to-implement` → `work-on-spec`, plus the
`spec-worker` agent that `work-on-spec` spawns per `[TASK]`.

`to-spec` has landed. The remaining slices of PRD #31 land the other three
skills and the agent.

## Layout

```
plugins/ado-workflow/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    references/ado-mcp-setup.md        # plugin-wide, see below
    to-spec/
    to-spec-tasks/  next-task-to-implement/  work-on-spec/  # land in later issues
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

### Plugin-wide references live at `skills/references/`

`ado-mcp-setup.md` is needed by all four skills — each one probes the ADO MCP
server before its first call — so it belongs to the plugin, not to whichever
skill happened to be written first. It sits beside `_shared` as a sibling of
the skill directories, which makes the pointer `../references/ado-mcp-setup.md`
from any skill: the same relative depth as `../_shared/…`, valid live through
the skills-dir symlink and valid inside a marketplace install cache, where the
whole plugin directory is copied. The cross-skill route the client repo used
(`../<other-skill>/references/…`) is what packaging cannot carry.

A directory under `skills/` with no `SKILL.md` is not registered as a skill —
`claude plugin details` reports `Skills (1) to-spec` with both `_shared` and
`references` present, and `claude plugin validate` gains no second warning.

A skill's *own* references still belong inside that skill, as
`figma-tools:figma-to-spec` does it. `skills/references/` is for what the
plugin shares.

### Names carry no `-ado` suffix

A plugin namespaces every component it provides, so skills invoke as
`ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`,
`ado-workflow:next-task-to-implement`, `ado-workflow:work-on-spec`, and the
agent resolves as `subagent_type: ado-workflow:spec-worker`. `work-on-spec` is
the exact sibling of `work-on-prd` — same shape, different tracker — so it
carries no tracker-specific prefix of its own.
