# figma-tools

`figma-to-spec`, packaged as a Claude Code plugin, plus the
`figma-region-extractor` agent it spawns per region — and `ds-catalog`, which
authors the per-project design-system catalog the spec skills resolve against.

Three skills:

- **`figma-to-spec`** — one Figma **page** node → a page-implementation spec plus
  DS gap tickets. Runs in a **consumer** repo.
- **`figma-component-to-spec`** — one Figma **component set** → one component
  spec. Runs in a **library** repo: the repo that *is* the design system. Same
  extractor agent, same catalog contract, same resolution rules; each variant
  frame becomes one region tagged `variant:<name>`.
- **`ds-catalog`** — writes the catalog the other two read.

One dependency runs through all of it: the catalog. `ds-catalog` writes it, both
spec skills read it, and the shape all three are written against is
`figma-to-spec/references/catalog-contract.md`.

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
    ds-catalog/
  agents/figma-region-extractor.md
```

`ds-catalog` and `figma-component-to-spec` reach the shape contract by a plain
relative path, `../figma-to-spec/references/catalog-contract.md` — as
`figma-component-to-spec` also reaches `resolution-rules.md`. All three skills
ship in one plugin, so those paths resolve identically in this working tree and
in an install cache copy — and they need no symlink, because nothing about them
decides whether a skill loads. `figma-component-to-spec` addresses the agent at
the plugin root instead (`../../agents/figma-region-extractor.md`, and
`../../../` from its `references/`), the same way `prd-workflow`'s `work-on-prd`
addresses `prd-worker` — it has no docs written against an inner path, so it
needs no nested link of its own.

Nothing sits at the plugin root — same reason as `plugins/prd-workflow/`: a
root `SKILL.md` alongside a `skills/` subdirectory registers twice.

## Decisions

Same three calls as `plugins/prd-workflow/` (see its README for the full
reasoning and evidence — repeated here only where this plugin differs):

- **No `version` in `plugin.json`.** Plain `claude plugin validate` passes with
  the missing-`version` warning as the only warning; `--strict` fails on that
  warning by definition and is expected to.
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

### The agent registers namespaced

The type is **`figma-tools:figma-region-extractor`**, because a plugin namespaces
every component it provides. The bare `figma-region-extractor` only exists where
the file was hand-placed in an `agents/` directory. Phase 0 checks both names
before falling back.

## Out of scope

`figma-component/` and `tokens-init/` were the two top-level skills this one
superseded. They sat deprecated and unlinked for a while pending #9 and #14;
ADR [0010](../../docs/adr/0010-one-distribution-one-dev-mode.md) deleted them.
