# Bundles

What `install-skills` installs. A **bundle** is a named set of skills that are only
useful together, plus everything a project needs for them to work: the global
reference files they read, the adapter sections they expect filled, any gate
templates, and any subagents they spawn.

The installer **reads this file** rather than hardcoding a list. Adding a bundle here
is the whole job of adding a bundle.

## Schema

One `##` section per bundle, named by its slug. Every field is a bold-labelled list
item, exactly these keys, in this order:

| Field | Meaning |
|---|---|
| **Status** | `ready` — installable. `pending #N` — refuse the install and point at the issue. |
| **Skills** | Directories in this repo to install. A trailing `(provisional)` marks one whose home is still being decided. |
| **Global reference** | Files under `_shared/` these skills read. Not installed in symlink mode (`../_shared/…` already resolves into this repo); **copied in vendor mode**, where nothing else would provide them. |
| **Adapter sections** | `##` headings of `<repo-root>/.claude/project/adapter.md` this bundle needs filled. Empty means the bundle is adapter-free — no adapter, no interview. This list is what makes the install interview finite and bundle-specific instead of asking every question every time. |
| **Gates** | Gate templates to offer, and where they land. Optional by definition — a gate exists only where a project has a silent-failure class. |
| **Agents** | Subagents the skills spawn by type, and their scope. `user` → `~/.claude/agents/`. `project` → `<repo-root>/.claude/agents/`. Every one is detachable; a missing agent degrades, it doesn't break. |

Section headings are matched by **prefix**, so `## Sources of truth` matches the
template's `## Sources of truth (deep-grill recon + hard gates)`.

---

## `prd-workflow`

The PRD → issues → implementation loop. The reason the adapter exists.

- **Status:** ready
- **Skills:** `to-prd`, `to-issues`, `next-prd-issue`, `work-on-prd`, `work-on-issue`, `deep-grill`
- **Global reference:** `_shared/prd-eligibility.md`, `_shared/model-effort-heuristics.md`, `_shared/ui-manifests.md`
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## QA doc convention`, `## Sources of truth`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only
- **Agents:** `work-on-prd/agents/prd-worker.md` → `project`

Which skill drives which section, so a partial install can drop questions:

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

`prd-worker` is project-scoped **on purpose**: it commits, so a stray auto-spawn from
an unrelated repo must not be possible. Installing it means `<repo-root>/.claude/agents/`,
never `~/.claude/agents/`.

## `prd-qa`

The QA loop that runs against a PRD branch before merge.

- **Status:** ready
- **Skills:** `qa-prd-log`, `triage-prd`
- **Global reference:** `_shared/model-effort-heuristics.md`, `_shared/prd-eligibility.md`
- **Adapter sections:** `## Repo`, `## QA doc convention`, `## Verify ladder`, `## Sources of truth`, `## Repo discipline`
- **Gates:** none
- **Agents:** none

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
machinery. Installing `prd-qa` alone is legal but leaves nothing downstream to run the
issues it files — say so rather than silently installing both.

Both skills degrade rather than break where the adapter says "None": no related repo
means every finding is a this-repo finding, and no contract-boundary explorer agent
means a cross-boundary root cause gets filed locally and flagged as unmodelled.

## `figma`

Figma → spec, and the UI-primitive skills that consume the same reference.

- **Status:** ready
- **Skills:** `figma-to-spec`
- **Global reference:** `_shared/ui-standard.md`, `_shared/ui-manifests.md`
- **Adapter sections:** —
- **Gates:** `install/gates/ui-manifests.template.md` → `.claude/project/ui-manifests.md`, optional
- **Agents:** `figma-to-spec/agents/figma-region-extractor.md` → `user`

**Adapter-free.** These skills read global reference only, so a repo can run them with
no `.claude/project/` at all — the installer skips the interview entirely and installs
nothing but symlinks. The optional `ui-manifests.md` gate is the exception: a project
that wants its own primitive homes, real token files and stack-specific traps named
registers one, the same way as any other gate.

`tokens-init` and `figma-component` are **deprecated** — superseded by `figma-to-spec`.
They are no longer part of this bundle, are linked into no project, and carry
`disable-model-invocation: true` so nothing can auto-fire them. The directories stay in
the canonical repo only until their salvageable parts are moved out; #14 tracks what the
UI Primitive and Token manifests need once that happens. Do not install them.
