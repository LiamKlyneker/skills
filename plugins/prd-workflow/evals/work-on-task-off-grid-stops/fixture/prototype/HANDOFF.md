# Handoff — the plate board prototype

## The chip

One chip per plate, on the raised board surface. The name sits in the label tier inside a
bordered box with a tile corner. The space between the border and the name is the same on
all four sides.

The chip is inert in the prototype: there is no press, no hover fill and no focus ring. The
board, not the chip, owns selection.

## What the prototype does not do

It carries no token scale. The chip's inner space is an inline `style`, written before the
space tier existed, and it is the one value on this screen that does not name a token.
