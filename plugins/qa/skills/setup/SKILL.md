---
name: setup
description: Set up the current project for the qa plugin — write or gap-fill `.claude/project/adapter.md` for the `qa` bundle, then run doctor. Run it after installing or updating the plugin. It does not install plugins. Invoke /qa:setup to set up, or /qa:setup doctor to check an existing setup.
disable-model-invocation: true
---

# Setup

Read `../install/setup.md` and follow it. It is the one installer every plugin in this
marketplace shares; this file only names the bundles this plugin ships.

| Bundle | Covers |
|---|---|
| `qa` | `prove-branch` |

## Picking the bundle

- **No argument** → Set up `qa`.
- **An argument naming a bundle above, or describing one** ("the QA part") → that bundle.
- **`doctor`** → doctor mode, with `--bundle` for each bundle above that the adapter already
  carries sections for. With no adapter at all, pass `--bundle` for every bundle above, so the
  missing adapter reports as a problem rather than a clean run.
- **A bundle this plugin does not ship** → name the plugin that ships it, from
  `../install/bundles.md`, and stop.
