---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

## Context Loading

If the `scoped-context` skill is available in this project, use it to load relevant `CONTEXT.md` files before beginning the interview. This gives you architectural context to ask better, more informed questions. If scoped-context is not available, proceed without it.

## Design tasks (implementing from a visual design)

When the task involves implementing from a Figma file or other visual design, do extra design-specific grilling **before** any engineering questions:

1. **Study the design.** Open the design node(s), look at every screen/state, and note what's actually drawn — not what you assume. Call out anything ambiguous (which states exist, what's interactive, what's decorative).
2. **Build a variant table.** For every variant (per-card, per-section, per-state) capture: base color, gradient/decoration colors, direction/origin, intensity, any texture or blend. Present the table back to the user and ask them to confirm or correct it before moving on.
3. **Record the design node pointers.** For every distinct area/screen, capture the node **URL** and its **node name** (from the design tool's MCP, e.g. Figma `get_metadata`). These flow downstream into the PRD's `## Design reference` and, after build, into the page's `CONTEXT.md` `## Design reference` table — so a cold implementation/verify session can find the target with zero conversation context.
4. **Build the UI Primitive Manifest (hard gate).** See below.
5. **Propose a vertical slice, not a horizontal plan.** Recommend picking one representative variant, implementing it end-to-end (including the reusable primitive's API), and only then propagating to the rest. Iterating on real pixels for one card will shape the primitive's knobs far better than enumerating everything up-front. Confirm with the user before locking in a multi-section plan.

### UI Primitive Manifest (HARD GATE)

After the variant table, before leaving design questions, build a manifest of **every** primitive the design needs. This is the step that prevents the recurring failure where a missing primitive gets **improvised inline** (e.g. a colored icon-badge rendered as ad-hoc utility classes instead of a shared component), causing the implementation to drift from the design.

For each primitive, classify it:

- ✅ **exists as-is** — a shared primitive already matches.
- ⚠️ **drifts / needs an API change** — covers two cases: (a) the primitive exists but its current API can't express the design (needs a new variant/state/prop), or (b) **brownfield**: it already exists *in the feature code* but as an inline/ad-hoc implementation that should be extracted into a shared primitive (e.g. an inline icon-badge → a shared `IconBadge`).
- ❌ **must be built** — no primitive exists.

For every ⚠️ and ❌ row, resolve **before the grill is "done"**:
- **Home** — a component library (e.g. shadcn) vs the project's custom UI library vs a new dependency.
- **API surface** — props, variants, states, sizes.
- **Consumers** — which screens/cards use it.

This is a **hard gate**: do not conclude the grill while any ⚠️/❌ primitive is unresolved. Treat UI primitives as if they ship from a UI library — each will become its own issue downstream (see the `to-issues` exception). Present the manifest back to the user as a table and get confirmation:

| Primitive | Status | Home | API surface | Consumed by |
|-----------|--------|------|-------------|-------------|
| IconBadge | ❌ build | custom UI library | color, icon, size | feature cards |
| Button | ⚠️ extend | component library | add solid variant | primary CTA |

Only after the variant table, the UI Primitive Manifest, and the vertical-slice approach are agreed on should engineering questions (motion tech, perf gates, breakpoints, reduced-motion, etc.) begin.
