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
  version: "1.5.0"
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

This skill depends on **inputs and capabilities**, not on sibling skills being invokable
from the current session. Skills resolve by directory scope, so a run rooted in a consumer
repo (e.g. `mygrimme-frontend`) **cannot invoke** Marketplace skills like
`grimme-ui-catalog`, `grimme-ui-components-best-practices`, or `/figma-use`. Treat every
dependency as detachable:

- **`catalog.md` (required artifact).** The existence source — and foundational: it's what
  tells the spec which classname, semantic token, component, and cva variant actually
  exist. **Bundled with this skill at `references/catalog.md`** (v1.5.0), so a run needs no
  cross-repo path. Resolution order: a **passed arg** overrides → else the **bundled
  `references/catalog.md`** → else ask. The `grimme-ui-catalog` *skill* is only needed to
  *(re)generate* it, and only if reachable; the skill runs fine from the bundled file.
  Staleness is **opportunistic and soft** — see Phase 0 step 2 — never a hard fail.
  *(Trade recorded: the bundled copy can drift from live grimme-ui until regenerated. This
  reverses the earlier "reference by path, one source of truth" stance deliberately, to let
  the skill be tested self-contained. `TODO: initiate mode` — a future skill mode that
  regenerates `references/catalog.md` in place — retires the manual copy.)*
- **Figma MCP — two distinct capability checks, do not conflate them:**
  1. **`figma-dev-mode` present (required):** `get_metadata`, `get_variable_defs`,
     `get_screenshot`, `get_design_context`. STOP if this server is absent — no fallback.
  2. **Binding read (`use_figma`, via `/figma-use`) available (strongly preferred, separate
     server):** resolves each node's `boundVariables` → variable **name per property**. If
     unreachable, **degrade** — but *not* to pure hex: `get_variable_defs` still yields
     region-level name→value, so you keep token **names**; what's lost is the *per-property*
     binding, so flag every color `binding-unverified` (its tier is unconfirmed). Never
     silently treat an unverified value as on-system. (Call discipline is spelled out in
     `references/region-agent-prompt.md`; the same traps apply here.)
- **A Figma node URL** (a page/frame, or a single component node in component mode).
  Missing → ask, never guess.
- **`grimme-ui-components-best-practices` (optional).** The page spec **cites** its rules
  by stable name and never duplicates them — so citations stand even when the skill isn't
  loaded. Load it to enrich HOW-guidance only if reachable.

## Resolution sources (what "does it exist?" reads)

- **Existence** → the `catalog.md` **artifact** (components, cva variants, tokens by tier,
  SYSTEM_ICONS keys), read from the **bundled `references/catalog.md`** (or an arg override)
  — not by invoking `grimme-ui-catalog`. This is the ONLY source for "does the DS have
  this?".
- **Usage / HOW** → `grimme-ui-components-best-practices` rules, **cited by stable name**
  (loaded if reachable; citations stand regardless). The page spec cites; never duplicates.
