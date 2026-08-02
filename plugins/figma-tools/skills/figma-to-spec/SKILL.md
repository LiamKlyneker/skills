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
  version: "1.8.0"
---

# Figma → Spec

Turn one Figma **page** node into two linked artifacts:

1. a **page-implementation spec** (region-by-region, on-system, filed as an ADO
   `[DESIGN-SPEC]` in **myGRIMME Core**), and
2. **N design-system gap specs** (one per real gap, triaged by the user, then filed
   as PBIs on the **GRIMME Libraries** backlog).

**This skill is a spec producer, not a builder.** It never writes page code. The specs
it emits are implemented later — by a downstream build workflow (e.g. `develop-ticket`) or
a human.

**The spec is high-fidelity; the 1:1 risk lives at implementation — which this skill hands
off.** Extraction can be near-complete (the region subagents read bound variable names,
tokens, spacing, and layout intent straight off the canvas); what no tool can guarantee is
that the *eventual rendered code* is faithful. So: resolve the design against what the DS
actually offers, capture layout precisely enough to place every element, and route every gap
through a **human triage checkpoint** — the point of the skill, never automated past. Three
residual uncertainties it flags rather than hides: inferred component identity (no Code
Connect), responsive behavior absent from a single node, and interaction states.

## Prerequisites

Depends on **inputs and capabilities**, not on sibling skills being invokable. Skills resolve
by directory scope, so a run rooted in a consumer repo (e.g. `mygrimme-frontend`) **cannot
invoke** Marketplace skills like `grimme-ui-catalog` or `/figma-use`. Every dependency is
detachable:

- **`catalog.md` (required artifact).** The existence source — what tells the spec which
  classname, semantic token, component, and cva variant actually exist. **Bundled at
  `references/catalog.md`**, so a run needs no cross-repo path. Resolution order: a **passed
  arg** → else the **bundled copy** → else ask. The `grimme-ui-catalog` *skill* is only needed
  to *(re)generate* it. Staleness is opportunistic and soft (Phase 0 step 2) — never a hard
  fail.
- **Figma MCP — two distinct capability checks, do not conflate them:**
  1. **`figma-dev-mode` present (required):** `get_metadata`, `get_variable_defs`,
     `get_screenshot`, `get_design_context`. STOP if this server is absent — no fallback.
  2. **Binding read (`use_figma`, via `/figma-use`) available (strongly preferred, separate
     server):** resolves each node's `boundVariables` → variable **name per property**. If
     unreachable, the run continues in **degraded color mode** — token *names* survive via
     `get_variable_defs`, per-property bindings do not, and every color is flagged unverified.
     `agents/figma-region-extractor.md` step 4 is the **normative** statement of that rule
     and its `bindingVerified` schema requirement; announce degraded mode up front and never
     present an unverified value as on-system.
- **A Figma node URL** (a page/frame, or a single component node in component mode). Missing
  → ask, never guess.
- **`figma-region-extractor` subagent (preferred, detachable).** Phase B's extraction
  contract lives at `agents/figma-region-extractor.md`. The `figma-tools` plugin provides
  the agent and namespaces it, so the type is **`figma-tools:figma-region-extractor`** on
  every route — installed from the marketplace, or loaded with `claude --plugin-dir`. There
  is no unprefixed form. Spawned by type it is pinned to Sonnet with write tools
  denied; if that name does not resolve, Phase B reads that same file and pastes its body
  into a `general-purpose` agent. One source of truth either way — but a freshly installed
  agent does not register until the next session, so Phase 0 checks and announces which
  path the run takes.
- **`grimme-ui-components-best-practices` (optional).** The page spec **cites** its rules by
  stable name and never duplicates them, so citations stand even when it isn't loaded. Load it
  to enrich HOW-guidance only if reachable.

## Resolution sources (what "does it exist?" reads)

- **Existence** → the `catalog.md` **artifact** (components, cva variants, tokens by tier,
  SYSTEM_ICONS keys), read from the bundle or an arg override — not by invoking
  `grimme-ui-catalog`. The ONLY source for "does the DS have this?".
- **Usage / HOW** → `grimme-ui-components-best-practices` rules, **cited by stable name**. The
  page spec cites; never duplicates.
- **Resolution + tolerance rules** → `references/resolution-rules.md` (bundled).

grimme-ui has **no Code Connect and no documented Figma-name↔code mapping** — component
detection **infers** by layer-name convention + visual confirmation. Deliberately loose for
v1: surface low-confidence matches for user confirmation rather than guessing silently.

## Phases

Read `references/phases.md` for the phase you are running — it carries the full procedure.
Region agents are driven by `agents/figma-region-extractor.md`.

| Phase | Model | Does |
|---|---|---|
| **0 — Setup** | main thread | Resolve catalog + check staleness · confirm Figma capability · collect extra nodes by role (`viewport:*` / `state:*`) · collect scope context · pick run mode (`page` default / `component` lean). |
| **A — Decompose & scope** | Sonnet | Enumerate regions by node ID (recursing through pass-through wrappers), then assign each `in-scope` / `spec-only` / `excluded`. `in-scope` + `spec-only` fan out. |
| **B — Region agents** | `figma-tools:figma-region-extractor` (Sonnet) ×N parallel | One agent per region: components, colors/tokens, type, spacing, icons, hidden variants, layout intent → structured JSON findings. |
| **C — Synthesis & triage** | Opus | Dedup gaps · reconcile by concern · merge data states + responsive · changelog vs prior spec · write `page-spec.md` + `gaps/gap-NNN-*.md` · **triage checkpoint**. |
| **D — Filing** | main thread | Page spec → ADO `[DESIGN-SPEC]` (child of the scope ticket) · escalated gaps → PBIs, IDs written back. |

(Catalog refresh, if it's needed: Sonnet, via `grimme-ui-catalog`.)

**STOP gates — none of these is automatable:**

1. **`figma-dev-mode` absent** → stop. There is no fallback (Phase 0).
2. **No resolvable `catalog.md`** → stop. (Staleness alone never stops a run.)
3. **Scope or node-canonicity conflict** between the ticket and the freetext → ask, don't
   silently pick (Phase 0).
4. **Human triage checkpoint** (Phase C step 8) → present every gap and flag; the user marks
   build-local vs escalate. **No ADO write happens before this** — including in component
   mode, which still triages even though it files nothing.

Two extraction rules the regression fixtures exist to protect: **never resolve a fill by hex**
(it silently collapses the token tier) and **never record absolute x/y coordinates** (layout
output is relative auto-layout intent only). Both are normative in
`agents/figma-region-extractor.md`.

## Idempotency & output

Re-running regenerates the local `page-spec.md` and `gaps/` fresh; ADO filing dedups via
backlog search + written-back IDs, and the page `[DESIGN-SPEC]` is updated, not duplicated. A second
run on the same node must create **zero** new PBIs/`[DESIGN-SPEC]`s. Write under a run directory
(suggest the scratchpad or a user-named dir): `page-spec.md` plus `gaps/gap-NNN-<slug>.md`.

Screenshots are **not** persisted — `get_screenshot` returns an inline image, not a path.
Region agents view it inline; the layout tree + auto-layout intent are the durable truth.

## What this skill verifies vs what it cannot

It verifies each design property **resolved** against the catalog and each gap was **triaged**
by a human. It cannot verify the design is *right*, that an inferred match is correct without
user confirmation, or that the eventual code renders faithfully — that's the implementing
skill's job. Never call an inferred match "confirmed" without the user's yes.

Regression fixtures for the highest-risk silent-correctness defects live in
`references/regression/` — run them after changing any extraction or enumeration rule.
