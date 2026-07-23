# Page-implementation spec template

Fill this from the synthesized region findings. It is the primary artifact — filed as an
ADO `[SPEC]` in **myGRIMME Core**. It tells an implementer HOW to build the page
on-system, cites `grimme-ui-components-best-practices` for usage rules (never duplicates
them), and marks every DS gap inline as `⚠ blocked on gap-NNN`.

---

# [SPEC] <Page name> — implementation

**Figma node:** <url> · **Mobile/tablet node:** <url | "none — responsive inferred">
**State nodes:** <state:empty=url, state:error=url | "none"> · **Scope ticket:** #<id | "none">
**Generated:** <YYYY-MM-DD> · **Gap specs:** `gaps/` (N gaps) · **ADO [SPEC]:** #<id once filed>

## Overview

<2–4 sentences: what the page is, its major regions, and the on-system posture — which
regions resolve cleanly vs which are blocked on DS gaps.>

## Scope

**In-scope regions:** <list>. **Excluded (app chrome / out of ticket scope):** <navbar,
global header, …> — recorded so re-runs are deterministic.

## Region blueprint

Repeat per region (from Phase A decomposition).

### <Region name> — node `<id>`

- **Components:** `<Component variant="..." size="..." />` — resolved from catalog.
  <For any low-confidence match: "⚠ inferred from layer `X`, confirm.">
- **Layout / placement:** containment tree + child order, and per-container auto-layout
  intent (direction · gap token · align · wrap). Maps to flex/grid — e.g.
  `Content = column, gap g-4; CardGrid = row, wrap, gap g-4, items stretch`. Relative
  intent only — never absolute coordinates.
- **Tokens (color / spacing / type):**
  | Property | Figma | Resolved token | Status |
  |----------|-------|----------------|--------|
  | background | surface/primary | `g-bg-surface-button-primary` | ✅ |
  | gap | 16px | `<dimension token>` | ✅ |
  | accent | #0a5c2b (raw) | nearest `<token>` | ⚠ flag → gap-003 |
- **Icons:** `<SystemIcon name="..." />` · or `<FA icon />` (app layer) · or ⚠ gap-005.
- **States:** *(only if this region contains a new/unknown component)* hover / focus /
  disabled / loading / empty / error — describe each.
- **Data states:** *(only if a `state:*` node was provided for this region)* populated /
  empty / loading / error — what changes (copy, illustration, CTA, layout) per state. A
  page/region content state, not a DS component state.
- **Best-practices rules to follow:** cite the relevant
  `grimme-ui-components-best-practices` rule(s) — e.g. form-controller-pattern,
  dialog-standard-structure. Cite, don't restate.
- **Reference image:** `screenshots/<region>.png` (verification aid — the layout above is
  the source of truth, not the image).
- **Blocked on:** `⚠ gap-NNN` (list any gaps this region depends on).

## Responsive notes

- **Mobile node provided?** yes → merged notes below / no → **inferred**, assumptions listed.
- Per-region reflow: <table → horizontal scroll, card grid → single column, etc.>
- Flag every inferred assumption so a reviewer can correct it — one Figma node is one
  viewport; breakpoints are not in the node.

## Blocked-on-gaps

| Gap | Category | Summary | Recommendation | ADO PBI |
|-----|----------|---------|----------------|---------|
| gap-001 | component | <...> | build-local / escalate | #<id or —> |
| gap-003 | color | <...> | escalate | #<id or —> |

## Verification notes

What an implementer should check after building: computed token values vs the Figma
numbers per region, Storybook renders match, states behave, and the built layout matches
each region's containment tree + auto-layout intent (cross-check against
`screenshots/<region>.png`). (This spec does not build or verify — it hands the
implementer the checklist.)
