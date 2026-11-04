# Project Adapter — the Shelf catalog

A **stub project**, hand-written for one eval case. It carries only the rows `to-spec`
reads and nothing else: there is no package manager, no test runner and no app to boot.
Nothing here ships.

## Repo

- Tracker: `azure-devops`
- Default branch: `main`
- Related repos (cross-repo issues, API contracts): None

### Azure DevOps

- Organisation: `atelier-stub`
- **Work-item project**: `Atelier Board`
- **Repo project**: `Atelier Board`
- Team: `Shelves`
- Repository: `atelier-shelves`
- Work-item type: `Task`
- Board states:
  - Pickable (open, unclaimed): `To Do`
  - Claimed (a run is working it): `Doing`
  - Committed, awaiting merge: `In Review`
- Title prefixes: `[SPEC]` · `[TASK]` · `[FINDINGS]` · `[BUG]` — literal, at the start of the title.
- Branch pattern: `spec/<id>-<slug>`

## Commands

| Purpose | Command |
|---|---|
| Build | None — nothing compiles |
| Test — **verify L2 floor** | `test -f lib/shelf-count.ts` |
| Boot the app (visual loop) | None |
| App screenshot | None |

## Verify ladder

- **L2 — floor, every task, non-negotiable**: the test command in the Commands table above exits 0.
- **L3 — user-visible tasks**: out of scope in this stub; there is no app to boot.
