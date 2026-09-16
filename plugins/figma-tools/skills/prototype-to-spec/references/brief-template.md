# Design brief template

The shape `prototype-to-spec` writes and `deep-grill` reads. **The `##` headings are fixed** —
the grill keys on them to tell a fact from a question — and everything inside them is the
project's and the prototype's vocabulary.

A brief is **disposable**. It describes one ticket against one prototype at one SHA, it is
written to a gitignored directory, and it is regenerated rather than updated. Nothing reads it
after the grill.

---

```markdown
# Design brief — <ticket> · <prototype name>
Source: <owner/repo>@<sha> (<path>) · Preview: <url> · Catalog: <fingerprint> · Generated: <YYYY-MM-DD>

## Scope

Kept: uc1-s1, uc1-s2, uc1-s4 …
Dropped: uc1-s8 (edit drawer — separate ticket), uc2-* (questions step — not in AC) …

## Overrides (ticket wins)

- ~~Range picker closes on first click~~ → overridden by ticket: stays open until both
  endpoints are chosen.

## Screens

### uc1-s4 — <step title>
Screenshot: <raw URL at the pinned SHA>
Annotations:
- <annotation text> `component:<tag>`

## Component states

### <ComponentName>
State page: <url>
- `<state>` — <description>

## Business rules & edge cases

- <rule> *(observed in uc1-s4)*

## Element → DS mapping

| Element | Seen in | Proposed | Confidence | Notes |
|---|---|---|---|---|
| value chips w/ remove | uc1-s4 | MultiSelectPicker | likely | prototype hand-rolls pills |
| click-away overlay | uc1-s2 | Popover (built-in) | exact | do not port the fixed div |
| saved-view switcher | uc1-s6 | — | OPEN | no catalog match |

## Fidelity ledger

One row per **element** — a distinct visual thing (container, row, divider, add row, value pill,
value-editor list, editor popover, search input, footer action), not a component. One row set per
**state** in scope, not per screenshot. Same element in two states with different content = one
row, never two.

| Element | States | Exact copy | Tokens | Layout facts | Interaction | Source | DS candidate | Fidelity class |
|---|---|---|---|---|---|---|---|---|
| rules container | uc1-s1 (`Populated`) | — | `sui-bg-white`, `sui-border-neutral-border`, `sui-rounded-2xl` · raw: `var(--color-slate-200)` | vertical stack, full-width; container owns no padding — each row owns its own; rows are direct children, add row is the last child | inert — no handler on the container | `components/EligibilityRulesBuilder.tsx:L120–L148` | — | local component — **grill question** |
| rules container | `Empty` — **source-only, no screenshot** | — | — | **not rendered in this state**: no border, no background, no radius — the empty state is a bare block | inert | `spec/component-states/eligibility-rules-builder/empty/page.tsx` (`rules={[]}`) · `components/EligibilityRulesBuilder.tsx:L735–L763` | — | local component — **grill question** |
| subtitle | `Populated` / `Empty` — **source-only, no screenshot** for `Empty` | "Participants must match all of the settings below." | `sui-text-neutral-text-weak`, type `sui-text-body-dense` | **rendered only when ≥1 rule exists**; absent in the `Empty` state | inert | `components/EligibilityRulesBuilder.tsx:L364–L372` | — | local component — **grill question** |
| rule row | uc1-s1, uc1-s4 | operator: "is" (no values), "is any of" (≥1 value) | `sui-border-neutral-border` (divider); operator text `sui-text-neutral-text-weak`, type `sui-text-body-dense`; label `sui-text-neutral-text`, type `sui-text-label` | row owns the divider as its own `border-bottom`, so it spans the full box width; padding on the row; **nesting**: label is a fixed 124px sibling column that wraps; operator, chips and caret sit in **one** wrapping inline flow; remove × is the last sibling. Icons: `close` 18px `sui-text-neutral-icon-medium`; `arrow_drop_down` 18px `sui-text-neutral-icon-weak` | **the whole value area owns the `onClick`** and opens the value editor; the chip × owns its own `onClick` and removes one value (stops propagation); remove × hover → `sui-text-negative-icon`; no focus ring on the row | `components/EligibilityRulesBuilder.tsx:L150–L212` | — | local component — **grill question** |
| value area | uc1-s1, uc1-s4 | "Any" (no values) · the value strings (≥1 value) | chip bg `sui-bg-action-background-weak`, chip text `sui-text-admin-action-text`, type `sui-text-label-sm` | **same element; content differs**: uc1-s1 renders one non-removable chip reading "Any"; uc1-s4 renders one removable chip per value. The caret is the **same** element in both — `arrow_drop_down` 18px `sui-text-neutral-icon-weak`, placed after the chip list, never inside a chip. Chip × is `close` 14px at opacity .55 | whole area is the trigger (see rule row); chip × removes one value | `components/EligibilityRulesBuilder.tsx:L388–L466` | `Badge` | DS with overrides — **grill question** (`Badge` is 24px tall, `sui-rounded-[24px]`, `sui-px-1`, `variant` is required and has no action-blue member — override height, padding and colours via `className`) |
| value editor list | uc1-s4 | "Any" (empty pill) | check icon `sui-text-admin-action-icon`; hover row `sui-bg-neutral-background-weak` | plain option rows, `check` 18px `sui-text-admin-action-icon` on the selected row only; no checkbox column, no "Select All" row | row is the click target; instant apply, popover stays open; hover tints the row | `components/EligibilityRulesBuilder.tsx:L410–L465` · `design_handoff_eligibility_rules/README.md` | `Popover` + `PopoverContent` | local component — **grill question** · base-primitive deltas on `PopoverContent`: `arrow={false}`; radius 12px over the default `sui-rounded`; padding 6px over the default `sui-p-2`; width hugs content (the css-module `.Content` ships `width:260px`); add `max-height` + `overflow-y-auto` on the option list **only**, so search and footer stay pinned |
| add row | uc1-s1 | "+ Add eligibility setting" | `sui-bg-neutral-background-weak`; label `sui-text-admin-action-text`, type `sui-text-label`, weight 600; icon `add` 18px `sui-text-admin-action-text` | full-width row with its own padding and the weak background, below the last rule row; the `+` glyph is inline with the label in one flow, not a separate column | **the whole row owns the `onClick`**, not the link inside it; no hover pill, no button chrome | `components/EligibilityRulesBuilder.tsx:L214–L236` | `LabelButton` | DS with overrides — **grill question** (`LabelButton` defaults to a 48px `sui-rounded-full` primary pill; `variantType="link"` is the only variant with no height, no radius and no hover background — and it underlines its label on hover) |

## Tokens

| Prototype token | Code token | Applies to | Status |
|---|---|---|---|
| `var(--color-surface-raised)` | the raised-surface semantic token | rules container | ✅ resolves |
| `var(--color-slate-200)` (raw) | — | rules container border | ⚠ no equivalent, do not invent |
| `--` | `sui-text-negative-icon` | rule row → remove × (hover only) | ✅ resolves |

## DS gaps (proposed, not filed)

- **saved-view switcher** — nothing in the catalog composes it. Would file against
  <the adapter's DS-gap backlog>. **Not filed.**

## Out of scope

- uc1-s8 (edit drawer) — separate ticket
- uc2-* (questions step) — not named in the AC

## Rules to cite

- `<rule name>` — from `<usage-rules source>`
```

