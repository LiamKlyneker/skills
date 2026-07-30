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
runner. The only executable is
`plugins/install-skills/skills/install-skills/scripts/doctor.sh`.

| Purpose | Command |
|---|---|
| Build | None — nothing compiles |
| Test — **verify L2 floor** | `bash -n plugins/install-skills/skills/install-skills/scripts/doctor.sh && bash plugins/install-skills/skills/install-skills/scripts/doctor.sh --repo . --quiet` |
| Manifest check — **also L2 floor** | `claude plugin validate --strict plugins/prd-workflow && claude plugin validate --strict plugins/figma-tools && claude plugin validate --strict plugins/ado-workflow && claude plugin validate --strict plugins/lk && claude plugin validate --strict plugins/install-skills && claude plugin validate --strict .` |
| Catalog + version gate — **also L2 floor** | `python3 .github/scripts/validate_skills.py --base origin/main` |
| Boot the app (visual loop) | `claude plugin list` — the loaded-plugin inventory *is* this repo's running state |
| App screenshot | None — terminal output is the evidence; paste it verbatim |
| Install deps | None |

The manifest check covers both plugin manifests and the marketplace catalog (`.`).
Any new directory carrying a `.claude-plugin/plugin.json` joins that line.

**`--strict`, and zero warnings is the bar.** That row was plain `validate` on purpose
until #57: manifests carried no `version`, the CLI warned about the missing field, and
`--strict` is defined as treating warnings as errors, so the two decisions could not
both hold. All five plugins now carry a `version`, mirrored in
`.claude-plugin/marketplace.json`, which removes the only warning there was and lets
`--strict` in. The convention that came with the old row — the missing-`version`
warning is allowed as the *only* warning — is **gone**; under `--strict` any warning
fails the check and there is nothing left to wave through. Why omitting `version` was
ever the safe choice, and what enforces that discipline now instead, is the
`version` bullet in `## Repo discipline`.

The catalog gate is the only thing CI runs, and the only check this repo owns rather
than borrows from the CLI: marketplace, plugin manifests, skill and agent frontmatter,
symlink integrity, `_shared` references, and the version-bump rule. `--base <ref>` is what switches the bump rule on; **without it that
one check reports itself skipped** and the rest still run. CI passes the pull request's
base SHA and gets nothing on `push: [main]` or `workflow_dispatch`, where no base
branch exists. Locally, `--base origin/main` is the equivalent.

## App facts

- Markdown/prose skills repo · one Bash script (`plugins/install-skills/skills/install-skills/scripts/doctor.sh`) · no runtime, no dependencies.
- **Also a plugin marketplace.** `.claude-plugin/marketplace.json` publishes marketplace `liamklyneker` with five plugins, `plugins/prd-workflow/`, `plugins/figma-tools/`, `plugins/ado-workflow/`, `plugins/lk/` and `plugins/install-skills/`, each carrying a `version` the catalog mirrors. A plugin's skills live in `<plugin>/skills/<skill>/` and its agents in `<plugin>/agents/`; both inventories are discovered from the directory, not listed in the manifest.
- **Every skill is inside a plugin — there are no plain skills left.** The top level is `.claude-plugin/`, `plugins/`, `_shared/` (global reference read by several skills), `install/` (what a consuming project gets wired with), `docs/`, and the two deprecated directories `figma-component/` and `tokens-init/`. The migration's compat shims (top-level symlinks into `plugins/`) were deleted by #26 — do not reintroduce the shape.
- **A plugin namespaces every component it provides.** Skills invoke as `prd-workflow:<skill>`, and agents resolve as `subagent_type: prd-workflow:prd-worker` / `figma-tools:figma-region-extractor`. Bare names exist only on the plain-skill symlink route. An unresolvable `subagent_type` does not error — it silently becomes `general-purpose` — so a wrong type name produces a run that looks entirely normal.
- **The estate inventory is `docs/estate-inventory.md`**: which config directory holds which plain-skill symlink, which repo enables which plugin, and why each is deliberate. Plain skills are placed by hand one link at a time, so that file is the only record of the state; a change to any config's wiring updates it in the same commit.
- **Two delivery routes.** A plugin installed from the marketplace is a *copy* in a config's cache, keyed by the plugin's **`version`** — the git commit SHA is only the fallback key an *unversioned* plugin gets, and all five here are versioned now. So a cache copy pins to its version, and neither an uncommitted edit nor a committed and pushed one reaches it until the version moves; reinstalling at an unchanged version is a silent no-op. Both key shapes are visible in `~/.claude/plugins/cache/` today, because the installs made before #57 have not been refreshed. A `.claude/skills/<name>` symlink pointing at a plugin directory loads as `<name>@skills-dir` with no copy, so edits are live — that is how this repo authors against itself, via the single link `.claude/skills/prd-workflow -> ../../plugins/prd-workflow`. Editing a file through such a symlink edits this repo. Never write "into" a skill via a consumer's link, and never run both routes for one plugin in one place (every skill loads twice).
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

## Sources of truth (recon + hard gates)

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
- **Plugin manifests carry a `version`, and changing a plugin means bumping it** — in `plugins/<name>/.claude-plugin/plugin.json` *and* in `.claude-plugin/marketplace.json`, which must agree; the catalog gate fails if they drift. This bullet used to say the opposite (*omit `version` deliberately*), for a reason that has not stopped being true: `version` is the install cache key, and a forgotten bump means installs silently never see the change. Observed, not assumed — `claude plugin install` at an already-cached version prints `already installed` and re-copies nothing, so a missed bump does not merely delay an update, it strands that consumer until they `uninstall --scope local` by hand. The routes visibly disagree today: `claude plugin list` shows `prd-workflow@skills-dir` at `1.0.0` while `prd-workflow@liamklyneker` still reports `81af34d0d5e1` from its pinned cache copy. Abstaining from versions was the old way to be safe from that; the bump rule in `validate_skills.py` is the new one, so **do not go back to omitting `version`** — dropping the version drops the check with it. A change under `_shared/` or `install/` counts as changing **every** plugin whose `skills/` symlinks it, because install dereferences the link into each cache copy.
- Distribution claims get **verified against the binary and the live config dirs**, never written from memory or from the platform docs. `INSTALL.md` is written from observed behaviour and is the place a corrected observation lands.

## One-time repo preconditions (human)

- GitHub Settings → General → "Auto-close issues with merged linked pull requests" must be **on** (not API-queryable — check in the web UI once). If off, `Closes #N` silently does nothing.
- The `needs-triage` label must exist in `LiamKlyneker/skills` — `to-prd` applies it on CREATE.
