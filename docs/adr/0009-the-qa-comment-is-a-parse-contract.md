# ADR 0009 — The QA comment is a parse contract, and the receipt comes back

- **Status**: Accepted
- **Date**: 2026-08-01
- **Context**: PRD #85, implemented by #89 (`manual-qa`) and #90 (`triage-prd`, and `work-on-prd`'s loop-end contract)
- **Supersedes**: ADR 0006

## Read this first: the sub-issues half of 0006 is untouched

ADR [0006](0006-sub-issues-and-qa-as-a-prd-comment.md) decided **two** things — *"A PRD's
children are sub-issues, and its QA pass is a comment on it"* — and this record revisits only
the second. The convention supersedes a record whole, so the `Superseded by ADR 0009` line now
sitting on 0006 would otherwise read as un-deciding native sub-issues. It does not.

**Native sub-issues remain how a PRD's children are enumerated**, exactly as 0006 decided:
`to-issues` and `triage-prd` write the link and verify it landed, `_shared/prd-eligibility.md`
reads the children back with a single call and applies no filter at all, the title prefixes stay
a human scanning convention that nothing keys on, and the failure mode stays loud and empty —
a mis-linked PRD reports zero children rather than a plausible wrong four. The full-text-search
defect that motivated it (`in:body "#66"` returning issue #4, because GitHub's tokenizer drops
the `#`) is still the reason, and nothing about it decayed.

Most of the QA half survives too, and for 0006's own reasons: the artifact is still a **comment
on the PRD plus a `needs-qa` label**, still **one per run and never one per PRD**, still never
edited or deleted, the earning rule still says a landed child gets a step only if a human can
exercise it, and the two trackers stay decoupled with `work-on-spec`'s `[QA]` work item
unchanged.

What changes is **what that comment is** — prose for a human, or a contract with parsers — and,
following from that, one of the two costs 0006 booked turns out to be partly recoverable.

## The comment is parsed

0006 could reasonably describe the template's shape as normative-by-convention, because it
assumed the comment's only consumer was the person running QA. That assumption was already
slightly false when it was written: `triage-prd` identified a QA comment by two markers taken
straight from `work-on-prd`'s template. It is emphatically false now. `manual-qa` parses the
step anchor `- [ ] <n>. `, checkbox state, the `<!-- 75 80 -->` id trailers and the
`Earlier QA pass still outstanding:` first line, and writes back into the body one line at a
time.

The evidence that convention was not enough: **#84 rewrote the template** — two headings, hidden
id trailers, checkboxes — and `work-on-prd` came out of it still saying no skill parsed the
comment, while one in another plugin did. A contract nobody had written down had already been
changed once without its reader being consulted.

So `work-on-prd`'s `## Loop end` now carries the five literals its two consumers depend on, and
says which skill parses each and why, with the instruction to change them in all three places
together. Everything else in the template stays normative because it is right, not because a
parser depends on the wording — and that distinction is the point of writing the five down.
The corollary `manual-qa` states about itself belongs here too: the comment **outlives the
skill**, and steps are read verbatim to a human, so no further compression of the template is
licensed by the fact that a machine can now read it.

## The never-edit carve-out widens from one to two

0006 admitted exactly one post-hoc mutation of a posted comment: checkbox state. There are two
now. The second is the **terminal failure suffix** — ` — **failed**, see [FINDING](<permalink>)`
— appended after a step's id trailer when that step failed and the failure was logged on the
run's PR.

It earns the carve-out on the properties that make it not authorship:

- **Pure append.** Step text and id trailer stay byte-identical; nothing is re-rendered or
  reflowed, which is the operation class that reformats a comment by accident.
- **Reversible.** Re-testing that step and passing drops the suffix and ticks the box in one
  write.
- **Not strikethrough**, which was the obvious alternative and was rejected: struck text reads
  as *cancelled / no longer applies*, which is the opposite of what happened; it mutates the
  step text; and it has no clean undo.

Everything else stays forbidden, and #90 spelled the list out rather than leaving it implied —
no rewording a step, not even a typo fix; no appending a step to a posted comment; no deleting
or editing away a comment. A tick and a failure suffix record what a tester observed. They do
not make the tester a second author.

## The receipt comes partly back

0006 booked this as a real loss and did not hedge it:

> **The closable receipt is genuinely lost.** A closed `[QA]` issue was proof the pass had been
> run; a comment has no closable state.

**All steps `[x]`, no failure suffix anywhere, `needs-qa` removed** is now that proof, and it is
strictly better than a closed issue: a closed `[QA]` issue said *a* pass happened, while the
comment says **which steps** passed and, until they do, exactly which one did not and where the
finding is.

**Why it could not be claimed in 0006, and this is the load-bearing part.** A failed step is
never re-tested inside its own comment — the comment is per-run and never edited, so the re-test
lands in the next run's comment. Without a *reversible* annotation, any PRD that ever produced a
single finding could never reach all-ticked, and "every box ticked" would have meant nothing at
all. Reversibility is not a nicety of the suffix's design; it is the entire mechanism that turns
tick state into a receipt.

**And 0006's instruction not to simulate the receipt still stands, unweakened.** Nothing was
added. `manual-qa` posts no session-log comment, writes no "pass complete" reply, and keeps no
aggregate state across passes. The receipt is *read off* state that had to exist anyway so a
half-finished pass could resume cold.

## `needs-*` semantics are intact

The skill **offers** to remove `needs-qa` when all three conditions hold, and never removes it
unprompted; if either of the first two fails it does not offer at all. A human still clears the
label, deliberately, and that is still the only signal in the tracker that a pass was run. What
the driver removed is the browser trip, not the human.

## A deliberate inversion: `[FINDING]` is hardcoded, and deliberately not in the adapter

This repo's standing rule is that a project-specific literal belongs in the adapter and never in
a skill — the title prefixes are registered there, and are *"a human scanning convention, not a
filter."* The `### [FINDING]` marker inverts that: it is **hardcoded in both `manual-qa` and
`triage-prd`, and deliberately absent from the adapter.**

The inversion is recorded because it reads as an inconsistency otherwise. A registered marker
would be a marker a project can edit, and editing it produces a `triage-prd` run that finds zero
findings and reports a clean PR — wrong, silent, and indistinguishable from a genuinely clean
run. The adapter registry exists for values that legitimately differ per project; a string two
skills must agree on byte-for-byte is not one of them. #90 supplied the proof by counterexample:
the old marker `### <emoji> QA finding:` contained a character no rule defined, and was therefore
unmatchable by construction — nobody noticed, because a triage pass that finds nothing looks
exactly like good news.
