# Agent Skills

A collection of my agent skills... more to come soon!

## Layout

This repo is a **plugin marketplace**. Everything it publishes lives inside a plugin;
five top-level directories carry all of it:

| Directory | What's in it |
|---|---|
| `.claude-plugin/` | `marketplace.json` — the catalog, published as marketplace **`liamklyneker`** |
| `plugins/` | The five packaged plugins: `prd-workflow/`, `figma-tools/`, `ado-workflow/` (the PRD workflow's ADO counterpart), `lk/` (the personal skills) and `install-skills/` (the bootstrapper, its own plugin so reaching it needs nothing else). Their skills live one level down, in `<plugin>/skills/` |
| `_shared/` | **Global reference** — nine docs several skills read that are true in every project, from the eligibility rules to the shape of a QA item. No templates, no project values. Each plugin reaches this one canonical copy through a `skills/_shared` symlink |
| `install/` | **Templates a project fills in** — `adapter.template.md`, `bundles.md` and `gates/`, plus the layout guide. Also the directory the `install-skills` plugin symlinks in as `skills/install`, which is what keeps its packaged skill reading these files at an unchanged relative path |
| `docs/` | The [decision records](docs/adr/README.md), and nothing else. Documentation for humans — no session loads it |

**There are no plain skills left in this repo.** That is a change of shape, not a detail:
every skill arrives by installing and enabling its plugin, and every one of them invokes
under that plugin's namespace. Nothing resolves through a pre-plugin path any more — the
migration's compat shims (top-level symlinks into `plugins/`) are gone, and so are the
links that used to make this repo load its own plugins live.

**This repo does not track who has installed it.** It publishes a versioned catalog and its
job ends there — a coherent marketplace, and a `version` that moves whenever a plugin's
content does, because a missed bump strands a consumer silently. Whether any given machine
has the plugin, at which version, is that machine's business; a stale install is an ordinary
bug, fixed where it surfaces. [ADR 0007](docs/adr/0007-a-marketplace-not-an-estate-manager.md)
has the argument.

**One delivery route, and one dev mode.** A skill reaches a machine as a plugin installed
from the marketplace — a copy in the config's cache, keyed by the plugin's `version` — and
there is no second way. Authoring is separate and session-scoped: `claude --plugin-dir
plugins/<name>` loads a plugin straight from a working tree, on any branch, copying
nothing. The two are not alternatives; ADR
[0010](docs/adr/0010-one-distribution-one-dev-mode.md) says why that distinction is worth
stating. Full instructions, including which config directory and which scope:
[`INSTALL.md`](INSTALL.md).

A project never owns a `_shared/`, so `../_shared/…` from any skill can only mean this
repo. Anything project-specific lives in `<repo-root>/.claude/project/`: `adapter.md`
plus any gates it registers, and packaging does not change that — skills resolve the
adapter from the project the session is running in, so it works the same from a plugin
cache. Layout: [`install/README.md`](install/README.md).

## Adopting a bundle

Getting the skills is the platform's job — `/plugin marketplace add LiamKlyneker/skills`
then `/plugin install <plugin>@liamklyneker`. To edit a plugin in place instead of
installing it, use `claude --plugin-dir <path>`. [`INSTALL.md`](INSTALL.md) walks both and
the traps in each.

What no distribution mechanism can do is fill in *your project's* facts. From the repo you
want to wire up:

```
/install-skills:install-skills install prd-workflow
```

The name is doubled because the `install-skills` skill ships inside the `install-skills`
plugin, and a plugin namespaces everything it provides. It copies the adapter template,
interviews you only for the facts your repo doesn't already state, offers any gate the
bundle declares, and ends with a clean bill of health — or tells you exactly what it
couldn't finish.

| Bundle | What it wires up |
|---|---|
| `prd-workflow` | The PRD → issues → implementation loop — five of the six skills the `prd-workflow` plugin ships |
| `ado-workflow` | The same loop against an Azure DevOps board — `[SPEC]` → `[TASK]`s → implementation, exactly the four skills the `ado-workflow` plugin ships |
| `prd-qa` | The QA loop run against a PRD branch before merge — `triage-prd`, the sixth skill the `prd-workflow` plugin ships |
| `grill` | The interviews that run *before* either loop — `grill` inline on one thread, `deep-grill` with recon subagents and hard gates. Two more `lk` skills; only `deep-grill` reads the adapter, so `## Sources of truth` is the whole of this bundle's interview |
| `figma-tools` | Figma → spec — the `figma-tools` plugin. Adapter-free |

Definitions live in [`install/bundles.md`](install/bundles.md); a bundle names the adapter
sections a set of skills needs filled, not the skills themselves. Bundle and plugin are
separate namespaces and only sometimes the same set — `prd-workflow` alone maps to **two**
bundles, `prd-workflow` and `prd-qa`, so even a plugin that shares a bundle's name is not
that bundle.

`/install-skills:install-skills doctor` is the other half, and the more important one.
Forked copies, leftover `_shared/` directories, half-filled adapters and dead gate
pointers all fail **silently** — that's how one project ends up with five drifted skills
nobody notices until they're diffed by hand. Doctor makes each of those a line of output.
Run it in any repo, any time; it changes nothing.

## Agents

Some skills ship a custom subagent alongside `SKILL.md` + `references/`. The agent file
carries the parts of the contract that never change between calls, so the orchestrator only
passes the per-call inputs. Each agent ships **inside its plugin**, in `<plugin>/agents/`,
so it arrives and departs with the plugin — no separate agent link to place or forget.

| Agent (type name) | Skill | Reach | Notes |
|---|---|---|---|
| `figma-tools:figma-region-extractor` | `figma-to-spec` (Phase B) | wherever `figma-tools` is enabled — user scope, personal config | Pinned to Sonnet; write tools denied. Detachable — if not installed, Phase B reads the same file and pastes its body into a `general-purpose` agent. |
| `prd-workflow:prd-worker` | `work-on-prd` (Loop step 5) | **only where `prd-workflow` is enabled** | No `model`/`effort` — the orchestrator routes per issue and passes the tier at spawn time. `Agent` denied (flat hierarchy — costs it `Explore`, so it greps for itself). Contained on purpose: it commits, so a stray auto-spawn must not be possible from an unrelated repo. Detachable the same way. |

**The type name carries the plugin prefix.** A plugin namespaces its agents exactly as it
namespaces its skills, so `subagent_type: prd-worker` does *not* resolve from a plugin
install — it has to be `prd-workflow:prd-worker`. The bare name only exists on the
pre-plugin route, a hand-placed file in an `agents/` directory. Getting it wrong is
**silent**: an unresolvable type falls through to `general-purpose`, the run completes, and
nothing in the output says the contract was never loaded. That failure has now happened
twice here — once from a missing agent link, once from packaging renaming the type.

Containment is the plugin's `enabledPlugins` entry — a repo that never enabled
`prd-workflow` cannot spawn `prd-worker` at all. See
[`INSTALL.md`](INSTALL.md) for which scope to enable in which config.

Things worth knowing before adding another one:

- **A newly installed agent takes a few minutes to register**, and a newly *created* agents
  directory does not register at all mid-session. Dropping a file into an agents directory
  that already existed at session start resolves after a few minutes, no restart needed —
  that is how `figma-region-extractor` behaved. Creating `.claude/agents/` for the first time
  and symlinking into it left `prd-worker` unresolvable for the rest of the session (three
  attempts, ~15 min). So the fallback is not a nicety: any skill that spawns by type must
  check availability and paste the body into `general-purpose` instead. Shipping an agent
  inside a plugin sidesteps the placement problem — but not the delay, and not the fallback
  requirement, since a missing agent still degrades silently to `general-purpose`.
- **Agents have no `disable-model-invocation`.** A `description` that reads like a capability
  advertisement invites auto-delegation from unrelated sessions, bypassing the skill's setup
  phase. Write it as a caller contract ("internal to X, never invoke directly"), and where
  the agent depends on inputs only the orchestrator can supply, make it hard-STOP when they
  are missing.
- **The body replaces the system prompt, but not everything comes from there.** Measured
  with a throwaway probe agent: git conventions (including the `Co-Authored-By` trailer and
  the never-commit-unless-asked rule), the prefer-dedicated-file-tools guidance, `CLAUDE.md`,
  and the date/user context all still reach a custom subagent — they arrive via tool
  descriptions and injected context rather than the system prompt. What measurably does
  **not** survive is the honesty/evidence/don't-fabricate guidance. Restate that in any
  agent whose job is to report results; don't waste lines restating the rest.
- **Reaching the agent is not the same as being followed.** The probe measured which guidance
  still *arrives*; it did not measure compliance. A worker built on the strength of that
  measurement — trailer inherited, so not restated — then committed without the
  `Co-Authored-By` trailer, and did so even on the `general-purpose` fallback path where the
  whole system prompt was intact. If an inherited convention has to hold for the skill to be
  correct, restate it and assert on it; treat the probe as a list of what you *may* omit, not
  what you can rely on.
- **Only pin `model` / `effort` in frontmatter when the tier is a property of the *agent*.**
  `figma-region-extractor` always does grep-and-extract work, so Sonnet is pinned. A
  `prd-worker` handles anything from a copy tweak to a migration, and the orchestrator makes
  that call per issue at spawn time (`_shared/model-effort-heuristics.md`: the call is made at
  point-of-use, never frozen) — a frontmatter tier there is dead config that reads as
  authoritative.
