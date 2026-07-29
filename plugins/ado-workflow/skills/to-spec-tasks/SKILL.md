---
name: to-spec-tasks
description: Slice a `[SPEC]` work item into the `[TASK]` work units that implement it, on Azure DevOps. Always produces at least one `[TASK]`. Use in a fresh session against a `[SPEC]` URL or id.
---

# To Spec Tasks

Take a `[SPEC]` work item and create the `[TASK]` work units that implement it.

A `[SPEC]` **always produces at least one `[TASK]`**. The spec is a document, never a work
unit — the same relationship a PRD has to its child issues on the GitHub side. So this skill
never decides *whether* to break a spec down; it decides only **where the cuts fall**, and a
spec with no seam in it yields exactly one `[TASK]` covering the whole thing, never zero.

**Invocation name depends on the install route.** From a plugin (marketplace install or a
skills-dir link) every skill in this plugin is namespaced: `/ado-workflow:to-spec-tasks`,
`/ado-workflow:next-task-to-implement`, and so on. Only a bare symlink into a config's
`skills/` directory — the pre-plugin route — gives the unprefixed `/to-spec-tasks`.
Unprefixed names below are shorthand for whichever form your route provides.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` → `## Repo` → `### Azure DevOps`: the organisation,
the **work-item project** the items live in, the **work-item type** to create them as, and the
**title prefixes**. Verify commands come from the same adapter's `## Commands` table. Read it
before the first MCP call and hardcode none of it here.

**Abort** if the adapter is missing, or if its `Tracker:` line is anything other than
`azure-devops` (an absent line means `github`). Guessing an organisation or a project does not
error — it writes work items somewhere nobody is looking, or returns an empty result that
reads like a story with no children.

`[SPEC]`, `[TASK]` and `[QA]` below are **shorthand for the adapter's *Title prefixes* row**,
written out for readability. If that row names different prefixes, they win — here, and in
every title filter this skill applies.

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

### 1. Resolve the SPEC

The argument is a `[SPEC]` work-item URL or id — **mandatory**. Strip query strings. If no
argument is passed, ask the user for one; never guess.

