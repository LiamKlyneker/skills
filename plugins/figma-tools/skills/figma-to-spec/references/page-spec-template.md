# Page-implementation spec template

Fill this from the synthesized region findings. It is the primary artifact — filed as a
`[DESIGN-SPEC]` against the adapter's **design-spec target**, on whichever tracker the
adapter's `Tracker:` line names. It tells an implementer HOW to build the page on-system,
cites the adapter's **usage-rules source** for usage rules (never duplicates them, cites
nothing when no such row exists), and marks every DS gap inline as `⚠ blocked on gap-NNN`.

**The `Extracted against:` line is required, and it is not decoration.** A spec is a snapshot
of a file that keeps moving. Without the version it was read at, a later design-QA pass
comparing build to design cannot tell an implementation defect from a design that changed
*after* the spec was written — and every discrepancy then costs a full re-derivation to
attribute. Record whichever the Figma tooling exposes (version id preferred, the file's
last-modified timestamp otherwise), and both when both are available. If neither can be read,
write `unknown — <why>`; never drop the line. An unpinned baseline is a real limitation, and
downstream QA needs to see it stated rather than infer it from an absence. It is also what
makes the Changelog below a *spec-vs-spec* diff between two known design states rather than
between two undated documents.

---

# [DESIGN-SPEC] <Page name> — implementation

**Mode:** page | component · **Figma node:** <url> · **Mobile/tablet node:** <url | "none — responsive inferred">
**State nodes:** <state:empty=url, state:error=url | "none"> · **Scope ticket:** #<id | "none">
**Generated:** <YYYY-MM-DD> · **Gap specs:** `gaps/` (N gaps) · **Filed [DESIGN-SPEC]:** <id on the design-spec target once filed | "n/a — component mode">
**Extracted against:** Figma file version `<version id>` · last modified `<ISO timestamp>`

## Changelog

*(update runs only — omit for a brand-new spec)* Diffed **spec-vs-spec** against the prior
baseline, never against code. Changed since <prior `page-spec.md` / filed [DESIGN-SPEC] id>:
- <region / property>: <old> → <new>

Unchanged: <everything else>. New spec, no prior baseline → "n/a".

## Overview

<2–4 sentences: what the page is, its major regions, and the on-system posture — which
regions resolve cleanly vs which are blocked on DS gaps.>

## Scope dispositions

Recorded so re-runs are deterministic and scope is auditable:

- **In-scope** (spec + implement): <list>.
- **Spec-only** (fully specced, **not integrated this pass** — leave as-is / UI-only):
  <list | "none">.
- **Excluded** (app chrome / out of ticket scope): <navbar, global header, …>.

## Region blueprint

Repeat per region (from Phase A decomposition). *In component mode, only the single
targeted region appears here — the page-level sections above collapse to that node.* On
update runs, prefix a changed region's heading with `△`. For a **spec-only** region, add a
**`> spec-only — not integrated this pass (leave as-is / UI-only)`** banner under its
heading so the implementer skips integration.

### <Region name> — node `<id>`

- **Components:** `<Component variant="..." size="..." />` — resolved from catalog.
  <For any low-confidence match: "⚠ inferred from layer `X`, confirm.">
- **Layout / placement:** containment tree + child order, and per-container auto-layout
  intent (direction · gap token · align · wrap). Maps to flex/grid — e.g.
  `Content = column, gap-4; CardGrid = row, wrap, gap-4, items stretch`. Relative
  intent only — never absolute coordinates.
- **Tokens (color / spacing / type):**
  | Property | Figma | Resolved token | Status |
  |----------|-------|----------------|--------|
  | background | surface/primary | `<catalog entry, verbatim>` | ✅ |
  | gap | 16px | `<dimension token>` | ✅ |
  | accent | #0a5c2b (raw) | nearest `<token>` | ⚠ flag → gap-003 |
- **Icons:** the reference form of whichever ladder source resolved it, copied from the
  catalog — noting the layer when the source is app-layer-only · or ⚠ gap-005.
- **States:** *(only if this region contains a new/unknown component)* hover / focus /
  disabled / loading / empty / error — describe each.
- **Data states:** *(only if a `state:*` node was provided for this region)* populated /
  empty / loading / error — what changes (copy, illustration, CTA, layout) per state. A
  page/region content state, not a DS component state.
- **Best-practices rules to follow:** cite the relevant rule(s) of the adapter's
  **usage-rules source**, by the stable name that source gives them. Cite, don't restate —
  a citation stands even where the source isn't loaded. No such row → omit this line.
  *(Screenshots aren't persisted under `figma-dev-mode` — the region agent viewed the
  canvas inline during extraction; the layout tree above is the source of truth.)*
- **Blocked on:** `⚠ gap-NNN` (list any gaps this region depends on).

## Responsive notes

- **Mobile node provided?** yes → merged notes below / no → **inferred**, assumptions listed.
- Per-region reflow: <table → horizontal scroll, card grid → single column, etc.>
- Flag every inferred assumption so a reviewer can correct it — one Figma node is one
  viewport; breakpoints are not in the node.

## Blocked-on-gaps

| Gap | Category | Summary | Recommendation | DS-gap ticket |
|-----|----------|---------|----------------|---------------|
| gap-001 | component | <...> | build-local / escalate | <id on the DS-gap backlog, or —> |
| gap-003 | color | <...> | escalate | <id on the DS-gap backlog, or —> |

## Verification notes

What an implementer should check after building: computed token values vs the Figma
numbers per region, components rendering the way the design system renders them, states
behaving, and the built layout matching each region's containment tree + auto-layout intent
(cross-check against the Figma node itself). (This spec does not build or verify — it hands
the implementer the checklist.)

**Compare against the pinned baseline, not against "current Figma".** The `Extracted
against:` version at the top is what this spec describes. If the file has moved on, a
difference between build and canvas may be a design change rather than a defect — check the
version before filing anything, and re-run the skill to re-baseline if it has.
