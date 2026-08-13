# figma-tools

The two Figma-to-spec skills, packaged as a Claude Code plugin, plus **an
extraction agent each** — `figma-region-extractor` for pages,
`figma-variant-extractor` for component sets — and `ds-catalog`, which authors
the per-project design-system catalog.

Three skills:

- **`figma-to-spec`** — one Figma **page** node → a page-implementation spec plus
  DS gap tickets. Runs in a **consumer** repo. Fans every region out to
  `figma-region-extractor`, and resolves against a project catalog it cannot run
  without.
- **`figma-component-to-spec`** — one Figma **component set** → one component
  spec. Runs in a **library** repo: the repo that *is* the design system. **Same
  resolution rules and same catalog contract; a different extractor agent, a
  different existence source, and no regions.** It spawns
  `figma-variant-extractor`, and only on the variant frames its triage checkpoint
  kept — the whole axis lattice comes from one `get_metadata` on the set root, so
  the checkpoint sits ahead of the metered extraction rather than behind it. Its
  existence source is a **token list** assembled from the adapter's *Token
  pipeline* row, which a catalog contributes to where one is registered.
- **`ds-catalog`** — writes the catalog, and the adapter rows that go with it.

What is genuinely shared is the **contracts**, not the pipeline:
`figma-to-spec/references/resolution-rules.md` and
`figma-to-spec/references/catalog-contract.md` are one file each with three
readers, referenced by relative path and never copied. What stopped being shared
is the agent (two now, with different call disciplines and different return
schemas), the unit of extraction (a region vs. a variant frame), and the
catalog's status — a hard requirement for `figma-to-spec`, an optional
cross-check for `figma-component-to-spec`, which stops only when **no** existence
source resolves at all.

**The two spec skills are mutually exclusive by repo, and both enforce it.** The
adapter's `## Design system` → `Repo role:` row decides which one may run;
**an absent row means `consumer`**, so an install that predates the row keeps
running `figma-to-spec` untouched and only the new skill refuses. Each guard is a
STOP with a one-line redirect to its sibling, checked before any Figma read.

## Naming

Not `figma-to-spec` — plugin skills are invoked as `plugin:skill`, so a plugin
named after its own skill would double up as `/figma-to-spec:figma-to-spec`.

And not plain `figma` either, which is what PRD #16 originally specified. That
name is **already taken by `figma@claude-plugins-official`**, Anthropic's own
Figma integration, which is installed and enabled in `~/.claude` — and all three
config dirs have that marketplace added, so the other two are one install away
from the same clash. The collision is not marketplace-only: linking a second
`figma` into a config's `skills/` reports
`✘ Not loaded — the name "figma" is already taken`, and a `--plugin-dir` load
collides with an installed `figma` just as readily.

`figma-tools` collides with nothing and yields `/figma-tools:figma-to-spec`.

## Layout

```
plugins/figma-tools/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared                    # symlink
    figma-to-spec/
      agents/figma-region-extractor.md -> ../../../agents/figma-region-extractor.md
    figma-component-to-spec/
      references/regression/                       # fixture format + assertion style
    ds-catalog/
  agents/figma-region-extractor.md                 # figma-to-spec's, per region
  agents/figma-variant-extractor.md                # figma-component-to-spec's, per variant frame
```

`ds-catalog` and `figma-component-to-spec` reach the shape contract by a plain
relative path, `../figma-to-spec/references/catalog-contract.md` — as
`figma-component-to-spec` also reaches `resolution-rules.md`. All three skills
ship in one plugin, so those paths resolve identically in this working tree and
in an install cache copy — and they need no symlink, because nothing about them
decides whether a skill loads. `figma-component-to-spec` addresses **its own**
agent at the plugin root instead — `../../agents/figma-variant-extractor.md` from
`SKILL.md`, `../../../` from its `references/`, and `../../../../` from
`references/regression/` — the same way `prd-workflow`'s `work-on-prd` addresses
`prd-worker`. It has no docs written against an inner path, so it needs no nested
link of its own. It deliberately never addresses `figma-region-extractor`:
spawning the page agent on a variant frame would hand a page contract the wrong
unit of work, so that agent is not even checked for on the component side.

Nothing sits at the plugin root — same reason as `plugins/prd-workflow/`: a
root `SKILL.md` alongside a `skills/` subdirectory registers twice.

## Decisions

Same three calls as `plugins/prd-workflow/` (see its README for the full
reasoning and evidence — repeated here only where this plugin differs):

- **`plugin.json` carries a `version`, and changing this plugin bumps it.** This
  bullet used to say the opposite — omit `version`, and accept the
  missing-`version` warning that `--strict` fails on. #57 reversed that for every
  plugin here: the version is bumped in this plugin's
  `.claude-plugin/plugin.json`, mirrored into the repo-root
  `.claude-plugin/marketplace.json` (the two must agree, because the catalog is
  what an install pins to), and
  `python3 .github/scripts/validate_skills.py --base origin/main` enforces the
  bump. `--strict` is the standard now, and zero warnings is the bar. See
  `plugins/prd-workflow/README.md` for the full argument and ADR
  [0001](../../docs/adr/0001-version-the-plugins-and-enforce-the-bump.md).
- **`skills/_shared -> ../../../_shared`.** Same depth as `prd-workflow`'s
  placement (`plugins/<name>/skills/` is three levels below the repo root
  either way), so the identical relative target is correct verbatim.
- **Compat shims — gone (#26).** The top-level `figma-to-spec` name survived the
  migration as a symlink into `plugins/figma-tools/skills/figma-to-spec` so that
  consumers' links kept resolving during the cutover. #24 repointed them at the
  plugin and #26 deleted the shim. Nothing reaches this plugin by a pre-plugin
  path, and ADR [0010](../../docs/adr/0010-one-distribution-one-dev-mode.md)
  retired the route those links belonged to outright.

### The nested agent link is not a shim, and stays

`skills/figma-to-spec/agents/figma-region-extractor.md -> ../../../agents/figma-region-extractor.md`
outlives the migration because it was never only a compat shim. The skill's own
docs address the agent from **inside** the skill — `SKILL.md` as
`agents/figma-region-extractor.md`, `references/phases.md` and
`references/resolution-rules.md` as `../agents/figma-region-extractor.md` — and
those paths have to resolve in an installed cache copy as well as here. The link
is what makes them resolve while the real file lives at the plugin root, where
the platform discovers agents.

`prd-workflow`'s nested link had no such second reason — it existed purely because
two consumer repos linked the inner path — so #26 deleted it and rewrote
`work-on-prd/SKILL.md` to address `../../agents/prd-worker.md` instead. The
asymmetry is deliberate.

### Both agents register namespaced

The types are **`figma-tools:figma-region-extractor`** and
**`figma-tools:figma-variant-extractor`**, because a plugin namespaces every
component it provides. A bare `figma-region-extractor` / `figma-variant-extractor`
only exists where the file was hand-placed in an `agents/` directory. Each skill
checks both names before falling back to `general-purpose` with the agent's own
body pasted in — `figma-to-spec` at Phase 0 step 3c, `figma-component-to-spec` at
Phase 1 (Setup) step 5c. The check is not optional politeness: an unresolvable
`subagent_type` does not error, it silently degrades to `general-purpose`, so a
run that never announced which name resolved is a run nobody can tell apart from
a correct one.

## Out of scope

`figma-component/` and `tokens-init/` were the two top-level skills this one
superseded. They sat deprecated and unlinked for a while pending #9 and #14;
ADR [0010](../../docs/adr/0010-one-distribution-one-dev-mode.md) deleted them.
