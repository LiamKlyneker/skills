# ADR 0012 — The QA pass is composed from the branch, not planned into a contract

- **Status**: Accepted
- **Date**: 2026-08-17
- **Context**: PRD #140, implemented by #141–#145
- **Supersedes**: ADR 0009 and ADR 0011, **on the QA-artifact half of each only**

## Read this first: what still stands in 0009 and 0011

The convention supersedes a record whole, so the `Superseded by ADR 0012` lines now sitting on
ADR [0009](0009-the-qa-comment-is-a-parse-contract.md) and ADR
[0011](0011-azure-devops-qa-is-a-tickable-comment.md) would otherwise read as re-opening
everything either record decided. They do not. Two halves survive, and this record depends on
both.

**0009's sub-issues half is untouched.** A PRD's children are still its **native GitHub
sub-issues** — `to-issues` and `triage` write the link and verify it landed,
`_shared/prd-eligibility.md` reads them back with one call and applies no filter, and a
mis-linked PRD still reports zero children rather than a plausible wrong four. 0009 inherited
that half from ADR [0006](0006-sub-issues-and-qa-as-a-prd-comment.md) and passed it on
unchanged; so does this record. Nothing here touches how children are enumerated on either
tracker.

**0011's plugin-membership half is untouched, and is the rule this record keeps applying.**
`manual-qa` and `triage` stay in `prd-workflow` and `ado-workflow` respectively — the ADO pair
where `work-on-spec` lives, the GitHub pair where `work-on-prd` lives. 0011 inherited that rule
from ADR [0008](0008-prd-qa-skills-belong-to-prd-workflow.md), whose stated reason was that the
writer and readers of a parse contract must ship in one version-bumped plugin. **The contract is
gone and the membership rule is not**, because the two skills still share literals with their
loop — `### [FINDING]`, `[FINDINGS]`, `PRD: #<n>` — and a QA driver that files issues was never
an `lk` skill on the other criterion either. `lk` stays at its stated criterion with no
carve-out; nothing moves plugins here.

Also untouched: ADR [0005](0005-qa-is-an-issue-not-a-committed-document.md)'s decision that the
QA pass is **not a committed document**. Both loops still commit nothing for QA, and both QA
drivers still write only to the tracker.

What is superseded is the artifact itself: 0009's *"the QA comment is a parse contract"* and
0011's port of that conclusion onto Azure DevOps, along with everything downstream of it — the
templates, the anchors, the id trailers, the never-edit rule and its carve-outs, and *all boxes
ticked, no failure suffix, label removed* as the receipt.

## The losing reasoning, stated fairly

0009 was right about the thing it was arguing. A template with two parsers reading it **is** a
contract, and pretending otherwise is how #84 rewrote that template while `triage-prd` went on
matching a marker that no longer existed and reporting clean PRs. Writing the five literals
down, naming which skill parses each, and instructing that they change in three places together
was the correct response to the failure that had actually happened. 0011 then measured the
Azure DevOps half against a live fixture rather than the docs, and got the platform facts right
where 0008 had guessed — checkboxes really do tick, `wit_work_item_comment_write` really does
take `format: "Markdown"`, and the sanitiser really does eat raw markup on the read path. None
of that was careless, and none of it is being reversed on the grounds that it was wrong.

It is being reversed on a defect neither record could see from where it stood, because both were
reasoning about the comment's **shape** and the defect is in the comment's **origin**.

## The defect: the pass was written before the code existed

`work-on-prd` and `work-on-spec` composed the QA pass at loop end, from the workers' refined
`## QA notes` — which each worker refined from the notes the planner wrote into the child before
a line of the slice was implemented. Every arrow points backwards. The artifact a human worked
was a **plan for what the run intended to make testable**, hardened into a contract, posted, and
then never allowed to change because the never-edit rule protected it from exactly the correction
it needed.

Three consequences followed, and all three were visible in practice:

- **Steps described work as specified, not as built.** A slice that deviated — and the worker
  report contract has a whole *deviation log* section because slices deviate — produced steps
  that tested the deviation's absence.
- **The seams between slices went untested.** Steps were per-child by construction, so the
  place two children meet, which is where a run breaks, belonged to no step.
- **The contract's cost bought nothing back.** Anchors, trailers, escaped angle brackets and
  read-modify-write discipline all exist so a machine can tick a box. The machine was ticking
  boxes in a document whose content it could not question.

## The decision

**The QA pass is composed on demand, in the QA session, from what actually landed.** `manual-qa`
— on both trackers, as siblings — finds the run's pull request, reads the branch diff, the
commit list and the landed children, and lays the pass out as a short list of **flows**: a name,
an explicit `start from:` line, numbered sub-steps naming an action and an observable result,
and attribution taken from the `(#N)` suffixes on the commits. The first flow is always *get
running*. The diff is the authority; a child's planned `## QA notes` is read for intent and the
diff overrules it.

