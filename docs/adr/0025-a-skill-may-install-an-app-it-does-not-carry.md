# ADR 0025 — A skill may install an app it does not carry

- **Status**: Accepted
- **Date**: 2026-11-05
- **Context**: the `figma-tools` skills `design-component` and `create-ui-component-lab`

## Context

This repo is prose. `CLAUDE.md` allows a skill one exception: a script, shipped **only when the
job is mechanical and must produce the same answer twice**. The validator is standard-library
Python, and the repo has no dependency manifest and no build. Everything a consumer installs is
text an agent reads, plus the few scripts that earned their place under that rule.

`design-component` needs something to render into. In a library repo it builds a proposed
component and shows it to the user with the library's real styles, so the user judges what they
see instead of answering one text question per ledger row. That something is the **UI component
lab**: a small app inside the library repo. The app is a few thousand lines. It was arrived at
through rounds of visual feedback, and it cannot be re-derived identically from a description —
two agents given the same description write two different apps, with two different entry
formats.

So the app has to exist somewhere as code, and that code is not prose.

## Decision

**The app lives in its own repository, and a skill in this repo installs it by copying files from
a pinned version.**

- The app is `https://github.com/LiamKlyneker/ui-component-lab`, with its own checks and its own
  version tags.
- `create-ui-component-lab` pins a tag **and** the commit SHA that tag must resolve to, and stops
  if the two disagree. It shallow-clones that pin to a temporary directory, copies files out, and
  runs nothing from the clone.
- The app separates a **generic part**, copied unchanged and replaced wholesale on upgrade, from
  **project wiring**, written once per library by the skill from reading the library and never
  overwritten by an upgrade. Entries belong to the library.
- The skill carries no app code. It carries only the method for wiring the app into a project,
  and it registers the lab in the adapter's `## Design system` → `UI component lab:` row.
- The app's **guide** is the contract. `design-component` reads the row and follows `guide:`; the
  lab owns its entry format, and the skill owns only the method.

## Rejected alternatives

**The app inside this repo.** It would keep everything in one place and one review. It breaks
prose-only outright: a dependency manifest and a build would land here, and the validator would
have to grow beyond the standard library to check them. Every fix to the app would also be a
content change to `figma-tools`, and so a plugin version bump, for code most consumers never run.

**The app inside the plugin's install cache.** The skill would copy it from its own directory,
with no fetch at all. But every consumer of `figma-tools` would receive a copy of the app with
every version, whether or not they have a library repo — and most do not.

**Regenerate the app from a description each time.** No code to host anywhere. But the result is
not reproducible: two installs produce two apps, and the guide and entry format that
`design-component` depends on would differ from one library to the next. A skill that follows a
guide needs the guide to be the same document wherever it runs.

**An npm dependency added to the library.** Versioning and updates come for free. But it edits the
library's package manifest, a tracked change a skill must not make, and it puts the lab into the
library's dependency graph and its consumers' installs.

## The limits

This record is not a general licence for skills to fetch code. The exception holds only within
these limits:

- **Pinned by SHA, never a branch.** A tag alone can move; the SHA it must resolve to cannot. A
  skill that follows a branch or "latest" installs something nobody reviewed.
- **Copy-only.** Nothing from the fetched tree executes — no install script, no build, no hook.
  The clone is a source of files and nothing else.
- **The app repo is public whenever the marketplace is.** A public skill must not depend on a
  private fetch, or it works only on the author's machine.
- **One contract file.** The app's guide is the only interface between the app and the skills.
  Neither side reaches into the other's internals, so either can change everything behind the
  guide without the other noticing.
- **The pin moves only with a plugin version bump.** The pin is skill content, so the validator's
  bump rule already covers it. That is what makes "which app version does this skill install"
  answerable from this repo's history alone.

## Consequences

- An app fix reaches users only when a skill release moves the pin. A fix merged in the app
  repo and not yet pinned here is invisible to every install.
- An upgrade replaces the generic part and leaves the wiring and the entries. An entry written
  against an older guide can lack fields the page has gained, which is why `design-component`
  brings an older entry up to the current guide on continue.
- A second kind of lab gets its own repository, its own installer skill and its own adapter row.
  That is why the row and the skill are named for their kind — `UI component lab:` and
  `create-ui-component-lab` — rather than for "the lab".
