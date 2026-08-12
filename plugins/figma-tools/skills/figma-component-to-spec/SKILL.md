---
name: figma-component-to-spec
description: >
  Turn one Figma component set into an implementation spec for the design-system
  library that owns the component. Runs only in a `library` repo, refuses anything
  that is not a single component set, fans each variant frame out to a Sonnet region
  agent, reads what the component already is — catalog-first, source-second — via the
  adapter's variant-mechanism ladder, triages every gap at a human checkpoint into
  already-expressible / extend-component / extend-tokens / fix-figma, and files one
  spec on the adapter's tracker.
  Invoke /figma-tools:figma-component-to-spec <url>.
disable-model-invocation: true
metadata:
  author: liam
  version: "2.1.0"
---

# Figma component → Spec

Turn one Figma **component set** into **one component spec**: what the component's variant
axes and values must become, expressed against the design system this repo *is*.

**This skill is a spec producer, not a builder.** It never writes component code, never edits
a `cva()` call, never adds a token. Its single deliverable is **one component spec per
component set** — implemented later by whatever the adapter's `## Design system` →
*downstream implementer* row names, and by a human where that row is absent.

**It is the `library`-side twin of `figma-tools:figma-to-spec`, and the two are mutually
exclusive by repo.** `figma-to-spec` specs a **page** in a repo that *consumes* a design
system and files gaps against it. This skill specs a **component** in the repo that *is* the
design system, where a spec does not file a gap against someone else's library — it changes
the thing every consumer resolves against. Phase 0 reads the adapter's `Repo role:` row and
hard-refuses on the wrong side of that line, in both directions. There is no run mode, no
flag, and no override that crosses it.

**The delta is against the component, not against a page.** A page spec asks "does this value
exist in the design system?". A component spec asks the harder question — "what does this
component *already do*, and what must change?" — so Phase B reads the component's current
state alongside the Figma side, **catalog-first, source-second**. The fingerprinted catalog is
the primary answer; source is fallback and cross-check, never a second derivation racing the
first.

## Prerequisites

Depends on **inputs and capabilities**, not on sibling skills being invokable — the same
detachability rule as `figma-to-spec`. What a session can invoke depends on which plugins that
machine has installed and where the session is rooted.

- **`Repo role: library` in the project adapter (hard requirement).** `## Design system`'s
  `Repo role:` row. **An absent row reads as `consumer`** — every adapter written before that
  row existed belongs to a consumer repo — so an install that never gained the row is not
  broken, it simply is not a library, and this skill refuses there. The role is an **intent,
  never inferred**: a `components/` directory is not evidence, and neither is a package name.
  No adapter or no `## Design system` section at all is a different failure — that is a
  missing install, and the answer is `install-skills`, not a guess.
- **A project design-system catalog (required artifact).** Same existence source, same shape
  contract, same resolution order as `figma-to-spec`: **passed arg → the adapter's catalog
  pointer → ask**, stopping there. Its required shape is
  `../figma-to-spec/references/catalog-contract.md` — **the shared file, referenced, never
  copied**. Phase 0 validates against it and **fails loudly** rather than degrading; staleness
  is a separate soft check. In a library repo the catalog describes *this* repo's own design
  system, which makes it both more likely to be current and more consequential when it is not —
  it stays a soft check either way. A project without a catalog gets one from
  **`figma-tools:ds-catalog`**; this skill never authors one mid-run.
- **Three library-only adapter rows**, all in `## Design system`, none of them inferable from
  the tree:
  - **Variant mechanism** — a **ladder**, read in its order, stopping at the first rung that
    resolves, honouring the trap the row names. It is what tells Phase B where this library
    declares a component's axes and values. Absent → ask; never pick a mechanism by looking at
    the code.
  - **Token pipeline** — decides how literal a token delta may be phrased (a generator and its
    source → a literal source edit; none → a coordinated file-edit list). Recorded in this
    slice; consumed when the spec is written.
  - **Story convention** — where stories live and how their `argTypes` are declared. Phase B's
    story-coverage read is scoped by it.
- **The rest of `## Design system`**: the **icon resolution ladder** (needed *verbatim* by
  every Phase B spawn — the region agent is deliberately adapter-blind) and the three
  **class-prefix** rows, which settle what form a spec may recommend.
