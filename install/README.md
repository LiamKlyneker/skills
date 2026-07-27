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

## Installing

Run the `install-skills` skill from the target repo:

```
/install-skills install prd-workflow
```

It resolves the repo and its remote, symlinks the bundle's skills and agents, copies the
adapter template if there isn't one already, interviews you for the facts no file in your
repo states, and finishes by running `doctor`. Bundles are defined in
[`bundles.md`](bundles.md) — `prd-workflow`, `prd-qa`, `figma`.

Two more modes worth knowing before you need them:

- **`doctor`** — the anti-rot check. A forked copy where a symlink belongs, a leftover
  `_shared/`, an unfilled placeholder, a dead pointer, a vendored skill behind its stamp:
  every one of those is silent today and loud after this. Safe to run anywhere, any time.
- **`install --vendor`** — copies instead of symlinking, and stamps each copy with the
  commit it came from. For repos whose install has to survive `git clone` — collaborators,
  CI, cloud agents — where a symlink would just dangle.

## Doing it by hand

The installer is the supported path; this is what it does, for when you're debugging it.

1. Symlink each skill you want into `.claude/skills/`, pointing at your clone of this repo.
2. Copy `install/adapter.template.md` → `.claude/project/adapter.md` and fill every `<placeholder>`.
3. Add gates only if this project has a silent-failure class the skills don't already cover. `install/gates/gate.template.md` is the shape; register each one in the adapter's `## Project gates`.
4. Commit `.claude/project/`. Gitignore `.claude/skills/` when it holds symlinks — they're machine-local and dangle for anyone else who clones.

Skills that ship a subagent need one more symlink each; see the root `README.md`.

A skill that's already installed globally (`~/.claude/skills/…`) must **not** be re-linked
per project — a session in the repo will find it either way, and the project copy is one
more thing to keep in step.
