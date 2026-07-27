# Project Adapter — LiamKlyneker/skills

Single home for every project-specific fact the skills need. Workflow skills
(`work-on-prd`, `to-issues`, `next-prd-issue`, `work-on-issue`) and `deep-grill`
reference this file and never hardcode these values.

**This repo is the canonical skills repo**, so it is its own install target: the
symlinks in `.claude/skills/` point at sibling directories here rather than at
another clone, and `../_shared/…` from a symlinked skill resolves back into this
same repo. That is self-hosting, not a broken install — expect `doctor` to say so.

## Repo

- Issue tracker / PRs: `LiamKlyneker/skills` (GitHub, via `gh`)
- Default branch: `main` (PRs must target it — `Closes` keywords only fire against the default branch)
- Related repos (cross-repo issues, API contracts): None. Consumer repos exist
  (`creative-ghost/neonplace`, `creative-ghost/neonplace-ios`,
  `liam-klyneker/liamklyneker`) but they consume this repo's output — there is no
  shared contract to keep in sync, so a finding there is a finding here.

## Commands

This is a **prose repo**. There is no build, no package manager, and no test
runner. The only executable is `install-skills/scripts/doctor.sh`.

| Purpose | Command |
|---|---|
| Build | None — nothing compiles |
| Test — **verify L2 floor** | `bash -n install-skills/scripts/doctor.sh && bash install-skills/scripts/doctor.sh --repo . --quiet` |
| Boot the app (visual loop) | `claude plugin list` — the loaded-plugin inventory *is* this repo's running state |
| App screenshot | None — terminal output is the evidence; paste it verbatim |
| Install deps | None |

Once a directory here carries a `.claude-plugin/plugin.json`, its structural check
becomes `claude plugin validate <dir> --strict` and that joins the L2 floor.

## App facts

- Markdown/prose skills repo · one Bash script (`install-skills/scripts/doctor.sh`) · no runtime, no dependencies.
- Every top-level directory is one skill, except `_shared/` (global reference read by several skills) and `install/` (what a consuming project gets wired with).
- Skills are consumed by **symlink** into config dirs under `~/.claude*/skills/` and into project `.claude/skills/`. Editing a file through a symlink edits this repo. Never write "into" a skill via a consumer's symlink.
- Three Claude Code config dirs consume this repo, switched by `$PWD` in `~/.zshrc`: `~/.claude` (personal), `~/.claude-teamsnap`, `~/.claude-schmiede`. Each has its own plugin cache, marketplaces and `enabledPlugins` — they do not share state.

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: `bash -n` on any changed shell script passes, and `doctor.sh` runs clean against at least one wired consumer repo. For a docs-only change, L2 is that every relative path the change introduces or moves actually resolves (`ls` the target).
- **L3 — user-visible issues**: L2 + the change is *loaded* by a real Claude Code config and shown to be there — `claude plugin list` for a plugin, or the skill appearing in a fresh session for a skill. Paste the command output as evidence. "User-visible" here means anything that changes what a session discovers or how a skill behaves.
- **L4** (agent-driven interaction): out of scope.
- **L5 — human**: once per PRD, via the QA doc, on the branch, before merge. For this repo that means actually running the affected skill end-to-end in a live session.

## QA doc convention

- Path: `docs/qa/prd-<n>.md` (`<n>` = PRD issue number), committed on the PRD branch, linked from the PR body.
- Per issue: what shipped · how to exercise it in a real session (which config dir, which command, what to look for) · edge cases the worker flagged.
- The human runs it start-to-finish before merging.

## Sources of truth (`deep-grill` recon + hard gates)

- **Project explorer agent**: None — use `Explore`. This repo is small and entirely prose; a custom explorer would be dead config.
- **Contract-boundary explorer agent**: None — no contract boundary.
- **Access-policy source**: None — no stored data, no user-scoped data layer.

Two sources of truth sit **outside** this repo and must be read rather than assumed
whenever a change touches distribution:

- The live config dirs (`~/.claude`, `~/.claude-teamsnap`, `~/.claude-schmiede`) — what is actually linked and installed today.
- The Claude Code plugin CLI (`claude plugin --help`, `list`, `details`, `validate`) — the platform's real behaviour, which has repeatedly differed from the docs. Verify against the binary before writing a claim down.

## Project gates

None — no gates beyond the ones the skills carry.

## Repo discipline

- **Commit straight to `main`.** Do not branch and open a PR by default; this repo's history is linear and direct-to-main. Branch only when explicitly asked, or for a sweeping restructure across many skills. Still only commit when asked — this governs *where*, not *whether*.
- **CONTEXT.md**: read the scoped `CONTEXT.md` before touching files in any directory (see the `scoped-context` skill), where one exists.
- **No project ever owns a `_shared/`.** Project facts live in `<repo-root>/.claude/project/`. `../_shared/…` from any skill can therefore only mean this repo's global reference.
- Skills address exactly three things: global reference via a relative path into `_shared/`, the project as `<repo-root>/.claude/project/adapter.md`, and project-specific gates **never by name** — the adapter's `## Project gates` registry names them and skills follow the pointer.
- Prose over scripts. `install-skills` ships the only executable, because mechanical checks must be deterministic. Everything else stays prose.
- Adding a skill means adding a symlink too; creating the directory here does not make it discoverable.

## One-time repo preconditions (human)

- GitHub Settings → General → "Auto-close issues with merged linked pull requests" must be **on** (not API-queryable — check in the web UI once). If off, `Closes #N` silently does nothing.
- The `needs-triage` label must exist in `LiamKlyneker/skills` — `to-prd` applies it on CREATE.
