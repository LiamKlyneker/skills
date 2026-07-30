---
name: scoped-context
description: Enforces the CONTEXT.md convention — always read scoped architectural context before modifying files in any directory.
user-invocable: false
---

# Scoped Context

Before modifying files in any directory, check for a `CONTEXT.md` in that directory and its parent directories up to the repository root. Read the ones relevant to your task.

Only load what's directly relevant. Do NOT read all context files.

If no `CONTEXT.md` exists for a directory, do not create one unprompted. After making changes, update it only if the documented architecture or patterns change.

See [convention-guide.md](convention-guide.md) for where to place `CONTEXT.md` files and what to include.
