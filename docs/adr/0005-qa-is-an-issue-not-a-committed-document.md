# ADR 0005 — The QA pass is a per-run item, not a committed document

- **Status**: Superseded by ADR 0006
- **Date**: 2026-07-31
- **Context**: the title-prefix + QA-item change; `docs/qa/prd-16.md` and `docs/qa/prd-52.md` are the evidence

## Context

`work-on-prd` ended a run by writing a markdown file to a path the project adapter named
(`docs/qa/prd-<n>.md`), committing it to the PRD branch, and linking it from the PR. The
human ran it start-to-finish before merging — verify-ladder L5.

Two of those documents exist. They are **440 lines** (`docs/qa/prd-52.md`) and **459 lines**
(`docs/qa/prd-16.md`). They are kept in the repo deliberately, as this record's evidence.

Nothing about the length was an accident of writing style. The instruction was *one section
per completed issue*, so every landed issue earned a section whether or not a human could act
on it — a dependency bump and a pure refactor each contributed several lines of prose whose
content was that there was nothing to test. The sections that mattered were buried among the
ones that didn't, and the length is what stops the document being read to the end, which is
the one thing it exists for.

The committed-file shape had a second problem that no amount of editing fixes. A PRD is run
more than once. The path is keyed on the PRD, so a second run appends to — or worse, rewrites
— a document describing a slice that was already tested, and there is no signal telling the
human which half is new. It accumulates and goes stale silently.

**The ADO side already had the answer.** `work-on-spec` ended a run by creating a `[QA]` work
item, one per run, committing nothing — and documented itself as *"the deliberate divergence
from `work-on-prd`"*. That was written when the divergence looked like a tracker difference.
It was not: it was the better design, on the tracker that happened to be built second.

## Decision

**Both loops file a per-run QA item and neither writes a file.**

- One item per **run**, never per PRD or `[SPEC]`. A second run creates a second item and
  never edits the first.
- **A landed child earns a step only if a human can exercise it in the running app.**
  Refactors, bumps, config and internal-only work get one line in `## What landed` and nothing
  else — no step, and no standalone "nothing to test here" line. Those lines are what produced
  440.
- **Nothing testable in the whole run → no item at all**, said explicitly in the final summary
  and where the PR's `QA:` line would have gone. An empty item is worse than none.
- Built from two sources only: each worker's **refined QA notes** and its **deviation log**.
  Not the parent, not the children's acceptance criteria, not the diff — those describe what
  was planned, and the reports are the only record of what was built.
- The shared rules live in `_shared/qa-item.md`. Each skill keeps its own tracker mechanics.

The adapter's `## QA doc convention` section is **deleted**, not renamed: after this change
nothing reads it. Its one genuinely useful clause — *which entry point, which command, what to
look for* — folds into the `## Verify ladder` **L5** line, which both bundles already require.

Two consequences of that deletion are the reason it was safe. `doctor.sh` matches a bundle's
declared sections as a **prefix** of an adapter heading and errors only on *missing*, never on
*extra* — so dropping the row leaves every already-installed adapter with an inert section and
zero doctor noise. A **rename** would have reported `UNFILLED` in four repos this change cannot
reach.

**Title prefixes came with it, and are not a separate decision.** ADO filters a parent's
children by the `[TASK]` prefix, which is what makes a `[QA]` sibling invisible to the pick
path by construction. GitHub had no prefixes, so a `[QA]` issue mentioning `#52` in its body
would be returned by `prd-eligibility`'s substring child search and picked up as implementable
work — a worker handed a human checklist to build. GitHub therefore gained `[PRD]` · `[TASK]` ·
`[BUG]` · `[QA]`, registered in the adapter rather than hardcoded, and `triage-prd`'s bugs moved
from `[QA]` to `[BUG]` because `[QA]` now names the opposite thing. The prefixes are what make
the QA issue safe; they are not decoration that happened to land in the same change.

## Consequences

**Pinned installs keep writing to a path this repo no longer documents.** `docs/estate-inventory.md`
records three `prd-workflow@liamklyneker` installs pinned at `81af34d0d5e1` and one under
`~/.claude-teamsnap` at `6ac8dfa62316` — and the `claude plugin` CLI cannot reach the
non-default config directories at all. Those installs run the old loop end: they will commit a
`docs/qa/prd-<n>.md` to their branch, against an adapter section their copy still has. Nothing
errors, and the working tree here looks converged. This is the ordinary cost of the version
cache key (ADR [0001](0001-version-the-plugins-and-enforce-the-bump.md)), stated here because
the symptom — a QA document appearing in a repo whose skills "no longer do that" — reads like
a bug in this change rather than a stale install.

**The two existing documents stay.** They are not migrated into issues and not deleted. They
are the evidence for the argument above, and a reader who wants to know why the shape changed
should be able to open the thing that changed it.

**The QA item is now closable, and that is a new failure mode.** A document on a branch could
not be marked done by a merge; an issue or work item can. Both loops therefore carry an
explicit prohibition at the point the link is written — GitHub's lever is the PR's `Closes`
line, ADO's is the linked-work-item list, and ADO's is armed by default. A QA pass that closes
itself on merge is silent: it surfaces only as nobody having tested the release.

**Every in-flight PRD depended on a fallback to survive the prefix filter.** No GitHub child
carried `[TASK]` when this landed, so the title filter keeps a set-level legacy fallback keyed
on `[TASK]`/`[BUG]` presence specifically. Keyed on *any* bracket prefix instead, one `[QA]`
issue from a single run would have switched the filter on and dropped every genuine child of a
legacy PRD at once — reported as "run `/to-issues` first", which reads entirely correct.

## Rejected alternatives

**Keep the document, shorten it by instruction.** The earning rule alone would have cut the
length, and it is the larger half of the fix. It does nothing about accumulation across runs,
which is the failure with no symptom: the document keeps looking finished.

**Rename `## QA doc convention` to something the new shape needs.** Nothing reads it after
this change, so a rename would preserve a question the installer no longer has an answer for,
and would report `UNFILLED` in four unreachable repos. Deleting was strictly cheaper.

**Have `work-on-spec` adopt the committed document, for symmetry.** This was the shape of the
original divergence note, read backwards. It converges the two loops on the worse design; the
440-line evidence is against it.
