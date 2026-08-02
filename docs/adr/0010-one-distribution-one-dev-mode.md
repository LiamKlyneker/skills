# ADR 0010 — One distribution, one dev mode

- **Status**: Accepted
- **Date**: 2026-08-02
- **Context**: an audit of the three consuming configs that spent most of its length on symlinks and SHA-keyed installs, and the observation that this keeps happening
- **Reverses**: ADR [0007](0007-a-marketplace-not-an-estate-manager.md)'s rejected alternative on `docs/estate-inventory.md`; retires ADR [0005](0005-qa-is-an-issue-not-a-committed-document.md)'s evidence files

## The reasoning this reverses, stated fairly

**Skills-dir mode was not a shortcut. For most of this repo's life it was the only route that
worked.**

Before the plugins existed there was nothing else: a skill reached a session because a symlink
put it in a `skills/` directory, and that was the whole mechanism. After the migration to
plugins it stayed useful for a different reason — an installed plugin is a *copy* keyed by
`version`, so an edit in the working tree is invisible to it, and a committed-and-pushed edit
is invisible too until the version moves. Authoring against a cache copy is authoring blind.
A symlink was the only thing that made an edit live.

`INSTALL.md §4` documented it, `CLAUDE.md` named it one of **two delivery routes**, and this
repo self-hosted `lk` and `prd-workflow` through it. All of that was correct given what the
platform offered, and it is why `doctor` grew a double-load scan: with two routes genuinely in
play, a skill really could load twice, and something had to say so.

## What changed

**`claude --plugin-dir` exists.** Verified on 2.1.220:

> `--plugin-dir <path>`  Load a plugin from a directory or .zip **for this session only**
> (repeatable: `--plugin-dir A --plugin-dir B.zip`)

It loads a plugin from the working tree with no cache copy, no install record, no version
bump, and it takes precedence over an installed copy for that session. Crucially it is
**session-scoped and branch-agnostic** — it does not care what `main` holds, so an unmerged
plugin change is testable without a merge and without a second clone.

That removes the premise the two-route doctrine rested on. Skills-dir mode existed because
there was no other way to load a plugin from a working tree. Now there is one, and it is a
supported flag rather than a shape the loader happens to accept.

Two supporting commands landed with it and belong in the same loop:

- `claude plugin validate <path>` — validates a plugin or a marketplace manifest **without
  installing**.
- `claude plugin tag [path]` — creates a `{name}--v{version}` git tag, *validating that
  `plugin.json` and the enclosing marketplace entry agree*. That is ADR
  [0001](0001-version-the-plugins-and-enforce-the-bump.md)'s bump rule, enforced by the
  platform instead of only by our own CI script.

## Prior art, since it is unusually unanimous

Every comparable ecosystem separates a **load-from-working-directory dev mode** from the
**distribution path**, and treats them as different things rather than as alternatives:

| Ecosystem | Dev mode | Distribution |
|---|---|---|
| VS Code extensions | `--extensionDevelopmentPath` | Marketplace |
| Chrome extensions | "Load unpacked" | Web Store |
| Terraform providers | `dev_overrides` | Registry |
| Homebrew | local tap build | Bottles |
| Claude Code | `--plugin-dir` | Marketplace |

The npm ecosystem reached the same place from the opposite direction. `npm link` is not
condemned as a concept — Vite and Vitest still use links and `pnpm overrides` for their inner
loop — but it is considered an anti-pattern *as pre-publish verification*, because symlinked
resolution diverges from a real install in ways that only surface after publish. Verification
moved onto things that produce the real artifact: `npm pack`, `yalc`, and now per-commit
preview registries like `pkg.pr.new`, which Vite, Vitest, Rollup, Vue and Nuxt all publish to
from CI.

The error was never "we used symlinks". It was **describing the dev mechanism and the
distribution mechanism as two routes to the same end**, which invites the reader to pick one.

## Decision

**The marketplace is the only way a skill reaches a machine. `--plugin-dir` is the only way a
skill is authored. They are not alternatives and are never presented as a choice.**

- **Delivery** is a versioned plugin installed from `.claude-plugin/marketplace.json`. There is
  no second route, no supported fallback, and no documented alternative.
- **Authoring** is `claude --plugin-dir plugins/<name>` from this repo's root. Session-scoped,
  branch-agnostic, leaves nothing behind.
