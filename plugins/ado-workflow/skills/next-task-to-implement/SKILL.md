---
name: next-task-to-implement
description: Recommend the next eligible `[TASK]` from a `[SPEC]`. Token-conscious; stops at recommendation. Use when starting a fresh implementation session.
---

# Next Task To Implement

Recommend the next work unit to implement from a `[SPEC]`. Reasons over its related `[TASK]`s,
respects `## Blocked by`, surfaces any `## External steps` the user must do in-session.

This skill **does not** implement, close tickets, modify state, or enter plan mode. It ends at
a recommendation. The user decides what to do next.

**Invocation name depends on the install route.** From a plugin (marketplace install or a
skills-dir link) every skill in this plugin is namespaced: `/ado-workflow:next-task-to-implement`,
`/ado-workflow:to-spec-tasks`, and so on. Only a bare symlink into a config's `skills/`
directory — the pre-plugin route — gives the unprefixed `/next-task-to-implement`. Unprefixed
names below are shorthand for whichever form your route provides.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` → `## Repo` → `### Azure DevOps`: the organisation,
the **work-item project**, the **work-item type**, and the **title prefixes**. Read it before
the first MCP call and hardcode none of it here.

**Abort** if the adapter is missing, or if its `Tracker:` line is anything other than
`azure-devops` (an absent line means `github`). Guessing an organisation or a project does not
error — it returns an empty result that reads like a spec with no tasks rather than like an
error.

`[SPEC]` and `[TASK]` below are **shorthand for the adapter's *Title prefixes* row**, written
out for readability. If that row names different prefixes, they win — here, and in every title
filter this skill applies.

## Readiness: the ADO MCP server

Requires the Azure DevOps MCP server (`mcp__ado__*` tools).

**Before starting:**

1. Check memory — the server may already be recorded as configured for this project.
2. If not in memory, probe: call `mcp__ado__core_list_projects` with `top: 1`.
   - Responds → proceed; save to memory: `ADO MCP active for this project`.
   - Fails → set it up. See [`ado-mcp-setup.md`](../references/ado-mcp-setup.md). **Read it
     before concluding the server is missing** — a probe failure has two causes, and the
     likelier one is a server running correctly under the wrong key, which this probe cannot
     distinguish from no server at all.

## Process

### 1. Resolve the `[SPEC]`

The argument is a `[SPEC]` work-item URL or id — **mandatory**. Strip query strings. If no
argument is passed, ask the user; do not guess.

Fetch it with `mcp__ado__wit_get_work_item`, passing `expand: "relations"` and **no** `fields`
filter — the two are mutually exclusive, and a `fields` filter silently suppresses the
relations the next step walks. Verify the work-item type matches the adapter's and the title
starts with `[SPEC]`. If not, abort with a clear message.

### 2. Find the `[TASK]`s and compute eligibility

Follow [`../_shared/ado-eligibility.md`](../_shared/ado-eligibility.md) for the mechanics — the
walk from the `[SPEC]` to its parent to its siblings, the `[TASK]` filter, the description
parse, and the `System.State` mapping — and
[`../_shared/eligibility-policy.md`](../_shared/eligibility-policy.md) for the rules the
mechanics feed: eligible = open ∧ every blocker done, cycle detection, and the picking order
when several are eligible. Read both; neither half decides a pick alone.

### 3. Recommend

Apply in order:

1. **Zero `[TASK]`s match** the spec (per the mechanics doc's filter) → the `[SPEC]` has not
   been broken down yet. Report that and point at `to-spec-tasks`. Stop. The `[SPEC]` is never
   itself a work unit and is never recommended.
2. **Zero eligible** (`[TASK]`s exist but none are eligible) → report `All open [TASK]s are
   blocked.` with the blocking chain. Stop.
3. **A cycle** in the Blocked-by graph → report the cycle. Stop. Do not recommend anything.
4. **One eligible `[TASK]`** → recommend it.
5. **N eligible `[TASK]`s** → apply the picking order from `../_shared/eligibility-policy.md`
   (fewest unmet `## External steps`, tie-break lowest id). Never batch — `[TASK]`s are already
   PR-sized.

### 4. Print

Use this exact structure. Omit empty sections.

```
SPEC: #<id> <title>     [<open> open / <closed> closed [TASK]s]

Recommended next: #<id> <title>

Why: <one-line reason>

External steps you'll need to do in-session:
  - [ ] <bullet>
  - ...

(Or "None — fully implementable from the editor.")

Other eligible right now:
  #<id> <title>  — <one-line reason it wasn't picked, e.g. "more external steps">

Blocked, waiting for upstream:
  #<id> <title>  blocked by #<id>[, #<id>...]

Needs backfill (## External steps section missing):
  #<id> <title>

Token-conscious note:
  <1–3 lines on size/risk, e.g. "spans src/lib/SWR/ + src/ui/Table.tsx — ~150 LOC across 4 files">

Suggested next step:
  Enter plan mode and implement #<id>. After the PR merges, close the [TASK]
  in Azure DevOps and re-run /next-task-to-implement.

Branch/commit/PR tip:
  Include "AB#<id>" in your commit/PR message so Azure DevOps auto-links the work item.
```

### 5. Stop here

Do not enter plan mode. Do not begin implementation. Do not edit code. Do not close or modify
any work item. The user reads the recommendation and decides.

## Edge cases

- **`[SPEC]` has zero `[TASK]`s** → "not broken down yet"; point at `to-spec-tasks`. Never
  recommend the `[SPEC]` itself.
- **All `[TASK]`s closed** → `All [TASK]s closed. Consider closing the SPEC and the parent work
  item if not already.`
- **Cycle in the Blocked-by graph** → report the cycle, stop.
- **Blocker references an id that does not exist** → treat as still blocking, flag in output
  (per `../_shared/ado-eligibility.md`).
- **Argument is not a `[SPEC]` work item** → abort with `Argument must be a [SPEC] work-item
  URL/ID.`

## Project conventions to respect

- Keep the output terse — sacrifice grammar for concision.
- Never modify the `[SPEC]`, any `[TASK]`, or the parent work item from this skill.
- The user prefers plan mode for non-trivial work but enters it themselves.
