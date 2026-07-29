# Agent Skills

A collection of my agent skills... more to come soon!

## Layout

This repo is both a marketplace and a collection of plain skills. Four top-level
entries are not skills:

| Directory | What's in it |
|---|---|
| `.claude-plugin/` | `marketplace.json` — the catalog, published as marketplace **`liamklyneker`** |
| `plugins/` | The packaged plugins: `prd-workflow/`, `figma-tools/`, and `ado-workflow/` (the PRD workflow's ADO counterpart). Their skills live one level down, in `<plugin>/skills/` |
| `_shared/` | **Global reference** — docs several skills read that are true in every project. No templates, no project values. |
| `install/` | **Templates a project fills in** — `adapter.template.md` and `gates/`, plus the layout guide. |

Every *other* top-level directory is one plain skill — `deep-grill`, `grill-me`,
`install-skills`, `how-i-write`, `pinpoint`, `qa-prd-log`, `scoped-context`,
`triage-prd` — plus `figma-component/` and `tokens-init/`, both deprecated and linked
nowhere. The migration's compat shims (top-level symlinks into `plugins/`) are gone;
nothing resolves through a pre-plugin path any more.

Which config directory and which repo actually has each of these is recorded in
[`docs/estate-inventory.md`](docs/estate-inventory.md) — the plain skills are placed
by hand, one symlink at a time, so the inventory is the only place that state exists.

Two delivery routes, on purpose: a plugin from the marketplace (a versioned copy,
cache-keyed by git commit), or a symlink into a config's `skills/` directory (nothing
copied, edits live — how this repo authors against itself). Full instructions,
including which config directory and which scope: [`INSTALL.md`](INSTALL.md).

A project never owns a `_shared/`, so `../_shared/…` from any skill can only mean this
repo. Anything project-specific lives in `<repo-root>/.claude/project/`: `adapter.md`
plus any gates it registers, and packaging does not change that — skills resolve the
adapter from the project the session is running in, so it works the same from a plugin
cache. Layout: [`install/README.md`](install/README.md).

## Adopting a bundle

Getting the skills is the platform's job — `/plugin marketplace add LiamKlyneker/skills`
then `/plugin install <plugin>@liamklyneker`, or a symlink into a config's `skills/`
directory for a plain skill and for editing in place. [`INSTALL.md`](INSTALL.md) walks
both routes and the traps in each.

What no distribution mechanism can do is fill in *your project's* facts. From the repo you
want to wire up:

```
/install-skills install prd-workflow
```

It copies the adapter template, interviews you only for the facts your repo doesn't
already state, offers any gate the bundle declares, and ends with a clean bill of health —
or tells you exactly what it couldn't finish.

| Bundle | What it wires up |
|---|---|
| `prd-workflow` | The PRD → issues → implementation loop — the `prd-workflow` plugin, plus `deep-grill`, which stays a plain skill |
| `ado-workflow` | The same loop against an Azure DevOps board — `[SPEC]` → `[TASK]`s → implementation, from the `ado-workflow` plugin, plus `deep-grill` |
| `prd-qa` | The QA loop run against a PRD branch before merge — two plain skills, no plugin |
| `figma-tools` | Figma → spec — the `figma-tools` plugin. Adapter-free |

Definitions live in [`install/bundles.md`](install/bundles.md); a bundle names the adapter
sections a set of skills needs filled, not the skills themselves. Bundle and plugin are
separate namespaces and only sometimes the same set.

`/install-skills doctor` is the other half, and the more important one. Forked copies,
leftover `_shared/` directories, half-filled adapters and dead gate pointers all fail
**silently** — that's how one project ends up with five drifted skills nobody notices
until they're diffed by hand. Doctor makes each of those a line of output. Run it in any
repo, any time; it changes nothing.

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

Containment is now the plugin's `enabledPlugins` entry rather than a hand-placed symlink —
a repo that never enabled `prd-workflow` cannot spawn `prd-worker` at all. See
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
