---
name: verify-ui
description: Verify that shipped UI matches its design 1:1 by driving the real browser and comparing against the design node. Use when the user wants to check a UI change against its design, "verify the UI", "does this match the design", or after implementing a design-heavy feature. Requires a Claude-Chrome session (`claude --chrome`) and a design-tool MCP (e.g. Figma).
---

# Verify UI

Compare shipped UI against its design and report (or fix) the deltas. This is the closing gate of the design-to-code pipeline (`grill-me` → `to-prd` → `to-issues` → implementation → **verify-ui**).

## Prerequisites

- **Claude-Chrome** (`claude --chrome` + the Chrome extension). The browser uses the user's *real, logged-in* session, so auth-protected routes and interaction-only states (modals) are reachable without scripted login.
- **A design-tool MCP** connected (e.g. Figma: `get_metadata`, `get_screenshot`, `get_design_context`).
- A running dev server. Start it if it isn't already up.

If Claude-Chrome is not available, STOP and tell the user to relaunch with `claude --chrome` — do not attempt a substitute.

## Scope

**PR-tied by default.** Verify what changed on the current branch. The user may pass a **manual override** (a route + optionally a node) to verify a screen that isn't in the current diff.

## Workflow

### 1. Determine what to verify

- **Default (PR-tied):** `git diff main...HEAD --name-only`, keep UI files. Group by the page/feature they belong to.
- **Override:** use the route + node the user passed.

### 2. Resolve the design node(s)

For each changed area, find its target design node:
- Read the area's `CONTEXT.md` `## Design reference` table (walk up to the route-group root if the leaf has none) and take the node URL + recorded node name.
- If override mode supplied a node, use that.
- If no node can be found, ask the user for it — do not guess.

### 3. Staleness hard-stop (per node)

Before trusting any node, call the design tool's `get_metadata(nodeId)`:
- If it **404s**, or the **live node name ≠ the recorded name**, STOP. Tell the user the reference looks stale (recorded "X", node now resolves to "Y"/missing) and ask for a fresh URL. **Never compare against a drifted node.**
- On match, update the `Verified` date in `CONTEXT.md` when you finish.

### 4. Capture target + actual

- **Target:** `get_screenshot(nodeId)` for the design.
- **Actual:** drive Chrome to the route, perform whatever interaction reaches the state (open the modal, select the tab, hover, etc.), and screenshot the live UI at a comparable viewport.

### 5. Compare + report

Diff target vs actual and report a **deltas table** — be specific and visual:

| Element | Design | Shipped | Delta |
|---------|--------|---------|-------|
| Primary CTA | solid bright green | pale/disabled green | wrong variant |
| Icon badge | blue filled circle | bare icon | missing IconBadge |

Cover: spacing/layout, colors (vs brand tokens), typography, icon treatment, states (selected/hover/disabled), radii, shadows. If it matches, say so plainly ("matches 1:1, no deltas").

### 6. Fix (only if `--fix`)

If invoked with `--fix`, apply the deltas to the working tree, then re-capture and re-compare to confirm. Otherwise report only and let the user decide.

## Notes

- A primitive-level delta (e.g. "should be a shared `IconBadge`, is inline utility classes") is a signal the pipeline's manifest gate was skipped or a primitive drifted — flag it as such, not just as a one-off pixel fix.
- This skill is **drafted and needs a live `--chrome` shakedown** before its compare-loop quality is proven.
