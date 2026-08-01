# prd-workflow

The PRD-to-merge workflow, packaged as a Claude Code plugin: `to-prd` →
`to-issues` → `next-prd-issue` → `work-on-prd` / `work-on-issue`, plus the
`prd-worker` agent that `work-on-prd` spawns per child issue.

`manual-qa` and `triage-prd` close the loop from the other end. `manual-qa`
drives the QA comment a run posted on the PRD — one step per turn, ticking each
box as the human confirms it and posting a `### [FINDING]` comment to the PR for
each failure. `triage-prd` then takes those findings and promotes the survivors
back into cold-runnable children that `work-on-prd` picks up with no new
machinery. Both lived in the `lk` plugin until they didn't — `lk` is the skills
that talk to the user and the codebase, and a skill that files GitHub issues was
never one of those.

## Layout

```
plugins/prd-workflow/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    to-prd/  to-issues/  next-prd-issue/  work-on-prd/  work-on-issue/
    manual-qa/                         # drive the QA comment, capture findings
    triage-prd/                        # QA findings back into children
  agents/prd-worker.md
```

Nothing sits at the plugin root. A directory holding both a root `SKILL.md`
and a `skills/` subdirectory registers **twice** — once as a plain skill, once
as a plugin skill — and pays always-on token cost for both.

## Decisions

### `plugin.json` carries a `version`, and changing this plugin bumps it

This section used to argue the opposite — omit `version`, because it becomes
the install cache key and a forgotten bump strands consumers on stale files.
That risk is real and has not gone away; #57 reversed the decision anyway,
because abstaining from versions bought safety by giving up `--strict` (a
missing `version` is a warning, and `--strict` is warnings-as-errors) and by
having no enforcement at all.

The rule now:

- Bump `version` in `.claude-plugin/plugin.json` for any change to this
  plugin's contents — including `skills/_shared`, whose target install
  dereferences into every consumer's cache copy.
- Mirror the same value into `.claude-plugin/marketplace.json`. The two must
  agree; the catalog is what an install actually pins to.
- `python3 .github/scripts/validate_skills.py --base origin/main` enforces
  both, and is what makes versions safe to have. Without `--base` the bump
  check reports itself skipped and the rest still run.

ADR [0001](../../docs/adr/0001-version-the-plugins-and-enforce-the-bump.md) has
the argument; the `version` bullet in the project adapter's `## Repo
discipline` has the observed failure mode in full.

### The shared reference lives at `skills/_shared`

`skills/_shared` is a symlink to the repo's single canonical `_shared/`
(`../../../_shared`). Every skill's existing `../_shared/…` reference keeps
resolving with zero rewrites, in both delivery modes: live through the symlink
in skills-dir mode, and inside the tree in marketplace mode (a marketplace
clone of this repo carries the root `_shared/` the link points at).

The alternative was `plugins/prd-workflow/_shared` plus rewriting every
reference to `../../_shared/`. It was not needed: `claude plugin details`
reports **Skills (7), Agents (1)** with the symlink in place — the seven real
skills and no phantom entry for `_shared`, because a directory under `skills/`
with no `SKILL.md` does *not* register as a component. Measured, not assumed —
and re-measured on each skill added, which is why the count is a number and not
"all of them".

Keeping the same link at the same depth in every plugin is also what let
`triage-prd` move here from `lk` without editing one of its `../_shared/…`
references.

### Compat shims — gone (#26)

During the migration the five top-level directory names in this repo survived
as symlinks into `skills/`, plus a nested `skills/work-on-prd/agents/prd-worker.md`
pointing back at `../../../agents/prd-worker.md`, so the ~22 consumer symlinks
across four repos kept resolving while the cutover ran. #24 repointed every
consumer onto the plugin and #26 deleted all of them. Nothing links into this
plugin by a pre-plugin path any more, and `work-on-prd/SKILL.md` addresses the
agent at its real location, `../../agents/prd-worker.md`.

### The agent registers namespaced

A plugin namespaces every component it provides, so the type is
**`prd-workflow:prd-worker`** — not the bare `prd-worker`, which is what a
hand-placed `.claude/agents/prd-worker.md` registers. Observed in a fresh
session, not assumed. This matters more than it looks: `work-on-prd`'s
detachable path treats a non-resolving agent as expected and falls back to
`general-purpose`, so a wrong type name produces a run that looks completely
normal and is not.
