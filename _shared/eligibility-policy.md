# Work-Unit Eligibility Policy

Tracker-agnostic. Given a parent document (a GitHub PRD, an Azure DevOps `[SPEC]`) and the
set of child work units under it, these rules decide which unit is eligible and which one to
pick next. They are identical on every tracker and live here once, so a fix lands in one
place instead of depending on remembering to apply it twice.

**Mechanics are per-tracker and are not repeated here**: how to fetch the children, how to
tell a real child from a mention, how to parse a body, how the tracker's own states map onto
open/done. Read this file *with* the mechanics document for the tracker you are on — neither
half decides a pick alone:

- GitHub — `../_shared/prd-eligibility.md`
- Azure DevOps — `../_shared/ado-eligibility.md`

Single source of truth for the rules below. Do not copy them into skills; reference this file.

## Eligibility

A child is **eligible** when:

- It is **open**, AND
- Every unit listed in its `## Blocked by` is **done**.

Open and done are tracker states; the mechanics document defines the mapping.

Done children count for summaries but are never picked. A blocker that is already done is not
blocking. Blockers **outside the current parent** are still respected — only the blocker's
state matters, never where it lives.

## Cycle detection

Walk the `Blocked by` graph. On a cycle, report the cycle and stop — do not pick anything.

## Orchestrated-mode exception

Inside an orchestrated run (`work-on-prd`, `work-on-spec`), a blocker **inside the parent
being run** also counts as satisfied once its commit exists on the run's branch. Children only
close on merge, so a strict done-only reading would deadlock the loop.

The relaxation holds only inside such a run — a recommendation-only skill (`next-prd-issue`,
`next-task-to-implement`) applies the strict rule. How "its commit exists on the branch" is
observed is mechanics, and each orchestrator specs it at its own pick step.

## Picking order (when multiple eligible)

1. Fewest unmet `## External steps` (less context-switching).
2. Tie-break: lowest work-unit id (oldest first).

One unit at a time — **never batch**. Units are worker-sized by construction, guaranteed by
the skill that wrote them.
