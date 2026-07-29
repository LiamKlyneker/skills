# ADO Work-Item Authoring Invariants

Normative home for the Azure DevOps API landmines hit when creating or updating work items. These are empirical quirks of the MCP tools and the ADO REST API, true of every Azure DevOps organisation — not style preferences, and do not soften them into intent statements.

Cited by: `ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`, `ado-workflow:work-on-spec`.

## 0. The tools are action-based, and reads are split from writes

There is no tool per verb. Every work-item operation goes through one of three tools plus an
`action` argument, and **reads live in a different tool from writes**:

| Operation | Tool | `action` |
|---|---|---|
| Read one / several | `mcp__ado__wit_work_item` | `get`, `get_batch` |
| Create | `mcp__ado__wit_work_item_write` | `create` (also `add_child`) |
| Update | `mcp__ado__wit_work_item_write` | `update`, `update_batch` |
| Link / unlink | `mcp__ado__wit_work_item_link_write` | `link`, `unlink`, `link_to_pull_request`, `add_artifact_link` |
| Comment | `mcp__ado__wit_work_item_comment_write` | `add`, `update` |

`wit_work_item` is **read-only** — `get`, `get_batch`, `list_comments`, `my`, `list_revisions`,
`list_for_iteration`, `get_type`. Every mutation is in `wit_work_item_write`. Reaching for a
mutation on the read tool fails; so does the reverse.

**The field shape differs between `create` and `update`, and they are not interchangeable:**

```
create   fields:  [{ name: "System.Title", value: "…" }]
update   updates: [{ op: "add", path: "/fields/System.Title", value: "…" }]
```

`create` takes a name/value array; `update` takes JSON-Patch. Carrying one shape into the other
call is invalid — this is the most common way a working create is turned into a failing update.

`add_child` exists as a create action and may collapse §3's create-then-link into one call.
**It is untested here**; §3's two-step is the documented path until someone verifies otherwise.

## 1. Pre-escape angle brackets in any description body

Anywhere the body mentions a JSX/TSX token, HTML element, or generic type (`<AccordionContent>`, `<h3>`, `Foo<T>`), write `&lt;` and `&gt;`. Backtick-wrap for monospace too: `` `&lt;AccordionContent&gt;` ``.

`wit_work_item_write` (`action: "create"`) accepts a per-field `format: "Markdown" | "Html"` flag, but `wit_work_item_write` (`action: "update"`)'s `updates[]` items have **no `format` option** and fall back to HTML — so any later edit silently strips every unescaped angle-bracketed token. Escaping at synthesis time means the body survives both calls regardless of the format flag.

## 2. Never reference a PR with a bare `#NNNN`

ADO autolinks `#NNNN` in a body to the **work item** with that ID, sending readers somewhere unrelated. For any PR reference, use a full markdown link, with `<org>`, `<project>` and `<repo>` sourced from the project adapter:

```
[<repo> PR NNNN](https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/NNNN)
```

Same for cross-repo bug IDs or anything else that could collide with the shortcut. Bare `#NNNN` is only safe when it genuinely points at a work item in the current org (e.g. a `## Scope` line referencing the parent User Story).

## 3. The hierarchy parent is a relation, not a field

Setting `System.Parent` in the `wit_work_item_write` (`action: "create"`) `fields` array is a **silent no-op** — the value is dropped and the work item comes back unparented. Link it after creation:

```
wit_work_item_link_write  { action: "link", updates: [{ id: <child-id>, linkToId: <parent-id>, type: "parent" }] }
```

`updates` is an array, so multiple parent links batch into one call.

## 4. `fields` and `expand` are mutually exclusive on reads

`wit_work_item` (`action: "get"`) rejects them together, and passing a `fields` filter suppresses `relations`. When you need relations, pass `expand: "relations"` and **no** `fields`.

## 5. Verify hierarchy before reporting

After creating and linking, re-fetch the parent with `expand: "relations"` and confirm each new child appears as `Hierarchy-Forward`. A missing link means the create-time `System.Parent` no-op (§3) — fix with the `type: "parent"` call.

## 6. Assign to the current user

```
wit_work_item_write  { action: "update", id: <id>, updates: [{ op: "add", path: "/fields/System.AssignedTo", value: "<email>" }] }
```

Pass the raw email string — ADO resolves it to the full identity. Take the email from the session's `# userEmail` context; fall back to `CLAUDE.local.md`; if neither is available, skip assignment and warn in the final report.

## 7. Call envelopes are arrays, not flat objects

`wit_work_item_write` (`action: "update"`) and `wit_work_item_link_write` (`action: "link"`) both take a top-level `updates: [...]` array (plus optional `project`). Passing the fields flat at the top level is invalid.
