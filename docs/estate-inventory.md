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

**Marketplace `liamklyneker` is registered in all three configs.** `~/.claude-schmiede` has
it registered with **nothing installed** — deliberate, not an oversight. It is the leftover
of an install attempt that could not complete (see Schmiede below), and it makes a future
install one command instead of two.

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
| `install-skills` | ✔ | — | — | Wires *this* repo's bundles into a project; nothing to wire at a client |
| `figma-to-spec` | — | — | ✔ | Plugin-provided under `~/.claude`; symlinked under Schmiede — see below |

Not linked into any config, and correct: `figma-component/`, `tokens-init/` — both
deprecated, awaiting #17.

`~/.claude` also holds skills from elsewhere (`apple-design`, `ios-accessibility`,
`swift-concurrency`, `swift-testing-pro`, `swiftui-pro`) and `~/.claude-schmiede` holds
Schmiede's own (`to-spec`, `to-spec-tasks`, `next-task-to-implement`, and its own `_shared`),
all out of this repo's scope.

### `deep-grill` is a plain skill, on purpose

It is in the `prd-workflow` **bundle** (`install/bundles.md`) but deliberately **not** in the
`prd-workflow` **plugin**. Those are different things and the overlap is exactly what makes it
easy to misread: its three config links look like migration leftovers and are not. `deep-grill`
is recon, useful on its own without the PRD loop, so it stays independently linkable — which
is also why it keeps its own symlink in *this* repo's `.claude/skills/`.

Promoting it — or any other plain skill — into a plugin is a **separate, one-at-a-time
decision**, explicitly out of scope for PRD #16.

---

## Schmiede: stays on the symlink route

`~/.claude-schmiede/skills/figma-to-spec` now points **straight at**
`plugins/figma-tools/skills/figma-to-spec`. Before #26 it pointed at the top-level
`figma-to-spec` compat shim, which resolved to the same directory via one extra hop; deleting
the shim without this repoint would have left a dangling link in a client config, silently and
with no error.

Repointing was chosen over installing the plugin because **installing is not currently
possible**: the `claude plugin` CLI ignores `CLAUDE_CONFIG_DIR` and always targets `~/.claude`,
and Schmiede repos refuse project and local scope outright (`SymlinkWriteRefusedError` — their
`.claude` is itself a symlink), leaving only an in-session user-scope `/plugin install`. It was
also chosen over deleting the link: Schmiede actively uses `figma-to-spec` alongside its own
`to-spec` workflow, so dropping it is a real loss.

`readlink -f` returns the identical path before and after, so this is a zero-behaviour-change
edit — it removes a hop, nothing else.

**Consequence to know:** on this route the skill loads unprefixed as `figma-to-spec`, and
Schmiede gets **no `figma-region-extractor` agent** (agents ship with plugins, not with skill
symlinks). Phase B therefore takes the documented inline fallback there — `general-purpose`
with the agent file's body pasted in. That is a supported path, not a defect, and it is why
`figma-to-spec` names both the namespaced and bare type names before falling back.

If a user-scope install into `~/.claude-schmiede` is ever done from an interactive session,
delete this symlink at the same time — running both routes for one skill loads it twice.

`~/.claude-schmiede/skills/_shared -> ~/schmiede-one/agent-skills/skills/_shared` is **another
repo's** shared reference (`ado-workitem-authoring.md`, `spec-splitting-seams.md`), not this
one's. Confirmed resolving, confirmed intended. It is not the banned project-owned `_shared/`
shape, because it belongs to a *skills* repo, and no skill of ours resolves `../_shared/`
through it.

---

## Agents

Both ship inside their plugin, so they arrive and depart with it. **No hand-placed agent
symlinks remain anywhere** — `~/.claude/agents/` holds only `Explore.md` and
`web-researcher.md`, neither from this repo; `~/.claude-teamsnap` and `~/.claude-schmiede`
have no `agents/` directory at all.

| Agent | Type name | Provided by |
|---|---|---|
| `prd-worker` | `prd-workflow:prd-worker` | `prd-workflow` |
| `figma-region-extractor` | `figma-tools:figma-region-extractor` | `figma-tools` |

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
