# ado-workflow

The ADO half of the PRD workflow, packaged as a Claude Code plugin: `to-spec` →
`to-spec-tasks` → `next-task-to-implement` → `work-on-spec`, plus the
`spec-worker` agent that `work-on-spec` spawns per `[TASK]`.

All four skills and the agent have landed, loop end included: `work-on-spec`
ends a run by creating a per-run `[QA]` work item and printing a final summary.
It commits **no** QA document — neither does `work-on-prd` any more, which is
the convergence that removed the adapter's QA-path convention from both
trackers. The shape of a `[QA]` item lives at `skills/references/qa-item.md` —
this plugin's own, stated in Azure DevOps terms; `work-on-prd` states the same
shape for GitHub inside its own `## Loop end`.

## Layout

```
plugins/ado-workflow/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    references/ado-mcp-setup.md        # plugin-wide, see below
    references/qa-item.md              # plugin-wide, see below
    to-spec/  to-spec-tasks/
    next-task-to-implement/  work-on-spec/
  agents/spec-worker.md                # spawned by work-on-spec, per [TASK]
```

Nothing sits at the plugin root. A directory holding both a root `SKILL.md`
and a `skills/` subdirectory registers **twice** — once as a skill in its own
right, once as a plugin skill — and pays always-on token cost for both.

## Decisions

### ~~No `version` in `plugin.json`~~ — reversed

This plugin shipped without a `version` on purpose: `version` is the install
cache key, so a forgotten bump means installs silently never see changes, and
omitting it made every install resolve fresh. The cost was that
`claude plugin validate --strict` could not pass, a missing `version` being a
warning and `--strict` turning warnings into errors.

**That was reversed in #57/#58**, and the reasoning against it has not stopped
being true — it was answered instead. All five plugins carry a `version`
mirrored in the marketplace catalog, and `validate_skills.py` fails a plugin
change that does not bump it, which is what the abstention used to buy by hand.
`--strict` passes now, with zero warnings as the bar. The argument is
ADR [0001](../../docs/adr/0001-version-the-plugins-and-enforce-the-bump.md).

A change under `_shared/` counts as a change to **every** plugin that symlinks
it, this one included — install dereferences the link into each cache copy.

### The shared reference lives at `skills/_shared`

`skills/_shared` is a symlink to the repo's single canonical `_shared/`
(`../../../_shared`), the same target and the same relative depth as the two
existing plugins. Every future skill's `../_shared/…` reference resolves with
zero rewrites wherever the plugin is loaded from: live through the link under
`--plugin-dir`, and inside the tree in an install cache.

### Plugin-wide references live at `skills/references/`

`ado-mcp-setup.md` is needed by all four skills — each one probes the ADO MCP
server before its first call — so it belongs to the plugin, not to whichever
skill happened to be written first. It sits beside `_shared` as a sibling of
the skill directories, which makes the pointer `../references/ado-mcp-setup.md`
from any skill: the same relative depth as `../_shared/…`, valid live through
the packaging link under `--plugin-dir` and valid inside an install cache, where
the whole plugin directory is copied. The cross-skill route the client repo used
(`../<other-skill>/references/…`) is what packaging cannot carry.

A directory under `skills/` with no `SKILL.md` is not registered as a skill —
`claude --plugin-dir plugins/ado-workflow plugin details ado-workflow` reports
`Skills (4) next-task-to-implement, to-spec, to-spec-tasks, work-on-spec`
(plus `Agents (1) spec-worker`) with both `_shared` and `references` present,
and `claude plugin validate` gains no second warning. (`--plugin-dir`
is a global `claude` flag, so it precedes the `plugin` subcommand; it is what
lets this plugin be inspected before it is installed anywhere.)

A skill's *own* references still belong inside that skill, as
`figma-tools:figma-to-spec` does it. `skills/references/` is for what the
plugin shares.

`qa-item.md` sits there too, and it is the one exception to that last line:
only `work-on-spec` reads it. It is placed at plugin level because it is the
ADO half of a document that used to be `_shared/qa-item.md` and is now stated
twice — once here, once inside `work-on-prd`'s `## Loop end` — and a
plugin-level file is the half a reader can find without knowing which skill
happens to cite it. Anything else a single skill owns still goes inside that
skill.

### Names carry no `-ado` suffix

A plugin namespaces every component it provides, so skills invoke as
`ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`,
`ado-workflow:next-task-to-implement`, `ado-workflow:work-on-spec`, and the
agent resolves as `subagent_type: ado-workflow:spec-worker`. `work-on-spec` is
the exact sibling of `work-on-prd` — same shape, different tracker — so it
carries no tracker-specific prefix of its own.
