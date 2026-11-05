# Blueprint template

The shape `design-component` writes and keeps current through a session. **The `##` headings are
fixed** — the grill and the implementation key on them — and everything inside them is the
library's and the design's vocabulary. The example below is an invented `Notice` component.

A blueprint lives at `<repo-root>/.claude/briefs/<ticket>/blueprint.md`, beside the brief's
screenshots. It is written at the start of the design and updated whenever a decision is made or
changed, never only at the end.

---

````markdown
# Blueprint — <ticket> · Notice
Status: draft
Brief: .claude/briefs/<ticket>.md
Pinned at figma <fileKey> · node <nodeId> · version <versionId or YYYY-MM-DD> · brief .claude/briefs/<ticket>.md
Entry: <lab path>/<entry path the guide gives>
Component files: <lab path>/<entry path>/notice.<ext> · <lab path>/<entry path>/notice-action.<ext>
Updated: <YYYY-MM-DD>

## Component

`Notice` — exports `Notice`, `NoticeAction`.

## API

| Prop / slot | Kind | Values | Default | Notes |
|---|---|---|---|---|
| `tone` | variant | `info` · `warning` · `error` | `info` | changes the fill, the border and the icon colour |
| `icon` | slot | any icon node | none | absent → no leading column |
| `action` | slot | `NoticeAction` | none | absent → no trailing column, the text takes the width |
| children | children | text or inline content | — | wraps; no line limit |

Alternative not built: `icon` as a boolean that renders a fixed glyph per tone — rejected because
the glyph is the consumer's choice.

## Axis map

| Design axis / boolean | Values | Became | Why |
|---|---|---|---|
| `tone` | info · warning · error | variant `tone` | changes the component's own chrome |
| `lines` | 1 · 2 | children | the values differ only in how much text there is |
| `hasIcon` | true · false | slot `icon` | toggles whether an element is present |
| `hasAction` | true · false | slot `action` | toggles whether an element is present |

## Parts

| Part | Status | Library component | Stand-ins |
|---|---|---|---|
| `Notice` | new | — | `<ticket>-1`, `<ticket>-2` |
| `NoticeAction` | updated | `TextButton` — before: underlines on hover only · after: underlined at rest, no hover fill | — |
| close glyph | reused | `Icon` (`close`) | — |

## Examples

### info, one line
Source: state `tone-info-lines-1`
```<lang>
<Notice tone="info" icon={<Icon name="info" />}>Your changes are saved.</Notice>
```

### stress — every slot filled, long text
Source: stress
```<lang>
<Notice tone="error" icon={<Icon name="alert" />} action={<NoticeAction>Retry</NoticeAction>}>
  A sentence long enough to wrap onto three lines at the narrowest width the design shows …
</Notice>
```

## Decisions

- `lines` is children, not a prop — the two variants differ only in text length.
- The action sits in its own trailing column, top-aligned — the two-line state shows it there.

## Fidelity decisions

| Element | State(s) | Decision | Override / note |
|---|---|---|---|
| notice container | `tone-info-lines-1`, `tone-error-lines-2` | local component — build `Notice` | owns padding and radius; fill and border per `tone` |
| action link | `tone-error-lines-2` | DS with overrides — `TextButton` | underlined at rest; no hover fill |
| close glyph | `tone-info-lines-1` | DS as-is — `Icon` | — |

## Stand-ins

| Id | Literal used | What replaces it |
|---|---|---|
| `<ticket>-1` | `6px` corner radius | a radius token for message surfaces |
| `<ticket>-2` | `14px / 20px` text | a type step at that size, added to the library |

## Integration

- Replace stand-in `<ticket>-1` with a radius token; add the token to the token source.
- Replace stand-in `<ticket>-2` with a new type step; the type step is a library change.
- Copy the component files into the library source; add the package exports.
- Tests: tone classes, slot presence, wrapping.
- Stories from `## Examples`.
- Keyboard and focus: the action is reachable by Tab; the notice itself takes no focus.
- Library change: `TextButton` gains an underlined-at-rest option (see `## Parts`).

## Questions for the designer

- The warning state binds a fill that differs from the render — which is right?

## Not handled

- `settings page` — a recipe; composes `Notice` with other components.
- `inline help text` — a loose part, not a component set; rendered as plain context in the
  examples only.
````

---

## Rules the template does not show

- **Every heading is present, every time.** A section with nothing in it says `None — <why>`.
- **`Status:` is `draft` or `settled` and nothing else.** Only an `approve` sets `settled`; a
  reopen sets it back to `draft`.
- **The pin line is copied from the brief character for character.** It is what tells a later
  session that the brief on disk has changed since this design was made.
- **`Component files:` names every file the component is built from.** The implementation starts
  as a copy of those files into the library source, so a file missing from this line is a file
  the implementation never receives.
- **With several component sets, the header lists one `Entry:` and one `Component files:` line
  per set, and each of `## Component`, `## API`, `## Axis map`, `## Parts` and `## Examples`
  carries one `### <Component>` subsection per set.** The other sections stay single lists, each
  line naming its component where that is not obvious.
- **No layout fact is restated in words.** Padding, gaps, radii, nesting and sizes live in the
  component file. A blueprint that also states them holds a second copy that drifts the moment
  the user nudges the entry.
- **`## Axis map` lists every axis and every boolean the brief's `## Component states` names for
  the set**, each with what it became: a variant, a slot, children, or `dropped — <why>`.
- **`## Parts` status is `new`, `updated` or `reused`, one part per row** — every sub-component
  or distinct part on its own, never several joined into one. An `updated` part names the library
  component and states its before and after in one line each; the change itself is a copy inside
  the entry and an item under `## Integration`.
- **`## Examples` carries usage code, not screenshots.** Each example names its source: the design
  state it reproduces, or `stress`.
- **`## Decisions` is one line each, with one line of reason.** Purely visual nudges are not
  decisions and are not recorded here.
- **`## Fidelity decisions` uses deep-grill's four columns exactly**, one line per ledger row the
  entry renders and none for a row it does not. The `Decision` cell opens with one of
  `DS as-is` · `DS with overrides` · `local component` · `DS change`, per
  `../../_shared/fidelity-ledger.md` §1, and every line is phrased as an instruction. A decision
  that adds a visual property the ledger row does not hold writes
  `added — not in the design: <property>` in the note.
- **Every stand-in id in `## Stand-ins` appears in a marker comment in a component file, and every
  marker in the component files appears here.** `grep` on the marker is the check.
- **`## Integration` is the work the implementation still owes**, and the list a later grill
  asks about. It always covers: each stand-in, tests, stories from the examples, package exports,
  keyboard and focus behaviour, and each real library change — every `new` and `updated` token
  among them, one line each.
- **`## Questions for the designer` is a list.** Nothing in it is sent anywhere.
- **`## Not handled` names each recipe and loose part by its ledger `Element` name**, so a later
  reader can find the rows it set aside.
