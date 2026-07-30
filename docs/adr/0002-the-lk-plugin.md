# ADR 0002 — The `lk` plugin, and why `install-skills` is not in it

- **Status**: Accepted
- **Date**: 2026-07-30
- **Context**: PRD #52, implemented by #62 (`lk`) and #53 (`install-skills` as its own plugin)

## Context

Seven skills lived at the repo root as plain skills, which means the only way to deliver
them was one hand-placed symlink per skill per config directory — around fifteen links
across `~/.claude`, `~/.claude-teamsnap` and `~/.claude-schmiede`. Nothing derives that
state and nothing validates it, which is why `docs/estate-inventory.md` has to exist and
be edited by hand in the same commit as the wiring.

## Decision

`plugins/lk/` ships seven skills: `grill`, `deep-grill`, `pinpoint`, `how-i-write`,
`qa-prd-log`, `triage-prd`, `scoped-context`. Same shape as every other plugin here — a
`.claude-plugin/plugin.json`, a `README.md`, a `skills/_shared` symlink to the canonical
global reference, and an inventory **discovered** from the directory.

The criterion that selects those seven, and it is the whole argument: **they talk to the
user and to the codebase, rather than to a tracker.** A grill interviews a person.
`pinpoint` searches a repo. `how-i-write` drafts prose. `scoped-context` reads a
`CONTEXT.md` before an edit.

That is precisely why they must not belong to a tracker-bound workflow plugin. Folding
them into `prd-workflow` would make a skill that has nothing to do with GitHub arrive
only with GitHub, and `ado-workflow` — the same workflow over Azure DevOps — would then
need its own copies of skills that are identical because they never touch a tracker at
all. `lk` is the home for the tracker-independent half, so the two workflow plugins stay
exactly their workflows.

Two of the seven, `qa-prd-log` and `triage-prd`, *do* write to GitHub. They are still here
because they are PRD-QA skills bound to Liam's own loop rather than components of the
workflow plugin, and because the isolation they need is enforced by invocation rather than
by which plugin they sit in — see ADR [0003](0003-invocation-policy.md).

## The short name is load-bearing

A plugin namespaces every component it provides, so the name is spent on every invocation
for the lifetime of the plugin. `/lk:grill` is typeable enough to stay a daily driver;
`/personal-skills:grill` or `/liam-skills:grill` is the kind of thing that quietly stops
getting used. Two characters of prefix is what makes a namespaced everyday skill livable,
and that is the entire reason the plugin is not named descriptively.

`grill-me` was renamed to `grill` inside the same commit as the packaging — directory,
frontmatter `name`, and the description's invocation, which became `/lk:grill`. Renaming
and repackaging together breaks muscle memory once instead of twice.

**A corrected observation, recorded because the correction matters more than the claim.**
PRD #52's namespacing decision stated that "a bare `/grill` is unreachable from any
plugin; that is the accepted cost of packaging." **That is false**, verified against the
binary during this PRD: a bare `/deep-grill` resolved, and the session echoed it back as
`/lk:deep-grill` — the platform resolves an unambiguous bare name *to* the namespaced
skill. Control probes in the same batch returned `Unknown command` for `/grill-me` and
`/nonsense-xyz`, so the resolution was real and not an artefact of a forgiving parser.

No decision changes. `/lk:grill` remains canonical, and the short-name argument above
stands on typeability, not on reachability. But **do not restate the unreachability
claim** — this repo's standing rule is that distribution claims get verified against the
binary and the live config dirs rather than written from memory or from platform docs, and
this claim is what that rule is for.

## `install-skills` is its own plugin, not part of `lk`

`plugins/install-skills/` is a separate catalog entry holding a single skill. It was not
folded into `lk` for one reason: **it is the only thing in this repo a stranger needs.**
`prd-workflow` and `ado-workflow` cannot run without the adapter it writes, so reaching
the bootstrapper must not require installing somebody else's personal bundle. It is also
the only skill in the repo that ships an executable —
`plugins/install-skills/skills/install-skills/scripts/doctor.sh` — because mechanical
checks have to be deterministic, and everything else here stays prose.

**A general rule came out of that move, and it generalises the `_shared` pattern.**
`install-skills` reads its templates by relative path (`../install/bundles.md`, seven
references in all), and `doctor.sh` reaches the same tree by inferring `<script>/../..`.
Under the old top-level layout both landed on the repo root's `install/`. From
`plugins/install-skills/skills/install-skills/` they would land on a directory that does
not exist — and a plugin **cache copy has no repo root above it at all**. So #53 added a
*second* symlinked directory inside `skills/`:

```
plugins/install-skills/skills/install -> ../../../install
```

which keeps all seven references byte-identical and needed no edit to `doctor.sh`. The
rule, now stated in `CLAUDE.md`: **a directory a packaged skill reaches by relative path
gets a symlink under `skills/`, never a rewritten path.** Rewriting the paths would have
worked perfectly in this working tree and broken every installed copy — the failure mode
being an installer that refuses every bundle and a doctor that silently loses its
templates. `install/` stays at the repo root as the canonical copy, exactly as `_shared/`
does.

## Rejected alternative: a `skills` array in the manifest

`mattpocock/skills` lists its skills explicitly in its manifest. Rejected here on two
grounds:

- It contradicts this repo's **discovered-not-listed** rule. A plugin's skills and agents
  are discovered from `skills/` and `agents/`; adding a skill to a plugin is just adding
  the directory. A listed inventory is a second place to forget, and a forgotten entry
  produces a skill that exists in the repo and ships to nobody.
- It would leave one plugin shaped unlike the other four. The consistency is what lets a
  single rule in `CLAUDE.md` describe all five, and lets `validate_skills.py` check them
  with one code path.

## Consequences

- The plugin exists, but the estate has **not** been cut over yet: #61 adds
  `.claude/skills/lk -> ../../plugins/lk` and retires the config-level links to all seven.
  Until it lands, `docs/estate-inventory.md` still describes the symlink route as live for
  these skills.
- This repo's own `.claude/skills/deep-grill -> ../../deep-grill` link died with the move
  and was removed in #62 rather than left dangling for the validator to reject.
- `install/adapter.template.md`'s `## Sources of truth` section belongs to the grills, not
  to a workflow, so #56 gave it a `grill` bundle of its own — a bundle named after two of
  `lk`'s seven skills rather than after the plugin, since a bundle is a set of adapter
  sections and not a package.
