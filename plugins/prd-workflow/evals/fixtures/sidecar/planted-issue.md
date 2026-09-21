## Summary

This issue rebuilds the shelf picker (the popover that keeps a piece on a shelf) from `@vitrine/ds` to the pinned prototype design. It splits the current `SaveToShelfCombobox` into `ShelfPickerPopover` and `ShelfRow` in `src/shelf-keeper/`, and it changes three behaviours: filtering becomes substring-only, the New shelf row stays in every list state, and a row press closes the picker. No feature flag gates it. The target is the pinned design below, not the current app.

**Implement this issue with `/prd-workflow:work-on-task <this-issue-url>`** — it is the implementer contract for
a `to-task` issue: read the brief's ledger, every screenshot and every source slice first, then
self-audit per ledger row before the verify gate.

## Design reference

Pinned at `LiamKlyneker/skills-fixture@8cb5bd20ea06098883257152582ec21b92746500` · path `prototype`.

- Spec: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec-data.ts
- Brief: `apps/consumer/capture/brief.md` (local file; not committed)
- Component states:
  - `open-empty-pick`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-picker-popover/open-empty-pick/page.tsx
  - `open-one-kept`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-picker-popover/open-one-kept/page.tsx
  - `filtered`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-picker-popover/filtered/page.tsx
  - `no-matches`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-picker-popover/no-matches/page.tsx
  - `naming`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-picker-popover/naming/page.tsx
  - `ShelfRow` `plain`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-row/plain/page.tsx
  - `ShelfRow` `kept`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-row/kept/page.tsx
  - `ShelfRow` `moving`: https://github.com/LiamKlyneker/skills-fixture/blob/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-row/moving/page.tsx

Download every screenshot below and read it as an image before implementing; humans open the state URLs on the preview instead.

### `uc1-s2` — Shelf picker open, nothing ticked yet (`open-empty-pick`)

