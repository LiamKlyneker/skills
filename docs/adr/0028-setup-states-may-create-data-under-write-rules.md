# ADR 0028 — `setup-states` may create data, under write rules

- **Status**: Accepted
- **Date**: 2026-11-11
- **Context**: PRD #301
- **Amends**: ADR [0022](0022-knowledge-is-derived-accounts-are-observed.md), on its clause
  "the pass never creates data" only. Everything else in 0022 stands: the two files, their split by
  how each drifts, and the three writers of `accounts.md`.

## Context

ADR 0022 closed the question of creating data in one bullet. Three levels were considered: use
known accounts only; run a named seeder when no account has the state; run it and record what it
created. Only the first was built, and the levels that create data were dropped for two reasons.
They make an external tester a writer of the data it judges. They also put a project's seeding
machinery on the critical path of every run. Both reasons are sound for `prove-branch`, and 0022's
rule that the pass never creates data stands for it.

0022 left one gap. A state that staging does not hold, and that the page cannot make, got a
`Seeder (for a human)` hint and nothing else. On the run behind PRD #301, a thorough pass found 14
of 20 states by observation, and all six that were left were made outside the page: on another
page of the app, in a sibling app, or by a chain through both. Two of the six were a short chain a
tester could follow. One of the six had no UI path at all, and a developer's belief that a sibling
app made it was wrong. The knowledge file had no place to record either fact.

## Decision

**Where a state is made is derived knowledge, recorded in the knowledge file.** The format gains a
fifth table, `## How a state is made`, one row per step, with the app, role, screen, action and
the result the user sees. A row with step `none` records that a tester cannot make the state, with
the reason. Every chain row carries the origin `app-repo (<repo name>)`, so a regenerate keeps it
byte-intact, and the header carries `Apps read:` in the form of `Backend read:`. `prove-branch`
reads the table to class a state: steps are a missing account that names `/qa:setup-states`, a
step `none` row is Unable to verify with the row's reason, and no row is unknown.

**The chain is read from another repo, and end-to-end specs are a source for it.** The screen, the
control and its label come from the UI code of the app that owns the step. The project's
end-to-end specs are a permitted source for the order and the preconditions of a chain, and for
nothing else in the file. 0022's rule that a test is never a substitute for a condition in the page
stays as written for the other four tables.

**`setup-states` may create data, and the reasons in 0022 do not reach it.** Both reasons were
about a tester that judges. `setup-states` judges nothing: it observes the state afterwards and
writes an `accounts.md` row only when it sees the state. It is not on the path of a run either: a
run of `prove-branch` reads rows and never starts it. `prove-branch` still never creates data,
never performs a chain and never starts a search.

**The risk `setup-states` does carry is writes to a shared staging environment, and five write
rules answer it.** They apply to every step it performs, and a project opts in once through the
adapter before any step is performed.

1. It creates items only, and every name it types starts with `qa-setup`.
2. It never changes or removes an item it did not create in this run. A step that changes an
   existing item, or an org-wide setting, is printed for the developer and not performed.
3. It never enters payment details. A chain with an online payment stops at that step and prints
   the remaining steps.
4. It signs in only through the saved sessions of roles the adapter lists.
5. It asks once per run, and the question lists every item it will create.

## Considered and dropped

- **Let `prove-branch` perform a chain when a state has no account.** It is the tester writing the
  data it judges, which is the first reason 0022 gave, and it puts the chain on the critical path
  of every run.
- **Keep the chain in the sibling app's knowledge file and join two files at read time.** The code
  of a producer app holds no reference to the page that shows the state, so a producer-side row has
  no source. The chain is written into the consumer's file.
- **Ask the developer which app makes which state at setup.** A developer's belief about that was
  wrong on the run behind PRD #301.

## Consequences

- A four-table `KNOWLEDGE.md` stays valid and reads as "no chain known for any state".
- A derive or a regenerate never searches for a chain, so the cost of a search is paid on demand,
  for named states only.
- A state whose cell says it needs time to pass or a payment to fail keeps its existing clause and
  is offered no search.
- `qa` moves to `0.6.0`.
