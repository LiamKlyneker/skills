# UI Profile Spec

The per-repo memory of the design-to-code skills: a **generated project skill** at `.claude/skills/<repo>-ui/SKILL.md` in the host repo. `tokens-init` creates it at bootstrap; `figma-component` creates it via discovery when missing, reads it every run, and appends to it. Because it's a skill, every session in the host repo benefits from the map (grill-me's "consult the project UI skill" hook included) — same role neonplace's `building-luar-ui` plays, but generated.

## Frontmatter

```yaml
name: <repo>-ui
description: <Repo>'s UI map — Figma→code token map, primitive homes, story idiom. Consult before implementing any visual design in this repo.
```

## Sections

### Stack
Tailwind version + config location, headless lib in use, styling approach (`cva`? CSS modules?), how tokens are consumed.

### Figma → code map
The Token Manifest's resolution source:

| Figma token | CSS var | Tailwind utility | Notes / traps |
|---|---|---|---|

Document near-miss traps explicitly (e.g. two similar greens, a gradient token that maps to a component variant) — this table is what prevents improvised tokens.

#### Typography

Its own table — typography comes from **text styles**, not variables, and its alias structure lives in `boundVariables` (see `../../_shared/ui-standard.md`). One Figma text style = one `text-*` utility:

| Figma text style | Tailwind utility | Font | Size/LH | Bound to | Used by |
|---|---|---|---|---|---|

`Bound to` is the style's `boundVariables` targets — an empty cell means a type token with no primitive beneath it, which is a finding, not a formatting gap. `Used by` names the components actually consuming the role; a row nothing consumes yet is speculative and should say so rather than implying precedent.

### Primitive homes
Where each class of component lives: registry primitives (`components/ui/`), the shared lib, colocated `_components/`. Plus a one-line inventory of existing primitives: name → path → API summary.

### Story idiom
Story file location/naming, CSF version, decorators — anything the repo does differently from `_shared/ui-standard.md`. Repo idiom beats the canon.

### Minted log
Append-only: `| date | token/primitive | minted by | source node |`

### Design references (fallback)
Only when the host repo lacks the scoped-context `CONTEXT.md` convention: `| area | node URL | node name | verified |`

## Staleness

- The map misses (a token exists in code but not in the map; a primitive moved) → re-run discovery, update the profile, note the correction.
- A recorded node name that no longer matches live `get_metadata` → flag stale and ask for a fresh URL. Never resolve against a drifted node.
