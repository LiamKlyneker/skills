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

1. a **page-implementation spec** (region-by-region, on-system, filed as a `[DESIGN-SPEC]`
   against the adapter's **design-spec target**), and
2. **N design-system gap specs** (one per real gap, triaged by the user, then the escalated
   ones filed against the adapter's **DS-gap backlog**).

**Where both of those land is the project adapter's answer, not this skill's.** Phase D reads
the adapter's `Tracker:` line and runs the matching filing profile — GitHub issues, or Azure
DevOps work items — against two separate rows, because a design system's gaps routinely live
somewhere other than the code being specced.

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

- **A project design-system catalog (required artifact).** The existence source — what tells
  the spec which class, token, component, and variant value actually exist. It is a
  **per-project artifact in the consuming repo**, never bundled here, and it is registered in
  the adapter's `## Design system` section by pointer — the same pattern as `## Project gates`,
  so this skill never names its filename. Resolution order: **passed arg → the adapter's
  catalog pointer → ask**, stopping there. Its required shape is
  `references/catalog-contract.md`; Phase 0 validates the resolved file against it and **fails
  loudly** rather than degrading. Staleness is a separate, soft check (Phase 0 step 2c) —
  never a hard fail.
- **The project adapter (`<repo-root>/.claude/project/adapter.md`), two sections of it.**
  `## Design system` carries the catalog pointer, the fingerprint command, the class-prefix
  facts and the icon ladder; `## Repo` carries the `Tracker:` line Phase D branches on plus the
  **design-spec target** and **DS-gap backlog** rows it files against. Two of that section's
  rows are optional and their absence is the answer, never a warning: no *usage-rules source*
  means the spec cites nothing, and no *downstream implementer* means a human picks the spec
  up. `install-skills` writes both sections — the `figma-tools` bundle asks for them.
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

- **Existence** → the project **catalog** artifact (components + variant axes and values,
  tokens by tier, typography utilities, icon sources), resolved and validated in Phase 0. The
  ONLY source for "does the DS have this?".
- **Catalog shape** → `references/catalog-contract.md` (bundled) — the required sections, the
  `status: current|legacy|deprecated` schema, and the Phase 0 validation rules.
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
| **0 — Setup** | main thread | Resolve catalog (arg → adapter pointer → ask) + validate against the shape contract + soft staleness check · confirm Figma capability · collect extra nodes by role (`viewport:*` / `state:*`) · collect scope context · pick run mode (`page` default / `component` lean). |
| **A — Decompose & scope** | Sonnet | Enumerate regions by node ID (recursing through pass-through wrappers), then assign each `in-scope` / `spec-only` / `excluded`. `in-scope` + `spec-only` fan out. |
| **B — Region agents** | `figma-tools:figma-region-extractor` (Sonnet) ×N parallel | One agent per region: components, colors/tokens, type, spacing, icons, hidden variants, layout intent → structured JSON findings. |
| **C — Synthesis & triage** | Opus | Dedup gaps · reconcile by concern · merge data states + responsive · changelog vs prior spec · write `page-spec.md` + `gaps/gap-NNN-*.md` · **triage checkpoint**. |
| **D — Filing** | main thread | Branch on the adapter's `Tracker:` line. Page spec → `[DESIGN-SPEC]` on the **design-spec target**, parented to the scope ticket (native sub-issue on GitHub, child work item on ADO) · escalated gaps → the **DS-gap backlog**, ids written back. |

(Catalog refresh, if it's needed: Sonnet, via `grimme-ui-catalog`.)

**STOP gates — none of these is automatable:**

1. **`figma-dev-mode` absent** → stop. There is no fallback (Phase 0).
2. **No resolvable catalog, or one that fails `references/catalog-contract.md`** → stop, naming
   the path and the rule that failed. (Staleness alone never stops a run.)
3. **Scope or node-canonicity conflict** between the ticket and the freetext → ask, don't
   silently pick (Phase 0).
4. **Human triage checkpoint** (Phase C step 8) → present every gap and flag; the user marks
   each **escalate** / **compose-from-tokens** / **build-local**, and every non-escalated
   decision records a one-line rationale in its gap file. **No tracker write happens before
   this**, on either tracker — including in component mode, which still triages even though it
   files nothing.

Four extraction rules the regression fixtures exist to protect: **never resolve a fill by
hex** (it silently collapses the token tier), **never record absolute x/y coordinates**
(layout output is relative auto-layout intent only), **never match across property kinds** (a
stroke must not resolve to a spacing token), and **never enumerate the interior geometry of an
icon** (it resolves as a whole; its paths are drawing data). All four are normative in
`agents/figma-region-extractor.md` and `references/resolution-rules.md`.

## Idempotency & output

Re-running regenerates the local `page-spec.md` and `gaps/` fresh; filing dedups via a search
of the filing target + written-back ids, on either tracker, and the page `[DESIGN-SPEC]` is
updated, not duplicated — including one still titled with the legacy `[SPEC]` prefix, which the
dedup search also matches. A second
run on the same node must create **zero** new gap tickets/`[DESIGN-SPEC]`s. Write under a run directory
(suggest the scratchpad or a user-named dir): `page-spec.md` plus `gaps/gap-NNN-<slug>.md`.

Screenshots are **not** persisted — `get_screenshot` returns an inline image, not a path.
Region agents view it inline; the layout tree + auto-layout intent are the durable truth.

## What this skill verifies vs what it cannot

It verifies each design property **resolved** against the catalog and each gap was **triaged**
by a human. It cannot verify the design is *right*, that an inferred match is correct without
user confirmation, or that the eventual code renders faithfully — that's the implementing
skill's job. Never call an inferred match "confirmed" without the user's yes.

The regression **fixture format** and **expected-findings assertion style** live in
`references/regression/`; concrete fixtures are per-project (they pin real node IDs) and are
optionally registered in the adapter. Re-running them is a **documented pre-release step** —
triggered by any change to an extraction or enumeration rule, before that change ships — and
explicitly **not CI**, which cannot drive a live authenticated Figma session.
