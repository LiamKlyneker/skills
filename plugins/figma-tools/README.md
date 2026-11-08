# figma-tools

The design-to-brief skills, packaged as a Claude Code plugin, plus `ds-catalog`, which authors
the per-project design-system catalog they resolve against.

**One spec per piece of work.** Design work gets no spec of its own. A Figma canvas and a
designer-authored code prototype each produce a disposable **brief**, the grill resolves it, and
the grill's output is the one spec. ADR
[0026](../../docs/adr/0026-design-work-enters-through-a-brief.md) has the argument.

Five skills:

- **`figma-to-brief`** — one or more Figma nodes from one file plus one ticket →
  a **design brief** at `.claude/briefs/<ticket>.md`, with one PNG per in-scope
  state saved beside it.
  Runs in a **consumer** repo or a **library** repo, reads the canvas once through
  the local `figma-dev-mode` server at a pinned file version, filters it to the
  ticket, renders the ticket's overrides on top, and resolves every element and
  token against the **existence source** into a **per-element fidelity ledger**:
  the catalog in a consumer repo, and in a library repo a list assembled from the
  library's own source through the *Variant mechanism* and *Token pipeline* rows,
  with a registered catalog as a cross-check only. In a library repo a `DS change`
  row is work in this repo, never a gap filed against another one. **Same brief slot as
  `prototype-to-brief`, a different source**: a canvas instead of a committed
  prototype spec. It asks nothing and files nothing — every judgement becomes a
  row, and `deep-grill` is where a human answers it. No subagents: a brief covers
  one ticket's states, and a region agent's JSON would have to be re-flattened into
  ledger rows anyway. Its Figma seat, call budget, pin rule and screenshot export
  come from the adapter's `## Design system` → `### Figma source` rows, and an
  absent sub-section is a STOP.
- **`prototype-to-brief`** — one preview URL plus one ticket → a **design brief** at
  `.claude/briefs/<ticket>.md`. Runs in a **consumer** repo, reads the designers'
  committed spec at a pinned SHA, filters it to the ticket, renders the ticket's
  overrides on top, and resolves every element and token against the catalog at three
  confidences. **It asks nothing and files nothing**: every judgement becomes a row,
  and `deep-grill` is where a human answers it. No subagents — the prototype's spec is
  already structured, so there is nothing to extract.
- **`ds-catalog`** — writes the catalog, and the adapter rows that go with it. Its
  output is **two files**: a `generated` half enumerated by
  `scripts/generate_catalog.py` from the design system's own declarations, stamped with
  the installed version, and **usage notes** a human owns — conventions, every `status:`,
  and the idiom mapping that says which design-system component a hand-rolled popover
  or chip row should have been. Where the design-system package ships its own generated
  catalog, the adapter's `Catalog:` row names that file and `ds-catalog` writes only the
  usage notes. A design-system bump re-runs the script and diffs; it re-runs the
  interview only where something was removed or renamed.
- **`design-component`** — one design brief → a proposed component in the library's
  **UI component lab**, plus a **blueprint** at `.claude/briefs/<ticket>/blueprint.md`.
  Runs in a **library** repo only. Applies every fidelity-ledger recommendation as a
  default instead of asking it, renders the result with the library's real styles, and
  takes the user's changes in plain language until they say `approve`. Writes only inside
  the lab and to the blueprint, which the later grill reads instead of the brief. Finds
  the lab through the adapter's `UI component lab:` row and follows the entry guide that
  row names; the lab owns the entry format, the skill owns only the method.
- **`create-ui-component-lab`** — installs the UI component lab into a library repo, or
  upgrades the one already there, and writes the `UI component lab:` row. The lab's code
  lives in its own repository, `https://github.com/LiamKlyneker/ui-component-lab`; the
  skill copies files out of a pinned tag and commit SHA and runs nothing from the clone.
  ADR [0025](../../docs/adr/0025-a-skill-may-install-an-app-it-does-not-carry.md) has the
  argument.

The brief skills share two contracts, `figma-to-brief/references/resolution-rules.md` and
`figma-to-brief/references/catalog-contract.md`, and `references/existence-source.md`. They are
referenced by relative path and never copied. Those paths resolve identically in this working tree
and in an install cache copy, because every skill ships in one plugin.

Both brief skills read the adapter's `Repo role:` row to choose the existence source: the catalog
in a consumer repo, and a list assembled from the library's own source in a library repo, with a
registered catalog as a cross-check. An absent row means `consumer`.

## Install

```
/plugin install figma-tools --marketplace LiamKlyneker/skills
```

## Naming

Not plain `figma`, which is what PRD #16 originally specified. That
name is **already taken by `figma@claude-plugins-official`**, Anthropic's own
Figma integration, which is installed and enabled in `~/.claude` — and all three
config dirs have that marketplace added, so the other two are one install away
from the same clash. The collision is not marketplace-only: linking a second
`figma` into a config's `skills/` reports
`✘ Not loaded — the name "figma" is already taken`, and a `--plugin-dir` load
collides with an installed `figma` just as readily.

`figma-tools` collides with nothing and yields `/figma-tools:figma-to-brief`.

## Layout

```
plugins/figma-tools/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared                    # symlink
    ds-catalog/
      scripts/generate_catalog.py                  # the enumerated half; no skill-specific input
    figma-to-brief/
      references/brief-template.md                 # the brief's fixed headings
      references/catalog-contract.md               # the catalog's shape
      references/resolution-rules.md               # how a property resolves
      references/existence-source.md               # catalog or assembled list, by repo role
      references/figma-read-discipline.md          # how one node is read
    prototype-to-brief/
    design-component/
      references/blueprint-template.md             # the blueprint's fixed headings
    create-ui-component-lab/
```

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
