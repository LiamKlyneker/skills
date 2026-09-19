# Design brief — capture/ticket.md ("Shelf picker: the popover and its rows, on the design system") · Keep on a shelf
Source: `../../prototype` → `/Users/klyneker/liam-klyneker/skills-fixture/prototype`@8cb5bd20ea06098883257152582ec21b92746500 (working tree clean under `prototype/` at that commit) · Preview: — (local prototype source) · Catalog: `@vitrine/ds` 0.1.0 (`./ds-catalog/`, generated + overlay; installed fingerprint 0.1.0, matches) · Generated: 2026-09-19

Ticket read from the local file `capture/ticket.md`; no tracker was called. Paths below are relative to the repository root (`prototype/…`).

**Default chrome source.** The catalog overlay carries no "Default chrome" note for any component. Every default-chrome comparison below reads the shipped class lists in `packages/ds/src/{popover,combobox,command,icon}.tsx` at 0.1.0 (and `cmdk` 1.1.1 behaviour) against the step screenshots. The grill should treat those comparisons as evidence, not as overlay facts.

## Scope

Ticket names `Component: ShelfPickerPopover`, `Component: ShelfRow` and files `components/shelf-picker-popover.tsx`, `components/shelf-row.tsx`. Scope is by name, not inferred.

Kept steps: uc1-s2, uc1-s3, uc1-s4, uc1-s5
Kept component states: `ShelfPickerPopover` → `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches`, `naming` · `ShelfRow` → `plain`, `kept`, `moving`
Kept rules: bl1, bl2 (overridden — see below), bl3 · responsiveness note 1 (250px panel)
Dropped: uc1-s1 (cabinet frame, `components/cabinet-frame.tsx` — the bell-jar button is another ticket) · uc1-s6, uc1-s7 (naming form, `components/new-shelf-panel.tsx` — another ticket) · uc2-s1, uc2-s2 (notice rail, `components/notice-rail.tsx` — another ticket)

The `naming` state is kept because it is a `ShelfPickerPopover` state. Only the popover's side of it is in scope: what the panel stops rendering and what it keeps. The form inside it is not.

## Overrides (ticket wins)

- ~~bl2: "Ticking a shelf applies at once and the panel stays open; there is no confirm step."~~ → overridden by ticket: "The picker **closes** as soon as a shelf is ticked. The prototype keeps it open and applies the tick in place; this ticket does not."
- ~~`HANDOFF.md` flow step 4: "Pressing a row toggles the piece on that shelf at once. The panel stays open, and the row dims and stops taking presses while the toggle is in flight."~~ → overridden by ticket: the picker closes as soon as a shelf is ticked.

Two consequences the ticket does not settle — both are **OPEN** for the grill:

- **Unticking.** Pressing a ticked row removes the piece from that shelf. The ticket says the picker closes when a shelf is *ticked*. Does an untick also close it?
- **The `moving` state.** The prototype dims the row while the toggle is in flight. If the panel closes "as soon as" the row is pressed, the `moving` state is never on screen. Does the panel close on press (and `moving` is dropped), or after the toggle resolves (and `moving` stays visible for that interval)?

## Screens

### uc1-s2 — Shelf picker open, nothing ticked yet
Screenshot: `prototype/spec/screenshots/uc1-s2.png`
Annotations:
- "The panel hangs off the right edge of the bell-jar button. A full-screen layer behind it takes the click that dismisses it." `component:shelf-picker-popover`
- "The search field keeps the magnifier on the left and a hairline under the whole row." `component:shelf-picker-popover`

### uc1-s3 — A shelf ticked
Screenshot: `prototype/spec/screenshots/uc1-s3.png`
Annotations:
- "The tally mark keeps its column when the row is not ticked — the label never shifts." `component:shelf-row`

### uc1-s4 — The list filtered as the curator types
Screenshot: `prototype/spec/screenshots/uc1-s4.png`
Annotations:
- "Filtering is plain substring matching, case-insensitive, against the shelf name." `component:shelf-picker-popover`

### uc1-s5 — Nothing matches what was typed
Screenshot: `prototype/spec/screenshots/uc1-s5.png`
Annotations:
- "The dust cover sits above the empty line, centred, and the New shelf row stays. The line reads "No shelves found."" `component:shelf-picker-popover`

