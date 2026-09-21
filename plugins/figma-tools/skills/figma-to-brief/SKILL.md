---
name: figma-to-brief
description: >
  Turn one Figma node into a design brief for one ticket. Pins the file key, the node id
  and the file version, reads the in-scope state frames through the local Figma MCP
  server, saves one PNG per state to disk, filters the design to what the ticket covers,
  renders the ticket's overrides on top, and resolves every element and token against the
  project's design-system catalog into a per-element fidelity ledger. Asks nothing —
  every judgement becomes a row the grill can question.
  Invoke /figma-tools:figma-to-brief <figma-url> <ticket>.
disable-model-invocation: true
metadata:
  author: liam
  version: "1.0.0"
---

# Figma → Brief

A **design source in the brief slot**, beside `prototype-to-spec` and in the same place in the
flow. The input is a canvas: one Figma node in the organisation the adapter's `### Figma source`
rows name, read through the local `figma-dev-mode` MCP server against the file open in Figma
Desktop.

```
/figma-tools:figma-to-brief <figma-url> <ado-id>     → writes a brief + screenshots, asks nothing
/lk:deep-grill <ado-id> .claude/briefs/<ado-id>.md   → design rows are answers, OPEN rows are questions
/ado-workflow:to-spec                                → the ledger and the pin line reach the [SPEC]
```

**The output is a brief, not a spec, and it is disposable.** It describes one ticket against one
Figma file at one version, it is written to an excluded directory, and it is regenerated rather
than updated. The durable artifact is the `[SPEC]` work item.

That is the deliberate difference from `figma-tools:figma-to-spec`, which files a `[DESIGN-SPEC]`
work item and has to freeze what it saw because the canvas moves under it. This skill files
nothing, on any tracker. What keeps the brief checkable is the **pin line** — file key, node id
and version — not a filed copy.

## What this replaces, and why it exists

Handing an implementer a Figma link does not work, in two distinct ways, and the brief is aimed
at both:

- **A link is not a fact.** Opening the canvas costs the implementer an MCP call budget it does
  not know it is spending, and what it reads back is a frame — the whole screen, with the row's
  facts buried inside it.
- **Reading the canvas per implementer** means re-deriving the same nesting, the same icon names
  and the same bound variables every session, non-deterministically. What came back was a
  hand-rolled copy of what the frame looked like rather than the design-system components that
  already do the same job.

**The canvas is read. It is read here, once, by this skill — and only layout facts come out of
it.** The element node is the only place the exact layout lives: which element owns the divider,
which axis a pair of fields stacks on, which element owns the padding, what a row contains left
to right, what each property is bound to. Those facts go into `## Fidelity ledger` as words and
token names. Nothing else crosses over: **no generated JSX from `get_design_context`, no
arbitrary Tailwind values, no absolute coordinates, no prototype wiring.** The implementer
re-reads the named element nodes and builds each ledger row from design-system components
against the facts in that row.

So an implementer session should open with **facts**: which states are in scope, what each
element's layout actually is, which design-system component each element resolves to and at what
fidelity class, and which design behaviours the ticket overrides.

## It asks nothing

**There are no questions in this skill.** Every judgement call becomes a row in the brief,
carrying its confidence, and the grill is where a human answers it. A skill that stops to ask is
a skill nobody runs twice.

The only stops are hard input failures, all in Phase 0 and Phase 1: `whoami` does not report the
organisation and seat the adapter's `### Figma source` rows name, the URL carries no `node-id`,
the node does not resolve, there is no catalog, or the adapter has no `### Figma source`. Each
says which input failed and what would fix it. There is no degraded mode and no partial brief.

## Invocation

```
/figma-tools:figma-to-brief <figma-url> <ado-id> [--out <path>]
```

- `<figma-url>` — a Figma design URL carrying a `node-id`. Required. A URL with no `node-id` is
  a STOP, never a guess: the node is what everything downstream is pinned to.
- `<ado-id>` — the work item this brief is for, as a number or a URL. Required; it is what the
  filter runs against, so a brief without one would be the whole canvas again.
- `--out` — where the brief goes. Default `<repo-root>/.claude/briefs/<ado-id>.md`, with the
  screenshots beside it at `<repo-root>/.claude/briefs/<ado-id>/screenshots/`. That directory is
  excluded from git; the brief is disposable and a committed one is a second source of truth with
  a long half-life.

