# Estate inventory

Where every skill and plugin from this repo actually lives on this machine, and why.

Plain skills are placed **by hand**, one symlink at a time, into a config directory's
`skills/`. Nothing derives this state and nothing validates it against an intent, so this
file *is* the intent — an entry missing here is a leftover, and a link missing there is a
config that quietly does not have the skill. Change the wiring, change this file in the
same commit.

Recorded at the close of PRD #16 (the plugin migration), from the live directories rather
than from memory. `doctor.sh` can confirm the links resolve; only this file says whether
they are supposed to exist.

---

## The two routes, and which one applies

- **Plugin** — installed from the `liamklyneker` marketplace into a config's cache, or
  linked as a *skills-dir plugin*. Components are **namespaced**: `prd-workflow:to-prd`,
  `subagent_type: prd-workflow:prd-worker`.
- **Plain skill** — one symlink per skill into a config's `skills/`. No namespace, no
  agents, no bundling. This is the only route for anything not in a plugin.

Full mechanics: [`../INSTALL.md`](../INSTALL.md).

---

## Plugins

| Plugin | Config | Install scope | Enabled where |
|---|---|---|---|
| `prd-workflow@liamklyneker` | `~/.claude` | project ×3 | `liamklyneker`, `neonplace`, `neonplace-ios` — each via committed `.claude/settings.json` |
| `prd-workflow@liamklyneker` | `~/.claude-teamsnap` | local | `organization-frontend-v2/.claude/settings.local.json` (gitignored — zero git footprint in a client repo) |
| `prd-workflow` (skills-dir) | this repo | project | `.claude/skills/prd-workflow -> ../../plugins/prd-workflow` — live authoring, edits take effect next session |
| `figma-tools@liamklyneker` | `~/.claude` | user | everywhere under the personal config |
| `ado-workflow@liamklyneker` | `~/.claude-schmiede` | **user** | every Schmiede repo — user scope is the only one available there, see Schmiede below |

**Marketplace `liamklyneker` is registered in all three configs**, and all three now install
from it. `~/.claude-schmiede` was the last holdout; PRD #31 closed that gap.

A registered marketplace caches its catalog. `~/.claude-schmiede` had `liamklyneker` registered
since before `ado-workflow` existed, so its cached catalog listed only `prd-workflow` and
`figma-tools` and the install failed to find the plugin until
`/plugin marketplace update liamklyneker` was run first. Registering early buys you one command
instead of two, not zero — the refresh is not optional after the catalog changes upstream.

`prd-workflow` is enabled per project rather than at user scope on purpose: `prd-worker`
commits, so it must not be spawnable from a repo that never opted in. `creative-ghost/reeckon`
is the standing negative control — the plugin is visible to the CLI as `✘ disabled` there,
and the agent type must not resolve in a session.

### Token cost of the current inventory

`claude plugin details`, run at the close of #26:

```
prd-workflow — Skills (5), Agents (1)      always-on ~694 tok
  work-on-issue    ~130 / ~1.2k     to-issues       ~100 / ~3.9k
  to-prd            ~60 / ~2.7k     work-on-prd     ~130 / ~3.6k
  next-prd-issue   ~130 / ~1.6k     prd-worker      ~150 / ~1.6k

figma-tools  — Skills (1), Agents (1)      always-on ~284 tok
  figma-to-spec    ~130 / ~2.9k     figma-region-extractor  ~150 / ~3.9k
```

(always-on / on-invoke per component. Always-on is paid every session in a config where the
plugin is enabled; on-invoke each time the component fires.)

Combined always-on is **~978 tok** in the personal config with both enabled, ~694 in a
consumer repo with only `prd-workflow`. That is the number to weigh before promoting another
plain skill into a plugin — a plugin's always-on cost lands on every session in scope,
including the ones that never use it.

**`ado-workflow` is not measured here.** It carries 4 skills and 1 agent, so expect a figure in
`prd-workflow`'s range, but that is an estimate and is not written down as fact. Measuring it
needs `claude plugin details`, which only ever reads `~/.claude` — and `ado-workflow` is
installed under `~/.claude-schmiede`, where the CLI cannot reach. Every Schmiede session now
pays that cost at user scope; quantify it before enabling anything else there.

