# [TASK] Shelf picker: the popover and its rows, on the design system

Component: `ShelfPickerPopover`
Component: `ShelfRow`
Files: `components/shelf-picker-popover.tsx`, `components/shelf-row.tsx`

## What to build

The shelf picker the designers prototyped, built out of `@vitrine/ds` rather than out of the
prototype's own `div`s. The bell-jar button, the naming panel and the notice rail are other
tickets and are not in scope here.

## Acceptance criteria

- The picker hangs off the right edge of the button that opens it, and a click outside it
  dismisses it.
- The search field carries its glyph on the left and a hairline under the whole row.
- A shelf row holds its tick column whether or not the shelf is ticked, so the label never
  shifts when a row is ticked.
- Typing narrows the list, case-insensitively, against the shelf name only.
- A query that matches nothing shows the glyph, the empty line under it and the New shelf row.
- The New shelf row stays at the foot of the list in every state of the list.

## Divergences from the prototype

- The picker **closes** as soon as a shelf is ticked. The prototype keeps it open and applies
  the tick in place; this ticket does not.
