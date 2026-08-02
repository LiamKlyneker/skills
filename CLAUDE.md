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
- `docs/` — `adr/`, and nothing else. Documentation for humans; no session loads it.
- `_shared/` — **global reference only.** Docs several skills read, true in every
  project: `model-effort-heuristics.md`, `eligibility-policy.md`, `prd-eligibility.md`,
  `ado-eligibility.md`, `ado-workitem-authoring.md`,
  `spec-splitting-seams.md`, `ui-manifests.md`, `ui-standard.md`. No templates, no project
  values, ever.
- `install/` — what a project gets wired with: `bundles.md` (the manifest the
  `install-skills` skill reads), `adapter.template.md`, and `gates/`. See
  `install/README.md` for the layout a wired project ends up with. Canonical copy,
  reached from inside the plugin by a packaging symlink — see below.

Two shapes were deleted rather than deprecated, and the validator now fails on both: the
migration's compat shims (top-level names that were **symlinks into `plugins/`**, #26,
along with the nested `work-on-prd/agents/prd-worker.md` link), and the self-host links
under `.claude/skills/` that used to make this repo load its own plugins live (ADR 0010).
Either one makes a skill reachable by a route the marketplace does not control. Don't
reintroduce them; author with `--plugin-dir` instead.

**What consumes this repo is not this repo's business.** It publishes a versioned
marketplace; whether a given machine has installed it, and at what version, is that
machine's concern. Don't read `~/.claude*` to answer a question about this repo and don't
audit consumers pre-emptively — a stale or broken install is an ordinary bug, fixed where
and when it surfaces. What *is* this repo's business is that the catalog is coherent and
every content change moves its plugin's `version`, because a missed bump strands a
consumer silently. ADR [0007](docs/adr/0007-a-marketplace-not-an-estate-manager.md) has
the argument, including why that one rule gets stricter rather than looser.

**A plugin namespaces everything it provides.** Skills invoke as
`prd-workflow:work-on-prd` and agents resolve as `subagent_type: prd-workflow:prd-worker`
— always, on every route, including `--plugin-dir`. There are no bare names left; the
plain-skill route that produced them is gone. Getting an agent type wrong does **not**
error — it degrades silently to `general-purpose` — so a successful run is never evidence
that the type resolved. Read the type name in a fresh session.

`install-skills` is **its own plugin**, at `plugins/install-skills/` — not a plain
skill and not part of a personal bundle. It is the one thing here a stranger needs,
because `prd-workflow` and `ado-workflow` cannot run without the adapter it writes, so
reaching it must not require installing anything else. It is also the only skill in the
repo that ships an executable
(`plugins/install-skills/skills/install-skills/scripts/doctor.sh`) — the mechanical
checks have to be deterministic, and a check that gets paraphrased differently on each
run isn't one. Everything else here stays prose.

`INSTALL.md` is the guide for getting any of it onto a machine — marketplace, config
directories, scopes, the dev mode, and the traps. Keep it accurate; it is written
from observed platform behaviour, and the platform has repeatedly differed from its
own docs.

## QA lands differently per tracker, and titles are only a scanning convention

Both orchestrators still **commit nothing** for QA, and the adapter names no QA path on either
tracker — but the artifact itself has diverged, deliberately. `work-on-prd` posts the run's QA
steps as a **comment on the PRD issue** and labels the PRD **`needs-qa`**; the human works the
comment and removes the label when the pass is done. **No `[QA]` issue is created on GitHub.**
The GitHub chain from there is `manual-qa` → `triage`, both in `prd-workflow` and neither in
`lk` — a skill that parses the loop's own template belongs in the plugin that writes it, ADR
[0008](docs/adr/0008-prd-qa-skills-belong-to-prd-workflow.md): `manual-qa`
takes a PRD URL, drives that comment's steps one at a time, ticks each box as the human
confirms it, and posts a `### [FINDING]` comment to the PR for each failure; `triage`
promotes the survivors into children. **That marker is a parse contract, not a title prefix** —
it is hardcoded in both skills and deliberately absent from the adapter, because a project free
to edit it would get a triage pass that silently finds nothing. The tick state in the comment is
the only record a pass happened; neither skill writes a session log, and only a human removes
`needs-qa`. `work-on-spec` still files a per-run **`[QA]` work item** on Azure DevOps, with no
driver on that side. Each loop owns the
whole shape of its own artifact — `work-on-prd`'s `## Loop end` for GitHub,
`plugins/ado-workflow/skills/references/qa-item.md` for ADO. There was a shared
`_shared/qa-item.md`; it was dissolved into those two, and they are now free to differ. The
reasoning for moving QA out of the repo at all is ADR
[0005](docs/adr/0005-qa-is-an-issue-not-a-committed-document.md) — whose two 440-line
evidence documents under `docs/qa/` were retired by ADR
[0010](docs/adr/0010-one-distribution-one-dev-mode.md), two supersessions after the loop
stopped producing them. The reasoning for the comment
being a **contract** rather than prose — its load-bearing literals, the second never-edit
carve-out, and "all boxes ticked, no failure suffix, label removed" as the receipt — is ADR
[0009](docs/adr/0009-the-qa-comment-is-a-parse-contract.md), which supersedes ADR 0006 **on the
QA half only**: a PRD's children are still native sub-issues.

