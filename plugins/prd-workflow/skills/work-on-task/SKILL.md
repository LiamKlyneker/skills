---
name: work-on-task
description: >
  Implement one `to-task` issue end to end with a fidelity self-audit. Reads the
  brief's fidelity ledger, every design screenshot and every prototype source slice
  before writing code, implements per the issue's Instruction column, and closes with
  a per-ledger-row self-audit before the verify gate. Use when the user hands over a
  single issue published by to-task. Invoke /prd-workflow:work-on-task <issue-url>.
---

# Work On Task

```
/prd-workflow:work-on-task <issue-url-or-number>
/prd-workflow:work-on-task <local-issue-path>
```

Takes **one** issue published by `to-task` and implements it end to end: evidence first, code second,
self-audit third, verify gate fourth, one commit, one final print.

This is the implementer half of the design-fidelity pipeline. `to-task` guarantees the issue carries
the brief's ledger rows verbatim, a screenshot fetch line per state and a source-slice fetch line per
`local component` / `DS with overrides` row. This skill's whole job is to make sure that evidence is
actually **read** before any code exists, and that the finished code is audited back against it row
by row.

Run 1 failed here. The implementer worked from the issue prose plus the screenshots, never opened
the brief or the prototype source, and never checked its own output against the ledger. Everything
the ledger knew about icon sizes, hotspots, nesting and type tokens was lost in that one hop.

**Who runs this.** Normally an **Opus worker session under a judging orchestrator** (Fable), not an
interactive human session. The orchestrator does not watch the work; it reads the **final print**
and scores it. Everything a judge needs — the self-audit table, the deviation list, the verify
result — lives in that print. Nothing load-bearing may exist only in mid-session narration.

## Inputs

| Input         | Where it comes from                                                                                                  |
| ------------- | -------------------------------------------------------------------------------------------------------------------- |
| `<issue>`     | the argument — a URL (`https://github.com/<owner>/<repo>/issues/N`), `#N`, bare `N`, or a path to an existing local file (the `to-task --out` shape). Strip query strings. |
| The issue     | `gh issue view` for a URL/number; the file's own contents, read directly, for a local path. Source of the ledger rows, the decisions, `## Changes`, and both fetch-line sets either way. |
| The brief     | the path the issue names (e.g. `.claude/briefs/FUS-8965-run2.md`). Source of the **full** `## Fidelity ledger`.      |
| Project facts | `<repo-root>/.claude/project/adapter.md` — tracker, branch pattern, L2 floor, repo discipline. Never hardcode these. |

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
   `Issue tracker / PRs:` row. A PR instead of an issue, or a closed issue → stop and say so.

2. **Locate the brief.** The issue body names its brief path and its pinned prototype
   `<owner>/<repo>@<sha>` + path. Resolve the brief path against the repo root and confirm the file
   exists.

3. **Stop conditions — refuse to start, do not improvise around any of them:**

   - the issue has **no `## Fidelity ledger (in scope)` table**, or the table has no rows;
   - the issue has **no screenshot fetch lines**, or **no source-slice fetch lines** for its
     `local component` / `DS with overrides` rows;
   - the brief path the issue names does not exist, or has no `## Fidelity ledger` section.

   Any of these means the issue was not produced by a current `to-task`. Report which one and stop.
   An issue without evidence is prose, and implementing from prose is the failure this pipeline
   exists to stop.

4. **Branch.** Read the adapter's `Branch pattern:` row and work on a branch matching it, cut from
   the base the run procedure names (a fixed-scorecard file, where the adapter's `Fixed scorecard`
   row names one, also names the baseline commit). Already on a matching branch → stay on it. Never work on the default branch.

5. **Scoped context.** Read the `CONTEXT.md` files scoped to the directories the issue touches,
   per the adapter's `## Repo discipline` row.

## Before any code

The evidence gate is normative in `../_shared/fidelity-ledger.md` §6 — read it and run it as
written, and state its one-line evidence statement before any file is created or edited.

## Implementing

- **Work the issue's `## Changes` in order**, each against its cited ledger row and the row's
  **Instruction** column. The Instruction says what to build (`build local X`, `use Y + override Z`,
  `use as-is`); the ledger row and the source slice say what it must look like.
