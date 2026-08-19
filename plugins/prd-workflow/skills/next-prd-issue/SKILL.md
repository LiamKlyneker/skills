---
name: next-prd-issue
description: Pick the next child issue to implement from a PRD on the project issue tracker. Use when the user wants to continue implementing a PRD, asks `what's next` on a PRD, or passes a PRD URL/issue number to start the next slice. Reads `## External steps` and `## Blocked by` from each child to recommend the next single issue.
---

# Next PRD Issue

Recommend the next child issue to implement from a PRD. Reasons over the open children, respects `## Blocked by`, surfaces any `## External steps` the user must do in-session, and is token-conscious. Issues are PR-sized after the `/to-issues` rewrite, so this skill recommends one issue at a time — never a batch.

This skill **does not** implement, close issues, or toggle plan mode. It ends at a recommendation — no plan mode, no edits, no closing. The user decides what to do with it.

## Process

### 1. Resolve the PRD

Argument may be a URL (`https://github.com/<owner>/<repo>/issues/N`), `#N`, or bare `N`. Strip query strings.

- If a URL is passed, derive `<owner>/<repo>` from it.
- Otherwise default `--repo` to the issue-tracker repo named in the **project adapter** at `<repo-root>/.claude/project/adapter.md` (or whatever the user's `gh` default is — let `gh` resolve it).
- If no argument and no obvious PRD in conversation context: ask the user for a PRD reference. Do not guess.

Validate the issue exists and is an issue (not a PR). If it's a PR, stop and tell the user.

### 2–4. Fetch, parse, compute eligibility

Follow `../_shared/prd-eligibility.md` — the source of truth for the `gh` fetch calls (the children are the PRD's **native sub-issues**, read back in one `gh api …/sub_issues` call), the `## External steps` / `## Blocked by` parsing rules (incl. the `needs-backfill` flag for pre-template issues), eligibility (`open` ∧ all blockers closed), and cycle detection (report the cycle and stop).

Everything that call returns is a child by construction. There are no filters, so nothing is dropped and there is nothing to report as dropped — the sub-issue list *is* the child set.

### 5. Recommend an issue

Apply rules in order:

1. **No eligible issues** → report "all open children are blocked" and show the blocking chain. Stop.
2. **One eligible issue** → recommend it.
3. **Multiple eligible** → apply the picking order from `../_shared/prd-eligibility.md` (fewest unmet external steps, then lowest number). Never batch.

### 6. Judge model / effort / plan mode

Read `../_shared/model-effort-heuristics.md` and apply it to the recommended issue. Produce three outputs: plan-mode y/n, model tier, effort. This is a downgrade detector against the operator's Opus-high default — flag loudly when it's safe to go lighter, otherwise confirm staying on the default. Speak in tiers; if exact model ids are needed, defer to `claude-api`. Hedge borderline calls.

### 7. Print the recommendation

Filter: `../_shared/final-prints.md`. Nearly everything here **is** the reasoning — the pick, why it won, the size call, the model call — and none of it exists on the board, so it stays. What the filter cuts is the PRD header line restating counts the human can see, and any recap of an issue body they are about to open.

Use this exact structure (omit empty sections):

```
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

Switch model/effort first if it differs from your current session.
/prd-workflow:work-on-issue #<n>
```

The three id-carrying lists each earn their ids: every one names something the human must **decide** on now — what to pick instead, what is waiting on what, what needs a body fixed. `Other eligible` and `Blocked` are the eligible and blocked sets, not the child set, and neither is a column on the board.

## Edge cases

- **PRD has no open children** → "All children closed. Consider a wrap-up comment on the PRD summarizing what shipped."
- **PRD has zero children at all** → **nothing is linked to this PRD.** Tell the user to link its children as native sub-issues, and say explicitly **not** to re-run `/to-issues`. Zero children no longer means "never sliced" — a PRD that was sliced but whose links were never written looks exactly the same from here — and re-running `/to-issues` on a PRD that already has children doubles every one of them. That is the expensive wrong move this branch exists to prevent.
- **`## External steps` missing on a child** → flag `needs-backfill` in the output; the user can backfill manually if it matters.
- **Argument is a PR URL, not an issue** → stop and ask for an issue.
- **Multiple PRDs at once** → not supported; one PRD per invocation.

## Project conventions to respect

- Be extremely concise per `CLAUDE.md`. Sacrifice grammar for concision in the output.
- Recommend plan mode before implementation — the user prefers it for non-trivial work.
- Model/effort is a recommendation only, decided at pickup (`../_shared/model-effort-heuristics.md` is normative on this).
- Never modify the PRD or any child issue from this skill.
