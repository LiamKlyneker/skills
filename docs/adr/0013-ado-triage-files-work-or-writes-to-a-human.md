# ADR 0013 — On Azure DevOps, triage either files work or writes to a human

- **Status**: Accepted
- **Date**: 2026-08-18
- **Context**: Observed on a live `ado-workflow` run — triaged findings sat on the board unworked
- **Supersedes**: nothing. **Narrows** ADR [0012](0012-the-qa-pass-is-composed-from-the-branch.md)'s
  ADO half by changing what `triage` emits, not how the pass is composed.

## Decision

`ado-workflow:triage` has **two outputs and only two**:

1. A finding that is **being fixed in this run** becomes a **`[TASK]`** under the same parent as the
   `[SPEC]`. It is eligible the moment it is written, so the next `work-on-spec` run picks it up
   with no promotion step.
2. **Everything else** — intentionally deferred, already planned, out of scope, rejected as
   works-as-designed / duplicate / invalid, or owned by another team — becomes **one human-readable
   comment on the parent work item**, and no work item anywhere.

`triage` no longer writes a `[BUG]`. It no longer files into a related repo. `[BUG]` stays
registered in the adapter as a **human** prefix, for work someone files by hand, and every
eligibility filter keeps dropping it.

The comment carries **no tracker plumbing**: no `[FINDINGS]` or `[SPEC]` reference, no finding or
flow numbers, no work-item ids, no skill names.

## Context

The previous shape filed every disposition as a `[BUG]`, in the adapter's pickable state, under the
same parent. Merge-blockers, deferred follow-ups and rejects all landed as work items; rejects were
filed and then immediately closed. The gate keeping them out of a run was the title prefix, and
promotion was a manual one-field retitle from `[BUG]` to `[TASK]`.

That design was ported from `prd-workflow:triage`, where it works. It did not survive contact with
the platform.

**GitHub has a label; Azure DevOps has nothing equivalent.** On GitHub a `deferred` label parks an
issue visibly without scheduling it — it is cheap, reversible, greppable, and invisible to the
eligibility filter. ADO offers no analogue a project can rely on. Everything the loop creates is
one work-item type under one parent, because Task → Task parenting is product-hostile and Bug-type
items are requirement-level. So the title prefix had to carry the schedule gate, and the prefix is
the item's name — the one field a human reads when scanning a board.

**The consequence was a board of items nobody was going to work.** Deferred findings, rejected
findings and closed-on-arrival duplicates accumulated as siblings of real tasks, indistinguishable
at a glance except by a bracket. And the fixes that *were* wanted still needed a manual retitle
before any run would touch them — so the common case cost a human action, and the uncommon case
cost board noise. Both halves were backwards.

**Underneath it was a category error.** A deferred finding is not a work item with the schedule bit
off. It is a *decision*, and its audience is a person — a product owner deciding whether it matters,
an engineer deciding whether to pick it up next quarter. A work item is an instruction for a worker.
Encoding a decision as an unscheduled instruction served neither reader: the worker never runs it,
and the human has to open it to find one sentence written in a robot's register.

**And that register leaked.** A `[BUG]` filed by triage pointed back at the `[FINDINGS]` item and
the `[SPEC]`, cited finding and flow numbers, and named the owning `[TASK]` by id. Every one of
those is a dead end for a product owner: an identifier they cannot interpret, attached to a document
written for a loop.

## Why this, rather than the alternatives

**Keep filing `[BUG]`s and change the eligibility filter to include them.** Rejected: it schedules
everything triage ever produced, including the findings the user explicitly declined and the
rejects. The prefix split existed to stop exactly that, and removing the split without removing the
filing makes the original problem worse rather than better.

**Keep the `[BUG]` prefix but file only the fixes as `[TASK]`.** Rejected as a half-measure — it
fixes the common case and leaves the board pollution intact. Deferred and rejected findings would
still land as items nobody works.

**Find an ADO analogue for the `deferred` label** — tags, a custom state, a separate area path.
Rejected: tags are the closest, and they are per-project configuration this repo cannot assume,
invisible on most board views, and would add a second thing the eligibility filter must read
alongside the prefix. The adapter would grow a row for something whose entire job is to say "a human
should read this" — which a comment already says, natively, to the right audience.

**One comment per finding rather than one per run.** Rejected: a run producing five deferred
findings would post five comments, which is the board-noise problem relocated to the discussion tab.
One write-up reads as a decision record; five read as a queue.

## Consequences

**Filing is now the schedule.** The user's confirmation at the card, and their approval of the filed
group at the board, are the only gate — nothing downstream asks again. `triage`'s first
non-negotiable (every filed item is cold-runnable) bites harder, because an under-specified `[TASK]`
reaches a worker on the next run instead of waiting for a human to notice it.

**The GitHub sibling does not move.** `prd-workflow:triage` keeps filing `deferred`-labelled issues
and filed-then-closed rejects, because the label makes that cheap and correct there. The two skills
were already siblings that arrived at a shape rather than a shared implementation
(ADR [0011](0011-azure-devops-qa-is-a-tickable-comment.md)'s surviving half), and this widens the
divergence deliberately. Do not port either direction.

**Contract-boundary findings stop being filed at all**, on either tracker's side of the boundary.
Filing into another team's repo from inside a QA pass created an item nobody here could close,
tracked by a local pointer nobody here would work. The comment describes what breaks and who owns
it; routing is a human act.

**Rejections survive as prose.** The reasoning that stops a false finding being re-investigated next
quarter now lives in the comment rather than a closed work item — a better home for it, since the
next person reads it without clicking anything.

**The comment is unparsed and unparseable, permanently.** Nothing reads it back, no skill matches on
it, and it has no template — only a required content shape and a tone rule. That is what lets it be
written for its reader. If a future change needs machine-readable state from a triage pass, it must
come from the work items or the findings item, never from this comment.

**Voice stays out of the plugin.** The skill specifies the outcome — plain, concrete, no jargon, no
ids — and deliberately names no writing skill to achieve it. `how-i-write` lives in `lk`; a
cross-plugin reference would silently produce nothing for anyone who installs `ado-workflow` without
it. Loading a voice skill at the moment of writing is the operator's call, and the content
requirements hold either way.
