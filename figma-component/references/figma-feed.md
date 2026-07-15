# Figma Feed Discipline

The official Figma MCP is the feed. Its noise problem is a *usage* problem — solved by scoping and call order, not by switching servers.

## Call order

1. **`get_metadata`** — cheap node map first. Identify the component set, its variants, its children. Record node name + URL.
2. **`get_variable_defs`** — token names + values for the selection; the Token Manifest's input. Node-scoped: run on the component-set root so every variant's tokens are captured.
3. **`get_screenshot`** — one per variant/state. Screenshots are the visual ground truth; capture them before generating any code.
4. **`get_design_context`** — LAST, and only on small scoped frames (a single variant, never the whole set). If the response is huge or truncated, re-scope smaller instead of pushing on.

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
