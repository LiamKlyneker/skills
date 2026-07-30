# UI Manifest Gates (Token + Primitive)

Shared reference for the skill that **builds** these tables (`figma-component`) and the workflow skills that **consume their rows** downstream (`to-prd`, `to-issues`). Two manifests that catch the two halves of design-drift: improvised **components** and improvised **tokens**. Both are **HARD GATES** — the invoking skill is not done while any ⚠️/❌ row is unresolved.

`figma-component` resolves rows **autonomously**; unresolvable rows batch into its single checkpoint. Run both right after the variant table, before any code.

This file is the **row schema** — statuses, columns, and the principles behind them — and stays stack-neutral. A project whose primitive homes, token files and traps need naming keeps its own flavored instance and registers it in its adapter's `## Project gates`; the schema below is unchanged by that, only the vocabulary the rows are filled with.

A grill is **not** a consumer of these tables: the design side is already resolved in the spec by the time the interview starts, so a grill reads those rows as answers rather than rebuilding them. Two skills resolving the same manifest is two sources of truth.

## UI Primitive Manifest

Build a manifest of **every** primitive the design needs. This prevents the recurring failure where a missing primitive gets **improvised inline** (e.g. a colored icon-badge rendered as ad-hoc utility classes instead of a shared component), causing the implementation to drift from the design.

Classify each primitive:

- ✅ **exists as-is** — a shared UI-lib primitive already matches.
- ⚠️ **drifts / needs an API change** — two cases: (a) the primitive exists but its API can't express the design (needs a new variant/state/prop); (b) **brownfield**: it exists *in feature code* as an inline/ad-hoc implementation that should be extracted into a shared primitive.
- ❌ **must be built** — no primitive exists.

For every ⚠️/❌ row, resolve:

- **Home** — pick by *earning the abstraction*, not by reflex. Four rungs, in order:
  - **stock** — something the platform or an installed registry already offers (a system icon set, a registry primitive). **Install or use it, never hand-roll it.**
  - **the project's shared UI lib** — a genuinely reusable, **cross-feature** custom primitive. Only promote here once there's a real second consumer.
  - **colocated with its one consumer** — single-consumer for now; hasn't earned shared status. Default new bespoke UI here.
  - **a new dependency** — last resort.

  What each rung is *called* is project vocabulary (a package name, a directory convention) and belongs in the project's flavored instance, not here. Respect the project's dependency direction: a primitive shared across two features lives in the shared lib, never imported feature-to-feature.
- **API surface** — props/params, variants, states, sizes.
- **Consumers** — which screens/cards use it.

Treat each ⚠️/❌ primitive as if it ships from a UI library — downstream, each becomes its own issue (see the `to-issues` exception). Present as a table:

| Primitive | Status | Home | API surface | Consumed by |
|-----------|--------|------|-------------|-------------|
| IconBadge | ❌ build | shared UI lib | color, icon, size | feature cards |
| Button | ⚠️ extend | stock (registry) | add solid variant | primary CTA |

If the project has a test vehicle that every primitive ships with (a snapshot baseline, a story), its flavored instance says so — a ❌/⚠️ row then implies that artifact lands with it.

## Token Manifest

Build a manifest of **every** Figma variable/token the design uses and resolve each to an **existing semantic code token**:

- **Never improvise a token.** A Figma value with no code equivalent is a *finding to surface* — not a license to drop in a raw palette value (a `gray-300`-style class, a system color, an arbitrary hex).
- Resolve via the project's **Figma → code map** (its ui-profile skill, or a `building-<x>-ui`-style project skill) and its token definitions, wherever this stack keeps them. Watch any traps the map documents — near-identical token names, and gradient/composite tokens that map to a component variant rather than a raw value.
- Any token that won't resolve gets a ⚠️ row with options: closest semantic token, mint a new token, or confirm an intentional one-off. Decide per the consumer's ask policy — never silently invent.

| Figma token | Code token | Status |
|-------------|-----------|--------|
| base/foreground | the semantic foreground token | ✅ resolves |
| brand/gradient | the brand-gradient token / a Button `gradient` variant | ✅ resolves |
| gray-300 (raw) | — | ⚠️ no equivalent — flag, do not invent |
