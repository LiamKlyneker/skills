# Estate inventory

Where every skill and plugin from this repo actually lives on this machine, and why.

Nothing derives this state and nothing validates it against an intent, so this file *is* the
intent — an entry missing here is a leftover, and a plugin missing there is a config that
quietly does not have the skill. Change the wiring, change this file in the same commit.

Rewritten at the close of PRD #52 (#61, the config cutover), **from the live directories**
rather than from memory. `doctor.sh` can confirm links resolve; only this file says whether
they are supposed to exist.

> **Confirmed by reading back:** `~/.claude`, this repo, and the symlink state of all three
> configs. **Not yet done:** `lk` and `install-skills` are *not installed* under
> `~/.claude-teamsnap` or `~/.claude-schmiede` — see [The open gap](#the-open-gap). That is a
> known, deliberate deferral, not an omission from this record.

---

## The two routes, and which one applies

- **Plugin** — installed from the `liamklyneker` marketplace into a config's cache, or
  linked as a *skills-dir plugin*. Components are **namespaced**: `prd-workflow:to-prd`,
  `subagent_type: prd-workflow:prd-worker`.
- **Skills-dir plugin** — one symlink to a whole *plugin* directory under a config's
  `skills/`. Still namespaced, still ships agents, but nothing is copied, so edits are live
  on the next session launch. This is the live-authoring route, and this repo uses it twice.

The old **plain-skill** route — one symlink per bare, un-namespaced skill — is **gone from
this repo's estate**. One link survives, and it points at a plugin's skill directory rather
than a top-level skill; see [Schmiede](#schmiede-plugin-for-the-spec-workflow-symlink-for-figma-to-spec).

Full mechanics: [`../INSTALL.md`](../INSTALL.md).

---

## Plugins

| Plugin | Config | Scope | Version | Enabled where |
|---|---|---|---|---|
| `prd-workflow@liamklyneker` | `~/.claude` | project ×3 | `81af34d0d5e1` | `liamklyneker`, `neonplace`, `neonplace-ios` — each via committed `.claude/settings.json`. **All three currently `✘ disabled`** |
| `prd-workflow@liamklyneker` | `~/.claude-teamsnap` | local | `6ac8dfa62316` | `organization-frontend-v2/.claude/settings.local.json` (gitignored — zero git footprint in a client repo) |
| `prd-workflow` (skills-dir) | this repo | project | `1.0.0` | `.claude/skills/prd-workflow -> ../../plugins/prd-workflow` |
| **`lk` (skills-dir)** | this repo | project | `1.0.0` | `.claude/skills/lk -> ../../plugins/lk` — **new in #61** |
| `figma-tools@liamklyneker` | `~/.claude` | user | `1.0.0` | everywhere under the personal config |
| `ado-workflow@liamklyneker` | `~/.claude-schmiede` | user | `6ac8dfa62316` | every Schmiede repo — user scope is the only one available there, see Schmiede below |

**Marketplace `liamklyneker` is registered in all three configs.** The `liamklyneker-dev`
marketplace — a local-directory source used to author PRD #52 — was **removed in #61**, along
with the two plugins installed from it.

A registered marketplace caches its catalog, so `/plugin marketplace update liamklyneker` is
required after the catalog changes upstream. Registering early buys one command instead of
two, not zero. This bit PRD #31 under Schmiede, and it bit #61 again: `~/.claude`'s cached
catalog listed three plugins until refreshed, and `lk` could not be found before that.

`prd-workflow` is enabled per project rather than at user scope on purpose: `prd-worker`
commits, so it must not be spawnable from a repo that never opted in. `creative-ghost/reeckon`
is the standing negative control — the plugin is visible to the CLI as `✘ disabled` there,
and the agent type must not resolve in a session.

### Versions, and the five installs still on a commit SHA

All five plugins now carry `version: 1.0.0` in both `plugin.json` and the marketplace catalog
(#57), and CI fails a plugin change that does not bump it (#58). **`version` is the install
cache key**, so the cache directory name moved from a commit SHA to a version string.

Three installs still sit on the old SHA key, and this is **deliberate, not leftover**:

| Install | Key | Why it was left |
|---|---|---|
| `prd-workflow@liamklyneker` ×3 under `~/.claude` | `81af34d0d5e1` | Three *other* repos. Updating changes what they load; out of scope for #61 |
| `prd-workflow@liamklyneker` under `~/.claude-teamsnap` | `6ac8dfa62316` | Client config, CLI cannot reach it |
| `ado-workflow@liamklyneker` under `~/.claude-schmiede` | `6ac8dfa62316` | Same |

Consequence: `~/.claude/plugins/cache/liamklyneker/prd-workflow/81af34d0d5e1` **cannot be
cleaned** while those three project installs reference it. Every other stale SHA directory was
removed in #61 (`figma-tools/81af34d0d5e1`, `figma-tools/ac7a89ab018a`,
`prd-workflow/ac7a89ab018a`, and the whole `liamklyneker-dev` tree) — `liamklyneker` went from
744K to 280K. Update those installs whenever it next suits, then delete the directory.

### Token cost of the current inventory

`claude plugin details`, measured at the close of #61:

```
prd-workflow — Skills (5), Agents (1)      always-on ~694 tok
  work-on-issue    ~130 / ~1.2k     to-issues       ~100 / ~3.9k
  to-prd            ~60 / ~2.7k     work-on-prd     ~130 / ~3.6k
  next-prd-issue   ~130 / ~1.6k     prd-worker      ~150 / ~1.6k

lk           — Skills (7), Agents (0)      always-on ~752 tok
  pinpoint          ~90 / ~790      qa-prd-log      ~110 / ~2.2k
  grill             ~70 / ~360      scoped-context   ~50 / ~190
  how-i-write      ~170 / ~4.4k     deep-grill       ~90 / ~4k
  triage-prd       ~160 / ~4.1k

figma-tools  — Skills (1), Agents (1)      always-on ~284 tok
  figma-to-spec    ~130 / ~2.9k     figma-region-extractor  ~150 / ~3.9k
```

(always-on / on-invoke per component. Always-on is paid every session in a config where the
plugin is enabled; on-invoke each time the component fires.)

**In this repo** all three are active — `lk` and `prd-workflow` via skills-dir, `figma-tools`
at user scope — for a combined always-on of **~1,730 tok** per session. Elsewhere under
`~/.claude` only `figma-tools` is enabled: **~284 tok**.

`lk` is the single most expensive always-on item in the estate, and it earns re-reading
occasionally: 7 skills, no agents, and `how-i-write` alone is ~170 always-on. Packaging seven
plain skills into one plugin changed *when* that cost is paid — a plain skill was paid per
config that linked it, a plugin is paid in every session where it is enabled.

**Two plugins are not measured here.** `ado-workflow` (4 skills, 1 agent) and `install-skills`
(1 skill) both sit outside `~/.claude` or are uninstalled, and `claude plugin details` only
ever reads `~/.claude`. Expect `ado-workflow` in `prd-workflow`'s range; that is an estimate
and is not written down as fact.

---

## The open gap

`lk` and `install-skills` are **installed in neither `~/.claude-teamsnap` nor
`~/.claude-schmiede`**, and their plain-skill symlinks were removed in #61. So both configs
have lost, and have not regained:

| Config | Lost | Was |
|---|---|---|
| `~/.claude-teamsnap` | `deep-grill`, `how-i-write`, `pinpoint` | now in `lk` |
| `~/.claude-schmiede` | `deep-grill`, `how-i-write`, `pinpoint`, `install-skills` | `lk` + its own plugin |

**Nothing was actually lost in the removal.** All fifteen links were already dangling before
#61 touched them: a plain-skill symlink points at a *working-tree path*, and PRD #52 moved
those directories into `plugins/`, which broke every link the instant the move happened — no
merge and no install involved. Removing a dead link loses nothing; these configs had already
lost the skills.

The fix is one `/plugin marketplace update liamklyneker` followed by two installs, typed
**inside a session under that config** — the `claude plugin` CLI ignores `CLAUDE_CONFIG_DIR`
and only ever reads `~/.claude`. Scopes: `~/.claude-teamsnap` → **local** (project scope would
write a committed `.claude/settings.json` into an employer's repo); `~/.claude-schmiede` →
**user**, the only scope available there.

Deferred on purpose rather than forgotten. Do it when a missing skill is actually felt.

---

## Symlinks, per config

| Link | Config | Target | Why it exists |
|---|---|---|---|
| `lk` | this repo | `../../plugins/lk` | Live authoring of the `lk` plugin |
| `prd-workflow` | this repo | `../../plugins/prd-workflow` | Live authoring of the `prd-workflow` plugin |
| `figma-to-spec` | `~/.claude-schmiede` | `…/plugins/figma-tools/skills/figma-to-spec` | The last hand-linked *skill*; see Schmiede below |
| `_shared` | `~/.claude-schmiede` | `~/schmiede-one/agent-skills/skills/_shared` | **Another repo's** shared reference, not ours |

That is the whole list. `~/.claude` and `~/.claude-teamsnap` now hold **no symlinks from this
repo at all**.

**A skills-dir plugin link must never coexist with an install of the same plugin in the same
place** — every skill would load twice. This repo therefore has no installed `lk@liamklyneker`
or `prd-workflow@liamklyneker`; both come from the links above, and `claude plugin list`
reports them as `lk@skills-dir` and `prd-workflow@skills-dir`.

`~/.claude` also holds skills from elsewhere (`apple-design`, `ios-accessibility`,
`swift-concurrency`, `swift-testing-pro`, `swiftui-pro`), all out of this repo's scope.

### What happened to the fifteen plain skills

Seven — `deep-grill`, `grill` (renamed from `grill-me`), `how-i-write`, `pinpoint`,
`qa-prd-log`, `scoped-context`, `triage-prd` — became skills of the **`lk` plugin** (#62).
`install-skills` became **its own plugin** (#53), deliberately separate, because it is the one
thing a stranger needs and reaching it must not require installing a personal bundle.

`deep-grill` used to be documented here as *deliberately* a plain skill: in the `prd-workflow`
**bundle** but not the **plugin**, on the grounds that it is recon and useful without the PRD
loop. That reasoning was not wrong — it argued against folding it into a *workflow* plugin,
and #62 did not do that. It went into a personal plugin instead, with the grills decoupled
from the workflow plugins entirely (#55). See [ADR 0002](adr/0002-the-lk-plugin.md).

`~/.claude-schmiede` **used to** hold Schmiede's own `to-spec`, `to-spec-tasks` and
`next-task-to-implement` as symlinks into `~/schmiede-one/agent-skills/skills/`. Those three
links went in PRD #31 — the `ado-workflow` plugin provides all three, and running both routes
loaded each skill twice. The link targets still exist in `agent-skills`; only the links were
removed.

---

## Schmiede: plugin for the spec workflow, symlink for `figma-to-spec`

Schmiede ran symlink-only until PRD #31. It no longer does — the spec workflow arrives as an
installed plugin, and only `figma-to-spec` is still hand-linked. The two routes coexist here
for different plugins, which is fine; what is never fine is both routes for the *same* one.

**`ado-workflow@liamklyneker` is installed at user scope.** User scope is not a preference, it
is the only option: the `claude plugin` CLI ignores `CLAUDE_CONFIG_DIR` and always targets
`~/.claude`, and Schmiede repos refuse project and local scope outright
(`SymlinkWriteRefusedError` — their `.claude` is itself a symlink). So the install must come
from an **in-session `/plugin install`** in a Schmiede repo, and it lands config-wide. The same
constraint is why `lk` and `install-skills` are still missing here (see the open gap above).

**Installing the plugin is only half of it.** Every `ado-workflow` skill reads
`<repo-root>/.claude/project/adapter.md`, and no install creates one — which is what
`install-skills` is for. Its symlink here was dangling and has been removed; **until the plugin
is installed, this config cannot bootstrap a new repo's adapter.** Already-bootstrapped repos
are unaffected. `~/schmiede-one/products` is the first repo bootstrapped; its adapter is
excluded through that clone's `.git/info/exclude`, so it is machine-local and any other clone
will read as `HOLE`.

**What the plugin route buys that the symlink route could not: the agent.** `spec-worker` ships
inside `ado-workflow`, so `ado-workflow:spec-worker` resolves in a Schmiede session — confirmed
by reading the type back in a fresh one, not inferred from a run. On the old route there was no
agent at all.

### `figma-to-spec` stays hand-linked

`~/.claude-schmiede/skills/figma-to-spec` points **straight at**
`plugins/figma-tools/skills/figma-to-spec`. It survived #61's sweep for exactly that reason —
it already pointed inside `plugins/`, so PRD #52's moves never broke it, while all fifteen
top-level links died.

It is still a symlink for the same reason it always was — `figma-tools` is a *different*
plugin, not installed here, and Schmiede actively uses `figma-to-spec` alongside the spec
workflow, so dropping the link is a real loss.

**Consequence to know:** on this route the skill loads unprefixed as `figma-to-spec`, and
Schmiede gets **no `figma-region-extractor` agent** (agents ship with plugins, not with skill
symlinks). Phase B therefore takes the documented inline fallback there — `general-purpose`
with the agent file's body pasted in. That is a supported path, not a defect, and it is why
`figma-to-spec` names both the namespaced and bare type names before falling back. Installing
`figma-tools` here would fix it and is a separate decision; if it is ever done, delete this
symlink in the same pass.

`~/.claude-schmiede/skills/_shared` is **another repo's** shared reference
(`ado-workitem-authoring.md`, `spec-splitting-seams.md`), not this one's. Confirmed resolving,
confirmed intended. It is not the banned project-owned `_shared/` shape, because it belongs to
a *skills* repo, and no skill of ours resolves `../_shared/` through it.

---

## Agents

All three ship inside their plugin, so they arrive and depart with it. **No hand-placed agent
symlinks remain anywhere** — `~/.claude/agents/` holds only `Explore.md` and
`web-researcher.md`, neither from this repo; `~/.claude-teamsnap` and `~/.claude-schmiede`
have no `agents/` directory at all.

| Agent | Type name | Provided by |
|---|---|---|
| `prd-worker` | `prd-workflow:prd-worker` | `prd-workflow` |
| `figma-region-extractor` | `figma-tools:figma-region-extractor` | `figma-tools` |
| `spec-worker` | `ado-workflow:spec-worker` | `ado-workflow` |

`lk` and `install-skills` ship **no agents** — the first plugins here that do not.

**The namespace is not optional.** `subagent_type: prd-worker` does not resolve from a plugin
install, and an unresolvable type does not error — it falls through to `general-purpose`. Both
skills are written to fall back deliberately, so the broken case and the working case produce
identical output. Verify by listing agent types in a fresh session; a successful run proves
nothing.

Project-owned agents that are **not** ours and must survive:
`neonplace-ios/.agents/agents/{grill-explorer,grill-web-explorer}.md`.
Project-owned skills likewise: `neonplace/.agents/skills/{building-luar-ui,
data-types-colocation,triage,verify-ui}`.

---

## Checking it

```bash
bash plugins/install-skills/skills/install-skills/scripts/doctor.sh --repo <path>   # per repo
claude plugin list                                    # ~/.claude only — the CLI ignores CLAUDE_CONFIG_DIR
find ~/.claude ~/.claude-teamsnap ~/.claude-schmiede -type l ! -exec test -e {} \; -print
```

The last one must print nothing — **it does, as of #61.** The other two configs are inspected
by reading their `settings.json`, `plugins/installed_plugins.json` and `plugins/cache/`
directly; the CLI cannot reach them.

**Known `doctor` defects** (reported, not fixed, each wants its own issue):

- It reports a **dangling** symlink as a double-load, matching the link's *name* against what
  the plugins provide without checking that the link resolves. Currently unreachable — there
  are no dangling links left — but the next stale link resurrects it.
- Run against a repo whose plugin comes from the personal config, it may report reachability
  at `~/.claude-teamsnap/plugins/cache/...`, because it scans all three configs and names the
  first match. Misleading output, not a false clean.
- `$canonical` now resolves to `plugins/install-skills/skills` rather than the repo root, so
  the `FORK` check at `doctor.sh:344` means something narrower than it reads. Nothing goes
  unreported — the `plugin_provides` branch still catches shadowing — but `--help` still
  describes `--canonical` as "path to the canonical skills repo", which is no longer literally
  true.
