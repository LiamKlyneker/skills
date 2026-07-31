# Bundles

What `install-skills` bootstraps. A **bundle** is a named set of skills that are only
useful together, described here by the one thing no distribution mechanism can deliver:
**which `##` sections of the project's adapter they need filled**, plus any gate template
the set implies.

That mapping is the whole point. It is what makes the install interview finite and
bundle-specific instead of asking every question every time, and it has no home anywhere
else. The installer **reads this file** rather than hardcoding a section list.

**Bundles do not list skills.** Getting the skills themselves onto a machine is the
platform's job — `/plugin marketplace add LiamKlyneker/skills` and `/plugin install`, or a
symlink into a config's `skills/` directory for a plain skill. The catalog owns the
inventory; this file owns the questions.

## Bundle is not plugin

Two separate namespaces, and they are only *sometimes* the same set. Never let a reader
assume otherwise:

| Bundle | Distributed as | Same set? |
|---|---|---|
| `prd-workflow` | the `prd-workflow` plugin | **Yes, today** — the five loop skills the plugin ships are exactly the set this bundle asks questions for. It read **No** until the `grill` bundle took `## Sources of truth` off the list; the grills are `lk` skills and their question is asked under their own bundle now |
| `ado-workflow` | the `ado-workflow` plugin | **Yes, today**, for the same reason — the plugin ships the four `[SPEC]`-loop skills and the `spec-worker` agent, and nothing outside it puts a section on this bundle's list any more |
| `prd-qa` | two skills of the `lk` plugin | **No** — the bundle is `triage-prd` + `qa-prd-log`, two of the seven skills `lk` ships. Installing the plugin is not adopting the bundle, and the bundle does not want the plugin's other five |
| `grill` | two skills of the `lk` plugin | **No** — the bundle is `grill` + `deep-grill`, the two `lk` skills that read a project fact. `lk` therefore maps to **two** bundles, which is exactly why neither of them is named after it |
| `figma-tools` | the `figma-tools` plugin | Yes, today |

`figma-tools` was called `figma` here until the plugin took that name and then had to give
it up: `figma@claude-plugins-official` already owns it, and the clash breaks skills-dir
loading outright. The bundle followed the plugin rather than keeping a name that now points
at somebody else's integration. A bundle and a plugin sharing a name still does not make
them the same set; where the table says "yes" it is reporting today's lists, not a rule.
`grill` and `prd-qa` are the standing proof that the two namespaces come apart: each is a
pair of skills inside the `lk` plugin, and neither of them is `lk`.

## Schema

One `##` section per bundle, named by its slug. Every field is a bold-labelled list
item, exactly these keys, in this order:

| Field | Meaning |
|---|---|
| **Status** | `ready` — bootstrappable. `pending #N` — refuse and point at the issue. |
| **Adapter sections** | `##` headings of `<repo-root>/.claude/project/adapter.md` this bundle needs filled. Empty means the bundle is adapter-free — no adapter, no interview, no questions. |
| **Gates** | Gate templates to offer, and where they land. Optional by definition — a gate exists only where a project has a silent-failure class. |

Section headings are matched by **prefix**, so `## Sources of truth` matches the
template's `## Sources of truth (recon + hard gates)`. A project whose adapter spells the
parenthetical differently still matches, which is the point — the heading's tail is prose
and free to change.

## Which tracker a bundle implies

The adapter template is **tracker-parametric**: `## Repo` and `## One-time repo
preconditions` each carry a `### GitHub` and an `### Azure DevOps` sub-section, and a
filled adapter keeps exactly one of the two. Which one is not a question worth asking
twice, because the bundle already answers it:

| Bundle | Implies `Tracker:` |
|---|---|
| `prd-workflow`, `prd-qa` | `github` |
| `ado-workflow` | `azure-devops` |
| `figma-tools` | neither — adapter-free, so there is no `Tracker:` line to write |
| `grill` | neither — a grill is tracker-agnostic recon that runs *before* `to-prd` or `to-spec`, so there is nothing tracker-shaped to write |

The installer reads this table rather than hardcoding the mapping, exactly as it reads
**Adapter sections** rather than hardcoding a section list. A project runs one tracker, so
a bundle whose implied tracker contradicts an **existing** adapter's `Tracker:` line is a
conflict to surface and stop on — never something to resolve by rewriting the line or
deleting a section. See the `install-skills` skill's own `SKILL.md`, step 3a, for the one
narrow case in which a tracker sub-section is deleted at all.

**"Neither" is not a licence to pick one.** `figma-tools` never reaches the question — it is
adapter-free, so no adapter is created. `grill` does reach it, being the one bundle that
needs a section but no tracker: it writes no `Tracker:` line and deletes neither `###`
sub-section, leaving the choice to whichever tracker-bound bundle is installed next. That
later install finds an adapter with no `Tracker:` line and **both** sub-sections still
present, which is the gap-fill case in step 3a and not a contradiction to stop on.

---

## `prd-workflow`

The PRD → issues → implementation loop. The reason the adapter exists.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section, so a partial adoption can drop questions:

| Section | Wanted by |
|---|---|
| `## Repo` | all five workflow skills — including the **title prefixes**, which every one of them either writes or filters on |
| `## Commands`, `## Verify ladder` | `to-issues`, `work-on-prd`, `work-on-issue` |
| `## App facts` | `work-on-prd` (pasted into every worker prompt) |
| `## Project gates` | `to-prd`, `to-issues` |
| `## Repo discipline` | `work-on-prd`, `work-on-issue` |
| `## One-time repo preconditions` | `work-on-prd` (the `Closes #N` setting) |

Every row names a skill this plugin ships. `## Sources of truth` used to be here too, for
`deep-grill` alone — it moved to the `grill` bundle, which is where a project that runs the
interviews answers for it.

