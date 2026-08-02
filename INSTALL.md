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
| `prd-workflow` | `to-prd`, `to-issues`, `next-prd-issue`, `work-on-prd`, `work-on-issue`, `manual-qa`, `triage` + the `prd-worker` agent | **two** bundles: `prd-workflow` (the five loop skills) and `prd-qa` (`manual-qa` + `triage`) |
| `ado-workflow` | `to-spec`, `to-spec-tasks`, `next-task-to-implement`, `work-on-spec`, `manual-qa`, `triage` + the `spec-worker` agent | **two** bundles: `ado-workflow` (the four loop skills) and `ado-qa` (`manual-qa` + `triage`) |
| `figma-tools` | `figma-to-spec` + the `figma-region-extractor` agent | `figma-tools`. Adapter-free |
| `lk` | `grill`, `deep-grill`, `pinpoint`, `how-i-write`, `scoped-context` | `grill` (`grill` + `deep-grill`) — one bundle, and not the whole plugin; the other three ask for nothing |
| `install-skills` | `install-skills` — and `scripts/doctor.sh`, the only executable in the repo | none; it is what *writes* the adapter a bundle needs, so it must be reachable before any bundle is adopted |

All five come from marketplace **`liamklyneker`**. Skills from a plugin are invoked
namespaced: `/prd-workflow:work-on-prd`, `/ado-workflow:work-on-spec`,
`/figma-tools:figma-to-spec`, `/lk:grill`, `/install-skills:install-skills`. That last one
doubles because the skill and its plugin share a name — the prefix is the plugin, the
suffix is the skill, and neither half is optional.

