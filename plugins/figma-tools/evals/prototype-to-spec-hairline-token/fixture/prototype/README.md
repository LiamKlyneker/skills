# Plate chip — prototype

A designer-authored stub of one element on the Atelier plate board: the chip that carries a
plate's name. It is one component, it was never captured, and it ships nothing.

`prototype-to-spec` reads it from the working tree at the directory the project adapter names
in its `### Prototype source` → `Path:` row.

## What is in here

| Path | What it is |
|---|---|
| `spec/spec-data.ts` | the spec: one use case, one step, one component, one state, the rules and the token notes |
| `spec/types.ts` | the types `spec/spec-data.ts` is declared in |
| `HANDOFF.md` | behaviour, and where each value came from |
| `README.md` | this file |
| `components/chip.tsx` | the prototype's one component — the `codeRef` in `spec/spec-data.ts` points here |
| `spec/component-states/chip/plain/page.tsx` | the props the chip renders with in that state |

## It was never captured

**There is no `spec/screenshots/` directory and no state preview.** The step and the state both
carry `null`, and the only evidence for a layout fact is the component source and this
document.

## It builds on nothing

**The prototype imports no component from `@atelier/ds`.** It imports the theme stylesheet and
nothing else, and hand-rolls the chip out of a `span`.
