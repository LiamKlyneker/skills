# Design brief — the plate chip

Pinned at `LiamKlyneker/atelier-stub@4b7d1e6c0a92f38517c4ba0d6e5f2319ac8d7e04` · path `prototype`.

The board draws one chip per plate. This brief covers the chip and nothing else: the board
that holds the chips and the plate detail panel are other tickets.

## Component states

| State | Screenshot | What it shows |
|---|---|---|
| `plain` | `prototype/screenshots/chip-plain.png` | the chip on the raised surface, plate name inside the bordered box |

## Fidelity ledger

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class | Decision | Instruction |
|---|---|---|---|---|---|---|---|---|---|---|
| plate chip | `plain` | the plate's name, from the board store — in the capture "Under glass" | `--color-surface` (bg), `--color-edge` (1px border), `--radius-tile` (8px corner), `type-label` (name), `--color-ink` default / `--color-ink-muted` when shelved | the box hugs the name, one row, no icon; **the space between the border and the name is 10px on all four sides**, the same on every edge — **⚠ off-grid**: the space tier carries no 10px token, and the two neighbours are `--space-step` (8px, Δ2px) and `--space-roomy` (12px, Δ2px); the border is 1px on all four sides and the corner is 8px | inert: no press, no hover, no focus ring | `prototype/components/chip.tsx:6–16` · `prototype/HANDOFF.md` "The chip" | — (no DS chip exists) | local component — **grill question** on the inner space | OPEN — **grill question** · the grill never reached the chip's inner space. Ship the raw 10px as an arbitrary-value utility, or move the chip onto one of the two neighbouring tokens — each changes what the board draws, and the shared UI standard forbids the raw value without a recorded decision. **Unresolved.** | Build the chip in `components/chip.tsx` on `@atelier/ds` tokens, and set the space between the border and the name to what the prototype draws on all four sides. |

## DS gaps (proposed, not filed)

- A 10px step on the space tier. The chip is the only element that asks for one, and one
  element is not a scale.

## Notes

- The prototype writes the chip's inner space as an inline `style`, not as a utility class —
  it predates the token scale.
- `type-label` already matches; nothing about the name's type tier is in question.
