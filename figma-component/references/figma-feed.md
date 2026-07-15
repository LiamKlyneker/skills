# Figma Feed Discipline

The official Figma MCP is the feed. Its noise problem is a *usage* problem — solved by scoping and call order, not by switching servers.

## Call order

1. **`get_metadata`** — cheap node map first. Identify the component set, its variants, its children. Record node name + URL.
2. **`get_variable_defs`** — token names + values for the selection; the Token Manifest's input. Node-scoped: run on the component-set root so every variant's tokens are captured.
3. **`get_screenshot`** — one per variant/state. Screenshots are the visual ground truth; capture them before generating any code.
4. **`get_design_context`** — LAST, and only on small scoped frames (a single variant, never the whole set). If the response is huge or truncated, re-scope smaller instead of pushing on.

## The binding read — what the four tools above can't tell you

None of them answer the question the build actually turns on: **which variable is bound to which property, in which variant.**

- `get_metadata` is **shallow**: names, types, positions, sizes. It does not recurse into a component set's variants' children, and it renders a `COMPONENT_SET` as `<frame>` — so the node you were handed can look like a plain frame when it isn't.
- `get_variable_defs` is a **flat name→value map** for the selection. It says which tokens are in play, never where they land. It flattens alias chains, and returns code-syntax names (`var(--x)`) only for the variables that happen to have one set — so one call can mix `fg/default` and `var(--color-border-hover)`.

So add one read-only `use_figma` script (load `/figma-use` first) that walks the set and resolves each node's `boundVariables` → variable **names**, plus `textStyleId` → style name, auto-layout, and per-node font size/LH. One call replaces N `get_design_context` calls and is the only source for the next rule.

**Hard rule: resolve a fill by its bound variable name, never by matching the hex.** Design systems routinely alias two semantics onto one primitive — a focus ring and an accent fill both `#3b82f6`; a disabled surface and a subtle surface both `#f5f5f5`. Matching on value is a coin flip that silently collapses the tier.

Gotcha: reading `componentPropertyDefinitions` on a **variant** child throws (`Can only get … of a component set or non-variant component`) — read it on the set, and guard the access.

## Treat output as intent, never final code

`get_design_context` returns generated React + Tailwind. It is a *representation of the design*, not code to paste:

- Strip arbitrary values (`leading-[22.126px]`, `w-[347px]`) — read the value, re-express it through semantic tokens and layout primitives.
- Ignore its component boundaries — yours come from the UI Primitive Manifest.
- Exact spacing/size numbers are read from it; their *expression* comes from the repo's tokens.

## Code Connect — optional accelerator

Org/Enterprise plans only. If the org has it, mapped components surface real code references in `get_design_context` — trust those mappings over discovery. Never require it: the ui-profile map is the plan-independent replacement.

## Traps

- One screenshot ≠ the design. Enumerate variants via metadata; fetch each one.
- A component *instance* inside the node may itself be an existing primitive — check metadata names against the ui-profile before classifying it ❌ build.
- Values visible on screen but absent from `get_variable_defs` mean raw, unbound fills in Figma → ⚠️ Token Manifest rows and hygiene-report findings.
