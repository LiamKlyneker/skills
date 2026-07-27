# Install: wiring a project

Templates for the two things a project owns. Everything else is symlinked and stays canonical here.

## Layout

```
<repo-root>/.claude/
  project/
    adapter.md                 # from install/adapter.template.md — committed, project-specific
    <gate>.md                  # optional, from install/gates/gate.template.md
    ui-manifests.md            # optional, from install/gates/ui-manifests.template.md
  skills/
    to-prd -> <canonical>/to-prd
    to-issues -> <canonical>/to-issues
    …                          # one symlink per skill, never a copy
```

**A project never owns a `_shared/`.** That is the whole point of this layout: `../_shared/…` from any skill resolves past the symlink into this repo, so it can only ever mean a canonical global-reference file. Project facts live in `.claude/project/`, which skills resolve from the repo root.

Three rules fall out, and skills are written against them:

1. Global reference → `../_shared/<file>.md`. Plain relative path, no ambiguity to warn about.
2. The project → `<repo-root>/.claude/project/adapter.md`. Exactly one path, resolved from the repo root.
3. Project gates → **never named by a skill.** The adapter's `## Project gates` registry names them; skills follow the pointer.

## Steps

1. Symlink each skill you want into `.claude/skills/`, pointing at your clone of this repo.
2. Copy `install/adapter.template.md` → `.claude/project/adapter.md` and fill every `<placeholder>`.
3. Add gates only if this project has a silent-failure class the skills don't already cover. `install/gates/gate.template.md` is the shape; register each one in the adapter.
4. Commit `.claude/project/`. The skill symlinks may or may not be committed — that's per project.

Skills that ship a subagent need one more symlink each; see the root `README.md`.

An install/uninstall/doctor command that automates this is tracked separately.
