# ADR 0007 — This repo publishes a marketplace; it does not manage the estate

- **Status**: Accepted
- **Date**: 2026-08-01
- **Context**: the close-out of PRD #73, and the observation that a routine "is anything stale?" question sent a session reading three config directories before answering

## The reasoning this reverses, stated fairly

Watching the consuming config directories was correct, and for a long time it was the only
thing that worked.

Before ADR 0001 there was no `version` on any plugin manifest. An install was keyed by a git
commit SHA, the catalog asserted nothing a machine could check, and most of this repo's
content reached a machine as **hand-placed symlinks** — one per bare skill, per config, placed
by hand and recorded nowhere else. Under those conditions there was no derivation available:
the only way to know what `~/.claude-teamsnap` had was to open it and look.
`docs/estate-inventory.md` existed because that was true, and it prevented real failures — a
skill that silently was not there, a config running a copy two designs behind, an agent type
that resolved to `general-purpose` because nothing had been placed.

None of that was paranoia. It was the correct response to a distribution model with no
integrity check in it.

## What changed

Two things, and together they move the check from *observation* to *enforcement*:

- **ADR 0001** made `version` mandatory and made it the install cache key. A consumer's copy
  now pins to a number that this repo controls.
- **`.github/scripts/validate_skills.py --base <ref>`** fails the pull request when a plugin's
  content changes without its `version` moving, and when `plugin.json` and
  `.claude-plugin/marketplace.json` disagree. CI runs it on every PR.

So the property that used to require reading three directories — *"is what I published
coherent, and will a consumer who updates get the change?"* — is now checked here, at publish
time, on every change, by a gate that cannot be forgotten.

The plain-skill route that made the inventory load-bearing is also gone (#26). Every skill
ships inside a versioned plugin.

## Decision

**This repo's responsibility ends at publishing a correct, correctly-versioned catalog.**

- Correctness is a property of *this repo* — the manifests, the catalog, the bump rule — and
  is verified by the gate, not by looking at what any machine happens to have installed.
- **A stale or broken consumer is an ordinary bug**, diagnosed and fixed at the moment it
  surfaces, in the config where it surfaces. It is not a standing audit obligation, and no
  rule here directs a session to go looking for one pre-emptively.
- Liam's three config directories are **one consumer among the possible consumers**. They get
  no special standing in this repo's rules. Their arrangement is documented as an example of
  the mechanics, not as state this repo owes anyone.

## The one thing this does not relax

**The version bump rule gets stronger, not weaker** — it is now load-bearing rather than
merely tidy.

A missed bump does not surface as a bug. The consumer gets **old behaviour with no error**:
`claude plugin install` at an already-cached version prints `already installed` and re-copies
nothing, so the consumer is stranded until they `uninstall --scope local` by hand. Silent
staleness is not a bug that arrives and gets fixed; it sits.

That is precisely why the obligation belongs *here*. "We stop auditing consumers" is only a
defensible position because the thing that would strand them is caught before it ships. If the
bump rule ever weakens, this ADR should be revisited with it.

The edge worth remembering: a change under `_shared/` or `install/` counts as changing **every**
plugin whose `skills/` symlinks it, because install dereferences the link into each cache copy.

## Consequences

- The adapter's `## Sources of truth` no longer names *"the live config dirs"* as a source to
  read before making a distribution claim. The **plugin CLI** remains one — the platform has
  repeatedly differed from its own docs, and that is a fact about the platform, not about an
  estate.
- `docs/estate-inventory.md` is **demoted to a dated snapshot**. It is no longer updated in the
  same commit as a wiring change, and no rule in `CLAUDE.md` or the adapter requires it. It is
  personal notes that happen to be committed.
- `INSTALL.md` reads as *how anyone installs this marketplace*, with the three-config
  arrangement kept as a worked example of scope-by-tenancy rather than as the subject.

## Rejected alternatives

**Delete `docs/estate-inventory.md` outright.** Cleaner, and consistent with "we do not track
this". Rejected because the file is not only an inventory — it carries observed platform
behaviour that cost real time to learn (SHA-keyed installs from the unversioned era, which
scope suits which tenancy and why, the symlink-repo install refusal). Deleting the record to
express a change of posture would throw away the evidence with it. Demoting says the same
thing and keeps the findings; anything in it that is genuinely about the *platform* belongs in
`INSTALL.md` and can migrate there over time.

**Automate the audit — a `doctor` mode that scans every `~/.claude-*` sibling.** Rejected on
two grounds. It re-encodes the obligation this record removes, just in a script instead of a
sentence. And it cannot work: the `claude plugin` CLI ignores `CLAUDE_CONFIG_DIR` and always
reads `~/.claude`, so such a check would have to parse other configs' internal JSON by hand and
would break whenever the platform changed its layout — an unversioned dependency on a private
file format, maintained here, to answer a question nobody is required to ask.
