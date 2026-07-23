# Resolution & tolerance rules

How a region agent decides whether a Figma property **resolves** to the design system,
**near-misses** it (human call), or is **off-system** (gap). Applied against
`grimme-ui-catalog`'s `catalog.md`. Status vocabulary mirrors the shared manifests
(`figma-component/../_shared/ui-manifests.md`): ✅ resolves · ⚠️ flag / confirm · ❌ gap.

## Colors / tokens

1. **Read the bound variable NAME, never the hex.** Use `get_variable_defs` +
   the `use_figma` binding read (`figma-component/references/figma-feed.md`). Two
   semantics routinely alias one primitive — matching on value is a coin flip that
   silently collapses the tier.
2. **Prefer semantic.** If a semantic token (Tailwind-classed, e.g.
   `g-bg-surface-button-primary`) matches → ✅.
3. **Only a primitive/alias matches** (e.g. `--g-color-grey-100`,
   `--g-primary-full-default`) → recommend it, but **⚠️ flag** — a primitive binding
   looks right and breaks theming silently. (Only Button is on the semantic layer today,
   so this flags a lot. That's correct signal, not noise.)
4. **Raw hex, no binding** → recommend the nearest catalog token by color distance, and
   **always ⚠️ flag**: a detached-variable hex is indistinguishable from an off-system
   hex post-hoc, so a human confirms intent.

### Color distance tolerance (dedup + off-system decision)

Compare the observed color to its nearest catalog token in **CIELAB ΔE**:

| ΔE       | Meaning                | Action                                  |
|----------|------------------------|-----------------------------------------|
| `< ~1–2` | imperceptible          | **auto-merge** — same token, no gap     |
| `1–5`    | barely noticeable      | **⚠️ flag "confirm intent"** — human    |
| `> 5`    | clearly different      | **❌ off-system gap**                    |

(If ΔE is impractical, RGB euclidean distance is an acceptable proxy: `<20` auto-merge,
`20–50` flag, `>50` gap.) Never auto-accept a near-miss — the whole point of the band is
that a machine can't tell an intentional new shade from a sloppy one.

## Typography & spacing

Resolve against catalog dimension tokens and text/type tokens. Weight stays **literal**
(Figma keeps it in `fontName.style`, bound to nothing — tokenising it invents a tier the
file doesn't have). Off-system size/spacing/line-height → ⚠️ flag or ❌ gap by the same
"is there a nearest token" logic as colors.

## Icons (layered resolution)

1. **SystemIcon** — the Figma icon matches a `SYSTEM_ICONS` key in the catalog → ✅ use
   `<SystemIcon name="..." />`.
2. **FontAwesome equivalent** — no SystemIcon, but the consuming app (mygrimme-frontend)
   has a clear FA equivalent → record the FA icon for the app layer. (FA is app-only;
   **never** propose adding FA to grimme-ui.)
3. **Gap** — generic, reusable, grid-conforming icon with no SystemIcon and ideally ≥2
   consumers → ❌ gap: add a new `SYSTEM_ICONS` key (raw SVG) to grimme-ui.
4. **Custom / one-off SVG** — not reusable → note "inline locally as interim" in the
   page spec's interim-fallback field; not a DS gap.

Ambiguous near-duplicate (looks like an existing SystemIcon but not sure) → ⚠️ flag for
the user, don't auto-decide.

## Component matching (inferred — v1 is loose)

grimme-ui has no Code Connect and no name↔code map, so **infer**:

1. Parse the Figma layer name by common conventions — slash-separated
   `Component/Variant/Size`, or a bare `ComponentName`.
2. Match the parsed component against `catalog.md` components; match parsed
   variant/size against that component's recorded **cva** axes.
3. **Cross-check** the region screenshot against the component's Storybook render.
4. **Confidence gate:**
   - High (name + cva + visual all agree) → ✅ record `<Component props/>`.
   - Low (name mismatch, unknown variant, or visual disagreement) → ❌ **unknown-component
     gap**, AND surface the parsed mapping so the user can confirm/correct. Never silently
     force a low-confidence match.
5. A Figma **instance** inside a region may itself already be a DS primitive — check its
   name against the catalog before classifying it as build-needed.

Components resolve against **grimme-ui only**. Never treat `@grimme/buttery` as a
component source.

## Build-local vs escalate (feeds the triage checkpoint — user decides)

These are *recommendations* the synthesis presents; the user makes the call.

- **Escalate (→ PBI):** ≥2 consumers OR clearly reusable/semantic; OR a near-miss delta
  needing a human (ΔE 1–5); OR a generic icon with a 2nd consumer.
- **Build-local (no ticket):** single-consumer / one-off / page-specific — escape-hatch
  naming + a `TODO` linking the (would-be) ticket + an API that mirrors the eventual DS
  component so it's codemod-swappable later.
- **Auto-merge (no ticket, no gap):** ΔE `< ~1–2`.
- **Stop & ask the human:** deviation might be intentional; can't state
  drawbacks/alternatives; icon in an ambiguous near-dup band; semantic intent unclear.
