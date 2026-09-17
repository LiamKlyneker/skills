# Design brief template

The shape `figma-to-brief` writes and `deep-grill` reads. **The `##` headings are fixed** — the
grill keys on them to tell a fact from a question — and everything inside them is the project's
and the design's vocabulary.

A brief is **disposable**. It describes one ticket against one Figma file at one version, it is
written to a git-excluded directory, and it is regenerated rather than updated. Nothing reads it
after the grill.

---

```markdown
# Design brief — <ado-id> · <design name>
Pinned at figma <fileKey> · node <nodeId> · version <versionId or YYYY-MM-DD> · brief .claude/briefs/<ado-id>.md
Catalog: <fingerprint> · Generated: <YYYY-MM-DD> · Figma calls: <n>

## Scope

Kept: `order-status-empty`, `order-status-populated`, `order-status-filter-open` …
Dropped: `order-status-export-dialog` (export flow — separate ticket), `order-detail-*` (not in AC) …

## Overrides (ticket wins)

- ~~Filter popover closes on the first selection~~ → overridden by ticket: stays open until the
  user clicks away.

## Screens

### `order-status-populated` — <frame title>
Screenshot: .claude/briefs/<ado-id>/screenshots/order-status-populated.png · node https://www.figma.com/design/<fileKey>/?node-id=<nodeId>
Annotations:
- <annotation text> `component:<tag>`

## Component states

### <ComponentName>
State node: https://www.figma.com/design/<fileKey>/?node-id=<nodeId>
- `<state>` — <description>

## Business rules & edge cases

- <rule> *(observed in `order-status-populated`)*

## Element → DS mapping

| Element | Seen in | Proposed | Confidence | Notes |
|---|---|---|---|---|
| filter chips w/ remove | `order-status-populated` | `MultiSelect` | likely | design draws bare pills |
| filter popover | `order-status-filter-open` | `Popover` (root) | exact | do not port the drawn rectangle |
| status legend | `order-status-populated` | — | OPEN | no catalog match |

## Fidelity ledger

One row per **element** — a distinct visual thing (container, row, divider, add row, value pill,
option list, popover, search input, footer action), not a component. One row set per **state** in
scope, not per screenshot. Same element in two states with different content = one row, never two.

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class |
|---|---|---|---|---|---|---|---|---|
| content container | `order-status-populated`, `order-status-filter-open` | — | `bg-surface-primary`, `border-border-primary`, `rounded-xl` · bound: `surface/primary`, `border/primary` | white panel wrapping the whole in-scope block; the panel owns `p-24`, radius 12px and a 1px border, and no shadow; it stretches to the content column width; the status card, the add row and the footer are its direct children in one vertical flow | inert | `<fileKey>:412:1176` | `Card` | DS with overrides — **grill question** (`Card` defaults to `variant: default`, which paints its own shadow; override through the class hook the adapter's emission-form row states) |
| content container | `order-status-empty` | — | `none — page background` — the container binds no fill, no border and no shadow | no panel in this state: the in-scope elements sit directly on the page background; the container owns no padding and no radius, and stretches to the content column width; the subtitle and the empty block are its direct children in one vertical flow | inert | `<fileKey>:412:1178` | — | local component — **grill question** |
| status card | `order-status-populated` | — | `bg-surface-secondary`, `border-border-primary`, `rounded-lg` · bound: `surface/secondary`, `border/primary` | vertical auto-layout, full-width; the card owns no padding — each row owns its own; rows are direct children, the add row is the last child | inert — the card carries no reaction | `<fileKey>:412:1180` | `Card` | DS with overrides — **grill question** (`Card` defaults to `variant: default`, which paints its own padding and shadow) |
| status card | `order-status-empty` — **hidden variant, no screenshot** | — | — | **not rendered in this state**: no border, no background, no radius — the empty state is a bare block | inert | `<fileKey>:412:1244` | — | local component — **grill question** |
| subtitle | `order-status-populated` / `order-status-empty` | "Alle Positionen dieser Bestellung." | `text-text-secondary`, type `text-body-sm` · raw: `#6B7280` — ⚠ no equivalent, do not invent | **rendered only when ≥1 row exists**; absent in the `order-status-empty` state | inert | `<fileKey>:412:1192` | — | local component — **grill question** |
| status row | `order-status-populated`, `order-status-filter-open` | label: "Status", value: "Versendet" | divider `border-border-primary`; label `text-text-default`, type `text-label`; value `text-text-secondary`, type `text-body-sm` | the row owns the divider as its own `border-bottom`, so it spans the full card width; padding on the row; **nesting**: the label is a fixed 124px sibling column that wraps; value, chips and caret sit in **one** wrapping inline flow; the remove × is the last sibling. Icons: `faXmark` 18px `fill-icon-secondary`; `faChevronDown` 18px `fill-icon-tertiary` | **the whole value area owns the reaction** — on click, opens `order-status-filter-open`; the chip × has its own reaction and removes one value. Hover and focus: `interaction not in the design — grill question` | `<fileKey>:412:1201` | — | local component — **grill question** |
| value area | `order-status-populated`, `order-status-filter-open` | "Alle" (no values) · the value strings (≥1 value) | chip bg `bg-surface-action-subtle`, chip text `text-text-action`, type `text-label-sm` · bound: `surface/action/subtle` | **same element; content differs**: `order-status-populated` renders one non-removable chip reading "Alle"; `order-status-filter-open` renders one removable chip per value. The caret is the **same** element in both — `faChevronDown` 18px `fill-icon-tertiary`, placed after the chip list, never inside a chip. The chip × is `faXmark` 14px at 55% opacity | the whole area is the trigger (see status row); the chip × removes one value | `<fileKey>:412:1207` | `Chip` | DS with overrides — **grill question** (`Chip` defaults to `variant: primary`, `size: md`; override height, padding and colour, and `selected` is a boolean, not a colour) |
| option list | `order-status-filter-open` | "Alle" (empty row) | check icon `fill-icon-action`; hover row `bg-surface-hover` | plain option rows, `faCheck` 18px `fill-icon-action` on the selected row only; no checkbox column, no "select all" row | the row is the click target; instant apply, the popover stays open; hover tints the row | `<fileKey>:412:1288` | `Popover` + `PopoverContent` | local component — **grill question** · base-primitive deltas on `PopoverContent`: no arrow; radius 12px over the default; padding 6px; width hugs content; add `max-height` + `overflow-y-auto` on the option list **only**, so the search field and the footer stay pinned |
| add row | `order-status-populated` | "+ Position hinzufügen" | `bg-surface-tertiary`; label `text-text-action`, type `text-label`, weight 600; icon `faPlus` 18px `fill-icon-action` | full-width row with its own padding and the tertiary background, below the last status row; the `+` glyph is inline with the label in one flow, not a separate column | **the whole row owns the reaction**, not the link inside it; no hover pill, no button chrome | `<fileKey>:412:1260` | `Button` | DS with overrides — **grill question** (`Button` defaults to `variant: primary`, `size: md`, a filled pill; the text variant is the only one with no fill — and it still ships its own height and hover) |