## Component states

### ShelfPickerPopover
Source: `prototype/components/shelf-picker-popover.tsx`
- `open-empty-pick` — Open, every shelf listed, none ticked. Page: `prototype/spec/component-states/shelf-picker-popover/open-empty-pick/page.tsx` (`keptShelfIds={[]}`) · Preview: `…/open-empty-pick/preview.png`
- `open-one-kept` — Open, one shelf ticked. Page: `…/open-one-kept/page.tsx` (`keptShelfIds={['shelf-brass-niche']}`) · Preview: `…/open-one-kept/preview.png`
- `filtered` — A query narrowing the list to one shelf. Page: `…/filtered/page.tsx` (`query="bra"`, Brass niche kept) · Preview: `…/filtered/preview.png`
- `no-matches` — A query matching nothing; the dust cover and the empty line. Page: `…/no-matches/page.tsx` (`query="vitrine"`) · Preview: `…/no-matches/preview.png`
- `naming` — The naming form in place of the list. Page: `…/naming/page.tsx` (`mode="naming"`) · Preview: `…/naming/preview.png`

### ShelfRow
Source: `prototype/components/shelf-row.tsx`
- `plain` — Not on this shelf; the tally column holds its width. Page: `prototype/spec/component-states/shelf-row/plain/page.tsx` (`kept={false}`) · Preview: `…/plain/preview.png`
- `kept` — On this shelf; the tally mark in accent. Page: `…/kept/page.tsx` (`kept`) · Preview: `…/kept/preview.png`
- `moving` — The toggle is in flight; the row is dimmed and inert. Page: `…/moving/page.tsx` (`kept={false} moving`) · Preview: `…/moving/preview.png` — no step screenshot shows it; the state preview is its only image.

## Business rules & edge cases

