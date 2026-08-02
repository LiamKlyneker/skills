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

`add_child` is a create action, and it is **tested**: one `add_child` call sets `System.Parent`
**and** writes the hierarchy relation, collapsing §3's create-then-link into a single call. No
follow-up link write is needed for an item created that way. §3's two-step remains the path for
parenting an item that already exists, and §5's verification still applies to both.

## 1. Pre-escape angle brackets in any description body

Anywhere the body mentions a JSX/TSX token, HTML element, or generic type (`<AccordionContent>`, `<h3>`, `Foo<T>`), write `&lt;` and `&gt;`. Backtick-wrap for monospace too: `` `&lt;AccordionContent&gt;` ``.

`wit_work_item_write` (`action: "create"`) accepts a per-field `format: "Markdown" | "Html"` flag, and so does **`action: "update_batch"`**, per item. **Plain `action: "update"` is the one that does not**: its `updates[]` items have **no `format` option** and fall back to HTML — so any later edit made through `update` silently strips every unescaped angle-bracketed token, and rewrites a Markdown body as HTML on its way past.

The limitation is `update`'s alone. Do not state it as a property of every write: an append made through `update` when `update_batch` was available is what pushes a body out of Markdown and into HTML for no reason. Where a later edit must stay Markdown, use `update_batch` and pass `format` explicitly. Escaping at synthesis time is still what makes the body survive *whichever* of the three calls it goes through, regardless of the format flag.

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

**`action: "add_child"` is the exception, and it is not a second no-op.** Creating through
`add_child` sets `System.Parent` *and* writes the hierarchy relation in that one call — parenting
is done when it returns (§0). The two-step above is what a *`create`* needs, and what any
already-existing item needs; it is not a general rule that parenting always takes a separate link
write. Reading it as one means a redundant link write against an item that is already parented,
and a two-call create where one would have done.

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

## 8. A read will not tell you a field's format, and the UI is not showing you its stored text

Two different reasons a read hands back a confident wrong answer about a body.

**A field-filtered `get` never returns `multilineFieldsFormat`.** Pass a `fields` filter and that
map comes back absent — including for a field verified on the same item to be Markdown. There is
**no cheap way to read a field's format back**, so an absent map means *the format was not
reported*, never *this field is HTML*. Treating it as HTML is how a Markdown body gets rewritten
into an HTML one by the very code trying to preserve it, at which point §1's escaping is the only
thing standing between the body and its angle-bracketed tokens. Carry the format forward from the
write that set it (§1) instead of probing for it. (§4 is the other half of this: a `fields` filter
also suppresses `relations`.)

**The Azure DevOps UI renders a comment from its sanitised text, not from `renderedText`.** So
markup the read path drops does not appear on screen escaped — it simply **is not there**, and the
sentence around it reads as if it were written that way. Vanishing text, not visible junk, is the
symptom of read-path data loss here, which makes it easy to miss and impossible to diagnose from
the UI alone. §1's escaping rule is therefore load-bearing for **comments** as much as for
descriptions; do not treat it as a description-only precaution.

## 9. A Task has no `AcceptanceCriteria` field

The **Task** work item type carries `System.Description` and no acceptance-criteria field —
`Microsoft.VSTS.Common.AcceptanceCriteria` belongs to the requirement-level types (User Story,
Product Backlog Item), not to Task. So where the adapter's work-item type is `Task`, a `[TASK]`'s
acceptance criteria live **in its description**, as a section of the body, and nothing should
reach for the field.

The failure mode is quiet in both directions: criteria aimed at a field the type does not have do
not land on the item, and a read of that field returns nothing, so the work item shows up with no
acceptance criteria at all — which looks exactly like a task that was authored without any.
