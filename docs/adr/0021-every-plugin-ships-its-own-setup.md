# ADR 0021 — Every plugin ships its own setup

- **Status**: Accepted
- **Date**: 2026-10-27

## Context

The installer that writes a project's `.claude/project/adapter.md` shipped as its own plugin,
`install-skills`, with one skill of the same name. The reason was sound: `prd-workflow` and
`ado-workflow` cannot run without the adapter, so reaching the installer must not require
installing anything else, and it must not sit inside the personal `lk` plugin.

Two costs showed up in use on consumer projects:

- **The command read badly.** `/install-skills:install-skills install the missing qa section`
  says "install" three times, because a plugin namespaces its skills and the two names matched.
- **The command was not where a user looks for it.** A user who updates `qa` or `prd-workflow`
  thinks of setting up *that* plugin. The installer lived in a third plugin they had to
  remember, and had to install separately before any bundle was usable.

Moving the installer into `lk` would have shortened the name and broken the original reason:
a stranger who wants only the PRD loop would have had to install every personal skill to reach
it.

## Decision

**Every plugin with a bundle ships a `setup` skill, and all of them follow one installer.**

- The installer moves to the canonical `install/` directory: `setup.md` (the procedure),
  `interview.md` and `doctor.sh`. Every path in `setup.md` is relative to that directory.
- `prd-workflow`, `ado-workflow`, `figma-tools`, `lk` and `qa` each get
  `skills/install -> ../../../install`, the same packaging symlink `install-skills` already
  used, and a `skills/setup/SKILL.md` that holds only its plugin's bundle table and how to
  pick from it. A plugin with two bundles asks which, and runs the installer once per bundle.
- The `install-skills` plugin is deleted, not deprecated, and leaves the catalog.

The command becomes `/<plugin>:setup` — `/qa:setup`, `/prd-workflow:setup`.

## Why this does not fork the installer

The engine stays single. `setup.md`, `interview.md`, `doctor.sh` and `bundles.md` exist once,
and a plugin's `setup` skill carries no installer logic. Adding a bundle still means editing
`bundles.md`, plus one row in the owning plugin's `setup` table.

Several plugins writing one adapter is safe because the installer was already built for it:
against an adapter that exists it gap-fills the bundle's sections, never overwrites, never
deletes, and stops on a tracker conflict. Running `/qa:setup` after `/prd-workflow:setup` is
the "adapter exists but predates the bundle" case it always handled.

## Consequences

- A stranger installs one plugin and finds its setup inside it. The standalone-installer
  argument is met by every plugin rather than by a separate one.
- Every edit under `install/` now ships in five plugins, so the validator's version-bump
  rule asks for five bumps instead of one. That is the rule working, not a side effect: the
  symlink puts those files in each cache copy.
- `doctor.sh` resolves canonical as its own directory's parent, which is the repo root in a
  working tree and `skills/` in a cache copy; both contain `install/`.
- Consumers with `install-skills` installed keep a stale copy until they uninstall it. Their
  adapters stay valid; nothing in the adapter format changed.
- A plugin added later with a bundle needs a `setup` skill and the `skills/install` link. A
  plugin with no bundle needs neither.