GitHub titles carry `[PRD]` · `[TASK]` · `[BUG]`, registered in the adapter's `## Repo` →
*Title prefixes* row, never hardcoded in a skill. **They are a human scanning convention and
nothing more — no skill filters on them.** A PRD's children are its **native GitHub
sub-issues**, read back from the sub-issues API (`_shared/prd-eligibility.md`), so an unprefixed
issue linked to a PRD is a full child while a perfectly prefixed one that was never linked is
invisible. The one place a prefix is still mechanical is `work-on-prd` stripping a leading
`[…]` group before slugging the branch. Don't reintroduce a title filter, and don't write a body
`## Parent` section to stand alongside the link — two sources of truth that can disagree is
exactly what the links removed.

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

## One distribution, one dev mode

**A skill reaches a machine exactly one way: as a versioned plugin installed from the
marketplace.** There is no second route, no supported fallback, and no alternative worth
describing. Full instructions: `INSTALL.md`. The argument, and why the old second route was
right until it wasn't, is ADR
[0010](docs/adr/0010-one-distribution-one-dev-mode.md).

**Authoring is `--plugin-dir`.** An installed plugin is a *copy* keyed by `version`, so
edits in this working tree are invisible to it — and so are committed and pushed ones,
because a reinstall at an unchanged version is a silent no-op. So don't author against an
install. Load the working tree directly:

```bash
# from this repo's root — repeatable, session-scoped, works on any branch
claude --plugin-dir plugins/lk --plugin-dir plugins/prd-workflow
```

Nothing is copied, nothing is recorded, and the loaded copy takes precedence over an
installed one for that session. Before opening a PR, `claude plugin validate <path>` checks
a plugin or the marketplace manifest without installing anything; `claude plugin tag`
creates the release tag and fails if `plugin.json` and the catalog entry disagree.

**Two different things are called "symlink" here, and only one of them is abolished.**

- **Delivery symlinks** — a link into a `.claude/skills/` directory that makes a plugin
  load. **Gone, and the validator fails on them.** That includes this repo's own former
  self-host links.
- **Packaging symlinks** — `plugins/*/skills/_shared -> ../../../_shared`,
  `plugins/install-skills/skills/install -> ../../../install`, and `figma-to-spec`'s agent
  link. **These are build mechanics and they stay.** Install dereferences them into each
  cache copy, which is the whole reason a relative reference resolves identically from a
  working tree and from a cache directory.

The rule is not "no symlinks". It is *no symlink decides whether a skill loads*.

Rules that follow from this:

- A relative `../_shared/…` inside a skill resolves to this repo's global reference.
  That is unambiguous **because no project owns a `_shared/`** — project facts live in
  `<repo-root>/.claude/project/` instead. Inside a plugin the reference is
  `skills/_shared`, a symlink to the same canonical directory, dereferenced into the
  install cache; that copy is a regenerated build artifact, not a fork. Don't
  reintroduce a project-side `_shared/`, and don't add "you may have resolved the
  wrong file" warnings back to the skills; the layout is what makes them unnecessary.
- **A directory a packaged skill reaches by relative path gets a packaging symlink under
  `skills/`, never a rewritten path.** `install-skills` reads its templates as
  `../install/bundles.md`, so `plugins/install-skills/skills/install ->
  ../../../install` is what keeps every one of those references byte-identical — live
  through the link under `--plugin-dir`, and dereferenced into the cache on install.
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
- Adding a skill means adding the directory under `plugins/<plugin>/skills/` — nothing
  else; the plugin's inventory is discovered, not listed. There is no other kind of skill
  to add. It is reachable under `--plugin-dir` immediately, and reaches a consumer when
  the plugin's `version` moves and they update.
