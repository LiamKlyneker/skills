# Figma read discipline

How a brief reads one Figma node. `figma-to-brief` applies this on the main thread, once per node
it reads, so "this region" below means that node.

The names `hiddenVariants`, `notes`, `status`, `flagReason`, `bindingVerified` and `property` label
facts the read must keep. A brief writes those facts into ledger rows and has no JSON output.

## Figma call discipline (do not deviate)

Scope every call to THIS region node — never the whole page. Steps 1–3 are `figma-dev-mode`
tools; step 4 is a **separate** server (`use_figma`). Front-load the essential reads (1–3):
`figma-dev-mode` sessions can expire on long runs, and the `get_design_context` LAST
ordering keeps a late failure non-fatal. If the session drops, re-auth and re-read this node.

1. `get_metadata` — map the region: children, names, types, **positions & sizes**.
   **Hidden nodes carry state — do not silently prune them.** `get_metadata` reports
   `visible:false` siblings, and a Figma frame routinely encodes its states as hidden
   variants inside one node (a warning banner, a status/warning Chip, an empty-state block,
   an error message). A child whose name implies a **state or variant** — matches
   `/chip|banner|warning|error|empty|badge|alert|tooltip|state/i`, or sits alongside a
   visible sibling as its alternate — is **in-scope content**, not noise. Record every such
   hidden node under `hiddenVariants` (below) with the state it represents; never drop it
   just because it's hidden. Only prune a hidden node when its name is clearly scaffolding
   (spacer, guide, placeholder, deprecated/old, `_`-prefixed) — and when you do, list it in
   `notes` so synthesis can see the call. When unsure, keep it and flag it.
2. `get_variable_defs` — bound token **names**+values for the region (flat name→value).
3. `get_screenshot` — visual ground truth for the region and each distinct sub-state.
   Viewed **inline** as a check; it returns an inline image, not a path — do **not** rely on
   persisting it. The layout tree (below) is the durable source of truth.
4. **Binding read** via `use_figma` (a separate server). **Load the `/figma-use` skill
   first — it is a mandatory prerequisite for every `use_figma` call.** If `/figma-use` is
   not in your available skills, treat the binding read as unavailable and go to degraded
   color mode below. Resolve each node's `boundVariables` → variable **NAMES** per property,
   `textStyleId` → style name, auto-layout, per-node font size/line-height. This is the ONLY source for
   variable-name-**per-property**. Resolve fills by bound name, never by hex. On a
   successful per-property read, set that color's `bindingVerified: true`.
   **If `use_figma` is unavailable (degraded color mode):** you still have
   `get_variable_defs` region-level name→value — keep those token **names**; what you lose is
   the per-property binding. In that mode **every** color object you emit MUST carry
   `bindingVerified: false`, `status: "flag"`, and `flagReason: "binding-unverified"` — no
   exceptions, not even a clean semantic-name match. `bindingVerified` is a required,
   non-droppable field: a color without it is an invalid finding. Never present an
   unverified value as on-system (`status: "resolves"` / `bindingVerified: true` are
   forbidden in degraded mode).
5. `get_design_context` — LAST, only on a small scoped sub-frame if you still need intent.
   Treat as intent, not pasteable code; strip arbitrary values.

## Two filters that apply before anything below

**1. Match within the property's kind.** For every value you resolve, narrow the catalog to
the entries that can legally apply to *that property* — stroke to stroke/border dimensions,
text fill to text colors, background fill to surface colors, gap to layout spacing — and only
then compare values or names. This is normative in the resolution rules; the consequence for
you is that a numerically perfect match from the wrong kind is a **wrong** finding, not a
lucky one, and it emits as `resolves`, which is what makes it dangerous. Record the property
kind you filtered on in the finding's `property` field. An empty candidate set is a real
answer — resolve it as a gap or a layout-scale value, never by widening to another kind.

**2. Vector geometry is out of scope for value flagging.** Inside a node that resolves as an
icon or an illustration, the interior vector data — `VECTOR` / `BOOLEAN_OPERATION` / `LINE` /
`STAR` / `POLYGON` children, their path fills, their sub-shape strokes and their internal
dimensions — is **drawing data, not design decisions**. Do not emit color, spacing, or
dimension findings for it, and never flag it as a hardcoded value. The icon resolves **as a
whole** through the icon ladder; enumerating its interior produces dozens of unactionable
"off-system hex" findings that bury the region's real ones.

Two things this exclusion does **not** cover, because they are genuine token decisions made
at the usage site:

- the icon's **own box** — the size/dimension applied to the icon node in this region;
- the **color applied to the icon** at its instance (the fill or `currentColor` binding on
  the icon node itself, not on its interior paths).

Both stay in scope and resolve normally. When you exclude interior geometry, say so once in
`notes` (e.g. "vector interiors of 6 icon nodes excluded per vector-geometry rule") so
synthesis can see the call rather than infer a silent gap in coverage.
