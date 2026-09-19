---
name: to-task
description: >
  Publish a single implementation issue from a deep-grill consensus, skipping the
  PRD → to-issues ceremony. Embeds the pinned design screenshots inline, pastes the
  fidelity ledger rows for the elements in scope as build instructions, and ends with
  the scorecard as a screenshot-pair verify checklist. Use when a grill has reached
  consensus on one design ticket and the work is a single issue rather than a PRD.
  Invoke /prd-workflow:to-task.
---

# To Task

```
/prd-workflow:to-task <ticket> <brief-path> [--out <path>]
```

Takes the **current conversation** — a `deep-grill` session that has reached consensus — plus the
design brief it grilled from, and publishes **one** implementation issue to the project tracker.

Use it instead of `to-prd` → `to-issues` when the work is a single ticket that one worker session
can carry: a design-fidelity pass, a small feature, one bug with a design target. There is no PRD,
no sub-issue tree, no `Blocked by` graph. One issue, one commit, one verify pass.

Do **not** interview. The grill already happened; this skill only transcribes its consensus into a
shape a cold worker can implement.

## Inputs

| Input          | Where it comes from                                                                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `<ticket>`     | the argument — e.g. `FUS-8965`. Names the feature and goes in the title.                                                                                     |
| `<brief-path>` | the argument — the design brief the grill read, e.g. `.claude/briefs/FUS-8965-run1.md`. Source of the **fidelity ledger rows** and the pinned prototype SHA. |
| `--out`        | the optional argument — a path. Given, the title and body go to that file and **no** issue is created; absent, the issue is filed as usual. |
| The grill      | this conversation. Source of `## Fidelity decisions`, the confirmed decisions, and the scope boundary.                                                       |
| Project facts  | `<repo-root>/.claude/project/adapter.md` — tracker, verify ladder, repo discipline. Never hardcode these.                                                    |
| Scorecard      | the file the adapter's `Fixed scorecard` row names, `## Scorecard` — the verify checklist, when the adapter registers that row and the file has one for this ticket. |

## Preflight

Before writing a single line of the body:

1. Read the adapter. Take the tracker from its **`Tracker:`** / `Issue tracker / PRs:` rows, and the
   **L2 floor** command from its `## Verify ladder`. If the adapter's L3 row says visual verify is
   deferred, the screenshot pairs below are still written into the issue — they are the run's
   scoring instrument, not an automated gate.
2. Read `<brief-path>` in full. Pull out: the pinned prototype repo + SHA, the prototype path, the
   spec / component-state URLs, and the `## Fidelity ledger` rows — **as raw markdown rows**, with
   every column, because they are pasted into the issue unchanged. Note the ledger's column order;
   the issue keeps it.
3. Settle where the verify rows come from, per `../_shared/fidelity-ledger.md` §5. Read the file
   the adapter's `Fixed scorecard` row names, when the adapter registers one, and use its
   `## Scorecard` rows and its `## Polish checklist` **only when that file carries them for this
   ticket**; both then go into `## Verify` verbatim. With no such row, or for any other ticket,
   derive the scorecard rows from the ledger per §5 and omit the polish checklist.
4. Find the grill's **`## Fidelity decisions`** block — the consensus list, one entry per ledger
   row, giving the decided class (`DS as-is` / `DS with overrides` / `local component` /
   `DS change`) and any named override.
5. **Stop if any of these is missing.** A ledger row with no decision, a decision with class
   `OPEN`, or no `## Fidelity decisions` block at all means the grill is not finished. Say which
   rows are unresolved and stop — do not fill the gap with a judgement of your own.
6. Settle **scope**: which ledger rows / elements this one issue covers. Everything else in the
   brief goes under `## Out of scope` by name, so a reader can tell "not this ticket" from
   "forgotten".

## Hard rules

Hard rules 1–9 are normative in `../_shared/fidelity-ledger.md` §2. Read them before writing the
body; a body that breaks any of the nine is not published.

## Title

```
<Feature> (<ticket>): <one-line scope>
```

Example: `Custom eligibility (FUS-8965): rules container, DOB editor, value editor, question picker`.

No `[PRD]` / `[TASK]` prefix — this issue has no parent and no children, so there is nothing for a
prefix to disambiguate. `<Feature>` is the product-facing name, `<ticket>` the Jira key, and the
one-line scope names the **elements** in scope, not the technique.

## Issue body

Write these sections, in this order, and no others.

<issue-template>
## Summary