- **Layout facts and icon names** — per `../_shared/fidelity-ledger.md` §6.
- **Translate facts into classes yourself** — that is this session's job, and the reason `to-task`
  is forbidden from doing it. A px fact resolves to a DS token where it equals a named token on
  that tier of the project's design-system catalog — token membership, never grid arithmetic, since
  a scale may hold a 1px hairline alongside its 4px or 8px steps. Otherwise it resolves to an
  arbitrary value **only where the issue records a grill decision permitting that value for that
  element**. A `⚠ off-grid` flag on the ledger row raises the question — it is not the permission.
  Where the source slice already holds a class, prefer copying it over re-deriving it.
- **An off-grid fact with no recorded grill decision is a stop.** Halt and ask. Shipping the raw
  value and quietly substituting the nearest token are both wrong: one puts a value the shared UI
  standard forbids into the component, the other makes a design decision the human never made.
- **Do not substitute a component.** If the Instruction says build local, build local — do not reach
  for the DS primitive that "would do the same thing". Each of `IconButton`, `LabelButton`, `Input`,
  `Badge` and `PopoverContent` ships chrome (rings, pill hovers, default sizes, an arrow) that the
  design may not have.
- **House rules still apply** — `cn()`, `Controller`, no standard-tailwind text sizes, helper
  components at the end of the file, minimal `useEffect`. See `CLAUDE.md` / `CLAUDE.local.md`.

## Self-audit (before the verify gate)

Write the per-ledger-row self-audit table in `../_shared/fidelity-ledger.md` §6 — before running
L2, with the code in its finished state, one line per ledger row in scope, every row.

**The self-audit lists every arbitrary value the code kept** — each one with its ledger row, the
grill decision in the issue that permitted it, and the token it rejected. An arbitrary value with
no such line is a value nobody approved.

Then tick the issue's `## Verify` checkboxes **from the code**, per
`../_shared/fidelity-ledger.md` §6 — scorecard rows and polish items get `expected pass` or
`cannot tell from code`, and never `pass`. A scorecard row the issue derived from the ledger (§5,
for a ticket with no fixed scorecard) is ticked exactly like a fixed one.

## Verify gate

1. **L2 — floor, non-negotiable** (the adapter's `## Verify ladder`):

   ```
   yarn ts-lint && TZ=UTC yarn test
   ```

   `TZ=UTC` matters — plain `yarn test` fails ~11 pre-existing timezone tests in
   `tests/registration/FinancialsStep.utils.spec.ts`. Do not chase those.

2. **Biome on the changed files only:**

   ```
   yarn biome:branch
   npx biome ci --changed --since=origin/main --no-errors-on-unmatched
   ```

3. Cypress is **not** a gate here — component specs need `@teamsnap/cypress-secrets` and integration
   specs need prism plus a booted app. Executing them is CI's and human QA's job.

4. **Debugging cap: three distinct approaches.** If the third has not landed the fix, stop and report
   the three and what you would try next. Do not start a fourth blindly.

## Commit

One commit, only after the gate is green. Never push, never open or touch a PR, never close the
issue, never touch labels.

- Subject ends with `(#N)` — this issue's number, as the last characters of the first line. A
  local-path `<issue>` carries no number; end the subject `(local)` instead.
- Conventional prefix and the Jira key, matching this repo's history:
  `feat: [FUS-XXXX] <what changed> (#N)`.
- Squash fixups locally **before** the commit exists; never amend a commit that already exists.
- End the message with the `Co-Authored-By` trailer this repo's git conventions require.

## Final print

This is what the judging orchestrator reads and scores. It is the deliverable — write it in full,
complete sentences, and put nothing load-bearing anywhere else.

In this order:

1. The one-line evidence statement: "read ledger (N rows), N screenshots, N source slices."
2. **The full self-audit table**, every row, unabridged.
3. **The deviation list** — one line per `deviated` row: the row, what the code does instead, why.
   Print `no deviations` explicitly when there are none; silence is not the same claim.
4. The scorecard and polish-checklist markings, `expected pass` / `cannot tell from code`.
5. The verify result: L2 outcome, biome outcome.
6. Files changed, and the commit sha + subject.
7. Anything the gate could not settle — a token trusted from the ledger but unverified in CSS, a
   screenshot that would not fetch, a fact the ledger and the screenshot disagree on and the call
   you made.

Do not summarise the issue back, and do not recap `## Changes`. The judge has the issue.
