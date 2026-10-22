# Task body — the one shape of a `[TASK]` issue

The single home for the body of a task issue in `prd-workflow`. Two skills write it and one
executes it:

- `to-prd-tasks` writes one per PRD child: **core** sections, plus the
  **fidelity** sections for a User-visible slice whose PRD carries a `## Fidelity ledger`.
- `to-task` writes one standalone task: **core** + **standalone** sections, plus the **fidelity**
  sections when the grill worked from a design brief (ledger mode).
- `work-on-task` executes either; `work-on-prd`'s worker executes a PRD child.

A section a writer does not use is **omitted, not stubbed** — no empty heading, no "N/A". Absent
sections are how `work-on-task` tells a plain task from a fidelity task, so a stubbed
`## Fidelity ledger (in scope)` would switch on a gate with nothing behind it.

## Section order

Write the sections a body uses in this order, and no others:

| # | Section | Kind | Written by |
|---|---|---|---|
| 1 | `## Summary` | standalone | `to-task` |
| 2 | `## External steps` | core | both |
| 3 | `## What to build` — or `## Changes` in ledger mode | core | both |
| 4 | `## Design reference` | fidelity (UI) | both |
| 5 | `## Fidelity ledger (in scope)` + `### Source slices — read before coding` | fidelity | both |
| 6 | `## Decisions confirmed` | standalone | `to-task` |
| 7 | `## Out of scope` | standalone | `to-task` |
| 8 | `## Worker context` | core | both |
| 9 | `## QA notes` | core | both |
| 10 | `## Acceptance criteria` | core | both |
| 11 | `## Verify` | fidelity, standalone only | `to-task` in ledger mode |
| 12 | `## Blocked by` | core | both |

A PRD child keeps its screenshot-pair and polish checkboxes in `## Acceptance criteria`; a standalone
ledger-mode task keeps them in `## Verify`. Same rows, per `../_shared/fidelity-ledger.md` §5, in
either place.

<!-- String contract: this file is the normative writer for the `## External steps`, `## Blocked by`, `## Worker context`, `## Design reference`, `## Fidelity ledger (in scope)` and `## QA notes` headings and for the two "None…" sentinel phrases below. `../_shared/prd-eligibility.md`, `work-on-prd` and `work-on-task` parse them. Change a heading or sentinel here and you must change it there. There is deliberately no `## Parent` heading: a PRD child's parent is the native sub-issue link, and a hand-written section beside it would be a second source of truth that can disagree. -->

<issue-template>
## Summary

*(standalone only)* 2–4 lines. What this task changes and why, in product terms. Name the
component the work lives in and the feature flag gating it, if there is one. In ledger mode, state
that the target is the pinned design below, not the current app.

Then one line, verbatim:

**Implement this issue with `/prd-workflow:work-on-task <this-issue-url>`.**

## External steps

A checklist of in-session manual actions Claude cannot perform — anything you'll need to do yourself during the implementation session (dashboard config, RPC/policy tweaks, env var changes, copy approval, manual prod verification, feature-flag toggles, webhook setup, etc.).

- [ ] Step 1
- [ ] Step 2

Or "None — fully implementable from the editor" if the issue requires no manual actions. <!-- parsed verbatim — do not reword -->


## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

*(standalone, no ledger)* Follow the description with the changes as a numbered list, in the order a
worker would build them, each naming the **symbols** it touches (component, prop, handler, function)
and the real path of its file — never a line number. Every fact comes from the consensus; add none
of your own.

## Changes

*(ledger mode only — replaces `## What to build`)* Numbered, one per element or decision, in the
order a worker would build them. Each entry:

1. **<Element> — <what changes>** · ledger row: `<element>` (`<class>`) · decision: `<the grill's decision>`

   What to build, referencing **named symbols** (component, prop, handler) and never a line number.
   Every fact in this entry is quoted from the cited ledger row or the cited decision — this
   section introduces **no** layout facts of its own (hard rule 8), no utility classes (hard rule
   5), no DS component the ledger did not name (hard rule 6) and no renamed icon (hard rule 7).
   Where the target needs more detail than the row states, point at the row's source slice rather
   than inventing the detail here.

