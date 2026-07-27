# CLAUDE.md

Canonical source repo for Liam's personal Claude Code skills. Each top-level
directory is one skill. Two directories are not skills:

- `_shared/` — **global reference only.** Docs several skills read, true in every
  project: `model-effort-heuristics.md`, `prd-eligibility.md`, `ui-manifests.md`,
  `ui-standard.md`. No templates, no project values, ever.
- `install/` — templates a project fills in: `adapter.template.md` and
  `gates/`. See `install/README.md` for the layout a wired project ends up with.

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

- A relative `../_shared/…` inside a skill resolves *past* the symlink, into
  this repo. That is by design and it is unambiguous **because no project owns a
  `_shared/`** — project facts live in `<repo-root>/.claude/project/` instead.
  Don't reintroduce a project-side `_shared/`, and don't add "you may have
  resolved the wrong file" warnings back to the skills; the layout is what makes
  them unnecessary.
- Skills address exactly three things: global reference as `../_shared/x.md`, the
  project as `<repo-root>/.claude/project/adapter.md`, and project-specific gates
  **never by name** — the adapter's `## Project gates` registry names them and
  skills follow the pointer. That last rule is what keeps a skill generic instead
  of forked to hardcode one project's filename.
- Adding a new skill means adding a symlink too; creating the directory here is
  not enough to make it discoverable.
