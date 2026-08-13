# Regression fixtures — the format, and when to re-run them

A fixture is a **frozen invocation** of `figma-component-to-spec`: the exact inputs a run gets,
the **capability profile** it must be run under, and the **repo conventions** it resolves
against. All three are part of the fixture. The same component set grades differently with the
binding read absent, and differently again against a repo whose variant mechanism or token
pipeline differs — so none of it is an accident of the day it was captured.

Run a fixture by invoking the skill with its inputs, then grade the produced `component-spec.md`
against the matching case in `expected-findings.md`. This file owns the **format**; that one
owns the **assertion style**. Both are plugin-side contracts. The fixtures themselves are not.

## Concrete fixtures are per-project

A fixture pins **real node IDs inside a real Figma file**, resolved against **a real project
catalog**, and graded against **one library's conventions**. The plugin owns none of those, and
a fixture built from them is not portable: the node IDs mean nothing in another file, the
expected tokens mean nothing against another design system, and the expected *shape* of a token
delta is decided by that repo's token-pipeline row rather than by anything here.

So: a project keeps its own fixtures, and **may register them in its adapter** alongside the
catalog pointer — by pointer, the same way the catalog is registered, and **never named by
filename in this plugin**. A project with no fixtures registered has nothing to re-run; the
pre-release step below then reports *"no fixtures registered"* out loud rather than passing
silently, because "no assertions ran" and "all assertions passed" must never look the same.

**This file carries no example fixture, and that is deliberate.** One shipped here would be one
library's node IDs, one library's catalog vocabulary and one library's variant mechanism,
published to every consumer of this plugin — and the first thing a reader would do is copy it.
The pull is stronger for this skill than for `figma-to-spec`, because a library's conventions
*look* like defaults in a way a page never does: a worked example naming `cva()` and a JSON
token generator would read as the expected shape rather than as one repo's answer, and the
adapter rows exist precisely because it is not. The field table below is the whole shape; a
fixture is that table filled in with values only the project has.

## Required fields of a fixture

Headings and field names are the contract; the values are the project's.

| Field | Required | Carries |
|---|---|---|
| Fixture ID + one-line title | yes | a stable name to cite from `expected-findings.md` and from a failure report |
| Component set node | yes | the node ID the run is invoked on — one component set, which is this skill's only shape |
| Variant frames | yes | how many the set contains, and any deliberately pruned, with the reason |
| Component under read | yes | the catalog entry and the source file the current-state read is expected to resolve to |
| Catalog | yes | how the run resolves it — normally "the project catalog via the adapter pointer" — plus the **catalog fingerprint** the case was captured against |
| **Convention profile** | yes | the adapter's three library rows as they stood: variant mechanism (including any trap), token pipeline (generator or not), story convention. A case graded against different rows is a different case |
| **Capability profile** | yes | which Figma capabilities are present and which are absent, per capability, not as a summary |
| Expected triage shape | yes (`none` counts) | which of the four outcomes the run should reach, and roughly how many of each |
| Why this fixture exists | yes | the specific defect(s) it reproduces — a fixture nobody can tie to a failure is one nobody can decide to delete |

**The capability profile is stated per capability, never as "full" or "degraded".**
`figma-dev-mode` present/absent and the `use_figma` binding read present/absent are two
independent facts, and the second one changes what a *passing* run looks like: with the binding
read absent, every color must come back flagged, so a run that resolves a color cleanly is a
failure rather than a better result.

**The convention profile is the field this skill adds, and it is the one most easily left
implicit.** The three adapter rows decide what a correct spec *says*, not merely what it finds
— a token delta is literal or a file-edit list depending on the pipeline row, and a story edit
is or isn't part of a change depending on the story row. Capture them with the fixture, because
a repo that later gains a token generator invalidates every case graded before it did, and
nothing about the produced spec will look wrong when that happens.

## When to re-run — a pre-release step, and explicitly not CI

**Trigger: any change to this skill's extraction, enumeration or triage rules, re-run before
that change ships** — before the plugin's version moves and before the PR merges. Concretely,
an edit to any of:

- the region-agent contract (`../../../../agents/figma-region-extractor.md`) — what gets extracted,
  the call discipline, the return schema, or the `variant:` source-node role;
- `../../../figma-to-spec/references/resolution-rules.md` — candidate filtering, tolerance bands,
  tier preference, status handling;
- Phase A variant enumeration or Phase B's spawn contract in `../phases.md`, and the Phase C
  four-outcome triage;
- the current-state read — how the adapter's variant-mechanism ladder is walked, and how a
  named trap is folded into the accepted set;
- `../component-spec-template.md`, where a section's contract changes what a passing spec
  contains;
- `../../../figma-to-spec/references/catalog-contract.md`, where a validation rule changes what a
  catalog may say — including the four status shapes.

A doc-only edit that changes no rule does not earn a re-run. A rule edit does, every time —
that is the whole point of pinning adversarial cases: the defects these guard are
*silent-correctness* ones, where the spec still looks complete.

**Not CI, and this is a property of the problem, not a gap in the tooling.** A run needs a live,
authenticated Figma MCP session against a private file, and it emits LLM-generated prose, so
there is no string to assert on and no headless way to produce one. Grade line-by-line against
`expected-findings.md` — by hand, or by handing the produced spec plus that file to a grader
agent and having it return pass/fail per line. Do not build a CI job that "runs the fixtures"
and passes when the session is unavailable; that is worse than no job, because it reports green
for a check that never executed.

## Adding a fixture

Add one whenever a run surfaces a defect no current fixture reproduces — a component shape not
yet covered (a single-variant component, a set with a boolean axis, a component whose axes
cross-multiply into dozens of frames), a convention profile not yet tested (no generator, no
`cva`, hand-written `argTypes`), or a capability profile not yet tested. **One fixture per
distinct failure mode**, each with a paired case in `expected-findings.md`. A fixture with no
paired case is not a fixture; it is an invocation nobody can grade.

The highest-value first fixture in any library is the component whose declaration mechanism has
a **trap** — an accepted value the primary mechanism does not list. That is the case where a
wrong answer looks most like a right one.
