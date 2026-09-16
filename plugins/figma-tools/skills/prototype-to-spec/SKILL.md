---
name: prototype-to-spec
description: >
  Turn a designer-authored code prototype into a design brief for one ticket. Resolves
  a preview URL to a pinned commit in the prototype repo, reads the spec and the
  prototype source committed there, reads the in-scope screenshots as images, filters
  it to what the ticket covers, renders the ticket's overrides on top, and resolves
  every element and token against the project's design-system catalog into a
  per-element fidelity ledger. Asks nothing — every judgement becomes a row the grill
  can question. Invoke /figma-tools:prototype-to-spec <preview-url> <ticket>.
disable-model-invocation: true
metadata:
  author: liam
  version: "1.0.0"
---

# Prototype → Brief

A **second design source**, beside `figma-to-spec` and in the same slot in the flow. The input
is not a canvas: it is a repo where designers ship running React prototypes together with a
committed, structured spec, deployed one preview per pull request.

```
/figma-tools:prototype-to-spec <preview-url> <ticket>   → writes a brief, asks nothing
/lk:deep-grill <ticket> <brief-path>                    → design rows are answers, OPEN rows are questions
/prd-workflow:to-prd                                    → UI Primitives + Design reference filled from the grill
```

**The output is a brief, not a spec, and it is disposable.** The prototype's spec is already a
structured document committed in git at a SHA; a second durable copy on this side would only
drift from it. The one persisted artifact is the PRD.

That is the deliberate difference from `figma-to-spec`, which files a `[DESIGN-SPEC]` issue: a
Figma canvas moves under the spec written from it, so that spec has to freeze what it saw. A
prototype at a commit SHA is already frozen. Nothing here files anything, on any tracker.

## What this replaces, and why it exists

Handing an implementer a preview URL does not work, in two distinct ways, and the brief is
aimed at both:

- **The preview is a built single-page app.** An agent cannot read a spec out of it without a
  browser session, and the spec's own text is inside a bundle.
- **Handing the prototype's source to every implementer** means digesting a 700-line component
  per ticket, every session, non-deterministically — and what came back was a hand-rolled copy
  of the prototype rather than the design-system components that already do the same job.

**The source is read. It is read here, once, by this skill — and only layout facts come out of
it.** The prototype's component file is the only place the exact layout lives: which element
owns the divider, which axis a pair of fields stacks on, which element owns the padding, what a
row contains left to right. Those facts go into `## Fidelity ledger` as words and token names.
Nothing else crosses over: **no control logic, no state handling, no overlay or click-away code,
no `sui-*` class lists copied verbatim, no JSX.** The implementer never opens the prototype
source; the implementer builds each ledger row from design-system components against the facts
in that row.

So an implementer session should open with **facts**: which prototype states are in scope, what
each element's layout actually is, which design-system component each element resolves to and at
what fidelity class, and which prototype behaviours the ticket overrides.

## It asks nothing

**There are no questions in this skill.** Every judgement call becomes a row in the brief,
carrying its confidence, and the grill is where a human answers it. A skill that stops to ask
is a skill nobody runs twice.

The only stops are hard input failures, all in Phase 0 and Phase 1: the URL does not resolve
through the adapter's rule, a named spec file is missing at the pinned SHA, there is no
catalog, or the adapter has no `### Prototype source`. Each says which input failed and what
would fix it. There is no degraded mode and no partial brief.

## Invocation

```
/figma-tools:prototype-to-spec <preview-url> <ticket-ref> [--out <path>]
```

- `<preview-url>` — a deployed preview of the prototype. Required.
- `<ticket-ref>` — the issue or work item this brief is for, as a number or URL. Required; it
  is what the filter runs against, so a brief without one would be the whole spec again.
- `--out` — where the brief goes. Default `<repo-root>/.claude/briefs/<ticket>.md`. The
  project gitignores that directory; the brief is disposable and a committed one is a second
  source of truth with a long half-life.

## Inputs

