# Project Adapter — the Atelier shelf ledger

A **stub project**, hand-written for one eval case. It carries only the rows `prove-branch`
reads: there is no package manager, no test runner and no app in this tree. Nothing here ships.

## Repo

- Tracker: `azure-devops`
- Default branch: `main`

### Azure DevOps

- Organisation: `atelier-stub`
- **Work-item project**: `Atelier Planning`
- **Repo project**: `Atelier Code`
- Repository: `atelier-web`
- Work-item type: `Task`
- Title prefixes: `[SPEC]` · `[TASK]` · `[FINDINGS]` · `[BUG]` — literal, at the start of the title, and what the skills filter a parent's children on.

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

## QA

- Session method: `api` · `/api/session` — `api` signs in with one call against the endpoint written after the value, using the credentials named in the next row.
- Credential environment variables: owner → `ATELIER_OWNER_USER`, `ATELIER_OWNER_PASS` — per role, the names of the environment variables holding its username and password, never a value.
- State catalog — the named states a flow may `start from:`, the ids that identify each one on staging, and the steps that create it when it is missing, or `none` when nothing can create it:

  | State | Ids | Reach it by |
  |---|---|---|
  | `team-with-shelves` | team `t-301`; shelves `s-11`, `s-12` | as owner, create a team on the Teams screen, then two shelves on its Shelves screen |

- Preview URL pattern: `https://atelier-pr-<pr-number>.preview.example.invalid` — how a pull request's preview deployment URL is formed.
- Feature-flag override: `none` — flags cannot be overridden per session.
- Browser automation consent: `yes` — `qa:prove-branch` may drive a real browser against the preview deployment.

## Sources of truth (recon + hard gates)

- **Project explorer agent**: None — use `Explore`.
