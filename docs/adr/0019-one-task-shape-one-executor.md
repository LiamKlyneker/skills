# ADR 0019 — One task shape, one executor

- **Status**: Accepted
- **Date**: 2026-10-22

## Context

`prd-workflow` had two ways to get one piece of work built, from two eras.

The manual era: `next-prd-issue` recommended the next eligible child of a PRD, and `work-on-issue`
ran a readiness gate on one issue and then entered plan mode to plan it. Both predate `deep-grill`,
which now settles the plan before any issue exists, and `work-on-prd`, which picks and runs a PRD's
children as a loop. A human picking the next child by hand and a session planning an issue that was
already planned are both steps the current flow does for itself.

The design-fidelity era: `to-task` filed one standalone issue from a grill, and `work-on-task`
implemented it. `to-task` refused to run without a design brief and a fidelity ledger, so it could
not file an ordinary single task — a refactor or a bug fix with no design behind it. In use it
stopped on four blockers: no ledger, no brief, no ticket key, no fidelity decisions. It also asked
for confirmation before filing, though the body is written for a worker to execute and the human
never reads it.

And the task body had two templates: `to-issues` wrote a PRD child's body inline, and `to-task`
wrote a different one inline. The headings the loop parses lived in one of them only.

## Decision

**Two routes, one shape.**

```
PRD flow:     deep-grill → to-prd → to-prd-tasks → work-on-prd
Single flow:  deep-grill → to-task → work-on-task
After either: manual-qa → triage
```

- **One task body**, in `plugins/prd-workflow/skills/references/task-body.md`: core sections every
  task carries, standalone sections only `to-task` writes (a task with no PRD has nowhere else to
  hold its summary, its decisions and its out-of-scope list), and fidelity sections only when a
  brief or a PRD ledger exists. A section a writer does not use is omitted, never stubbed. The file
  is plugin-local because `_shared/` holds no templates.
- **`to-task` files any task.** The brief and the ticket key are optional. Without a brief the task
  has no fidelity sections and the fidelity hard rules do not apply; with one, ledger mode is
  unchanged. It stops only on a decision the consensus left open.
- **`to-task` files without confirmation.** The body is machine-read; a confirmation step showed a
  human a document they had no reason to read, and approval of the decisions already happened in
  the grill.
- **`work-on-task` is the one executor for a single task**, from `to-task` or a PRD child. It
  absorbs `work-on-issue`'s readiness gate — open blocker, unchecked external step, a `[PRD]` title,
  a closed issue, an open question — and runs the fidelity evidence gate and self-audit iff the task
  carries a `## Fidelity ledger (in scope)` table.
- **`work-on-issue` and `next-prd-issue` are deleted.** `deep-grill` plans and the loops pick.
- **`to-issues` is renamed `to-prd-tasks`.** The name says what it writes — the `[TASK]` children
  of a PRD — and mirrors the ADO side's `to-spec` → `to-spec-tasks` → `work-on-spec`.
- **`work-on-task` enters no plan mode and spawns no subagents.** The plan is the task body. Whether
  a session delegates is the operator's model rule, decided by the session's model, not by a skill.
- **`work-on-task` names no project's tooling.** The verify gate runs the adapter's L2 command and
  the gates the adapter registers; house rules come from the repo's `CLAUDE.md`.

## Considered and dropped

- **Keep `work-on-issue` for PRD children.** Two executors for one body shape would drift, and the
  readiness gate is the only part of it the current flow still needs.
- **Keep the confirmation step behind a flag.** Nothing reads the body before a worker does; a
  flag preserves a step nobody takes.
- **Put the task body under `_shared/`.** `_shared/` is global reference with no templates, and only
  `prd-workflow` writes this body; ADO keeps its own shapes under `ado-workflow/skills/references/`.

## Consequences

- `prd-workflow` moves to 2.0.0: two skills a consumer could invoke are gone.
- An issue `to-task` wrote before this change still runs under `work-on-task` — absent sections are
  not blockers, and a fidelity issue carries the table that switches fidelity mode on.
- `prd-worker` does not follow the `work-on-task` contract yet; aligning them is separate work.
- `ado-workflow:next-task-to-implement` is the ADO side's manual-era picker and is untouched here.
