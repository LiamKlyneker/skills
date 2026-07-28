# Project Adapter — TEMPLATE

Single home for every project-specific fact the skills need. Workflow skills (`work-on-prd`, `to-issues`, `next-prd-issue`, `work-on-issue`) and `deep-grill` reference this file and never hardcode these values. (`grill-me` deliberately does **not** — it is the lightweight inline grill and reads nothing from here.) Porting the workflow to another repo = install the plugin + fill in this file, nothing else.

> **This is a template.** Copy it to `<repo-root>/.claude/project/adapter.md` and fill every `<placeholder>` with your project's real values before running `work-on-prd`. Delete rows that don't apply; add rows the workflow needs. Nothing else in the skills should mention a tool, path, or command by name — if it does, lift it into this file.

**Canonical source:** skill *logic* is canonical in **`LiamKlyneker/skills`** and reaches a project either as an installed plugin from marketplace `liamklyneker` or as a symlink into a config's `skills/` directory. Either way there is nothing to back-port — an installed copy is a regenerated cache keyed by git commit, never a place to edit. Project *facts* live in `<repo-root>/.claude/project/`, which is the one directory skills resolve from the repo root, and they resolve it against the project the session is running in regardless of how the skill was delivered. A project never owns a `_shared/`: `../_shared/…` from any skill can therefore only ever mean the canonical global-reference files in the skills repo.

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

## Project gates

Extra hard gates this project runs, on top of the ones the skills already carry. Each one is a **sibling of this file** in `.claude/project/`, and this table is the **only** place it is named — canonical skills never name a project gate directly, they read this registry and follow the pointer. That is what keeps a skill like `to-prd` generic instead of forked to hardcode one project's filename.

Gates live in their own files rather than inline here for a concrete reason: `work-on-prd` pastes the **full contents of this adapter** into every worker prompt, so anything parked here is a tax on every worker, most of whom don't need it.

| Gate | File | Runs when |
|---|---|---|
| `<gate name>` | `./<gate>.md` | `<the trigger — the condition under which a plan must run it, and when it may be skipped>` |

Or "None — no gates beyond the ones the skills carry."

A project-flavored `ui-manifests.md` (concrete primitive homes, real token files, this stack's traps and test vehicle) is registered here the same way; the row schema itself stays canonical in `_shared/ui-manifests.md`.

## Repo discipline

- **CONTEXT.md**: read the scoped `CONTEXT.md` before touching files in any directory (see the `scoped-context` skill). Update it only if documented architecture changes.
- `<any house rules: export order, no barrel files, where generated code lives, etc.>`
- Where skills come from: `<installed plugin + scope, or a symlink in .claude/skills/>`. Either way the skill files are not this project's to edit: a plugin cache is regenerated on install, and a symlink writes straight into the canonical repo. Project facts and gates live in `.claude/project/` instead, which is real and committed.

## One-time repo preconditions (human)

- GitHub Settings → General → "Auto-close issues with merged linked pull requests" must be **on** (not API-queryable — check in the web UI once). If off, `Closes #N` silently does nothing.

<!--
`install-skills doctor` flags any `<token>` that appears in **both** this template and a
filled adapter, on the theory that it was never filled in. A few angle-bracket tokens here
are notation rather than placeholders and are legitimately still there after filling —
list them below so the check stays quiet about them and loud about everything else.

doctor:not-a-placeholder <repo-root> <n>
-->

