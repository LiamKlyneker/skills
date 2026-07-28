# Installing these skills

How the plugins in this repo get onto a machine, into the right config directory, and
enabled for the right project — plus the traps that cost real time when the platform
behaves differently from the docs. Written from what actually worked, not from what the
docs claim.

Everything below is the *distribution* half. The other half — filling in a project's own
facts — is `install-skills`' job and is described in [`install/README.md`](install/README.md).
They are independent: a plugin can be installed with no adapter, and an adapter is worth
having before the plugin lands.

## What ships

| Plugin | Contains | Bundle it serves |
|---|---|---|
| `prd-workflow` | `to-prd`, `to-issues`, `next-prd-issue`, `work-on-prd`, `work-on-issue` + the `prd-worker` agent | `prd-workflow` (which also wants `deep-grill`, a plain skill) |
| `figma-tools` | `figma-to-spec` + the `figma-region-extractor` agent | `figma-tools` |

Both come from marketplace **`liamklyneker`**. Skills from a plugin are invoked namespaced:
`/prd-workflow:work-on-prd`, `/figma-tools:figma-to-spec`.

Everything else in this repo — `deep-grill`, `grill-me`, `install-skills`, `how-i-write`,
`pinpoint`, `qa-prd-log`, `scoped-context`, `triage-prd` — is a plain skill and reaches a
machine by symlink into a config's `skills/` directory. Two delivery modes coexist on
purpose; see [Live authoring](#4-live-authoring-skills-dir-mode).

## Before you start: which config directory

Three Claude Code config directories are switched by `$PWD` in `~/.zshrc`. Each has its own
plugin cache, its own marketplace registry and its own `enabledPlugins` — **they share
nothing**. Installing into one tells you nothing about the others.

| Config | Tenancy | Serves |
|---|---|---|
| `~/.claude` | multi-tenant | personal repos: this one, `liamklyneker`, `neonplace`, `neonplace-ios`, and anything else personal |
| `~/.claude-teamsnap` | single-tenant | TeamSnap repos only |
| `~/.claude-schmiede` | single-tenant | Schmiede repos only |

Pick the scope from the *tenancy*, not from the scope's name:

| Config | Correct scope | Why |
|---|---|---|
| `~/.claude` | **project** | user scope would enable `prd-worker` in every personal repo, including ones that never opted in |
| `~/.claude-teamsnap` | **local** | project scope writes a *committed* `.claude/settings.json` into an employer's repo. Local scope writes `.claude/settings.local.json` instead — confirm the repo ignores it before installing (`organization-frontend-v2` covers it with `.claude/**/*.local.*`) |
| `~/.claude-schmiede` | **user** | its repos refuse scoped writes outright — see [trap 3](#trap-3-a-repo-whose-claude-is-itself-a-symlink-cannot-take-a-scoped-install) |

**In a single-tenant config, user scope *is* the narrow option.** The PRD's "install broadly,
enable narrowly" was written with `~/.claude` in mind and does not generalise. Repeating it
at a single-tenant config sends you straight into trap 3.

**Never use project scope in a client repo.** It writes a committed settings file — exactly
the footprint the plugin migration existed to avoid.

## 1. Add the marketplace

From a session running under the config directory you want it in:

```
/plugin marketplace add LiamKlyneker/skills
```

It registers as **`liamklyneker`** — the name comes from `.claude-plugin/marketplace.json`,
not from the repo or the owner. Confirm with `/plugin marketplace list`.

A GitHub source is recorded portably:

```json
"liamklyneker": { "source": { "source": "github", "repo": "LiamKlyneker/skills" } }
```

That portability matters. A local *directory* source records an absolute path, which cannot
be committed into a project's settings and shared. Use the GitHub form.

A GitHub source clones the **default branch**. A catalog change on a branch is invisible
until it reaches `main`.

## 2. Install the plugin

From a session under the same config directory:

```
/plugin install prd-workflow@liamklyneker
```

Choose the scope when prompted, per the tenancy table above. Then **restart the session** —
a freshly installed plugin does not load into the session that installed it. (`claude plugin
update` says as much in its own help text: *restart required to apply*.)

There is also a CLI form:

```bash
claude plugin install prd-workflow@liamklyneker --scope project   # user | project | local
```

but it only ever acts on `~/.claude`. See [trap 1](#trap-1-the-plugin-cli-ignores-claude_config_dir).
For the two non-default configs the in-session `/plugin` command is the only route.

Repeat per config directory. Nothing is shared between them.

## 3. Enable it for a single project

Installing puts the plugin in the config's cache. **Enabling** is what makes a session see it,
and enablement is a settings key, so it is per-project by construction:

```jsonc
// <repo-root>/.claude/settings.json          — project scope, committed
// <repo-root>/.claude/settings.local.json    — local scope, gitignored
{
  "enabledPlugins": { "prd-workflow@liamklyneker": true }
}
```

Note what is *not* in there: no path, no version, no marketplace source. Just the
`plugin@marketplace` id. The marketplace itself is registered once at user level in the
config's own `settings.json`, so the committed file stays portable.

This is the mechanism that keeps `prd-worker` contained. The agent ships inside
`prd-workflow`, so it is spawnable exactly where the plugin is enabled and nowhere else —
which matters because `prd-worker` commits. A repo that never enabled the plugin reports it
as `✘ disabled` and cannot spawn the agent.

**A missing agent degrades silently to `general-purpose` rather than erroring.** After
wiring a repo, confirm `prd-worker` resolves *by type*; a successful run is not evidence.

## 4. Live authoring: skills-dir mode

An installed plugin is a **copy** in the config's cache, keyed by the **git commit SHA**. It
pins to *committed* `HEAD`, so uncommitted edits in your clone are invisible to it. Correct
behaviour, and it will surprise you once.

For authoring against this repo, use skills-dir mode instead — a symlink in `.claude/skills/`
pointing at the plugin directory:

```bash
# from this repo's root
ln -s ../../plugins/prd-workflow .claude/skills/prd-workflow
```

Any directory under a `.claude/skills/` that carries a `.claude-plugin/plugin.json` loads as a
plugin. Because it is a symlink there is no cache copy, so edits are live on the next session
launch with no reinstall. `claude plugin list` reports it under **Skills-directory plugins**:

```
  ❯ prd-workflow@skills-dir
    Version: unknown
    Scope: project
    Path: ./.claude/skills/prd-workflow
    Status: ✔ loaded
```

That is how this repo self-hosts: one symlink, not one per skill. The same trick works at
config level (`~/.claude/skills/<name>`), which is what `claude plugin init` scaffolds.

**Do not run both modes for the same plugin in the same place.** Every skill loads twice.
`doctor` reports it as `INFO … loads twice` — which is suppressed by `--quiet`, so run
without it when checking cutover state.

Plain skills (no `plugin.json`) use the same directory and load as ordinary skills:

```bash
ln -s /Users/klyneker/liam-klyneker/skills/deep-grill ~/.claude/skills/deep-grill
```

## 5. Bootstrap the project's adapter

Getting the skills is the platform's job. Filling in *your project's* facts is not, and no
distribution mechanism can do it. From the target repo:

```
/install-skills install prd-workflow
```

It copies `install/adapter.template.md` → `.claude/project/adapter.md`, interviews you only
for the facts your repo does not already state, offers any gate the bundle declares, and
finishes with `doctor`.

**Packaging does not touch the adapter.** Skills read it at a path relative to *the project
the session is running in*, resolved at runtime — so a skill served from a plugin cache
directory finds the adapter exactly the way a symlinked one did. Only *creating* the adapter
was ever a bootstrapping problem, which is why `install-skills` kept that half and dropped
everything else.

**A project never owns a `_shared/`.** Still the rule, and still what makes `../_shared/…`
from any skill unambiguous. Inside a plugin, `skills/_shared` is a symlink back to this
repo's single canonical `_shared/`; on install it is dereferenced into a real directory in
the versioned cache. That is a build artifact of a regenerated cache, not an editable
project-side fork, and it does not make a project-owned `_shared/` any less of a problem.

## 6. Verify

```bash
bash install-skills/scripts/doctor.sh --repo <path>      # or: /install-skills doctor
claude plugin list
```

`doctor` looks a plugin up in four places — installed manifests, versioned cache directories,
skills-dir plugins, and a repo-local `plugins/` — across all three config directories, so a
plugin-provided skill no longer reads as `MISSING`. A real directory shadowing one still
reports `FORK`. It scans all three configs because it cannot know which one a session in the
target repo will use; a plugin present in only one config still reads as reachable, and that
is deliberate.

---

## Trap 1: the plugin CLI ignores `CLAUDE_CONFIG_DIR`

Config switching depends entirely on that variable, and `claude plugin` does not honour it.
Point it at a throwaway directory and the CLI still reads `~/.claude` — for plugins *and* for
marketplaces:

```console
$ CLAUDE_CONFIG_DIR=/tmp/throwaway claude plugin list
Installed plugins:

  ❯ figma-tools@liamklyneker
    Version: ac7a89ab018a
    Scope: user
    Status: ✔ enabled
...

$ CLAUDE_CONFIG_DIR=/tmp/throwaway claude plugin marketplace list
Configured marketplaces:

  ❯ claude-plugins-official
  ❯ claude-code-warp
  ❯ liamklyneker

$ ls -A /tmp/throwaway
# empty — nothing was ever read from or written to it
```

Two consequences:

- **Installs must go through the in-session `/plugin` command**, from a session launched under
  the config you want, or they land in `~/.claude` regardless of the environment.
- **You cannot inspect a non-default config from the CLI either.** `claude plugin list` always
  reports `~/.claude`. To see what `~/.claude-teamsnap` or `~/.claude-schmiede` actually has,
  read their files:

  | File | Tells you |
  |---|---|
  | `<config>/settings.json` | `enabledPlugins`, `extraKnownMarketplaces` |
  | `<config>/plugins/installed_plugins.json` | scope, `projectPath`, `gitCommitSha` |
  | `<config>/plugins/cache/<marketplace>/<plugin>/<sha>/` | what actually got copied |

## Trap 2: omit `version` from the plugin manifest

The single most-reported plugin footgun. **Set a `version` and it becomes the install cache
key.** Forget to bump it and every install silently keeps serving the old copy — no error, no
warning, just changes that never arrive.

Omit the field and the cache key is the **git commit SHA** instead, which cannot be forgotten:

```
~/.claude/plugins/cache/liamklyneker/prd-workflow/ac7a89ab018a/
```

Both manifests here omit it deliberately. The cost is a warning:

```console
$ claude plugin validate plugins/prd-workflow
⚠ Found 1 warning:
  ❯ version: No version specified. Consider adding a version following semver (e.g., "1.0.0")
✔ Validation passed with warnings
```

So the structural check here is plain `validate`, **never `--strict`** — `--strict` treats
warnings as errors, and the two decisions cannot both hold. The missing-`version` warning must
be the *only* warning; a second one is a real failure and does not get waved through. The
marketplace manifest reports one such warning per plugin it lists (two today).

## Trap 3: a repo whose `.claude` is *itself* a symlink cannot take a scoped install

If `<repo>/.claude` is a symlink — a team-owned `.agents/` directory, say — both project and
local scope fail outright:

```
Failed to update settings: Failed to read raw settings from
<repo>/.claude/settings.local.json:
SymlinkWriteRefusedError: Refusing to write into symlinked directory: <repo>/.claude
```

**Only user scope works there**, because it writes into the config directory rather than into
the repo. In a single-tenant config that is fine — user scope is already the narrow option.

Distinguish this from the shape that *does* work: a **real** `.claude/` directory with things
symlinked *inside* it writes without complaint. `neonplace` has `.claude/skills -> ../.agents/skills`
and `.claude/agents -> ../.agents/agents` and takes a project-scope install fine. It is only a
symlinked `.claude` itself that is refused.

## Naming: `figma-tools`, never `figma`

`figma@claude-plugins-official` owns that name. A collision reports `Not loaded — the name
"figma" is already taken`, and it is not marketplace-only: a second `figma` in a config's
`skills/` breaks skills-dir loading too. The bundle in `install/bundles.md` was renamed to
follow the plugin.

---

## The estate today

What is actually installed, for orientation when something looks wrong.

| Config | Plugin | Scope | Where |
|---|---|---|---|
| `~/.claude` | `prd-workflow@liamklyneker` | project | `liam-klyneker/liamklyneker`, `creative-ghost/neonplace`, `creative-ghost/neonplace-ios` — committed `.claude/settings.json` in each |
| `~/.claude` | `figma-tools@liamklyneker` | user | everywhere under the personal config |
| `~/.claude` | `prd-workflow@skills-dir` | project | this repo, via `.claude/skills/prd-workflow` |
| `~/.claude-teamsnap` | `prd-workflow@liamklyneker` | local | `teamsnap/organization-frontend-v2` — gitignored `settings.local.json` |
| `~/.claude-schmiede` | none | — | marketplace registered only; deliberately out of scope |
