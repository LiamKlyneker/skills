# UI Manifest Gates — TEMPLATE (project-flavored instance)

**Optional.** Copy to `<repo-root>/.claude/project/ui-manifests.md` and register it in the adapter's `## Project gates` only if this project's primitive homes, token files or traps need naming. A project whose vocabulary the canonical schema already covers needs no instance at all.

The **row schema is canonical** in `_shared/ui-manifests.md` — statuses, columns, the earn-the-abstraction principle, the hard-gate rule. Do not restate it here and do not contradict it. This file names *what the rows are filled with in this repo*: the concrete homes, the real token files, the traps, and the test vehicle.

The examples below are web/Tailwind-flavored because that is the stack this template was lifted from. Replace them wholesale — an iOS instance, for example, reads SF Symbols / a `DesignSystem` package / colocated feature views instead.

## Primitive homes (this repo's four rungs)

Fill in what each rung of the canonical ladder is actually called here:

- **stock** — `components/ui` (shadcn-style): a standard primitive the registry offers. **Install it, never hand-roll it.**
- **shared UI lib** — `<the package or directory>`: cross-feature reusable. Only promote here once a real second consumer exists.
- **colocated** — `_components/` next to its single consumer. The default home for new bespoke UI.
- **new dependency** — last resort. `<any rule this project has about adding one>`.

**Dependency direction:** `<e.g. features depend on the shared lib only — no feature→feature imports>`.

## Token sources

- Definitions live in `<tailwind.config.js / tokens.css / the token file(s) for this stack>`.
- The Figma → code map is `<the ui-profile skill or equivalent>`.
- **Traps** — the near-misses that have actually caused drift here. Name them concretely:
  - `<two brand values that look alike and must not be collapsed>`
  - `<a composite/gradient token that maps to a component variant, not a raw value>`
- **Theming state**: `<e.g. v1 is light-only; dark is a later token swap — name tokens semantically so the swap stays mechanical>`.

## Test vehicle

`<what every ❌/⚠️ primitive ships with — a snapshot baseline, a CSF3 story, nothing>`. A row is not done until that artifact lands with it.