Fetch it with `mcp__ado__wit_work_item` (`action: "get"`), passing `expand: "relations"` and **no** `fields`
filter — the two are mutually exclusive, and a `fields` filter silently suppresses the
relations the next steps walk (see [`_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md)
§4). Verify the work-item type matches the adapter's and the title starts with `[SPEC]`. If
not, abort.

### 2. Check for existing `[TASK]`s

Take the parent work item from the `[SPEC]`'s `Hierarchy-Reverse` relation and fetch its
`Hierarchy-Forward` children — the spec's **siblings**. If any sibling title starts with
`[TASK]`, list them and ask:

```
[TASK]s already exist under this parent. Continue and add more? (yes / no)
```

On `no`, stop.

### 3. Ground in current code state

Read every file listed under the spec's `## Critical files & areas`. This grounds the seam
decision in what the code looks like **now**: a spec can be days or weeks old, and `to-spec`'s
UPDATE mode may have enriched it since. The spec's own prose is a record of decisions, not a
report on the current tree.

The spec carries no splitting advice to read — it stopped carrying any, because a spec always
produces at least one `[TASK]` and the cut is decided here against real code.

### 4. Decide where to cut

Apply [`_shared/spec-splitting-seams.md`](../_shared/spec-splitting-seams.md) — the normative
list of seams, including the ~5-acceptance-criteria size seam, and the cap of 4 work items with
a push-back to Product past that.

That document decides *where*, not *whether*. Resolve it to a concrete slice list:

- **A seam applies** → one `[TASK]` per slice, in dependency order, each carrying a `Blocked by`
  edge to the slices it needs.
- **No seam applies** → **exactly one `[TASK]`** covering the whole spec, `Blocked by: None`.
  This is a normal, common outcome — not a fallback and not a failure. There is no verdict to
  print, nothing to plan-mode into, and no path through this skill that creates zero `[TASK]`s.

### 5. Present the slice list

Print:

```
Proposed [TASK]s:
1. [TASK] <title>
   Scope: <2–3 lines>
   Blocked by: <#id from this list, or "None">
   Covers AC: <numbers from the SPEC>
2. ...

Approve? (approve / edit / abort)
```

- `approve` → proceed to step 6.
- `edit` → conversational mode; adjust titles / scope / blockers / coverage until the user
  re-approves. Merging every slice into one is a legitimate edit; deleting them all is not.
- `abort` → stop.

A one-slice list is presented the same way, as a single numbered entry. Do not editorialise
about it being unsplit.

### 6. Author and create the `[TASK]`s

Author each description per the template below, applying the authoring invariants in
[`_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) — angle-bracket
escaping (§1) matters here as much as on the spec, since `[TASK]` scopes routinely name
components and generic types.

Then, for each approved `[TASK]`, **in dependency order** (so blockers reference real ids):

- `mcp__ado__wit_work_item_write` (`action: "create"`):
  - `project`: the adapter's **work-item project** (same as the spec's)
  - `workItemType`: the adapter's **work-item type**
  - `title`: the `[TASK]` prefix followed by the slice title
  - `description`: the authored body
  - `System.IterationPath`: inherit from the parent work item
- **Parent link — a separate call, never `System.Parent` at creation** (§3). Link each `[TASK]`
  as a child of **the parent work item**, i.e. a **sibling of the `[SPEC]`, not a child of it**.
  All parent links batch into one `wit_work_item_link_write` (`action: "link"`) call.
- Add a `Related` link from each new `[TASK]` back to the `[SPEC]` (`type: "related"`).
- **Verify** each `[TASK]` appears as a `Hierarchy-Forward` child of the parent before
  reporting (§5).
- Assign each `[TASK]` to the current user (§6).

Hierarchy and the `Related` link are not decoration: `../_shared/ado-eligibility.md` walks
spec → parent → siblings to find a spec's tasks at all, and filters them by the `Spec: #<id>`
line or that `Related` link. A `[TASK]` parented to the spec, or created without either
back-reference, is invisible to every downstream skill.

#### The `[TASK]` body template

<!-- String contract: this template is the NORMATIVE copy of the `[TASK]` body contract. It is
the sole writer of the `Spec:` line and of the `## External steps`, `## What to build`,
`## Worker context`, `## QA notes`, `## Acceptance criteria` and `## Blocked by` headings, plus
the two "None…" sentinel phrases below. `../_shared/ado-eligibility.md` parses the `Spec:` line,
`## External steps` and `## Blocked by` verbatim; `next-task-to-implement` reads them through
it; `work-on-spec` consumes `## Worker context` and `## QA notes` when it briefs a `spec-worker`.
Reword a heading or a sentinel here and you must change it in all three. -->

<task-template>

Spec: #<spec-id>

## External steps

In-session manual actions Claude cannot perform (env config, copy approval, RPC tweaks, prod
verification, etc.):

- [ ] <step>

Or "None — fully implementable from the editor." <!-- parsed verbatim — do not reword -->

## What to build

A concise description of this vertical slice. End-to-end behavior, not layer-by-layer
implementation.

## Worker context

Deliberately slim, and **slice-local only** — facts that belong to this slice and cannot drift:

- **Verify**: the exact commands, taken from the adapter's `## Commands` table (L2 test command;
  L3 boot/screenshot command when user-visible).
- **User-visible**: y/n — y means the verify ladder's L3 applies.

## QA notes

2–3 lines for the human QA pass: what to do in the running app, what they should see, one edge
case worth poking.

## Acceptance criteria

- [ ] <criterion>
- [ ] <criterion>

## Blocked by

- #<task-id> <title>

Or "None — can start immediately." <!-- parsed verbatim — do not reword -->

</task-template>

**Why `## Worker context` stays this slim.** No file inventories, no architecture, no module
shapes, no prior-art tours — all of that stays on the `[SPEC]`, and a worker reads it there.
This is the deliberate difference from the GitHub sibling `to-issues`, which does put real
paths in the issue: a GitHub issue's parent PRD is frozen once its children are written, but
`to-spec`'s **UPDATE mode mutates a spec after its `[TASK]`s exist**. Anything a task restates
from the spec can therefore go stale silently, with nothing anywhere to detect the divergence.
A verify command, a user-visible flag and QA steps are the exceptions: they describe this slice,
not the architecture, so the spec changing underneath them cannot falsify them.

### 7. Report

List each created `[TASK]` with id + URL in dependency order, then:

```
Run /next-task-to-implement <spec-url> to pick the first one.
```

## Stops here

Do not modify the `[SPEC]` or the parent work item. The only state change this skill makes is
creating `[TASK]` work items — which it always does, at least one.

**This skill never enters plan mode**, on any path. There is no verdict, no monolithic
outcome, and no branch that hands the session a spec to plan directly; planning happens per
`[TASK]`, in the session that implements it.