- **The project adapter**, `<repo-root>/.claude/project/adapter.md`:
  - `## Design system` → `### Prototype source` — the five rows this skill runs on. **Absent
    is a STOP**, and it is the expected one: it means this project's designers ship no code
    prototypes.
  - `## Design system` → the **catalog pointer**, validated exactly as `figma-to-spec` Phase 0
    validates it, and the **usage-rules sources**, which may name several.
  - `## Repo` → the `Tracker:` line, to fetch the ticket, and the **DS-gap backlog**, which
    this skill only ever *names* in a proposed gap row. It files nothing there.
- **The prototype repo**, read-only through `gh`, at one pinned SHA.
- **The catalog**, per `../figma-to-spec/references/catalog-contract.md` — the existence source
  every element and token resolves against, including its `## Idiom mapping` table where the
  overlay has one.
- **The brief's shape**, `references/brief-template.md`.

## Phases

All on the main thread. **No subagents.** The prototype's spec is already structured — there
is nothing to extract, and fanning out over a document that is already a document is the token
burn this skill exists to replace.

| Phase | Does |
|---|---|
| **0 — Resolve** | Adapter rows · catalog validated · ticket fetched. |
| **1 — Locate** | Preview URL → ref and path · resolve the head SHA · fetch every `Spec files:` entry raw at that SHA · download and read the in-scope screenshots. |
| **2 — Filter by ticket** | Keep what the ticket covers; record every drop with its reason. |
| **3 — Overrides** | Render the ticket's divergences on top of the prototype's. |
| **4 — Resolve elements** | Every element and token against the catalog, at three confidences · one fidelity-ledger row per element, with its fidelity class. |
| **5 — Write and stop** | The brief, then the path and the counts. Nothing else. |

### Phase 0 — Resolve

Read the adapter. Establish, and stop on any of them:

1. **`### Prototype source`** — all five rows. Absent sub-section → STOP: *this project has no
   prototype source registered; `install-skills` asks for one.*
2. **The catalog** — resolve through the pointer and validate against the shape contract,
   which is the same gate `figma-to-spec` runs and fails the same way. A directory pointer is
   a split catalog and is read as one document.
3. **The usage-rules sources** — keep all of them, by name. Absent is the answer, not a
   warning: the brief then cites nothing.
4. **The ticket** — fetch it from the tracker the `Tracker:` line names. Its body is the
   filter's input, so a ticket that cannot be fetched is a STOP.

### Phase 1 — Locate, and pin

1. **Apply the `URL → path:` rule** to the preview URL. It yields a **ref** in the prototype
   repo and a **path** within it. Honour the casing rule the row states — a host segment is
   lowercased and a path segment frequently is not, and getting it wrong returns a 404 that
   reads exactly like a spec that was never written.
2. **Resolve the ref to a commit.** Where the rule yields a pull request number:
   `gh pr view <n> --repo <prototype-repo> --json headRefOid,headRefName`. The `headRefOid` is
   the SHA everything else in the run is pinned to.
3. **Fetch every file the `Spec files:` row names**, raw, at that SHA. The row names four kinds
   of file and each is fetched the same way — `gh api repos/<repo>/contents/<path>/<file>?ref=<sha>`
   returns base64 in `.content`, so decode it:

   ```
   gh api repos/<repo>/contents/<path>/<file>?ref=<sha> --jq '.content' | base64 -d
   ```

   1. **The named spec files** — `spec-data.ts`, `HANDOFF.md`, `types.ts`, `README.md`. A named
      file missing at that SHA is a STOP — say which file and which SHA, because the usual cause
      is a `URL → path:` rule that resolved one segment wrongly rather than a genuinely absent spec.
   2. **Every `design_handoff_*/README.md` under the prototype path.** Glob it rather than
      guessing a name: list the directory
      (`gh api repos/<repo>/contents/<path>?ref=<sha> --jq '.[].name'`), keep every entry
      matching `design_handoff_*`, and fetch the `README.md` inside each. **Zero matches is not
      a STOP** — the folder may carry none; record `None` and move on.
   3. **Every source file a `components.new[].codeRef` names.** Parse `spec-data.ts` for the
      `codeRef` string on each `components.new[]` entry and resolve it to a real path under the
      prototype path (a `codeRef` is repo- or folder-relative; try it as given, then relative to
      the prototype path). Fetch each resolved file. A `codeRef` that resolves to nothing is
      **not** a STOP — record it in `## Fidelity ledger` as an unsourced row and carry `OPEN`.
   4. **Every in-scope `components.new[].states` entry's state page.** The states are listed in
      `spec-data.ts`; each has a page at `spec/component-states/<component>/<state>/page.tsx`
      under the prototype path. Fetch the page for every in-scope state, including the states no
      step screenshot shows — the page names the **props the component renders with** in that
      state, and it is the only evidence a state with no PNG has. A state page that resolves to
      nothing is **not** a STOP: the ledger row then cites the component source branch alone and
      still carries `source-only, no screenshot`.
   5. **Every in-scope screenshot** — see step 4 below.

   These source files are read for **layout facts only**, per *What this replaces*. They feed
   `## Fidelity ledger`; no implementation crosses over.