## Inputs

- **The project adapter**, `<repo-root>/.claude/project/adapter.md`:
  - `## Design system` → `### Figma source` — the rows this skill runs on: the **account and
    seat**, the **servers**, the **URL → pin** rule, the **screenshot** export rule and the
    **call budget**. **Absent is a STOP**: it means this project has no Figma source registered.
  - `## Design system` → the **catalog pointer** (`Catalog:`), the **class-prefix** rows, the
    **icon resolution ladder**, and the **usage-rules source**. An absent `## Design system` is
    a STOP.
  - `## Repo` → `### Azure DevOps`, for the **work-item project** row the ticket is fetched
    from, and the **DS-gap backlog**, which this skill only ever _names_ in a proposed gap row.
    It files nothing there.
- **The Figma file**, read-only through the local `figma-dev-mode` MCP server, at one pinned
  version. The file must be open in Figma Desktop — the local server's tools resolve against the
  running app.
- **The catalog**, per `../figma-to-spec/references/catalog-contract.md` — the existence source
  every element and token resolves against. Validate the resolved file against that contract and
  fail loudly rather than degrade, exactly as `figma-to-spec` Phase 0 does.
- **The resolution rules**, `../figma-to-spec/references/resolution-rules.md` — property-kind
  filtering, colour tiers and tolerance, typography and spacing, and the icon ladder's mechanics.
  **Cited, never restated**: this skill adds the fidelity classification on top of them and does
  not re-derive how a colour resolves.
- **The extraction discipline**, `../../agents/figma-region-extractor.md`, its
  *Figma call discipline* and *Two filters that apply before anything below* sections. Read them
  and apply them on the main thread. Two of its rules are load-bearing here and are restated in
  Phase 4 because a reader who skips the file still has to obey them: **hidden state-bearing
  nodes are in-scope content**, and **vector interiors are drawing data, not design decisions**.
- **`$FIGMA_PAT`** — a Figma personal access token with `files:read`, in the environment. It is
  what saves the PNGs and reads the version id. Never print it, never echo it, never write it
  into the brief.
- **The brief's shape**, `references/brief-template.md`.

## Phases

All on the main thread. **No subagents.** `figma-to-spec` fans out over a whole page because a
page has many regions; a brief covers one ticket's states, and a region agent's JSON would have
to be re-flattened into ledger rows anyway — the flattening is where fidelity leaks.