## `ado-workflow`

The same loop against an Azure DevOps board: `[SPEC]` → `[TASK]`s → implementation, run by
`work-on-spec`. `prd-workflow`'s sibling, and it needs almost the same facts.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | all four workflow skills — and it carries far more here than on GitHub, though the gap has narrowed: both trackers now register **title prefixes** there. The `### Azure DevOps` sub-section holds the org, the **two** projects (work items and repo, routinely different), the team, the repository, the work-item type, the three board states, the title prefixes and the branch pattern. None of it is discoverable from the tree, which is why every one of them is a question |
| `## Commands`, `## Verify ladder` | `to-spec-tasks` (every `[TASK]` names its own verify command), `work-on-spec`, and `spec-worker` through the adapter `work-on-spec` pastes into each worker prompt |
| `## App facts` | `work-on-spec` (pasted into every worker prompt) |
| `## Project gates` | `to-spec`, `to-spec-tasks` |
| `## Repo discipline` | `work-on-spec`, and `spec-worker` for the scoped `CONTEXT.md` rule |
| `## One-time repo preconditions` | all four — its `### Azure DevOps` sub-section names the MCP server key and the exact spelling of the board states, and both fail *silently* when wrong: a server under the wrong key reads as unconfigured, and a near-miss state name is a no-op rather than an error |

**This bundle's section list and `prd-workflow`'s are now the same set**, and neither asks
anything about QA. They used to differ by exactly one row, back when `work-on-spec` created
a per-run `[QA]` work item while `work-on-prd` committed a document to a path the adapter
named. Both loops file a per-run item now, so that row was removed from the template and
from both lists rather than added to this one — do not restore it to either. The shape of a
QA item ships with the plugins — `work-on-prd`'s `## Loop end` for GitHub,
`plugins/ado-workflow/skills/references/qa-item.md` for ADO — and is not something an
installer can ask a human for; the argument is ADR 0005.

The row that looks like a GitHub leftover is real. `## One-time repo preconditions` survives
even though the ADO side has no analogue of GitHub's un-queryable auto-close setting (the pull request's completion options transition
the linked work items instead): what is left there is the MCP server and the board-state
spelling, both human-checked once.

## `prd-qa`

The QA loop that runs against a PRD branch before merge.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Verify ladder`, `## Sources of truth`, `## Repo discipline`
- **Gates:** none

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | both — `triage-prd` also reads `Related repos` to route across the contract boundary, and the **title prefixes** it files bugs under |
| `## Verify ladder` | `triage-prd` (every filed issue names its verify step) |
| `## Sources of truth` | `triage-prd` — the project explorer agent, and the contract-boundary one for cross-repo findings |
| `## Repo discipline` | both — scoped `CONTEXT.md` loading |

**Pairs with `prd-workflow`, doesn't replace it.** `triage-prd` files issues shaped like
`to-issues` children, so `work-on-prd` / `work-on-issue` execute them with no new
machinery. Adopting `prd-qa` alone is legal but leaves nothing downstream to run the
issues it files — say so rather than silently bootstrapping both.

Both skills degrade rather than break where the adapter says "None": no related repo
means every finding is a this-repo finding, and no contract-boundary explorer agent
means a cross-boundary root cause gets filed locally and flagged as unmodelled.

## `grill`

The two interviews that run **before** either loop: `grill` inline on one thread, and
`deep-grill` with recon subagents and hard gates for anything that crosses a boundary.

- **Status:** ready
- **Adapter sections:** `## Sources of truth`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Sources of truth` | `deep-grill` only — the project explorer agent, the contract-boundary one, and the access-policy source its Data & Access Manifest gate reads before the interview starts |

**One section, and one skill wants it.** `grill` reads **nothing** from the adapter — it is
the lightweight inline interview and explores on the thread it is invoked from — so the whole
of this bundle's interview is `deep-grill`'s three sources of truth. Ask against the table,
not against the `lk` plugin's inventory.

That asymmetry is why this bundle exists at all. `## Sources of truth` used to ride along on
`prd-workflow` and `ado-workflow`, which meant every adopter of a loop was interviewed for
three agent names belonging to a skill they may never have installed. The section now lives
where the skill that reads it does.

`deep-grill` also reads the adapter's `## Project gates` registry and runs every gate whose
trigger the plan matches — but that is not an interview question here. A project with no
extra gates needs no such section, and a project that accepts the gate template gains
`## Project gates` as the place its gate is registered, by the same route `figma-tools`
reaches an adapter it otherwise does not need.

Adopting this bundle alone is entirely normal: a grill is useful with no loop downstream, and
its output is a conversation, not a tracker artifact. That is also why it implies neither
tracker — see *Which tracker a bundle implies* above.

## `figma-tools`

Figma → spec, and the UI-primitive skills that consume the same reference.

- **Status:** ready
- **Adapter sections:** —
- **Gates:** `install/gates/ui-manifests.template.md` → `.claude/project/ui-manifests.md`, optional

**Adapter-free.** These skills read global reference only, so a repo can run them with
no `.claude/project/` at all — the installer skips the interview entirely and asks
nothing. The optional `ui-manifests.md` gate is the exception: a project that wants its
own primitive homes, real token files and stack-specific traps named registers one, the
same way as any other gate. Accepting it is the one case where an adapter-free bundle
still ends up with an adapter, because the `## Project gates` registry lives there.

`tokens-init` and `figma-component` are **deprecated** — superseded by `figma-to-spec`.
They are part of no bundle and no plugin, are linked into no project, and carry
`disable-model-invocation: true` so nothing can auto-fire them. The directories stay in
the canonical repo only until their salvageable parts are moved out; #14 tracks what the
UI Primitive and Token manifests need once that happens. Do not install them.
