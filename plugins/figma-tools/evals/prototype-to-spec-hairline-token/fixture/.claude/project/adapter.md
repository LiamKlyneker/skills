# Project Adapter — the Atelier plate board

A **stub project**, hand-written for one eval case. It carries only the sections
`prototype-to-spec` reads and nothing else: there is no build, no test runner, no verify
ladder and no app to boot. Nothing here ships.

## Repo

- Tracker: `github`
- Issue tracker / PRs: `LiamKlyneker/atelier-stub` (GitHub, via `gh`)
- Default branch: `main`
- Title prefixes: `[TASK]` · `[DESIGN-SPEC]` — a human scanning convention, not a filter.
- DS-gap backlog: `LiamKlyneker/atelier-stub` — the design system `@atelier/ds` is developed in
  this same repository, so a proposed gap would be filed here.

## Design system

- Repo role: `consumer`
- Design-system source: the package `@atelier/ds`.
- Catalog: `.claude/project/ds-catalog/`, relative to this project's root — the directory sits
  beside this adapter. The directory is the pointer; every markdown file directly inside it is
  read as one document.
- Fingerprint command: `node -p "require('./node_modules/@atelier/ds/package.json').version"` —
  run from this project's root.
- Class prefixes:
  - Tailwind class prefix: `None` — this project's Tailwind config sets no prefix.
  - CSS variable prefix: `None` — the custom properties are named by tier (`--color-`,
    `--radius-`, `--space-`, `--type-`) with nothing in front.
  - Consumer-facing emission form: the **arbitrary-value utility**, e.g. `bg-[--color-surface]`.
    No token emits a class of its own; the package ships no Tailwind theme.
- Icon resolution ladder: the `@atelier/ds` icon exports the catalog enumerates, always wrapped
  in `Icon` → nothing else. There is no second source, and an inline `svg` is a defect.
- Usage-rules sources: `None` — this project registers none, so a brief cites nothing.

### Prototype source

Read by `prototype-to-spec` and by nothing else.

| Row | Value |
|---|---|
| `Path:` | `./prototype` — the prototype directory, relative to this project's root. It is read from the working tree; no preview URL is resolved and none is needed |
| `Spec files:` | `spec/spec-data.ts` · `spec/types.ts` · `HANDOFF.md` · `README.md`, resolved under the path above |
| `Schema:` | a typed spec module plus a handoff document — the shape `prototype-to-spec` implements. `spec/types.ts` is the type file it is declared in |
| `Screenshots:` | `<path>/spec/screenshots/<step-id>.png`, read from the working tree and linked by path, never embedded. **This prototype was never captured — the directory does not exist and every step and state carries `null`** |

## Repo discipline

- The design system is not this project's to edit. A missing component, token or icon is a gap
  filed against the DS-gap backlog above, never a local copy of one.
