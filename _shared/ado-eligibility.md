# `[SPEC]` Task Eligibility — Azure DevOps Mechanics

Shared by `next-task-to-implement` and `work-on-spec`. Given a `[SPEC]` work item, find its
`[TASK]` work units and produce the facts eligibility runs on: how to walk the relation graph
to them, which siblings really belong to this spec, how to parse a description, and how
`System.State` maps onto open/done.

**The rules themselves live in `../_shared/eligibility-policy.md`** — eligible = open ∧ every
blocker done, cycle detection, the orchestrated-mode exception, picking order, never batch.
Read both; this file alone does not decide a pick.

Single source of truth for the mechanics below — do not copy them into skills; reference this file.

Requires the Azure DevOps MCP server (`mcp__ado__*`). Organisation, project, work-item types
and the board's state names come from the project adapter, never from this file.

## Read expansion: `fields` and `expand` are mutually exclusive

Every read below passes `expand: "relations"` and **no** `fields` filter.
`wit_get_work_item` rejects the two together, and a `fields` filter silently suppresses
`relations` — the very graph this document walks, so the failure looks like a spec with no
tasks rather than like an error. Full landmine list: `../_shared/ado-workitem-authoring.md`.

## 1. Resolve the `[SPEC]`

The argument is a `[SPEC]` work-item URL or id — mandatory. Strip query strings; never guess
one. Fetch it with `wit_get_work_item` (`expand: "relations"`) and verify both the work-item
type and a title starting with `[SPEC]`. Anything else aborts with a clear message.

## 2. Walk to the siblings

1. From the `[SPEC]`'s **`Hierarchy-Reverse`** relation, take the parent work item's id.
2. Fetch that parent with `expand: "relations"` and read its **`Hierarchy-Forward`** (child)
   relations. Those children are the `[SPEC]`'s **siblings** — `[TASK]`s hang off the parent
   alongside the spec, never underneath it, so walking the spec's own children finds nothing.
3. Fetch each sibling in parallel.

## 3. Filter to this spec's `[TASK]`s (do this before parsing)

Keep a sibling only when **both** hold:

- Its title starts with `[TASK]`, AND
- Its description carries the spec reference (`Spec: #<spec-id>`) **or** a `Related` link
  points back at this `[SPEC]`.

The parent collects every kind of child — other specs, their tasks, `[QA]` items, ordinary
work someone filed by hand. Sitting under the same parent is not membership, and picking such
a sibling means working something this spec never scoped.

Report the siblings you dropped and why. A silently-dropped task looks identical to a spec
with fewer slices than it has.

**Zero matches**: the `[SPEC]` has not been broken down yet. Report that and stop — the fix is
to run `to-spec-tasks`. The `[SPEC]` is never itself a work unit.

## 4. Parse each `[TASK]` description

The headings and "None…" sentinels below are a string contract with the writer — normative
copy lives in `to-spec-tasks`'s `[TASK]` body template. Reword there first, never here alone.

- **External steps**: everything under `## External steps` until the next `## ` heading. Each `- [ ]` line is an unmet step; `- [x]` is met. The literal phrase "None — fully implementable from the editor" (or just "None") means no external steps. Section missing entirely → treat as "None" and flag `needs-backfill` (work item predates the template).
- **Blocked by**: everything under `## Blocked by` until the next `## ` heading. Collect every `#<id>` reference. "None" (or "None — can start immediately") means no blockers.

A bare `#<id>` in a description autolinks to the work item with that id, so a blocker
reference resolves directly. A blocker outside this spec's `[TASK]` set is fetched separately
for its state and respected all the same. An id that does not resolve counts as still
blocking; flag it in the output.

## 5. Map `System.State` onto open/done

`System.State` is a per-process string, not a boolean, and the names differ between ADO
processes. Treat every **terminal** state as done and everything else — including the in-flight
board states an orchestrated run drives — as open. The project adapter names this process's
states; where it names none, ADO's stock terminal states are `Closed`, `Done`, `Resolved` and
`Completed`.

**Orchestrated-mode exception, observed**: a `[TASK]` whose commit is already on the spec
branch still reads as a non-terminal (committed-awaiting-merge) state, because tasks close on
pull-request completion rather than on commit — that gap is what the exception in
`../_shared/eligibility-policy.md` covers. An orchestrated run observes the condition by
grepping the branch's commit messages for the work-item reference, not by reading state:
commits are truth, state is cache.
