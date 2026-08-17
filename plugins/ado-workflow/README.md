# ado-workflow

The ADO half of the PRD workflow, packaged as a Claude Code plugin. **Six skills**
in two halves: the loop — `to-spec` → `to-spec-tasks` →
`next-task-to-implement` → `work-on-spec`, plus the `spec-worker` agent that
`work-on-spec` spawns per `[TASK]` — and the QA pair, `manual-qa` → `triage`.

All six and the agent have landed, loop end included: `work-on-spec` ends a run
by tagging the `[SPEC]` `needs-qa`, printing the `/ado-workflow:manual-qa`
invocation, and printing a final summary. It **composes no QA pass**, commits
**no** QA document and **creates no `[QA]` work item** — that type is retired
here, and `work-on-prd` files no `[QA]` issue either, which is the convergence
that removed the adapter's QA-path convention from both trackers.

The QA pair is why the plugin outgrew its bundle. `manual-qa` **composes** the
pass on demand from what actually landed on the run's branch — the diff, the
commits, the landed `[TASK]`s — as a short list of flows, drives it one flow at a
time, and appends each failure to the run's **`[FINDINGS]` work item**; `triage`
reads that one item, files a `[BUG]` per survivor under the same parent, and
closes it. They sit here rather than in `prd-workflow` or `lk` for ADR 0008's
surviving reason — the writer and readers of a tracker's literals ship in one
version-bumped plugin — and they answer to the **`ado-qa`** bundle, not to
`ado-workflow`. ADR
[0011](../../docs/adr/0011-azure-devops-qa-is-a-tickable-comment.md) is the
argument, including which of 0008's claims about this tracker were wrong; ADR
[0012](../../docs/adr/0012-the-qa-pass-is-composed-from-the-branch.md) supersedes
it **on the QA-artifact half only** — the tickable comment is gone, the plugin
membership and the board reasoning behind the title prefixes are not.

## Layout

```
plugins/ado-workflow/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    references/ado-mcp-setup.md        # plugin-wide, see below
    references/findings-item.md        # plugin-wide, see below
    to-spec/  to-spec-tasks/
    next-task-to-implement/  work-on-spec/
    manual-qa/  triage/
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

`ado-mcp-setup.md` is needed by every skill here — each one probes the ADO MCP
server before its first call — so it belongs to the plugin, not to whichever
skill happened to be written first. It sits beside `_shared` as a sibling of
the skill directories, which makes the pointer `../references/ado-mcp-setup.md`
from any skill: the same relative depth as `../_shared/…`, valid live through
the packaging link under `--plugin-dir` and valid inside an install cache, where
the whole plugin directory is copied. The cross-skill route the client repo used
(`../<other-skill>/references/…`) is what packaging cannot carry.

A directory under `skills/` with no `SKILL.md` is not registered as a skill —
`claude --plugin-dir plugins/ado-workflow plugin details ado-workflow` reports
`Skills (6) manual-qa, next-task-to-implement, to-spec, to-spec-tasks, triage,
work-on-spec` (plus `Agents (1) spec-worker`) with both `_shared` and
`references` present,
and `claude plugin validate` gains no second warning. (`--plugin-dir`
is a global `claude` flag, so it precedes the `plugin` subcommand; it is what
lets this plugin be inspected before it is installed anywhere.)

A skill's *own* references still belong inside that skill, as
`figma-tools:figma-to-spec` does it. `skills/references/` is for what the
plugin shares.

`findings-item.md` sits there too, and it is the clearest case for the rule:
**two** skills share it — `manual-qa` is the `[FINDINGS]` item's only writer and
`triage` its only reader — so neither owns the shape alone and it can live in
neither's directory. A skill never borrows a reference out of a sibling skill's
folder; plugin level is what makes `../references/findings-item.md` resolve
identically from both, live under `--plugin-dir` and inside an install cache.

It replaced the `[QA]`-item reference that used to sit beside it, deleted along
with the work item it described. Anything a single skill owns still goes inside
that skill.

### Names carry no `-ado` suffix

A plugin namespaces every component it provides, so skills invoke as
`ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`,
`ado-workflow:next-task-to-implement`, `ado-workflow:work-on-spec`,
`ado-workflow:manual-qa`, `ado-workflow:triage`, and the agent resolves as
`subagent_type: ado-workflow:spec-worker`. `work-on-spec` is the exact sibling
of `work-on-prd` — same shape, different tracker — so it carries no
tracker-specific prefix of its own.

The last two go further and share their names outright with
`prd-workflow:manual-qa` and `prd-workflow:triage`. That is deliberate: those
two name an **activity**, where `to-prd`/`to-spec` and `work-on-prd`/`work-on-spec`
name an **artifact** whose noun genuinely differs per tracker. Namespacing makes
the pair unambiguous on every route, and `validate_skills.py`'s name-uniqueness
check is per-plugin rather than global for exactly this case.
