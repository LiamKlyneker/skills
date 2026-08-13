# Regression fixtures — the format, and when to re-run them

A fixture is a **frozen invocation** of `figma-component-to-spec`: the exact inputs a run gets,
the **capability profile** it must be run under, the **repo conventions** it resolves against,
and the **answers the human triage checkpoint is given** — including the frames that checkpoint
shortlists. All four are part of the fixture. The same component set grades differently with the
binding read absent, differently again against a repo whose variant mechanism or token pipeline
differs, and differently again when triage shortlists three frames instead of twenty-four — so
none of it is an accident of the day it was captured.

**The shortlist is an input, not an outcome, and that is what changed with this engine.**
Verification runs only on the frames Phase 4's checkpoint shortlisted (`../phases.md` →
*Phase 4.3*), so a fixture that does not pin them pins nothing: two runs of the same component set
that answer the checkpoint differently verify different frames and produce legitimately different
*Token delta* and *Figma fixes* sections. A case graded against a different shortlist is a
different case.

Run a fixture by invoking the skill with its inputs, then grade the produced `component-spec.md`
against the matching case in `expected-findings.md`. This file owns the **format**; that one
owns the **assertion style**. Both are plugin-side contracts. The fixtures themselves are not.

## Concrete fixtures are per-project

A fixture pins **real node IDs inside a real Figma file**, resolved against **one library's real
token list**, and graded against **one library's conventions**. The plugin owns none of those, and
a fixture built from them is not portable: the node IDs mean nothing in another file, the
expected tokens mean nothing against another design system, and the expected *shape* of a token
delta is decided by that repo's token-pipeline row rather than by anything here.

So: a project keeps its own fixtures, and **may register them in its adapter** — by pointer, the
same way a catalog is registered where one exists, and **never named by filename in this
plugin**. A project with no fixtures registered has nothing to re-run; the
pre-release step below then reports *"no fixtures registered"* out loud rather than passing
silently, because "no assertions ran" and "all assertions passed" must never look the same.

**This file carries no example fixture, and that is deliberate.** One shipped here would be one
library's node IDs, one library's token vocabulary and one library's variant mechanism,
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
| **The lattice** | yes | what the set draws: how many variant frames, the axes and their values in Figma's own vocabulary, and drawn-vs-cross-product. This is what Phase 2 derives from Setup's single root read, and it is graded whether or not a frame is ever extracted |
| **Triage answers + shortlist** | yes | the outcome the human gives each candidate at the Phase 4 checkpoint, and the **shortlist** confirmed with it — the frames, by node ID, that Phase 5 is allowed to verify. An **empty shortlist is a valid pinned value**. Without these the run is not reproducible, because the checkpoint is a human gate in the middle of it |
| Component under read | yes | the token-list entry and the source file the current-state read is expected to resolve to — **source first**, per `../phases.md` → *Phase 3* |
| **Existence source** | yes | what the run assembles its token list from: the token source the adapter's *Token pipeline* row names, plus the project catalog **where one is registered** (how it resolves — normally the adapter pointer — and the **catalog fingerprint** the case was captured against). A fixture captured with no catalog registered says so; that is a valid profile now, not a broken one |
| **Convention profile** | yes | the adapter's three library rows as they stood: variant mechanism (including any trap), token pipeline (generator or not), story convention. A case graded against different rows is a different case |
| **Capability profile** | yes | which Figma capabilities are present and which are absent, per capability, not as a summary — **plus the seat's plan tier and the rate ceiling the run was budgeted against** |
| Expected triage shape | yes (`none` counts) | which of the four outcomes the run should **recommend**, and roughly how many of each. The recommendation is the skill's; the decision is the human's, and it is pinned in the row above |
| Why this fixture exists | yes | the specific defect(s) it reproduces — a fixture nobody can tie to a failure is one nobody can decide to delete |

**The capability profile is stated per capability, never as "full" or "degraded".**
`figma-dev-mode` present/absent, **`get_screenshot` present/absent**, and the `use_figma` binding
read present/absent are three independent facts, and two of them change what a *passing* run
looks like. With the binding read absent, every color must come back flagged, so a run that
resolves a color cleanly is a failure rather than a better result. **`get_screenshot` is a pinned
capability now, because the cheap pass takes one wide set-level shot with it**: a case captured
with it available and re-run without it loses the skeleton's visual half, and every geometry
question that shot closed legitimately moves onto the shortlist instead — a bigger shortlist there
is a capability difference, not a regression. The binding read also changes the arithmetic the
budget guard does — no binding read means `3K` calls rather than `4K` worst-case, and a wave of 6
rather than 5 — so the facts are not independent of the *cost* of the run even though they are
independent of each other.

**The plan tier is part of that profile, because the budget guard's behaviour depends on it.**
State it the way `../phases.md` → *Phase 5.1* states it, and do not invent a second phrasing:

- the **tier and seat** the run's ceiling belongs to, and the ceiling itself — the reference seat
  is **org tier, Dev seat, `200/day · 20/min`**, which is also Phase 5.1's stated default;
- **which of Phase 5.1's three sources** the ceiling came from (passed to the run · recorded in
  the adapter · the stated default);
- that the ceiling is **org-scoped, not account-scoped** — it is a property of the org that owns
  the file being read, so a fixture pinned at a file outside that org-tier team is running against
  a **View** seat's *monthly* allowance instead, which is a different product and not a rate to
  throttle around;