**Every skill in this repo is inside one of those five plugins, and installing one of those
plugins is the only way any of them reaches a machine.** There is no second route. Nothing
here is hand-placed into a `skills/` directory, and a link that made a skill load would be a
bug rather than a shortcut — the validator fails on one. Authoring against the working tree
is a separate mechanism with its own flag; see [Dev mode](#4-dev-mode). The
reasoning is ADR [0010](docs/adr/0010-one-distribution-one-dev-mode.md).

## Before you start: which config directory, and at what scope

You may have more than one Claude Code config directory — a common arrangement is one per
client or employer, switched by `$PWD` in a shell profile. Each has its own plugin cache, its
own marketplace registry and its own `enabledPlugins`; **they share nothing**, so installing
into one tells you nothing about the others.

**Pick the scope from the config's tenancy, not from the scope's name.**

| Tenancy | Correct scope | Why |
|---|---|---|
| **Multi-tenant** — one config serving many unrelated repos | **project** | user scope would enable the plugin's agents in *every* repo that config serves, including ones that never opted in |
| **Single-tenant, client repo** | **local** | project scope writes a *committed* `.claude/settings.json` into someone else's repo. Local scope writes `.claude/settings.local.json` instead — confirm the repo ignores it before installing |
| **Single-tenant, repo that refuses scoped writes** | **user** | see [trap 3](#trap-3-a-repo-whose-claude-is-itself-a-symlink-cannot-take-a-scoped-install) |

**In a single-tenant config, user scope *is* the narrow option.** "Install broadly, enable
narrowly" was written with a multi-tenant config in mind and does not generalise; repeating it
at a single-tenant config sends you straight into trap 3.

**Never use project scope in a client repo.** It writes a committed settings file — exactly
the footprint the plugin migration existed to avoid.

*Worked example — Liam's machine, as of PRD #52's close:* `~/.claude` is multi-tenant across
personal repos and takes **project** scope; `~/.claude-teamsnap` is single-tenant and takes
**local**; `~/.claude-schmiede` is single-tenant over repos whose `.claude` is a symlink, so it
takes **user**. That is an illustration of the table above, not state this repo tracks — see
ADR [0007](docs/adr/0007-a-marketplace-not-an-estate-manager.md).

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

A GitHub source resolves the **default branch** unless you give it a `ref` (a branch or tag
— `sha` is accepted for a *plugin* source, not for a marketplace one):

```json
"liamklyneker": { "source": { "source": "github", "repo": "LiamKlyneker/skills", "ref": "main" } }
```

So by default a catalog change on a branch is invisible until it reaches `main`. Pinning a
`ref` is the escape hatch, but it is a config edit per iteration — for *authoring*, use
[dev mode](#4-dev-mode) instead, which ignores branches entirely.

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

Set `CLAUDE_CONFIG_DIR` to target a non-default config — that works as of 2.1.220, though it
did not always; see [trap 1](#trap-1-fixed-the-plugin-cli-once-ignored-claude_config_dir).

```bash
CLAUDE_CONFIG_DIR="$HOME/.claude-teamsnap" claude plugin install prd-workflow@liamklyneker --scope local
```

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

**Plugin components are namespaced, agents included.** The type is
**`prd-workflow:prd-worker`**, not the bare `prd-worker` — same prefix the skills get
(`/prd-workflow:work-on-prd`). The unprefixed name only ever belonged to the pre-plugin
route, a hand-placed file in an `agents/` directory. Same for
`figma-tools:figma-region-extractor`.

**A missing agent degrades silently to `general-purpose` rather than erroring.** After
wiring a repo, confirm `prd-workflow:prd-worker` resolves *by type* — list the available
agent types in a fresh session and read the name. A successful run is not evidence: the
skills are written to fall back to `general-purpose` when the type does not resolve, so the
broken case and the working case produce the same output. This has bitten twice — once from
a missing agent link, once from packaging renaming the type out from under the skills.

## 4. Dev mode

**Authoring runs through `--plugin-dir`.** Not through an install, and not through a symlink.

An installed plugin is a **copy** in the config's cache, keyed by the plugin's **`version`**.
From a **`github`** source it pins to *committed* `HEAD` on the default branch, so uncommitted
edits in your clone are invisible to it — and, because the key is the version rather than the
commit, a *committed and pushed* edit is invisible too until the version moves. Correct
behaviour, and it will surprise you once; see
[trap 2](#trap-2-version-is-the-install-cache-key-and-a-forgotten-bump-is-silent).

So do not author against an install. Load the plugin directly from its directory:

```bash
# from this repo's root
claude --plugin-dir plugins/prd-workflow
```

```
--plugin-dir <path>   Load a plugin from a directory or .zip for this session only
                      (repeatable: --plugin-dir A --plugin-dir B.zip)
```

Four properties make this the authoring route and not merely one option among several:

- **Nothing is copied and nothing is recorded.** No cache directory, no entry in
  `installed_plugins.json`, no `enabledPlugins` key. It ends with the session.
- **It ignores branches.** The flag reads a path, so an unmerged plugin change is testable
  without reaching `main` and without pinning a `ref`.
- **It takes precedence** over an installed copy of the same plugin for that session, so you
  can shadow a released version while working on the next one.
- **Namespacing is unchanged.** Skills still invoke as `prd-workflow:work-on-prd`, and the
  agent type is still `prd-workflow:prd-worker`. Nothing about the packaging contract differs
  from an install — including `skills/_shared`, which resolves live through the packaging
  symlink here and is dereferenced into the cache on a real install.

Repeat the flag for each plugin you are working on:

```bash
claude --plugin-dir plugins/lk --plugin-dir plugins/prd-workflow
```

`--plugin-url <url>` is the same thing for a `.zip` fetched over HTTP, and `--bare` skips
`--plugin-dir` along with hooks, settings and MCP — worth knowing when a session is not
loading what you expect.

**Verify without installing.** Two commands close the loop before a PR:

```bash
claude plugin validate plugins/prd-workflow   # a plugin manifest
claude plugin validate .                      # the marketplace manifest
claude plugin tag plugins/prd-workflow        # {name}--v{version} tag; fails if
                                              # plugin.json and the catalog disagree
```

That last one enforces ADR [0001](docs/adr/0001-version-the-plugins-and-enforce-the-bump.md)'s
bump rule at the platform level, alongside this repo's own
`.github/scripts/validate_skills.py`.

**There is no symlink in any of this.** A link under `.claude/skills/` that made a plugin load
was the old route; it is gone, and `validate_skills.py` fails on one. The packaging symlinks
inside `plugins/*/skills/` are a different thing entirely and are load-bearing — ADR
[0010](docs/adr/0010-one-distribution-one-dev-mode.md) draws the line.

## 5. Local-directory marketplace: for testing install mechanics

Dev mode covers authoring. It does not exercise the thing that makes a plugin *installed* — the
cache copy, the install record, the scope prompt, the dereferenced `_shared`. When the install
mechanics are themselves what you are testing, register a marketplace whose source is a **local
directory**: a real install, no merge in the loop.

This is a narrow tool. If you are editing a `SKILL.md`, you want [§4](#4-dev-mode).

**Give the dev clone a different marketplace name.** The registry key comes from
`.claude-plugin/marketplace.json`'s `name` field, so a clone of *this* repo declares
`liamklyneker` — the name already registered from GitHub. Edit the clone's `name` to something
like `liamklyneker-dev` before registering it. Two entries offering the same plugin under one
name is not a state worth discovering the behaviour of.

```
/plugin marketplace add /path/to/your/dev/clone
```
```console
Successfully added marketplace: liamklyneker-dev
```

A directory source is recorded differently from a GitHub one, and **nothing is cloned** — the
`installLocation` is the directory itself, where a GitHub source gets a copy under
`~/.claude/plugins/marketplaces/<name>/`:

```json
"liamklyneker-dev": {
  "source": { "source": "directory", "path": "/path/to/your/dev/clone" },
  "installLocation": "/path/to/your/dev/clone"
}
```

That is the absolute path [§1](#1-add-the-marketplace) warns about. It is fine here precisely
because a dev marketplace is never shared or committed — but it does mean **moving the clone
breaks the marketplace**. Re-run `marketplace add` against the new path: an existing name is
updated in place (`✔ Successfully added marketplace: liamklyneker-dev`), so you never need
`marketplace remove` merely to relocate a dev clone. Given what `remove` does to the registry,
that distinction is worth knowing.

Then install as usual — `/plugin install <plugin>@liamklyneker-dev`. Observed on a run of this:

- **It did not prompt for scope.** It silently chose **project**, pinned to the cwd's repo.
  Pass `--scope` on the CLI form if you want to be sure.
- **The skills registered mid-session**, without the restart the success message asks for. The
  **agent type** was only confirmed in a fresh session — whether it would have resolved in the
  installing session was not tested, so assume it needs the restart.
- `skills/_shared` was dereferenced into a real directory in the cache, and `agents/` carried
  the agent, exactly as from a GitHub source. The packaging contract is unchanged by the route.

### It copies the working tree — and mislabels it

A directory source reads your **working tree**, not committed `HEAD`. Both halves were tested
with uncommitted edits: a rename in `marketplace.json` was honoured at registration, and a
marker line added to a `SKILL.md` appeared in the install cache.

But the install record still labels that cache with `HEAD`'s SHA:

```json
{ "version": "256cfd9bfa0c", "gitCommitSha": "256cfd9bfa0cb2ec5805f32283543be177f74111" }
```

**The version string names a commit whose content is not what got copied.** Do not read a SHA
in `claude plugin list` as evidence of what a dev install contains; the only authority is the
cache directory itself.

### Refreshing after an edit

This is where
[trap 2](#trap-2-version-is-the-install-cache-key-and-a-forgotten-bump-is-silent) bites from
an unexpected direction. The cache key does not move when your *files* move, so after the
first install nothing notices your changes. The observation below was captured before the
manifests carried versions, when the key was still the commit SHA and an uncommitted edit
could not shift it:

```console
$ claude plugin install ado-workflow@liamklyneker-dev --scope project
✔ Plugin "ado-workflow@liamklyneker-dev" is already installed (scope: project)

$ claude plugin update ado-workflow@liamklyneker-dev --scope project
✔ ado-workflow is already at the latest version (256cfd9bfa0c).
```

**Setting a version made this worse, not better.** The key is now the manifest's `version`,
so on a dev loop it does not move until you bump it by hand — the same `already installed`
no-op, but reachable by committing, pushing and merging as well as by editing in place.
That trade, and why it was still worth making, is
[ADR 0001](docs/adr/0001-version-the-plugins-and-enforce-the-bump.md).

Both commands are no-ops, and the cache still holds the copy from the *first* install. Only
the full cycle re-copies:

```bash
claude plugin uninstall <plugin>@liamklyneker-dev --scope project
claude plugin install   <plugin>@liamklyneker-dev --scope project   # then restart
```

So the loop is **edit → uninstall → install → restart**, which is exactly why this is not the
authoring route. Uninstalling does **not** delete the cache directory, so
`cache/<marketplace>/<plugin>/` accumulates one directory per cache key you ever installed;
only the one named in `installed_plugins.json` is live, and the rest are stale copies safe
to delete. Both shapes of key turn up in that tree — a versioned one like `lk/1.3.0/`, and a
bare SHA like `prd-workflow/81af34d0d5e1/` from an install predating the versions.
Note also that `uninstall` and `update` both default to **`--scope user`** and fail outright
against an install at any other scope (`✘ Failed to uninstall … is not installed in user
scope. Use --scope to specify`); pass the scope every time.

A local marketplace has to be registered separately in each config — they share nothing —
but the CLI can target any of them via `CLAUDE_CONFIG_DIR`
([trap 1](#trap-1-fixed-the-plugin-cli-once-ignored-claude_config_dir)).

### Graduating to the GitHub source

Once the plugin is on `main`, the order matters:

1. `claude plugin uninstall <plugin>@liamklyneker-dev --scope <scope>`
2. `/plugin marketplace remove liamklyneker-dev`
3. `/plugin install <plugin>@liamklyneker` — the GitHub source
4. Restart

Uninstall *before* removing the marketplace. **`/plugin marketplace remove <name>` drops every
installed-plugin registry entry sourced from that marketplace**, not only the one you were
working on — observed once against `liamklyneker`, which took out `figma-tools` and three
`prd-workflow` entries in a single command. The `enabledPlugins` keys in each project's
`settings.json` survive, so the damage reads as plugins that are enabled but no longer
installed. Back up `~/.claude/plugins/installed_plugins.json` before you run it.

**What a user runs never changes.** A marketplace source decides only where the copy came from;
the plugin content, the skill names and the agent types are identical either way.

## 6. Bootstrap the project's adapter

Getting the skills is the platform's job. Filling in *your project's* facts is not, and no
distribution mechanism can do it. From the target repo:

```
/install-skills:install-skills install prd-workflow
```

The doubled name is the plugin prefix plus the skill name; `install-skills` is its own
plugin precisely so that reaching it never requires adopting anything else.

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

## 7. Verify

Before publishing, from this repo:

```bash
python3 .github/scripts/validate_skills.py     # catalog, manifests, frontmatter, symlinks
claude plugin validate .                       # the marketplace manifest
claude plugin validate plugins/<name>          # one plugin manifest
```

After wiring a project:

```bash
bash plugins/install-skills/skills/install-skills/scripts/doctor.sh --repo <path>
# or, from any session that has the plugin: /install-skills:install-skills doctor
claude plugin list
```

`doctor` looks a plugin up in installed manifests, versioned cache directories, and a
repo-local `plugins/`, across every config directory it can see — it cannot know which config
a session in the target repo will use, so a plugin present in only one still reads as
reachable, and that is deliberate. It checks reachability, the adapter and the gates; it does
**not** audit what any machine has lying around in a `skills/` directory (ADR
[0007](docs/adr/0007-a-marketplace-not-an-estate-manager.md), ADR
[0010](docs/adr/0010-one-distribution-one-dev-mode.md)).

---

## Trap 1 (fixed): the plugin CLI once ignored `CLAUDE_CONFIG_DIR`

**This no longer applies. Re-verified on 2.1.220 — the CLI honours the variable, for reads
and for writes.** Kept because the old behaviour is still described in ADR
[0007](docs/adr/0007-a-marketplace-not-an-estate-manager.md), and because anyone on an
older build will still hit it.

It used to be that config switching depended entirely on that variable and `claude plugin`
did not honour it: pointed at a throwaway directory the CLI still read `~/.claude`, for
plugins *and* for marketplaces, leaving the throwaway untouched. The consequences were that
installs into a non-default config had to go through the in-session `/plugin` command, and
that a non-default config could not be inspected from the CLI at all.

What was observed on **2.1.220** instead:

```console
$ CLAUDE_CONFIG_DIR=~/.claude-schmiede claude plugin list
Installed plugins:

  ❯ ado-workflow@liamklyneker      # this config's plugin, not ~/.claude's
    Scope: user
    Status: ✔ enabled

$ CLAUDE_CONFIG_DIR=~/.claude-schmiede claude plugin install lk@liamklyneker --scope user
✔ Successfully installed plugin: lk@liamklyneker (scope: user)
# ~/.claude-schmiede/plugins/installed_plugins.json changed; the other configs did not
```

So the CLI form now works against any config:

```bash
CLAUDE_CONFIG_DIR="$HOME/.claude-<name>" claude plugin install <plugin>@liamklyneker --scope user
CLAUDE_CONFIG_DIR="$HOME/.claude-<name>" claude plugin update  <plugin>@liamklyneker --scope user
```

Two things that did **not** change, and still bite:

- **`update` and `uninstall` default to `--scope user`** and fail outright against an install
  at any other scope. Pass `--scope` every time.
- **A marketplace clone goes stale.** `install` against a catalog entry your local clone
  predates fails with *"not found in marketplace … your local copy may be out of date"*. Run
  `claude plugin marketplace update <name>` first — per config, since they share nothing.

If you need the raw state rather than the CLI's view, these are still the files:

| File | Tells you |
|---|---|
| `<config>/settings.json` | `enabledPlugins`, `extraKnownMarketplaces` |
| `<config>/plugins/installed_plugins.json` | scope, `projectPath`, `gitCommitSha` |
| `<config>/plugins/cache/<marketplace>/<plugin>/<version-or-sha>/` | what actually got copied |

## Trap 2: `version` is the install cache key, and a forgotten bump is silent

The single most-reported plugin footgun, and the reason every manifest in this repo went
without a version number for as long as it did. **Set a `version` and it becomes the install
cache key.** Forget to bump it and every install keeps serving the old copy — no error, no
warning, just changes that never arrive.

The mechanism is real and measured, not folklore. Reinstalling at an unchanged version
re-copies nothing and says so cheerfully:

```console
✔ Plugin "install-skills@liamklyneker-dev" is already installed
```

Only `uninstall --scope <scope>` followed by a fresh `install` refreshes the cache. So a
missed bump does not *delay* an update; it strands that consumer on stale files until they
uninstall by hand.

Omit the field and the cache key is the **git commit SHA** instead, which cannot be
forgotten. Both key shapes exist in the cache right now — the version directory from a
manifest that has one, the SHA directory from an install that predates them:

```
~/.claude/plugins/cache/liamklyneker-dev/lk/1.0.0/
~/.claude/plugins/cache/liamklyneker/prd-workflow/81af34d0d5e1/
```

**Every manifest here omitted `version` deliberately, and none of them does now.** All five
plugins carry `1.0.0`, mirrored in `.claude-plugin/marketplace.json`. Nothing above stopped
being true — the reversal replaced *abstinence* with *enforcement*:

- **The bump is checked, not remembered.** `check_version_bumps()` in
  `.github/scripts/validate_skills.py` fails any plugin whose files changed against the fork
  point without its `version` moving, and fails a manifest whose version and catalog entry
  disagree. It needs a base ref (`--base <ref>` or `VALIDATE_BASE_REF`); given none, that one
  check reports itself skipped rather than passing quietly, and every other check still runs.
- **`--strict` is now the bar, where it used to be ruled out.** The missing-`version` warning
  was the one warning the old scheme had to tolerate, and tolerating a warning is
  incompatible with a flag that treats warnings as errors. With the field set there is
  nothing left to wave through:

  ```console
  $ claude plugin validate --strict plugins/prd-workflow
  Validating plugin manifest: /Users/klyneker/liam-klyneker/skills/plugins/prd-workflow/.claude-plugin/plugin.json

  ✔ Validation passed
  ```

  All five plugins and the marketplace catalog pass `--strict` with zero warnings.
- **A change under `_shared/` or `install/` changes every plugin that symlinks it**, because
  install dereferences the link into each cache copy. One shared-doc edit therefore costs
  several bumps. That is real tedium, and it is the accepted price: tedium is recoverable and
  silent staleness is not.

Why the reversal was worth making at all — a SHA is not something a consumer can read, pin
to, or roll back along, and this is a public catalog of executable prose — is
[ADR 0001](docs/adr/0001-version-the-plugins-and-enforce-the-bump.md). **Read it before
restoring the old rule from history.** The reasoning that once recommended omitting `version`
was never wrong; it is now the justification for the gate rather than for abstinence, and
dropping the version would drop the check along with it.

**Setting a version is not releasing one.** `claude plugin tag` creates a `{name}--v{version}`
git tag and validates that `plugin.json` and the enclosing marketplace entry agree — but
nothing here is tagged, and `git tag` is empty. Tagging a release is a deliberate act, not a
side effect of carrying a version.

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

## Trap 4: a project-scope install writes into the repo, and the file is not gitignored

Project scope is a settings key ([§3](#3-enable-it-for-a-single-project)), so installing at that
scope **creates or edits `<repo>/.claude/settings.json`** — a tracked-by-default file appearing
in `git status` as a side effect of a plugin command:

```console
$ git status --short
?? .claude/settings.json
```

For a normal install that content is exactly what you want committed. For a **dev install it is
not**: the id carries the dev marketplace name, which resolves to an absolute path on one
machine and nowhere else.

```jsonc
{ "enabledPlugins": { "ado-workflow@liamklyneker-dev": true } }   // never commit this
```

`.gitignore` here covers `.claude/settings.local.json` but **not** `.claude/settings.json` —
correctly, since the committed form is the sharing mechanism. So the guard has to be your eyes:
after any dev install, check `git status` before staging, and never reach for `git add -A`.
Prefer `--scope local` for dev installs where the repo allows it — that writes the gitignored
file instead — but note [trap 3](#trap-3-a-repo-whose-claude-is-itself-a-symlink-cannot-take-a-scoped-install)
rules local scope out wherever `.claude` is a symlink.

## Naming: `figma-tools`, never `figma`

`figma@claude-plugins-official` owns that name. A collision reports `Not loaded — the name
"figma" is already taken`, and it is not marketplace-only — a `--plugin-dir` load of a plugin
named `figma` collides with the installed one just as readily. The bundle in
`install/bundles.md` was renamed to follow the plugin.

---

## What this repo does not track

**Who has installed what.** This repo publishes a versioned marketplace and its
responsibility ends there: a coherent catalog, and a `version` that moves whenever a plugin's
content does. Whether any given machine has installed it, at which version, is that machine's
business — a stale or broken install is an ordinary bug, diagnosed in the config where it
surfaces, at the moment it surfaces. The argument is ADR
[0007](docs/adr/0007-a-marketplace-not-an-estate-manager.md), including why the bump rule in
[trap 2](#trap-2-version-is-the-install-cache-key-and-a-forgotten-bump-is-silent) gets
*stricter* under that posture rather than looser.

So there is no current inventory here, and there is not meant to be. There was one —
`docs/estate-inventory.md`, kept for the platform behaviour it recorded rather than for the
inventory — and ADR [0010](docs/adr/0010-one-distribution-one-dev-mode.md) deleted it: the
platform findings worth keeping belong on this page, and everything else was a dated
description of three config directories that every audit started by reading.

What belongs here is the **mechanism**: which scope suits which tenancy
([above](#before-you-start-which-config-directory-and-at-what-scope)), and the traps that make
a given choice the only workable one.

A dev install from a local-directory marketplace is scaffolding and belongs in neither.
