# Resolved by the code

- Click-away dismissal, Escape-to-close and focus return are already the DS popover's own
  behaviour (`packages/ds/src/popover.tsx`) — the prototype's gap in `HANDOFF.md` is not
  reproduced. *(project code recon)*
- `cmdk` ships arrow-key navigation through the list by default — no separate build needed.
  *(project code recon)*

# Round 1

❓ **Q1 — picker panel**: The ledger holds the panel as `DS with overrides` — `ComboboxContent`'s
default chrome is `w-72` (288px), `align="start"`, `shadow-md`. The design is a fixed 250px panel,
`align="end"`, no visible arrow, and a raw `0 8px 24px rgba(0,0,0,0.18)` lift with no token
equivalent. Width and align are a straightforward override. The shadow has no token — build it
local as a raw box-shadow, or accept `shadow-md` as close enough?

➡️ Override width to `w-[250px]` and `align="end"`; keep `shadow-md` rather than inventing a raw
value with no design-system precedent.

**Answer:** Accepted as recommended.

❓ **Q2 — search band**: The ledger holds the band as `DS change` — `ComboboxCommandInput`'s
wrapper only exposes `className` on the inner `input`, so the 12px horizontal padding and the
16px magnifier can't be reached through props alone. The design shows the magnifier at 16px in
`--color-ink-muted`, first in the row, 8px from the field. Build a local wrapper, or file the gap
against `@vitrine/ds` and ship the input at its current sizing until the gap lands?

➡️ File the gap as a blocker (icon stays 16px `--color-ink-muted`, wrapper padding 16px vs. the
design's 12px is the delta being filed); do not change the icon's size or color to work around it.

**Answer:** Accepted as recommended.

❓ **Q3 — option list band**: `CommandList` ships `p-1.5` (6px) and a `max-h-[300px]` cap the
design doesn't call for. Override the padding to 4px and the row gap to 2px; drop the max-height
or keep it?

➡️ Override padding and gap; drop the max-height — the design shows no scroll affordance and this
picker's list is short by construction.

**Answer:** Accepted as recommended.

❓ **Q4 — shelf row**: `CommandItem` highlights the first row on open (cmdk's default selected
state) and none of the design's captures show that. Suppress the open-time highlight?

➡️ Suppress it — no capture shows a highlighted row before a pointer or keyboard interaction.

**Answer:** Accepted as recommended.

❓ **Q5 — empty result**: `CommandEmpty` only renders when `cmdk` counts zero items, which
collides with the New shelf row question below. Resolve New shelf row first, then this follows.

➡️ Deferred to Q6.

**Answer:** Deferred, resolved by Q6.

❓ **Q6 — New shelf row**: Two candidates: a `ComboboxCommandItem` pinned last (breaks
`ComboboxCommandEmpty` in `no-matches`), or a sibling after `ComboboxCommandList` (keeps the
empty result working, but drops out of `cmdk`'s arrow-key flow and `Button` ships chrome the
design doesn't draw). Which one?

➡️ The sibling-after-list shape — the empty result rendering correctly in `no-matches` matters
more than keeping this one row in the arrow-key flow, and a plain unstyled row (not `Button`)
avoids the chrome mismatch.

**Answer:** Accepted as recommended.

❓ **Q7 — panel content, `naming`**: Does this ticket build the mode switch to the naming form, or
leave the whole `naming` state to the naming-form ticket?

➡️ Leave it to the naming-form ticket — this ticket only stops rendering the search band, the
option list band and the New shelf row when `naming` is active; it renders nothing in their place.

**Answer:** Accepted as recommended.

# Fidelity decisions

| Element | State(s) | Decision | Override / note |
|---|---|---|---|
| picker panel | all 5 popover states | DS with overrides — `ComboboxContent` | width `w-[250px]`; `align="end"`; keep `shadow-md` |
| click-away layer | all 5 popover states | DS as-is — `Combobox` (Radix `Popover` root) | — |
| search band | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` | DS change — `ComboboxCommandInput` | gap filed: wrapper padding + icon slot — blocker; magnifier stays 16px `--color-ink-muted` until the gap lands |
| option list band | `open-empty-pick`, `open-one-kept`, `filtered` | DS with overrides — `ComboboxCommand` + `ComboboxCommandList` | padding `p-1` (4px); row gap `gap-0.5` (2px) on the `cmdk-list-sizer`; drop `max-h-[300px]` |
| shelf row | `plain`, `kept`, `moving` | DS with overrides — `ComboboxCommandItem` | corner `rounded-[--radius-tile]`; padding `px-2`; text `type-body`; suppress the open-time highlight; `disabled` for `moving` |
| option rows — absent | `no-matches` | DS as-is — `ComboboxCommandList` | — |
| empty result | `no-matches` | DS with overrides — `ComboboxCommandEmpty` | `type-body`; `flex flex-col items-center gap-1`; renders correctly once New shelf row is a sibling, not a pinned item |
| New shelf row | all 4 list states | Build local | a sibling after `ComboboxCommandList`, not a `ComboboxCommandItem`; not `Button` — a plain row with its own top hairline |
| panel content — naming | `naming` | Override the design | this ticket renders nothing in place of the search band, option list band and New shelf row for `naming`; the mode switch and the form belong to the naming-form ticket |