![uc1-s2](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/screenshots/uc1-s2.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/screenshots/uc1-s2.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/uc1-s2.png"
```

Scorecard elements **#1 picker panel**, **#2 search band**, **#3 option list band**, **#4 shelf row**, **#6 New shelf row** — the target for the panel's width, anchor and chrome, the search band, the unticked rows and the New shelf row at the foot.

### `uc1-s3` — A shelf ticked (`open-one-kept`)

![uc1-s3](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/screenshots/uc1-s3.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/screenshots/uc1-s3.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/uc1-s3.png"
```

Scorecard element **#4 shelf row** — the target for the tally mark in accent, and for the labels that do not shift between ticked and unticked rows. The prototype keeps the panel open after a tick; this ticket closes it, so this still is the ticked row's look, not the post-press flow.

### `uc1-s4` — The list filtered as the curator types (`filtered`)

![uc1-s4](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/screenshots/uc1-s4.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/screenshots/uc1-s4.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/uc1-s4.png"
```

Scorecard elements **#2 search band**, **#3 option list band** — the target for the typed query "bra" and the list narrowed to one shelf.

### `uc1-s5` — Nothing matches what was typed (`no-matches`)

![uc1-s5](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/screenshots/uc1-s5.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/screenshots/uc1-s5.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/uc1-s5.png"
```

Scorecard elements **#5 empty result**, **#6 New shelf row** — the target for the dust cover, the empty line, and the New shelf row that stays under them.

### `naming` — The naming form in place of the list

![naming](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-picker-popover/naming/preview.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/component-states/shelf-picker-popover/naming/preview.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/naming.png"
```

Scorecard elements **#1 picker panel**, **#7 panel content — naming** — the target for the panel chrome in `naming`, and for the search band, list and New shelf row being absent. The form's own look belongs to the naming-form ticket.

### `ShelfRow` `plain` — Not on this shelf

![shelf-row-plain](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-row/plain/preview.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/component-states/shelf-row/plain/preview.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/shelf-row-plain.png"
```

Scorecard element **#4 shelf row** — the target for the empty tally column holding its width.

### `ShelfRow` `kept` — On this shelf

![shelf-row-kept](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-row/kept/preview.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/component-states/shelf-row/kept/preview.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/shelf-row-kept.png"
```

Scorecard element **#4 shelf row** — the target for the tally mark in accent.

### `ShelfRow` `moving` — The toggle is in flight

![shelf-row-moving](https://raw.githubusercontent.com/LiamKlyneker/skills-fixture/8cb5bd20ea06098883257152582ec21b92746500/prototype/spec/component-states/shelf-row/moving/preview.png)

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/spec/component-states/shelf-row/moving/preview.png?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .download_url | xargs curl -sL -o "$SCRATCH/shelf-row-moving.png"
```

Scorecard element **#4 shelf row** — the target for the dimmed, inert row. No step screenshot shows this state; this preview is its only image.

## Fidelity ledger (in scope)

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class | Decision | Instruction |
|---|---|---|---|---|---|---|---|---|---|---|
| picker panel | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches`, `naming` · uc1-s2, uc1-s3, uc1-s4, uc1-s5 | — | `--color-surface` (bg), `--color-edge` (1px border), `--radius-panel` (16px corner) · raw: `0 8px 24px rgba(0,0,0,0.18)` drop shadow — **⚠ no equivalent, do not invent** | fixed **250px** wide at every viewport, never hugs content; anchored to the **right** edge of the bell-jar button, 4px below it; the panel owns **no** padding — the search band, the option list band and the New shelf row each own their own; vertical stack of those three bands, each full panel width | inert itself; dismissal belongs to the click-away row | `components/shelf-picker-popover.tsx:L43–L46` · `design_handoff_shelf_picker/README.md` "The panel" | `ComboboxContent` | DS with overrides — **grill question** · `PopoverContent` deltas under `ComboboxContent`: width `w-72` (288px) → `w-[250px]`; `align` defaults `start` → pass `align="end"`; `sideOffset` 4 = design, keep; padding already `p-0` from `ComboboxContent`, keep; radius, border, bg and ink match, keep; shadow `shadow-md` ≠ the design's lift, and the design's value is raw — the grill decides between `shadow-md` as-is and a new token (see DS gaps); no arrow is rendered, nothing to remove; `overflow-hidden` is on by default | `DS with overrides` — `className="w-[250px]"`, `align="end"`. Keep `sideOffset` 4, `p-0`, the radius, the border and the surface. Keep `shadow-md` in place of the design's raw `0 8px 24px rgba(0,0,0,0.18)`, with no token filed. The same chrome applies in every state, including `naming` | Use `ComboboxContent` + override `className="w-[250px]"` and `align="end"`. Keep `sideOffset` 4 and `shadow-md`. File no lift token. |
| click-away layer | all 5 popover states · uc1-s2 | — | — | not a visual element in the DS build: no `fixed inset-0` layer is rendered | an outside pointer-down closes the panel; Escape closes it; focus moves into the panel on open and returns to the trigger on close — the DS behaviour, which the prototype lacks and `HANDOFF.md` calls the prototype's gap | `components/shelf-picker-popover.tsx:L23–L24, L45` · `HANDOFF.md` "What the panel does not do" | `Combobox` (Radix `Popover` root) | DS as-is | `DS as-is` — no `fixed inset-0` layer. An outside press or Escape closes the panel, and focus moves in on open and returns to the trigger | Use `Combobox` as-is, no overrides. Render no click-away layer of your own. |
| search band | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` · uc1-s2 → uc1-s5 | placeholder "Search shelves…" (single ellipsis character) · accessible name "Search shelves" | hairline `--color-edge`; magnifier `--color-ink-muted`; field text `type-body` in `--color-ink`; placeholder `type-body` in `--color-ink-muted` | **same element; content differs**: `open-empty-pick` / `open-one-kept` show the placeholder, `filtered` shows "bra", `no-matches` shows "vitrine". One row: magnifier then field, 8px between; band padding **12px** left and right, **8px** top and bottom; one 1px hairline along the band's bottom, **owned by the band**, spanning the full panel width; the field has no border and no background and takes the rest of the row. Icon: `LoupeGlassIcon` **16px** `--color-ink-muted`, first in the row | typing narrows the list per bl3; the field owns focus when the panel opens (DS behaviour) | `components/shelf-picker-popover.tsx:L51–L62` · `design_handoff_shelf_picker/README.md` "The search band" | `ComboboxCommandInput` | DS change — **grill question** · shipped wrapper is `flex items-center gap-2 border-b border-[--color-edge] px-4` with the loupe in `Icon size="sm"` (**14px**); its `className` reaches only the inner `input`. So: horizontal padding 16px ≠ 12px, no path; loupe 14px ≠ 16px, no path; the input is `h-10 py-3 text-sm` (40px row, 14px text) ≠ 8px + 22px `type-body` — fixable through `className` (`h-auto py-2 type-body`). Gap 8px, hairline and muted loupe match | `DS with overrides` — `className="h-auto py-2 type-body"` on the input. Placeholder "Search shelves…". Known deltas from the stills: 16px horizontal padding, not 12px, and a 14px loupe, not 16px. No DS blocker filed | Use `ComboboxCommandInput` + override `className="h-auto py-2 type-body"` on the input, placeholder "Search shelves…". Add no second magnifier. Leave the wrapper padding and the loupe size as the DS ships them. |
| option list band | `open-empty-pick`, `open-one-kept`, `filtered` · uc1-s2, uc1-s3, uc1-s4 | — | — | **4px** padding all round, **2px** between rows; the band owns that padding, a row does not; rows are direct children in one vertical stack | inert; keyboard arrow navigation through the rows comes with `cmdk` (the prototype has none; the design does not forbid it) | `components/shelf-picker-popover.tsx:L63, L70–L78` · `design_handoff_shelf_picker/README.md` "The option list" | `ComboboxCommand` (`shouldFilter={false}`) + `ComboboxCommandList` | DS with overrides — **grill question** · `CommandList` deltas: padding `p-1.5` (6px) → `p-1` (4px); `cmdk` wraps items in a `[cmdk-list-sizer]` div, so a `gap` on the list does not reach the rows — set the 2px on the sizer (`[&_[cmdk-list-sizer]]:flex [&_[cmdk-list-sizer]]:flex-col [&_[cmdk-list-sizer]]:gap-0.5`) or on each item; `max-h-[300px] overflow-y-auto` is on by default and the design states no max-height — keep or drop is a grill call; `ComboboxCommand` adds its own `rounded-[--radius-panel] bg-[--color-surface]`, which matches the panel | `DS with overrides` — `shouldFilter={false}` on `ComboboxCommand`. `p-[--space-snug] [&_[cmdk-list-sizer]]:flex [&_[cmdk-list-sizer]]:flex-col [&_[cmdk-list-sizer]]:gap-0.5` on the list. Keep `max-h-[300px] overflow-y-auto` | Use `ComboboxCommand` + `ComboboxCommandList` + override as named in Decision. Filter in the app per bl3. |
| shelf row | `plain`, `kept`, `moving` (ShelfRow) · `open-empty-pick`, `open-one-kept`, `filtered` · uc1-s2, uc1-s3, uc1-s4 | the shelf's name, from the shelf store — in the captures "Upper bay", "Brass niche", "Under glass", "Cold drawer" | name `type-body` in `--color-ink`; tally mark `--color-accent`; hover fill `--color-shade`; corner `--radius-tile` | **same element; content differs**: `plain` draws the tally mark at **zero opacity**, `kept` draws it in accent, `moving` dims the whole row to 50% opacity. Anatomy: 100% wide; **tally column and shelf name in one flow**, 8px between; the tally column is a **fixed 16px** in every state, so no name shifts sideways; the name takes the rest. Row padding **8px** left and right, **6px** top and bottom; corner 8px. Icon: `TallyMarkIcon` **16px** `--color-accent` in `Icon size="md" tone="accent"`; unticked it stays in the layout with `opacity-0` — never removed | **the whole row owns the press** (`onSelect` on the item, which also takes Enter); nothing inside it is separately pressable. Press toggles the piece on that shelf, applies at once, and **closes the picker** (ticket override; untick and `moving` timing are OPEN — see Overrides). Hover fills the row `--color-shade`; **no focus ring**. `moving`: inert, no press, 50% opacity | `components/shelf-row.tsx:L10–L27` · `components/shelf-picker-popover.tsx:L70–L78` · `spec/component-states/shelf-row/{plain,kept,moving}/page.tsx` · `design_handoff_shelf_picker/README.md` "The option list" | `ComboboxCommandItem` | DS with overrides — **grill question** · `CommandItem` deltas: corner `rounded-[--radius-pill]` → `rounded-[--radius-tile]`; padding `px-3` → `px-2` (py-1.5 matches); text `text-sm` → `type-body`; gap-2 matches; highlight is `data-[selected=true]:bg-[--color-shade]`, which `cmdk` sets on pointer hover **and** on keyboard focus, and `cmdk` **selects the first item on open** — so the first row renders shaded on open, and none of uc1-s2 → uc1-s4 shows that; the grill decides whether to suppress the open-time highlight; `disabled` gives `pointer-events-none opacity-50`, which **matches** `moving` exactly — pass `disabled` for `moving`, and `outline-none` already gives no focus ring | `DS with overrides` — `className="rounded-[--radius-tile] px-[--space-step] type-body"`. Tally is `<Icon size="md" tone="accent"><TallyMarkIcon /></Icon>`, `opacity-0` when not kept and never removed. `moving` means `disabled`. The press toggles, awaits, then closes the picker, tick or untick. Known delta from the stills: cmdk shades the first row on open | Use `ComboboxCommandItem` + override as named in Decision. Pass `disabled` while the toggle is in flight. Close the picker after the toggle resolves, for a tick and for an untick. |
| option rows — absent | `no-matches` · uc1-s5 | — | — | **not rendered in this state**: zero rows; the option list band shows the empty result instead and keeps its 4px padding | — | `components/shelf-picker-popover.tsx:L64` | `ComboboxCommandList` | DS as-is | `DS as-is` — zero rows. The band keeps its 4px padding | Use `ComboboxCommandList` as-is, no overrides. |
| empty result | `no-matches` · uc1-s5 | "No shelves found." — `spec-data.ts` and the source win; `design_handoff_shelf_picker/README.md` and `HANDOFF.md` read "No shelves.", which is stale | glyph `--color-ink-muted`; line `type-body` in `--color-ink-muted` | **rendered only when zero shelves match**, in place of the rows, inside the option list band. Vertical stack, centred: glyph, **4px**, then one centred line; 24px top and bottom. Icon: `DustCoverIcon` **20px** `--color-ink-muted` in `Icon size="lg" tone="muted"` | inert | `components/shelf-picker-popover.tsx:L64–L68` · `design_handoff_shelf_picker/README.md` "The empty result" | `ComboboxCommandEmpty` | DS with overrides — **grill question** · `CommandEmpty` deltas: `text-sm` → `type-body`; add `flex flex-col items-center gap-1` for the glyph stack; `py-6 text-center text-[--color-ink-muted]` match. It renders only when `cmdk` counts zero items — **it never renders if the New shelf row is a `ComboboxCommandItem`** (see that row) | `DS with overrides` — `className="flex flex-col items-center gap-[--space-snug] type-body"`. `<Icon size="lg" tone="muted"><DustCoverIcon /></Icon>` above "No shelves found." | Use `ComboboxCommandEmpty` + override as named in Decision, copy "No shelves found." |
| New shelf row | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` · uc1-s2 → uc1-s5 | "New shelf" | hairline `--color-edge`; glyph and label `--color-accent`; label `type-body` | the **last** band of the panel in every list state, below the option list band and the empty result alike; full panel width; padding **12px** left and right, **8px** top and bottom; one 1px hairline along its **top, owned by the row**, spanning the full panel width. Glyph and label in **one flow**, 8px between, left-aligned. No pill, no fill, no button chrome. Icon: `NewNicheIcon` **16px** `--color-accent` in `Icon size="md" tone="accent"` | **the whole row owns the press**; in the prototype it switches the panel to `naming`. Whether this ticket wires that press, given the naming form is another ticket, is a grill question. Hover and focus treatment: none in the source or the handoff | `components/shelf-picker-popover.tsx:L81–L88` · `design_handoff_shelf_picker/README.md` "The New shelf row" | — (`ComboboxCommandItem` or a sibling of `ComboboxCommandList`) | OPEN — **grill question** · as a `ComboboxCommandItem` pinned last: breaks the empty result (see above) and sits inside the list's padding, so the hairline would not span the panel; it would also be filtered unless the item is excluded. As a sibling after the list: renders the empty result and spans the panel, but leaves `cmdk`'s arrow-key flow, and `Button` (`variant`/`size` chrome) is not what the design draws | `local component` — private `NewShelfRow` in `shelf-picker-popover.tsx`. A plain `button`, a sibling after `ComboboxCommandList` inside `ComboboxCommand`: `flex w-full items-center gap-[--space-step] border-t border-[--color-edge] px-3 py-[--space-step] type-body text-[--color-accent]` with `<Icon size="md" tone="accent"><NewNicheIcon /></Icon>` and "New shelf". No DS `Button`: even `ghost` carries a pill radius and `font-medium`. Reached by Tab, not arrow keys. Press sets naming. No hover fill. Keep the browser's default `focus-visible` outline, with no `outline-none` | Build local `NewShelfRow` as named in Decision. It must not be a `ComboboxCommandItem`, so cmdk never counts it and it stays in every list state. |
| panel content — naming | `naming` | — (form copy belongs to the naming-form ticket) | — | **the search band, the option list band and the New shelf row are not rendered in this state**; the naming form fills the same panel at the same 250px width; no second layer opens | the form's own actions leave this state; out of scope here | `components/shelf-picker-popover.tsx:L47–L48` · `spec/component-states/shelf-picker-popover/naming/page.tsx` (`mode="naming"`) · `spec-data.ts` uc1-s6 annotation | `ComboboxContent` with the form in place of `ComboboxCommand` | OPEN — **grill question** · whether this ticket builds the mode switch (and a placeholder for the form) or leaves the whole `naming` state to the naming-form ticket | `DS with overrides` — `ComboboxContent` with the form in place of `ComboboxCommand`. The search band, the list band and the New shelf row are not rendered. The existing `NewShelfInlinePanel` renders unchanged and owns its own padding. Panel chrome as in the picker panel row | Keep the naming switch in `ShelfPickerPopover`. In `naming`, render `NewShelfInlinePanel` unchanged in place of `ComboboxCommand`. Closing the popover leaves `naming`. |

### Source slices — read before coding

Run every fetch line below and read every slice before writing any code — the slice is where the hotspots, the nesting, the icon sizes and the exact classes live; the screenshots and this table cannot carry them.

#### `picker panel` — `components/shelf-picker-popover.tsx:43–46`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '43,46p'
```

#### `search band` — `components/shelf-picker-popover.tsx:51–62`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '51,62p'
```

#### `option list band` — `components/shelf-picker-popover.tsx:63, 70–78`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '63p;70,78p'
```

#### `shelf row` — `components/shelf-row.tsx:10–27`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-row.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '10,27p'
```

#### `shelf row` — `components/shelf-picker-popover.tsx:70–78`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '70,78p'
```

#### `empty result` — `components/shelf-picker-popover.tsx:64–68`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '64,68p'
```

#### `New shelf row` — `components/shelf-picker-popover.tsx:81–88`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '81,88p'
```

#### `panel content — naming` — `components/shelf-picker-popover.tsx:47–48`

```
gh api "repos/LiamKlyneker/skills-fixture/contents/prototype/components/shelf-picker-popover.tsx?ref=8cb5bd20ea06098883257152582ec21b92746500" --jq .content | base64 -d | sed -n '47,48p'
```

## Changes

1. **Split the picker into two files** · engineering, no ledger row · decision: split `SaveToShelfCombobox` into `ShelfPickerPopover` and `ShelfRow`

   Create `src/shelf-keeper/shelf-picker-popover.tsx` exporting `ShelfPickerPopover`, and `src/shelf-keeper/shelf-row.tsx` exporting `ShelfRow`. Delete `src/shelf-keeper/save-to-shelf-combobox.tsx`. `ShelfPickerPopover` keeps the current props contract (`specimenId`, `kind`, and a `trigger` node wrapped in `ComboboxTrigger asChild`), and it owns the controlled `open` state and the naming switch. In `KeepSpecimenButton`, swap the import to `ShelfPickerPopover`; change nothing else in that component.

2. **Picker panel — width, anchor, chrome** · ledger row: `picker panel` (`DS with overrides`) · decision: `ComboboxContent` with the overrides named in the row's Decision cell

   The panel is a fixed 250px wide at every viewport, anchored to the right edge of the bell-jar button. It owns no padding. Keep the shipped offset, radius, border, surface and shadow. The panel fades in over 150ms and fades out over 100ms. File no shadow token. The panel hugs its content, so its width tracks the longest shelf name.

3. **Click-away layer — dismissal from the DS root** · ledger row: `click-away layer` (`DS as-is`) · decision: `Combobox` as-is

   Render no click-away layer. An outside pointer-down closes the panel, Escape closes it, focus moves into the panel on open and returns to the trigger on close.

4. **Search band — input text and height** · ledger row: `search band` (`DS with overrides`) · decision: override on the input only; accept the DS wrapper padding and loupe size

   Use `ComboboxCommandInput` with placeholder "Search shelves…" (single ellipsis character) and the override named in the row's Decision cell. Add no second magnifier. The 16px-vs-12px horizontal padding and the 14px-vs-16px loupe are accepted deltas; file no DS change.

5. **Option list band — padding, row gap, filtering** · ledger row: `option list band` (`DS with overrides`) · decision: the overrides named in the row's Decision cell, `max-h-[300px]` kept

   The band owns 4px padding all round and 2px between rows (see the row's Decision cell for the sizer override). Turn off cmdk filtering on `ComboboxCommand` and filter in `ShelfPickerPopover` per bl3: case-insensitive substring match against the shelf name only, on the trimmed query. The shelf note is never searched.

6. **Shelf row — anatomy, states, press** · ledger row: `shelf row` (`DS with overrides`) · decision: the overrides named in the row's Decision cell; close after the toggle resolves, tick or untick

   `ShelfRow` renders `ComboboxCommandItem` with the tally column held in every state (`TallyMarkIcon`, invisible when not kept, never removed) and the shelf name. The whole row owns the press. On press, `ShelfRow` sets its `moving` state (`disabled`), awaits `toggleOnShelf`, clears `moving`, posts the `kept` / `removed` notice unchanged, and then asks `ShelfPickerPopover` to close. It closes for an untick as well as a tick. Keep the visually hidden "on this shelf" text for ticked rows. A tooltip names the shelf's owner after a 400ms hover.

7. **Empty result — glyph stack** · ledger row: `empty result` (`DS with overrides`) · decision: the overrides named in the row's Decision cell

   `ComboboxCommandEmpty` renders `DustCoverIcon` above the line "No shelves found.", centred, only when zero shelves match.

8. **New shelf row — local, outside the list** · ledger row: `New shelf row` (`local component`) · decision: build local `NewShelfRow`, a sibling after `ComboboxCommandList`

   Build the private `NewShelfRow` in `shelf-picker-popover.tsx` as the row's Decision cell names it, with `NewNicheIcon` and "New shelf". It is the last band of the panel in every list state, including `no-matches`, and it owns the top hairline. The whole row owns the press, which switches the popover to `naming`. It has no hover fill, and it keeps the browser's default focus-visible outline. The New shelf row shows a keyboard hint reading ⌘N against its right edge.

9. **Naming — form in place of the list** · ledger row: `panel content — naming` (`DS with overrides`) · decision: keep the naming switch; render `NewShelfInlinePanel` unchanged

   In `naming`, `ShelfPickerPopover` renders the existing `NewShelfInlinePanel` in place of `ComboboxCommand`; the search band, the option list band and the New shelf row are not rendered. Closing the popover leaves `naming`. Do not change `NewShelfInlinePanel`.

10. **Tests** · engineering, no ledger row · decision: move the 7 existing tests and cover the new behaviour

    Move the tests in `save-to-shelf-combobox.test.tsx` to test files for the new components. Add tests for: a query that fuzzy-matches but does not substring-match (for example "bn") shows no shelf; a query that matches nothing shows "No shelves found." **and** the New shelf row; ticking a shelf closes the picker; unticking a shelf closes the picker; a query is matched on the name and never on the note.

## Decisions confirmed

- **Where the work lands:** split `SaveToShelfCombobox` into `src/shelf-keeper/shelf-picker-popover.tsx` and `src/shelf-keeper/shelf-row.tsx`, delete the old file, swap the import in `KeepSpecimenButton`. Reason: it matches the ticket's component names, keeps the repo's kebab-case colocation in `shelf-keeper/`, and replaces the old component rather than leaving two.
- **Every row press closes the picker, tick or untick.** Reason: one rule is easier to learn, and a picker that closes on only one of its two actions looks broken.
- **The picker closes after `toggleOnShelf` resolves, and `moving` (`disabled`) stays.** Reason: "ticked" means the tick applied, the guard blocks a second press, and a slower store later needs no change.
- **Picker panel:** `ComboboxContent` with `className="w-[250px]"` and `align="end"`; `sideOffset` 4 kept because the handoff README wins on layout; `shadow-md` kept and no lift token filed. Reason: a token for one panel does not justify a blocker, and the design's written shadow does not match what the prototype renders (`shadow-lg`).
- **Search band:** overrides on the input only (`className="h-auto py-2 type-body"`); 16px padding and the 14px loupe accepted as known deltas; no DS blocker on this ticket.
- **Option list band:** overrides as named; `max-h-[300px]` kept. Reason: the design states no height, and a long list must scroll rather than run off the screen.
- **Filtering:** `shouldFilter={false}` plus an app-side substring filter. Reason: cmdk's default fuzzy score breaks bl3, and `CommandProps` does not type cmdk's `filter`.
- **Shelf row:** overrides as named; tally at `Icon size="md" tone="accent"`; the cmdk open-time first-row highlight kept and listed as a known delta. Reason: keyboard users need a start point, and it is the DS hover colour.
- **Empty result:** overrides as named.
- **New shelf row:** build local `NewShelfRow`, no DS `Button`, no DS blocker. Reason: a `ComboboxCommandItem` either suppresses `ComboboxCommandEmpty` or is filtered away on no match, and its hairline cannot span the panel; even `ghost` `Button` carries a pill radius and `font-medium`. Losing arrow-key reach is accepted: it is an action, reached by Tab.
- **New shelf row hover and focus:** no hover fill; keep the browser's default focus-visible outline. Reason: the design draws no hover state, and removing the only focus indicator on a Tab stop is an accessibility defect.
- **Naming:** keep the naming switch in the popover and render `NewShelfInlinePanel` unchanged. Reason: leaving it to the other ticket removes a working flow between the two tickets.
- **Anchor, hairline, naming swap mappings:** `ComboboxTrigger asChild` through a `trigger` prop; the New shelf hairline is the row's own top border, not `ComboboxCommandSeparator`; the naming swap is `ComboboxContent` rendering the form in place of `ComboboxCommand`.
- **Notices:** `ShelfRow` keeps posting `kept` / `removed` notices, unchanged. Reason: dropping them regresses the notice rail, which works today.
- **Dismissal, keyboard and focus:** the DS behaviour (Escape, focus in, focus return, arrow keys) is kept. Reason: `HANDOFF.md` calls the prototype's missing keyboard handling "the prototype's gap, not the design's".
- **Data & Access Manifest:** all rows ✅. The store is in-memory React context with no policy layer; `shelves` read, holdings read (`shelvesHolding`), holdings update (`toggleOnShelf`, always resolves), `notices` create (`postNotice`, sync), shelves create (`addShelf`, through the unchanged naming panel).

## Out of scope

- **uc1-s1 and the bell-jar button (`KeepSpecimenButton`, all 3 states)** — another ticket. Only the one-line import swap in change 1 touches it.
- **uc1-s6, uc1-s7 and the naming form's internals (`NewShelfInlinePanel`, `blank`, `name-missing`)** — the naming-form ticket. This issue only renders it in `naming`.
- **uc2-s1, uc2-s2 and the notice rail (`NoticeRail`, `kept`, `removed`, `alarm`)** — another ticket. This issue keeps posting the same notices.
- **bl4 (create-and-keep in one action), bl5 (blank name blocks submit)** — observed only in the naming form.
- **bl6 (every move posts one notice)** — the notice-rail ticket; the existing posting is kept unchanged.
- **Responsiveness note 2 (the cabinet list is a single column)** — seen only in uc1-s1.
- **DS gaps proposed by the brief, none filed:** the `ComboboxCommandInput` wrapper class and icon size (deltas accepted instead), the panel lift token (`shadow-md` kept), the pinned footer action (the New shelf row is built local).
- **An error path for `toggleOnShelf`** — the store has none today; adding one is outside this ticket.

## Verify

**L2 — floor, non-negotiable** (from the adapter's `## Verify ladder`), both from `apps/consumer`:

```
pnpm test
pnpm ts-lint
```

**Screenshot pairs** — boot the app (`pnpm dev`, then open `http://localhost:5173`), capture each state, and pair it against the prototype PNG embedded above. A row passes on the **pair**, never on a text claim that it matches.

- [ ] **1** pair uc1-s2 · uc1-s3 · uc1-s4 · uc1-s5 · shelf-picker-popover/naming vs app — picker panel · `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches`, `naming` · uc1-s2, uc1-s3, uc1-s4, uc1-s5: fixed **250px** wide at every viewport, never hugs content; anchored to the **right** edge of the bell-jar button, 4px below it; the panel owns **no** padding — the search band, the option list band and the New shelf row each own their own; vertical stack of those three bands, each full panel width inert itself; dismissal belongs to the click-away row
- [ ] **2** pair uc1-s2 · uc1-s3 · uc1-s4 · uc1-s5 vs app — search band · `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` · uc1-s2 → uc1-s5: **same element; content differs**: `open-empty-pick` / `open-one-kept` show the placeholder, `filtered` shows "bra", `no-matches` shows "vitrine". One row: magnifier then field, 8px between; band padding **12px** left and right, **8px** top and bottom; one 1px hairline along the band's bottom, **owned by the band**, spanning the full panel width; the field has no border and no background and takes the rest of the row. Icon: `LoupeGlassIcon` **16px** `--color-ink-muted`, first in the row typing narrows the list per bl3; the field owns focus when the panel opens (DS behaviour)
- [ ] **3** pair uc1-s2 · uc1-s3 · uc1-s4 vs app — option list band · `open-empty-pick`, `open-one-kept`, `filtered` · uc1-s2, uc1-s3, uc1-s4: **4px** padding all round, **2px** between rows; the band owns that padding, a row does not; rows are direct children in one vertical stack inert; keyboard arrow navigation through the rows comes with `cmdk` (the prototype has none; the design does not forbid it)
- [ ] **4** pair uc1-s2 · uc1-s3 · uc1-s4 · shelf-row/plain · shelf-row/kept · shelf-row/moving vs app — shelf row · `plain`, `kept`, `moving` (ShelfRow) · `open-empty-pick`, `open-one-kept`, `filtered` · uc1-s2, uc1-s3, uc1-s4: **same element; content differs**: `plain` draws the tally mark at **zero opacity**, `kept` draws it in accent, `moving` dims the whole row to 50% opacity. Anatomy: 100% wide; **tally column and shelf name in one flow**, 8px between; the tally column is a **fixed 16px** in every state, so no name shifts sideways; the name takes the rest. Row padding **8px** left and right, **6px** top and bottom; corner 8px. Icon: `TallyMarkIcon` **16px** `--color-accent` in `Icon size="md" tone="accent"`; unticked it stays in the layout with `opacity-0` — never removed **the whole row owns the press** (`onSelect` on the item, which also takes Enter); nothing inside it is separately pressable. Press toggles the piece on that shelf, applies at once, and **closes the picker** (ticket override; untick and `moving` timing are OPEN — see Overrides). Hover fills the row `--color-shade`; **no focus ring**. `moving`: inert, no press, 50% opacity
- [ ] **5** pair uc1-s5 vs app — empty result · `no-matches` · uc1-s5: **rendered only when zero shelves match**, in place of the rows, inside the option list band. Vertical stack, centred: glyph, **4px**, then one centred line; 24px top and bottom. Icon: `DustCoverIcon` **20px** `--color-ink-muted` in `Icon size="lg" tone="muted"` inert
- [ ] **6** pair uc1-s2 · uc1-s3 · uc1-s4 · uc1-s5 vs app — New shelf row · `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` · uc1-s2 → uc1-s5: the **last** band of the panel in every list state, below the option list band and the empty result alike; full panel width; padding **12px** left and right, **8px** top and bottom; one 1px hairline along its **top, owned by the row**, spanning the full panel width. Glyph and label in **one flow**, 8px between, left-aligned. No pill, no fill, no button chrome. Icon: `NewNicheIcon` **16px** `--color-accent` in `Icon size="md" tone="accent"` **the whole row owns the press**; in the prototype it switches the panel to `naming`. Whether this ticket wires that press, given the naming form is another ticket, is a grill question. Hover and focus treatment: none in the source or the handoff
- [ ] **7** pair shelf-picker-popover/naming vs app — panel content — naming · `naming`: **the search band, the option list band and the New shelf row are not rendered in this state**; the naming form fills the same panel at the same 250px width; no second layer opens the form's own actions leave this state; out of scope here

