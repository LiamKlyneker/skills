---
name: work-on-issue
description: Start work on a single GitHub issue passed by number or URL. Fetches the issue, runs a readiness gate, and either auto-enters plan mode (when scope is clear and unblocked) or tells the user exactly what's missing. Use when the user says `work on` with an issue number, runs `/work-on-issue <url>`, or hands you an issue to start.
---

# Work On Issue

Take one issue (number or URL), decide whether we have enough to start, and act:

- **Ready** → load scoped context, then **auto-enter plan mode** (`EnterPlanMode`) to draft the implementation plan.
- **Not ready** → stop, list precisely what's blocking or missing, and ask. Do not enter plan mode.

This skill does the readiness gate + plan-mode handoff only. It does not implement, push, or close anything.

## Process

### 1. Resolve the issue

Argument may be a URL (`https://github.com/<owner>/<repo>/issues/N`), `#N`, or bare `N`. Strip query strings.

- URL → derive `<owner>/<repo>` from it.
- Otherwise use the issue-tracker repo from the **project adapter** at `<repo-root>/.claude/project/adapter.md` (or let `gh` resolve its default).
- No argument and no obvious issue in conversation context → ask for an issue reference. Do not guess.

### 2. Fetch it

```
gh issue view <n> --repo <repo> --json number,title,body,state,labels,comments
```

If it's a PR not an issue → stop, tell the user. If `state` is `closed` → flag it and ask whether to proceed.

### 3. Readiness gate

Mark the issue **NOT ready** if any of these hold:

- **No clear scope** — body is empty, a stub, or has no description of what to build / what "done" looks like.
- **Blocked** — has a `## Blocked by` section with any open `#NNN`. Check their state with `gh`.
- **Unmet external steps** — has a `## External steps` section with `- [ ]` items the user must do in-session first (e.g. a Supabase migration, an env var). Surface them; these block an autonomous start.
- **Open questions** — the issue text raises a decision you can't resolve from the issue + codebase.
- **Not implementable work** — the title starts with the adapter's `[PRD]` prefix (`## Repo` → *Title prefixes*). A PRD is the parent, not a slice to build, and `/work-on-prd` is what runs it. Handed one by number, say so and stop — do not plan-mode it. `[TASK]` and `[BUG]` are both normal work here.

`## Blocked by` / `## External steps` are optional — most standalone issues won't have them. Absence is fine, not a blocker. So is a missing prefix: nothing filters on titles, an unprefixed issue is ordinary work, and `[PRD]` is the only refusal.

### 4a. If NOT ready

Print concisely (sacrifice grammar per CLAUDE.md):

```
Issue: #<n> <title>  [<state>]

Not ready to start. Need:
  - <missing thing 1>
  - <missing thing 2>
```

Then ask the user how to proceed. Do not enter plan mode.

### 4b. If ready

1. Identify the directories/routes the issue touches. Read their `CONTEXT.md` (use the `scoped-context` skill if cross-feature imports are involved — it walks up to the route-group root).
2. Apply `../_shared/model-effort-heuristics.md` to the issue → plan-mode y/n, model tier, effort. Downgrade detector against the Opus-high default; tiers not versioned ids (defer to `claude-api` for ids); hedge borderline.
3. **Branch and PR, advisory only** — this skill still does not branch, push, or open anything. Read the adapter's optional **`Branch pattern:`** and **`PR template:`** rows, in the `### GitHub` sub-section of `## Repo`, the same two rows and the same substitution rule `work-on-prd`'s Setup steps 2–3 use, but for this one issue and with **no machine block**: no pointer, no child checklist, no resume search — there is no loop here to resume. `<n>` is this issue's number, `<slug>` its title slugged (strip a leading `[…]` bracket group first, then lowercase, collapse non-alphanumerics to hyphens, keep every word — the same pathological-title exception `work-on-prd` uses if the title runs long). **Either row absent → today's behaviour: say nothing about it.** The two rows are independent — resolve whichever is present, both, or neither.
4. One-line confirm what you understood the issue to be.
5. Print the block below — including the model/effort call and, when step 3 resolved anything, the branch/PR-template line — **before** `EnterPlanMode`. Entering plan mode commits the session model, so the operator needs the recommendation in hand first; if it differs from their current session they can switch before continuing.
6. `EnterPlanMode` and draft the implementation plan there.

```
Issue: #<n> <title>  [open]

Ready. Scope: <one line>. Touches: <dir(s)>.
Branch: <resolved-name>   PR template: <path-or-"snapshot">

Model/effort: <tier> · <effort>   (<downgrade from default | stay on default | borderline>)
  Why: <matched signals — no score>

Entering plan mode. Switch model/effort first if it differs from your current session.
```

Omit the `Branch:`/`PR template:` line entirely when both rows are absent — that is today's behaviour, unchanged. When only one row is present, print only that half of the line.

## Conventions

- Be extremely concise (CLAUDE.md).
- Plans must enumerate every `CONTEXT.md` they touch.
- Model/effort is a pickup-time recommendation only — never written into the issue (see `../_shared/model-effort-heuristics.md`).
- One issue per invocation.
