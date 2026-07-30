# ADR 0001 — Version the plugins, and enforce the bump

- **Status**: Accepted
- **Date**: 2026-07-30
- **Context**: PRD #52, implemented by #57 (versions + catalog metadata) and #58 (the gate)
- **Reverses**: the omit-`version` decision recorded in `efa8f24` (PRD #16)

## The decision this reverses, in its own words

Until #57 every plugin manifest here deliberately had no `version`. That was not an
oversight, and `efa8f24` says so twice. The adapter's `## Commands` section read:

> **Not `--strict`**, deliberately. Plugin manifests here omit `version` on purpose —
> with a version set it becomes the install cache key, and a forgotten bump means
> installs silently never see changes.

and `INSTALL.md` carried it as Trap 2, "the single most-reported plugin footgun":

> **Set a `version` and it becomes the install cache key.** Forget to bump it and every
> install silently keeps serving the old copy — no error, no warning, just changes that
> never arrive.
>
> Omit the field and the cache key is the **git commit SHA** instead, which cannot be
> forgotten.

The accepted cost was a warning on every manifest, which is why the structural check
could not be `--strict`; the convention that came with it was that the missing-`version`
warning was the one warning allowed to pass.

**That reasoning was correct, and it was correct about a real mechanism, not a
theoretical one.** Two things measured on this branch confirm it:

1. **Reinstalling at an unchanged version is a silent no-op.** `claude plugin install`
   printed `✔ Plugin "install-skills@liamklyneker-dev" is already installed` and
   re-copied nothing. Only `claude plugin uninstall <name> --scope local` followed by a
   fresh install refreshed the cache. So a forgotten bump does not delay an update — it
   strands that consumer on stale files until they uninstall by hand.
2. **The two delivery routes visibly disagree.** After #57, `claude plugin list` showed
   `prd-workflow@skills-dir` at `1.0.0` (live off this working tree) while
   `prd-workflow@liamklyneker` still reported `81af34d0d5e1` from its pinned cache copy.
   Same repo, two answers.

A SHA key guarantees freshness with zero discipline. Nothing about that stopped being
true. The reversal is not "the old call was wrong".

## Why it was reversed anyway

Because the thing being distributed is a **public** marketplace of executable prose. A
`SKILL.md` edit changes what an agent does on a stranger's machine, and a commit SHA is
not a version number in any of the ways that matters:

1. **A consumer cannot tell what they have.** `Version: 81af34d0d5e1` answers no question
   anyone asks. "Which version of the PRD workflow am I running" has no answer, and
   neither does "is my copy newer than the one in the README".
2. **A consumer cannot pin.** There is nothing stable to pin *to* — a SHA is an identity,
   not a position in a sequence, so a consumer cannot say "stay here until I choose to
   move".
3. **A consumer cannot roll back.** Recovering from a bad change means finding a previous
   SHA of someone else's repo. There is no ordering to walk backwards along.
4. **The blast radius is a stranger's machine.** Prose here is what an agent executes, so
   an unannounced behavioural change to `work-on-prd` is a change to how somebody else's
   work gets committed. That is exactly the class of change a version exists to announce,
   and the SHA-keyed scheme has no way to announce anything.

Freshness-by-default bought (1)–(4) as its price. For a private set of symlinks that is a
good trade. For a published catalog it is not.

## What makes the reversal safe

**The bump-or-fail check** — `check_version_bumps()` in
`.github/scripts/validate_skills.py`, standard library only:

- Base ref comes from `--base <ref>` or `VALIDATE_BASE_REF`. **With no base ref that one
  check prints itself skipped and every other check still runs** — it never passes
  silently.
- The base is resolved to the **fork point** (`git merge-base`), not the base branch tip:
  commits the base branch gained after this branch left it are not this branch's changes
  to answer for.
- It diffs the base against the **working tree**, and adds untracked files, so an
  uncommitted edit already counts.
- A plugin that was absent at the base, or present but unversioned, is exempt.
- A failure names the plugin, the version it is still on, and which files changed.
- It also enforces that the manifest `version` and the `.claude-plugin/marketplace.json`
  entry **agree**. A bump that lands in only one of the two fails. This was added beyond
  what the issue asked for, because a drifted catalog is the same silent-staleness failure
  wearing a different hat: the catalog is what a consumer resolves against.

CI wiring, in `.github/workflows/validate.yml`: `fetch-depth: 0` (the fork point does not
exist in a depth-1 clone) and `VALIDATE_BASE_REF: ${{ github.event.pull_request.base.sha }}`.
The SHA-pinned checkout, `permissions: contents: read`, `persist-credentials: false` and
the `pull_request`-never-`pull_request_target` trigger are unchanged. On `push: [main]`
and `workflow_dispatch` the expression is empty and the check reports itself skipped,
which is correct — there is no base branch there to compare against.

**Without that check the reversal would be strictly worse than the status quo it
replaced.** The old key guaranteed freshness and asked nothing of the maintainer; a
version key plus a forgotten bump strands consumers indefinitely. The check is not a
convenience bolted onto the versions — it is the thing that lets the versions exist. Two
consequences follow, and both are load-bearing:

- **Never drop a `version` to silence a bump failure.** Dropping the version drops the
  check with it, and lands you in the strictly-worse quadrant rather than back at the old
  trade-off.
- **`--strict` became adoptable**, because the missing-`version` warning was the only
  warning there was. The adapter's manifest-check row is now `claude plugin validate
  --strict` across all five plugins plus the catalog, and **zero warnings is the bar**.
  The old "one warning is allowed" convention is dead — there is nothing left to wave
  through.

Both now-false passages in `.claude/project/adapter.md` were **rewritten, not deleted**.
The `## Repo discipline` bullet opens by saying it used to state the opposite, and that
the reason it gave has not stopped being true. Deleting them would have left the next
reader to rediscover the footgun the hard way.

## Consequences, including one that hurts

All five plugins carry `"version": "1.0.0"` — `prd-workflow`, `figma-tools`,
`ado-workflow`, `lk`, `install-skills` — mirrored into all five catalog entries, which
also gained `keywords` and `category` so the catalog is browsable.

**A change under `_shared/` or `install/` counts as a change to every plugin whose
`skills/` symlinks it.** Install dereferences the link into each cache copy, so the edit
genuinely does change what four or five plugins publish, while `git diff` only ever names
`_shared/…`. `plugin_pathspecs()` therefore walks each plugin's symlinks and folds their
targets into that plugin's contents. Demonstrated on this branch: editing
`_shared/ui-manifests.md` made the gate demand a bump from all four other plugins.

So one shared-doc edit costs five version bumps. That is real tedium and it is the honest
price of keeping one copy of a shared reference (ADR
[0004](0004-shared-reference-and-skill-dependencies.md)). It is accepted on one ground:
**tedium is recoverable and silent staleness is not.** The alternative failure — a
shared-doc change that ships to nobody, with a green build — has no symptom at all.

**No release tag exists.** `claude plugin tag` creates a `{name}--v{version}` git tag and
validates that `plugin.json` and the enclosing marketplace entry agree, but on this branch
it was exercised `--dry-run` only. `git tag` is empty. Tagging a release is a separate,
deliberate act, not a side effect of setting a version.

## Rejected alternatives

- **Changesets.** Rejected on a hard constraint rather than a preference: it wants a
  dependency manifest, and this repo takes none — `validate_skills.py` is standard
  library "by design — this repo has no dependency manifest and should not grow one", and
  `CLAUDE.md` says the same. Adding `package.json` and a lockfile to a prose repo to
  manage five version numbers inverts the cost. `claude plugin tag` already does the
  release half natively, including the manifest/catalog agreement check, so the gap
  changesets would fill is mostly already filled.
- **Keep omitting `version`.** This is the decision being reversed; see above. Its
  reasoning survives as the justification for the gate.
