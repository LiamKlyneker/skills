# Project Adapter — the Atelier shelf ledger

A **stub project**, hand-written for one eval case. It carries only the rows `prove-branch`
reads, and deliberately no QA section: there is no package manager, no test runner and no app
in this tree. Nothing here ships.

## Repo

- Tracker: `github`
- Default branch: `main`

### GitHub

- Issue tracker / PRs: `LiamKlyneker/atelier-stub` (GitHub, via `gh`)
- Title prefixes: `[PRD]` · `[TASK]` · `[BUG]` · `[FINDINGS]` — a human scanning convention, not a filter.

## Commands

| Purpose | Command |
|---|---|
| Build | None — nothing compiles |
| Test — **verify L2 floor** | `test -f app/shelves.tsx` |
| Install deps | None |
| Boot the app (visual loop) | None — the pass runs against the pull request's preview deployment |

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: the Test command above exits 0.
- **L3 — user-visible issues**: the change is seen on the preview deployment, signed in as the role the change is for.

## Sources of truth (recon + hard gates)

- **Project explorer agent**: None — use `Explore`.
