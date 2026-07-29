# ADO Work-Item Authoring Invariants

Normative home for the Azure DevOps API landmines hit when creating or updating work items. These are empirical quirks of the MCP tools and the ADO REST API, true of every Azure DevOps organisation — not style preferences, and do not soften them into intent statements.

Cited by: `ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`.

## 1. Pre-escape angle brackets in any description body

Anywhere the body mentions a JSX/TSX token, HTML element, or generic type (`<AccordionContent>`, `<h3>`, `Foo<T>`), write `&lt;` and `&gt;`. Backtick-wrap for monospace too: `` `&lt;AccordionContent&gt;` ``.

`wit_create_work_item` accepts a per-field `format: "Markdown" | "Html"` flag, but `wit_update_work_item`'s `updates[]` items have **no `format` option** and fall back to HTML — so any later edit silently strips every unescaped angle-bracketed token. Escaping at synthesis time means the body survives both calls regardless of the format flag.

## 2. Never reference a PR with a bare `#NNNN`

ADO autolinks `#NNNN` in a body to the **work item** with that ID, sending readers somewhere unrelated. For any PR reference, use a full markdown link, with `<org>`, `<project>` and `<repo>` sourced from the project adapter:

```
[<repo> PR NNNN](https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/NNNN)
```

Same for cross-repo bug IDs or anything else that could collide with the shortcut. Bare `#NNNN` is only safe when it genuinely points at a work item in the current org (e.g. a `## Scope` line referencing the parent User Story).

## 3. The hierarchy parent is a relation, not a field

Setting `System.Parent` in the `wit_create_work_item` `fields` array is a **silent no-op** — the value is dropped and the work item comes back unparented. Link it after creation:

```
wit_work_items_link  { updates: [{ id: <child-id>, linkToId: <parent-id>, type: "parent" }] }
```

`updates` is an array, so multiple parent links batch into one call.

## 4. `fields` and `expand` are mutually exclusive on reads

`wit_get_work_item` rejects them together, and passing a `fields` filter suppresses `relations`. When you need relations, pass `expand: "relations"` and **no** `fields`.

## 5. Verify hierarchy before reporting

After creating and linking, re-fetch the parent with `expand: "relations"` and confirm each new child appears as `Hierarchy-Forward`. A missing link means the create-time `System.Parent` no-op (§3) — fix with the `type: "parent"` call.

## 6. Assign to the current user

```
wit_update_work_item  { id: <id>, updates: [{ op: "add", path: "/fields/System.AssignedTo", value: "<email>" }] }
```

Pass the raw email string — ADO resolves it to the full identity. Take the email from the session's `# userEmail` context; fall back to `CLAUDE.local.md`; if neither is available, skip assignment and warn in the final report.

## 7. Call envelopes are arrays, not flat objects

`wit_update_work_item` and `wit_work_items_link` both take a top-level `updates: [...]` array (plus optional `project`). Passing the fields flat at the top level is invalid.
