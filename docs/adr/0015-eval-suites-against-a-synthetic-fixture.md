# ADR 0015 — Eval suites against a synthetic fixture are the release gate

- **Status**: Accepted
- **Date**: 2026-09-19
- **Context**: PRD #173, implemented by #174–#183

## The problem this replaces

Until this PRD, the only way to test a skill was to run it on real work in a consumer
project: a real branch, a real ticket, real prototype screenshots, and a human judging
the result by eye, once. That loop found real leaks — the design-fidelity chain went
from 0/4 to a diagnosable leak per hop — but it was slow, expensive in tokens, and not
repeatable: a skill edit could not be re-run against the same input and compared. It
also had a side effect: consumer material leaked into this public repo's issues,
because the consumer project was the only test bed. Nothing checked that a skill still
did what its contract said before it shipped.

## Decision

**An eval suite run against a synthetic fixture, on the first-party `claude plugin
eval` runner, is the release gate a skill change passes before its plugin's version
moves.** Real-ticket runs continue, but as a smoke on one real project through
`--plugin-dir`, never as the test.

### Suites are per hop, scored mostly by free graders

The design-fidelity chain is interactive end to end, so it cannot run headless as one
case. Each case covers one hop, fed by a frozen artifact of the hop before it: a frozen
brief for `deep-grill`, a frozen brief plus a frozen grill transcript (the runner's
`history_file`) for `to-task`, a frozen issue plus the scaffolded fixture app for
`work-on-task`. A change to one skill's prose therefore fails only its own case.

**Amended by ADR [0017](0017-two-fixture-tiers-and-which-one-a-leak-lands-in.md)**, which
supersedes this clause only: a case earns the scaffolded workspace when the leak is about
fixture shape, and tests one contract sentence on a micro stub otherwise.

Cases are named `<skill>-<leak>`, one per known leak cluster, tagged per hop.
Assertions are mechanical first: regex over the artifact a hop produced (a brief, an
issue body, a self-audit table), `tool_used` with an input match on the call that
matters, `file_exists`, trace checks. At most one `llm` grader per case, for a check a
regex cannot express — row coverage against the brief's ledger, or that a `## Changes`
section adds no layout fact absent from the ledger. A grader that would pass for a
clearly wrong output gets removed, not kept as coverage.

### Ablation is off

Every skill under test is invoked by its slash command, so the runner's default
no-plugin baseline arm scores a prompt that invokes nothing — it is meaningless here.
Suites run with `--ablation none`; the with-arm score is the whole score.

### Run policy

By hand, before a version bump, never on `pull_request` — the repo is public and fork
PRs must never see a credential, so CI keeps running the structural validator only.
Every run passes `--no-publish` (the runner's default publishes an HTML report to
claude.ai) and `--scaffold` (a case's fixture workspace is placed by a scaffold
script; without the flag every case runs against an empty workspace and fails for the
wrong reason).

While learning the suites: `--runs 1`, `--threshold 1.0`, a 5 USD list-price ceiling.
After calibration: three runs and `--threshold 0.8` — the pass@k choice, because a
single flaky run should not gate a release the way a repeatable failure should. On a
Max subscription the ceiling is a list-price estimate, not the real cost against the
usage window; the first suite runs are what measure the real cost. Measured so far, one
Sonnet 5 run each: `to-task-ledger-verbatim` at USD 1.61, `deep-grill-row-coverage` at
USD 1.21, `work-on-task-self-audit-skipped` at USD 1.79 — all under the ceiling with
room for the `--runs 3` calibrated policy.

The gate is `--model claude-sonnet-5`; a `claude-haiku-4-5` run is advisory only, since
ambiguity that a weaker model trips on is a signal about the prose rather than a
regression in it.

### The fixture

A private repo, a sibling checkout of this one by convention
(`../skills-fixture`), with a `git clone` fallback when the sibling is absent — the
scaffold script prints which source it used. It plays every external party a skill
under test talks to: a design-system package a real catalog can be built from, a
consumer app with a real verify ladder, and a prototype in the one shape
`prototype-to-spec` implements. Its content is invented — a neutral domain, English
copy, no server wiring — so nothing in it can leak a real consumer's name.