- that the daily figure is a **recorded disagreement**, not a settled number: the seat's own
  `whoami` reports 200/day where Figma's published table lists Organization at 600/day, the
  per-minute figures agreeing at 20. The conservative, live-authority value is the one to pin.

`whoami` is on Figma's rate-limit-exempt list, so confirming a seat's real tier before capturing
a fixture is free. A case captured on the good seat and re-run on a different one is a case whose
budget guard will legitimately stop the run before it spawns anything, and that is a **capability
difference, not a regression** — which is exactly why the tier is written down.

**The convention profile is the field this skill adds, and it is the one most easily left
implicit.** The three adapter rows decide what a correct spec *says*, not merely what it finds
— a token delta is literal or a file-edit list depending on the pipeline row, and a story edit
is or isn't part of a change depending on the story row. **The *Token pipeline* row now carries
more than that**: it names the source the token list is assembled from, so it also decides
whether a catalog is involved in the run at all (`../phases.md` → *Phase 1*, steps 3b and 3e).
Capture all three with the fixture, because a repo that later gains a token generator invalidates
every case graded before it did — the catalog stops being load-bearing on the same day — and
nothing about the produced spec will look wrong when that happens.

## When to re-run — a pre-release step, and explicitly not CI

**Trigger: any change to this skill's extraction, enumeration or triage rules, re-run before
that change ships** — before the plugin's version moves and before the PR merges. Concretely,
an edit to any of:

- the **variant**-agent contract (`../../../../agents/figma-variant-extractor.md`) — what gets
  extracted, the call discipline, the return schema (whose echo key is `variant`), or the
  `variant:` source-node role. **Not** the page-side `../../../../agents/figma-region-extractor.md`,
  which belongs to `figma-to-spec` and is never spawned by this skill: an edit there earns that
  skill's fixtures a re-run, not this one's;
- `../../../figma-to-spec/references/resolution-rules.md` — candidate filtering, tolerance bands,
  tier preference, status handling;
- in `../phases.md`: **Phase 1.5**'s cheap pass — the three set-level reads it consumes, the
  axis-decomposed skeleton it writes, and the inference flag it stamps, all of which decide what a
  passing spec contains before any frame is read; **Phase 2**'s lattice derivation (axes,
  drawn-vs-cross-product, the computed instance counts); **Phase 4**'s four-outcome triage and
  **the shortlist rule** it hands forward — one frame per axis-value at one representative size,
  plus flagged anomalies, minus what the source read settled; and **Phase 5**'s spawn contract —
  including **5.1**'s budget guard, whose stop changes which frames a run reaches, and **5.2**'s
  wave sizing;
- **Phase 1** (Setup) step 3 — what the token list must cover, where each part comes from, and
  when the run stops for want of an existence source. A change here changes what "exists" means
  for every finding in the case;
- the current-state read (**Phase 3**) — how the adapter's variant-mechanism ladder is walked,
  how a named trap is folded into the accepted set, and the catalog's role as cross-check rather
  than answer;
- `../component-spec-template.md`, where a section's contract changes what a passing spec
  contains;
- `../../../figma-to-spec/references/catalog-contract.md`, where a validation rule changes what a
  catalog may say — including the four status shapes.

A doc-only edit that changes no rule does not earn a re-run. A rule edit does, every time —
that is the whole point of pinning adversarial cases: the defects these guard are
*silent-correctness* ones, where the spec still looks complete.

**The cheap-first engine is itself such a change, and it triggers a full re-run of every
registered fixture before the version ships.** It moves what the pre-checkpoint half reads, what
writes the spec's largest sections, what the shortlist means and what the agent is spawned to do —
so no case graded against the previous engine grades this one. A fixture whose expected shortlist
was a subset of the drawn set may legitimately become `0 of N` here; that is the change working,
and it is re-captured rather than treated as a failure.

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
`cva`, hand-written `argTypes`), a capability profile not yet tested, or a **shortlist shape** not
yet tested. **One fixture per distinct failure mode**, each with a paired case in
`expected-findings.md`. A fixture with no paired case is not a fixture; it is an invocation nobody
can grade.

Three shortlist shapes are worth pinning deliberately, because they fail in different directions:

- **`0 of N`** — a well-tokenized component whose skeleton is complete and whose triage
  shortlisted nothing. The spec must be **complete**, written entirely from the three set-level
  reads, and *Extraction coverage* must say `0 of 24` with *Figma fixes* carrying its
  bounded-completeness caveat. This is the case that catches a run treating an empty shortlist as
  a failure — or padding one to have something to spend on;
- **a strict subset** — triage shortlists 3 of 24 frames. The whole *Variant axes* table, and
  every instance count in it, must still be complete, and *Extraction coverage* must say
  `3 of 24` with a reason per omission. This is the case that catches a run deriving counts from
  what it verified;
- **the whole set** — triage shortlists 24 of 24. Rare under the shortlist rule and worth pinning
  precisely because it is: it must still be written `24 of 24` rather than "full coverage", so
  that the section reads the same way in all three cases and a reader never has to guess which one
  they are looking at.

The highest-value first fixture in any library is the component whose declaration mechanism has
a **trap** — an accepted value the primary mechanism does not list. That is the case where a
wrong answer looks most like a right one.
