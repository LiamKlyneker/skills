# Project Adapter — the Atelier shelf ledger

A **stub project**, hand-written for the `qa:prove-branch` eval cases that read page knowledge.
There is no package manager, no test runner and no running app in this tree. Nothing here ships.

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
| Test — **verify L2 floor** | `test -f app/shelves/page.tsx` |
| End-to-end suite | `e2e/` — Cypress; data-creation tasks are registered in `e2e/cypress.config.ts` |
| Install deps | None |
| Boot the app (visual loop) | None — the pass runs against the pull request's preview deployment |

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: the Test command above exits 0.
- **L3 — user-visible issues**: the change is seen on the preview deployment, signed in as the role the change is for.

## QA

- Session method: `api` · `/api/session` — `api` signs in with one call against the endpoint written after the value, using the credentials named in the next row.
- Credential environment variables: owner → `ATELIER_OWNER_USER`, `ATELIER_OWNER_PASS` — per role, the names of the environment variables holding its username and password, never a value.
- Known accounts: `.claude/project/accounts.md` — the observed layer: the staging org the pass uses and the page states known to exist there.
- Preview URL pattern: `https://atelier-pr-<pr-number>.preview.example.invalid` — how a pull request's preview deployment URL is formed.
- Preview basic auth: `ATELIER_PREVIEW_USER`, `ATELIER_PREVIEW_PASS` — the names of the environment
  variables holding the HTTP Basic Auth username and password in front of the preview, never a value.
- Feature-flag override: `none` — flags cannot be overridden per session.
- Browser automation consent: `yes` — the `qa` skills may drive a real browser against the target.

## Sources of truth (recon + hard gates)

- **Project explorer agent**: None — use `Explore`.
