# ADR 0006 — A PRD's children are sub-issues, and its QA pass is a comment on it

- **Status**: Superseded by ADR 0009
- **Date**: 2026-07-31
- **Context**: PRD #73, implemented by #74–#81
- **Supersedes**: ADR 0005

## Context

ADR [0005](0005-qa-is-an-issue-not-a-committed-document.md) was right about what it was
solving, and it landed **the same day this record supersedes it** — nothing about it decayed.
It replaced a committed `docs/qa/prd-<n>.md` with a per-run tracker item, on two grounds that
both still hold. The two surviving documents run to 440 and 459 lines because the instruction
was *one section per completed issue*, so a dependency bump and a pure refactor each
contributed several lines of prose whose content was that there was nothing to test, and the
sections that mattered were buried among the ones that didn't. And a path keyed on the PRD
accumulates across runs, going stale with no signal telling the human which half is new.

**None of that is undone here.** The per-run shape survives, the earning rule survives, and
the nothing-testable rule survives — a landed child earns a step only if a human can exercise
it in the running app, and a run with nothing testable produces no artifact at all and says so
in both places the link would have gone. What changes is only *where the item lives*.

The reason is a fact 0005 could not have had, because the rest of PRD #73 established it:
GitHub's native **sub-issues** make a PRD render its children, and their completion state, on
the PRD's own page. A comment beneath that list is read next to the work it tests. A
standalone `[QA]` issue was orphaned **by construction** — deliberately given no `## Parent`,
no `ready-to-start` and no `state:*` label so that nothing could pick it as work — which is
precisely what left an operator unable to tell by eye which pass belonged to which PRD.

Sub-issues arrived to fix a different problem, and what that problem was belongs in this
record. Children were discovered by full-text search — `gh issue list --search 'in:body
"#<n>"'` — and the search does not do what its quoting suggests, because GitHub's tokenizer
drops the `#`. Measured on this repo: `in:body "#66"` returned closed, unrelated issue **#4**,
matching on the string `l.66–67`. Every PRD's candidate child set was one coincidental integer
away from a stranger, held back only by text filters over the results.

## Decision

**Three changes, and they are one decision because each removes the last defence the others
needed.**

1. **A PRD's children are native sub-issues.** `to-issues` and `triage-prd` write the link and
   verify it landed; `_shared/prd-eligibility.md` reads children back with a single call and
   applies **no filter at all**, because everything that endpoint returns is a child by
   construction.
2. **The QA pass is a comment on the PRD, plus a `needs-qa` label on it.** No `[QA]` issue is
   created on GitHub. The operator filters on `needs-qa` for one queue of PRDs awaiting a
   manual pass, and removes the label when the pass is done.
3. **The two trackers decouple.** `_shared/qa-item.md` is dissolved rather than edited: its
   GitHub rules fold into `work-on-prd`, its Azure DevOps rules into `ado-workflow`'s
   `skills/references/qa-item.md`. `work-on-spec` keeps its `[QA]` work item and its behaviour
   unchanged — only the location of the rules it reads moved.

0005 stated that *"the shared rules live in `_shared/qa-item.md`"*. That sentence is the one
line of it this record contradicts outright, and it is why a superseding record was owed.

## Consequences

**The most delicate rule in the workflow disappears with the `[QA]` issue.** 0005 recorded
that `prd-eligibility`'s title filter had to drop `[QA]` *unconditionally*, keyed on
`[TASK]`/`[BUG]` presence rather than on any bracket prefix, because a legacy PRD whose
children carried no prefix would otherwise have every genuine child dropped the moment one
`[QA]` issue existed. Its whole justification was cost asymmetry — picking a QA issue costs a
full worker run. No such issue is created now, and no filter keys on a title, so the rule and
the fallback defending it are both gone rather than merely relaxed. The title prefixes stay as
a human scanning convention and nothing more.

**The failure mode inverts, and that is the point.** A mis-linked child set used to fail
**silently and wrongly**: a wrong set of four looks exactly like a right set of four. Under
sub-issues it fails **loudly and emptily** — the PRD reports zero children, which `work-on-prd`
already handles explicitly, with a warning that specifically tells the operator to link rather
than re-slice, since re-slicing a PRD that already has children doubles every one of them.

**ADR [0004](0004-shared-reference-and-skill-dependencies.md)'s inventory changes; its rule
does not.** `_shared/qa-item.md` was that record's headline example of a document several
skills legitimately share. Dissolving it removes a row from 0004's table and costs it its
illustration, not its argument — `eligibility-policy.md` and its two tracker dialects are the
same case and remain live. 0004 stays `Accepted` and is amended, not superseded.

**The closable receipt is genuinely lost.** A closed `[QA]` issue was proof the pass had been
run; a comment has no closable state. Removing `needs-qa` is what "done" looks like now — a
human action nothing enforces. Accepted deliberately, and nothing was added to simulate the
receipt. It buys back the merge-survival hazard 0005 had to guard against: a comment cannot be
auto-closed by a `Closes` line, so the rule protecting the QA item from its own PR is gone too.

## Rejected alternatives

**Keep the `[QA]` issue and simply link it as a sub-issue of its PRD.** Tested, and it is
exactly why the issue is removed rather than merely left unlinked: a hand-linked `[QA]` issue
**does** come back in the sub-issues list. Linking it would put it straight back into the pick
path, forcing a filter to be re-invented under the one mechanism that otherwise needs none.
Leaving it unlinked instead preserves the orphan this record exists to end.

**Native issue dependencies for `## Blocked by`.** `gh` 2.94.0 ships `--blocked-by` /
`--blocking`, the same generation of feature as sub-issues, and the symmetry is tempting.
Deliberately left out. Enumerating a PRD's children is *input to* the eligibility question;
`## Blocked by` **is** the eligibility question, so getting it wrong picks the wrong work
rather than the wrong list. It earns its own change with its own verification instead of
riding along on this one, and the parsed text section stays untouched here.