4. **Download and read the in-scope screenshots.** Scope is not known until Phase 2, so do this
   as soon as Phase 2 settles the kept step ids, and before writing anything. For each kept
   `<step-id>`, resolve the `Screenshots:` row's path rule, then:

   ```
   gh api repos/<repo>/contents/<path>/spec/screenshots/<step-id>.png?ref=<sha> --jq '.download_url' \
     | xargs curl -sL -o <scratchpad>/<step-id>.png
   ```

   (The raw URL at the SHA fetched with `curl -sL` is equivalent and is the fallback when the
   contents API elides `download_url` for a large file.) **Then read each downloaded PNG as an
   image** before writing the brief. The screenshot is the arbiter for every layout fact the
   handoff is silent on, and it is what the classification rules in Phase 4 compare a composite's
   default chrome against. A ledger written without the images is a ledger written from names.

   Reading them here does **not** change the rule that the brief *links* screenshots by raw URL
   at the pinned SHA and never embeds them — see *Screenshots are linked, never embedded*. The
   images are read into this session; the brief carries URLs.

   A screenshot missing at the SHA is **not** a STOP: record the row's layout facts from the
   source and the handoff, and mark the ledger row's `States` column `⚠ no screenshot`.

5. **Pin the SHA into the brief's header.** It is this skill's equivalent of `figma-to-spec`'s
   `Extracted against:` line: the brief describes a prototype at a moment, and a brief that
   cannot say which moment cannot be checked against anything later.

The `Schema:` row says what shape the fetched spec is in. **Only one shape is implemented — a
typed spec module plus a handoff document.** A `Schema:` naming anything else is a STOP, not an
invitation to improvise: the row exists so a second shape can be added deliberately later.

### Phase 2 — Filter by ticket

The prototype spec covers a whole flow; the ticket covers a slice of it. Read the ticket for
three things: a **named component or file** (a `Component:` line, or a backticked `X.tsx`), the
**acceptance-criteria text**, and an **overrides or divergence section** where one exists.

With a component named, keep:

| Keep | On what basis |
|---|---|
| `useCases[].steps[]` | the step's `codeRef` names one of the ticket's files |
| `components.new[]` and their `states` | the entry's name is one the ticket names |
| `businessLogic[]` | its `observedIn` intersects a kept step id |
| `responsiveness[]` | its `seenIn` intersects a kept step id |
| `implementationNotes.tokens`, and the handoff document's token table | whole — both are small, and a token dropped for being out of scope is a token the implementer invents |

**Record every dropped step id with the reason it was dropped.** Those go in the brief's
`## Out of scope`, which is not padding: the failure this skill exists to fix produced
implementations of things nobody asked for, because the prototype showed them.

**With no component named**, score instead of guessing. Tokenise the ticket's acceptance
criteria and each step's and rule's title, drop stopwords, and score each step by how many
distinct tokens it shares with the AC text, weighting a token by how *few* steps carry it — a
term appearing in every step separates nothing. Then:

- **Print the whole scored list in the brief**, every step with its score, not just the kept
  ones. The scoring is a guess and showing its working is what makes it checkable in one glance.
- Keep the steps that score above the natural break in the list, and where there is no natural
  break, keep the top-scoring use case whole rather than slicing one down the middle.
- **Mark the `## Scope` section `⚠ inferred`.** Still no question: the grill confirms scope, and
  it will confirm it faster looking at a scored list than at a prompt.

### Phase 3 — Overrides

