# Expected findings — the pass/fail contract

One case per fixture — per fixture the *project* holds, in the format `fixtures.md` defines.
This file documents the **assertion style**; like that format it is plugin-side, while the
concrete cases are per-project and live wherever that project keeps its fixtures. Nothing here
is an example case, for the same reason nothing there is an example fixture: a case is written
in one library's token vocabulary and graded against one library's conventions, and this
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
  *didn't* happen (no gap for a component the token list contains, no Tailwind class recommended
  for a var-only token, no tracker write before triage, **no metered extraction call before the
  triage checkpoint**). An absence nobody wrote down is an absence nobody checks.
- **A narrow extraction is not thin coverage, and the case must be able to tell them apart.**
  Extraction runs only on the frames the fixture's kept set names, so most sections of a passing
  spec are graded against the **lattice** rather than against what was extracted. Grade *Variant
  axes* and every instance count as complete regardless of the kept set; grade *Token delta* and
  *Figma fixes* against the kept set only. A case that grades the whole spec against the whole
  set will fail every correct run of a narrowed triage.
- **Grade the current-state read separately from the design read.** This skill produces a
  *delta*, so a spec can be wrong in two independent ways: it misread Figma, or it misread the
  component as it stands today. A case that only asserts on the design half will pass a run
  whose delta is inverted.
- **Run at will, and as the pre-release step in `fixtures.md`** — after any edit to the skill
  you want to trust, before a version is stamped. Grade by hand, or hand the produced spec
  plus this file to a grader agent and have it return pass/fail per line.

## Assertions any case should carry

Rule-level lines every library's case is expected to include, adapted to its own token list,
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
- **Emission constraints are respected** — where the adapter, the token list or the catalog
  records that some tokens do not get a class, or that a source may only be used at one layer,
  the spec does not recommend the unavailable form. A spec that recommends a class for a var-only
  token cannot be implemented as written.
- **Legacy resolution, not false-gapping** — a design element matching a token-list entry stamped
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
  spec exists in **the token list the run was handed**, or is explicitly marked as new. The list
  is the whole existence source, whether it was assembled from the *Token pipeline* row's source,
  from a registered catalog, or from both; an entry that is not on it does not exist, however
  on-system it reads. Grade this against the **raw variant-agent findings** as well as the spec —
  an invented token that synthesis happens to drop is still an extraction regression.
- **Version pin** — the spec's extraction line carries a Figma file version or last-modified
  timestamp (or an explicit `unknown — <why>`), never nothing.
- **One artifact** — the run produces `component-spec.md` and nothing else. A `gaps/` directory
  or a second file is a `MUST` failure: it gives one decision two homes that can disagree.

### What the checkpoint-before-extraction order makes checkable

These are the lines the engine's shape earns, and each is graded against something a run either
did or did not do rather than against the quality of its prose. All of them are `MUST`.

- **The axis table is complete before any per-frame extraction** — every axis and every value the
  set draws appears in *Variant axes*, including on frames the kept set never touched. The lattice
  comes from Setup's single root `get_metadata`, so an axis missing from the spec means the
  lattice was mis-derived, **never** that a frame went unextracted. Grade this on a fixture whose
  kept set is a strict subset; on a full-coverage fixture the assertion cannot fail.
- **The extracted subset is disclosed, and a full-coverage reading is impossible** — the spec
  carries an *Extraction coverage* section written as `<K> of <N>`, naming each frame that was
  **deliberately** not extracted and its one-line reason, with a budget-guard narrowing recorded
  as exactly that rather than dressed up as a design judgement. A spec that omits the section, or
  writes "full coverage" for a kept set that happened to be everything, is a failure even when
  every finding in it is correct: an implementer has no other way to tell a scoping decision from
  thin coverage.
- **Instance counts are computed from the lattice, not derived from extracted frames** — every
  count is lattice arithmetic over the **drawn** set and is marked as computed. The tell is a
  count that tracks `K` instead of `N`: on a fixture that keeps 3 of 24 frames, a value drawn in
  8 frames still reports 8. A count that shrank with the triage tells a reviewer the opposite of
  the truth about how load-bearing a value is.
- **No metered call is spent before the triage checkpoint** — the only Figma read the run makes
  before the human triages is the single `get_metadata` on the component set root. A per-frame
  read, a second root read, or any `get_screenshot` at all before the checkpoint is a failure:
  the whole point of the order is that the human narrows the spend before it happens. **There is
  no `get_screenshot` anywhere in a correct run**, before the checkpoint or after it.
- **The budget is projected out loud before the first spawn, and the run stops rather than
  discovers the ceiling** — the run states `K`, the floor and worst-case projections, the ceiling
  and which source it came from, and the wave size it will throttle to. Where the projection
  exceeds the ceiling it stops **before spawning anything** and re-triages. A run that extracts a
  prefix of the kept set and stops half-way is a failure even if the partial spec looks clean:
  the sections it never reached are silently empty, which reads exactly like a component with no
  findings there.
- **Triage gate — two negatives, both asserted** — before the human triages, **zero tracker
  writes** have happened (not a search, not a draft, on either tracker) **and zero metered
  extraction calls** have been spent. These fail independently and neither implies the other.

## How to read a failure

- A **current-state `MUST`** failing is the highest severity, and it is specific to this skill:
  the delta is computed against the wrong baseline, so the spec proposes work that is already
  done or omits work that isn't. It reads as a clean spec either way.
- A **silent-correctness `MUST`** failing (a variant frame collapsed, a value resolved to the
  wrong property kind, an axis reported covered that isn't) is next: the spec looks complete
  and isn't.
- A **coverage `MUST`** failing (no *Extraction coverage* section, "full coverage" in place of
  `K of N`, an instance count that tracked the kept set) is the same severity and is the failure
  this engine specifically invites: a spec written from 3 of 24 frames is a **correct** spec, and
  the only thing separating it from a badly thin one is the disclosure. Read it as a scoping bug,
  not a formatting one.
- A **shape `MUST`** failing (token delta in the wrong form, a class recommended for a var-only
  token) means the spec is right about *what* and wrong about *how*; the implementer hits it at
  edit time rather than at review time.
- A **vocabulary `MUST`** failing means the spec emits something that doesn't exist; the
  implementer inherits a wrong value that looks on-system.
- A **gate `MUST`** failing means the run crossed the checkpoint before the human did — it wrote
  to the tracker, or it spent a metered extraction call, before triage. A process breach, not
  just a content bug, and the metered half costs a day's rate budget as well as the trust.
