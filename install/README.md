# Install: wiring a project

Templates for the two things a project owns. Everything else stays canonical here and
reaches a machine through the platform.

**Getting the skills onto a machine is [`INSTALL.md`](../INSTALL.md)'s job**, not this
directory's — marketplace, config directories, scopes, the dev mode and the traps in
each. This file covers only what a *project* owns once the skills can reach it.

## Layout

```
<repo-root>/.claude/
  project/                     # ← everything this directory is about
    adapter.md                 # from install/adapter.template.md — committed, project-specific
    <gate>.md                  # optional, from install/gates/gate.template.md
    ui-manifests.md            # optional, from install/gates/ui-manifests.template.md
```

**A project never owns a `_shared/`.** That is the whole point of this layout: `../_shared/…` from any skill can only ever mean a canonical global-reference file in this repo. Project facts live in `.claude/project/`, which skills resolve from the repo root. Packaging does not weaken this: inside a plugin, `skills/_shared` is a symlink back to the same canonical directory, dereferenced into the versioned install cache at install time. That copy is a regenerated build artifact, not an editable project-side fork — a `_shared/` in a project repo is still a bug.

Three rules fall out, and skills are written against them:

1. Global reference → `../_shared/<file>.md`. Plain relative path, no ambiguity to warn about.
2. The project → `<repo-root>/.claude/project/adapter.md`. Exactly one path, resolved from the repo root.
3. Project gates → **never named by a skill.** The adapter's `## Project gates` registry names them; skills follow the pointer.

**Rule 2 is unaffected by how a skill was delivered.** It resolves against the project the
session is running in, at runtime — so a skill served from a plugin cache directory finds
the adapter exactly the way a skill loaded from a working tree does. Only *creating* the
adapter was ever a bootstrapping problem, which is why `setup` keeps that half and does nothing else.

## Bootstrapping the adapter

Run the `setup` skill of the plugin you installed, from the target repo:

```
/prd-workflow:setup
```

Every plugin with a bundle ships one — `prd-workflow`, `ado-workflow`, `figma-tools`, `lk` and
`qa`. Each is a thin entry point: it names the bundles its plugin ships and follows
[`setup.md`](setup.md), the one installer they all share. The interview it runs is
[`interview.md`](interview.md), and the anti-rot check is [`doctor.sh`](doctor.sh). There is no
per-plugin installer logic; adding a bundle means editing [`bundles.md`](bundles.md) and naming
it in its plugin's `setup` table.

Each plugin reaches this directory through a packaging symlink, `skills/install ->
../../../install`, which install dereferences into the plugin's cache copy. Every path in
`setup.md` is relative to this directory, so it resolves the same from the working tree and
from a cache copy. Several plugins writing one adapter is safe because `setup` gap-fills an
existing adapter and never deletes from it.

It resolves the repo and its remote, copies the adapter template if there isn't one
already, interviews you for the facts no file in your repo states, offers any gate the
bundle declares, and finishes by running `doctor`. Bundles are defined in
[`bundles.md`](bundles.md) — `prd-workflow`, `ado-workflow`, `prd-qa`, `ado-qa`, `qa`,
`grill`, `figma-tools` — and a bundle names adapter sections, not skills.

The template is **tracker-parametric**: `## Repo` and `## One-time repo preconditions` each
carry a `### GitHub` and an `### Azure DevOps` sub-section, and the bundle decides which
one survives — except `figma-tools`, which files on both and therefore asks you once. On a
fresh copy the installer writes the `Tracker:` line and deletes the
other sub-section, so the adapter you end up filling only ever asks about your own tracker.
That deletion is the single narrow exception to never-delete, and it applies to a fresh
template copy only — an install against an adapter that already exists gap-fills and
deletes nothing. See [`setup.md`](setup.md) step 3a.

The other mode is **`doctor`**, the anti-rot check: a leftover `_shared/`, an unfilled
placeholder, a dead gate pointer, a dangling link. Every one of those is silent today and
loud after this. Safe to run anywhere, any time; it changes nothing.

It resolves a plugin from installed manifests, versioned cache directories and a
repo-local `plugins/`, across every config directory it can see, so a skill that arrives
from a plugin does not read as missing. It does **not** inspect what a project keeps in
its own `.claude/skills/` beyond reporting what is broken — that is the project's
business.

## Doing it by hand

The skill is the supported path; this is what it does, for when you're debugging it.

1. Copy `install/adapter.template.md` → `.claude/project/adapter.md`, set the `Tracker:` line, delete the sub-sections of the tracker you did not pick, and fill every remaining `<placeholder>`.
2. Add gates only if this project has a silent-failure class the skills don't already cover. `install/gates/gate.template.md` is the shape; register each one in the adapter's `## Project gates`.
3. Commit `.claude/project/`. It is the project's own facts, and it is the only thing here a project owns.
