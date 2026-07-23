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

Scope every call to THIS region node — never the whole page. Steps 1–3 are `figma-dev-mode`
tools; step 4 is a **separate** server (`use_figma`). Front-load the essential reads (1–3):
`figma-dev-mode` sessions can expire on long runs, and the `get_design_context` LAST
ordering keeps a late failure non-fatal. If the session drops, re-auth and re-run this one
region agent.

1. `get_metadata` — map the region: children, names, types, **positions & sizes**.
2. `get_variable_defs` — bound token **names**+values for the region (flat name→value).
3. `get_screenshot` — visual ground truth for the region and each distinct sub-state.
   Viewed **inline** as a check; it returns an inline image, not a path — do **not** rely on
   persisting it. The layout tree (below) is the durable source of truth.
4. **Binding read** via `use_figma` (if `/figma-use` is available, a separate server) —
   resolve each node's `boundVariables` → variable **NAMES** per property, `textStyleId` →
   style name, auto-layout, per-node font size/line-height. This is the ONLY source for
   variable-name-**per-property**. Resolve fills by bound name, never by hex. **If
   `use_figma` is unavailable (degraded color mode):** you still have `get_variable_defs`
   region-level name→value — keep those token **names**; what you lose is the per-property
   binding, so set every color's status/flag to `binding-unverified`. Never present an
   unverified value as on-system.
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
- **Typography & spacing** — **first decide which kind of spacing it is.** *Generic layout
  spacing* between elements/regions (page rhythm: 24/16/12/8/4px gaps between siblings) maps
  to the **Tailwind spacing scale** (`gap-4`, `p-3`, …) and is **not a DS concern — do not
  flag it.** Only *component-internal dimensions* (a control's own padding/height/radius)
  resolve against catalog **dimension** tokens; flag those off-system. Typography: resolve
  against the catalog's enumerated **`text-*`** utilities (consumer form — unprefixed:
  `text-h4`, `text-body1`, `text-overline`, …); match by name, don't flag ordinary text as a
  gap, and **never emit the `g-` prefixed form** (grimme-ui-internal, not the consumer API).
  Weight is literal, not a token.
- **Icons** — layered: SystemIcon → FontAwesome (app-only) → gap (add SystemIcon) →
  custom-inline. Flag ambiguous near-duplicates.
- **States** — capture ONLY for components you classified unknown/new. Known DS
  components' states are DS-owned; don't spec them.
- **Layout / placement** — the **output** is always *relative auto-layout intent*, never
  absolute coordinates. Capture the region's containment tree (child order preserved) and
  each container's intent: direction (row/column), gap (resolved token if bound), alignment,
  wrap. **Preferred input:** the binding read's auto-layout data. **Fallback (input only):**
  when auto-layout data is unavailable, you MAY *infer* relative intent from `get_metadata`
  positions & sizes (siblings sharing a Y are a row, an X are a column; gaps from the
  deltas) — this reads geometry to derive intent, it does **not** put coordinates in the
  output. Flag any container derived this way `layout-inferred` in the layout note. Never
  record absolute x/y.

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
      "figmaValue": "#0a5c2b", "resolvedToken": "bg-surface-button-primary|null",
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