- **Figma MCP — two distinct capability checks, do not conflate them:**
  1. **`figma-dev-mode` present (required):** `get_metadata`, `get_variable_defs`,
     `get_screenshot`, `get_design_context`. STOP if this server is absent — no fallback.
  2. **Binding read (`use_figma`, via `/figma-use`) available (strongly preferred, separate
     server):** resolves each node's `boundVariables` → variable **name per property**. If
     unreachable, the run continues in **degraded color mode**, announced up front, with every
     color flagged unverified. `../../agents/figma-region-extractor.md` step 4 is the
     **normative** statement of that rule and its `bindingVerified` schema requirement.
- **A Figma node URL** naming **one component set**. Missing → ask, never guess. What counts,
  and what is refused, is Phase 0's node-shape gate below.
- **`figma-region-extractor` subagent (preferred, detachable).** The same agent
  `figma-to-spec` spawns, at `../../agents/figma-region-extractor.md`, spawned as
  **`figma-tools:figma-region-extractor`** — the plugin namespaces it, on every route,
  installed or `--plugin-dir`. There is no unprefixed form except a hand-placed `agents/` file.
  If the type does not resolve, Phase B reads that same file and pastes its body into a
  `general-purpose` agent. One source of truth either way; Phase 0 checks and announces which
  path the run takes.

## Resolution sources (what "does it exist?" reads)

- **Existence** → the project **catalog**, resolved and validated in Phase 0. The ONLY source
  for "does the DS have this?" — including for the component under spec.
- **Catalog shape** → `../figma-to-spec/references/catalog-contract.md` (shared with
  `figma-to-spec` and `ds-catalog`; one file, three readers).
- **Resolution + tolerance rules** → `../figma-to-spec/references/resolution-rules.md`
  (shared, same rule).
- **Current state of the component** → **catalog first, source second.** The catalog entry is
  the primary statement of what axes and values exist. Source is fallback where the catalog is
  silent, and cross-check where it is not — read by walking the adapter's **variant mechanism**
  ladder, in its order. A source read that disagrees with the catalog is **recorded as a
  disagreement**, never silently preferred: one of the two is wrong, and deciding which is the
  human's call in Phase C.

**Component identity is looked up, not inferred, wherever it can be.** In a library repo the
component being drawn usually *is* a catalog entry, so match the component set to that entry
and confirm it with the user when the match is anything less than obvious. Where no entry
matches, that is the interesting case — a genuinely new component — and it is recorded as such,
never forced onto the nearest name.

## What triage decides, and where the spec lands

**Four outcomes, and they are about *where the edit lands*.** At the Phase C checkpoint every
candidate is marked **already-expressible** (the library already says it — record how, change
nothing) · **extend-component** (a variant axis, a value, or a props-API change) ·
**extend-tokens** (through the adapter's token pipeline) · **fix-figma** (an unbound or raw value
in the **Figma library itself** — designer-side work, riding the same tracker item, and never
written into a code section).

They are **not** a relabelling of `figma-to-spec`'s three. That checkpoint asks *is this
genuinely reusable across the product, or one-off to this design?* — a question that answers
nothing in the repo that *is* the design system, where everything is reusable by definition,
there is nobody to escalate to, and "build it locally" and "extend the component" are the same
act. The consumer set stays where it is, in
`../figma-to-spec/references/resolution-rules.md` → `## Triage outcomes`: **referenced, never
edited**, because it is shared and consumer-mode-normative.

**Only extend-component triggers pattern research** — the ladder **ARIA APG → headless libraries
→ shadcn**, one subagent per gap, landing as the spec's *Pattern precedent* section. It is the
only outcome that invents API surface, and a props API specced from one variant frame is a guess
wearing a spec's clothes. A gap with no precedent found **says so**; an invented one launders a
guess as an industry standard.

**The spec files as a plain `[SPEC]` work item (ADO) or an ordinary issue (GitHub), on this
repo's own `## Repo` rows** — not the `Design-spec target` / `DS-gap backlog` rows, which are
`figma-to-spec`'s and answer nothing here. **The design-spec prefix that skill files under is
never written by this one**, on either tracker: it marks a spec whose implementer is somewhere
else, and a component spec filed under it is invisible to the slicing chain that would pick it
up — a dead end that looks exactly like a
successful run. Filing the right type in the first place is what lets `ado-workflow:to-spec-tasks`
and `prd-workflow:to-issues` consume it with **zero new machinery and no edit to either plugin**.

## Phases

Read `references/phases.md` for the phase you are running — it carries the full procedure.
Region agents are driven by `../../agents/figma-region-extractor.md`; the run's one artifact is
shaped by `references/component-spec-template.md`.