- bl1 — A piece can sit on more than one shelf at once. Ticking a second shelf never unticks the first. *(observed in uc1-s3)*
- bl2 — ~~Ticking a shelf applies at once and the panel stays open; there is no confirm step.~~ → overridden by ticket: the picker closes as soon as a shelf is ticked. "Applies at once, no confirm step" still stands. *(observed in uc1-s3)*
- bl3 — The filter is case-insensitive substring matching against the shelf name only; the note is never searched. *(observed in uc1-s4, uc1-s5)* The prototype trims the query before it matches (`query.trim().toLowerCase()`, `shelf-picker-popover.tsx:L39–L41`).
- **Edge case — `cmdk` does not filter by substring.** `ComboboxCommand` filters by default with `cmdk`'s fuzzy score, so "bn" would match "Brass niche". bl3 and the ticket's AC need `shouldFilter={false}` on `ComboboxCommand` (the overlay's idiom row names this prop) and the substring filter in the app. `CommandProps` does not expose `cmdk`'s `filter` prop, so a custom filter function is not a typed option.
- **Edge case — the panel's keyboard and focus.** `HANDOFF.md`, "What the panel does not do": the prototype closes on an outside pointer only — no Escape, no focus move in, no focus return, no arrow keys — and "that gap is the prototype's, not the design's". The DS popover and `cmdk` ship all four. Do not reproduce the prototype's gap.
- Responsiveness — "The panel is a fixed 250px wide at every width and stays anchored to the right edge of the button." *(seen in uc1-s2)*

## Element → DS mapping

| Element | Seen in | Proposed | Confidence | Notes |
|---|---|---|---|---|
| picker panel | uc1-s2 → uc1-s5, all 5 popover states | `Combobox` + `ComboboxContent` | likely | idiom row "A panel drawn floating beside a control, with a click-away layer behind it". A composite with chrome, so not `exact` — see the ledger |
| click-away layer | uc1-s2 | `Combobox` root dismissal (Radix `Popover`) | exact | do not port the `fixed inset-0` div (`shelf-picker-popover.tsx:L45`) |
| anchor to the bell-jar button | uc1-s2 | `ComboboxTrigger` with `asChild` around the bell-jar button | likely | the button itself is another ticket; this ticket owns only the trigger wrapper and `align="end"` |
| search band | uc1-s2 → uc1-s5 | `ComboboxCommandInput` | likely | idiom row "A search affordance on a text field → already inside `CommandInput`". Chrome differs — see the ledger |
| magnifier | uc1-s2 → uc1-s5 | `LoupeGlassIcon`, drawn by `ComboboxCommandInput` itself | exact | adding a second one doubles it (overlay idiom row) |
| option list band | uc1-s2 → uc1-s4 | `ComboboxCommand` (`shouldFilter={false}`) + `ComboboxCommandList` | likely | idiom row "A filterable list of options under a search box" |
| shelf row | uc1-s2 → uc1-s4, `plain` / `kept` / `moving` | `ComboboxCommandItem` | likely | one item per shelf |
| tally mark | uc1-s3, uc1-s4, `kept` | `TallyMarkIcon` in `Icon` | exact | idiom row "A tick marking a chosen row". Prototype name `TallyGlyph` — not the name to build against |
| empty result | uc1-s5, `no-matches` | `ComboboxCommandEmpty` | likely | renders only when `cmdk` counts zero items — see the New shelf row |
| dust cover | uc1-s5 | `DustCoverIcon` in `Icon` | exact | prototype name `CoverGlyph` |
| New shelf row | uc1-s2 → uc1-s5 | — | OPEN | two candidates, each breaks something: a `ComboboxCommandItem` "pinned last" (the per-element handoff) keeps `cmdk`'s item count ≥ 1, so `ComboboxCommandEmpty` never renders in `no-matches`; a sibling after `ComboboxCommandList` renders the empty result but leaves the arrow-key flow, and `Button` ships chrome the design does not draw |
| New shelf plus glyph | uc1-s2 → uc1-s5 | `NewNicheIcon` in `Icon` | exact | prototype name `PlusGlyph`; not `PlusIcon`, which does not exist |
| New shelf hairline | uc1-s2 → uc1-s5 | the New shelf row's own top border | likely | `ComboboxCommandSeparator` (`-mx-1 h-px`) sits inside the list's padding and would not span the panel |
| naming swap | `naming` | `ComboboxContent` with the form rendered in place of the command list | likely | idiom row "A modal dialog, a sheet, or a drawer holding a short form". The form is another ticket |

## Fidelity ledger

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class |
|---|---|---|---|---|---|---|---|---|
| picker panel | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches`, `naming` · uc1-s2, uc1-s3, uc1-s4, uc1-s5 | — | `--color-surface` (bg), `--color-edge` (1px border), `--radius-panel` (16px corner) · raw: `0 8px 24px rgba(0,0,0,0.18)` drop shadow — **⚠ no equivalent, do not invent** | fixed **250px** wide at every viewport, never hugs content; anchored to the **right** edge of the bell-jar button, 4px below it; the panel owns **no** padding — the search band, the option list band and the New shelf row each own their own; vertical stack of those three bands, each full panel width | inert itself; dismissal belongs to the click-away row | `components/shelf-picker-popover.tsx:L43–L46` · `design_handoff_shelf_picker/README.md` "The panel" | `ComboboxContent` | DS with overrides — **grill question** · `PopoverContent` deltas under `ComboboxContent`: width `w-72` (288px) → `w-[250px]`; `align` defaults `start` → pass `align="end"`; `sideOffset` 4 = design, keep; padding already `p-0` from `ComboboxContent`, keep; radius, border, bg and ink match, keep; shadow `shadow-md` ≠ the design's lift, and the design's value is raw — the grill decides between `shadow-md` as-is and a new token (see DS gaps); no arrow is rendered, nothing to remove; `overflow-hidden` is on by default |
| click-away layer | all 5 popover states · uc1-s2 | — | — | not a visual element in the DS build: no `fixed inset-0` layer is rendered | an outside pointer-down closes the panel; Escape closes it; focus moves into the panel on open and returns to the trigger on close — the DS behaviour, which the prototype lacks and `HANDOFF.md` calls the prototype's gap | `components/shelf-picker-popover.tsx:L23–L24, L45` · `HANDOFF.md` "What the panel does not do" | `Combobox` (Radix `Popover` root) | DS as-is |
| search band | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` · uc1-s2 → uc1-s5 | placeholder "Search shelves…" (single ellipsis character) · accessible name "Search shelves" | hairline `--color-edge`; magnifier `--color-ink-muted`; field text `type-body` in `--color-ink`; placeholder `type-body` in `--color-ink-muted` | **same element; content differs**: `open-empty-pick` / `open-one-kept` show the placeholder, `filtered` shows "bra", `no-matches` shows "vitrine". One row: magnifier then field, 8px between; band padding **12px** left and right, **8px** top and bottom; one 1px hairline along the band's bottom, **owned by the band**, spanning the full panel width; the field has no border and no background and takes the rest of the row. Icon: `LoupeGlassIcon` **16px** `--color-ink-muted`, first in the row | typing narrows the list per bl3; the field owns focus when the panel opens (DS behaviour) | `components/shelf-picker-popover.tsx:L51–L62` · `design_handoff_shelf_picker/README.md` "The search band" | `ComboboxCommandInput` | DS change — **grill question** · shipped wrapper is `flex items-center gap-2 border-b border-[--color-edge] px-4` with the loupe in `Icon size="sm"` (**14px**); its `className` reaches only the inner `input`. So: horizontal padding 16px ≠ 12px, no path; loupe 14px ≠ 16px, no path; the input is `h-10 py-3 text-sm` (40px row, 14px text) ≠ 8px + 22px `type-body` — fixable through `className` (`h-auto py-2 type-body`). Gap 8px, hairline and muted loupe match |
| option list band | `open-empty-pick`, `open-one-kept`, `filtered` · uc1-s2, uc1-s3, uc1-s4 | — | — | **4px** padding all round, **2px** between rows; the band owns that padding, a row does not; rows are direct children in one vertical stack | inert; keyboard arrow navigation through the rows comes with `cmdk` (the prototype has none; the design does not forbid it) | `components/shelf-picker-popover.tsx:L63, L70–L78` · `design_handoff_shelf_picker/README.md` "The option list" | `ComboboxCommand` (`shouldFilter={false}`) + `ComboboxCommandList` | DS with overrides — **grill question** · `CommandList` deltas: padding `p-1.5` (6px) → `p-1` (4px); `cmdk` wraps items in a `[cmdk-list-sizer]` div, so a `gap` on the list does not reach the rows — set the 2px on the sizer (`[&_[cmdk-list-sizer]]:flex [&_[cmdk-list-sizer]]:flex-col [&_[cmdk-list-sizer]]:gap-0.5`) or on each item; `max-h-[300px] overflow-y-auto` is on by default and the design states no max-height — keep or drop is a grill call; `ComboboxCommand` adds its own `rounded-[--radius-panel] bg-[--color-surface]`, which matches the panel |
| shelf row | `plain`, `kept`, `moving` (ShelfRow) · `open-empty-pick`, `open-one-kept`, `filtered` · uc1-s2, uc1-s3, uc1-s4 | the shelf's name, from the shelf store — in the captures "Upper bay", "Brass niche", "Under glass", "Cold drawer" | name `type-body` in `--color-ink`; tally mark `--color-accent`; hover fill `--color-shade`; corner `--radius-tile` | **same element; content differs**: `plain` draws the tally mark at **zero opacity**, `kept` draws it in accent, `moving` dims the whole row to 50% opacity. Anatomy: 100% wide; **tally column and shelf name in one flow**, 8px between; the tally column is a **fixed 16px** in every state, so no name shifts sideways; the name takes the rest. Row padding **8px** left and right, **6px** top and bottom; corner 8px. Icon: `TallyMarkIcon` **16px** `--color-accent` in `Icon size="md" tone="accent"`; unticked it stays in the layout with `opacity-0` — never removed | **the whole row owns the press** (`onSelect` on the item, which also takes Enter); nothing inside it is separately pressable. Press toggles the piece on that shelf, applies at once, and **closes the picker** (ticket override; untick and `moving` timing are OPEN — see Overrides). Hover fills the row `--color-shade`; **no focus ring**. `moving`: inert, no press, 50% opacity | `components/shelf-row.tsx:L10–L27` · `components/shelf-picker-popover.tsx:L70–L78` · `spec/component-states/shelf-row/{plain,kept,moving}/page.tsx` · `design_handoff_shelf_picker/README.md` "The option list" | `ComboboxCommandItem` | DS with overrides — **grill question** · `CommandItem` deltas: corner `rounded-[--radius-pill]` → `rounded-[--radius-tile]`; padding `px-3` → `px-2` (py-1.5 matches); text `text-sm` → `type-body`; gap-2 matches; highlight is `data-[selected=true]:bg-[--color-shade]`, which `cmdk` sets on pointer hover **and** on keyboard focus, and `cmdk` **selects the first item on open** — so the first row renders shaded on open, and none of uc1-s2 → uc1-s4 shows that; the grill decides whether to suppress the open-time highlight; `disabled` gives `pointer-events-none opacity-50`, which **matches** `moving` exactly — pass `disabled` for `moving`, and `outline-none` already gives no focus ring |
| option rows — absent | `no-matches` · uc1-s5 | — | — | **not rendered in this state**: zero rows; the option list band shows the empty result instead and keeps its 4px padding | — | `components/shelf-picker-popover.tsx:L64` | `ComboboxCommandList` | DS as-is |
| empty result | `no-matches` · uc1-s5 | "No shelves found." — `spec-data.ts` and the source win; `design_handoff_shelf_picker/README.md` and `HANDOFF.md` read "No shelves.", which is stale | glyph `--color-ink-muted`; line `type-body` in `--color-ink-muted` | **rendered only when zero shelves match**, in place of the rows, inside the option list band. Vertical stack, centred: glyph, **4px**, then one centred line; 24px top and bottom. Icon: `DustCoverIcon` **20px** `--color-ink-muted` in `Icon size="lg" tone="muted"` | inert | `components/shelf-picker-popover.tsx:L64–L68` · `design_handoff_shelf_picker/README.md` "The empty result" | `ComboboxCommandEmpty` | DS with overrides — **grill question** · `CommandEmpty` deltas: `text-sm` → `type-body`; add `flex flex-col items-center gap-1` for the glyph stack; `py-6 text-center text-[--color-ink-muted]` match. It renders only when `cmdk` counts zero items — **it never renders if the New shelf row is a `ComboboxCommandItem`** (see that row) |
| New shelf row | `open-empty-pick`, `open-one-kept`, `filtered`, `no-matches` · uc1-s2 → uc1-s5 | "New shelf" | hairline `--color-edge`; glyph and label `--color-accent`; label `type-body` | the **last** band of the panel in every list state, below the option list band and the empty result alike; full panel width; padding **12px** left and right, **8px** top and bottom; one 1px hairline along its **top, owned by the row**, spanning the full panel width. Glyph and label in **one flow**, 8px between, left-aligned. No pill, no fill, no button chrome. Icon: `NewNicheIcon` **16px** `--color-accent` in `Icon size="md" tone="accent"` | **the whole row owns the press**; in the prototype it switches the panel to `naming`. Whether this ticket wires that press, given the naming form is another ticket, is a grill question. Hover and focus treatment: none in the source or the handoff | `components/shelf-picker-popover.tsx:L81–L88` · `design_handoff_shelf_picker/README.md` "The New shelf row" | — (`ComboboxCommandItem` or a sibling of `ComboboxCommandList`) | OPEN — **grill question** · as a `ComboboxCommandItem` pinned last: breaks the empty result (see above) and sits inside the list's padding, so the hairline would not span the panel; it would also be filtered unless the item is excluded. As a sibling after the list: renders the empty result and spans the panel, but leaves `cmdk`'s arrow-key flow, and `Button` (`variant`/`size` chrome) is not what the design draws |
| panel content — naming | `naming` | — (form copy belongs to the naming-form ticket) | — | **the search band, the option list band and the New shelf row are not rendered in this state**; the naming form fills the same panel at the same 250px width; no second layer opens | the form's own actions leave this state; out of scope here | `components/shelf-picker-popover.tsx:L47–L48` · `spec/component-states/shelf-picker-popover/naming/page.tsx` (`mode="naming"`) · `spec-data.ts` uc1-s6 annotation | `ComboboxContent` with the form in place of `ComboboxCommand` | OPEN — **grill question** · whether this ticket builds the mode switch (and a placeholder for the form) or leaves the whole `naming` state to the naming-form ticket |

## Tokens

| Prototype token | Code token | Applies to | Status |
|---|---|---|---|
| `--color-surface` | `bg-[--color-surface]` | picker panel | ✅ resolves — `ComboboxContent` / `ComboboxCommand` already set it |
| `--color-shade` | `bg-[--color-shade]` | shelf row (hover) | ✅ resolves — `CommandItem`'s selected state already sets it |
| `--color-edge` | `border-[--color-edge]` | picker panel (border), search band (bottom hairline), New shelf row (top hairline) | ✅ resolves |
| `--color-ink` | `text-[--color-ink]` | shelf row (name), search band (typed text) | ✅ resolves — inherited from `PopoverContent` |
| `--color-ink-muted` | `text-[--color-ink-muted]` | search band (magnifier, placeholder), empty result (glyph, line) | ✅ resolves |
| `--color-accent` | `text-[--color-accent]` / `Icon tone="accent"` | shelf row (tally mark), New shelf row (glyph, label) | ✅ resolves |
| `--radius-panel` | `rounded-[--radius-panel]` | picker panel | ✅ resolves |
| `--radius-tile` | `rounded-[--radius-tile]` | shelf row | ✅ resolves |
| `rgba(0,0,0,0.18)` drop shadow, `0 8px 24px` | — | picker panel | ⚠ no equivalent, do not invent |
| 4px | `--space-snug` | picker panel (offset, via `sideOffset={4}`), option list band (padding), empty result (glyph-to-line gap) | ✅ resolves |
| 8px | `--space-step` | search band (vertical padding, glyph gap), shelf row (horizontal padding, tally gap), New shelf row (vertical padding, glyph gap) | ✅ resolves |
| 1px | `--space-hairline` | search band (hairline), New shelf row (hairline), picker panel (border) | ✅ resolves |
| 12px | — | search band (horizontal padding), New shelf row (horizontal padding) | ⚠ no `--space-*` step; the overlay routes component-internal spacing to `--space-*`, so `px-3` is a grill call |
| 6px | — | shelf row (vertical padding) | ⚠ no `--space-*` step; `CommandItem` ships `py-1.5`, which already matches |
| 2px | — | option list band (row gap) | ⚠ no `--space-*` step; `gap-0.5` is a grill call |
| `type-body` | `type-body` | shelf row (name), search band (field, placeholder), empty result (line), New shelf row (label) | ✅ resolves |

## DS gaps (proposed, not filed)

- **`ComboboxCommandInput` wrapper and icon size** — the search band's 12px horizontal padding and 16px loupe cannot be reached: `className` lands on the inner `input` only, and the loupe is fixed at `Icon size="sm"` (14px). A proposed change: a wrapper `className` (or slot) and an icon size on `CommandInput`. Would file against `LiamKlyneker/skills-fixture` (the adapter's DS-gap backlog; `@vitrine/ds` is `packages/ds`). **Not filed.**
- **Panel lift token** — the picker panel's `0 8px 24px rgba(0,0,0,0.18)` has no token; `PopoverContent` ships `shadow-md`. Proposed only if the grill rejects `shadow-md`. Would file against `LiamKlyneker/skills-fixture`. **Not filed.**
- **A pinned footer action in the command list** — the New shelf row (OPEN) has no DS shape that keeps it last, spans the panel, and leaves `ComboboxCommandEmpty` working. Proposed only if the grill resolves the row to neither candidate. Would file against `LiamKlyneker/skills-fixture`. **Not filed.**

## Out of scope

- uc1-s1 (the cabinet, with one piece already kept) — `components/cabinet-frame.tsx`; the bell-jar button (`KeepButton`, all 3 states) is another ticket
- uc1-s6 (naming a new shelf), uc1-s7 (the name was left empty) — `components/new-shelf-panel.tsx`; `NewShelfPanel` (`blank`, `name-missing`) is another ticket
- uc2-s1 (a notice after keeping a piece), uc2-s2 (a notice after taking a piece off) — `components/notice-rail.tsx`; `NoticeRail` (`kept`, `removed`, `alarm`) is another ticket
- bl4 (create-and-keep in one action), bl5 (blank name blocks submit) — observed only in uc1-s6 / uc1-s7
- bl6 (every move posts one notice) — observed only in uc2-*
- Responsiveness note 2 (the cabinet list is a single column) — seen only in uc1-s1

## Rules to cite

None — the adapter's `## Design system` section registers no usage-rules source.