---

## Plain skills, per config

Every one of these is a symlink into `/Users/klyneker/liam-klyneker/skills/<name>`.

| Skill | `~/.claude` | `~/.claude-teamsnap` | `~/.claude-schmiede` | Why |
|---|:--:|:--:|:--:|---|
| `deep-grill` | ✔ | ✔ | ✔ | **Deliberately not in the `prd-workflow` plugin** — see below |
| `how-i-write` | ✔ | ✔ | ✔ | Personal voice; useful in every context |
| `pinpoint` | ✔ | ✔ | ✔ | Generic recon; cheap and context-free |
| `grill-me` | ✔ | — | — | Personal-project ideation |
| `scoped-context` | ✔ | — | — | Enforces this repo's `CONTEXT.md` convention; not a client convention |
| `qa-prd-log` | ✔ | — | — | Half of the PRD QA loop, which only runs in personal repos |
| `triage-prd` | ✔ | — | — | Other half of the same loop |
| `install-skills` | ✔ | — | ✔ | Bootstraps a project's adapter. Linked under Schmiede once `ado-workflow` landed there — a bundle with no adapter is skills that cannot run. TeamSnap still has nothing to wire |
| `figma-to-spec` | — | — | ✔ | Plugin-provided under `~/.claude`; symlinked under Schmiede — see below |

Not linked into any config, and correct: `figma-component/`, `tokens-init/` — both
deprecated, awaiting #17.

`~/.claude` also holds skills from elsewhere (`apple-design`, `ios-accessibility`,
`swift-concurrency`, `swift-testing-pro`, `swiftui-pro`), all out of this repo's scope.

`~/.claude-schmiede` **used to** hold Schmiede's own `to-spec`, `to-spec-tasks` and
`next-task-to-implement` as symlinks into `~/schmiede-one/agent-skills/skills/`. Those three
links are **gone** — the `ado-workflow` plugin now provides all three, and running both routes
loaded each skill twice. The link targets still exist in `agent-skills`; only the links into
this config were removed. Its own `_shared` symlink stays (see Schmiede below).

### `deep-grill` is a plain skill, on purpose

It is in the `prd-workflow` **bundle** (`install/bundles.md`) but deliberately **not** in the
`prd-workflow` **plugin**. Those are different things and the overlap is exactly what makes it
easy to misread: its three config links look like migration leftovers and are not. `deep-grill`
is recon, useful on its own without the PRD loop, so it stays independently linkable.

Promoting it — or any other plain skill — into a plugin is a **separate, one-at-a-time
decision**, explicitly out of scope for PRD #16.

**Superseded by PRD #52, in progress.** `deep-grill` is now a skill of the `lk` plugin
(`plugins/lk/skills/deep-grill`), along with `grill` (renamed from `grill-me`),
`how-i-write`, `pinpoint`, `qa-prd-log`, `scoped-context` and `triage-prd`. This repo's own
`.claude/skills/deep-grill -> ../../deep-grill` link died with the move and was removed in
the same commit; it is replaced by `.claude/skills/lk -> ../../plugins/lk` in #61, which
also retires the config-level links to all seven. **Until #61 lands, every row below for
those seven names is dangling on this branch** — a broken link in a config's `skills/` means
the skill silently does not load, and checking out `main` restores it. That is the cutover
window the PRD names, not a defect.

---

## Schmiede: plugin for the spec workflow, symlink for `figma-to-spec`

Schmiede ran symlink-only until PRD #31. It no longer does — the spec workflow arrives as an
installed plugin, and only `figma-to-spec` is still hand-linked. The two routes now coexist
here for different plugins, which is fine; what is never fine is both routes for the *same*
one.

**`ado-workflow@liamklyneker` is installed at user scope.** User scope is not a preference, it
is the only option: the `claude plugin` CLI ignores `CLAUDE_CONFIG_DIR` and always targets
`~/.claude`, and Schmiede repos refuse project and local scope outright
(`SymlinkWriteRefusedError` — their `.claude` is itself a symlink). So the install must come
from an **in-session `/plugin install`** in a Schmiede repo, and it lands config-wide.

