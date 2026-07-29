---
name: to-spec
description: Lock the current grill session into a `[SPEC]` work item on Azure DevOps, as a child of the work item that was grilled. Use after a grill to publish the engineering decisions that were locked.
---

# To Spec

Take the current grill session and codebase understanding and publish them as a `[SPEC]` work
item on Azure DevOps, as a child of the work item being grilled. Do NOT interview the user —
synthesize what you already know.

If no grill discussion is detected in conversation context, abort with: `No grill discussion
detected. Run a grill first (/grill-me <work-item-url>).`

The `[SPEC]` is **engineering-only**. Product owns the parent work item; never restate product
scope here.

**Invocation name depends on the install route.** From a plugin (marketplace install or a
skills-dir link) every skill in this plugin is namespaced: `/ado-workflow:to-spec`,
`/ado-workflow:to-spec-tasks`, and so on. Only a bare symlink into a config's `skills/`
directory — the pre-plugin route — gives the unprefixed `/to-spec`. Unprefixed names below are
shorthand for whichever form your route provides. The grill skills are not part of this plugin
and invoke bare on either route.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` → `## Repo` → `### Azure DevOps`: the organisation,
the **work-item project** the items live in, the **work-item type** to create them as, and the
**title prefixes**. Read it before the first MCP call and hardcode none of it here.

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

## Modes

- **CREATE** (default) — no `[SPEC]` exists under the lead work item → author a new one.
- **UPDATE** — a `[SPEC]` already exists → **enrich it in place**. This lets a spec accrue
  detail across multiple grills instead of spawning a rival spec under the same parent.

### UPDATE mode rules

1. Fetch the existing `[SPEC]` and read its **full current body** first.
2. Do a **section-aware merge**: replace only the sections *this grill produced*; leave every
   other section byte-intact. Don't reflow, reorder, or re-tone untouched prose.
3. Replace a section's body **in place under its exact existing heading** — never rename,
   remove, duplicate, or re-level a heading. If a template section doesn't exist yet and this
   grill produced content for it, insert it in template order.
4. `## Critical files & areas` and `## Open Questions` **accumulate** — merge new entries in,
   and only drop an existing one when this grill explicitly supersedes it. Narrative sections
   this grill owns are replaced wholesale.
5. Update the trailing generation line to note the additional pass; leave assignment, state,
   iteration, and links untouched.
6. Escaping still applies — see [`_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md)
   §1. A `wit_update_work_item` body has no `format` flag, so an unescaped token that survived
   CREATE gets stripped now.

UPDATE mode stays useful after `to-spec-tasks` has run: a spec that keeps absorbing detail is
what keeps the `[TASK]` bodies slim, because they point at the spec instead of restating it.

## Process

### 1. Identify the lead work item

From the grill context, identify the work item (or items) discussed. The **first** one
introduced in the grill is the **lead**; any others are **followers**.

The lead is a requirement-level item — whatever this board's process calls that. Do **not**
assert a type name; process templates disagree about it. Verify instead that the lead's title
carries **none** of the adapter's title prefixes: a `[SPEC]`, `[TASK]` or `[QA]` is never a
lead.

### 2. Resolve mode

Run in parallel with the MCP probe above:

- **Fetch lead:** `mcp__ado__wit_get_work_item` with `expand: relations` and **no** `fields`
  filter — the two are mutually exclusive, and a `fields` filter silently suppresses the
  relations this step reads (see `_shared/ado-workitem-authoring.md` §4).
- **Mode:** look at the lead's `Hierarchy-Forward` (Child) relations and fetch each child's
  title. Any title starting with `[SPEC]` → **UPDATE** that one. None → **CREATE**.

### 3. Explore the codebase (light touch)

If the grill already walked the relevant code, skip this. Otherwise, briefly explore the files
and modules touched by the decisions to confirm names and locations. Look for deep modules:
encapsulated functionality behind a simple, testable interface that rarely changes.

### 4. Synthesize the SPEC body

Use the template below. **Omit any section that has no content** (e.g., no migration risk →
drop the section entirely, don't write "None"). Exception: `## Scope` is always present.

Apply the authoring invariants in [`_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md)
to the body **before sending** — angle-bracket escaping (§1) and PR-reference linking (§2) both
have to be right at synthesis time to survive later edits.

<spec-template>

## Scope

Implements decisions for:
- #<id> — <title>
- (when grouped) #<id> — <title>

## Implementation Decisions

The technical decisions locked during the grill:
- Modules built/modified and their interface shapes
- Architectural choices
- Schema or API contract decisions
- Library / pattern choices
- Technical clarifications agreed in the grill

## Modules

Major modules touched, with rationale for any deep-module extraction.

## Critical files & areas

Concrete pointers the next session must read or be aware of before starting. File paths and
short rationale — enough context so the next session doesn't waste tokens rediscovering.

- `path/to/file.ts` — why it matters
- `path/to/dir/` — pattern to follow

## Migration risk

For each table / RPC / column requiring expand/contract:
- The artifact affected
- Whether legacy is removed afterward (drives 3-part vs 2-part split)

## Testing Decisions

What makes a good test for this work, which modules get tests, references to prior art in the
codebase.

## Out of Scope

Engineering-side deferrals only. Do NOT restate product scope — that lives on the parent work
item.

## Open Questions

Things the grill flagged but didn't resolve. Non-blocking — for follow-up in `to-spec-tasks` or
implementation.

---
Generated by to-spec on <YYYY-MM-DD>.

</spec-template>

The spec carries **no splitting advice**. A `[SPEC]` always produces at least one `[TASK]`, so
there is nothing left to advise on; `to-spec-tasks` decides where the cuts fall, against
current code state rather than against a guess made at synthesis time.

### 5. Publish

**UPDATE mode:** apply the merged body with `mcp__ado__wit_update_work_item` (`op: replace`,
`path: /fields/System.Description`), then skip to step 7 — parent, assignment, and follower
links already exist.

**CREATE mode:** call `mcp__ado__wit_create_work_item`:

- `project`: the adapter's **work-item project**
- `workItemType`: the adapter's **work-item type**
- `title`: the `[SPEC]` prefix followed by the lead's title
- `description`: the synthesized markdown body
- `System.IterationPath`: inherit from the lead work item

Then, per [`_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md):

- Link the new `[SPEC]` as a **child of the lead** (§3) — a separate `wit_work_items_link`
  call, never `System.Parent` at creation.
- Verify the child link landed before reporting (§5).
- Assign to the current user (§6).

### 6. Link followers (group case only)

For each follower, add a `Related` link to the `[SPEC]` via `mcp__ado__wit_work_items_link`.
This makes the spec discoverable from any work item in the group via the "Related Work"
sidebar. Skip in UPDATE mode unless the grill introduced a new follower.

### 7. Report

Print:

```
[SPEC] #<id> created: <url>          — or "updated: <url>" in UPDATE mode
Scope: <one-line summary>
(Sections merged: <names>)           — UPDATE mode only
(Followers linked: #<id>, #<id>)     — if applicable
```

## Stops here

Do not modify the lead work item's description. Do not change any state. Do not break the spec
into `[TASK]`s — that is `to-spec-tasks`. Do not enter plan mode.
