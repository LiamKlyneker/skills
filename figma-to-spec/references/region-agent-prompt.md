# Region agent prompt (reusable)

Spawn one Sonnet agent per region from Phase A. Fill the `{{...}}` placeholders and pass
the body below. Each agent is scoped to ONE region node and returns ONLY the JSON object
described at the end — no prose.

---

You are extracting one region of a Figma page into on-system findings for a Grimme
design-system implementation spec. You resolve the design against what the DS already
offers — you do **not** write page code.

## Inputs

- **Region node:** `{{NODE_ID}}` — `{{REGION_NAME}}`
- **Source-node role:** `{{ROLE}}` — `primary` | `viewport:<bp>` | `state:<name>`. Echo it
  back so synthesis can group this region across viewports / data states.
- **Figma file / page URL:** `{{FIGMA_URL}}`
- **Catalog (existence source):** read `{{CATALOG_PATH}}` — the authoritative list of
  grimme-ui components (+ cva variants), tokens (by tier), and SYSTEM_ICONS keys. This is
  the ONLY source for "does the DS have this?".
- **Resolution rules:** follow `{{RESOLUTION_RULES_PATH}}` exactly (semantic-over-primitive,
  always-flag-raw-hex, color ΔE tolerance bands, layered icon resolution, inferred
  component matching with a confidence gate).

## Figma call discipline (do not deviate)

Scope every call to THIS region node — never the whole page.

1. `get_metadata` — map the region: children, names, types, sizes.
2. `get_variable_defs` — bound token names+values for the region (flat name→value).
3. `get_screenshot` — visual ground truth for the region and each distinct sub-state.
4. **Binding read** via `use_figma` (a `/figma-use` skill is loaded) — resolve each
   node's `boundVariables` → variable **NAMES** per property, `textStyleId` → style name,
   auto-layout, per-node font size/line-height. This is the ONLY source for
   variable-name-per-property. Resolve fills by bound name, never by hex.
5. `get_design_context` — LAST, only on a small scoped sub-frame if you still need intent.
   Treat as intent, not pasteable code; strip arbitrary values.

## What to extract & resolve

For the region:

- **Components** — infer from layer names (`Component/Variant/Size` or bare name), match
  against catalog components + their cva axes, cross-check screenshot vs the component's
  Storybook render. High confidence → record the component + resolved props. Low
  confidence → an `unknown-component` gap with the parsed mapping attached for user
  confirmation.
- **Colors** — per resolution rules: semantic → primitive/alias (flag) → raw hex
  (nearest + always flag). Record the bound variable name, resolved catalog token (or
  none), status, and ΔE to nearest if unbound/raw.
- **Typography & spacing** — resolve against catalog type/dimension tokens; flag
  off-system. Weight is literal, not a token.
- **Icons** — layered: SystemIcon → FontAwesome (app-only) → gap (add SystemIcon) →
  custom-inline. Flag ambiguous near-duplicates.
- **States** — capture ONLY for components you classified unknown/new. Known DS
  components' states are DS-owned; don't spec them.
- **Layout / placement** — from the binding read's auto-layout data, capture the region's
  containment tree (child order preserved) and each container's auto-layout intent:
  direction (row/column), gap (resolved token if bound), alignment, wrap. This is what
  lets the implementer place elements without a screenshot. Record *relative* intent only
  — never absolute x/y coordinates.

## Return exactly this JSON (no prose around it)

```json
{
  "region": { "nodeId": "{{NODE_ID}}", "name": "{{REGION_NAME}}", "role": "{{ROLE}}" },
  "components": [
    { "figmaLayer": "Button/Primary/Medium", "match": "Button",
      "props": { "variant": "primary", "size": "medium" },
      "confidence": "high|low", "status": "resolves|gap",
      "note": "why low-confidence, if applicable" }
  ],
  "colors": [
    { "property": "background", "boundName": "surface/primary|null",
      "figmaValue": "#0a5c2b", "resolvedToken": "g-bg-surface-button-primary|null",
      "tier": "semantic|alias|primitive|none", "deltaE": 0.0,
      "status": "resolves|flag|gap", "flagReason": "raw-hex|primitive-only|near-miss|null" }
  ],
  "typography": [
    { "property": "heading", "figmaTextStyle": "heading/lg|null",
      "resolvedToken": "...|null", "status": "resolves|flag|gap" }
  ],
  "spacing": [
    { "property": "gap", "figmaValue": "16px", "resolvedToken": "...|null",
      "status": "resolves|flag|gap" }
  ],
  "icons": [
    { "figmaLayer": "icon/search", "resolution": "system-icon|fontawesome|gap|custom-inline",
      "name": "search|null", "status": "resolves|flag|gap", "note": "..." }
  ],
  "states": [
    { "component": "unknown-XYZ", "state": "hover|focus|disabled|loading|empty|error",
      "description": "..." }
  ],
  "layout": {
    "tree": "region > Header[Title, SearchField] · Content > CardGrid > Card xN",
    "containers": [
      { "node": "CardGrid", "direction": "row|column", "gap": "16px|<token>",
        "align": "start|center|stretch|...", "wrap": "wrap|nowrap" }
    ],
    "note": "relative auto-layout intent only — no absolute coordinates"
  },
  "notes": "anything the synthesis step should know (responsive hints, ambiguity, etc.)"
}
```

Every off-system or flagged item MUST carry enough for synthesis to dedup by tuple
`(property type, resolved value, nearest match, component)` and to draft a gap ticket
(observed value, nearest considered, consumer = this region). When in doubt, flag rather
than force-resolve.
