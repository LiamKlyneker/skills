---
name: prototype-to-spec
description: >
  Turn a designer-authored code prototype into a design brief for one ticket. Resolves
  a preview URL to a pinned commit in the prototype repo, reads the spec committed
  there, filters it to what the ticket covers, renders the ticket's overrides on top,
  and resolves every element and token against the project's design-system catalog.
  Asks nothing — every judgement becomes a row the grill can question.
  Invoke /figma-tools:prototype-to-spec <preview-url> <ticket>.
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
- **Reading the prototype's source instead means digesting a 700-line component per ticket**,
  every session, non-deterministically — and what came back was a hand-rolled copy of the
  prototype rather than the design-system components that already do the same job.

So an implementer session should open with **facts**: which prototype states are in scope,
which design-system component each element resolves to, and which prototype behaviours the
ticket overrides.

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
| **1 — Locate** | Preview URL → ref and path · resolve the head SHA · fetch the spec files raw at that SHA. |
| **2 — Filter by ticket** | Keep what the ticket covers; record every drop with its reason. |
| **3 — Overrides** | Render the ticket's divergences on top of the prototype's. |
| **4 — Resolve elements** | Every element and token against the catalog, at three confidences. |
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
3. **Fetch each file the `Spec files:` row names**, raw, at that SHA:
   `gh api repos/<repo>/contents/<path>/<file>?ref=<sha>`. A named file missing at that SHA is
   a STOP — say which file and which SHA, because the usual cause is a `URL → path:` rule that
   resolved one segment wrongly rather than a genuinely absent spec.
4. **Pin the SHA into the brief's header.** It is this skill's equivalent of `figma-to-spec`'s
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

**Every `OPEN` row that looks like a genuine design-system gap** also gets a row in
`## DS gaps (proposed, not filed)`, naming the adapter's DS-gap backlog as where it would go.
**Proposing is the whole of it.** Filing is a decision, the grill is where it gets made, and a
gap filed by a skill that asks nothing is a gap nobody agreed to.

### Phase 5 — Write the brief, and stop

Write it per `references/brief-template.md` to `--out`, or to the default path. Then print,
per `../_shared/final-prints.md`, exactly two things: **the path**, and **the counts** — steps
kept and dropped, and rows at each of the three confidences. Close with the next command.

The brief's content is not summarised into the print. It is a file, one click away, and it is
about to be read by the grill.

## Screenshots are linked, never embedded

Build each step's screenshot URL from the `Screenshots:` row's path rule, **as a raw URL at the
pinned SHA**, and put it in the brief beside the step it belongs to.

The implementer fetches one per state as it builds that state. Embedding them instead would put
every image of a flow into a context that needs one of them at a time, which is the same cost
this skill was written to remove.

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
