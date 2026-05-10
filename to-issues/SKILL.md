---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

# To Issues

_Inspired by Matt Pocock's `to-issues` skill, adjusted for my own workflow._

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
- Default to BUNDLE multiple tracer bullets into one issue when they would naturally land in a single PR to main. Only split when one of these seams applies:
  1. HITL gate in the middle (one bullet needs the user to do something outside the editor before the next bullet can start)
  2. Expand/contract migration flagged in the PRD's `## Migration risk` section (split into expand → cutover, plus contract if the PRD mentions removing legacy)
  3. Different code areas with zero touch overlap (e.g. backend schema + unrelated frontend copy change in the same PRD)
  4. Bundled AC count would exceed ~5 (split on the most natural seam)
- A completed issue lands as one PR to main. It does NOT need to be independently demoable in prod — partial-feature PRs are fine as long as prod stays unbroken.
- Bundle schema + RPC + consumer together by default so prod is never half-wired. Only split when the PRD's `## Migration risk` section explicitly flags expand/contract.
</vertical-slice-rules>

Read the PRD's `## Migration risk` section if present. For each entry there:
- If the PRD's `## Implementation Decisions` mentions removing/dropping the legacy column/RPC afterward, generate a 3-part split (expand → cutover → contract).
- Otherwise generate a 2-part split (expand → cutover).

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

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. Apply the `needs-triage` triage label so each issue enters the normal triage flow.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## External steps

A checklist of in-session manual actions Claude cannot perform — anything you'll need to do yourself during the implementation session (Vercel dashboard config, Supabase RPC tweaks, env var changes, copy approval, manual prod verification, GrowthBook flag toggles, Stripe webhook setup, etc.).

- [ ] Step 1
- [ ] Step 2

Or "None — fully implementable from the editor" if the issue requires no manual actions.

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.

</issue-template>

Do NOT close or modify any parent issue.
