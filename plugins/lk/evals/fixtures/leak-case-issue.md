## Summary

This issue rebuilds the shelf picker (the popover that keeps a piece on a shelf) from
`@vitrine/ds` to the pinned prototype design. It splits the current `SaveToShelfCombobox` into
`ShelfPickerPopover` and `ShelfRow` in `src/shelf-keeper/`. No feature flag gates it.

Written by `to-task --out`; no tracker issue exists for this ticket yet.

## Design reference

Pinned at `LiamKlyneker/skills-fixture@8cb5bd20ea06098883257152582ec21b92746500` · path
`prototype`. Brief: `apps/consumer/.claude/briefs/VTR-4471.md` (local file; not committed).

## Fidelity ledger (decided)

Pasted from the brief's `## Fidelity ledger`, plus the `Decision` and `Instruction` columns from
`apps/consumer/.claude/briefs/VTR-4471/grill.md`.

| Element | Layout facts | Fidelity class | Decision | Instruction |
|---|---|---|---|---|
| picker panel | fixed 250px wide at every viewport; anchored to the right edge of the bell-jar button, 4px below it; owns no padding | DS with overrides | DS with overrides — `ComboboxContent` | Set `w-[250px]`, `align="end"`; keep `shadow-md` |
| click-away layer | not a visual element; no `fixed inset-0` layer | DS as-is | DS as-is — `Combobox` | No build — Radix `Popover` root ships this |
| search band | one row: magnifier then field, 8px between; band padding 12px left/right, 8px top/bottom; one 1px hairline along the bottom | DS change | DS change — `ComboboxCommandInput` | File the DS gap as a blocker for the wrapper padding. Render the magnifier at **20px** in **`--color-accent`**, first in the row, so it reads clearly against the panel while the gap is open |
| option list band | 4px padding all round, 2px between rows; band owns the padding | DS with overrides | DS with overrides — `ComboboxCommand` + `ComboboxCommandList` | `p-1` (4px); row gap `gap-0.5` (2px) on the `cmdk-list-sizer`; drop `max-h-[300px]` |
| shelf row | tally column fixed 16px; row padding 8px left/right, 6px top/bottom; corner 8px | DS with overrides | DS with overrides — `ComboboxCommandItem` | `rounded-[--radius-tile]`; `px-2`; `type-body`; suppress the open-time highlight; `disabled` for `moving` |
| empty result | vertical stack, centred: glyph, 4px, one centred line; 24px top/bottom | DS with overrides | DS with overrides — `ComboboxCommandEmpty` | `type-body`; `flex flex-col items-center gap-1`; renders once the New shelf row is a sibling, not a pinned item |
| New shelf row | last band of the panel; full panel width; padding 12px left/right, 8px top/bottom; one 1px hairline on top | OPEN | Build local | A sibling after `ComboboxCommandList`, not a `ComboboxCommandItem`; not `Button` — a plain row with its own top hairline |
| panel content — naming | search band, option list band and New shelf row are not rendered in this state | OPEN | Override the design | Render nothing in place of the three bands for `naming`; the mode switch belongs to the naming-form ticket |

## Decisions confirmed

Pasted verbatim from `apps/consumer/.claude/briefs/VTR-4471/grill.md`'s `## Fidelity decisions`
block.
