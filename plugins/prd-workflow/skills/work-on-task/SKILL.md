---
name: work-on-task
description: >
  Implement one task end to end — any `[TASK]` issue (from to-task or a PRD child) or a
  local issue file. Runs a readiness gate, a fidelity evidence gate when the task carries a
  ledger, implements, verifies, commits once. Use when the user hands over a single issue
  to build. Invoke /prd-workflow:work-on-task <issue-url-or-path>.
---

# Work On Task

```
/prd-workflow:work-on-task <issue-url-or-number>
/prd-workflow:work-on-task <local-issue-path>
```

Takes **one** task and implements it end to end: readiness gate, evidence (when the task carries a
ledger), code, verify gate, one commit, one final print.

The task's shape is `../references/task-body.md`. The task carries a **`## Fidelity ledger (in
scope)` table** or it does not, and that one fact decides the mode:

- **Fidelity mode** — the table is present. The evidence gate, the per-row self-audit and the
  scorecard markings all apply. An implementer that works from the issue prose plus the screenshots,
  without opening the brief or the prototype source, loses every layout fact the ledger held; the
  evidence gate exists to stop that.
- **Plain mode** — no table. The evidence gate and the self-audit are skipped entirely.

**Who runs this.** Any session — interactive, or a worker under an orchestrator that reads only the
**final print**. Everything a reader needs to judge the run lives in that print. Nothing
load-bearing may exist only in mid-session narration.

## Inputs

| Input         | Where it comes from |
| ------------- | ------------------- |
| `<issue>`     | the argument — a URL (`https://github.com/<owner>/<repo>/issues/N`), `#N`, bare `N`, or a path to an existing local file (the `to-task --out` shape). Strip query strings. |
| The issue     | `gh issue view` for a URL/number; the file's own contents, read directly, for a local path. |
| The brief     | fidelity mode only — the path the issue names. Source of the **full** `## Fidelity ledger`. |
| Project facts | `<repo-root>/.claude/project/adapter.md` — tracker, title prefixes, branch pattern, verify ladder, project gates, repo discipline. Never hardcode these. |

## Preflight

1. **Resolve and fetch the issue.**

   `<issue>` names an existing local file → read it directly as the issue body; there is no
   number, no state and no labels, so nothing here is fetched and nothing is closed later. This
   is the shape `to-task --out` writes, for a sandbox with no network and no tracker credential.

   Otherwise:

   ```
   gh issue view <n> --repo <repo> --json number,title,body,state,labels,url
   ```

   URL → derive `<owner>/<repo>` from it. Otherwise take the tracker from the adapter's
   `Issue tracker / PRs:` row.

2. **Readiness gate.** The task is **not ready** if any of these hold:

   - **Not an issue, or closed** — a PR rather than an issue, or `state` is `closed`.
   - **A PRD, not a task** — the title starts with the adapter's `[PRD]` prefix (`## Repo` →
     *Title prefixes*). A PRD is the parent, not a slice to build; `/prd-workflow:work-on-prd`
     runs it.
   - **Blocked** — `## Blocked by` names an open `#N`. Check each one's state with `gh`; a local
     file names nothing `gh` can check, so any `#N` there counts as open.
   - **Unmet external steps** — `## External steps` has an unchecked `- [ ]` item. Those are
     actions a human does outside the editor before the work can start.
   - **No clear scope** — the body is empty, a stub, or says nothing about what to build or what
     "done" looks like.
   - **An open question** — the body raises a decision the task, the codebase and the adapter
     cannot answer.

   `## Blocked by` and `## External steps` are optional, and their absence is not a blocker. So is
   a missing title prefix: `[PRD]` is the only prefix that refuses.

   Not ready → change no file, create no branch, and print this, then stop:

   ```
   Not ready — #<n> <title>. Need:
     - <missing thing 1>
     - <missing thing 2>
   ```

   A local file has no number: use `Not ready — <path> <title>.` Each `Need:` line names one
   specific gap and nothing else. This print has no closing command line, because the next move is
   the human's answer, not a skill.

3. **Fidelity mode — iff the issue has a `## Fidelity ledger (in scope)` table.** Then the issue
   names its brief path and its pinned prototype `<owner>/<repo>@<sha>` + path. Resolve the brief
   path against the repo root. Refuse to start, and do not improvise around any of these:

   - the table has no rows;
   - the issue has **no screenshot fetch lines**, or **no source-slice fetch lines** for its
     `local component` / `DS with overrides` rows;
   - the brief path the issue names does not exist, or has no `## Fidelity ledger` section.

   Report which one and stop. In plain mode, skip this step.

4. **Branch.** Read the adapter's `Branch pattern:` row and work on a branch matching it, cut from
   the base the run procedure names (a fixed-scorecard file, where the adapter's `Fixed scorecard`
   row names one, also names the baseline commit). Already on a matching branch → stay on it. Never
   work on the default branch.

5. **Scoped context.** Read the `CONTEXT.md` files scoped to the directories the issue touches,
   per the adapter's `## Repo discipline` row.

