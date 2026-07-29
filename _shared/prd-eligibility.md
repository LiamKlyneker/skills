# PRD Child Eligibility — GitHub Mechanics

Shared by `next-prd-issue` and `work-on-prd`. Given a PRD issue number, find its child issues
and produce the facts eligibility runs on: how to fetch them, which returned issues are real
children, how to parse a body, and how GitHub state and labels map onto open/done.

**The rules themselves live in `../_shared/eligibility-policy.md`** — eligible = open ∧ every
blocker done, cycle detection, the orchestrated-mode exception, picking order, never batch.
Read both; this file alone does not decide a pick.

Single source of truth for the mechanics below — do not copy them into skills; reference this file.

## Fetch (parallel `gh` calls, single message)

```
gh issue view <prd-number> --repo <repo> --json title,body,state,comments
gh issue list --repo <repo> --search "in:body \"#<prd-number>\"" --state all --limit 50 --json number,title,state,body,labels
```

(No `-is:pr` qualifier — `gh issue list` already excludes PRs and current `gh` rejects PR qualifiers here.)

The search may include the PRD itself — filter it out by number.

## Filter to real children (do this before parsing)

The search is a **substring match on the issue body**, so it returns every issue that
merely *mentions* `#<prd-number>` in prose — a sibling issue writing "unrelated to #16",
an old audit issue citing it, a cross-reference in either direction. Those are not
children, and picking one means working an issue the PRD explicitly scoped out.

Keep an issue only when its `## Parent` section names this PRD:

- `## Parent` present and it references `#<prd-number>` → **child**.
- `## Parent` present and it references a *different* issue → **not a child**, always.
- `## Parent` absent → not a child, *unless* the fallback below applies.

**Legacy fallback**: if no returned issue has a `## Parent` section at all, the PRD's
children predate the section being written and the substring match is all there is —
use it, and flag `needs-backfill` on the result so the gap is visible. Do not apply the
fallback per-issue: one issue in the set carrying `## Parent` proves the convention was
in force when these issues were written, so an issue lacking it is a mention, not a child.

Report the issues you dropped and why. A silently-dropped child looks identical to a PRD
with fewer slices than it has.

## Parse each child body

The headings and "None…" sentinels below are a string contract with the writer — normative copy lives in `to-issues`'s issue template. Reword there first, never here alone.

- **External steps**: everything under `## External steps` until the next `## ` heading. Each `- [ ]` line is an unmet step; `- [x]` is met. The literal phrase "None — fully implementable from the editor" (or just "None") means no external steps. Section missing entirely → treat as "None" and flag `needs-backfill` (issue predates the template).
- **Blocked by**: everything under `## Blocked by` until the next `## ` heading. Collect every `#NNN` reference. "None" (or "None - can start immediately") means no blockers.

## State and labels

- **Open / done**: the issue's `state` from the `gh` response — `open` is open, `closed` is done. There is no third state.
- A `## Blocked by` entry that is a **PR** resolves fine via `gh`; merged or closed = done, so the blocker is satisfied.
- **Labels**: keep for state reconstruction (`ready-to-start`, `state:in-progress`, `state:done-on-branch`). The vocabulary is normative in `work-on-prd`'s `## Label vocabulary`.
- **Orchestrated-mode exception, observed**: `state:done-on-branch` is how a `work-on-prd` run shows that a child's commit is on the PRD branch — the condition the exception in `../_shared/eligibility-policy.md` turns on. `work-on-prd` specs its use at Loop step 1.
