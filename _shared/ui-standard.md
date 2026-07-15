# UI Standard (the canon)

Shared reference for the component-tier design-to-code skills: `tokens-init` bootstraps toward it, `figma-component` resolves against it, and the future `ui-foundation` skill will audit/migrate existing repos toward it. When a host repo has its own established conventions, its ui-profile documents them and **repo idiom wins** — this doc is the default for greenfield and the yardstick for hygiene findings.

## Stack

- **Tailwind CSS** for styling; tokens consumed through the Tailwind theme — never raw values in components.
- **Headless behavior**: Base UI preferred for new repos; Radix fine where already present. Never hand-roll focus management, keyboard nav, or ARIA wiring a headless lib provides.
- **shadcn-style ownership**: standard primitives get *installed* from a registry and restyled with tokens — the code lives in the repo, owned, not imported from a black box.
- **`cva`** (class-variance-authority) for variant plumbing, with a `cn()` merge helper.

## Token architecture — three tiers

1. **Primitives** — raw values (`--green-500: #00c853`). Never consumed by components.
2. **Semantic** — aliases with usage meaning (`--color-surface-primary: var(--green-500)`). **The only tier components consume.**
3. **Component tokens** (optional) — per-component knobs (`--button-radius`) aliasing semantic tokens; mint only when a component genuinely needs its own dial.

Implementation: CSS custom properties exposed through the Tailwind theme (v4 `@theme`; v3 `theme.extend`). Light/dark via mode-scoped CSS-var overrides, never per-component logic.

Naming mirrors Figma slash paths 1:1: `color/surface/primary` → `--color-surface-primary` → `bg-surface-primary`.

**Hard rule:** no raw palette classes or hex in components. A value with no semantic token is a manifest finding (see `ui-manifests.md`), never an inline improvisation.

## Component conventions

- Compositional API by default (compound `Root/Trigger/Content` parts) for behavior-heavy components.
- Config-heavy widgets (DataGrid/DatePicker class) may take a configured-props API — follow established library precedent (see figma-component's `pattern-precedent.md`), don't invent taxonomy.
- The **WAI-ARIA APG** pattern is the behavior spec of record.

## Story contract

- CSF3 + autodocs (`tags: ['autodocs']`).
- One story per variant/state axis, plus an `AllVariants` grid story for visual comparison.
- Play-function interaction tests only where real behavior exists (open/close, keyboard).
- **Naming parity**: Figma property = component prop = story arg. A mismatch (`type` in code vs `variant` in Figma) breaks the single source of truth — it's a checkpoint question, never a silent rename.

## Designer contract (Figma hygiene checklist)

What `figma-component`'s hygiene report measures a node against:

- All colors/spacing/radius/typography bound to **variables** with semantic slash names (`color/surface/primary`, never `blue-500` or a raw hex). Code syntax set where the plan allows.
- **Auto layout** everywhere — spacing defined, not implied.
- Component properties are code-friendly: lowercase variant values (`primary`, not `Primary`), boolean `is*`/`has*` states (`isDisabled`, not `State=Disabled`).
- Layers named semantically (`PriceLabel`, not `Frame 42 copy`); 2–3 nesting levels max.
- Components published to the team library.
