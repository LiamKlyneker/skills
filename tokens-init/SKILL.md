---
name: tokens-init
description: Bootstrap a repo's semantic token system from a Figma seed node (foundations frame or representative component). Harvests variables via the Figma MCP, classifies primitive/semantic tiers, emits CSS variables + Tailwind theme mapping, and generates the repo's ui-profile skill. Use when a repo has no token system yet, the user says "init tokens", "bootstrap tokens from Figma", or "/tokens-init <node-url>".
---

# Tokens Init

Seed a repo's token system from Figma. The Figma MCP's `get_variable_defs` is **node-scoped** (there is no file-wide variable dump below Enterprise), so bootstrap is inherently seeded: the better the seed node, the more complete the system.

This skill is Phase 1 (Foundations) of the future `ui-foundation` skill, shipped standalone.

## Prerequisites

- Official Figma MCP connected (`get_metadata`, `get_variable_defs`, `get_screenshot`). STOP if absent.
- A paid Dev/Full seat on Figma Professional+ (free seats are rate-limited to uselessness). See `../figma-component/references/install.md`.

## Process

### 1. Preflight

- Detect an existing token system (Tailwind v4 `@theme` block, a `tokens.css`, populated `theme.extend` colors). If found → STOP: this skill bootstraps, it doesn't merge. Report what exists and point at `figma-component` (which resolves against existing tokens) or the future `ui-foundation` (migration).
- Detect Tailwind version → emission format: v4 `@theme` in CSS vs v3 `tailwind.config` `theme.extend`.
- Locate the CSS entry point.

### 2. Seed

Argument is a Figma node URL. If not passed, ask — normally the only question: "Paste your foundations/style-guide frame URL (the frame with color swatches / type specimens). No foundations page? Paste your most representative component."

### 3. Harvest

`get_metadata` (map the node, record its name), `get_variable_defs` (variable names + values), `get_screenshot` (sanity-check the harvest against what's visible — values on screen but missing from the defs mean raw, unbound fills).

### 4. Classify tiers

Per `../_shared/ui-standard.md`. Figma naming usually encodes the tier: palette-style (`color/brand/green-500`) → primitive; usage-style (`color/surface/primary`) → semantic. Figma modes → light/dark overrides.

Batch ALL ambiguities into ONE question set with recommended answers (e.g. "`green-2` is used directly as a fill in the seed — primitive exposed by mistake, or intentionally semantic?"). Do not trickle questions.

### 5. Emit

- `tokens.css` (or the repo's CSS entry): primitives + semantic aliases as CSS custom properties; mode overrides if Figma modes exist.
- The Tailwind mapping, in the detected format.
- The **ui-profile** project skill at `.claude/skills/<repo>-ui/SKILL.md` per `../figma-component/references/ui-profile.md`, seeded with the Figma → code token map.

### 6. Report

- Token inventory table: Figma name → CSS var → Tailwind utility, grouped by tier.
- Gap/hygiene findings vs the designer contract (`../_shared/ui-standard.md`): e.g. "seed has no spacing/radius variables — raw values found", "3 fills bound to raw hex, not variables".
- Next step: `/figma-component <component-node-url>`.

Leave the working tree **uncommitted**.
