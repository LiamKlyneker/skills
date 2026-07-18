---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

The issue tracker and triage label vocabulary should have been provided in context — ask the user to share them if not.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

<vertical-slice-rules>
- Each slice is a vertical cut through every relevant layer (schema, API, UI, tests). Slices are NOT horizontal layers.
- Default to BUNDLE multiple tracer bullets into one issue when they fit **one fresh worker session**: a single context window, a single commit, a single verify pass. (The PR unit is the PRD branch — `/work-on-prd` maintains one PR per PRD — so "would it land as one PR" is NOT a sizing seam.) Only split when one of these seams applies:
  1. HITL gate in the middle (one bullet needs the user to do something outside the editor before the next bullet can start)
  2. Expand/contract migration flagged in the PRD's `## Migration risk` section (split into expand → cutover, plus contract if the PRD mentions removing legacy)
  3. Different code areas with zero touch overlap (e.g. backend schema + unrelated frontend copy change in the same PRD)
  4. Bundled AC count would exceed ~5 — the concrete proxy for "too big for one worker" (split on the most natural seam)
  5. Prefactoring: a refactor that would make the feature bullets trivial becomes its own leading slice ("make the change easy, then make the easy change"), listed as `Blocked by` for the slices it unblocks.
- Splitting with a `Blocked by` edge is cheap in orchestrated mode (an in-PRD blocker is satisfied as soon as its commit lands on the PRD branch), so when in doubt between one big issue and two chained ones, chain.
- A completed issue = one commit on the PRD branch that passes verify on its own. It does NOT need to be independently demoable — but it MUST be independently verifiable: the orchestrator judges each worker report in isolation, and a failed issue discards the whole bundle's uncommitted work.
- Bundle schema + RPC + consumer together by default so prod is never half-wired. Only split when the PRD's `## Migration risk` section explicitly flags expand/contract.
- **UI primitive exception (the one exception to bundling):** treat UI primitives as if they ship from a UI library. Each ⚠️/❌ row in the PRD's `## UI Primitives` section becomes its **own issue**, published first, and listed as `Blocked by` for every feature issue that consumes it. This is a deliberate horizontal slice — a primitive's API deserves isolated review so it doesn't get improvised inside a feature PR (the root cause of design drift). Trivial one-off styling tweaks stay bundled; this exception is scoped to *shared primitives that must be built or have their API changed/extracted*. Everything non-UI keeps the bundling rules above.
</vertical-slice-rules>

Read the PRD's `## UI Primitives` section if present. Emit one issue per ⚠️/❌ row (see the UI primitive exception in `<vertical-slice-rules>`), published ahead of and listed as `Blocked by` for the feature issues that consume them.

Read the PRD's `## Migration risk` section if present. For each entry there:
- If the PRD's `## Implementation Decisions` mentions removing/dropping the legacy column/RPC afterward, generate a 3-part split (expand → cutover → contract).
- Otherwise generate a 2-part split (expand → cutover).

Read the PRD's `## Data & Access` section if present. For each ⚠️ row (a CRUD op with a missing/wrong access policy, or a mis-scoped client):
- The access-policy migration must land **in the same slice as — or as a `Blocked by` of — the slice that first introduces that operation**, never a slice later. A user-scoped write with no policy is silently denied, so the write and its policy cannot ship apart.
- This matters most for a **new operation on an already-used table** (e.g. the first UPDATE/DELETE on a read/insert-only table): there's no `create table` migration to hang the policy off, so it's easy to slice the write into a feature issue and lose the policy entirely. Call it out explicitly in that issue's acceptance criteria (see the template note below).
- ✅ rows need nothing — they're already covered.

While drafting each slice, also gather its `## Worker context` and `## QA notes` (see the template): explore the codebase for the real file paths, scoped `CONTEXT.md`s, and prior-art examples the slice needs; take verify commands from `_shared/project-adapter.md` (never hardcode them); mark **User-visible: y/n** (y = app boot + screenshot verification applies). These two sections are what let an isolated orchestrated worker (`/work-on-prd`) implement the slice without plan mode — vague pointers here mean a blind worker there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **External steps**: any in-session manual actions required (or "None")
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)
- **Bundled bullets**: when a slice bundles multiple tracer bullets, list them so the user can sanity-check the grouping

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the bundles grouped sensibly, and any expand/contract splits aligned with the PRD's `## Migration risk` section?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. Apply the `ready-to-start` triage label so each issue is immediately pickable.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## External steps

A checklist of in-session manual actions Claude cannot perform — anything you'll need to do yourself during the implementation session (dashboard config, RPC/policy tweaks, env var changes, copy approval, manual prod verification, feature-flag toggles, webhook setup, etc.).

- [ ] Step 1
- [ ] Step 2

Or "None — fully implementable from the editor" if the issue requires no manual actions.

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

## Design reference

For UI issues only. Carry the design node(s) from the PRD's `## Design reference` so a cold implementation session has the target with no prior context. Omit for non-UI issues.

| Area | Design node | Node name |
|------|-------------|-----------|
| <area> | <url#node-id> | "<node name>" |

## Worker context

Everything a cold, isolated worker session needs to implement this slice without plan mode. The PRD stays path-free (paths rot over months); this section gets real paths because issues are consumed within days.

- **Files**: real paths the slice touches (create/edit), plus the scoped `CONTEXT.md`(s) to read first.
- **Prior art**: concrete in-repo examples to copy the pattern from (path + one line on what to imitate).
- **Verify**: exact commands, taken from `_shared/project-adapter.md` (L2 test command; L3 app/boot command if applicable).
- **User-visible**: y/n — y means the verify ladder's L3 (app boot + screenshot) applies.

## QA notes

2–3 lines for the human QA pass (these seed the PRD's QA doc): what to do in the running app, what they should see, edge cases worth poking.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] (UI issues) Implementation matches the design node 1:1
- [ ] (UI issues) The node URL + name recorded in the page's `CONTEXT.md` `## Design reference` table
- [ ] (Issues introducing a new write on an existing table — from the PRD's `## Data & Access`) An access policy `for <operation>` exists for the acting user, and the write path checks `response.error` (does not return `void`)

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.

</issue-template>

Once all child issues are published, transition the parent PRD's triage label from `needs-triage` to `ready-to-start` (it has now been broken down and is ready to be picked up). Do NOT close the parent issue or modify anything else about it.
