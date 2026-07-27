---
name: to-prd
description: Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context.
---

This skill takes the current conversation context and codebase understanding and produces a PRD. Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided in context — ask the user to share them if not.

## Mode: CREATE vs UPDATE

- **CREATE (default):** invoked with no issue reference → publish a brand-new PRD via the Process below and apply the `needs-triage` triage label.
- **UPDATE:** invoked with an existing issue reference (number/URL/path) as an argument → **enrich that PRD in place** instead of creating a new one. This lets a fidelity PRD accrue detail across multiple grills — a later grill on the same feature appends to the existing PRD rather than spawning a fresh one.

### UPDATE mode rules

1. Fetch the issue and read its **full current body** first.
2. Do a **section-aware, contract-preserving merge**: replace only the sections *this grill produced*; leave every other section **byte-intact**. Don't reflow, reorder, or re-tone untouched prose.
3. **Never clobber the headings `to-issues` parses.** These are a downstream contract — `to-issues` reads them verbatim:
   - `## Implementation Decisions`
   - `## UI Primitives`
   - `## Design reference`
   - `## Migration risk`
   - `## Data & Access`
   When you update one, replace its **body in place under the exact heading text** — never rename, remove, duplicate, or change the level of these headings. If a contract heading doesn't exist yet and this grill produced content for it, insert it in template order.
4. Sections are **append/replace by ownership**: tables like `## UI Primitives` and `## Design reference` accumulate **rows** (merge new rows in, don't drop existing ones unless this grill supersedes a specific row); narrative sections this grill owns are replaced wholesale. Anything outside this grill's scope is untouched.
5. **Do not re-apply triage labels** in UPDATE mode — leave the issue's labels exactly as they are. (Only CREATE applies `needs-triage`.)

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the PRD, and respect any ADRs in the area you're touching.

2. Sketch out the major modules you will need to build or modify to complete the implementation. Prefer deep modules — a simple, stable, testable interface with a lot behind it.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

3. Write the PRD using the template below, then publish it to the project issue tracker. **(CREATE mode)** apply the `needs-triage` triage label so it enters the normal triage flow. **(UPDATE mode)** instead merge into the referenced issue per the UPDATE rules above and leave its labels untouched.

<prd-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list of user stories, each in the format:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

Cover every actor and every interaction the feature touches; no padding.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

## UI Primitives

Only for PRDs that implement a visual design. The component manifest carried over from the **design spec** (the grill confirms these rows, it does not build them) — every UI primitive the design needs, so `to-issues` can emit one issue per primitive that must be built or changed. Schema (statuses, homes, column meanings) is normative in `../_shared/ui-manifests.md`.

| Primitive | Status | Home | API surface | Consumed by |
|-----------|--------|------|-------------|-------------|
| IconBadge | ❌ build | shared UI lib | color, icon, size | feature cards |

Omit this section (or write "None — no new/changed UI primitives") for non-visual PRDs.

## Design reference

The design node pointers, carried through from the **design spec** (or recorded during the grill if there is no spec), so a cold implementation or verify session can find the target. Omit for non-visual PRDs.

| Area | Design node | Node name |
|------|-------------|-----------|
| Edit dialog | <url#node-id> | "Edit / Options" |

## Migration risk

A list of tables, RPC functions, or columns where this PRD requires an expand/contract migration (i.e. cannot be deployed atomically). For each entry, specify:

- The table/RPC/column affected
- Whether the legacy shape will be removed afterward (drives 3-part vs 2-part split)

Or "None — all schema/RPC changes can land atomically in a single deploy" if no expand/contract is needed.

## Data & Access

The Data & Access Manifest agreed during the grill (`deep-grill`'s hard gate) — one row **per operation** the implementation actually exercises on each store, so `to-issues` can spin the access-control work into the right slices. This is orthogonal to `## Migration risk`: that section asks "can this deploy atomically?"; this one asks "is every operation permitted, correctly scoped, and its error surfaced?". The trap it exists to catch is a **new operation on an already-used store** (e.g. a first update or delete on something only ever read from and appended to) whose missing access policy silently blocks the write.

| Store | Operation | Client | Access policy exists? | Status |
|-------|-----------|--------|-----------------------|--------|
| document | update | user-scoped | ❌ none for update | ⚠️ needs a policy change |
| job | update | privileged | n/a — policies bypassed by design | ✅ covered |

Client ∈ user-scoped (policies apply) / privileged (policies bypassed — admin key, service credential, or trusted backend job). Status ∈ ✅ covered / ⚠️ gap (needs a policy change or code fix) / ❌ unchecked. For every write row, the grill must also have confirmed the transitions of any status field and that the write path surfaces a denied write rather than swallowing it. Omit this section (or write "None — no stored-data reads/writes") for PRDs whose code touches no stored data.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>