A ticket that contradicts the prototype **wins, always**, and the brief says so at the point of
contradiction rather than in a preamble. Render the ticket's divergences on top of the
prototype's own annotations:

```
~~the prototype's annotation~~ → overridden by ticket: <the ticket's text>
```

Both halves stay visible. An override with the prototype's text deleted reads as the
prototype's design, and the next person to open the prototype finds a disagreement with no
record of which way it was settled.

### Phase 4 — Resolve elements against the catalog

Three populations, one resolution pass:

1. Every annotation carrying a `component:` tag.
2. Every design-system import the kept prototype code makes.
3. Every **hand-rolled idiom** detectable from a kept `states[].description` — a popover, a
   click-away overlay, a chip row, a date-range editor, a search field. These are the ones that
   matter: the prototype builds them out of primitives because a prototype has no reason not
   to, and an implementer copying it faithfully reproduces a component that already ships.

Propose a design-system mapping for each, using the catalog and — where the overlay has one —
its `## Idiom mapping` table. **Three confidences, and they are the brief's whole interface to
the grill:**

| Confidence | Means | What the grill does |
|---|---|---|
| `exact` | the catalog names this component, or the idiom table has a row for it | treats it as resolved and never asks |
| `likely` | name similarity, or exactly one plausible candidate | one confirm question, batched with the others |
| `OPEN` | nothing in the catalog matches | a round-one question, with the three standard answers |

**Never promote a guess to `exact` to tidy the table.** An `exact` row is never asked about
again, so a wrong one is the only kind of error in this brief that reaches implementation
unchallenged.

**Tokens** resolve against the catalog's tiers the same way `_shared/ui-manifests.md`'s token
manifest does, and a raw `var(--color-x)` with no semantic equivalent is flagged
`⚠ no equivalent, do not invent` — not silently mapped to the nearest thing. The prototype is
allowed to use a raw value; the implementation is not.

**Every `## Tokens` row names the element or elements it applies to**, in its own `Applies to`
column, and the names it writes there are element names the fidelity ledger also uses. A token
row with no element is dead text: nobody can act on it, and the run that produced this rule listed
`sui-text-negative-icon` in the token table while the element that needed it shipped in the wrong
colour. **Remove a token that attaches to no element** rather than carrying it unattached.

**Every `OPEN` row that looks like a genuine design-system gap** also gets a row in
`## DS gaps (proposed, not filed)`, naming the adapter's DS-gap backlog as where it would go.
**Proposing is the whole of it.** Filing is a decision, the grill is where it gets made, and a
gap filed by a skill that asks nothing is a gap nobody agreed to.

#### The fidelity ledger

`## Element → DS mapping` answers *which component*. It does not answer *does that component,
rendered with no arguments, look like the screenshot* — and that is the question a run loses
fidelity on. `## Fidelity ledger` answers it, one row per element, and it sits directly after
`## Element → DS mapping` in the brief.

**An element is a distinct visual thing, not a component.** A container, a row, a divider, an
add row, a value pill, a value-editor list, an editor popover, a search input, a footer action
— each is its own row. One design-system component can appear as the candidate on several rows,
and one row can name several. Do not collapse rows to match a component count.

**One row set per state, not per screenshot.** Emit ledger rows for **every**
`components.new[].states` entry that is in scope — not only for the states a step screenshot
happens to show. A state with no PNG under `spec/screenshots/` is evidenced from two places and
both are read: the state's own page, `spec/component-states/<component>/<state>/page.tsx`, which
says the **props the component renders with** in that state, and the branch of the component
source those props take. Mark every such row `source-only, no screenshot` in the `States` column,
so the grill asks about it rather than inheriting a screenshot's silence. **Per-state conditional
rendering gets its own row**, under the state that toggles it — "subtitle rendered only when ≥1
rule exists", "bordered container rendered only when ≥1 rule exists". A fact of the form *this
element is absent in this state* is a row, never a note appended to another row: a state that
reaches the brief only as a link under `## Component states` reaches implementation as nothing.

**Same element, content differs — one row.** Where two states render the **same** element with
different content — an empty "Any" chip against a row of value chips plus one caret — the ledger
writes **one** row whose layout facts read `same element; content differs: <state A> renders …,
<state B> renders …`. Never two rows with two anatomies. Two anatomies is what makes an
implementer build two components with two tokens and two icons for one design element.

