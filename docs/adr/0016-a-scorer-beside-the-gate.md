# ADR 0016 — A scorer sits beside the gate, never inside it

- **Status**: Accepted
- **Date**: 2026-09-21
- **Context**: PRD #188, implemented by #199 onward

## The rule this bends

`CLAUDE.md` holds one rule about scripts in this repo: **a skill ships a script only when the
job is mechanical and must produce the same answer twice**, and *"a script whose output is a
judgement never does"*. That rule is right, and it is right for the reason it gives. A skill is
prose an agent executes on someone else's machine; a script inside a skill is the part of that
prose nobody reads. If the script returns a judgement, the skill's behaviour becomes a number
that cannot be argued with and cannot be reproduced — two runs of the same check disagree, and
the disagreement looks like a fact.

The eval suites of ADR 0015 obey it. Their graders are regex, `tool_used`, `file_exists` and
trace checks; at most one `llm` grader per case, and one that would pass for a clearly wrong
output gets removed rather than kept as coverage. The gate says pass or fail, and a
contributor can read why.

## The thing that does not fit

A case tells you whether `to-task` transcribed the ledger. It does not tell you how far the
output drifted, which claims drifted, or whether a prose edit moved the drift up or down. That
question is a measurement, not a gate: its answer is a number, the number moves between runs,
and a single reading of it should change nothing about whether a version ships.

Its procedure is deterministic — take the `## Changes` section, cut it into claims, normalise
them, and check each against the ledger the run was given. Its numbers are not: every claim the
exact match cannot settle goes to a model, and a model is the part that disagrees with itself.

## Decision

**A scorer may live in this repo, and it lives beside the release gate rather than inside it.**
`plugins/prd-workflow/evals/sidecar.py` is the first one. Four constraints make it acceptable:

- **Beside, not inside.** It runs by hand, after a suite has finished, over the runner's
  `aggregate-result.json`. No case declares it, no grader calls it, and nothing that gates a
  version bump reads its numbers. A suite that passes without the sidecar having ever run is a
  suite that passed.
- **It pins its model id.** `jev-1.13.0`, a constant in the module. A score compared across two
  prose edits is only a comparison if the judge did not change underneath it; an unpinned model
  turns a measurement into a rumour.
- **It never edits the runner's output.** It does not touch `aggregate-result.json` and it
  writes nothing into a case directory. Its own file lands in the results stamp directory,
  beside the aggregate the runner wrote and inside the directory `.gitignore` already covers.
- **No credential, no run.** With `TYPESAFE_API_KEY` absent it prints that it scored nothing and
  exits zero. There is no offline fallback and no degraded mode — a number produced by half the
  procedure would be compared against one produced by all of it.

The deterministic half stands on its own and is unit-tested as such: the normaliser is a pure
function, and the exact-match stage scores the frozen `to-task` output with no network call.
Only the claims that stage cannot settle reach the model.

## Consequences

- **The source a claim is checked against is the produced issue's own
  `## Fidelity ledger (in scope)` section.** That is what landed, and it is what
  `to-task-ledger-verbatim/sidecar.json` names. The alternative was the scaffolded brief at
  `apps/consumer/capture/brief.md`: both files are present in a kept run directory, but the
  issue's ledger is the state the `## Changes` section was written against, so a claim that
  restates a Decision or Instruction cell scores as carried rather than as drift. The reader
  falls back to the whole file when a source carries no ledger section, which is what lets the
  brief be named instead without a second code path.
- A case opts in by carrying `sidecar.json`. A case without one is skipped silently, so adding
  the scorer changed no existing case and cannot fail one.
- The sidecar reads a run's kept working directory, derived from the run's `tracePath`. That
  directory only exists when the suite ran with `--keep-temp`; without it the sidecar fails
  naming the path it looked for, rather than scoring an empty output as total drift.
- This repo now holds a script whose output is a judgement. The rule in `CLAUDE.md` stands for
  skills, and this record is the whole of the exception: a scorer, outside every skill, outside
  the gate.

## Rejected alternatives

**Add the measurement as one more `llm` grader on the case.** Rejected because it makes a
drifting number decide whether a version ships. ADR 0015 already caps a case at one `llm`
grader for a check a regex cannot express, and requires that a grader failing to reject a
clearly wrong output be removed; a grader that returns "72% of claims carried" fails both — it
never rejects anything outright, and it converts a release decision into a threshold nobody set
deliberately.

**Write it as a line in ADR 0015.** Rejected because 0015's argument is that the gate is
mechanical, and a scorer is the opposite kind of thing. Appending the exception to the record
that establishes the rule leaves a reader unable to tell which half they are allowed to copy.

**Score offline only, with no model at all.** Rejected because exact match after normalisation
settles a small minority of the claims of a real output — two of forty-one, on the frozen
`to-task` issue. A number built from that alone would report drift wherever a run re-worded a
sentence faithfully, which is the measurement's whole subject and not its noise.
