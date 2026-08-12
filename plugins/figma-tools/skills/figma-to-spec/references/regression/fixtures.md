# Regression fixtures — the format, and when to re-run them

A fixture is a **frozen invocation** of `figma-to-spec`: the exact inputs a run gets, plus the
**capability profile** it must be run under (the same page grades differently with the binding
read present vs. absent, so the profile is part of the fixture — not an accident of the day it
was captured).

Run a fixture by invoking the skill with its inputs, then grade the produced spec against the
matching case in `expected-findings.md`. This file owns the **format**; that one owns the
**assertion style**. Both are plugin-side contracts. The fixtures themselves are not.

## Concrete fixtures are per-project

A fixture pins **real node IDs inside a real Figma file**, resolved against **a real project
catalog**. The plugin owns none of those, and a fixture built from them is not portable: the
node IDs mean nothing in another file, and the expected tokens mean nothing against another
design system.

So: a project keeps its own fixtures, and **may register them in its adapter** alongside the
catalog pointer — by pointer, the same way the catalog is registered, and **never named by
filename in this plugin**. A project with no fixtures registered has nothing to re-run; the
pre-release step below then reports *"no fixtures registered"* out loud rather than passing
silently, because "no assertions ran" and "all assertions passed" must never look the same.

**This file carries no example fixture, and that is deliberate.** One shipped here would be one
project's node IDs and one project's catalog vocabulary, published to every consumer of this
plugin — and the first thing a reader would do is copy it. The field table below is the whole
shape; a fixture is that table filled in with values only the project has.

## Required fields of a fixture

Headings and field names are the contract; the values are the project's.

| Field | Required | Carries |
|---|---|---|
| Fixture ID + one-line title | yes | a stable name to cite from `expected-findings.md` and from a failure report |
| Run mode | yes | `page` or `component` — a component-mode run skips fan-out, so the two grade differently |
| Primary node | yes | the node ID the run is invoked on |
| Additional nodes | yes (`none` counts) | each with its role: `viewport:<bp>` or `state:<name>` |
| Scope context | yes (`none` counts) | the ticket and/or freetext the run is given — scope precedence is itself under test |
| Catalog | yes | how the run resolves it — normally "the project catalog via the adapter pointer", or an explicit arg override when the fixture is testing resolution order |
| **Capability profile** | yes | which Figma capabilities are present and which are absent, per capability, not as a summary |
| Why this fixture exists | yes | the specific defect(s) it reproduces — a fixture nobody can tie to a failure is one nobody can decide to delete |

**The capability profile is stated per capability, never as "full" or "degraded".** `figma-dev-mode`
present/absent and the `use_figma` binding read present/absent are two independent facts, and
the second one changes what a *passing* run looks like: with the binding read absent, every
color must come back flagged, so a run that resolves a color cleanly is a failure rather than a
better result.

## When to re-run — a pre-release step, and explicitly not CI

**Trigger: any change to this skill's extraction or enumeration rules, re-run before that
change ships** — before the plugin's version moves and before the PR merges. Concretely, an
edit to any of:

- the region-agent contract (`../../agents/figma-region-extractor.md`) — what gets extracted,
  the call discipline, or the return schema;
- `../resolution-rules.md` — candidate filtering, tolerance bands, tier preference, status
  handling, triage outcomes;
- Phase A enumeration or scoping in `../phases.md`, and Phase B's spawn contract;
- `../catalog-contract.md`, where a validation rule changes what a catalog may say.

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

Add one whenever a run surfaces a defect no current fixture reproduces — a page shape not yet
covered (form-heavy, data-table with reflow, real component instances), or a capability profile
not yet tested. **One fixture per distinct failure mode**, each with a paired case in
`expected-findings.md`. A fixture with no paired case is not a fixture; it is an invocation
nobody can grade.
