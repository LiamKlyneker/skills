# Project Adapter — LiamKlyneker/skills

Single home for every project-specific fact the skills need. Workflow skills
(`work-on-prd`, `to-issues`, `next-prd-issue`, `work-on-issue`) and `deep-grill`
reference this file and never hardcode these values.

**This repo is the canonical skills repo**, so it is its own install target: what
`.claude/skills/` holds points at sibling directories here rather than at another
clone, and `../_shared/…` from a skill reached that way resolves back into this same
repo. That is self-hosting, not a broken install — expect `doctor` to say so.

## Repo

- Issue tracker / PRs: `LiamKlyneker/skills` (GitHub, via `gh`)
- Default branch: `main` (PRs must target it — `Closes` keywords only fire against the default branch)
- Triage labels: `needs-triage` → `ready-to-start` → `state:in-progress` → `state:done-on-branch`. All four exist in the repo. The vocabulary is normative in `work-on-prd`'s `## Label vocabulary`; this line exists so a cold session that has only this adapter in context knows which tracker and which labels to use without asking.
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
| Manifest check — **also L2 floor** | `claude plugin validate plugins/prd-workflow && claude plugin validate plugins/figma-tools && claude plugin validate plugins/ado-workflow && claude plugin validate .` |
| Boot the app (visual loop) | `claude plugin list` — the loaded-plugin inventory *is* this repo's running state |
| App screenshot | None — terminal output is the evidence; paste it verbatim |
| Install deps | None |

The manifest check covers both plugin manifests and the marketplace catalog (`.`).
Any new directory carrying a `.claude-plugin/plugin.json` joins that line.

**Not `--strict`**, deliberately. Plugin manifests here omit `version` on purpose —
with a version set it becomes the install cache key, and a forgotten bump means
installs silently never see changes. The CLI emits a warning for the missing field,
and `--strict` is defined as treating warnings as errors, so the two decisions cannot
both hold. Plain `validate` must pass with the missing-`version` warning as the *only*
warning; a second warning is a real failure and does not get waved through.

## App facts

- Markdown/prose skills repo · one Bash script (`install-skills/scripts/doctor.sh`) · no runtime, no dependencies.
- **Also a plugin marketplace.** `.claude-plugin/marketplace.json` publishes marketplace `liamklyneker` with three plugins, `plugins/prd-workflow/`, `plugins/figma-tools/` and `plugins/ado-workflow/`. A plugin's skills live in `<plugin>/skills/<skill>/` and its agents in `<plugin>/agents/`; both inventories are discovered from the directory, not listed in the manifest.
- Every *other* top-level directory is one plain skill, except `.claude-plugin/`, `plugins/`, `_shared/` (global reference read by several skills) and `install/` (what a consuming project gets wired with). The migration's compat shims (top-level symlinks into `plugins/`) were deleted by #26 — do not reintroduce the shape.
- **A plugin namespaces every component it provides.** Skills invoke as `prd-workflow:<skill>`, and agents resolve as `subagent_type: prd-workflow:prd-worker` / `figma-tools:figma-region-extractor`. Bare names exist only on the plain-skill symlink route. An unresolvable `subagent_type` does not error — it silently becomes `general-purpose` — so a wrong type name produces a run that looks entirely normal.
- **The estate inventory is `docs/estate-inventory.md`**: which config directory holds which plain-skill symlink, which repo enables which plugin, and why each is deliberate. Plain skills are placed by hand one link at a time, so that file is the only record of the state; a change to any config's wiring updates it in the same commit.
- **Two delivery routes.** A plugin installed from the marketplace is a *copy* in a config's cache, keyed by the git commit SHA, so it pins to committed `HEAD` and uncommitted edits are invisible to it. A `.claude/skills/<name>` symlink pointing at a plugin directory loads as `<name>@skills-dir` with no copy, so edits are live — that is how this repo authors against itself, via the single link `.claude/skills/prd-workflow -> ../../plugins/prd-workflow`. Editing a file through such a symlink edits this repo. Never write "into" a skill via a consumer's link, and never run both routes for one plugin in one place (every skill loads twice).
- Three Claude Code config dirs consume this repo, switched by `$PWD` in `~/.zshrc`: `~/.claude` (personal), `~/.claude-teamsnap`, `~/.claude-schmiede`. Each has its own plugin cache, marketplaces and `enabledPlugins` — they do not share state. **The `claude plugin` CLI ignores `CLAUDE_CONFIG_DIR`** and always reads `~/.claude`, so the other two are inspected by reading their `settings.json`, `plugins/installed_plugins.json` and `plugins/cache/` directly, and installed into only from an in-session `/plugin` under that config.
- **Packaging did not move the project.** Skills resolve `<repo-root>/.claude/project/adapter.md` against the project the session runs in, at runtime — unchanged whether the skill came from a cache directory or a symlink. `INSTALL.md` is the guide for all of the above.

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

- **Branch and open a PR.** The standard workflow, no exceptions — if you are on `main`, branch first. This repo publishes a public marketplace, so a `SKILL.md` edit changes what an agent does on someone else's machine and earns a readable diff plus a green CI run. `main` additionally blocks force-push and deletion for everyone. Still only commit when asked — this governs *how* changes land, not *whether*.
- **CONTEXT.md**: read the scoped `CONTEXT.md` before touching files in any directory (see the `scoped-context` skill), where one exists.
- **No project ever owns a `_shared/`.** Project facts live in `<repo-root>/.claude/project/`. `../_shared/…` from any skill can therefore only mean this repo's global reference.
- Skills address exactly three things: global reference via a relative path into `_shared/`, the project as `<repo-root>/.claude/project/adapter.md`, and project-specific gates **never by name** — the adapter's `## Project gates` registry names them and skills follow the pointer.
- Prose over scripts. `install-skills` ships the only executable, because mechanical checks must be deterministic. Everything else stays prose.
- Adding a skill to a plugin is just the directory under `plugins/<plugin>/skills/` — the inventory is discovered. Adding a **plain** skill means adding a symlink into each config that should see it; creating the directory here does not make it discoverable.
- **Plugin manifests omit `version` deliberately** (see `## Commands`). Do not add one: with a version set it becomes the install cache key, and a forgotten bump means installs silently never see changes.
- Distribution claims get **verified against the binary and the live config dirs**, never written from memory or from the platform docs. `INSTALL.md` is written from observed behaviour and is the place a corrected observation lands.

## One-time repo preconditions (human)

- GitHub Settings → General → "Auto-close issues with merged linked pull requests" must be **on** (not API-queryable — check in the web UI once). If off, `Closes #N` silently does nothing.
- The `needs-triage` label must exist in `LiamKlyneker/skills` — `to-prd` applies it on CREATE.
