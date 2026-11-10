# ADR 0027 — Eval cases are earned by a failure

- **Status**: Accepted
- **Date**: 2026-11-10
- **Context**: PRD #286
- **Supersedes**: ADR [0015](0015-eval-suites-against-a-synthetic-fixture.md) **on evals being
  the release gate**, ADR [0017](0017-two-fixture-tiers-and-which-one-a-leak-lands-in.md) **on
  the two fixture tiers**, and ADR [0016](0016-a-scorer-beside-the-gate.md) **in full**. ADR
  0015's rule that fixtures are named and consumer material never is, stays in force (see
  below).
- **Corrects**: one sentence of ADR [0020](0020-the-automated-qa-pass-gets-its-own-plugin.md),
  which stays `Accepted` with its body unedited (see below).

## The reasoning that got us here, and where it stops

ADR 0015 made an eval suite against a synthetic fixture the release gate. ADR 0017 cut the cost
of a case by adding a micro tier beside the full one. ADR 0016 added a scorer to measure what a
gate cannot. Each decision was fair on its own terms. A skill is prose an agent runs on someone
else's machine, a regression in it is invisible in a diff, and a case that replays the input
catches it mechanically. At the time of 0015 the design-fidelity chain had a failure log to write
cases against, and the suite was small.

The suite then grew by projection. Most cases were written at design time for a failure somebody
expected, not for one that happened. By 2026-11-10 it held 57 cases across five plugins, and all
34 cases in `qa` guarded a skill that had not completed a run on a real project. The local run
history shows 127 suite runs from 2026-09-19 to 2026-11-10 at a list price of USD 151.62, with
`qa` alone at 53% of it. Of 391 recorded case runs, 108 failed, and those failures cluster at
each case's creation: they are authoring iteration, not regression catching. An audit of all 57
cases against the rule below found 3 that pass. A micro case costs about USD 0.45 per run and a
full case about USD 1.80, and unlike a unit test that charge recurs for as long as the case
exists.

## Decision

**An eval case is admitted only when a failure has earned it. The default answer to "does this fix
need an eval" is no.**

### The admission rule

A case is added only when all four hold:

1. **The failure came back after a fix.** A first failure is fixed in prose and gets no case.
2. **The maintainer would not see the failure when it happens again.** The path is unattended, or
   a second skill or a script parses the output, or the output is public or irreversible.
3. **A deterministic grader decides it in one run.** No LLM grader, and no grader on wording.
4. **No free check can prevent it instead.** A validator rule, a script, a template or a
   redesign comes first.

### The one exception

A failure the maintainer could never notice qualifies on its first plausible occurrence: private
data in a public issue, or a broken contract in an unattended run. Waiting for a second
occurrence that would go unseen is not an option, so condition 1 is waived. Conditions 2 to 4
still hold.

### Redesign before eval

When a failure returns after a fix, the first answer is a free mechanical check that makes it
impossible. A case is the second answer, for when no such check exists.

### The recurrence signal

Recurrence is detected where reports are filed. `lk:report` marks a report that matches a closed
issue with a `Recurrence of #N` line. The session that fixes an issue carrying that line answers
"redesign or eval" before it closes the work, and records the answer in the pull request
description.

### What it kept

Three cases, each admitted by its own condition. One run of all three costs about USD 1.50.

- `work-on-prd-unattended-continues` (`prd-workflow`). Admitted under the exception: the path is
  unattended and the night script reads only the exit code, so a broken contract fails a night
  and not a gate. Its graders are file regexes.
- `work-on-spec-unattended-continues` (`ado-workflow`). The same contract on the other tracker,
  whose loop prose is separate. The same graders.
- `report-sanitized` (`lk`). Admitted under the exception: the output is a public, permanent
  issue, and the leak class has happened before. Its graders are regexes.

The other 54 cases are deleted along with the machinery that served only them: the full fixture
tier, the fixture scaffold and history scripts, the sidecar scorer and the tier vocabulary. Git
history keeps every case, and one can be restored when a real failure matches it.

### What stays in force from ADR 0015

Fixtures are named, and consumer material never is. Issues, evals, docs and commits in this repo
name synthetic fixtures only, never a consumer repo, ticket or path. Run logs on real work stay in
the consumer project. A case that uses a fixture still carries a grader that checks the artifacts
it scores for consumer vocabulary. The `--ablation none`, `--no-publish` and `--scaffold` flags
stay as the adapter's gate row has them.

### The sentence in ADR 0020 this corrects

ADR 0020 places the automated QA pass's evals under `plugins/qa/evals/`. After this ADR the `qa`
plugin has no eval directory. Read that sentence as history. ADR 0020 stays `Accepted`, since its
decision to give the pass its own plugin is untouched, and its body is not edited.

## The argument

**An eval is a recurring charge.** A test in a conventional codebase costs nothing per run. A case
here costs real money each time the gate runs, for as long as the case exists, so each case needs
a reason that outlives its authoring.

**A single maintainer who reads a skill's output is that skill's regression test.** Interactive
skills print their result into a conversation, and the maintainer sees a failure the moment it
happens, for free. A case only adds value where nobody is reading: an unattended run, an output
another skill or script parses, or an output that is public or irreversible. That is condition 2.

**A suite's density is copied by the agents that work beside it.** An agent working in a plugin
with 34 cases reads that as the expected density and adds more. A suite that stays small and
states its admission rule gives the agent the opposite signal.

## Consequences

- The gate row in the adapter stays: once per branch, scoped to the touched skills. A touched
  skill with no case runs nothing, and that is the expected answer, not a gap.
- 22 skills have no case and will not get one by default. A skill earns its first case by
  failing twice, or by being a path nobody watches.
- The cost of this decision is that a first failure of an observed skill ships unguarded. The
  maintainer sees it, fixes it in prose, and a case appears only if it returns.
- `qa` and `figma-tools` end with no case and lose their eval wiring. `lk:report` gains the
  recurrence line, and its change does not itself earn a case.

## Rejected alternatives

**Keep the full fixture tier.** Rejected because it exists only for cases that fail the rule. The
fixture scaffold, the history preparation, the shared fixture files and the scorer serve
workspace-shaped cases, and none of them is unattended, parsed by a second skill, or public.
Keeping the machinery keeps the signal that such cases are expected.

**Keep a case that needs an LLM grader.** Rejected because a grader that judges wording passes on
some phrasings and fails on others, and one run at threshold 1.0 cannot absorb that. It is the
expensive and unstable kind of case, and it makes a drifting number decide whether a version
ships. That is the argument ADR 0016 already made against a model in the gate, applied to the
whole suite. `to-task-ledger-verbatim`, the one case with a recorded catch, is deleted for this
reason.

**Run evals in CI.** Rejected for 0015's reason, unchanged: a public repo's fork pull requests
must never see a credential. It is also now unneeded, since a gate of at most three cases is
cheap enough to run by hand once per branch.