| Phase | Model | Does |
|---|---|---|
| **0 — Setup** | main thread | **Repo-role guard** · **node-shape gate** (one component set) · resolve catalog (arg → adapter pointer → ask) + validate against the shape contract + soft staleness check · read the `## Design system` rows this skill needs · three Figma capability checks · identify the component under spec. |
| **A — Variants are the regions** | main thread | Enumerate the component set's variant frames. One variant frame = one region = one `variant:<name>` source-node role. Coverage self-check + logged tally. |
| **B — Variant agents + current state** | `figma-tools:figma-region-extractor` (Sonnet) ×N parallel, plus main thread | One agent per variant frame → structured JSON findings. In parallel, on the main thread: what the component already is — **catalog-first, source-second** via the variant-mechanism ladder — plus computable story coverage. |
| **C — Synthesis, triage & the spec** | Opus, main thread (+ research subagents) | Reconcile the two reads into one axis table · reconcile by concern · **four-outcome triage checkpoint** · **pattern-precedent research** per extend-component gap (APG → headless → shadcn) · write **one** component spec per `references/component-spec-template.md`. |
| **D — Filing** | main thread | Branch on the adapter's `Tracker:` line. The spec files as a plain `[SPEC]` work item (ADO) / an ordinary issue (GitHub) on **this repo's own tracker rows**, parented to the scope ticket where one was given, deduped by the component set's node id and updated in place. |

(No catalog, or one that has drifted from the design system: author or refresh it with
`figma-tools:ds-catalog`, then re-run Phase 0.)

**STOP gates — none of these is automatable:**

1. **`Repo role:` is `consumer`, or the row is absent** → stop, with a one-line redirect to
   `figma-tools:figma-to-spec`. Before any Figma read. Not a warning, not overridable
   (Phase 0 step 1).
2. **The node is not one component set** → stop: *one component set per run*. A page-shaped
   node and a node holding several component sets are both refused **by decision, not by
   omission**. A lone component is fine — it is the 1-variant case (Phase 0 step 2).
3. **`figma-dev-mode` absent** → stop. There is no fallback (Phase 0 step 5).
4. **No resolvable catalog, or one that fails
   `../figma-to-spec/references/catalog-contract.md`** → stop, naming the path and the rule
   that failed. (Staleness alone never stops a run.)
5. **No variant-mechanism ladder in the adapter** → ask the user for it; never infer the
   mechanism from the code. `ds-catalog` is what writes the row (Phase 0 step 4).
6. **Human triage checkpoint** (Phase C4) → present every candidate and flag; the user marks each
   **already-expressible** / **extend-component** / **extend-tokens** / **fix-figma**, settles
   every legacy flag (match-as-is vs modernize) and every catalog-vs-source disagreement, and
   **every decision records a one-line rationale** in the spec's *Triage record*. **No tracker
   write happens before this** — not a search, not a draft — on either tracker.

The four extraction rules the regression fixtures protect apply here unchanged — **never
resolve a fill by hex**, **never record absolute x/y coordinates**, **never match across
property kinds**, **never enumerate the interior geometry of an icon** — and they are normative
in `../../agents/figma-region-extractor.md` and
`../figma-to-spec/references/resolution-rules.md`, never restated here.

## Idempotency & output

Re-running re-derives everything from the node: extraction is a pure function of the component
set plus the catalog. Filing dedups by **searching the filing target for the component set's
node id** — never by title, because a component gets renamed — and **updates the existing item
in place**, writing its id back into the spec. A second run on the same component set creates
**zero** new tracker items.

Write under a run directory (suggest the scratchpad or a user-named dir): **one
`component-spec.md`, and nothing else**. There is deliberately **no `gaps/` directory** — in a
library the gap and the spec are the same document, so every gap is a section of the spec and its
rationale a row in *Triage record*. A second artifact would give one decision two homes that can
disagree.

Screenshots are **not** persisted — `get_screenshot` returns an inline image, not a path.
Variant agents view it inline; the layout tree plus auto-layout intent are the durable truth.

## What this skill verifies vs what it cannot

It verifies that every variant frame in the component set was extracted or explicitly pruned,
that every design property was **resolved** against the catalog, and that the component's
current state was read through the adapter's stated mechanism rather than guessed.

It cannot verify that the design is right, that an inferred component identity is correct
without the user's yes, or that the eventual code renders faithfully. **Nor does it verify a
precedent it cites** — the research subagent reports what published sources say about a
component class, which is evidence for an API shape and never proof that the shape fits this
library; the deviations line exists for exactly that gap. One limit is specific to
this skill and worth saying plainly: **story coverage is only as computable as the story
convention allows.** An axis whose `argTypes` entry is not a select is reported *not computable
— verify manually*, and never guessed at from story export names, which are proven unreliable
as a coverage signal.