## Design reference

*(fidelity)* For UI issues only. Omit for non-UI issues.

A PRD child carries the design ref(s) from the PRD's `## Design reference` so a cold implementation
session has the target with no prior context:

| Area | Design ref | Label |
|------|------------|-------|
| <area> | <design ref url> | "<label>" |

A ledger-mode standalone task carries the brief it was grilled from and the pinned prototype:

Pinned at `<proto-owner>/<proto-repo>@<sha>` · path `<proto-path>`.

- Brief: `<brief-path>`
- Spec: <spec url>
- Component states: <one state url per in-scope state>

Then one screenshot block per in-scope state, per `../_shared/fidelity-ledger.md` §3.

## Fidelity ledger (in scope)

*(fidelity)* The ledger rows for this task's elements — the brief's rows for a standalone task, the
PRD's rows for this slice's elements for a PRD child — built per `../_shared/fidelity-ledger.md` §1:
run the extraction command that section specifies and paste its output, every column byte for byte,
then append the Decision and Instruction cells to each pasted line. Never retype a row. Run §1's
check before writing the body out; a row the diff reports is replaced with the printed bytes.

A PRD child also carries here the screenshot blocks for those rows' states, per §3. Omit the whole
section for a task with no ledger rows.

### Source slices — read before coding

One block per row whose Decision is `local component` or `DS with overrides`, per
`../_shared/fidelity-ledger.md` §4.

## Decisions confirmed

*(standalone only)* From the grill's consensus — its `## Fidelity decisions` in ledger mode — close
to verbatim. One bullet per decision, each stating the decision and the reason that was accepted for
it. A decision to keep existing behaviour belongs here with its reason, not in `## Out of scope`.

## Out of scope

*(standalone only)* Named, not implied. What this task deliberately does not touch — in ledger mode,
the ledger rows and brief elements left out — each with one clause on why (another ticket, no design
artifact, deferred). A reader must be able to tell a deliberate exclusion from an omission.

## Worker context

Everything a cold, isolated worker session needs to implement this slice without plan mode. The PRD stays path-free (paths rot over months); this section gets real paths because issues are consumed within days.

- **Files**: real paths the slice touches (create/edit), plus the scoped `CONTEXT.md`(s) to read first.
- **Prior art**: concrete in-repo examples to copy the pattern from (path + one line on what to imitate). Prior art is an **engineering** source only; never a layout-fact source (`../_shared/fidelity-ledger.md` §2 rule 9).
- **Verify**: exact commands, taken from the project adapter at `<repo-root>/.claude/project/adapter.md` (L2 test command; L3 app/boot command if applicable).
- **User-visible**: y/n — y means the verify ladder's L3 (app boot + screenshot) applies.

## QA notes

2–3 lines for the human QA pass: what to do in the running app, what they should see, edge cases worth poking. These are **context for the QA pass, not the pass itself** — `manual-qa` composes the pass from the branch later and lets the diff overrule them — so write each as "start from X, then …", naming the state to be in before the action, and where this slice is a refactor, a bump or config that nobody can exercise by hand, say that instead of inventing a step.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] (UI issues) One checkbox per scorecard row and per polish-checklist item in this slice's scope, each carrying its pass condition verbatim, per `../_shared/fidelity-ledger.md` §5 — and where the file the adapter's `Fixed scorecard` row names has no `## Scorecard` for this ticket, or the adapter registers no such row, the derived rows that section specifies, never another ticket's scorecard
- [ ] (UI issues) The design ref + label recorded in the page's `CONTEXT.md` `## Design reference` table
- [ ] (Issues introducing a new write on an existing store — from the PRD's `## Data & Access`) An access policy for that specific operation exists for the acting user, and the write path surfaces a denied write instead of swallowing it

*(standalone ledger mode)* The scorecard and polish checkboxes go in `## Verify` instead; the rest
stay here.

## Verify

*(standalone, ledger mode only)* **Screenshot pairs** and **Polish checklist** — per
`../_shared/fidelity-ledger.md` §5.

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers. <!-- parsed verbatim — do not reword -->


</issue-template>