- **Pre-publish verification** is `claude plugin validate` plus
  `.github/scripts/validate_skills.py`, and release is `claude plugin tag`.

### The distinction that has to survive

Two unrelated things are both called "symlink" in this repo, and collapsing them is how this
decision would get misread into breaking the build:

- **Delivery symlinks** — a link into a `.claude/skills/` directory that makes a plugin load.
  **This is what is abolished.** None exist here any more.
- **Packaging symlinks** — `plugins/*/skills/_shared → ../../../_shared`,
  `plugins/install-skills/skills/install → ../../../install`, and `figma-to-spec`'s agent link.
  These are **build mechanics**: install dereferences them into each cache copy, which is what
  keeps `../_shared/x.md` byte-identical across every route. They are enforced by
  `validate_skills.py`, they are the subject of ADR
  [0004](0004-shared-reference-and-skill-dependencies.md), and **they stay**.

A rule that says "no symlinks" is wrong. The rule is *no symlink decides whether a skill
loads*.

## Consequences

- **`CLAUDE.md`'s "Two delivery routes" section is gone**, along with `INSTALL.md §4`. The
  replacement describes one distribution and one dev mode, and explains packaging symlinks
  once so nobody deletes them.
- **`doctor` loses the double-load scan, `FORK` detection, and skills-dir-root handling.** With
  one route there is no second copy for a skill to load from, so the scan's whole subject no
  longer exists. Worth noting: that scan walked `~/.claude*/skills/` and parsed other configs'
  internal JSON by hand — which is, almost exactly, the automated estate audit ADR 0007
  **rejected**. It was rejected in prose and shipped in code. Removing it makes the executable
  agree with the record.
- **The validator gains the inverse rule.** `check_symlinks()` now fails on any symlink under
  `.claude/skills/` pointing into `plugins/`. Doctrine that only lives in prose comes back by
  habit; this one is a gate.
- **`docs/estate-inventory.md` is deleted**, reversing ADR 0007's rejected alternative. That
  record kept it because it carried observed platform behaviour worth preserving — a fair
  reason, and the reason it survived demotion. What has changed is that the behaviour worth
  keeping is *platform* behaviour, which belongs in `INSTALL.md`, and everything else in the
  file was a dated description of three config directories written in the vocabulary this
  record retires. Keeping it meant every future audit started by reading it.
- **`docs/qa/prd-16.md` and `docs/qa/prd-52.md` are deleted.** ADR 0005 kept them as its
  evidence. They are retired here because the thing they evidence — a 440-line committed QA
  document produced by a loop that no longer produces one — is now two supersessions old, and
  33 of their lines describe the pre-plugin symlink world as current fact. Evidence for a
  decision nobody is relitigating is not worth the search hits it generates.
- **`figma-component/` and `tokens-init/` are deleted**, being deprecated, superseded by
  `figma-to-spec`, installed nowhere, and the last two top-level plain skills. The top level now
  matches what `CLAUDE.md` has claimed since #26.

## Rejected alternatives

**Pure dogfood — install `lk` and `prd-workflow` from the GitHub marketplace and author against
that.** Maximally honest, zero mechanism to explain, and genuinely tempting. Rejected on a hard
fact: a `github` marketplace source resolves the repository's **default branch** when no `ref`
is given, and this repo requires branch-and-PR. Authoring that way means every experiment
reaches `main` before it can be run once — shipping skill changes you could not test. A `ref`
can pin a marketplace to a branch, which softens this, but it makes every iteration a config
edit. `--plugin-dir` is strictly better for the same goal.

**A local-directory marketplace (`liamklyneker-dev`).** Symlink-free, a real install, exercises
namespacing and agent registration. Rejected as the *primary* loop because the marketplace name
is committed as `liamklyneker`, so avoiding a registry collision needs a second clone carrying a
permanent uncommitted edit, and the refresh cycle is uninstall → install → restart. It remains
the right tool for one narrow job — testing **install mechanics** themselves, where the cache
copy is the thing under test — and `INSTALL.md` keeps it at that scope.

**Keep the two self-host symlinks, demoted to a documented build detail.** The cheapest option,
and it preserves the fastest loop. Rejected because it preserves exactly the artifact that
causes the problem: a session that runs `ls .claude/` finds a symlink and asks about it, and
with the surrounding doctrine deleted there is *less* written down to answer with, not more.
The mechanism was only ever worth its explanation when nothing else could do the job.
