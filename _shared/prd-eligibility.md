# PRD Child Eligibility — GitHub Mechanics

Shared by `next-prd-issue` and `work-on-prd`. Given a PRD issue number, find its child issues
and produce the facts eligibility runs on: how to fetch them, how to parse a body, and how
GitHub state and labels map onto open/done.

**The rules themselves live in `../_shared/eligibility-policy.md`** — eligible = open ∧ every
blocker done, cycle detection, the orchestrated-mode exception, picking order, never batch.
Read both; this file alone does not decide a pick.

Single source of truth for the mechanics below — do not copy them into skills; reference this file.

## Fetch (parallel `gh` calls, single message)

```
gh issue view <prd-number> --repo <repo> --json title,body,state,comments
gh api repos/<owner>/<repo>/issues/<prd-number>/sub_issues
```

The second call is the **authoritative and only** list of the PRD's children. `to-issues` links
each child to its PRD as a native sub-issue as it creates it, and `triage-prd` does the same for
each `[BUG]` it files; this endpoint reads those links back. It returns one object per child
carrying `number`, `title`, `state`, `body` and `labels` — everything the parsing below needs,
in one call.

**Everything it returns is a child by construction, so there is nothing to filter.** No body
search to sift, no `## Parent` section to match, no title prefix to keep or drop. An issue that
merely *mentions* `#<prd-number>` in prose is never returned, and neither is the PRD itself.

Three properties of the endpoint to hold on to:

- **Never read `sub_issues_summary` (`subIssuesSummary`) for control flow.** The parent's rollup
  — `total` / `completed` / `percent_completed` — is **eventually consistent**: observed still
  reporting `completed: 0` immediately after a child was closed, and only later reporting `1/3`
  for the same parent. Read each child's own `state` off the list instead; that is correct
  immediately. The rollup is fine to *display*, never to branch on.
- **Sub-issues come back in link order, not numeric order.** Immaterial in itself — the picking
  order in `../_shared/eligibility-policy.md` sorts explicitly — but do not read the returned
  order as meaning anything, and do not assume `#41` precedes `#42`.
- **No result cap to set by hand.** There is no `--limit` here (the old body-search fetch needed
  one); GitHub caps a *parent* at **100 sub-issues**, which is the only ceiling and far above any
  PRD's slice count.

**Zero children returned** means nothing was ever linked — either the PRD has not been sliced, or
it was sliced and the links were never written. Both are fixed by linking, never by re-slicing:
re-running `/to-issues` on a PRD that already has children doubles every child. The consuming
skills own the exact message.

## Parse each child body

The headings and "None…" sentinels below are a string contract with the writer — normative copy lives in `to-issues`'s issue template. Reword there first, never here alone.

- **External steps**: everything under `## External steps` until the next `## ` heading. Each `- [ ]` line is an unmet step; `- [x]` is met. The literal phrase "None — fully implementable from the editor" (or just "None") means no external steps. Section missing entirely → treat as "None" and flag `needs-backfill` (issue predates the template).
- **Blocked by**: everything under `## Blocked by` until the next `## ` heading. Collect every `#NNN` reference. "None" (or "None - can start immediately") means no blockers.

## State and labels

- **Open / done**: the issue's `state` from the `gh` response — `open` is open, `closed` is done. There is no third state.
- A `## Blocked by` entry that is a **PR** resolves fine via `gh`; merged or closed = done, so the blocker is satisfied.
- **Labels**: keep for state reconstruction (`ready-to-start`, `state:in-progress`, `state:done-on-branch`). The vocabulary is normative in `work-on-prd`'s `## Label vocabulary`.
- **Orchestrated-mode exception, observed**: `state:done-on-branch` is how a `work-on-prd` run shows that a child's commit is on the PRD branch — the condition the exception in `../_shared/eligibility-policy.md` turns on. `work-on-prd` specs its use at Loop step 1.
