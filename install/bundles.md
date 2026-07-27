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

- **Status:** pending #13
- **Skills:** `qa-prd-log`, `triage-prd`
- **Global reference:** —
- **Adapter sections:** `## QA doc convention`, `## Verify ladder`
- **Gates:** none
- **Agents:** none

Neither skill exists in this repo yet. `install-skills install prd-qa` must **refuse**
and say so — do not partially install it, and do not silently fall back to
`prd-workflow`.

## `figma`

Figma → spec, and the UI-primitive skills that consume the same reference.

- **Status:** ready
- **Skills:** `figma-to-spec`, `tokens-init` (provisional), `figma-component` (provisional)
- **Global reference:** `_shared/ui-standard.md`, `_shared/ui-manifests.md`
- **Adapter sections:** —
- **Gates:** `install/gates/ui-manifests.template.md` → `.claude/project/ui-manifests.md`, optional
- **Agents:** `figma-to-spec/agents/figma-region-extractor.md` → `user`

**Adapter-free.** These skills read global reference only, so a repo can run them with
no `.claude/project/` at all — the installer skips the interview entirely and installs
nothing but symlinks. The optional `ui-manifests.md` gate is the exception: a project
that wants its own primitive homes, real token files and stack-specific traps named
registers one, the same way as any other gate.

`tokens-init` and `figma-component` are marked provisional because #14 is still deciding
where they live. Install them; be ready for them to move.
