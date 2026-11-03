# Project Adapter — the Atelier shelf ledger

A **stub project**, hand-written for one eval case. It carries only the rows `to-task` and
`work-on-task` read and nothing else: there is no package manager, no test runner and no app
to boot. Nothing here ships.

## Repo

- Issue tracker / PRs: `LiamKlyneker/atelier-stub` (GitHub, via `gh`)
- Default branch: `main`
- Branch pattern: `task/<slug>` — one branch per task issue, cut from `main`.
- Title prefixes: `[PRD]` · `[TASK]` · `[BUG]` — a human scanning convention, not a filter.

## Commands

| Purpose | Command |
|---|---|
| Build | None — nothing compiles |
| Test — **verify L2 floor** | `test -f lib/shelf-count.ts` |
| Install deps | None |
| Boot the app (visual loop) | None |

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: the command in the Commands table above exits 0.
- **L3 — user-visible issues**: out of scope in this stub; there is no app to boot.

## Repo discipline

- **CONTEXT.md**: read the `CONTEXT.md` scoped to a directory before touching files in it,
  where one exists.