**Write anatomy as nesting, not as a flat list of parts.** Say which parts share one wrapping
flow and which are siblings — "operator, chips and caret sit in one wrapping inline flow; the
label is a fixed sibling column". A flat `icon · label · operator · chips · caret · remove` is
satisfied by six separate columns, and the design frequently has three of them inside one flow.

| Column             | Contents                                                                                                                                                                                                                                                                                                                              |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Element            | the visual thing, in the design's own words                                                                                                                                                                                                                                                                                           |
| States             | the state ids and step ids it appears in; `⚠ no screenshot` where a step's PNG was absent at the SHA; `source-only, no screenshot` for a `states[]` entry that has no PNG at all                                                                                                                                                       |
| Exact copy         | every string, per state — label, placeholder, empty text, button text. Quote it; never paraphrase                                                                                                                                                                                                                                      |
| Tokens             | the semantic tokens the element uses, and — listed separately in the same cell — every raw `var(--color-*)` that still needs a mapping                                                                                                                                                                                                 |
| Layout facts       | in words: nesting (which parts share one wrapping flow), stack direction, full-width or not, divider placement and **which element owns it**, which element owns the padding, and — per icon — **icon name, size and colour token**, and — per text run — its **type token and colour token**                                           |
| Interaction        | which element owns the `onClick` (the click target, named as an element: "the whole value area opens the editor; the chip × removes one value"), plus hover, focus and keyboard behaviour. `—` only where the element is genuinely inert                                                                                               |
| Source             | `components/<file>.tsx:L<start>–L<end>` — where the facts came from. An unresolved `codeRef` reads `— (codeRef unresolved)`; a source-only state also cites its `spec/component-states/**/page.tsx`                                                                                                                                     |
| DS candidate       | the component from `## Element → DS mapping`, or `—`                                                                                                                                                                                                                                                                                  |
| **Fidelity class** | `DS as-is` · `DS with overrides` · `local component` · `DS change` · `OPEN`                                                                                                                                                                                                                                                            |

**An icon written without a name, a size and a colour token is an incomplete row, and so is a
text run written without a type token and a colour token.** Both are invisible in a screenshot at
the sizes a design ships at, and both are the difference between a 14px muted glyph and a 24px
blue one. Read them off the source slice the `Source` column cites.

**The `Interaction` column carries what no screenshot can.** A hotspot, a hover colour, a focus
ring, a keyboard affordance — none of them render in a PNG, all of them live in the source, and
an implementer working from screenshots alone invents them. Name the element that owns the
handler, not the behaviour in the abstract: "the row is the click target", not "the row is
clickable".

##### Classification rules

1. **Composites are never `exact`, and never `DS as-is` without evidence.** A composite is any
   component that ships its own chrome: `MultiSelectPicker`, `Combobox`, `DatePicker`, `Select`,
   `DropdownMenu`, `DataTable`, and **any component whose catalog-overlay entry carries a
   "Default chrome" note**. Such a component may not be given confidence `exact` in
   `## Element → DS mapping`, and may not be given fidelity class `DS as-is` unless rule 2
   produced no difference.
2. **Compare the default chrome against the row's layout facts.** Take the composite's default
   chrome from the overlay's "Default chrome" note for that component; **where the overlay is
   silent, take it from the screenshot** — what the shipped control renders next to what the
   design draws. Then:
   - **No difference** → `DS as-is`.
   - **A difference the component exposes a prop, slot or `className` for** (the overlay's note
     says which chrome is removable) → `DS with overrides`. Name the prop or slot in the notes.
   - **A difference with no prop, slot or `className` path** → `local component`.
   - **A difference that should not be solved locally because the design system itself is wrong
     or missing the affordance** → `DS change`.
3. **Only chromeless primitives may be `exact` and `DS as-is`: `Popover` (the root), `Icon`,
   `Separator`.** They render nothing the caller did not ask for, so name-matching them is safe.
   **`IconButton`, `LabelButton`, `Input`, `Badge` and `PopoverContent` are not on that list** —
   each ships colour, hover, focus, radius, height or padding of its own, and each carries a
   "Default chrome" note in the overlay. They go through rule 2's compare exactly as a composite
   does. A blue-by-default `IconButton` under a design that draws a neutral glyph turning red on
   hover is a difference, and the rule that let it through as `exact` is the rule this one
   replaces.
