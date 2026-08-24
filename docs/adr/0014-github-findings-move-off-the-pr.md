# ADR 0014 — GitHub findings move off the pull request, onto a disposable per-run issue

- **Status**: Accepted
- **Date**: 2026-08-24
- **Context**: PRD #155, implemented by #156–#158
- **Supersedes**: ADR [0012](0012-the-qa-pass-is-composed-from-the-branch.md), **on the
  findings-location half only**

## Read this first: what still stands in 0012

0012 decided two things bundled into one record: that the QA pass is **composed from the
branch** rather than planned into a contract, and that a GitHub failure is captured as a
**`### [FINDING]` comment on the run's pull request**. Only the second half is reversed here.

**Composed-from-the-branch is untouched.** `manual-qa` still finds the run's PR by the PR body's
`PRD: #<n>` resume key, still reads the diff/commits/landed-children as the sole authority, still
lays the pass out as flows with a `start from:` line and sub-steps, and still takes one verdict
per flow from a human with no partial credit. Nothing about *how the pass is built or driven*
changes here.

**The three surviving QA literals are untouched in kind, one of them relocated.** `### [FINDING]`
is still the hardcoded parse-contract marker `triage` matches on; `PRD: #<n>` in the PR body's
machine block is still how the run is found. The `[FINDINGS]` title prefix — previously
ADO-only, `triage`'s input there — now also exists on GitHub, registered the same way ADO's is,
but as a **human scanning convention only**: the GitHub findings issue is *located* by the same
`PRD: #<n>` resume key the PR finder already uses, never by its title.

What is superseded is narrow: 0012's claim that a GitHub finding lands as a PR comment, and
everything that followed from posting it there.

## The losing reasoning, stated fairly

0012 put findings on the PR because the PR was already the composed-pass's home — `manual-qa`
had just read the PR to build the flows, so writing the verdict back to the same thread kept
capture and composition in one place, with no second artifact to find-or-create. That was a real
economy, and it is not being reversed because posting to the PR was hard or the comment shape was
wrong. It is being reversed because the PR was never QA's room to begin with.

## The defect: the PR thread belongs to CI, not to QA

A pull request's conversation is not blank space waiting for a QA driver to use. On any
reasonably instrumented repo it already carries CI status checks, e2e test reports, and AI
reviewer comments — and a `### [FINDING]` posted into that stream competes with all of it for
attention, scrolls past as the PR accumulates other activity, and leaves no record of a run's
findings as a set once the PR closes. The PR's timeline was built to review *a change*, not to
hold *a QA pass's findings*, and asking it to do both scattered the record across a timeline
never meant to carry it.

## The decision

**A GitHub QA pass files findings to one disposable, per-run `[FINDINGS]` issue — never to the
PR.** `manual-qa` find-or-creates it **lazily, on the first failed flow** — a clean pass creates
nothing — located by the same `PRD: #<n>` resume key the PR finder already uses, matched as a
whole line. It is **free-standing**: never linked as a sub-issue of the PRD, so it never shows up
to eligibility as an implementable child. `triage` reads its `### [FINDING]` comments exactly as
it always read them, and **closes it** — never deletes it — as the last step of publishing, once
every finding on it is disposed. A closed findings issue is the permanent record that a pass
happened and what it found; the PR goes back to being a record of the change alone.

### Two points handled gracefully, not designed around

Both of these are real situations the mechanism will hit and both get the same treatment: **stop
and ask**, not a rule engineered to resolve them silently.

- **Two open `[FINDINGS]` issues for one PRD.** This should not happen by construction — one run,
  one lazily-created issue — but a human can create a second one by hand, or two sessions can
  race. When the find-or-create search turns up more than one open hit, `manual-qa` and `triage`
  both **stop and ask which one**, rather than picking the newer one, merging them, or guessing.
- **Capturing against a merged PR.** A pass can resume, or a finding can be captured ad-hoc, after
  the PR it exercised has already merged. The branch that produced the diff may still exist, or
  may not; either way, filing a finding against a run whose PR is gone is worth a human's eyes
  before it happens, not a silent proceed. `manual-qa` warns and asks before writing anything;
  `triage` warns up front, in one line, before starting its cadence.

Neither carve-out gets a mechanism of its own — no dedup heuristic, no "most recent wins", no
auto-detection of whether the branch is still live. A person answers once and the session
proceeds on that answer.

## Consequences

- **The PR's conversation is CI's and the reviewer's again.** A `### [FINDING]` never appears
  there; the only trace of a QA pass on the PR is whatever `manual-qa` chose to say about it in
  the PRD receipt, which was already true under 0012.
- **`[FINDINGS]` joins the adapter's *Title prefixes* row on GitHub**, registered exactly like
  `[PRD]` / `[TASK]` / `[BUG]` — a human scanning convention, filtered on by nothing, because the
  finder is the `PRD: #<n>` line in the body, not the title.
- **The two trackers' shapes converge.** GitHub and Azure DevOps now both capture findings to a
  disposable, per-run `[FINDINGS]` issue/work item rather than a PR/`[SPEC]` comment stream, both
  find-or-create it lazily on the first failure, and both close it in `triage`. They remain
  siblings that arrived at the same shape independently, not a shared file with two call sites —
  every literal, and every find-or-create query, is still written out in full on each side.
- **One more object exists per run that finds anything** — a clean pass still creates nothing, so
  a PRD with no QA findings gains no extra issue.

## Rejected alternatives

- **Keep posting to the PR, and have `triage` filter the thread for the marker.** This is 0012's
  shape with no change at all. It does not fix the defect: the PR thread still competes with CI
  and review noise, and a finding posted mid-review is exactly as easy to scroll past as before.
- **One long-lived `[FINDINGS]` issue per PRD, reused across every run.** Tempting, because it is
  one fewer find-or-create per run. It fails the same way a resumable QA pass would have failed
  under 0012's own reasoning: a reused issue accumulates findings from runs whose branches have
  since moved or merged, and "which run is this finding from" stops being answerable from the
  issue alone. A fresh issue per run keeps that question free.
- **Auto-resolve the two-open-issues and merged-PR cases instead of asking.** Picking the
  newest open issue, or silently refusing to capture against a merged PR, would remove one
  question from the flow. Both are situations that happen by human action outside the loop's own
  invariants, so the honest answer is to surface them rather than guess — the same posture ADR
  0012 already takes toward "blocked" verdicts and toward two-open-issue races on the ADO side.