- **Resolution + tolerance rules** → `references/resolution-rules.md` (bundled with this
  skill — always available).

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
2. **Resolve `catalog.md`** — arg override → else the bundled `references/catalog.md` → else
   ask. Read it in. Then run the **skill-free staleness check** (no `grimme-ui-catalog`
   invocation needed): if `~/schmiede-one/grimme-ui` is reachable, recompute the fingerprint
   over its source-of-truth files and compare to the catalog's line-1 stamp —

   ```
   shasum \
     <(sed -n '/"exports"/,/^  }/p' ~/schmiede-one/grimme-ui/package.json) \
     ~/schmiede-one/grimme-ui/theme/tokens/primitives.generated.css \
     ~/schmiede-one/grimme-ui/theme/tokens/alias.generated.css \
     ~/schmiede-one/grimme-ui/theme/tokens/semantic.generated.css \
     ~/schmiede-one/grimme-ui/theme/tokens/dimensions.generated.css \
     ~/schmiede-one/grimme-ui/system_icons/_list.tsx \
     | shasum | cut -d' ' -f1
   ```

   Match → note "catalog current". Mismatch → **soft-warn** ("bundled catalog may lag live
   grimme-ui — regenerate via `grimme-ui-catalog`") and **continue**. grimme-ui not reachable
   → note "bundled snapshot, staleness unchecked" and continue. **Never hard-fail on
   staleness.** The only hard STOP here is no resolvable `catalog.md` at all. *(Caveat: this
   recipe uses process-substitution paths, so it's reproducible on one machine but not
   portable across machines — fine for local runs; the future initiate mode should switch to
   a path-independent hash.)*
3. **Confirm Figma capability — two separate checks (Prerequisites).** (a) Ensure
   **`figma-dev-mode`** is present — STOP if not. (b) Try to make the binding read
   (`use_figma`) available (load `/figma-use` if reachable). If it isn't, continue in
   **degraded color mode** — token **names** still come from `get_variable_defs`
   (region-level), but per-property bindings are lost, so every color is flagged
   `binding-unverified` — and announce that up front so the user knows token tiers are
   unconfirmed.
4. **Ask the user: "Is there a separate mobile/tablet node?"** A Figma node is one
   viewport — breakpoints are not node properties. If yes, take that URL too; if no,
   responsive will be *inferred* and the assumptions flagged.
5. **Accept optional scope context** — an ADO ticket URL and/or freetext ("only the card
   grid + CTA"). This drives Phase A scoping and intent; it does **not** override canvas
   values (ticket/context = *what to look at*; Figma = *the design values*). If a ticket
   is given, fetch it and keep its ID for Phase D (the `[SPEC]` files as its child).

   **Scope precedence:** freetext (the most recent explicit human instruction) **>** ticket
   scope **>** the Phase A layer-name heuristic. The ticket is context/default; freetext
   overrides it.

   **Conflict gate (STOP and ask — don't silently pick).** Two conflicts surface here, both
   cheap to resolve before any fan-out:
   - **Scope conflict:** the ticket scopes narrower/differently than the freetext (e.g. the
     ticket is "1/4" — search only — while the freetext also names create-button +
     card-actions from sibling stories). Surface both and ask which governs. Offer the
     third option the user may actually want: **spec the wider set, but mark the
     out-of-ticket regions `spec-only`** (fully specced, *not* integrated this pass — see
     Phase A dispositions).
   - **Node canonicity:** the ticket links a different primary node than the invocation URL.
     Default recommendation: the **invocation node** is the design source (Figma = values).
     Ask whether to (a) use the given node, (b) switch to the ticket's node, or (c) treat
     them as multiple nodes by role (step 6). Never assume.
6. **Accept additional nodes by role.** One implementation can span several nodes. Each
   extra node URL carries a role, read from the freetext context, on one of two axes:
   - **`viewport:*`** (mobile / tablet) — same design, different breakpoint (see step 4).
   - **`state:*`** (empty / loading / error / …) — same viewport, different **data state**
     (e.g. a populated list node + its empty-state node).
   Keep the axes separate: viewport nodes feed responsive notes; state nodes feed the
   region's **Data states** (Phase C). Infer the role from context; if ambiguous, ask —
   never merge a data-state node into the mobile/viewport slot.
7. **Determine the run mode — from the prompt, not the node.** Node geometry can *suggest*
   granularity but cannot tell you *intent* (a Card node might be a fresh build or a
   one-line padding tweak). Read the mode from the invocation:
   - **`page` (default)** — full decompose + fan-out + full page-spec; auto-files an ADO
     `[SPEC]` (Phase D).
   - **`component` (lean)** — the prompt scopes to a single node / component ("lean
     update", "single-component / single-node", "only X changed", "just this node",
     "already implemented — give me the delta"). No fan-out; emit a lean **component-delta
     spec** (one region blueprint + changelog); **files nothing unless the user explicitly
     asks** (local artifacts only); the triage checkpoint still runs — never silently
     accept an off-system value, even for one node.
   Node structure (child count / depth via `get_metadata`) is only a sanity check. If the
   prompt is silent and the node looks like a lone component, **confirm — don't assume**.

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
   - **Granularity / thin sub-headers:** a *thin* structural header that carries
     page-**feature** content (e.g. a feature "Top Bar" with the page title + a search
     field) is its **own region**, not chrome. A *repeated global* bar is chrome. When a
     node is genuinely ambiguous (neither clearly a region nor chrome), default to
     **including it as a region and `log()` the call**; only pause to ask if scope is fuzzy.
2. Fold in the Phase 0 scope context (ADO ticket + freetext) per the **precedence** in
   Phase 0 step 5 (freetext > ticket > heuristic) — an explicit "only the card grid"
   overrides the heuristic.
3. **Assign each region one of three dispositions:**
   - **`in-scope`** — specced *and* handed off for implementation.
   - **`spec-only`** — fully specced (blueprint, tokens, layout, gaps) but flagged **not to
     be integrated this pass** ("leave as-is / UI-only"). This is the "spec the whole page,
     but don't build part X yet" case from the Phase 0 conflict gate. It still fans out to a
     Phase B agent and still runs triage — it just carries a banner downstream so
     `develop-ticket` / a human skips integration.
   - **`excluded`** — app chrome or clearly out of scope; not specced.
4. **Auto-skip when scope is explicit:** if the context names dispositions unambiguously,
   proceed and simply **`log()`** the `spec-only` and `excluded` regions. Only **pause for
   confirmation** when scope is fuzzy — present the annotated in-scope / spec-only / excluded
   list.
5. **Record the accepted dispositions** — they go into `page-spec.md` as a "Scope
   dispositions" note (in-scope / spec-only / excluded) so re-runs are deterministic and the
   scope is auditable.

Decompose **each provided node** (primary + any `viewport:*` / `state:*` nodes) this way,
and tag every resulting region with its source-node role so Phase C can group the same
region across viewports / data states. **`in-scope` and `spec-only` regions fan out to
Phase B; `excluded` regions do not.**

In **component mode** there is nothing to fan out: the node *is* the single region — skip
enumeration and hand it straight to one Phase B agent.

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
  x/y coordinates (input-vs-output rule in `references/region-agent-prompt.md`).
  `get_screenshot` is viewed inline by the agent as a visual check during extraction; under
  `figma-dev-mode` it returns an inline image, **not a file path**, so it is **not
  persisted** — the layout tree is the source of truth, not a saved image.

**Session lifetime.** `figma-dev-mode` sessions can expire on long parallel runs (~10–15
min/agent). The call ordering (`get_design_context` LAST) front-loads the essential reads
so a late failure is non-fatal. On session loss, re-auth and **re-run only the affected
region agent** — extraction is per-region and idempotent.

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
5. **Changelog / delta (if a prior spec exists).** If a previous `page-spec.md` (run-dir)
   or a linked ADO `[SPEC]` is found, diff **new spec vs old spec** — spec-vs-spec, never
   spec-vs-code — and emit a **Changelog** section (what changed: tokens, props, layout,
   copy; what stayed). Mark affected regions `△ changed`. No prior baseline → note "new
   spec, no prior" and skip. Computing the *code*-level delta is the implementer's job
   (`develop-ticket` reconciles this spec against live code and touches only what differs);
   this skill stays a pure function of the Figma node.
6. **Write the spec** per `references/page-spec-template.md`. **Page mode:** full
   region-by-region blueprint. **Component mode:** just the one targeted region's
   blueprint. Either way — grimme-ui component + props, token per color/spacing/type,
   **layout/placement (containment tree + auto-layout intent)**, **data states** where
   state nodes were given, component states **only for new/unknown components**, responsive
   notes, and the **Changelog** from step 5 up top; gaps marked inline as `⚠ blocked on
   gap-NNN`; cite the relevant `grimme-ui-components-best-practices` rules for HOW. Record
   the **Scope dispositions** (in-scope / spec-only / excluded); prefix every `spec-only`
   region's heading with a **`spec-only — not integrated this pass`** banner so the
   implementer skips it.
7. **Write `gaps/gap-NNN-*.md`** per `references/gap-spec-template.md`, one per deduped gap.
8. **STOP — human triage checkpoint.** Present the gap list. The user marks each
   **build-local** vs **escalate**, and confirms/overrides every near-miss,
   suspected-intentional-deviation, and ambiguous-icon flag. **No ADO write happens
   before this.**

## Phase D — Filing (gated — only after triage)

- **Page spec → ADO `[SPEC]`** in **myGRIMME Core** (reuse the `to-spec` pattern). If a
  scope ticket was given in Phase 0, file the `[SPEC]` as its **child**. On re-run,
  search for an existing linked `[SPEC]` and **update** it — never duplicate. *(Component
  mode files nothing by default — no `[SPEC]`, no PBIs — unless the user explicitly asks;
  it produces local artifacts only.)*
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
  gaps/
    gap-001-<slug>.md
    gap-002-<slug>.md
    ...
```

Screenshots are **not** persisted — under `figma-dev-mode`, `get_screenshot` returns an
inline image, not a file path. Region agents view it inline during extraction; the layout
tree + auto-layout intent are the durable source of truth.

## What this skill verifies vs what it cannot

It verifies each design property **resolved** against the catalog and each gap was
**triaged** by a human. It cannot verify the design is *right*, that an inferred
component match is correct without user confirmation, or that the eventual code renders
faithfully — that's the implementing skill's job. Report resolved-and-triaged plainly;
never call an inferred match "confirmed" without the user's yes.
