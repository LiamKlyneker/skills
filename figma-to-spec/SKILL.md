---
name: figma-to-spec
description: >
  Turn a Figma page node into a detailed, on-system implementation spec plus
  design-system gap tickets. Scans via Figma MCP + Sonnet subagents, resolves
  against grimme-ui, flags off-system colors/tokens/icons/components, and routes
  each gap to build-local or a grimme-ui backlog PBI. Invoke /figma-to-spec <url>.
disable-model-invocation: true
metadata:
  author: liam
  version: "1.2.0"
---

# Figma → Spec

Turn one Figma **page** node into two linked artifacts:

1. a **page-implementation spec** (region-by-region, on-system, filed as an ADO
   `[SPEC]` in **myGRIMME Core**), and
2. **N design-system gap specs** (one per real gap, triaged by the user, then filed
   as PBIs on the **GRIMME Libraries** backlog).

**This skill is a spec producer, not a builder.** It never writes page code. The specs
it emits are implemented later — by `figma-component`, `develop-ticket`, or a human.

**The spec is high-fidelity; the 1:1 risk lives at implementation — which this skill
hands off.** Extraction here can be near-complete: the region subagents read bound
variable names, tokens, spacing, and layout intent straight off the canvas. What no tool
can guarantee is that the *eventual rendered code* is faithful — and this skill doesn't
write that code. Its job is to resolve the design against what the DS actually offers,
capture layout precisely enough to place every element, and route every gap through a
**human triage checkpoint**. That checkpoint is the point of the skill — do not automate
past it. The three residual uncertainties it flags rather than hides: inferred component
identity (no Code Connect), responsive behavior absent from a single node, and
interaction states.

## Prerequisites

- **Figma MCP** (official plugin `figma@claude-plugins-official`): `get_metadata`,
  `get_variable_defs`, `get_screenshot`, `get_design_context`, and `use_figma`. STOP
  if absent. Call discipline lives in `figma-component/references/figma-feed.md` —
  follow it; the same traps apply here.
- **A Figma node URL** (a page or large frame). Missing → ask, never guess.
- **`grimme-ui-catalog`** — the existence catalog this scan resolves against. Its
  `catalog.md` must exist and be current (Phase 0 handles this).

## Resolution sources (what "does it exist?" reads)

- **Existence** → `grimme-ui-catalog`'s `catalog.md` (components, cva variants, tokens
  by tier, SYSTEM_ICONS keys). This is the ONLY source for "does the DS have this?".
- **Usage / HOW** → the `grimme-ui-components-best-practices` skill (Marketplace). The
  page spec **cites** its rules; it never duplicates them.
- **Resolution + tolerance rules** → `references/resolution-rules.md`.

grimme-ui has **no Code Connect and no documented Figma-name↔code mapping** — component
detection **infers** by layer-name convention + visual confirmation. That inference is
deliberately loose for v1; surface low-confidence matches for user confirmation rather
than guessing silently.

## Model tiers

Decompose: **Sonnet**. Region agents: **Sonnet ×N** parallel. Synthesis & triage:
**Opus**. (Catalog refresh, if needed: Sonnet, via `grimme-ui-catalog`.)

---

## Phase 0 — Setup (main thread)

1. Require the Figma node URL arg. Ask if missing.
2. Ensure `catalog.md` is current: run `grimme-ui-catalog`'s staleness check; if drifted
   or absent, refresh it (that skill) before continuing. Load `catalog.md` into context.
3. Load the Figma MCP. If the binding read is needed (it will be — see Phase B), load
   the `/figma-use` skill first so `use_figma` is available.
4. **Ask the user: "Is there a separate mobile/tablet node?"** A Figma node is one
   viewport — breakpoints are not node properties. If yes, take that URL too; if no,
   responsive will be *inferred* and the assumptions flagged.