2–4 lines. What this issue changes and why, in product terms. Name the component the work lives in
and the feature flag gating it, if there is one. State that the target is the pinned design below,
not the current app.

Then one line, verbatim:

**Implement this issue with `/prd-workflow:work-on-task <this-issue-url>`** — it is the implementer contract for
a `to-task` issue: read the brief's ledger, every screenshot and every source slice first, then
self-audit per ledger row before the verify gate.

## Design reference

Pinned at `<proto-owner>/<proto-repo>@<sha>` · path `<proto-path>`.

- Spec: <spec url>
- Component states: <one state url per in-scope state>

Then one screenshot block per in-scope state, per `../_shared/fidelity-ledger.md` §3.

## Fidelity ledger (in scope)

The brief's ledger rows for this issue's elements, built per `../_shared/fidelity-ledger.md` §1 —
pasted verbatim, every column, plus the Decision and Instruction columns.

### Source slices — read before coding

One block per row whose Decision is `local component` or `DS with overrides`, per
`../_shared/fidelity-ledger.md` §4.

## Changes

Numbered, one per element or decision, in the order a worker would build them. Each entry:

1. **<Element> — <what changes>** · ledger row: `<element>` (`<class>`) · decision: `<the grill's decision>`

   What to build, referencing **named symbols** (component, prop, handler) and never a line number.
   Every fact in this entry is quoted from the cited ledger row or the cited decision — this
   section introduces **no** layout facts of its own (hard rule 8), no utility classes (hard rule
   5), no DS component the ledger did not name (hard rule 6) and no renamed icon (hard rule 7).
   Where the target needs more detail than the row states, point at the row's source slice rather
   than inventing the detail here.

## Decisions confirmed

From the grill's `## Fidelity decisions` and the rest of its consensus, close to verbatim. One
bullet per decision, each stating the decision and the reason that was accepted for it. A decision
to keep existing behaviour belongs here with its reason, not in `## Out of scope`.

## Out of scope

Named, not implied. Ledger rows and brief elements this issue deliberately does not touch, each
with one clause on why (another ticket, no design artifact, deferred). A reader must be able to
tell a deliberate exclusion from an omission.

## Verify

**L2 — floor, non-negotiable** (from the adapter's `## Verify ladder`):

```
<the adapter's L2 command, verbatim>
```

**Screenshot pairs** and **Polish checklist** — per `../_shared/fidelity-ledger.md` §5.
</issue-template>

## Publishing

**With `--out`, this whole section is one step: write the title on the first line, one blank line,
then the body verbatim, to that path.** Then go straight to the final print. Nothing is created,
the tracker is never called, and nobody is asked to confirm — the file is what the human reads, and
it can be edited in place. Do not stop to ask, and do not write the body anywhere else first. A
sandbox with no network and no tracker credential still produces the whole deliverable this way.
Everything above this section is unchanged: the same preflight, the same hard rules, the same body.

Without `--out`:

1. Write the finished body to a scratchpad file — never inline it into a shell argument, since the
   body contains backticks, pipes and markdown image syntax that a shell will mangle.
2. **Show the human the title and the body, and ask for confirmation before creating.** This skill
   is used interactively at the end of a grill; the body is the whole deliverable and it is cheaper
   to fix it here than to edit a published issue. Do not create on an implied yes.
3. On approval:

```bash
gh issue create \
  --repo <tracker> \
  --title "<Feature> (<ticket>): <one-line scope>" \
  --body-file <scratchpad>/<ticket>-task.md
```

4. The prototype repo is private, so every screenshot carries a fetch line and the Design reference
   blocks carry the download sentence — per `../_shared/fidelity-ledger.md` §3.

5. Apply the project's filed-and-unclaimed triage label from the adapter's `Triage labels:` row if
   the human wants this on the board; a one-off run issue does not need one.

## Final print

Filter: the issue is one click away and more current than any recap of it.

```
#<n> created: <url>
```

With `--out`, there is no number and no url, so the last two lines are the path and the invocation
that implements it:

```
issue body written: <path>
/prd-workflow:work-on-task <path>
```

Above that line, one line per **deviation** — a ledger row left out of scope because the grill never
settled it, a scorecard element whose pass condition had no matching ledger row, a screenshot whose fetch line could not be resolved at the SHA. When no fixed scorecard file carries a polish checklist for this ticket, print "no polish checklist for this ticket" here. Print every one, even when it makes the print
longer than the URL. No section recap, no change list — the human is about to open the issue.