| Phase                    | Does                                                                                                                              |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| **0 — Resolve**          | `whoami` (the adapter's organisation and seat) · adapter rows · catalog validated · ticket fetched.                               |
| **1 — Locate and pin**   | URL → file key + node id · `get_metadata` for the frame tree · version or date · the pin line.                                    |
| **2 — Filter by ticket** | Keep the state frames the ticket covers; record every drop with its reason.                                                       |
| **3 — Overrides**        | Render the ticket's divergences on top of the design's.                                                                           |
| **4 — Resolve elements** | Every element and token against the catalog, at three confidences · one fidelity-ledger row per element, with its fidelity class. |
| **5 — Write and stop**   | The brief, the saved PNGs, then the path and the counts. Nothing else.                                                            |

### The Figma call budget, per phase

The seat allows a **daily and a per-minute call budget**, and the adapter's `### Figma source`
*Budget* row states both — read them from there, never from this file. The whole budget is shared
with every other session on this machine. Only `whoami` is free; every read counts.

| Phase | Calls                                                                                                          |
| ----- | ---------------------------------------------------------------------------------------------------------------- |
| 0     | `whoami` — free, and the only free call there is.                                                              |
| 1     | one `get_metadata` on the node in the URL. One more per kept state frame **only** where the tree is nested deeper than the first response returned. |
| 2     | none. The filter runs on the ticket and the metadata already read.                                             |
| 3     | none.                                                                                                          |
| 4     | per in-scope element node: one `get_design_context`, one `get_variable_defs`, and `get_screenshot` **only** where the row is ambiguous without a render. Read each node once. |
| 5     | none. The PNGs are saved over the REST API, which does not spend this budget.                                  |

**Count the calls as you make them and print the total in the final print.** Stop at the daily
cap rather than pushing through it: a run that exhausts the budget takes the whole day's Figma
access with it, for every session on the machine. On a stop, say how many calls were spent, which
nodes were read and which were not, and write no partial brief.

Never walk a frame hunting for a node. Never re-read a node to check a value you already have in
this session.

### Phase 0 — Resolve

Read the adapter. Establish, and stop on any of them:

1. **`### Figma source`** — all of its rows. Absent sub-section → STOP: _this project has no
   Figma source registered; `install-skills` asks for one._
2. **The seat.** Call `whoami` on the Figma MCP server. It must report the **organisation** and
   the **seat** the `### Figma source` *Account and seat* row names. Any other plan on the same
   login is a STOP: a lesser plan's allowance does not survive one run, and the failure mid-run
   looks like a broken file rather than an exhausted quota.
3. **`## Design system`** — the catalog pointer, the class-prefix rows, the icon resolution
   ladder and the usage-rules source. An absent section → STOP: _this project has no design
   system registered; `install-skills` asks for one._
4. **The catalog** — resolve through the `Catalog:` pointer and validate against the shape
   contract, which is the same gate `figma-to-spec` runs and fails the same way. **Where the
   pointer resolves to a single file** there is **no overlay document and no `## Idiom mapping`
   table** — so every rule below that reads a "Default chrome" note reads the catalog's variant
   axes and the node render instead. Say so once in the run; it changes what Phase 4's rule 2
   compares against, not whether it runs.
5. **The usage-rules source** — keep it by name, as the adapter's row names it. Absent is the
   answer, not a warning: the brief then cites nothing.
6. **The ticket** — fetch work item `<ado-id>` with `mcp__ado__wit_work_item`, against the
   **work-item project** the adapter's `## Repo` → `### Azure DevOps` rows name. Where that
   project's work-item type carries no `AcceptanceCriteria` field, the acceptance criteria live
   in the description instead — either way that text is the filter's input, so a ticket that
   cannot be fetched is a STOP.

### Phase 1 — Locate, and pin

1. **Parse the URL**, per the adapter's `### Figma source` *URL → pin* row.
   `https://www.figma.com/design/<fileKey>/<name>?node-id=<a>-<b>` yields the **file key** and
   the **node id**, and the node id is written `<a>:<b>` in every tool call and in the ledger. A
   `/design/branch/<branchKey>/` URL pins the **branch key** as the file key. A URL with no
   `node-id` is a STOP. A `/make/` URL is a STOP — the local server does not read them.
2. **Read the tree.** `get_metadata` on that node returns the children, names, types, positions
   and sizes. That is the **state frame list** Phase 2 filters and the **element node ids**
   Phase 4 resolves. Read it once and work from the response.

   **Hidden nodes carry state.** A `visible:false` child whose name implies a state or a variant —
   a banner, a chip, an empty state, an error message — is in-scope content, not noise. Keep it,
   and say which state it represents. Only a clearly scaffolding node (spacer, guide,
   placeholder, `_`-prefixed) is pruned, and a pruned node is named in the brief's `## Scope`.
3. **Pin the version.** Read the file's newest version id over the REST API, which does not spend
   the MCP budget:

   ```
   curl -sS -H "X-Figma-Token: $FIGMA_PAT" \
     "https://api.figma.com/v1/files/<fileKey>/versions?page_size=1" \
     | python3 -c "import json,sys; print(json.load(sys.stdin)['versions'][0]['id'])"
   ```

   Where `$FIGMA_PAT` is unset or the call fails, pin **today's date** as `YYYY-MM-DD` instead and
   say in the brief's header that the version id was unavailable. Both forms are allowed by the
   contract; a silent omission is not.
4. **Write the pin line**, in exactly this form, per `../_shared/fidelity-ledger.md` §1:

   ```
   Pinned at figma <fileKey> · node <nodeId> · version <versionId or YYYY-MM-DD> · brief <path>
   ```

   It is what lets a later session re-read the same design state. Every consumer copies it
   character for character, so it is written once, here, and never reworded.

### Phase 2 — Filter by ticket

The canvas covers a whole screen or flow; the ticket covers a slice of it. Read the ticket for
three things: a **named component or file** (a `Component:` line, or a backticked `X.tsx`), the
**acceptance-criteria text**, and an **overrides or divergence section** where one exists.

With a component named, keep:

| Keep                                          | On what basis                                                                            |
| --------------------------------------------- | ------------------------------------------------------------------------------------------ |
| a state frame                                 | its name, or an element inside it, is one the ticket names                                |
| a hidden state-bearing node inside a kept frame | it is a content state of a kept frame                                                    |
| an element node inside a kept frame           | it is part of the named component's anatomy                                               |
| every variable the kept nodes bind            | whole — a token dropped for being out of scope is a token the implementer invents         |

**Record every dropped frame id with the reason it was dropped.** Those go in the brief's
`## Out of scope`, which is not padding: the failure this pipeline exists to fix produced
implementations of things nobody asked for, because the design showed them.

**With no component named**, score instead of guessing. Tokenise the ticket's acceptance criteria
and each frame's name, drop stopwords, and score each frame by how many distinct tokens it shares
with the AC text, weighting a token by how _few_ frames carry it — a term appearing in every
frame separates nothing. Then:

- **Print the whole scored list in the brief**, every frame with its score, not just the kept
  ones. The scoring is a guess and showing its working is what makes it checkable in one glance.
- Keep the frames that score above the natural break in the list, and where there is no natural
  break, keep the top-scoring frame group whole rather than slicing one down the middle.
- **Mark the `## Scope` section `⚠ inferred`.** Still no question: the grill confirms scope, and
  it will confirm it faster looking at a scored list than at a prompt.

Scope settles here, and Phase 4 reads only the nodes it kept. That ordering is the budget rule in
practice — a node read before the filter is a node read for a frame that gets dropped.

### Phase 3 — Overrides

A ticket that contradicts the design **wins, always**, and the brief says so at the point of
contradiction rather than in a preamble. Render the ticket's divergences on top of the canvas's
own:

```
~~the design's behaviour~~ → overridden by ticket: <the ticket's text>
```

Both halves stay visible. An override with the design's text deleted reads as the design, and the
next person to open the file finds a disagreement with no record of which way it was settled.

### Phase 4 — Resolve elements against the catalog

Three populations, one resolution pass:

1. Every **instance node** in a kept frame — a node whose name follows `Component/Variant/Size`
   or matches a catalog component's name.
2. Every element the ticket's acceptance criteria names.
3. Every **hand-drawn idiom** in a kept frame — a popover, a chip row, a search field, a table
   header, a stepper. These are the ones that matter: a designer draws them out of rectangles
   because a canvas has no components for them, and an implementer copying the drawing faithfully
   reproduces a component that already ships.

Resolve each per `../figma-to-spec/references/resolution-rules.md` — **property-kind filtering
first**, then the colour tiers, the typography and spacing split, and the icon ladder. Two of
that file's consequences decide rows here and are not negotiable: a numerically perfect match
from the wrong property kind is a **wrong** row, not a lucky one; and **vector interiors inside
an icon are drawing data** — the icon resolves as a whole through the adapter's ladder, while its
own box size and its applied colour stay in scope.

Propose a design-system mapping for each, using the catalog's `## Components` table. **Three
confidences, and they are the brief's whole interface to the grill:**

| Confidence | Means                                                                 | What the grill does                                   |
| ---------- | --------------------------------------------------------------------- | ----------------------------------------------------- |
| `exact`    | the catalog names this component and rule 3 below allows a name match | treats it as resolved and never asks                  |
| `likely`   | name similarity, or exactly one plausible candidate                   | one confirm question, batched with the others         |
| `OPEN`     | nothing in the catalog matches                                        | a round-one question, with the three standard answers |

**Never promote a guess to `exact` to tidy the table.** An `exact` row is never asked about
again, so a wrong one is the only kind of error in this brief that reaches implementation
unchallenged.

**Tokens** resolve against the catalog's `## Tokens` tiers. The bound variable name comes from
`get_variable_defs` on the node; a value with no bound variable and no catalog token is flagged —
not silently mapped to the nearest thing. The canvas is allowed to hold a raw value; the
implementation is not. An unbound colour is flagged `⚠ no equivalent, do not invent`. An unbound
spacing, radius, size or font size — a padding, gap, corner radius, dimension or text size the
node holds as a literal number matching no named token on its tier — is flagged `⚠ off-grid`,
naming the nearest catalog token and the delta.

**An off-grid value stays raw, and the decision belongs to the grill.** Four things happen to it
together: it appears in the ledger's `Layout facts` **unchanged**; it carries its `⚠ off-grid`
flag with the nearest token and the delta; it gets a row in `## DS gaps (proposed, not filed)`,
the way an unbound hex does; and its ledger row is marked **grill question** with both options
spelled out — the raw value, and the nearest token. Writing the nearest token in place of the
value is the same failure as carrying the value bare, and a row that presents the choice as
already made is the same failure again. This is how a text size with no type token survives too:
a size and a weight standing in for a token is an incomplete row unless it meets all four
conditions.

**There is no per-property binding read where the adapter registers no remote server.**
`use_figma` lives on the remote Figma server, so where the `### Figma source` *Servers* row names
only the local one, a bound variable is known **per node**, from `get_variable_defs`, never per
property. Where one node binds several variables and the assignment to fill, border and text is
not obvious from the render, the row says so —
`binding unverified: node binds <names>, property assignment not readable` — and that phrase is a
grill question like any other. Never present an inferred assignment as verified.

**Every `## Tokens` row names the element or elements it applies to**, in its own `Applies to`
column, and the names it writes there are element names the fidelity ledger also uses. A token row
with no element is dead text: nobody can act on it. **Remove a token that attaches to no element**
rather than carrying it unattached.

**Every `OPEN` row that looks like a genuine design-system gap** also gets a row in
`## DS gaps (proposed, not filed)`, naming the adapter's DS-gap backlog as where it would go.
**Proposing is the whole of it.** Filing is a decision, the grill is where it gets made, and a
gap filed by a skill that asks nothing is a gap nobody agreed to. An icon that resolves from
neither source of the adapter's ladder is **not** a DS gap — it is a design question for the
designer, per the ladder's own last step.

#### The fidelity ledger

`## Element → DS mapping` answers _which component_. It does not answer _does that component,
rendered with no arguments, look like the node_ — and that is the question a run loses fidelity
on. `## Fidelity ledger` answers it, one row per element, and it sits directly after
`## Element → DS mapping` in the brief.

**An element is a distinct visual thing, not a component.** A container, a row, a divider, an add
row, a value pill, an option list, a popover, a search input, a footer action — each is its own
row. One design-system component can appear as the candidate on several rows, and one row can
name several. Do not collapse rows to match a component count.

**One row set per state, not per screenshot.** Emit ledger rows for **every** in-scope state,
including a state that lives as a `visible:false` node inside a kept frame and therefore renders
in no screenshot of the visible frame. Mark such a row `hidden variant, no screenshot` in the
`States` column, so the grill asks about it rather than inheriting a screenshot's silence.
**Per-state conditional rendering gets its own row**, under the state that toggles it — "subtitle
rendered only when ≥1 row exists", "bordered container rendered only when ≥1 row exists". A fact
of the form _this element is absent in this state_ is a row, never a note appended to another
row: a state that reaches the brief only as a link reaches implementation as nothing.

**Same element, different content in two states — one row.** Where two states render the **same**
element with different content, the ledger writes **one** row whose layout facts read `same
element; content differs: <state A> renders …, <state B> renders …`. Never two rows with two
anatomies. Two anatomies is what makes an implementer build two components with two tokens and
two icons for one design element.

**The content container is an element, and it gets a row.** Every kept state wraps the in-scope
elements in something — a panel, a section card, a list wrapper, or the page surface itself — and
that immediate wrapper is a row like any other. `Element` reads `content container`, in those
words, so a consumer merging rows on Element plus States matches the same element across states.
`States` carries the kept state or states: one row per state where the container's facts differ,
one shared row where they are identical. `Tokens` carries the fill token, or the literal
`none — page background` where the container binds no fill, plus the border and shadow tokens
where it binds them. `Layout facts` carries padding, corner radius, border, shadow, width
behaviour, and where the in-scope elements sit relative to it. `Interaction` is `inert`. `Source`
cites the **container** node, `<fileKey>:<nodeId>`, never the frame and never the page root.
`DS candidate` and `Fidelity class` follow the classification rules below, as on every other row.

**A container that binds no fill is recorded as its own row, reading `none — page background`.**
It is never a note inside another element's row. A container fact parked in a neighbour's `Tokens`
cell reads as a parenthesis about that neighbour, and the container it described gets built from
the other state's row instead — a white panel drawn around a state whose design has none. Two
states whose containers differ are two rows, each stating its own fill, padding and radius.

**Page-chrome pruning never prunes the content container.** Navigation, the top bar and the app
shell are chrome and stay out of the brief. The wrapper around the in-scope elements is the design
the ticket covers, and its fill, padding, radius and border are the surface every other row in the
state sits on.

**Write anatomy as nesting, not as a flat list of parts.** Say which parts share one wrapping flow
and which are siblings — "the label is a fixed sibling column that wraps; operator, chips and
caret sit in one wrapping inline flow". A flat `icon · label · chips · caret` is satisfied by four
separate columns, and the design frequently has three of them inside one flow.

**Never write an absolute coordinate.** `get_metadata` answers in x/y and size; the ledger answers
in auto-layout intent — direction, gap, padding, alignment, wrap, and which element owns each.
Where the intent was derived from positions rather than read from auto-layout, the row says
`layout inferred from positions`.

| Column             | Contents                                                                                                                                                                                                                                                                              |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Element            | the visual thing, in the design's own words                                                                                                                                                                                                                                           |
| States             | the state frames it appears in; `hidden variant, no screenshot` for a `visible:false` state node; `⚠ no screenshot` where the PNG export failed                                                                                                                                       |
| Exact copy         | every string, per state — label, placeholder, empty text, button text. Quote it; never paraphrase                                                                                                                                                                                      |
| Tokens             | the bound variable names the node reports, mapped to the catalog's consumer-facing class or CSS custom property, and — listed separately in the same cell — every raw hex that still needs a mapping                                                                                    |
| Layout facts       | in words: nesting (which parts share one wrapping flow), stack direction, full-width or not, divider placement and **which element owns it**, which element owns the padding, gap, corner radius, size, and — per icon — **icon name, size and colour token**, and — per text run — its **type token and colour token** |
| Interaction        | the Figma prototype reaction on the node, named as an element: "the whole value area opens the editor", plus the trigger and the destination state. `—` **plus a grill question** where the node carries no reaction — see below                                                        |
| Source             | `<fileKey>:<nodeId>` — the **element** node, never a frame and never a page root                                                                                                                                                                                                       |
| DS candidate       | the component from `## Element → DS mapping`, or `—`                                                                                                                                                                                                                                   |
| **Fidelity class** | `DS as-is` · `DS with overrides` · `local component` · `DS change` · `OPEN`                                                                                                                                                                                                            |

**An icon written without a name, a size and a colour token is an incomplete row, and so is a text
run written without a type token and a colour token.** Both are invisible in a screenshot at the
sizes a design ships at, and both are the difference between a 14px muted glyph and a 24px red
one. Read them off the node the `Source` column cites. Icon names are written in the ladder's own
reference form — the name the adapter's icon ladder gives its primary source, as the design places
it — and are never translated into a near neighbour.

**The `Interaction` column carries what no screenshot can**, and on a canvas it is also the column
most often empty. Where the node carries a **prototype reaction**, `get_design_context` reports it
and the cell names the element that owns it, the trigger and the destination. Where the node
carries none, the cell is `—` **and the row says `interaction not in the design — grill
question`**. That is not the same as an inert element: `—` alone means inert, and a static frame's
silence about hover, focus and keyboard is a gap the grill fills, never a licence for the
implementer to invent one.

##### Classification rules

1. **Composites are never `exact`, and never `DS as-is` without evidence.** A composite is any
   component that ships its own chrome: `Select`, `Autocomplete`, `MultiSelect`, `Calendar`,
   `Table`, `Card`, `Accordion`, `Carousel`, and **any component the catalog records a variant
   axis for**. Such a component may not be given confidence `exact` in `## Element → DS mapping`,
   and may not be given fidelity class `DS as-is` unless rule 2 produced no difference.
2. **Compare the default chrome against the row's layout facts.** Where the catalog is a generated
   document with no overlay, a component's **default chrome is its catalog entry's default variant
   values plus what it renders** — take the defaults from the `## Components` table (the `(def)`
   values) and the rendering from the node's screenshot next to however the app already renders
   that component. Then:
   - **No difference** → `DS as-is`.
   - **A difference the component exposes a prop, a variant value or a `className` for** →
     `DS with overrides`. Name the prop, the variant or the class hook in the notes.
   - **A difference with no prop, variant or `className` path** → `local component`.
   - **A difference that should not be solved locally because the design system itself is wrong
     or missing the affordance** → `DS change`, against the design system the adapter's
     *Design-system source* row names.
3. **Only a chromeless root may be `exact` and `DS as-is` on name alone: `Popover`, `Dialog` and
   `Tooltip` (the roots, not their `*Content`), and an icon rendered through the adapter's icon
   ladder.** They render nothing the caller did not ask for, so name-matching them is safe.
   **`Button`, `IconButton`, `Chip`, `Tag`, `Separator`, `PopoverContent` and `DialogContent` are
   not on that list** — each ships colour, hover, focus, radius, height, thickness or padding of
   its own, and each carries a variant axis or a fixed default in the catalog. They go through
   rule 2's compare exactly as a composite does. A `primary`-by-default `IconButton` under a
   design that draws a neutral glyph turning red on hover is a difference.
4. **A `local component` built on a base primitive enumerates that primitive's deltas as explicit
   override instructions.** Replacing a composite with a primitive does not make the primitive
   chromeless. Where a row is `local component` (or `DS with overrides`) on top of a base
   primitive — a local option list on `PopoverContent`, a local pill on `Chip` — the row's notes
   list **every** default-chrome delta that primitive brings, each as an instruction: padding,
   radius, arrow and width behaviour for `PopoverContent`; variant colour, size, height and
   `selected` treatment for `Chip`; variant, size, loading slot and hover for `Button` and
   `IconButton`; variant and thickness for `Separator`; `size` and overlay behaviour for
   `DialogContent`. "Built on `PopoverContent`" is not an instruction; "no arrow, radius 12px over
   the default, padding 6px, width hugs content, max-height and scroll on the option list only"
   is.
5. **Every row that is not `DS as-is` is a grill question.** Say so in the row's notes, in those
   words. The grill's contract is that it asks about them; the ledger's contract is that it marks
   them.
6. **`## DS gaps (proposed, not filed)` may not read `None` while any row is `local component` or
   `DS change`.** Each such row becomes a DS-gap entry, proposed, not filed — naming the adapter's
   DS-gap backlog as where it would go, per the rule above.

##### Where the facts come from, and who wins

A Figma node answers through three tools that disagree in predictable ways, so the order is fixed:

- **`get_variable_defs` wins on tokens.** A bound variable name is the design's own statement of
  which token it meant. A hex read out of `get_design_context`'s generated code, or off a render,
  is a value — it loses to a name every time, and it is written into the row only where no
  variable is bound.
- **`get_design_context` wins on nesting, auto-layout and interaction.** It is the only read that
  reports the containment tree, the auto-layout direction, gap and padding, and the node's
  prototype reactions. **Its generated code is read as intent, never as output**: no class list,
  no arbitrary value, no JSX crosses into the brief. Strip every arbitrary value it emits.
- **`get_metadata` wins on identity and on what exists** — the node id, name, type, size, and the
  hidden siblings. It is the source for the `Source` column's node id and for the hidden-variant
  rows, and it is never the source for a layout fact, because positions are not intent.
- **The screenshot is the arbiter of last resort**, for a row two reads leave ambiguous. It is not
  evidence about a token name, and a colour taken off a PNG is a hex, which loses to rule one
  above.

Where a ticket's text disagrees with the node on **copy**, the ticket wins and the row says so —
Phase 3 already rendered it, and the ledger's `Exact copy` cell carries the winning string with
the loser noted inline. The node still wins on **layout**.

### Phase 5 — Write the brief, and save the screenshots

1. **Save one PNG per in-scope state**, at
   `.claude/briefs/<ado-id>/screenshots/<state-id>.png`, per `../_shared/fidelity-ledger.md` §3
   and the adapter's `### Figma source` *Screenshots* row. The state id is the frame's name,
   slugged, and it is the same string the ledger's `States` column uses —
   `ado-workflow:to-spec-tasks` matches the two on that string, so a mismatch orphans the
   attachment. Create the directory first.

   The local `get_screenshot` returns an **image into this session, not a file**, so the PNG
   reaches disk over the Figma REST images endpoint, which does **not** spend the MCP budget:

   ```
   mkdir -p .claude/briefs/<ado-id>/screenshots

   URL=$(curl -sS -H "X-Figma-Token: $FIGMA_PAT" \
     "https://api.figma.com/v1/images/<fileKey>?ids=<nodeId>&format=png&scale=2" \
     | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['images'].popitem()[1])")

   curl -sSL -o ".claude/briefs/<ado-id>/screenshots/<state-id>.png" "$URL"
   ```

   The `ids` parameter takes the node id in `<a>:<b>` form, one node per call, and the answer's
   `images` map holds a short-lived URL — download it at once. `scale=2` is deliberate: a 1×
   export of a dense frame loses the icon sizes the ledger asserts.

   **`$FIGMA_PAT` unset is a STOP**, named as such: the brief's screenshots are a contract §3
   requirement and a brief without them hands the implementer prose. Say that the fix is a Figma
   personal access token with `files:read` exported as `FIGMA_PAT`. Never print the token, and
   never write it into the brief or a command the brief carries.

   Where a single export fails, that is **not** a STOP: mark the ledger row's `States` cell
   `⚠ no screenshot` and carry on.

2. **Read each saved PNG as an image** before writing the ledger. The render is what
   classification rule 2 compares a component's default chrome against, and a ledger written
   without the images is a ledger written from names.

3. **Write the brief** per `references/brief-template.md`, to `--out` or to the default path.
   Before writing it, check the ledger against its own rules: one row set per kept state, **one
   `content container` row per kept state**, an icon name, a size and a colour token on every icon
   and a type token and a colour token on every text run, an element node id in every `Source`
   cell, and `grill question` in the notes of every row that is not `DS as-is`.

4. **Print**, per `../_shared/final-prints.md`, exactly three things: **the path**, **the counts**
   — states kept and dropped, rows at each of the three confidences, ledger rows at each fidelity
   class, PNGs saved — and **the Figma calls spent**. Close with the next command,
   `/lk:deep-grill <ado-id> <brief path>`.

The brief's content is not summarised into the print. It is a file, one click away, and it is
about to be read by the grill.

## Screenshots are saved to disk, never embedded

The brief carries, per state, the **local path** of the saved PNG and the **node link** as the
pinned address:

```
Screenshot: .claude/briefs/<ado-id>/screenshots/<state-id>.png · node https://www.figma.com/design/<fileKey>/?node-id=<nodeId>
```

Both halves are required and neither replaces the other. The path is what
`ado-workflow:to-spec-tasks` copies into the task; the node link is what a human opens to see the
design in context.

**A `figma.com` image export URL is never written anywhere.** The REST answer's URL expires
within the hour, and a Figma render is not public, so a link to one is a broken image on every
work item that carries it.

**This skill reads the PNGs anyway, and that is not a contradiction.** Phase 5 saves every
in-scope export and reads it as an image, because the fidelity ledger and its classification rules
cannot be written from names. The images land on disk and in this session; the brief carries paths
and node links.

## STOP gates

1. **No `### Figma source` in the adapter** → stop, and name `install-skills` as what adds one.
2. **`whoami` does not report the organisation and seat those rows name** → stop, naming the plan
   it did report and its call allowance. Never start a run on a lesser seat.
3. **No `## Design system` in the adapter** → stop, and name `install-skills` as what adds one.
4. **The URL carries no `node-id`, or names a `/make/` file** → stop, showing the URL and what a
   usable one looks like.
5. **`get_metadata` does not resolve the node** → stop, naming the file key and the node id. The
   usual cause is a file that is not open in Figma Desktop, because the local server reads the
   running app — say so.
6. **No catalog, or a catalog that fails the shape contract** → stop exactly as `figma-to-spec`
   does, naming the resolved path, the rule and the fix.
7. **The ticket cannot be fetched** → stop, naming the project and the id.
8. **`$FIGMA_PAT` is unset** → stop before Phase 5 writes anything, naming the token scope and the
   variable.
9. **The daily Figma call cap is reached mid-run** → stop, report the calls spent and the nodes
   still unread, and write no partial brief.

## What this skill does not do

- **It does not file anything.** No work item, no attachment, on any tracker. It proposes gaps in
  a brief and stops.
- **It does not write code**, and it does not paste `get_design_context`'s generated output. It
  reads the canvas for layout facts.
- **It does not persist a spec.** The brief is disposable and the `[SPEC]` work item is the
  durable artifact.
- **It does not call `use_figma`** where the adapter's `### Figma source` *Servers* row names no
  remote server. That tool lives on the remote Figma server, so per-property bindings are then out
  of reach by construction and the row says so rather than guessing.
- **It does not ask.** Anything it cannot settle is a row, at a confidence, for the grill.
