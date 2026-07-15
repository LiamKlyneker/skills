---
name: figma-component
description: Build a production component from a Figma node — scoped MCP triage, Token + Primitive Manifests resolved against the repo, pattern research (APG/shadcn/headless), component + CSF3 story variants, render verification against the Figma spec, manifest + hygiene report. Autonomous; asks only at one batched checkpoint when something won't resolve. Use when handed a Figma component/node URL to implement, "build this component from Figma", or "/figma-component <node-url>".
---

# Figma Component

Turn one Figma node into: the coded component, its story variants, and a token/primitive manifest — asking the user only when the design genuinely collides with something (unresolvable token, industry standard, naming mismatch).

**Ask policy — silent when clean.** If every token and primitive resolves and nothing collides, build and ship without a single question; the manifest arrives as a report. Everything unresolvable batches into ONE checkpoint at the triage boundary. Never ask mid-build.

## Prerequisites

- Official Figma MCP (`get_metadata`, `get_variable_defs`, `get_screenshot`, `get_design_context`) — STOP if absent; do not substitute a screenshots-only flow. Setup: `references/install.md`.
- A Figma node URL. Missing → ask; do not guess.
- Feed discipline throughout: `references/figma-feed.md`.

## Phase 1 — Profile

Load the repo's ui-profile skill (`.claude/skills/<repo>-ui/SKILL.md`).

- **Absent** → read-only discovery: token definitions (Tailwind theme / `tokens.css`), primitive homes (`components/ui`, shared lib, colocated `_components/`), Storybook config + the prevailing story idiom, how tokens are consumed. Write the profile per `references/ui-profile.md`.
- **No token system at all** → STOP: the repo needs `/tokens-init` first. Offer to run it inline with a seed node.
- **Probe the styling layer** if the repo has a `cn()`/merge helper *and* semantic names that reuse a built-in namespace (`text-body`, `bg-surface`): confirm a style + colour survive together before building on it. One command, `references/render-verification.md`. A broken helper silently erases tokens from every component in the repo — finding it here beats finding it in Phase 5.

## Phase 2 — Triage

1. `get_metadata` on the node — map it; **record URL + node name** (feeds the design reference downstream).
2. **Enumerate every variant/state** from metadata (component-set siblings/children). Never generalize from one screenshot. `get_screenshot` per variant.
3. `get_variable_defs` → build the **Token Manifest**; from screenshots + metadata build the variant table and the **UI Primitive Manifest** — both per `../_shared/ui-manifests.md`, resolved against the ui-profile.
   - Then the **binding read** (`references/figma-feed.md`): one read-only `use_figma` script resolving `boundVariables` → variable names per property, per variant. Nothing else exposes this, and **resolving a fill by hex instead of by bound name silently collapses the token tier** — two semantics routinely share one primitive. Capture the type numbers here; Phase 5 checks the render against them.
4. Pattern research per `references/pattern-precedent.md` → a short **pattern precedent** note.
5. Collect designer-contract violations (raw unbound values, missing auto layout, non-code-friendly properties) for the hygiene report — findings, not blockers.

## Phase 3 — Checkpoint (conditional)

- All manifest rows ✅ and no design≠standard collisions → **proceed silently**.
- Otherwise: ONE batched question set covering every unresolved ⚠️/❌ row, token-minting decision, standard collision, and naming mismatch — each with a recommended answer. After answers, build without further questions.

## Phase 4 — Build

- Implementation path per the precedence ladder (`references/pattern-precedent.md`).
- Semantic tokens only — never a raw palette class or hex (hard rule, `../_shared/ui-standard.md`).
- `cva` variants; **naming parity**: Figma property = component prop = story arg.
- CSF3 stories per the story contract in `../_shared/ui-standard.md`: story per variant axis, `AllVariants` grid, autodocs, play functions where behavior exists **or where a styling failure would be silent**. On conflict, the repo's existing story idiom (profile) beats the canon.

## Phase 5 — Verify the render

A ✅ manifest means the token **resolved**, not that it **survived to the screen**. These failures are silent: they type-check, lint, pass their stories, and look approximately right. Recipe + traps: `references/render-verification.md`.

- Typecheck, then run the repo's story/test suite.
- Render at least the default variant in the real harness and read **computed styles** — size/line-height/weight, colours, box — against the Phase 2 numbers. A screenshot doesn't count: it proves layout, not type.
- A utility in source but **missing from the DOM class list** = the styling layer erased it. That's a **repo-wide** defect → fix the profile's helper; never dodge it in the component.
- Leave a regression guard wherever the failure would be invisible, and **prove it fails without the fix**.

## Phase 6 — Report & persist

Deliver in the final report:

1. **Token Manifest + UI Primitive Manifest** — final state, as tables.
2. **Pattern precedent** note.
3. **Figma hygiene report** — designer-contract violations (checklist in `../_shared/ui-standard.md`).
4. **Verification** — what Phase 5 proved: computed values checked against which Figma numbers, suites run. Name any repo-wide defect found; it outranks the component in importance.

Persist:

- Node URL + node name → the area's `CONTEXT.md` `## Design reference` table (scoped-context convention). If the repo has no CONTEXT convention, record in the ui-profile's fallback table instead.
- Newly minted tokens/primitives → the ui-profile's map + minted log (with date).

Leave the working tree **uncommitted**. Close by separating what Phase 5 **proved** — computed values matching the Figma spec, suites green — from what it **cannot**: whether the design is *right*, and whether the component reads well in a real screen. Fidelity is verified; intent is the user's call. Never report "verified" for anything you only looked at.
