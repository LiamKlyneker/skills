---
name: setup
description: Set up the current project for the ado-workflow plugin — write or gap-fill `.claude/project/adapter.md` for the `ado-workflow` and `ado-qa` bundles, then run doctor. Run it after installing or updating the plugin. It does not install plugins. Invoke /ado-workflow:setup to set up, or /ado-workflow:setup doctor to check an existing setup.
disable-model-invocation: true
---

# Setup

Read `../install/setup.md` and follow it. It is the one installer every plugin in this
marketplace shares; this file only names the bundles this plugin ships.

| Bundle | Covers |
|---|---|
| `ado-workflow` | the `[SPEC]` loop |
| `ado-qa` | `manual-qa` and `triage` |

## Picking the bundle

- **No argument** → Ask which of the bundles above to set up — one, or both. Offer both as the default.
- **An argument naming a bundle above, or describing one** ("the QA part") → that bundle.
- **`doctor`** → doctor mode, with `--bundle` for each bundle above that the adapter already
  carries sections for. With no adapter at all, pass `--bundle` for every bundle above, so the
  missing adapter reports as a problem rather than a clean run.
- **A bundle this plugin does not ship** → name the plugin that ships it, from
  `../install/bundles.md`, and stop.

Two bundles run as two passes of `setup <bundle>` against the same adapter, in the table's
order. The second pass is a gap-fill of an adapter the first one wrote, so it asks only for the
sections the first did not. Run doctor once per bundle at the end, not after each pass.
