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

## Then filter by title prefix

`[TASK]`, `[BUG]`, `[QA]` and `[PRD]` here are **shorthand for the adapter's *Title
prefixes* row** at `<repo-root>/.claude/project/adapter.md`. If that row names different
prefixes, they win.

Of the issues that survived the `## Parent` filter, keep the ones that are *implementable
work*:

- Title starts with `[TASK]` (a planned child) or `[BUG]` (a triaged finding) → **keep**.
- Title starts with `[QA]` → **drop, always**, fallback or not. A `[QA]` issue is one run's
  human QA pass, not work: it carries no `## Parent` and no `ready-to-start`, and picking one
  means handing a worker a checklist to implement. It is the only prefix excluded
  unconditionally, and it is excluded because the *cost of getting it wrong is asymmetric* —
  a dropped `[QA]` costs nothing, a picked one costs a whole worker run.
- Any other prefix, or none → subject to the fallback below.

**Legacy fallback, and read the keying carefully.** If **no** returned issue's title starts
with `[TASK]` or `[BUG]`, the prefixes were not in force when this PRD's children were
written. Skip this filter entirely — keep everything the `## Parent` step kept — and flag
`needs-backfill` so the gap is visible.

Two things about that condition are load-bearing:

- It is keyed on **`[TASK]`/`[BUG]` presence specifically**, never on "some issue has a
  bracket prefix". A legacy PRD that gains one `[QA]` issue from a run still has zero
  implementable prefixes in the set, so the fallback stays on and its real children stay
  visible. Keying it on any prefix would let that single `[QA]` issue switch the filter on and
  drop every genuine child at once.
- It is **set-level**, like the `## Parent` one above, and for the same reason: one prefixed
  issue proves the convention was in force, so an unprefixed sibling is an oversight to report
  rather than a child to keep. Never apply it per-issue.

The `[QA]` exclusion survives the fallback because it is not part of it — the fallback
answers "were prefixes in force here?", and a `[QA]` issue is evidence about *this run*, not
about the era the children were written in.

Report the issues you dropped and why, at both steps. A silently-dropped child looks
identical to a PRD with fewer slices than it has — and a whole PRD reporting zero children
right after this filter landed reads exactly like "run `/to-issues` first", which is the one
wrong conclusion available here.

## Parse each child body

The headings and "None…" sentinels below are a string contract with the writer — normative copy lives in `to-issues`'s issue template. Reword there first, never here alone.

- **External steps**: everything under `## External steps` until the next `## ` heading. Each `- [ ]` line is an unmet step; `- [x]` is met. The literal phrase "None — fully implementable from the editor" (or just "None") means no external steps. Section missing entirely → treat as "None" and flag `needs-backfill` (issue predates the template).
- **Blocked by**: everything under `## Blocked by` until the next `## ` heading. Collect every `#NNN` reference. "None" (or "None - can start immediately") means no blockers.

## State and labels

- **Open / done**: the issue's `state` from the `gh` response — `open` is open, `closed` is done. There is no third state.
- A `## Blocked by` entry that is a **PR** resolves fine via `gh`; merged or closed = done, so the blocker is satisfied.
- **Labels**: keep for state reconstruction (`ready-to-start`, `state:in-progress`, `state:done-on-branch`). The vocabulary is normative in `work-on-prd`'s `## Label vocabulary`.
- **Orchestrated-mode exception, observed**: `state:done-on-branch` is how a `work-on-prd` run shows that a child's commit is on the PRD branch — the condition the exception in `../_shared/eligibility-policy.md` turns on. `work-on-prd` specs its use at Loop step 1.
