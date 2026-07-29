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
| `prd-workflow` | the `prd-workflow` plugin | **No** — the bundle also covers `deep-grill`, which stays a plain top-level skill, deliberately outside the plugin. Its `## Sources of truth` requirement is why that section is in this bundle's list at all |
| `ado-workflow` | the `ado-workflow` plugin | **No**, for the same reason as `prd-workflow` — the plugin ships the four `[SPEC]`-loop skills and the `spec-worker` agent, and the bundle additionally covers `deep-grill`, the plain skill that puts `## Sources of truth` on the list |
| `prd-qa` | two plain skills, no plugin | n/a — nothing is packaged |
| `figma-tools` | the `figma-tools` plugin | Yes, today |

`figma-tools` was called `figma` here until the plugin took that name and then had to give
it up: `figma@claude-plugins-official` already owns it, and the clash breaks skills-dir
loading outright. The bundle followed the plugin rather than keeping a name that now points
at somebody else's integration. A bundle and a plugin sharing a name still does not make
them the same set — `prd-workflow` is the standing counter-example.

## Schema

One `##` section per bundle, named by its slug. Every field is a bold-labelled list
item, exactly these keys, in this order:

| Field | Meaning |
|---|---|
| **Status** | `ready` — bootstrappable. `pending #N` — refuse and point at the issue. |
| **Adapter sections** | `##` headings of `<repo-root>/.claude/project/adapter.md` this bundle needs filled. Empty means the bundle is adapter-free — no adapter, no interview, no questions. |
| **Gates** | Gate templates to offer, and where they land. Optional by definition — a gate exists only where a project has a silent-failure class. |

Section headings are matched by **prefix**, so `## Sources of truth` matches the
template's `## Sources of truth (deep-grill recon + hard gates)`.

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

The installer reads this table rather than hardcoding the mapping, exactly as it reads
**Adapter sections** rather than hardcoding a section list. A project runs one tracker, so
a bundle whose implied tracker contradicts an **existing** adapter's `Tracker:` line is a
conflict to surface and stop on — never something to resolve by rewriting the line or
deleting a section. See `install-skills/SKILL.md` step 3a for the one narrow case in which
a tracker sub-section is deleted at all.

---

## `prd-workflow`

The PRD → issues → implementation loop. The reason the adapter exists.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## QA doc convention`, `## Sources of truth`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section, so a partial adoption can drop questions:

| Section | Wanted by |
|---|---|
| `## Repo` | all five workflow skills |
| `## Commands`, `## Verify ladder` | `to-issues`, `work-on-prd`, `work-on-issue` |
| `## App facts` | `work-on-prd` (pasted into every worker prompt) |
| `## QA doc convention` | `work-on-prd` |
| `## Sources of truth` | `deep-grill` only |
| `## Project gates` | `to-prd`, `to-issues`, `deep-grill` |
| `## Repo discipline` | `work-on-prd`, `work-on-issue` |
| `## One-time repo preconditions` | `work-on-prd` (the `Closes #N` setting) |

Two of those rows name skills the `prd-workflow` **plugin** does not contain. `deep-grill`
is a plain top-level skill and stays one — it is recon, not the loop, and it is useful on
its own. So a project that installs the plugin and skips `deep-grill` genuinely does not
need `## Sources of truth`, and one that runs `deep-grill` without the loop still does.
Ask against this table, not against the plugin's inventory.

## `ado-workflow`

The same loop against an Azure DevOps board: `[SPEC]` → `[TASK]`s → implementation, run by
`work-on-spec`. `prd-workflow`'s sibling, and it needs almost the same facts.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## Sources of truth`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | all four workflow skills — and it carries far more here than on GitHub. The `### Azure DevOps` sub-section holds the org, the **two** projects (work items and repo, routinely different), the team, the repository, the work-item type, the three board states, the title prefixes and the branch pattern. None of it is discoverable from the tree, which is why every one of them is a question |
| `## Commands`, `## Verify ladder` | `to-spec-tasks` (every `[TASK]` names its own verify command), `work-on-spec`, and `spec-worker` through the adapter `work-on-spec` pastes into each worker prompt |
| `## App facts` | `work-on-spec` (pasted into every worker prompt) |
| `## Sources of truth` | `deep-grill` only |
| `## Project gates` | `to-spec`, `to-spec-tasks`, `deep-grill` |
| `## Repo discipline` | `work-on-spec`, and `spec-worker` for the scoped `CONTEXT.md` rule |
| `## One-time repo preconditions` | all four — its `### Azure DevOps` sub-section names the MCP server key and the exact spelling of the board states, and both fail *silently* when wrong: a server under the wrong key reads as unconfigured, and a near-miss state name is a no-op rather than an error |

**`## QA doc convention` is deliberately absent** — the one section `prd-workflow` requires
that this bundle does not. `work-on-spec` ends a run by creating a `[QA]` **work item**
describing the slice that just landed, not by committing a QA document to the repo, so
there is no path convention to agree on and asking for one would fill in a value nothing
reads.

The two rows that look like GitHub leftovers are real. `## Sources of truth` is here for
the same reason as in `prd-workflow` — `deep-grill` is tracker-agnostic recon that runs
*before* `to-spec`, and a project that skips it genuinely does not need the section.
`## One-time repo preconditions` survives even though the ADO side has no analogue of
GitHub's un-queryable auto-close setting (the pull request's completion options transition
the linked work items instead): what is left there is the MCP server and the board-state
spelling, both human-checked once.

## `prd-qa`

The QA loop that runs against a PRD branch before merge.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## QA doc convention`, `## Verify ladder`, `## Sources of truth`, `## Repo discipline`
- **Gates:** none

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | both — `triage-prd` also reads `Related repos` to route across the contract boundary |
| `## QA doc convention` | `triage-prd` (loads the QA doc as decision context) |
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
