# Install: wiring a project

Templates for the two things a project owns. Everything else stays canonical here and
reaches a machine through the platform.

**Getting the skills onto a machine is [`INSTALL.md`](../INSTALL.md)'s job**, not this
directory's — marketplace, config directories, scopes, live authoring and the traps in
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
the adapter exactly the way a symlinked one did. Only *creating* the adapter was ever a
bootstrapping problem, which is why `install-skills` kept that half and dropped the rest.

## Bootstrapping the adapter

Run the `install-skills` skill from the target repo:

```
/install-skills install prd-workflow
```

It resolves the repo and its remote, copies the adapter template if there isn't one
already, interviews you for the facts no file in your repo states, offers any gate the
bundle declares, and finishes by running `doctor`. Bundles are defined in
[`bundles.md`](bundles.md) — `prd-workflow`, `prd-qa`, `figma-tools` — and a bundle names
adapter sections, not skills.

The other mode is **`doctor`**, the anti-rot check: a real directory shadowing a skill that
canonical or a reachable plugin already provides, a leftover `_shared/`, an unfilled
placeholder, a dead gate pointer, a dangling link. Every one of those is silent today and
loud after this. Safe to run anywhere, any time; it changes nothing.

It resolves a plugin from four places — installed manifests, versioned cache directories,
skills-dir plugins, and a repo-local `plugins/` — across all three config directories, so a
skill that arrives from a plugin does not read as missing.

## Doing it by hand

The skill is the supported path; this is what it does, for when you're debugging it.

1. Copy `install/adapter.template.md` → `.claude/project/adapter.md` and fill every `<placeholder>`.
2. Add gates only if this project has a silent-failure class the skills don't already cover. `install/gates/gate.template.md` is the shape; register each one in the adapter's `## Project gates`.
3. Commit `.claude/project/`. It is the project's own facts, and it is the only thing here a project owns.