5. **Accept optional scope context** — an ADO ticket URL and/or freetext ("only the card
   grid + CTA"). This drives Phase A scoping and intent; it does **not** override canvas
   values (ticket/context = *what to look at*; Figma = *the design values*). If a ticket
   is given, fetch it and keep its ID for Phase D (the `[SPEC]` files as its child).
6. **Accept additional nodes by role.** One implementation can span several nodes. Each
   extra node URL carries a role, read from the freetext context, on one of two axes:
   - **`viewport:*`** (mobile / tablet) — same design, different breakpoint (see step 4).
   - **`state:*`** (empty / loading / error / …) — same viewport, different **data state**
     (e.g. a populated list node + its empty-state node).
   Keep the axes separate: viewport nodes feed responsive notes; state nodes feed the
   region's **Data states** (Phase C). Infer the role from context; if ambiguous, ask —
   never merge a data-state node into the mobile/viewport slot.

## Phase A — Decompose & scope (Sonnet)

`get_metadata` on the page node → enumerate region sub-nodes (hero, card grid, CTA,
table, form, footer, …). Produce a **region list with node IDs**. Do **not** feed the
whole page to one agent — the Figma MCP degrades badly on whole-page selections. One
region = one node ID = one downstream agent.

Then **scope** the list — a page node arrives with app chrome (left navbar, global
header/footer) that is noise for a feature spec:

1. Classify each region **content** vs **app-chrome** — heuristics on layer names
   (`Navbar`, `Sidebar`, `TopBar`, `Footer`), pinned/fixed position, and "repeats on
   every page" shape.
2. Fold in the Phase 0 scope context (ADO ticket + freetext) as the deciding input — an
   explicit "only the card grid" overrides the heuristic.
3. **Auto-skip when scope is explicit:** if the context names the regions unambiguously,
   proceed with just those and simply **`log()` the excluded regions**. Only **pause for
   confirmation** when scope is fuzzy — present the annotated in-scope / excluded list.
4. **Record the accepted scope** — it goes into `page-spec.md` as an "Excluded regions"
   note so re-runs are deterministic and the exclusion is auditable.

Decompose **each provided node** (primary + any `viewport:*` / `state:*` nodes) this way,
and tag every resulting region with its source-node role so Phase C can group the same
region across viewports / data states. Only in-scope regions fan out to Phase B.

## Phase B — Region agents (Sonnet ×N, parallel)

One agent per region, each scoped to its sub-node, driven by
`references/region-agent-prompt.md`. Each performs full extraction and returns
**structured findings** (the JSON-ish schema in that prompt, so synthesis merges
deterministically):

- **Component match** — infer from the Figma layer name (e.g. slash-separated
  `Component/Variant/Size`) → match against `catalog.md` components + cva variants;
  cross-check the screenshot against the component's Storybook render. Confident →
  record `<Component props/>`. Low confidence → record as an unknown-component gap and
  **surface the parsed mapping for user confirmation**.
- **Colors / tokens** — `get_variable_defs` + the `use_figma` binding read for bound
  variable **names** (never resolve a fill by hex — that silently collapses the token
  tier). Resolve per `resolution-rules.md`: prefer **semantic** token; only a primitive
  matches → recommend it but **flag**; raw hex with no binding → nearest + **always flag**.
- **Typography, spacing** — resolve against catalog dimension/type tokens; flag off-system.
- **Icons** — layered: SystemIcon (catalog) → FontAwesome equivalent → gap (add to
  grimme-ui SystemIcon). Custom SVG → note "inline locally as interim."
- **Layout / placement** — capture the region's containment tree, child order, and
  **auto-layout intent** (direction, gap token, alignment, wrap) so an implementer can
  place every element without a screenshot. Capture *relative* intent, never absolute
  x/y coordinates. Also persist a region reference screenshot into the run dir.

## Phase C — Synthesis & triage (Opus, main thread or one Opus agent)

1. **Dedup / aggregate** gaps across regions by tuple `(property type, resolved value,
   nearest match, component)`. Color tolerance (CIELAB ΔE): `< ~1–2` → auto-merge (same,
   no gap); `1–5` → flag "confirm intent"; `> 5` → off-system gap. One gap = one ticket,
   carrying an aggregated consumer/instance count.
2. **Reconcile by concern.** Region agents extract locally; this pass makes each *concern*
   consistent across the whole page — one color→token map (the same hex must not resolve
   two ways), one component inventory, one type/spacing scale. Principle: **extract by
   region, reconcile by concern.** It reasons over already-extracted findings — no Figma
   re-traversal, no whole-page MCP read.
3. **Merge data states.** Group regions that are the same region across `state:*` nodes
   (e.g. populated list + empty-state list) into one blueprint with a **Data states**
   subsection (populated / empty / loading / error). This is a page/region-level content
   state — distinct from DS-owned component states, which stay DS-owned.
4. **Responsive** — if a mobile node was given, merge responsive notes; otherwise infer
   (table reflow, minor stacking) and record the assumptions explicitly.
5. **Write `page-spec.md`** per `references/page-spec-template.md`: region-by-region
   blueprint — grimme-ui component + props per region, token per color/spacing/type,
   **layout/placement (containment tree + auto-layout intent) + region reference
   screenshot**, **data states** where state nodes were given, component states **only for
   new/unknown components**, responsive notes; gaps marked inline as `⚠ blocked on
   gap-NNN`; cite the relevant `grimme-ui-components-best-practices` rules for HOW.
6. **Write `gaps/gap-NNN-*.md`** per `references/gap-spec-template.md`, one per deduped gap.
7. **STOP — human triage checkpoint.** Present the gap list. The user marks each
   **build-local** vs **escalate**, and confirms/overrides every near-miss,
   suspected-intentional-deviation, and ambiguous-icon flag. **No ADO write happens
   before this.**

## Phase D — Filing (gated — only after triage)

- **Page spec → ADO `[SPEC]`** in **myGRIMME Core** (reuse the `to-spec` pattern). If a
  scope ticket was given in Phase 0, file the `[SPEC]` as its **child**. On re-run,
  search for an existing linked `[SPEC]` and **update** it — never duplicate.
- **Escalated gaps → PBIs** in **GRIMME Libraries**. First **query available work-item
  types** (ADO MCP) to confirm PBI exists; **search the backlog** (title / fingerprint)
  to avoid duplicates; file only new ones; **write the returned work-item IDs back**
  into the gap spec files and into the page spec's inline `blocked on gap-NNN` markers.
- **Build-local gaps** are not filed — the page spec's interim-fallback field carries the
  local recommendation + a `TODO` marker (codemod-friendly API note so it's swappable to
  the DS component later).

Reference PRs as `!<id>` and work items as `#<id>` in any ADO text (separate ID
namespaces — see `~/schmiede-one/CLAUDE.md`).

## Idempotency

Re-running regenerates the local `page-spec.md` and `gaps/` fresh. ADO filing dedups via
backlog search + written-back IDs; the page `[SPEC]` is updated, not duplicated. So a
second run on the same node must create **zero** new PBIs/`[SPEC]`s.

## Output layout

Write specs under a run directory (suggest the scratchpad or a user-named dir):

```
<run-dir>/
  page-spec.md
  screenshots/
    <region>.png          # reference image per in-scope region (verification aid)
  gaps/
    gap-001-<slug>.md
    gap-002-<slug>.md
    ...
```

## What this skill verifies vs what it cannot

It verifies each design property **resolved** against the catalog and each gap was
**triaged** by a human. It cannot verify the design is *right*, that an inferred
component match is correct without user confirmation, or that the eventual code renders
faithfully — that's the implementing skill's job. Report resolved-and-triaged plainly;
never call an inferred match "confirmed" without the user's yes.
