# [TASK] Plate chip: the bordered name box, on the design system

Component: `Chip`
Files: `components/chip.tsx`

## What to build

The chip the designers prototyped, built out of `@atelier/ds` rather than out of the
prototype's own `span`s. The board that holds the chips and the plate detail panel are other
tickets and are not in scope here.

## Acceptance criteria

- The chip is a bordered box on the raised surface, with the plate name inside it.
- The border is the board's hairline and the corner is the tile radius.
- The name sits in the label type tier, in the default ink, or in the muted ink when the plate
  is shelved.
- The space between the border and the name is the same on all four sides, and it matches what
  the prototype draws.
- The chip is inert: no press, no hover, no focus ring.

## Divergences from the prototype

None — the ticket takes the prototype as drawn.
