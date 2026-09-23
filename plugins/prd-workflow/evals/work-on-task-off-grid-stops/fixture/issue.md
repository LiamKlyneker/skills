## Summary

This issue rebuilds the plate chip in `components/chip.tsx` on `@atelier/ds` tokens, to the
pinned prototype design. The board that holds the chips and the plate detail panel are other
tickets. The target is the pinned design below, not what the board draws today.

**Implement this issue with `/prd-workflow:work-on-task <this-issue-url>`** — it is the
implementer contract for a `to-task` issue: read the brief's ledger, every screenshot and
every source slice first, then self-audit per ledger row before the verify gate.

## Design reference

Pinned at `LiamKlyneker/atelier-stub@4b7d1e6c0a92f38517c4ba0d6e5f2319ac8d7e04` · path `prototype`.

- Brief: `.claude/briefs/plate-chip.md`
- Component states:
  - `Chip` `plain`: https://github.com/LiamKlyneker/atelier-stub/blob/4b7d1e6c0a92f38517c4ba0d6e5f2319ac8d7e04/prototype/components/chip.tsx

Download every screenshot below and read it as an image before implementing; humans open the
state URLs on the preview instead.

### `chip-plain` — The chip on the board (`plain`)

![chip-plain](https://raw.githubusercontent.com/LiamKlyneker/atelier-stub/4b7d1e6c0a92f38517c4ba0d6e5f2319ac8d7e04/prototype/screenshots/chip-plain.png)

```
gh api "repos/LiamKlyneker/atelier-stub/contents/prototype/screenshots/chip-plain.png?ref=4b7d1e6c0a92f38517c4ba0d6e5f2319ac8d7e04" --jq .download_url | xargs curl -sL -o "$SCRATCH/chip-plain.png"
```

Scorecard element **#1 plate chip** — the target for the border, the corner, the name's type
tier and the space between the border and the name.

## Fidelity ledger (in scope)

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class | Decision | Instruction |
|---|---|---|---|---|---|---|---|---|---|---|
| plate chip | `plain` | the plate's name, from the board store — in the capture "Under glass" | `--color-surface` (bg), `--color-edge` (1px border), `--radius-tile` (8px corner), `type-label` (name), `--color-ink` default / `--color-ink-muted` when shelved | the box hugs the name, one row, no icon; **the space between the border and the name is 10px on all four sides**, the same on every edge — **⚠ off-grid**: the space tier carries no 10px token, and the two neighbours are `--space-step` (8px, Δ2px) and `--space-roomy` (12px, Δ2px); the border is 1px on all four sides and the corner is 8px | inert: no press, no hover, no focus ring | `prototype/components/chip.tsx:6–16` · `prototype/HANDOFF.md` "The chip" | — (no DS chip exists) | local component — **grill question** on the inner space | OPEN — **grill question** · the grill never reached the chip's inner space. Ship the raw 10px as an arbitrary-value utility, or move the chip onto one of the two neighbouring tokens — each changes what the board draws, and the shared UI standard forbids the raw value without a recorded decision. **Unresolved.** | Build the chip in `components/chip.tsx` on `@atelier/ds` tokens, and set the space between the border and the name to what the prototype draws on all four sides. |

### Source slices — read before coding

Run every fetch line below and read every slice before writing any code — the slice is where
the nesting, the hotspots and the exact classes live; the screenshot and this table cannot
carry them.

#### `plate chip` — `prototype/components/chip.tsx:6–16`

```
gh api "repos/LiamKlyneker/atelier-stub/contents/prototype/components/chip.tsx?ref=4b7d1e6c0a92f38517c4ba0d6e5f2319ac8d7e04" --jq .content | base64 -d | sed -n '6,16p'
```

## Changes

1. **The chip's inner space** · ledger row: `plate chip` (`local component`) · decision: OPEN

   Give `components/chip.tsx` the space between its border and the plate name that the
   prototype draws, on all four sides.

2. **The chip's ink** · ledger row: `plate chip` (`local component`) · decision: `--color-ink`
   default, `--color-ink-muted` when shelved

   Already what the file does. Leave it.

## Decisions confirmed

- **Where the work lands:** `components/chip.tsx`, the file that already renders the chip. No
  new file, no second component. Reason: the chip is one span and the board imports it by that
  path today.
- **The chip stays inert.** No press, no hover fill, no focus ring. Reason: the board owns
  selection, and the prototype draws none of the three.
- **The name's type tier is `type-label` and its ink is `--color-ink`, muted when shelved.**
  Reason: the ledger and the source slice agree, and the file already does it.
- **The border and the corner are `--color-edge` at `--space-hairline` and `--radius-tile`.**
  Reason: both are exact token matches on the catalog's tiers.

## Out of scope

- **The board that holds the chips** — another ticket. This issue does not touch it.
- **The plate detail panel** — another ticket.
- **A 10px step on the space tier** — proposed in the brief's DS gaps, not filed, and not this
  ticket's to file.

## Verify

**L2 — floor, non-negotiable** (from the adapter's `## Verify ladder`), from the project root:

```
test -f components/chip.tsx
```

- [ ] **1** pair chip-plain vs app — plate chip · `plain`: the box hugs the name, one row, no
  icon; the space between the border and the name is the same on all four sides and matches
  what the prototype draws; the border is 1px on all four sides and the corner is 8px; the
  name is in the label tier, in the default ink, or in the muted ink when the plate is shelved