## Before any code

**Fidelity mode only.** The evidence gate is normative in `../_shared/fidelity-ledger.md` §6 — read
it and run it as written, and state its one-line evidence statement before any file is created or
edited.

## Implementing

In every mode:

- **Work `## What to build` — or `## Changes` — in order**, against `## Acceptance criteria`, using
  the paths and prior art in `## Worker context`.
- **Do not substitute a component.** Use the design-system primitive the issue names, and no other;
  where it says build local, build local. A DS primitive that "would do the same thing" ships its
  own chrome, which the design may not have.
- **House rules apply** — follow the repo's `CLAUDE.md` (and `CLAUDE.local.md`, where present).

In fidelity mode, also:

- **Work each `## Changes` entry against its cited ledger row** and the row's **Instruction**
  column. The Instruction says what to build (`build local X`, `use Y + override Z`, `use as-is`);
  the ledger row and the source slice say what it must look like.
- **Layout facts and icon names** — per `../_shared/fidelity-ledger.md` §6.
- **Translate facts into classes yourself** — that is this session's job, and the reason `to-task`
  is forbidden from doing it. A px fact resolves to a DS token where it equals a named token on
  that tier of the project's design-system catalog — token membership, never grid arithmetic, since
  a scale may hold a 1px hairline alongside its 4px or 8px steps. Otherwise it resolves to an
  arbitrary value **only where the issue records a grill decision permitting that value for that
  element**. A `⚠ off-grid` flag on the ledger row raises the question — it is not the permission.
  Where the source slice already holds a class, prefer copying it over re-deriving it.
- **An off-grid fact with no recorded grill decision is a stop.** Halt: write no code for it, and
  end with the final print, which states that the run stopped, names the flagged fact and its raw
  value, and says the issue records no decision for it. Then ask. Shipping the raw value and quietly
  substituting the nearest token are both wrong: one puts a value the shared UI standard forbids
  into the component, the other makes a design decision the human never made.

## Self-audit (before the verify gate)

**Fidelity mode only.** Write the per-ledger-row self-audit table in `../_shared/fidelity-ledger.md`
§6 — before running L2, with the code in its finished state, one line per ledger row in scope,
every row.

**The self-audit lists every arbitrary value the code kept** — each one with its ledger row, the
grill decision in the issue that permitted it, and the token it rejected. An arbitrary value with
no such line is a value nobody approved.

Then tick the issue's scorecard and polish checkboxes — in `## Verify`, or in `## Acceptance
criteria` for a PRD child — **from the code**, per `../_shared/fidelity-ledger.md` §6. They get
`expected pass` or `cannot tell from code`, and never `pass`. A scorecard row the issue derived from
the ledger (§5, for a ticket with no fixed scorecard) is ticked exactly like a fixed one.

## Verify gate

1. **L2 — floor, non-negotiable.** Run the adapter's `## Verify ladder` L2 command verbatim.
2. **Further gates.** Run any further gate the verify ladder or the adapter's `## Project gates`
   registry names for the files this task changed.
3. **L3** — per the verify ladder: run it where the ladder says it applies to a User-visible task,
   and say so where the ladder defers it.
4. **Debugging cap: three distinct approaches.** If the third has not landed the fix, stop and report
   the three and what you would try next. Do not start a fourth blindly.

## Commit

One commit, only after the gate is green. Never push, never open or touch a PR, never close the
issue, never touch labels.

- Subject ends with `(#N)` — this issue's number, as the last characters of the first line. A
  local-path `<issue>` carries no number; end the subject `(local)` instead.
- A conventional prefix, plus the ticket key when the task title carries one, matching this repo's
  history.
- Squash fixups locally **before** the commit exists; never amend a commit that already exists.
- End the message with the `Co-Authored-By` trailer this repo's git conventions require.

## Final print

This is what a reader judges the run by. It is the deliverable — write it in full, complete
sentences, and put nothing load-bearing anywhere else.

A run that stops after preflight still ends with this print: it opens by saying the run stopped
and why, then carries every item below that the run reached — in fidelity mode, item 1 always.

In this order:

1. *(fidelity mode)* The one-line evidence statement: "read ledger (N rows), N screenshots, N source
   slices."
2. *(fidelity mode)* **The full self-audit table**, every row, unabridged.
3. **The deviation list** — one line per departure from the task: in fidelity mode each `deviated`
   row; in plain mode each change or criterion the code does not meet as written. The item, what
   the code does instead, why. Print `no deviations` explicitly when there are none; silence is not
   the same claim.
4. *(fidelity mode)* The scorecard and polish-checklist markings, `expected pass` / `cannot tell
   from code`.
5. The verify result: L2 outcome, and the outcome of every further gate that ran.
6. Files changed, and the commit sha + subject.
7. Anything the gate could not settle — in fidelity mode, a token trusted from the ledger but
   unverified in CSS, a screenshot that would not fetch, a fact the ledger and the screenshot
   disagree on and the call you made.

Do not summarise the issue back, and do not recap the change list. The reader has the issue.
