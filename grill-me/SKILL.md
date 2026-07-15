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

## Manifest gates (HARD GATES — design tasks only)

Right after the variant table, build the **UI Primitive Manifest** and the **Token Manifest** per `../_shared/ui-manifests.md` — full classification rules (✅/⚠️/❌, "earn the abstraction" homes, never-improvise-a-token) and table formats live there. In this skill both run **interactively**: present each table back to the user and resolve every ⚠️/❌ row during the interview.

Project specifics:

- Resolve tokens via the project's Figma → code map (`building-luar-ui` when present, or a generated `<repo>-ui` profile skill) and its token definitions (`tailwind.config.js`). Watch the documented traps (e.g. `green-1` bright vs `green-2` dark; `ai`/AI Gradient → `bg-ai-gradient` / Button `variant="gradient"`).
- Custom primitives' shared home is the project UI lib (e.g. `luar-ui/`); promote there only with a real second consumer.
- Treat each ⚠️/❌ primitive as if it ships from a UI library — each becomes its own issue downstream (see the `to-issues` exception).

Both are **hard gates**: do not conclude the grill while any primitive or token row is unresolved.

Only after the variant table, both manifests, and the vertical-slice approach are agreed on should engineering questions (motion tech, perf gates, breakpoints, reduced-motion, etc.) begin.