## Tokens

| Figma variable | Code token | Applies to | Status |
|---|---|---|---|
| `surface/secondary` | `bg-surface-secondary` (`<css-var-prefix>surface-secondary`) | status card | ✅ resolves |
| `#6B7280` (raw, unbound) | — | subtitle text colour | ⚠ no equivalent, do not invent |
| `--` | `fill-icon-error` | status row → remove × (hover only) | ✅ resolves |

## DS gaps (proposed, not filed)

- **status legend** — nothing in the catalog composes it. Would file against
  <the adapter's DS-gap backlog>. **Not filed.**

## Out of scope

- `order-status-export-dialog` (export flow) — separate ticket
- `order-detail-*` — not named in the AC

## Rules to cite

- `<rule name>` — from `<usage-rules source>`
```

---

## Rules the template does not show

- **Every heading is present, every time.** A section with nothing in it says
  `None — <why>`. An absent heading and an empty one are indistinguishable to the grill, and
  "the design had no business rules" and "nobody looked" are very different facts.
- **The pin line is required and carries a file key, a node id and a version**, never a bare
  Figma URL. A brief that cannot say which design state it describes cannot be checked against
  anything later. It is written in the contract's form, character for character, because every
  consumer copies it.
- **Screenshots are saved to disk and referenced by path plus node link**, never embedded and
  never linked to a `figma.com` image export — those URLs expire within the hour and are not
  public.
- **`## Scope` carries `⚠ inferred`** where the ticket named no component and the state frames
  were scored. The scored list — every frame, with its score, not only the kept ones — goes under
  the heading so the guess is checkable at a glance.
- **`## Overrides` keeps both halves** — the design's text struck through, the ticket's text
  after it. An override with the original deleted reads as the design.
- **Confidence is `exact`, `likely` or `OPEN`, and nothing else.** They are the grill's
  interface: `exact` is never asked about, `likely` gets one batched confirmation, `OPEN` is a
  round-one question. Promoting a guess to `exact` is the one error here that reaches
  implementation unchallenged.
