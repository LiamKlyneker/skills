# Design brief — the plate board header

Pinned at figma `Qx7AtelierBoard` · node `12:40` · version `2026-09-30` · brief `.claude/briefs/plate-board.md`

The board's top band: the heading and the plate chip under it. The board grid and the plate
detail panel are other tickets.

## Component states

| State | Screenshot | What it shows |
|---|---|---|
| `board-default` | `.claude/briefs/plate-board/screenshots/board-default.png` | the heading above one chip, on the raised surface |

## Fidelity ledger

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class |
|---|---|---|---|---|---|---|---|---|
| board heading | `board-default` | "Plates" | `type-title-quiet` (heading), `--color-ink-hush` (heading text) | sits flush left above the first chip row, 24px above it; one line, never wraps | inert | `Qx7AtelierBoard:12:41` | `Heading` (level 2) | DS as-is |
| plate chip | `board-default` | the plate's name, from the board store — in the capture "Under glass" | `--color-surface` (bg), `--color-edge` (1px border), `--radius-tile` (8px corner), `type-label` (name) | the box hugs the name, one row, no icon; 8px between the border and the name on all four sides; the border is 1px on all four sides and the corner is 8px | inert: no press, no hover, no focus ring | `Qx7AtelierBoard:12:44` | — (no DS chip exists) | local component |
