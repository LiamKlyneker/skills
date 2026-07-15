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

**Typography maps onto the same tiers, through different Figma objects.** A **text style** *is* the semantic tier (`heading/lg` → `text-heading-lg`, one utility carrying size + line-height + weight); the `font/size/*` and `font/lineHeight/*` variables its fields bind to are the primitives. Weight stays **literal** — Figma keeps it in `fontName.style`, bound to nothing, so tokenising it invents a tier the file doesn't have.

**Hard rule:** no raw palette classes or hex in components. A value with no semantic token is a manifest finding (see `ui-manifests.md`), never an inline improvisation.

## Component conventions

- Compositional API by default (compound `Root/Trigger/Content` parts) for behavior-heavy components.
- Config-heavy widgets (DataGrid/DatePicker class) may take a configured-props API — follow established library precedent (see figma-component's `pattern-precedent.md`), don't invent taxonomy.
- The **WAI-ARIA APG** pattern is the behavior spec of record.

## Story contract

- CSF3 + autodocs (`tags: ['autodocs']`).
- One story per variant/state axis, plus an `AllVariants` grid story for visual comparison.
- Play-function interaction tests only where real behavior exists (open/close, keyboard) — **plus** a regression guard wherever a styling failure would be *silent* (computed size/weight on the type slots). Guarding a silent failure is not over-testing; it is the only thing that catches it.
- Never assert a pseudo-state that an addon forces for display — it won't apply in the test runner. Real focus is assertable; synthetic hover is not. See `figma-component/references/render-verification.md`.
- **Naming parity**: Figma property = component prop = story arg. A mismatch (`type` in code vs `variant` in Figma) breaks the single source of truth — it's a checkpoint question, never a silent rename.

## Designer contract (Figma hygiene checklist)

What `figma-component`'s hygiene report measures a node against:

- All colors/spacing/radius bound to **variables** with semantic slash names (`color/surface/primary`, never `blue-500` or a raw hex). Code syntax set where the plan allows.
- **Typography bound to text styles** — *not* variables; a text style is a different object entirely. Role-based slash names (`heading/lg`, `body` — never `text-20`, which becomes a lie the day the size changes), with each style's `fontSize`/`lineHeight` bound to variables so the ramp has a primitive tier beneath it. Text carrying unbound font properties is the type equivalent of a raw hex fill.
- **Auto layout** everywhere — spacing defined, not implied.
- Component properties are code-friendly: lowercase variant values (`primary`, not `Primary`), boolean `is*`/`has*` states (`isDisabled`, not `State=Disabled`).
- Layers named semantically (`PriceLabel`, not `Frame 42 copy`); 2–3 nesting levels max.
- Components published to the team library.
