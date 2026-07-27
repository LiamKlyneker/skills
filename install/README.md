# Install: wiring a project

Templates for the two things a project owns. Everything else stays canonical here and
reaches a machine through the platform — the marketplace for plugins, a `skills/` symlink
for plain skills and live authoring.

## Layout

```
<repo-root>/.claude/
  project/                     # ← everything this directory is about
    adapter.md                 # from install/adapter.template.md — committed, project-specific
    <gate>.md                  # optional, from install/gates/gate.template.md
    ui-manifests.md            # optional, from install/gates/ui-manifests.template.md
```

**A project never owns a `_shared/`.** That is the whole point of this layout: `../_shared/…` from any skill resolves past the symlink into this repo, so it can only ever mean a canonical global-reference file. Project facts live in `.claude/project/`, which skills resolve from the repo root.

Three rules fall out, and skills are written against them:

1. Global reference → `../_shared/<file>.md`. Plain relative path, no ambiguity to warn about.
2. The project → `<repo-root>/.claude/project/adapter.md`. Exactly one path, resolved from the repo root.
3. Project gates → **never named by a skill.** The adapter's `## Project gates` registry names them; skills follow the pointer.

## Getting the skills

Not this directory's job, and not `install-skills`' job either. The platform installs,
versions and updates:

- **Plugin** — `/plugin marketplace add LiamKlyneker/skills`, then `/plugin install
  <plugin>` from a session running under the config directory you want it in. Plugins are
  stored per config directory, so each one is an independent decision.
- **Plain skill, or editing in place** — symlink it into that config's `skills/`
  directory, pointing at your clone. Loads live; nothing is copied.
- **A plugin that has to travel with the repo** — collaborators, CI, cloud agents —
  committed project settings, not a symlink only your laptop has.

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

The other mode is **`doctor`**, the anti-rot check: a forked copy where a symlink belongs,
a leftover `_shared/`, an unfilled placeholder, a dead gate pointer. Every one of those is
silent today and loud after this. Safe to run anywhere, any time; it changes nothing.

## Doing it by hand

The skill is the supported path; this is what it does, for when you're debugging it.

1. Copy `install/adapter.template.md` → `.claude/project/adapter.md` and fill every `<placeholder>`.
2. Add gates only if this project has a silent-failure class the skills don't already cover. `install/gates/gate.template.md` is the shape; register each one in the adapter's `## Project gates`.
3. Commit `.claude/project/`. It is the project's own facts, and it is the only thing here a project owns.