---

## Rules the template does not show

- **Every heading is present, every time.** A section with nothing in it says
  `None — <why>`. An absent heading and an empty one are indistinguishable to the grill, and
  "the prototype had no business rules" and "nobody looked" are very different facts.
- **`Source:` is required and is a pinned SHA**, never a branch name. A brief that cannot say
  which commit it describes cannot be checked against anything later.
- **Screenshots are linked at that SHA, never embedded.**
- **`## Scope` carries `⚠ inferred`** where the ticket named no component and the steps were
  scored. The scored list — every step, with its score, not only the kept ones — goes under the
  heading so the guess is checkable at a glance.
- **`## Overrides` keeps both halves** — the prototype's text struck through, the ticket's
  text after it. An override with the original deleted reads as the design.
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
  element that owns the `onClick` — "the whole value area opens the editor", not "clickable" —
  plus hover, focus and keyboard. `—` only where the element is genuinely inert. A hotspot renders
  in no screenshot; if it is not in this column it does not reach the implementer.
- **Every icon in `Layout facts` carries a name, a size and a colour token; every text run carries
  a type token and a colour token.** A row missing either is incomplete, and both are read off the
  source slice the `Source` column cites.
- **One row set per `components.new[].states` entry in scope**, not one per step screenshot. A
  state with no PNG is written from its `spec/component-states/<component>/<state>/page.tsx` plus
  the component source branch, and its `States` cell reads `source-only, no screenshot`. Per-state
  **conditional rendering** — "subtitle only when ≥1 rule", "container only when ≥1 rule" — is its
  own row under the state that toggles it, never a note on another row.
- **Same element, different content in two states = one row**, whose layout facts read
  `same element; content differs: …`. Two rows with two anatomies is what makes an implementer
  build two components for one design element.
- **Anatomy is written as nesting, not as a flat list of parts** — which parts share one wrapping
  flow, which are siblings. `operator · chips · caret` is satisfied by three separate columns.
- **A `local component` or `DS with overrides` row built on a base primitive enumerates that
  primitive's Default-chrome deltas as explicit override instructions** — arrow, width behaviour,
  radius, padding, max-height and scroll for `PopoverContent`; colour, hover, focus ring, size and
  border for `IconButton`; variant, size, height and hover for `LabelButton`; size and shape for
  `Input`; shape, height, padding and variant colour for `Badge`. The overlay's "Default chrome"
  note for that primitive is the source.
- **Only `Popover` (the root), `Icon` and `Separator` may be `exact` / `DS as-is` on name alone.**
  `IconButton`, `LabelButton`, `Input`, `Badge` and `PopoverContent` carry chrome and go through
  the same compare a composite does.
- **Every `## Tokens` row names the element or elements it applies to**, in the `Applies to`
  column, using the same element names the ledger uses. A token that attaches to no element is
  removed, not carried.
- **`## DS gaps (proposed, not filed)` may not read `None`** while any ledger row is
  `local component` or `DS change`. Each such row is a proposed gap.
- **`Source` cites where the layout facts came from** — `components/<file>.tsx:L<start>–L<end>`,
  plus the `design_handoff_*/README.md` where the folder has one. Where that handoff and
  `spec-data.ts` disagree on **copy**, `spec-data.ts` wins and the row says so; the handoff still
  wins on **layout**.
- **A rule is cited by name and by the source it came from.** The adapter's usage-rules row may
  name several sources, and two of them may name a rule the same thing. Cite, never restate.
- **Nothing in this brief is filed anywhere.** A proposed DS gap says where it *would* go and
  that it has not gone there.
