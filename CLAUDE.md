# CLAUDE.md

Canonical source repo for Liam's personal Claude Code skills, and the marketplace
that publishes them. Skills live in one of two places:

- **Inside a plugin** — `plugins/<plugin>/skills/<skill>/`, with the plugin's agents
  in `plugins/<plugin>/agents/`. Two plugins today, `prd-workflow` and `figma-tools`,
  catalogued in `.claude-plugin/marketplace.json` as marketplace `liamklyneker`.
- **At the top level** — one directory per plain skill, for anything not packaged.

Four top-level entries are not skills:

- `.claude-plugin/` — `marketplace.json`, the published catalog.
- `plugins/` — the packaged plugins.
- `_shared/` — **global reference only.** Docs several skills read, true in every
  project: `model-effort-heuristics.md`, `prd-eligibility.md`, `ui-manifests.md`,
  `ui-standard.md`. No templates, no project values, ever.
- `install/` — what a project gets wired with: `bundles.md` (the manifest the
  `install-skills` skill reads), `adapter.template.md`, and `gates/`. See
  `install/README.md` for the layout a wired project ends up with.

The migration's compat shims — top-level names that were **symlinks into
`plugins/`** — are **gone** (#26), along with the nested
`work-on-prd/agents/prd-worker.md` link. Every top-level entry is now either a plain
skill or one of the four above. Don't reintroduce the shape: a top-level symlink into
`plugins/` makes the same skill discoverable under two names, which is what the
migration existed to end. The estate that consumes all of this — which config has
which plain skill, which repo enables which plugin — is recorded in
`docs/estate-inventory.md`; update it when you change the wiring.

**A plugin namespaces everything it provides.** Skills invoke as
`prd-workflow:work-on-prd`, agents resolve as `subagent_type: prd-workflow:prd-worker`,
and the bare names only exist on the plain-skill symlink route. Getting an agent type
wrong does **not** error — it degrades silently to `general-purpose` — so any doc or
skill naming a subagent type has to say which route it means.

`install-skills` *is* a plain skill and lives at the top level like any other. It is
the only one that ships an executable (`scripts/doctor.sh`) — the mechanical checks
have to be deterministic, and a check that gets paraphrased differently on each run
isn't one. Everything else here stays prose.

`INSTALL.md` is the guide for getting any of it onto a machine — marketplace, config
directories, scopes, live authoring, and the traps. Keep it accurate; it is written
from observed platform behaviour, and the platform has repeatedly differed from its
own docs.

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

## Two delivery routes, and what each means for editing

A skill reaches a machine either as part of an **installed plugin** — a copy in the
config's cache, keyed by the git commit SHA — or as a **symlink** into a config's
`skills/` directory, where nothing is copied. Full instructions: `INSTALL.md`.

The consequence that bites: **an installed plugin pins to committed `HEAD`.** Edits in
this working tree are invisible to it until they are committed and it is reinstalled.
Live authoring therefore runs through skills-dir mode — this repo self-hosts via one
symlink, `.claude/skills/prd-workflow -> ../../plugins/prd-workflow`, and edits there
are live on the next session launch. Never run both routes for the same plugin in one
place; every skill loads twice.

Rules that hold regardless of route:

- A relative `../_shared/…` inside a skill resolves to this repo's global reference.
  That is unambiguous **because no project owns a `_shared/`** — project facts live in
  `<repo-root>/.claude/project/` instead. Inside a plugin the reference is
  `skills/_shared`, a symlink to the same canonical directory, dereferenced into the
  install cache; that copy is a regenerated build artifact, not a fork. Don't
  reintroduce a project-side `_shared/`, and don't add "you may have resolved the
  wrong file" warnings back to the skills; the layout is what makes them unnecessary.
- Skills address exactly three things: global reference as `../_shared/x.md`, the
  project as `<repo-root>/.claude/project/adapter.md`, and project-specific gates
  **never by name** — the adapter's `## Project gates` registry names them and
  skills follow the pointer. That last rule is what keeps a skill generic instead
  of forked to hardcode one project's filename.
- **Packaging never moved the project.** The adapter path resolves against whichever
  project the session is running in, at runtime, so it works unchanged from a plugin
  cache directory. Only *creating* the adapter is a bootstrapping problem, which is
  why `install-skills` keeps that half and places nothing.
- Adding a skill to a plugin means adding the directory under `plugins/<plugin>/skills/`
  — nothing else; the plugin's inventory is discovered, not listed. Adding a *plain*
  skill means adding a symlink into each config that should see it; creating the
  directory here is not enough to make it discoverable.