The three legacy symlinks — `to-spec`, `to-spec-tasks`, `next-task-to-implement`, all pointing
into `~/schmiede-one/agent-skills/skills/` — were **removed in the same pass**. With the plugin
installed and the links still present, a live session listed each skill twice, once bare and
once as `ado-workflow:*`, and `doctor` named all three. After removal it names none while still
reporting what it walked. Only the links went; the directories in `agent-skills` are untouched,
and deleting them is that repo's decision, not this one's.

**Installing the plugin is only half of it.** Every `ado-workflow` skill reads
`<repo-root>/.claude/project/adapter.md`, and no install creates one — so `install-skills` is
now linked into this config too. Without it the skills are present and unusable, which is the
one failure mode that looks like a successful install. `~/schmiede-one/products` is the first
repo bootstrapped; its adapter is excluded through that clone's `.git/info/exclude`, so it is
machine-local and any other clone will read as `HOLE`.

**What the plugin route buys that the symlink route could not: the agent.** `spec-worker` ships
inside `ado-workflow`, so `ado-workflow:spec-worker` now resolves in a Schmiede session —
confirmed by reading the type back in a fresh one, not inferred from a run. On the old route
there was no agent at all.

### `figma-to-spec` stays hand-linked

`~/.claude-schmiede/skills/figma-to-spec` points **straight at**
`plugins/figma-tools/skills/figma-to-spec`. Before #26 it went through the top-level compat
shim, which resolved to the same directory via one extra hop; deleting the shim without this
repoint would have left a dangling link in a client config, silently and with no error.

It is still a symlink for the same reason it always was — `figma-tools` is a *different*
plugin, not installed here, and Schmiede actively uses `figma-to-spec` alongside the spec
workflow, so dropping the link is a real loss. Nothing about installing `ado-workflow` changes
that; they provide disjoint skills, so there is no double-load between them.

**Consequence to know:** on this route the skill loads unprefixed as `figma-to-spec`, and
Schmiede gets **no `figma-region-extractor` agent** (agents ship with plugins, not with skill
symlinks). Phase B therefore takes the documented inline fallback there — `general-purpose`
with the agent file's body pasted in. That is a supported path, not a defect, and it is why
`figma-to-spec` names both the namespaced and bare type names before falling back. Installing
`figma-tools` here would fix it and is a separate decision; if it is ever done, delete this
symlink in the same pass, exactly as the three above were.

`~/.claude-schmiede/skills/_shared -> ~/schmiede-one/agent-skills/skills/_shared` is **another
repo's** shared reference (`ado-workitem-authoring.md`, `spec-splitting-seams.md`), not this
one's. Confirmed resolving, confirmed intended. It is not the banned project-owned `_shared/`
shape, because it belongs to a *skills* repo, and no skill of ours resolves `../_shared/`
through it.

---

## Agents

All three ship inside their plugin, so they arrive and depart with it. **No hand-placed agent
symlinks remain anywhere** — `~/.claude/agents/` holds only `Explore.md` and
`web-researcher.md`, neither from this repo; `~/.claude-teamsnap` and `~/.claude-schmiede`
have no `agents/` directory at all. `spec-worker` reaches Schmiede purely as plugin cargo,
which is the whole reason that config stopped being symlink-only.

| Agent | Type name | Provided by |
|---|---|---|
| `prd-worker` | `prd-workflow:prd-worker` | `prd-workflow` |
| `figma-region-extractor` | `figma-tools:figma-region-extractor` | `figma-tools` |
| `spec-worker` | `ado-workflow:spec-worker` | `ado-workflow` |

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
bash install-skills/scripts/doctor.sh --repo <path>   # per repo
claude plugin list                                    # ~/.claude only — the CLI ignores CLAUDE_CONFIG_DIR
find ~/.claude ~/.claude-teamsnap ~/.claude-schmiede -type l ! -exec test -e {} \; -print
```

The last one must print nothing. The other two configs are inspected by reading their
`settings.json`, `plugins/installed_plugins.json` and `plugins/cache/` directly — the CLI
cannot reach them.

**Known cosmetic bug in `doctor`** (reported, not fixed, needs its own issue): run against a
repo whose plugin comes from the personal config it may report reachability at
`~/.claude-teamsnap/plugins/cache/...`, because it scans all three configs and names the first
match. Misleading output, not a false clean.
