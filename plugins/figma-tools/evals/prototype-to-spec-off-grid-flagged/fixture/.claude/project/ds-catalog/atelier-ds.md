# Atelier catalog (fingerprint: 0.3.1 · generated: 2026-09-21)

Read from the package `@atelier/ds` at version `0.3.1` — its bundled declarations
(`dist/index.d.ts`) and its theme stylesheet (`dist/theme.css`). The fingerprint is that
version, and it covers exactly those two files.

This catalog is a **single document in one file**. The pointer in the adapter names the
directory this file sits in; nothing else in that directory is part of the catalog.

## Conventions

**The consumer-facing form is the arbitrary-value utility.** `@atelier/ds` ships no Tailwind
theme and no preset, so **no token emits a utility class of its own**. A consumer writes the
custom property into a Tailwind arbitrary value, and that is the form every entry below is
written in:

```
bg-[--color-surface]   text-[--color-ink-muted]   rounded-[--radius-tile]   p-[--space-step]
```

**How a token's name becomes what a consumer writes.** Take the custom property whole,
including its tier word, and put it in the brackets: `--space-step` is written
`p-[--space-step]`, never `p-step`. Nothing is dropped and nothing is prefixed.

**Where the spacing bifurcation falls.** Page rhythm — the gap between cards, page padding, a
page section's stack — is the **Tailwind scale's** business: `gap-3`, `p-8`. The `--space-*`
tier is the design system's own **component-internal** spacing: the padding inside a control,
the step between a tile's rows, the hairline. Anything that sits inside a design-system
surface reaches for `--space-*`.

**The spacing scale is not uniform and is not a multiplier.** Its five steps are `1`, `4`,
`8`, `12`, `16` px, enumerated below, and `1px` is a real step — the hairline every border in
this design system is drawn at. There is no step between `8` and `12`, and there is no rule
that generates one: a dimension that lands between two steps has no token, and the catalog is
the only evidence of that.

**The four type tiers.** `--type-size-plate`, `--type-size-label`, `--type-size-body` and
`--type-size-title` are the four sizes this design system has, and each one backs exactly one
utility in `## Typography`. A text run is styled by the utility, not by the size token.

**Statuses today.** Nothing here is `legacy`, `deprecated` or `unused`. Every entry is
`current`, which is the default, so no `status:` field is written anywhere.

**Exports that are not components.** `cx` is a class-merging helper. It never matches a design
element and is not counted among the components.

## Components

| Component | Reference | Variant axes / values | Source |
|---|---|---|---|
| Icon | `@atelier/ds` | `size`: `sm`, `md`, `lg` · `tone`: `default`, `muted`, `accent` | `dist/index.d.ts` |
| Stack | `@atelier/ds` | `direction`: `row`, `column` · `gap`: `snug`, `step`, `pad`, `room` | `dist/index.d.ts` |
| Surface | `@atelier/ds` | `elevation`: `flat`, `raised` | `dist/index.d.ts` |
| Text | `@atelier/ds` | `tier`: `plate`, `label`, `body`, `title` · `tone`: `default`, `muted` | `dist/index.d.ts` |

**There is no chip, tag, badge, pill or token component in this design system.** A design that
draws a small bordered label resolves against nothing here.

## Tokens

Three tiers. Every tier is **`CSS var only`** — the package ships no Tailwind theme, so there
is nothing for Tailwind to generate a class from, and the arbitrary-value utility is the only
consumer-facing form.

### Palette

Every surface, edge and ink on the board. Consumed directly. **`CSS var only`** — written
`bg-[--color-surface]`, `text-[--color-ink]`, `border-[--color-edge]`. 5 entries, enumerated.

| Custom property | Value |
|---|---|
| `--color-accent` | `#7a5c2e` |
| `--color-edge` | `#ded7c9` |
| `--color-ink` | `#2a2723` |
| `--color-ink-muted` | `#6f695e` |
| `--color-surface` | `#fbfaf7` |

### Radii

The two corner sizes. Consumed directly. **`CSS var only`** — written
`rounded-[--radius-tile]`. 2 entries, enumerated.

| Custom property | Value |
|---|---|
| `--radius-tile` | `6px` |
| `--radius-panel` | `12px` |

### Dimensions

The design system's own component-internal spacing steps, per the bifurcation above.
Consumed directly, for component-internal spacing only. **`CSS var only`** — written
`p-[--space-step]`, `gap-[--space-snug]`, `border-[length:--space-hairline]`. 5 entries,
enumerated.

| Custom property | Value |
|---|---|
| `--space-hairline` | `1px` |
| `--space-snug` | `4px` |
| `--space-step` | `8px` |
| `--space-pad` | `12px` |
| `--space-room` | `16px` |

### Type sizes

The four sizes the type utilities are built from. Reached through a `## Typography` utility
rather than consumed on their own. **`CSS var only`** — written `text-[--type-size-body]` in
the rare case a utility does not fit. 4 entries, enumerated.

| Custom property | Value |
|---|---|
| `--type-size-plate` | `11px` |
| `--type-size-label` | `13px` |
| `--type-size-body` | `15px` |
| `--type-size-title` | `20px` |

## Typography

Four utilities, one per type tier, in consumer-facing form.

| Utility | Sets |
|---|---|
| `.type-plate` | font-size: 11px · line-height: 16px · font-weight: 500 · letter-spacing: 0.08em · text-transform: uppercase |
| `.type-label` | font-size: 13px · line-height: 18px · font-weight: 500 |
| `.type-body` | font-size: 15px · line-height: 22px · font-weight: 400 |
| `.type-title` | font-size: 20px · line-height: 26px · font-weight: 600 · letter-spacing: -0.01em |

None of the four carries a built-in responsive step, so none of them is a composite and each
may be written with a responsive prefix.

## Icons

### Atelier icon exports — the only source

Referenced as a component from `@atelier/ds` and sized and coloured by wrapping it in `Icon`,
which owns the `size` and `tone` axes:

```tsx
<Icon size="sm" tone="muted"><LoupeGlassIcon /></Icon>
```

The set is closed. 4 exports, enumerated:

`DustCoverIcon`, `LoupeGlassIcon`, `NewNicheIcon`, `TallyMarkIcon`

**There is no second source**: no icon library is installed, and a consumer must not reach for
one. A glyph the set does not have is a gap to file, never an inline `<svg>`.
