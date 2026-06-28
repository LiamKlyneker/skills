---
name: next-prd-issue
description: Pick the next child issue to implement from a PRD on the project issue tracker. Use when the user wants to continue implementing a PRD, asks "what's next" on a PRD, or passes a PRD URL/issue number to start the next slice. Reads `## External steps` and `## Blocked by` from each child to recommend the next single issue.
---

# Next PRD Issue

Recommend the next child issue to implement from a PRD. Reasons over the open children, respects `## Blocked by`, surfaces any `## External steps` the user must do in-session, and is token-conscious. Issues are PR-sized after the `/to-issues` rewrite, so this skill recommends one issue at a time — never a batch.

This skill **does not** implement, close issues, or toggle plan mode. It ends at a recommendation. The user decides whether to enter plan mode and start work.

## Process

### 1. Resolve the PRD

Argument may be a URL (`https://github.com/<owner>/<repo>/issues/N`), `#N`, or bare `N`. Strip query strings.

- If a URL is passed, derive `<owner>/<repo>` from it.
- Otherwise default `--repo` to the project's primary repo (`creativeghosts/neonplace` in this workspace, or whatever the user's `gh` default is — let `gh` resolve it).
- If no argument and no obvious PRD in conversation context: ask the user for a PRD reference. Do not guess.

Validate the issue exists and is an issue (not a PR). If it's a PR, stop and tell the user.

### 2. Fetch state in parallel

Run these `gh` calls in a single message (parallel Bash tool calls):

```
gh issue view <prd-number> --repo <repo> --json title,body,state,comments
gh issue list --repo <repo> --search "in:body \"#<prd-number>\" -is:pr" --state all --limit 50 --json number,title,state,body
```

The search may include the PRD itself — filter it out by number.

### 3. Parse each child

For each child issue body, extract:

- **External steps**: read everything under `## External steps` until the next `## ` heading. Collect each `- [ ]` line as a bullet. The literal phrase "None — fully implementable from the editor" (or just "None") means no external steps. If the section is missing entirely, treat as if "None" and flag `needs-backfill` in the output (the issue predates the new template).
- **Blocked by**: read everything under `## Blocked by` until the next `## ` heading. Collect every `#NNN` reference. The literal phrase "None" (or "None - can start immediately") means no blockers.
- **State**: `open` | `closed` from the gh response.

### 4. Compute eligibility

A child is **eligible** when:

- It is `open`, AND
- Every issue listed in its `## Blocked by` is `closed`.

Closed children are tracked for the count summary but never recommended.

Walk the `Blocked by` graph to detect cycles. On a cycle, report the cycle and stop — do not recommend anything.

### 5. Recommend an issue

Apply rules in order:

1. **No eligible issues** → report "all open children are blocked" and show the blocking chain. Stop.
2. **One eligible issue** → recommend it.
3. **Multiple eligible** → recommend the issue with the smallest `## External steps` list (less context-switching). Tie-break by lowest issue number (oldest first). Never batch — issues are already PR-sized after the `/to-issues` rewrite.

### 6. Judge model / effort / plan mode

Read `../_shared/model-effort-heuristics.md` and apply it to the recommended issue. Produce three outputs: plan-mode y/n, model tier, effort. This is a downgrade detector against the operator's Opus-high default — flag loudly when it's safe to go lighter, otherwise confirm staying on the default. Speak in tiers; if exact model ids are needed, defer to `claude-api`. Hedge borderline calls.

### 7. Print the recommendation

Use this exact structure (omit empty sections):

```
PRD: #<n> <title>     [<open> open / <closed> closed children]

Recommended next: #<n> <title>

Why: <one-line reason>

External steps you'll need to do in-session:
  - [ ] <bullet from issue's `## External steps` section>
  - ...

(Or "None — fully implementable from the editor.")

Other eligible right now:
  #<n> <title>  — <one-line reason it wasn't picked, e.g. "more external steps">

Blocked, waiting for upstream:
  #<n> <title>  blocked by #<n>[, #<n>...]

Needs backfill (## External steps section missing — predates template change):
  #<n> <title>

Token-conscious note:
  <one to three lines explaining size/risk: e.g. "#244 spans lib/ai/ scaffolding, /api/chat refactor, and the collection chat builder — ~300+ LOC across 6 files. Plan accordingly.">

Model/effort: <tier> · <effort>   (<downgrade from default | stay on default | borderline>)
  Why: <matched signals from the heuristics — no score>
Plan mode: <yes | optional> — <one-line reason>

Suggested next step:
  Switch to the recommended model/effort if it differs from your current session, then enter plan mode and implement #<n>. After the PR merges and you've verified in prod, close the issue on GitHub and re-run /next-prd-issue.
```

### 8. Stop here

Do not enter plan mode. Do not begin implementation. Do not edit code. Do not close the issue. The user reads the recommendation (including the model/effort call) and decides what to do.

## Edge cases

- **PRD has no open children** → "All children closed. Consider a wrap-up comment on the PRD summarizing what shipped."
- **PRD has zero children at all** → tell the user to run `/to-issues` first.
- **`## Blocked by` references a PR number, not an issue** → `gh` resolves either; treat merged/closed as unblocked.
- **A blocker references an issue from a different PRD** → still respected; only state matters.
- **Closed issue listed in another's `Blocked by`** → not blocking; ignore.
- **`## External steps` missing on a child** → treat as if "None", flag in output. Issue predates the template change; user can backfill manually if it matters.
- **Argument is a PR URL, not an issue** → stop and ask for an issue.
- **Multiple PRDs at once** → not supported in v1; one PRD per invocation.

## Project conventions to respect

- Be extremely concise per `CLAUDE.md`. Sacrifice grammar for concision in the output.
- Recommend plan mode before implementation — the user prefers it for non-trivial work.
- Model/effort is a recommendation only, decided at pickup — never written back into the issue body (the lineup churns; see `../_shared/model-effort-heuristics.md`).
- Never modify the PRD or any child issue from this skill.