- **`## Fidelity ledger` sits directly after `## Element → DS mapping`**, and carries one row per
  element. `Fidelity class` is `DS as-is`, `DS with overrides`, `local component`, `DS change` or
  `OPEN`, and nothing else. **A composite is never `DS as-is` without evidence** — the full
  classification rule set is in `SKILL.md`, Phase 4, *Classification rules*. Every row that is not
  `DS as-is` says **grill question** in its notes.
- **The ledger's nine columns are fixed, `Interaction` among them.** `Interaction` names the
  element that owns the prototype reaction — "the whole value area opens the filter", not
  "clickable" — plus the trigger and the destination state. `—` only where the element is
  genuinely inert; a node the design gives no reaction says
  `interaction not in the design — grill question` instead. A hotspot renders in no screenshot; if
  it is not in this column it does not reach the implementer.
- **Every icon in `Layout facts` carries a name, a size and a colour token; every text run carries
  a type token and a colour token.** A row missing either is incomplete, and both are read off the
  element node the `Source` column cites. Icon names are written in the adapter's ladder form —
  the name its primary source gives the glyph the design places — and never translated into a near
  neighbour.
- **One row set per in-scope state**, not one per screenshot. A state that lives as a
  `visible:false` node inside a kept frame renders in no screenshot and still gets its rows; its
  `States` cell reads `hidden variant, no screenshot`. Per-state **conditional rendering** —
  "subtitle only when ≥1 row", "card border only when ≥1 row" — is its own row under the state
  that toggles it, never a note on another row.
- **Same element, different content in two states = one row**, whose layout facts read
  `same element; content differs: …`. Two rows with two anatomies is what makes an implementer
  build two components for one design element.
- **Anatomy is written as nesting, not as a flat list of parts** — which parts share one wrapping
  flow, which are siblings. `label · value · chips · caret` is satisfied by four separate columns.
  **No absolute coordinate is ever written**: the node answers in x/y, the ledger answers in
  auto-layout intent, and a row derived from positions says `layout inferred from positions`.
- **A `local component` or `DS with overrides` row built on a base primitive enumerates that
  primitive's default-chrome deltas as explicit override instructions** — arrow, width behaviour,
  radius and padding for `PopoverContent`; variant colour, size, height and `selected` for `Chip`;
  variant, size, loading slot and hover for `Button` and `IconButton`; variant and thickness for
  `Separator`; `size` and overlay behaviour for `DialogContent`. The catalog's `## Components`
  entry — its variant axes and its `(def)` values — is the source where the catalog has no overlay
  and therefore no "Default chrome" note.
- **Only `Popover`, `Dialog` and `Tooltip` (the roots) and an icon from the adapter's icon ladder
  may be `exact` / `DS as-is` on name alone.** `Button`, `IconButton`, `Chip`, `Tag`, `Separator`,
  `PopoverContent` and `DialogContent` carry chrome and go through the same compare a composite
  does.
- **Tokens are written in the consumer form the adapter's *Consumer-facing emission form* row
  states**, with the CSS custom property named alongside where the row needs the raw value. Follow
  that row's spelling exactly — a design system that prefixes its own internal build and emits
  something else is the ordinary case, and the internal spelling is not writable in the app.
- **Every `## Tokens` row names the element or elements it applies to**, in the `Applies to`
  column, using the same element names the ledger uses. A token that attaches to no element is
  removed, not carried.
- **`## DS gaps (proposed, not filed)` may not read `None`** while any ledger row is
  `local component` or `DS change`. Each such row is a proposed gap. An icon that matches neither
  source of the adapter's ladder is **not** a gap — it is a design question for the designer.
- **`Source` cites the element node** — `<fileKey>:<nodeId>`, never a frame id and never a page
  root. A frame id in that cell is a broken row, because a frame read answers with the whole
  screen and buries the row's facts inside it.
- **A bound variable name beats a hex, and a hex is only written where no variable is bound.**
  Where the adapter's `### Figma source` *Servers* row registers no remote server, per-property
  bindings are unavailable, so a node binding several variables whose property assignment is not
  readable says `binding unverified: node binds <names>` rather than asserting one.
- **A rule is cited by name and by the source it came from.** The adapter's usage-rules row may
  name several sources, and two of them may name a rule the same thing. Cite, never restate.
- **Nothing in this brief is filed anywhere.** A proposed DS gap says where it *would* go and
  that it has not gone there.