What ships where: case prompts, graders, case configs, and a frozen brief (only when it
names fixture things) live in this repo. The design system, the app, the prototype, its
rendered captures, the frozen grill transcript, and the fixture's own render/cleanup
scripts live in the fixture repo. The runner's results directory and mock recordings
are gitignored here. Run logs on real tickets belong in neither repo.

### Platform constraints this fixture design works around

The eval child has no network and no credentials, so every input a hop would normally
fetch is scaffolded into the run directory instead — `to-task` gained a local `--out`
path and `work-on-task` reads a local issue path, so a case never depends on a live
tracker call. The child cannot read a plugin's `skills/_shared` packaging symlink, so a
case's scaffold script copies the shared contract file into the run directory rather
than relying on the link resolving. `history_file` must resolve inside the case
directory, so a replayed transcript is placed there before the scaffold script runs,
never referenced from outside it. `file_exists` cannot see a file the scaffold placed
before the run started — only a file the run itself produces. A grader must never
match a string that already appears in the case prompt, or it scores a case that never
ran. The fixture brief repeats information across sections by design — because the
skill under test is asked to read every section, not just the ledger — so a regression
check has to remove an element from every section that carries it, not from the
ledger alone.

### Two tiers

**Tier 1** is this repo's suite, run against the synthetic fixture. An adapter variant
— a second fixture adapter naming different handoff files — proves a skill reads the
adapter's pointers rather than its own defaults, by giving the same prototype two
different sets of files to find.

**Tier 2** is a consumer project's own private cases, run against the installed plugin
with the runner's `--eval-dir` from the project directory. Tier 2 is recorded here as
intent only. Its mechanics and any `install-skills` scaffolding are a follow-up,
because the mechanism is read from the runner's CLI help and has not yet been
exercised against a real project.

### The transcript re-capture trigger

The frozen grill transcript backing `to-task-ledger-verbatim` is re-captured only when
`deep-grill`'s output contract changes — the shape of a round, a consensus line, what a
`Decision` cites. A prose edit that leaves the contract alone does not need a
re-capture; the transcript is a replay of what the hop *produces*, not of the words
that produced it.

### The privacy rule

Issues, evals, docs and commits in this repo name fixtures only — the synthetic
design system, the synthetic app, the synthetic prototype — never a consumer repo,
ticket or path. Run logs on real work stay in the consumer project, gitignored, as
they already did before this PRD. Every case carries a grader that checks the
artifacts it scores for consumer vocabulary, so a leak fails the case that produced it
rather than surviving as a passing score.

## Consequences

- A skill's `experimental.evals` manifest key and its `plugins/<plugin>/evals/`
  directory are load-bearing: CONTRIBUTING.md documents the run invocation, and a
  contributor changing a skill covered by a case runs it before opening a PR.
- Real-ticket runs are demoted in status, not retired. They remain the only check on
  the visual rows a screenshot-pair judges, and the only rehearsal of a real tracker's
  API shape — the fixture repo *is* a tracker under test, but it is not the consumer's
  tracker.
- A skill with no case covering it (most of `ado-workflow`, `install-skills`, and all
  of `lk` beside `deep-grill`) has no automated release gate yet. That gap is
  unaddressed by this PRD, deliberately — the first suite covers the design-fidelity
  chain only, because that is where the failure log existed to write cases against.

## Rejected alternatives

**Score suites against the real consumer project instead of a synthetic fixture.**
Rejected on the problem this PRD exists to fix: a real project's material cannot appear
in this public repo's cases, and a case that scaffolds a copy of the real project into
every run defeats the point of not naming it. A synthetic fixture that plays the same
role — real default chrome, a real verify gate, a real prototype shape — gets the same
coverage without the leak.

**Keep `--ablation` at its default (with/without).** Rejected because every case
invokes a skill by its slash command; the "without" arm is a prompt with no plugin
loaded and nothing to invoke, so it scores noise at double the cost.

**Run the suites in CI on `pull_request`.** Rejected for the same reason the QA driver
is never auto-invoked (ADR 0012): CI on a public repo's fork PRs has no credential to
run against, and a `workflow_dispatch` job that could carry one is a later decision,
not this PRD's.
