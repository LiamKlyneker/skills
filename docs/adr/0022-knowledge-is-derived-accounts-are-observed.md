# ADR 0022 — Knowledge is derived, accounts are observed

- **Status**: Accepted
- **Date**: 2026-10-27
- **Context**: PRD #237, implemented from #238 on

## Context

`qa:prove-branch` knows the ticket and the diff, and nothing about the app. A flow that needs a
page in a particular data state — a plan with a waitlisted registrant, an order with three
participants — needs to know which role sees that screen, what data makes the section render, and
which staging account already holds such data. On its first real run the pass stopped and asked the
developer for a URL, an org id and an order number, and the answer landed in that run's folder,
where the next run could not find it.

The adapter's *State catalog* row was the place this knowledge was meant to live, and its case is
stated here first. One hand-written table in the adapter keeps every project fact in one file, which
is the rule the adapter exists for; it needs no new skill, no new file and no new writer; and a
developer who knows the app can fill it in minutes. For a small app with a handful of states that
holds.

It did not hold on the project where the pass ran. The row read `none`. One table cannot hold a
whole app, nobody fills it, and it goes stale the first time staging data moves. It also mixes two
kinds of fact. *Which section shows for which role under which data state* is written down in the
page's render conditions and in the backend rules the page reads, and it changes when the code
changes. *Which staging org holds a plan in that state, and by which id* is written down nowhere,
and it changes when somebody edits staging data.

## Decision

**Two files, split by how each one drifts.** The formats are defined once each, in
`plugins/qa/skills/references/knowledge-file.md` and
`plugins/qa/skills/references/accounts-file.md`; no skill restates them.

- **Knowledge is derived from code and regenerable.** A page's `KNOWLEDGE.md` sits in the page
  folder and states, in user words only, what the user sees and can do, the data states behind
  both, and the open questions the repos cannot answer. `qa:build-knowledge` derives it from the
  page and the backend repos and may rewrite every row whose origin is `code` at any time. Rows from
  a backend repo, an observed run or a developer are never rewritten by a regenerate.
- **Accounts are observed and only grow.** A project's `accounts.md` sits beside the adapter and
  records which staging org the pass uses and which page states are known to exist there, with the
  proving ids and a last-verified date. Rows are never deleted; a state that is no longer visible is
  marked stale and resolves no flow.
- **The two never live in one file, because they drift differently.** Knowledge drifts with the
  code and is corrected by a regenerate. Accounts drift with staging data and are corrected by a
  re-verification. One file would need both corrections, and a regenerate that rewrites code-derived
  rows has no business near a row a human verified against staging last week.
- **`accounts.md` has three writers and no others.** `qa:setup` writes the empty skeleton and the
  adapter pointer. `qa:setup-states` writes every observed row. `qa:prove-branch` writes a row only
  when the developer answers a gap during a run. `qa:build-knowledge` never touches it, because it
  reads code and never looks at staging.
- **Knowledge belongs to a page, not a feature.** An epic describes one feature at one time and
  drifts; the page outlives every ticket, and a diff that touches the page folder is what reopens
  its file.
- **The pass never creates data.** Three levels were considered: use known accounts only; run a
  named seeder when no account has the state; run it and record what it created. Only the first is
  built. A flow whose state has no account is a stop naming `setup-states`, or Unable to verify when
  the state cannot be made in the app at all. The knowledge file's `Seeder (for a human)` column
  stays as a hint for a human, because for a few states — set in another application, needing time
  to pass, needing a payment failure — it is the only fast path, and it is never a default.

## Considered and dropped

- **Keep the *State catalog* row and make setup ask harder.** The row's failure was not that nobody
  was asked; it is that one table in a config file cannot hold an app's states and has no way to
  notice it has gone stale.
- **One knowledge file per project, or per feature.** A project file grows without bound and is
  reopened by every diff; a feature file describes the feature as it was when the ticket closed.
- **Account ids inside `KNOWLEDGE.md`.** It puts staging facts under a regenerate and makes a
  tracked file change every time staging data moves. The knowledge file's `Known account` cell is a
  pointer, never a copy.
- **Let the pass run the seeder (levels two and three).** It makes an external tester a writer of
  the data it judges, and puts a project's seeding machinery on the critical path of every run.

## Consequences

- The adapter's *State catalog* row goes, from the `## QA` section, the template, the interview and
  `doctor.sh`, and `## QA` gains one row pointing at `accounts.md`.
- A new branch meets at most two stops before the gate — one naming `build-knowledge`, one naming
  `setup-states` — and a branch that touches a known page with known states meets none.
- Open questions are expected in every knowledge file whose page reads permissions from an API. A
  file with none on such a page is a file that guessed.
- A regenerate that renumbers a state id leaves `accounts.md` rows citing the old id until
  `setup-states` re-verifies them, since `build-knowledge` never writes that file. The regenerate
  prints every renumbering so a human sees it.
- The browser readiness check and the consent read move to
  `plugins/qa/skills/references/browser-readiness.md`, so `prove-branch` and `setup-states` read one
  copy.
