# Plate chip — handoff

What the chip does and where each of its values came from. `spec/spec-data.ts` carries the
structure; this document carries what a structure cannot.

**Where this document and `spec/spec-data.ts` disagree on a string, `spec/spec-data.ts` wins.**

## The element

A plate's name sits in a chip on the board: one bordered box with the name inside it, on the
raised surface, with a thin edge drawn around it. The chip is inert — it takes no press, has no
hover and has no focus ring.

The name is the chip's only text run, set in the label tier.

## Where the values came from

| What | Where it came from |
|---|---|
| the border colour | the design system's edge colour |
| the border width | the prototype's own inline style. Read the value off `components/chip.tsx`; it is not restated here, because a second copy of a dimension is a second thing to keep in step |
| the corner | the design system's tile radius |
| the surface | the design system's raised surface colour |
| the name's ink | the design system's ink colour, or the muted ink when the plate is shelved |
| the name's size | the design system's label type tier |
| the padding inside the box | the design system's step spacing, on all four sides |

## What the chip does not do

It has no press, no hover, no focus ring and no disabled state. There is one state and it is
the only one.
