# CLAUDE.md

Canonical source repo for Liam's personal Claude Code skills, and the marketplace
that publishes them. **Every skill lives inside a plugin**, at
`plugins/<plugin>/skills/<skill>/`, with that plugin's agents in
`plugins/<plugin>/agents/`. Five plugins today — `prd-workflow`, `figma-tools`,
`ado-workflow` (the PRD workflow's ADO counterpart), `lk` (the personal skills) and
`install-skills` — all catalogued in `.claude-plugin/marketplace.json` as marketplace
`liamklyneker`.

**There are no plain skills at the top level any more.** There used to be a second
route — one top-level directory per unpackaged skill — and it is gone, not deprecated:
adding a skill here means adding it to a plugin. The rest of the top level:

- `.claude-plugin/` — `marketplace.json`, the published catalog.
- `plugins/` — the packaged plugins.
- `docs/` — `estate-inventory.md`, `adr/`, and `qa/`, the two committed QA documents the
  loops no longer produce (kept as ADR 0005's evidence — see below). Documentation for
  humans; no session loads any of it.
- `_shared/` — **global reference only.** Docs several skills read, true in every
  project: `model-effort-heuristics.md`, `eligibility-policy.md`, `prd-eligibility.md`,
  `ado-eligibility.md`, `ado-workitem-authoring.md`,
  `spec-splitting-seams.md`, `ui-manifests.md`, `ui-standard.md`. No templates, no project
  values, ever.
- `install/` — what a project gets wired with: `bundles.md` (the manifest the
  `install-skills` skill reads), `adapter.template.md`, and `gates/`. See
  `install/README.md` for the layout a wired project ends up with. Canonical copy,
  reached from inside the plugin by a symlink — see below.

The migration's compat shims — top-level names that were **symlinks into
`plugins/`** — are **gone** (#26), along with the nested
`work-on-prd/agents/prd-worker.md` link. Every top-level entry is now one of the ones
listed above. Don't reintroduce the shape: a top-level symlink into
`plugins/` makes the same skill discoverable under two names, which is what the
migration existed to end. The estate that consumes all of this — which config has
which plain skill, which repo enables which plugin — is recorded in
`docs/estate-inventory.md`; update it when you change the wiring.

**A plugin namespaces everything it provides.** Skills invoke as
`prd-workflow:work-on-prd`, agents resolve as `subagent_type: prd-workflow:prd-worker`,
and the bare names only exist on the plain-skill symlink route. Getting an agent type
wrong does **not** error — it degrades silently to `general-purpose` — so any doc or
skill naming a subagent type has to say which route it means.

`install-skills` is **its own plugin**, at `plugins/install-skills/` — not a plain
skill and not part of a personal bundle. It is the one thing here a stranger needs,
because `prd-workflow` and `ado-workflow` cannot run without the adapter it writes, so
reaching it must not require installing anything else. It is also the only skill in the
repo that ships an executable
(`plugins/install-skills/skills/install-skills/scripts/doctor.sh`) — the mechanical
checks have to be deterministic, and a check that gets paraphrased differently on each
run isn't one. Everything else here stays prose.

`INSTALL.md` is the guide for getting any of it onto a machine — marketplace, config
directories, scopes, live authoring, and the traps. Keep it accurate; it is written
from observed platform behaviour, and the platform has repeatedly differed from its
own docs.

## QA is an issue, and titles carry prefixes

Both orchestrators end a run by filing a **per-run QA item** — a `[QA]` issue on GitHub, a
`[QA]` work item on ADO — and **commit nothing**. The adapter has no QA-path convention on
either tracker any more, and each loop owns the whole shape of its own item: `work-on-prd`'s
`## Loop end` for GitHub, `plugins/ado-workflow/skills/references/qa-item.md` for ADO. There
was a shared `_shared/qa-item.md`; it was dissolved into those two, and the rules read the same
on both sides on purpose — a divergence there is a bug, not a tracker difference. The reasoning,
including why the two 440-line documents in `docs/qa/` are kept rather than deleted, is ADR
[0005](docs/adr/0005-qa-is-an-issue-not-a-committed-document.md).

GitHub titles carry `[PRD]` · `[TASK]` · `[BUG]` · `[QA]`, registered in the adapter's
`## Repo` → *Title prefixes* row, never hardcoded in a skill. They are load-bearing:
`_shared/prd-eligibility.md` keeps a PRD's child only when its title is `[TASK]` or `[BUG]`,
and drops `[QA]` unconditionally so a run's QA pass can never be picked as work. Legacy
children carry no prefix, which a set-level fallback handles — do not "simplify" that fallback
to key on any bracket prefix, or one `[QA]` issue will hide every real child of a legacy PRD.

## Git workflow

**Branch and open a PR.** The standard workflow applies here with no exceptions —
if you are on `main`, branch first. This repo publishes a public marketplace, so a
change to a `SKILL.md` is a change to what an agent does on someone else's machine;
it earns a diff to read and a green CI run before it lands, the same as code.

This repo previously ran direct-to-main. It no longer does. If you find a doc still
saying otherwise, that doc is stale — fix it.

Unchanged: **still only commit or push when Liam asks.** This governs *how* changes
land, not *whether* to make them unprompted.

## GitHub, and what `gh` may and may not do here

`gh` is authenticated as `LiamKlyneker` with scopes `gist`, `read:org`, `repo`,
`workflow`. That covers issues, PRs, releases, repo settings and workflow files. It
does **not** cover org/user Projects (`project`), packages, or org admin — if a task
needs those, say so rather than improvising around it.

This is a **public** repo, and its content is executable instruction, so a few things
are settings, not conventions:

- **`main` blocks force-push and deletion**, via the `main-history-protection`
  ruleset, with **no bypass actors** — the block applies to Liam and to admin tokens
  too. Never reach for `git push --force` on `main`; if history genuinely has to be
  rewritten, that is a conscious ruleset change and Liam's call, not something to
  work around.
- **CI must stay fork-safe.** `.github/workflows/validate.yml` triggers on
  `pull_request`, never `pull_request_target` — the latter would run fork code with a
  writable token and secrets. Keep `permissions:` least-privilege and keep every
  action **pinned to a commit SHA**; the repo now enforces SHA pinning, so a tag
  reference will be rejected outright.
- **Structural changes must pass `python3 .github/scripts/validate_skills.py`** — it
  checks the marketplace catalog, plugin manifests, skill and agent frontmatter,
  symlink integrity, and `_shared` references. Run it before committing anything that
  moves a skill, renames one, edits a manifest, or touches a symlink. Standard library
  only; don't give this repo a dependency manifest.
- **Secret scanning and push protection are on.** A blocked push is a real finding —
  read what it caught, don't retry past it.
- Contributors have no push access; fork-and-PR is the only outside route.
  `CONTRIBUTING.md` and `SECURITY.md` state the review posture — a skill PR gets read
  as code, because prose here is what an agent executes on someone else's machine.
  Keep those two files true if the workflow changes.

## Two delivery routes, and what each means for editing

A skill reaches a machine either as part of an **installed plugin** — a copy in the
config's cache, keyed by the plugin's `version` (the git commit SHA is only the
fallback key an *unversioned* plugin gets, and nothing here is unversioned any more) —
or as a **symlink** into a config's `skills/` directory, where nothing is copied. Full
instructions: `INSTALL.md`.

The consequence that bites: **an installed plugin pins to its cached version.** Edits in
this working tree are invisible to it, and so are committed and pushed ones — a reinstall
at an unchanged version is a silent no-op that re-copies nothing, so the copy only moves
when the `version` does. Live authoring therefore runs through skills-dir mode — this repo self-hosts via one
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
- **A directory a packaged skill reaches by relative path gets a symlink under
  `skills/`, never a rewritten path.** `install-skills` reads its templates as
  `../install/bundles.md`, so `plugins/install-skills/skills/install ->
  ../../../install` is what keeps every one of those references byte-identical — live
  through the link in skills-dir mode, and dereferenced into the cache on install.
  Rewriting the paths instead would have worked in the working tree and broken every
  installed copy, since a cache copy has no repo root above it to reach back into.
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
