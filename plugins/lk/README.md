# lk

The five skills that travel everywhere Liam does, packaged as a Claude Code
plugin: `grill` and `deep-grill` for interviewing a plan, `pinpoint`,
`scoped-context`, and `how-i-write`.

They talk to the **user and the codebase** rather than to a tracker, which is
exactly why they do not belong to a tracker-bound workflow plugin. Before this
plugin they reached a machine only as hand-made symlinks, one per skill per
config directory, recorded nowhere the repo could check. This plugin ended
that: `/plugin install lk@liamklyneker` places all five at once, at a version
the catalog pins.

That criterion — the user and the codebase, never a tracker — is the whole
membership rule, and it now holds with **no exception**. The plugin carried the PRD QA loop for a while, and that loop
writes to GitHub — so it belonged to `prd-workflow` all along. `triage-prd`
moved there and invokes as `/prd-workflow:triage-prd`.

## Layout

```
plugins/lk/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared        # symlink, see below
    grill/  deep-grill/                # the interviews
    pinpoint/                          # throwaway-subagent search
    scoped-context/                    # the CONTEXT.md convention
    how-i-write/                       # Liam's voice, with references/
```

Nothing sits at the plugin root, and there are no agents. A directory holding
both a root `SKILL.md` and a `skills/` subdirectory registers **twice** — once
as a skill in its own right, once as a plugin skill — and pays always-on token cost for
both.

The inventory is **discovered from the directory**, not listed in the manifest.
Adding a skill here means adding the directory and nothing else.

## Decisions

### `grill-me` is now `grill`

A plugin namespaces every component it provides, so the interview invokes as
**`/lk:grill`** — and `/lk:grill-me` would have stuttered. The rename lands in
the same change as the packaging, so muscle memory breaks once rather than
twice. A bare `/grill` resolves nowhere; that is the accepted cost of
packaging, and the two-character prefix is what makes it acceptable.

Every skill here is namespaced the same way: `lk:deep-grill`, `lk:pinpoint`,
`lk:how-i-write`, `lk:scoped-context`.

### The name is two characters on purpose

`/lk:grill` is what makes the namespace livable, and it is the only reason
these are packaged at all rather than staying hand-linked forever. A longer
plugin name would have made the daily commands worse than the symlinks they
replace.

### The shared reference lives at `skills/_shared`

`skills/_shared` is a symlink to the repo's single canonical `_shared/`
(`../../../_shared`), the same target and the same relative depth as the other
plugins. A skill's existing `../_shared/…` references keep resolving with zero
rewrites wherever the plugin is loaded from: live through the link under `--plugin-dir`,
and inside the tree in marketplace mode. Same depth in every plugin is also
what let `triage-prd` move to `prd-workflow` without touching a single
reference.

A directory under `skills/` with no `SKILL.md` is not registered as a skill, so
`_shared` costs nothing in the inventory.

### A skill's own references stay inside the skill

`how-i-write/references/` (the writing samples) and
`scoped-context/convention-guide.md` moved with their skills and are addressed
relatively, so they resolve unchanged from an install cache. Only what several
skills share is promoted to `skills/_shared`.

### Project facts still come from the adapter

`deep-grill` reads
`<repo-root>/.claude/project/adapter.md` at runtime, resolved against whichever
project the session is running in. Packaging did not move the project — that
pointer works unchanged from a plugin cache directory. `grill` deliberately
reads nothing from the adapter; it is the lightweight inline interview.