4. **A `local component` built on a base primitive enumerates that primitive's deltas as
   explicit override instructions.** Replacing a composite with a primitive does not make the
   primitive chromeless. Where a row is `local component` (or `DS with overrides`) on top of a
   base primitive — a local option list on `PopoverContent`, a local pill on `Badge` — the row's
   notes list **every** Default-chrome delta that primitive brings, each as an instruction:
   arrow, width behaviour, radius, padding, max-height and scroll for `PopoverContent`; colour,
   hover, focus ring, size and border for `IconButton`; variant, size, height and hover treatment
   for `LabelButton`; size and shape for `Input`; shape, height, padding and variant colour for
   `Badge`. "Built on `PopoverContent`" is not an instruction; "`arrow={false}`, radius 12px over
   the default, padding 6px over the default `sui-p-2`, add a max-height and scroll on the list
   only" is.
5. **Every row that is not `DS as-is` is a grill question.** Say so in the row's notes, in those
   words. The grill's contract is that it asks about them; the ledger's contract is that it
   marks them.
6. **`## DS gaps (proposed, not filed)` may not read `None` while any row is `local component`
   or `DS change`.** Each such row becomes a DS-gap entry, proposed, not filed — naming the
   adapter's DS-gap backlog as where it would go, per the rule above.

##### Where the facts come from, and who wins

Some prototype folders carry a **designer per-element handoff** — a `design_handoff_*/README.md`
with a "Component mapping" table or per-element px facts. Where one exists:

- **The ledger cites it per row**, by file name, in the `Source` column alongside the `.tsx`
  line range.
- **Its layout facts beat `HANDOFF.md`'s.** `HANDOFF.md` is behaviour and a token table; the
  per-element handoff is the one written against the elements.
- **Where the two disagree on copy, `spec-data.ts` wins**, and the row says so — a per-element
  handoff frequently describes a slightly older variant, so its strings go stale while its px
  facts stay true. Write the winning string in `Exact copy` and note the loser inline.

### Phase 5 — Write the brief, and stop

Write it per `references/brief-template.md` to `--out`, or to the default path. Then print,
per `../_shared/final-prints.md`, exactly two things: **the path**, and **the counts** — steps
kept and dropped, rows at each of the three confidences, and ledger rows at each fidelity class.
Close with the next command.

The brief's content is not summarised into the print. It is a file, one click away, and it is
about to be read by the grill.

## Screenshots are linked, never embedded

Build each step's screenshot URL from the `Screenshots:` row's path rule, **as a raw URL at the
pinned SHA**, and put it in the brief beside the step it belongs to.

The implementer fetches one per state as it builds that state. Embedding them instead would put
every image of a flow into a context that needs one of them at a time, which is the same cost
this skill was written to remove.

**This skill reads them anyway, and that is not a contradiction.** Phase 1 downloads every
in-scope screenshot and reads it as an image, because the fidelity ledger and its classification
rules cannot be written from names. The images land in this session; the brief carries URLs.

## STOP gates

1. **No `### Prototype source` in the adapter** → stop, and name `install-skills` as what adds
   one. This is the expected stop for a project that does not work this way.
2. **The preview URL does not resolve through the `URL → path:` rule** → stop, showing the URL,
   the rule, and how far the match got.
3. **A named spec file is absent at the pinned SHA** → stop, naming the file and the SHA.
4. **No catalog, or a catalog that fails the shape contract** → stop exactly as `figma-to-spec`
   does, naming the resolved path, the rule and the fix.
5. **A `Schema:` naming an unimplemented prototype shape** → stop. Never improvise a reader.

## What this skill does not do

- **It does not file anything.** No issue, no work item, on either tracker. It proposes gaps in
  a brief and stops.
- **It does not write code**, and it does not read the prototype's components to reimplement
  them. It reads the committed spec.
- **It does not persist a spec.** The brief is disposable and the PRD is the durable artifact.
- **It does not ask.** Anything it cannot settle is a row, at a confidence, for the grill.
