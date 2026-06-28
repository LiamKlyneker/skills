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

**Conditionally load `building-luar-ui`:** if (and only if) this grill implements from a Figma file or other visual design, also consult the `building-luar-ui` skill before the interview so you can resolve primitives and tokens against the real component library. **Skip it for pure-DB / logic grills** — it's noise there.

## Design-to-code triage (run before engineering questions)

When the task involves implementing from a Figma file or other visual design, do this **before** asking any implementation/architecture questions:

1. **Enumerate every distinct visual variant.** Do not generalize from one screenshot. If the user shares a single Figma URL or node, ask whether sibling/child nodes cover variants you haven't seen, and fetch screenshots of each one.
2. **Build a variant table.** For every variant (per-card, per-section, per-state) capture: base color, gradient/decoration colors, direction/origin, intensity, any texture or blend. Present the table back to the user and ask them to confirm or correct it before moving on.
3. **Propose a vertical slice, not a horizontal plan.** Recommend picking one representative variant, implementing it end-to-end (including the reusable primitive's API), and only then propagating to the rest. Iterating on real pixels for one card will shape the primitive's knobs far better than enumerating everything up-front. Confirm with the user before locking in a multi-section plan.

4. **Record the Figma node pointers.** For every distinct area/screen, capture the node **URL** and its **node name** (from `get_metadata`). These flow downstream into the PRD's `## Design reference` and, after build, into the page's `CONTEXT.md` `## Design reference` table — so a cold implementation/verify session can find the target with zero conversation context.

## UI Primitive Manifest (HARD GATE — design tasks only)

After the variant table, before leaving design questions, build a manifest of **every** primitive the design needs. This is the step that prevents the recurring failure where a missing primitive gets **improvised inline** (e.g. a colored icon-badge rendered as ad-hoc Tailwind instead of a shared component), causing the implementation to drift from the design.

For each primitive, classify it:

- ✅ **exists as-is** — a shared `components/ui` or `luar-ui` primitive already matches.
- ⚠️ **drifts / needs an API change** — covers two cases: (a) the primitive exists but its current API can't express the design (needs a new variant/state/prop), or (b) **brownfield**: it already exists *in the feature code* but as an inline/ad-hoc implementation that should be extracted into a shared primitive (e.g. an inline icon-badge → a shared `IconBadge`).
- ❌ **must be built** — no primitive exists.

For every ⚠️ and ❌ row, resolve **before the grill is "done"**:
- **Home** — pick by *earning the abstraction*, not by reflex:
  - `components/ui` (shadcn) — a standard primitive shadcn offers; install it rather than hand-rolling.
  - `luar-ui/` (custom) — a genuinely reusable, **cross-feature** custom primitive. Only promote here once there's a real second consumer.
  - colocated `_components/` — single-consumer for now; hasn't earned shared status yet. Default new bespoke UI here and bubble it up to `luar-ui/` only when a second consumer actually appears.
  - a new dependency — last resort.
- **API surface** — props, variants, states, sizes.
- **Consumers** — which screens/cards use it.

This is a **hard gate**: do not conclude the grill while any ⚠️/❌ primitive is unresolved. Treat UI primitives as if they ship from a UI library — each will become its own issue downstream (see the `to-issues` exception). Present the manifest back to the user as a table and get confirmation:

| Primitive | Status | Home | API surface | Consumed by |
|-----------|--------|------|-------------|-------------|
| IconBadge | ❌ build | luar-ui/ | color, icon, size | Editar-con-IA cards |
| Button | ⚠️ extend | components/ui/ | add solid-green variant | Continuar CTA |

Only after the variant table, the Token Manifest, the UI Primitive Manifest, and the vertical-slice approach are agreed on should engineering questions (motion tech, perf gates, breakpoints, reduced-motion, etc.) begin.

## Token Manifest (HARD GATE — design tasks only)

Run this right after the variant table, alongside the UI Primitive Manifest. Where the Primitive Manifest catches improvised *components*, this catches improvised *tokens* — the other half of the design-drift failure (e.g. mistaking the dark brand color `green-2` for "a green fill", or inventing a raw Tailwind `gray-300` because no semantic token was checked).

Build a manifest of **every** Figma variable/token the design uses and resolve each one to an **existing code token** before building:

- **Never improvise a token.** If a Figma value has no brand equivalent, that is a finding to surface — not a license to drop in a raw palette class (`gray-300`, `slate-500`, an arbitrary hex).
- Resolve via the `building-luar-ui` skill's **Figma → code map** and the project's token definitions (`tailwind.config.js`). Watch the documented traps (e.g. `green-1` bright vs `green-2` dark; `ai`/AI Gradient → `bg-ai-gradient` / Button `variant="gradient"`).
- Any token that won't resolve gets a ⚠️ row and is raised to the user with options (closest semantic token, add a new token, or confirm it's intentional one-off) — decide together; don't silently invent.

Present as a table and get confirmation:

| Figma token | Code token | Status |
|-------------|-----------|--------|
| base/foreground | `foreground` | ✅ resolves |
| AI Gradient | `bg-ai-gradient` / Button `variant="gradient"` | ✅ resolves |
| gray-300 (raw) | — | ⚠️ no brand equivalent — flag, do not invent |

This is a **hard gate**: do not conclude the grill while any token is unresolved.
