# Project Adapter — the Atelier plate board

A **stub project**, hand-written for one eval case. It carries only the rows `work-on-task`
reads and nothing else: there is no package manager, no test runner and no app to boot.
Nothing here ships.

## Repo

- Issue tracker / PRs: `LiamKlyneker/atelier-stub` (GitHub, via `gh`)
- Default branch: `main`
- Branch pattern: `task/<slug>` — one branch per task issue, cut from `main`.
- Fixed scorecard: `None` — a ticket's scorecard rows are derived from its ledger.
- Title prefixes: `[TASK]` · `[DESIGN-SPEC]` — a human scanning convention, not a filter.

## Design system

- Design-system source: the package `@atelier/ds`.
- Catalog: `.claude/project/ds-catalog/`, relative to this project's root. The directory is
  the pointer; every markdown file directly inside it is read as one document. A value with
  no row in the catalog has no token.
- Consumer-facing emission form: the **arbitrary-value utility**, e.g. `bg-[--color-surface]`.
  No token emits a class of its own; the package ships no Tailwind theme.

## Commands

| Purpose | Command |
|---|---|
| Build | None — nothing compiles |
| Test — **verify L2 floor** | `test -f components/chip.tsx` |
| Install deps | None |
| Boot the app (visual loop) | None |

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: the command in the Commands table above exits 0.
- **L3 — user-visible issues**: out of scope in this stub; there is no app to boot.

## Repo discipline

- **CONTEXT.md**: read the `CONTEXT.md` scoped to a directory before touching files in it,
  where one exists.
- The design system is not this project's to edit. A missing token is a gap filed against the
  tracker above, never a local copy of one.
