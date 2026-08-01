# ADR 0008 — The PRD-QA skills belong to `prd-workflow`, not to `lk`

- **Status**: Accepted
- **Date**: 2026-08-01
- **Context**: PRD #85, implemented by #88 (the relocation) and #89 (`manual-qa`)
- **Supersedes**: ADR 0002

## Context

ADR [0002](0002-the-lk-plugin.md)'s criterion is **correct and unchanged**, and it is the
reason the five remaining skills stay exactly where they are: **they talk to the user and to
the codebase, rather than to a tracker.** A grill interviews a person. `pinpoint` searches a
repo. `how-i-write` drafts prose. `scoped-context` reads a `CONTEXT.md` before an edit. Folding
those into `prd-workflow` would make a skill that has nothing to do with GitHub arrive only
with GitHub, and `ado-workflow` would then need its own copies of skills that are identical
precisely because they never touch a tracker at all. None of that is disturbed here.

0002 then granted one exception, in its own words:

> Two of the seven, `qa-prd-log` and `triage-prd`, *do* write to GitHub. They are still here
> because they are PRD-QA skills bound to Liam's own loop rather than components of the
> workflow plugin, and because the isolation they need is enforced by invocation rather than
> by which plugin they sit in.

That was a reasonable reading at the time. Both skills were end-of-loop tools a human typed
after a run, neither read anything the loop had written down as a contract, and the thing that
made them safe — invocation — genuinely is orthogonal to packaging (ADR
[0003](0003-invocation-policy.md)). The exception cost nothing while it was true.

## Decision

**`lk` becomes exactly its stated criterion, with no carve-out.** `qa-prd-log` is deleted,
`triage-prd` moves into `plugins/prd-workflow/`, and `manual-qa` is born there. `lk` ships five
skills, every one of which talks to a person or a repo and to no tracker.

The argument has two halves, and the decision needs both.

### The parse contract is cross-plugin, and it was already live

`triage-prd` already identified a QA comment by two markers lifted from `work-on-prd`'s
template, and `manual-qa` now parses that template far more deeply — the step anchor, checkbox
state, the `<!-- 75 80 -->` id trailers, the outstanding-pass first line. Those literals are
enumerated in `work-on-prd`'s `## Loop end` with the instruction to change them in all three
places at once.

Two **independently-versioned plugins** with a string contract between them and nothing
checking compatibility is the stranding failure ADRs
[0001](0001-version-the-plugins-and-enforce-the-bump.md) and
[0007](0007-a-marketplace-not-an-estate-manager.md) exist to police: a consumer who updates
`prd-workflow` and not `lk` gets a triage pass reading a template nobody promised it.
This was not hypothetical. #84 rewrote the comment template — headings, hidden ids, checkboxes —
and `work-on-prd` still claimed no skill parsed the comment while a skill in another plugin
did. The shape was load-bearing and documented as convention, across a version boundary.

Inside one plugin the boundary is gone: writer and both readers ship together, at one version,
and the catalog gate fails a change to any of them that does not move it.

### The ADO objection cannot apply to these two

0002's strongest argument against a tracker-bound home was duplication — `ado-workflow` would
need its own copies. It cannot, here, because the driver is **GitHub-only by construction**:

- `plugins/ado-workflow/skills/references/qa-item.md` is prose sections with **no checkboxes**.
  There is no tick-able state to drive, and it says outright that no skill parses it.
- ADO access is **MCP-only**, by deliberate decision
  (`plugins/ado-workflow/skills/references/ado-mcp-setup.md`).
- `wit_work_item_write` (`action: "update"`) has **no `format` option and falls back to HTML**,
  so editing a description is a destructive rewrite of the whole field rather than the
  single-line append `manual-qa` depends on.

No tick-able state, no safe append, nothing to parse — so there is nothing for `ado-workflow` to
copy, now or later. If ADO ever grows a driver it will be a different skill answering to a
different artifact, not a port of this one.

## What this record does not change

- **ADR 0003 is untouched.** `manual-qa` and `triage-prd` both carry
  `disable-model-invocation: true`. Invocation is still the isolation boundary; it simply
  stopped being a reason to *override* the plugin criterion. 0003's table still lists
  `qa-prd-log`, a skill this PRD deleted; `manual-qa` takes that row's place under the same
  clause for the same reason — it writes findings as comments on a PR. Its **inventory** ages,
  its **rule** does not: 0003 stays `Accepted`, amended here rather than superseded or edited.
- **The rest of 0002 stands.** The short-name argument, the corrected bare-name observation,
  `install-skills` being its own plugin, the symlink-not-rewritten-path rule, and the rejected
  `skills` array in the manifest are all untouched. This record supersedes 0002 **on plugin
  membership only** — the convention supersedes a record whole, so that limit is stated here
  rather than left to inference.
- **Duplicating a skill across plugins was never on the table** as an alternative to moving
  one. ADR [0004](0004-shared-reference-and-skill-dependencies.md) already settles it: `_shared/`
  files are shared, skills are not.

## Consequences

- **`lk` maps to one bundle rather than two.** `prd-qa` moves with the skills, and the standing
  proof that a bundle and a plugin are different namespaces now comes from the `prd-workflow`
  side: `prd-qa` is two skills inside a plugin that is *also* named after a different bundle, so
  `prd-workflow` answers to two bundles while being neither of them.
- **Three plugin versions moved, not two.** `install/bundles.md` sits inside `install-skills`'
  installed copy via its `skills/install` symlink, so editing it counts as changing that plugin
  — correctly, since an un-bumped consumer would keep a `bundles.md` still claiming `prd-qa`
  lives in `lk`.
- `/lk:triage-prd` is now `/prd-workflow:triage-prd`. Muscle memory breaks once, in the same
  commit as the deletion, rather than twice.
