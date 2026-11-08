# Plate chip — handoff

What the chip does and where each of its values came from. `spec/spec-data.ts` carries the
structure; this document carries what a structure cannot.

**Where this document and `spec/spec-data.ts` disagree on a string, `spec/spec-data.ts` wins.**

## The element

A plate's name sits in a chip on the board: one bordered box with the name inside it, on the
raised surface, with the board's hairline drawn around it. The chip is inert — it takes no
press, has no hover and has no focus ring.

The name is the chip's only text run, set in the label tier.

## Where the values came from

| What | Where it came from |
|---|---|
| the border | the design system's hairline dimension, drawn in the edge colour |
| the corner | the design system's tile radius |
| the surface | the design system's raised surface colour |
| the name's ink | the design system's ink colour, or the muted ink when the plate is shelved |
| the name's size | the design system's label type tier |
| the padding inside the box | **nothing** — the designer set it by eye in the prototype's own inline style, and no step of the design system's spacing scale is that value. Read it off `components/chip.tsx`; it is not restated here, because a second copy of a value nobody has a token for is a second thing to keep in step |

## What the chip does not do

It has no press, no hover, no focus ring and no disabled state. There is one state and it is
the only one.
