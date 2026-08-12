# Expected findings — the pass/fail contract

One case per fixture — per fixture the *project* holds, in the format `fixtures.md` defines.
This file documents the **assertion style**; like that format it is plugin-side, while the
concrete cases are per-project and live wherever that project keeps its fixtures. Nothing here
is an example case, for the same reason nothing there is an example fixture: a case is written
in one project's catalog vocabulary, and this plugin ships to every project.

## The style

- **One case per fixture, cited by the fixture's ID.** A case with no fixture grades nothing;
  a fixture with no case cannot be graded.
- **Every line is a single checkable assertion**, written as a tickable `- [ ]` box, and tied
  to the defect it guards. "The spec looks right" is not an assertion.
- **`MUST` vs `SHOULD`.** A `MUST` failing means the run regressed — stop and find the edit
  that caused it (`git log` / `git bisect` the skill; the repo has per-version history). A
  `SHOULD` is a quality signal that is worth reading but does not fail the run.
- **Name the artifact each line is graded against** — the produced `page-spec.md`, a gap file,
  or the **raw region-agent findings**. These disagree, and that disagreement is itself
  informative: synthesis re-flagging something an agent got wrong is diligence, not a pass.
  Grade the raw findings wherever the assertion is about extraction.
- **Assert on the property, not on the prose.** The output is LLM-generated, so a line that
  requires an exact word will fail on a run that was correct. Grade "a per-card state chip
  surfaces in Data states", not "the word *expired* appears".
- **Assert absences explicitly.** Several of the rules below are only visible as things that
  *didn't* happen (no cross-kind token match, no gap for a legacy component, no findings for
  vector interiors). An absence nobody wrote down is an absence nobody checks.
- **Run at will, and as the pre-release step in `fixtures.md`** — after any edit to the skill
  you want to trust, before a version is stamped. Grade by hand, or hand the produced spec
  plus this file to a grader agent and have it return pass/fail per line.

## Assertions any case should carry

Rule-level lines every project's case is expected to include, adapted to its own catalog and
page. These guard the rules in `../resolution-rules.md` and the region-agent contract, so they
are the ones a rule edit is most likely to break:

- **Property-scoped matching** — no value resolves to a token of a different property kind: no
  stroke width resolving to a layout spacing step, no text color resolving to a background/
  surface token. Graded on the raw findings, where each resolved value carries the
  `propertyKind` it was filtered on.
- **Legacy resolution, not false-gapping** — a design element matching a catalog entry stamped
  `legacy` / `deprecated` appears as **resolved + flagged** with its successor named, and
  produces **no gap file**. A gap for a component the catalog contains is a `MUST` failure.
- **Vector-geometry exclusion** — an icon or illustration produces no color/spacing findings
  for its interior path data, while its **own box size and applied color** still resolve
  normally. Both halves are asserted; the exclusion swallowing the usage-site color is its own
  regression.
- **Version pin** — the page spec's `Extracted against:` line carries a Figma file version or
  last-modified timestamp (or an explicit `unknown — <why>`), never nothing.
- **Triage outcomes and rationale** — the checkpoint offers all three outcomes, and every
  non-escalated gap file carries a one-line rationale. A blank rationale on a
  compose-from-tokens or build-local decision is a failure: it is what a re-run reads to avoid
  re-litigating the deviation.
- **No invented vocabulary** — every token, utility and variant value emitted in the spec
  exists in the catalog the run resolved.
- **Triage gate** — zero tracker writes happen before the human triages.

## How to read a failure

- A **silent-correctness `MUST`** failing (required content missing, a region collapsed, a
  value resolved to the wrong property kind) is the highest severity: the spec looks complete
  and isn't, so nobody catches it by reading.
- A **vocabulary `MUST`** failing means the spec emits something that doesn't exist; the
  implementer inherits a wrong value that looks on-system.
- A **gate `MUST`** failing means the skill wrote to the tracker before human triage — a
  process breach, not just a content bug.
