# Page-implementation spec template

Fill this from the synthesized region findings. It is the primary artifact — filed as an
ADO `[SPEC]` in **myGRIMME Core**. It tells an implementer HOW to build the page
on-system, cites `grimme-ui-components-best-practices` for usage rules (never duplicates
them), and marks every DS gap inline as `⚠ blocked on gap-NNN`.

---

# [SPEC] <Page name> — implementation

**Mode:** page | component · **Figma node:** <url> · **Mobile/tablet node:** <url | "none — responsive inferred">
**State nodes:** <state:empty=url, state:error=url | "none"> · **Scope ticket:** #<id | "none">
**Generated:** <YYYY-MM-DD> · **Gap specs:** `gaps/` (N gaps) · **ADO [SPEC]:** #<id once filed | "n/a — component mode">

## Changelog

*(update runs only — omit for a brand-new spec)* Diffed **spec-vs-spec** against the prior
baseline, never against code. Changed since <prior `page-spec.md` / ADO [SPEC] #id>:
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
  | background | surface/primary | `bg-surface-button-primary` | ✅ |
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
  *(Screenshots aren't persisted under `figma-dev-mode` — the region agent viewed the
  canvas inline during extraction; the layout tree above is the source of truth.)*
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
each region's containment tree + auto-layout intent (cross-check against the Figma node
itself). (This spec does not build or verify — it hands the implementer the checklist.)
