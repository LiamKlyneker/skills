# Project Adapter — TEMPLATE

Single home for every project-specific fact the skills need. Workflow skills (`work-on-prd`, `to-issues`, `next-prd-issue`, `work-on-issue`) and `deep-grill` reference this file and never hardcode these values. (`grill-me` deliberately does **not** — it is the lightweight inline grill and reads nothing from here.) Porting the workflow to another repo = copy the skills + rewrite this file, nothing else.

> **This is a template.** Fill every `<placeholder>` with your project's real values before running `work-on-prd`. Delete rows that don't apply; add rows the workflow needs. Nothing else in the skills should mention a tool, path, or command by name — if it does, lift it into this file.
>
> **If you are reading this during a real `work-on-prd` / `deep-grill` / `to-issues` run, you resolved the wrong file — stop.** This is the unfilled template in the canonical skills repo. The project's filled adapter lives at `<project-root>/.claude/skills/_shared/project-adapter.md`. A relative `../_shared/...` from a skill directory resolves *past* the symlink and lands here; re-read from the project repo root instead. Never paste this file into a worker prompt.

**Canonical source:** skill *logic* is canonical in **this repo** (`LiamKlyneker/skills`) and reaches a project repo either by copy or by symlinking each skill directory into its `.claude/skills/` — an improvement made in a copy is drift until it's back-ported here. **This `_shared/` file is always copied, never symlinked**, because each project fills it in with its own values; that copy lives at `<project-root>/.claude/skills/_shared/project-adapter.md`, which is the path skills must resolve from the project repo root.

## Repo

- Issue tracker / PRs: `<owner>/<repo>` (GitHub, via `gh`)
- Default branch: `<main>` (PRs must target it — `Closes` keywords only fire against the default branch)
- Related repos (cross-repo issues, API contracts): `<owner>/<other-repo>` — or "None"

## Commands

Every command a worker or the orchestrator runs. Keep the **Purpose** column stable (the skills refer to L2/L3 by name); swap the **Command** column for your stack.

| Purpose | Command |
|---|---|
| Build | `<build command>` |
| Test — **verify L2 floor** | `<test command>` |
| Boot the app (visual loop) | `<run/boot command>` |
| App screenshot | `<screenshot command>` |
| Install deps | `<dependency install command>` |

## App facts

- One or two lines of stack facts every worker should know before touching code (language + version, framework, the one file to edit vs. never touch, strict-mode flags, etc.).
- e.g. `<language + version> · <framework> · <the generated/config file to edit, never its raw output>`

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: `<test command>` passes.
- **L3 — user-visible issues**: L2 + `<boot command>` boots the app + a screenshot as evidence (`<screenshot command>`).
- **L4** (agent-driven interaction): out of scope v1.
- **L5 — human**: once per PRD, via the QA doc, on the branch, before merge.

## QA doc convention

- Path: `<docs/qa/prd-<n>.md>` (`<n>` = PRD issue number), committed on the PRD branch, linked from the PR body.
- Per issue: what shipped · how to test in the running app (from the issue's `## QA notes`, refined by the worker) · edge cases the worker flagged.
- The human runs it start-to-finish before merging the PR.

## Sources of truth (`deep-grill` recon + hard gates)

- **Project explorer agent**: `<subagent_type>` — read-only, one feature/package area per spawn. Or "None — use `Explore`".
- **Contract-boundary explorer agent**: `<subagent_type>` — owns the related repo/service above (API handlers, contract spec, data layer). Or "None — no contract boundary".
- **Access-policy source**: `<migrations path, IaC definition, policy console, or MCP>` — how to read the live per-operation policies for a store, wherever this project enforces them (database row policies, document-store rules, IAM, or authorization middleware). Or "None — no user-scoped data layer".

## Repo discipline

- **CONTEXT.md**: read the scoped `CONTEXT.md` before touching files in any directory (see the `scoped-context` skill). Update it only if documented architecture changes.
- `<any house rules: export order, no barrel files, where generated code lives, etc.>`
- Where skills live: `<.claude/skills or your path>` (note any symlink so real files never land in the wrong place).

## One-time repo preconditions (human)

- GitHub Settings → General → "Auto-close issues with merged linked pull requests" must be **on** (not API-queryable — check in the web UI once). If off, `Closes #N` silently does nothing.
