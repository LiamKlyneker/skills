# Expected findings — the pass/fail contract

One case per fixture — per fixture the *project* holds, in the format `fixtures.md` defines.
This file documents the **assertion style**; like that format it is plugin-side, while the
concrete cases are per-project and live wherever that project keeps its fixtures. Nothing here
is an example case, for the same reason nothing there is an example fixture: a case is written
in one library's catalog vocabulary and graded against one library's conventions, and this
plugin ships to every library.

## The style

- **One case per fixture, cited by the fixture's ID.** A case with no fixture grades nothing;
  a fixture with no case cannot be graded.
- **Every line is a single checkable assertion**, written as a tickable `- [ ]` box, and tied
  to the defect it guards. "The spec looks right" is not an assertion.
- **`MUST` vs `SHOULD`.** A `MUST` failing means the run regressed — stop and find the edit
  that caused it (`git log` / `git bisect` the skill; the repo has per-version history). A
  `SHOULD` is a quality signal that is worth reading but does not fail the run.
- **Name the artifact each line is graded against** — the produced `component-spec.md`, or the
  **raw variant-agent findings**. These disagree, and that disagreement is itself informative:
  synthesis re-flagging something an agent got wrong is diligence, not a pass. Grade the raw
  findings wherever the assertion is about extraction, and the spec wherever it is about what
  the run concluded.
- **Assert on the property, not on the prose.** The output is LLM-generated, so a line that
  requires an exact word will fail on a run that was correct. Grade "the deprecated values
  appear in the variant-axes table with successors named", not "the word *deprecated* appears
  three times".
- **Assert absences explicitly.** Several of the rules below are only visible as things that
  *didn't* happen (no gap for a component the catalog contains, no Tailwind class recommended
  for a var-only token, no tracker write before triage). An absence nobody wrote down is an
  absence nobody checks.
- **Grade the current-state read separately from the design read.** This skill produces a
  *delta*, so a spec can be wrong in two independent ways: it misread Figma, or it misread the
  component as it stands today. A case that only asserts on the design half will pass a run
  whose delta is inverted.
- **Run at will, and as the pre-release step in `fixtures.md`** — after any edit to the skill
  you want to trust, before a version is stamped. Grade by hand, or hand the produced spec
  plus this file to a grader agent and have it return pass/fail per line.

## Assertions any case should carry

Rule-level lines every library's case is expected to include, adapted to its own catalog,
component and conventions. These guard the rules most likely to break under a rule edit.

- **Trap-inclusive current-state read** — the accepted set for a variant axis is the
  declaration mechanism's values **union** whatever the adapter's *variant mechanism* row names
  as a trap for that repo. A read that stops at the primary mechanism and reports a narrower
  API is a silent-correctness `MUST` failure: the spec looks complete, proposes to "add" a value
  that already exists, and nobody catches it by reading. Assert the count and the origin of each
  value, not just the count.
- **Ladder order, not ladder membership** — where the adapter names a fallback, the primary
  mechanism is tried first and the fallback only on a genuine miss. A read that resolves a
  component through the fallback while the primary was available is a `SHOULD` failure worth
  chasing: it usually means the primary was mis-parsed rather than absent.
- **Story coverage is computed, or declared non-computable** — coverage for an axis comes from
  `argTypes[axis].options` diffed against the values actually passed in story `args`. An axis
  whose `argTypes` entry is not a select asserts as *not computable — verify manually*.
  Reporting such an axis as **covered** is a `MUST` failure, and so is deriving coverage from
  story **export names**, which are unreliable as a coverage signal.
- **Token-delta literalness follows the adapter** — a repo whose *token pipeline* row names a
  generator gets a delta stating the **literal source edit**; a repo with no generator gets a
  **coordinated file-edit list** naming every file that must change together. Emitting the wrong
  shape is a `MUST` failure even when the token itself is correct, because the implementer
  either hand-edits build output or misses half the files.
- **Emission constraints are respected** — where the adapter or catalog records that some
  tokens do not get a class, or that a source may only be used at one layer, the spec does not
  recommend the unavailable form. A spec that recommends a class for a var-only token cannot be
  implemented as written.
- **Legacy resolution, not false-gapping** — a design element matching a catalog entry stamped
  `legacy` / `deprecated` / `unused` appears as **resolved + flagged** with its successor named
  where one exists, and produces no extend-component section merely for existing. A
  "modernize" triage decision may still generate one; an automatic one is a `MUST` failure.
- **Four outcomes offered, rationale recorded** — the triage checkpoint offers all four
  (already-expressible / extend-component / extend-tokens / fix-figma) and every decision
  carries a one-line rationale in the *Triage record*. A blank rationale is a failure: it is
  what a re-run reads to avoid re-litigating the decision.
- **Figma fixes are separated from code work** — an unbound or raw value in the Figma library
  lands in the *Figma fixes* section and is not silently specced as a code change. The two have
  different owners, and folding one into the other loses the designer-side work.
- **Pattern precedent is cited, not asserted** — every extend-component gap carrying a props
  API names the sources the precedent came from, and the spec does not present a researched
  shape as verified fit. `SHOULD`, and it is the line most worth reading even when it passes.
- **No invented vocabulary** — every token, utility, variant value and prop name emitted in the
  spec exists in the catalog the run resolved, or is explicitly marked as new.
- **Version pin** — the spec's extraction line carries a Figma file version or last-modified
  timestamp (or an explicit `unknown — <why>`), never nothing.
- **Triage gate** — zero tracker writes happen before the human triages.
- **One artifact** — the run produces `component-spec.md` and nothing else. A `gaps/` directory
  or a second file is a `MUST` failure: it gives one decision two homes that can disagree.

## How to read a failure

- A **current-state `MUST`** failing is the highest severity, and it is specific to this skill:
  the delta is computed against the wrong baseline, so the spec proposes work that is already
  done or omits work that isn't. It reads as a clean spec either way.
- A **silent-correctness `MUST`** failing (a variant frame collapsed, a value resolved to the
  wrong property kind, an axis reported covered that isn't) is next: the spec looks complete
  and isn't.
- A **shape `MUST`** failing (token delta in the wrong form, a class recommended for a var-only
  token) means the spec is right about *what* and wrong about *how*; the implementer hits it at
  edit time rather than at review time.
- A **vocabulary `MUST`** failing means the spec emits something that doesn't exist; the
  implementer inherits a wrong value that looks on-system.
- A **gate `MUST`** failing means the skill wrote to the tracker before human triage — a
  process breach, not just a content bug.