**The loop's entire QA output is a label and a printed line.** `work-on-prd` labels the PRD
`needs-qa`, `work-on-spec` tags the `[SPEC]` `needs-qa`, each iff a child reported something a
human can exercise, and each prints the `manual-qa` invocation. **Neither loop invokes it.** The
developer who watched the run decides whether it warrants a pass; a driver that starts itself at
loop end is the checklist-nobody-works failure in a new costume.

**The receipt is output, never input.** End of pass posts one **free-form** comment — on the PRD,
or on the `[SPEC]` — saying which flows ran, the verdict on each, links to any findings, and
where the pass stopped if it stopped early. Nothing parses it. It has no template, and there is
no resume state to read: a re-run reads the branch again, composes fresh flows, and *asks the
human where to start*, offering the earlier receipt's stopping point as the obvious answer.
Storing a resumable pass would be storing a description that drifts against the branch it
describes.

**A verdict is per flow, and only a human produces one.** Pass, or fail at sub-step *k*. No
partial progress is recorded and a failure blocks nothing downstream. 0009's rule that a pass
verdict means *a human executed this and observed it work* is the one thing carried across
verbatim.

## What literals are left

Three, and they are the complete list:

- **`### [FINDING]`** — hardcoded in `manual-qa` and `triage` on the GitHub side, and
  deliberately absent from the adapter. 0009's inversion survives intact and for its own reason:
  a project free to edit the marker gets a triage pass that matches nothing and reports good
  news.
- **The `[FINDINGS]` title prefix** on Azure DevOps — `triage`'s input, found by scanning the
  parent's children, registered in the adapter's prefix row with the rest because ADO prefixes
  are load-bearing there. 0011's board reasoning for that is unchanged.
- **`PRD: #<n>`** in the pull-request body's machine block — how `manual-qa` and `triage` locate
  the run. This is **not a new literal**: it is the PR body's own resume key, which `work-on-prd`
  already wrote and already depended on. Match the whole line; `PRD: #12` is a prefix of
  `PRD: #127`.

Everything else that was a literal is deleted with the artifact it addressed: on GitHub the
comment template, the `## Steps` / `## Before you start` heading rules, the `- [ ] <n>. ` step
anchor, the `<!-- 75 80 -->` id trailers and the ` — **failed**` suffix; on Azure DevOps the
same shapes in that tracker's spelling, the run-context line, the backticked-id conventions that
existed only for the comment, and the never-edit rule with all three of its carve-outs.

## Consequences

- **`needs-qa` changes meaning slightly and changes owner not at all.** It means *not yet QA'd*,
  it is applied only when the run landed something exercisable, and only a human clears it —
  `manual-qa` offers, at the end of a completed pass, and leaves it on when the pass stopped
  early. The `needs-*` / `state:*` split holds. GitHub still needs the label created once by
  hand; ADO's tag is created implicitly on first use.
- **The worker report's item 4 shrinks to a signal.** `prd-worker` and `spec-worker` no longer
  refine QA steps for a comment that no longer exists; they report one line — what a human can
  exercise, or `nothing` — and that line is the only input to whether the label goes on.
- **`triage` reads findings, never the pass.** On GitHub it takes the PR's `### [FINDING]`
  comments, located by `PRD: #<n>`, as its sole source; on ADO it reads the run's `[FINDINGS]`
  item, whose closed-ness still answers *already handled*. GitHub's `Triaged:` back-annotation
  still does not exist on ADO and still must not be added.
- **The planners keep writing `## QA notes`, demoted to context.** `to-issues` and
  `to-spec-tasks` still ask for two or three lines per slice, now framed as *start from X, then
  …* so the composer can lift a starting state out of them. They are input to composition and no
  longer the pass; no flow schema went into a planning skill, and neither planner learned
  anything about flows.
- **Both loops got smaller.** Loop end §1 on each side lost a template and every rule that
  existed to protect it. The two remain **siblings, not a shared file with two call sites** —
  the reshape landed twice, once per tracker, with every literal its own.

## Rejected alternatives

- **Keep posting the comment as context for the composer.** It would have preserved the audit
  trail of what the run intended. It also preserves the artifact a tester reaches for first, and
  a stale plan sitting next to a fresh pass is read as the pass — the failure mode being fixed,
  with an extra step.
- **Let the loop invoke `manual-qa` at loop end.** Tempting, because it closes the loop without
  a human deciding anything. That is the objection: an unrequested QA session at the end of every
  run is a session nobody asked for and nobody works, which is how the committed QA document died
  in ADR 0005.
- **Make the flow list itself a contract, so a later session can resume it.** This is 0009's
  argument re-applied one level up, and it fails on the same defect: the branch moves, so any
  stored pass is a description going stale. Composing fresh costs one read and is never wrong.
