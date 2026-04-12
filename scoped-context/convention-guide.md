# CONTEXT.md Convention Guide

A lightweight convention for giving AI assistants scoped architectural context per directory. Instead of one massive docs file, each route or feature directory gets a focused `CONTEXT.md` that describes its local architecture.

## Why

- AI assistants work better with focused, relevant context than with everything at once
- Developers document decisions close to where they matter
- Context stays up-to-date because it lives next to the code it describes

## Placement Rules

### Where to put CONTEXT.md

- **Workspace packages** — each package in a monorepo (`packages/foo/`, `apps/web/`)
- **Route directories** — each page/route that has meaningful architecture
- **Route group roots** — overview of the group's shared layout, auth, and components
- **Feature directories** — standalone features with their own patterns (`lib/<feature>/`, `services/<name>/`)
- **Top-level docs** — cross-cutting concerns can use named files at the project root

### Where NOT to put CONTEXT.md

- Individual component folders (`_components/my-widget/`) — merge into the parent route's CONTEXT.md
- Utility folders with simple exports
- Anywhere the content would be < 5 lines (just put it in the parent)

## Content Template

```markdown
# Feature/Route Name

One-line description of what this area does.

## Files

| File | Description |
|------|-------------|
| `index.ts` | Entry point. Exports X, orchestrates Y. |
| `lib/helpers.ts` | Shared utilities for Z. |

## Architecture

How the pieces fit together. Data flow direction, key abstractions, component composition.

## Key Patterns

Patterns specific to this area that differ from or extend the project-wide patterns in CLAUDE.md.
```

## What NOT to Include

- Full prop type definitions (TypeScript is the source of truth)
- Code examples longer than 5 lines (link to the file instead)
- Implementation details that change frequently
- Anything already covered in the project's CLAUDE.md

## Installing in a Project

1. Place the skill in `.agents/skills/scoped-context/` (canonical location) and create symlinks:

```bash
ln -s ../../.agents/skills/scoped-context .claude/skills/scoped-context
ln -s ../../.agents/skills/scoped-context .agent/skills/scoped-context
```

2. Add the CONTEXT.md convention section to your `CLAUDE.md`:

```markdown
### Context Files

Each route/package can have a `CONTEXT.md` file documenting technical decisions.
**Always read the relevant `CONTEXT.md` before working on a package or route**.

The `scoped-context` skill (`.agents/skills/scoped-context/`) automates context loading.
See its `convention-guide.md` for placement rules.
```

3. Start adding `CONTEXT.md` files to your route and feature directories as you work on them
