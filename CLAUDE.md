# CLAUDE.md

Canonical source repo for Liam's personal Claude Code skills. Each top-level
directory is one skill; `_shared/` holds docs several skills reference.

## Git workflow

**Commit straight to `main`.** Do *not* branch and open a PR by default — this
repo's history is linear and direct-to-main, and a PR for a prose edit to a
`SKILL.md` is pure friction. This overrides the general "if on the default
branch, branch first" guidance.

Branch only when:

- Liam explicitly asks for a branch or a PR, or
- the change is a genuinely exceptional one — a sweeping restructure across
  many skills, or something he'd plausibly want to review before it lands.

When in doubt, commit to `main` and say so in your summary; that's cheaper to
undo than an unwanted PR.

Unchanged by the above: **still only commit or push when Liam asks.** This rule
governs *where* commits go, not *whether* to make them unprompted.

## Skills are consumed via symlink

Skill directories are symlinked into the config dirs under `~/.claude*/skills/`,
never copied — so an edit here is live everywhere on the next session launch.
Two consequences when editing a skill:

- A relative `../_shared/…` inside a skill resolves *past* the symlink. Skills
  that need a project's filled-in adapter must resolve it from the project repo
  root (`<project-root>/.claude/skills/_shared/project-adapter.md`), not
  relatively. Several skills carry an explicit warning about this — preserve it.
- Adding a new skill means adding a symlink too; creating the directory here is
  not enough to make it discoverable.
