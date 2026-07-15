# Pattern Precedent

How to decide a component's implementation path and API shape. A fixed ladder, so two runs never pick different philosophies for sibling components:

1. **Repo idiom wins.** If the ui-profile/repo already has a pattern for this class of component, follow it.
2. **shadcn registry.** If a registry offers the component, install it and restyle with the repo's tokens. Never hand-roll a standard primitive (button, dialog, select, tabs…).
3. **Headless + APG.** Behavior-heavy components with no registry match: build on the repo's headless lib (Base UI / Radix per profile) with the WAI-ARIA APG pattern as the behavior spec — roles, keyboard, focus management.
4. **Config-heavy widgets** (DataGrid, DatePicker, complex pickers): consult MUI / Polaris / Ant as **API precedent only** — prop naming, variant taxonomy — never as implementation to copy.

## Research recipe (scoped — not an open-ended crawl)

- The APG entry for the component class, if one exists.
- 2–3 established reference libraries for that class (shadcn / Base UI / Radix docs; MUI or Polaris for the config-heavy rung).
- Timebox it; distill, don't dump.

## Output: the precedent note (≤10 lines, goes in the final report)

- **Behavior spec** — APG pattern used, or "none applies".
- **Path** — ladder rung chosen and why.
- **API precedent** — which library's API informed prop/variant naming.
- **Deviations** — where the Figma design or repo idiom forced a departure from the standard.

## Collisions → checkpoint

The design contradicting the standard (a dialog with no dismiss affordance; tabs styled as a select; focus order fighting the visual order) is a ⚠️ checkpoint question — never silently followed *or* silently "fixed".
