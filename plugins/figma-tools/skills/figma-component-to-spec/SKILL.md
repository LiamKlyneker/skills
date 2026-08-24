---
name: figma-component-to-spec
description: >
  Turn one Figma component set into an implementation spec for the design-system
  library that owns the component. Runs only in a `library` repo, refuses anything
  that is not a single component set, and derives the whole variant lattice — axes,
  values, instance counts — from one `get_metadata` on the set root. Reads what the
  component already is source-first, through the adapter's variant-mechanism ladder,
  with a project catalog as optional cross-check rather than a hard requirement.
  Triages every candidate at a human checkpoint into already-expressible /
  extend-component / extend-tokens / fix-figma before a single per-frame extraction
  call is spent, and lets an incomplete input — an undefined Figma variable, a token that
  does not exist yet — ship as a provisional decision carrying one stable id across marker,
  ticket, spec and run record, rather than blocking the run; a later run reads those markers
  back instead of re-asking. Derives the whole spec skeleton from three cheap set-level reads, then
  spends targeted verification extractions on a single-digit shortlist of frames —
  one Sonnet figma-variant-extractor per shortlisted frame, budgeted and throttled
  against the seat's Figma rate ceiling — and files one spec on the adapter's tracker.
  Invoke /figma-tools:figma-component-to-spec <url>.
disable-model-invocation: true
metadata:
  author: liam
  version: "4.2.0"
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
the thing every consumer resolves against. Setup reads the adapter's `Repo role:` row and
hard-refuses on the wrong side of that line, in both directions. There is no run mode, no
flag, and no override that crosses it.

**The delta is against the component, not against a page.** A page spec asks "does this value
exist in the design system?". A component spec asks the harder question — "what does this
component *already do*, and what must change?" — so *Current state* reads it **source-first,
catalog-second**, before any extraction happens. In a library repo the variant declaration in
source **is** the truth and the catalog is a photocopy of it sitting in the same tree, so the
declaration is the primary answer and the catalog is cross-check — and a disagreement between
the two is recorded as a disagreement, never quietly settled.

**A component set is a lattice, not a list of unknowns**, and that is what makes this engine
cheap. One `get_metadata` on the set root returns every variant frame *with its property
assignments* — the whole axis lattice in one response — so the axes, the values, the
drawn-vs-cross-product and the instance counts are all **computed, never observed**, and the
human triage checkpoint sits **before a single per-frame extraction call is spent** rather than
after a hundred of them.

**The lattice is not the only thing that reads at set level, and that is the whole engine.** One
`get_variable_defs` on the same root returns every named token binding across the set in one
small payload, and one wide `get_screenshot` on it returns every variant frame in one image.
Three set-level reads, made once per run, and **the spec skeleton is free** — the axes, the
color schemes, the size ladder and the props API are all written from them before any frame is
read individually. Per-frame extraction stopped being how the spec gets written and became a
**targeted verification pass** over a short list of frames that still hold an open question.

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
- **An existence source (hard requirement) — the *token list*, and no longer necessarily a
  catalog.** Setup assembles one explicit list covering **tokens by tier · typography utilities ·
  dimension tokens · the components this library ships · the icon sources the icon ladder names,
  with their entries**, and hands it verbatim to every extraction spawn. Its primary source is
  the **token source the adapter's *Token pipeline* row names** — that row already answers "where
  do the tokens live", and one file read gives what the catalog was standing in for.
  **What must survive is the guarantee, not the artifact:** the catalog's hard STOP existed to
  keep the extractor **training-blind**, and that needs only *an explicit list the agent may not
  add to*. Without one, nothing stops a spec citing a token from a well-known public design
  system this library never had, and it reads as entirely plausible. So **no existence source at
  all is still a hard STOP**; a missing catalog is not.
- **A project catalog (optional, and demoted rather than banned).** Where one is registered it
  still resolves **passed arg → the adapter's catalog pointer → ask**, is still validated against
  `../figma-to-spec/references/catalog-contract.md` — **the shared file, referenced, never
  copied** — with a **registered** catalog that fails it a hard STOP, and is still soft
  staleness-checked. What changed is its job: it contributes component and icon entries to the
  token list and **cross-checks** the current-state read, rather than being the primary answer to
  either. **The revisit condition is a row read, not a preference:** a *Token pipeline* row
  naming a generator and its source means one read gives the token set and a derived catalog is
  redundant; a row reading `None` means there is no single file whose read gives that set, the
  run reconstructs it across many files every time, and a derived catalog starts paying for
  itself again. `figma-tools:ds-catalog` writes one; this skill never authors one mid-run.
- **Three library-only adapter rows**, all in `## Design system`, none of them inferable from
  the tree:
  - **Variant mechanism** — a **ladder**, read in its order, stopping at the first rung that
    resolves, honouring the trap the row names. It is the **primary** current-state read: where
    this library declares a component's axes and values. Absent → ask; never pick a mechanism by
    looking at the code.
  - **Token pipeline** — **does double duty.** It names the token source Setup reads to build the
    existence list, *and* it decides how literal a token delta may be phrased (a generator and
    its source → a literal source edit; `None` → a coordinated file-edit list). Absent → ask.
  - **Story convention** — where stories live and how their `argTypes` are declared. The
    story-coverage read is scoped by it.
- **Four provisional-decision rows, all optional and all defaulting** — *Gap policy*,
  *Provisional marker*, *Gap tracker*, *Provisional expiry*, in the same `## Design system`
  section. **None of them is a stop and none of them warns**: absent, the run uses the stated
  defaults — token-layer and Figma-side gaps may ship provisionally and API changes may not; the
  marker is `PROVISIONAL(<id>): <what should replace it>`; provisionals file where the spec files;
  nothing is surfaced as overdue. They are **not library-only in principle** — a consumer repo has
  the same problem — which is why they sit outside the library block, even though this skill is the
  only reader today. Setup announces which came from a row and which from a default, because a
  policy the project chose and this skill's opinion are not the same thing to agree to.
- **The rest of `## Design system`**: the **icon resolution ladder** (needed *verbatim* by
  every extraction spawn — the variant agent is deliberately adapter-blind and catalog-blind)
  and the three **class-prefix** rows, which settle what form a spec may recommend and which
  form the token list is written in.
- **Figma MCP — two distinct capability checks, do not conflate them:**
  1. **`figma-dev-mode` present (required):** `get_metadata`, `get_variable_defs`,
     `get_screenshot`, `get_design_context` — the four this run actually calls.
     **`get_screenshot` is part of the capability check**: the cheap pass takes one wide
     set-level shot, and a run that cannot take it loses the visual half of the skeleton and
     must say so up front. STOP if this server is absent — no fallback.
  2. **Binding read (`use_figma`, via `/figma-use`) available (strongly preferred, separate
     server):** resolves each node's `boundVariables` → variable **name per property**. If
     unreachable, the run continues in **degraded color mode**, announced up front, with every
     color flagged unverified. `../../agents/figma-variant-extractor.md` step 3 is the
     **normative** statement of that rule and its `bindingVerified` schema requirement.
- **A Figma node URL** naming **one component set**. Missing → ask, never guess. What counts,
  and what is refused, is Setup's node-shape gate below.
- **A Figma rate ceiling to project against — stated, not discovered.** Phase 5.1 budgets the
  verification pass against it, so the run resolves one before spawning anything: a ceiling
  passed to the run → a ceiling the adapter records, where a project records one → **the stated
  default, `200/day · 20/min`**. The *magnitude* the guard projects is small now — the base is
  the cheap pass's **three set-level reads**, and the fan-out is sized to a **single-digit
  shortlist** rather than to the drawn set — but every property of the ceiling below still holds
  and is still stated out loud. Three of them are carried in Phase 5.1 rather than
  re-derived: it is **org-scoped** (a file owned by a team the seat holds only a *View* membership
  in falls back to a **monthly** allowance in the single or low double digits — a different
  product, not a rate to throttle around); the daily figure is a **recorded disagreement** between
  the seat's own `whoami` (200/day) and Figma's published rate-limits page (600/day for
  Organization), taken at the lower, live-authority value; and **`use_figma`'s quota status is
  unknown** — it appears on that page neither as exempt nor as counted. `whoami` is itself
  rate-limit-exempt, so confirming a seat's real ceiling is free.
- **`figma-variant-extractor` subagent (preferred, detachable).** This skill's own agent, at
  `../../agents/figma-variant-extractor.md`, spawned as
  **`figma-tools:figma-variant-extractor`** — the plugin namespaces it, on every route,
  installed or `--plugin-dir`. There is no unprefixed form except a hand-placed `agents/` file.
  If the type does not resolve, the extraction phase reads that same file and pastes its body
  into a `general-purpose` agent. One source of truth either way; Setup checks and announces
  which path the run takes. The page-side `figma-region-extractor` is `figma-to-spec`'s and is
  deliberately **not** checked here — spawning it would hand a page contract a variant frame.

## Resolution sources (what "does it exist?" reads)

- **Existence** → the **token list Setup assembles** and hands to every spawn. The ONLY source
  for "does the DS have this?" — including for the component under spec. Its parts: tokens,
  typography utilities and dimension tokens from the **token source the *Token pipeline* row
  names**; the components this library ships and the icon sources' entries from the catalog where
  one is registered, and otherwise enumerated once from the library itself. A part with no
  resolvable source is written into the list as `none resolvable — <why>` and announced, never
  left out — an omitted part and an empty one read identically to the agent.
- **Catalog shape** (where a project registers one) →
  `../figma-to-spec/references/catalog-contract.md` (shared with `figma-to-spec` and
  `ds-catalog`; one file, three readers).
- **Resolution + tolerance rules** → `../figma-to-spec/references/resolution-rules.md`
  (shared, same rule).
- **Current state of the component** → **source first, catalog second.** The variant declaration
  in source is the primary statement of what axes and values exist, read by walking the adapter's
  **variant mechanism** ladder in its order, stopping at the first rung that resolves and
  honouring the trap the row names. The catalog is **cross-check**: agreement is recorded once as
  cross-checked, and a disagreement is **recorded as a disagreement**, never silently resolved in
  either direction — one of the two is wrong, and deciding which is the human's call at the
  triage checkpoint. This phase makes **no Figma call at all**.

**Component identity is looked up, not inferred, wherever it can be.** In a library repo the
component being drawn usually *is* an entry in the token list, so match the component set to that
entry and confirm it with the user when the match is anything less than obvious. Where no entry
matches, that is the interesting case — a genuinely new component — and it is recorded as such,
never forced onto the nearest name.

## What triage decides, and where the spec lands

**Four outcomes, and they are about *where the edit lands*.** At the *Reconcile & triage*
checkpoint — which sits **before any per-frame extraction call**, not after the fan-out — every
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

**A fifth thing is decided there, and it is a modifier rather than an outcome.** The four answer
*where does the edit land?*; **provisional** answers *do we ship now?*, so it rides on top of an
outcome instead of replacing one. **`extend-tokens` and `fix-figma` accept it — a colour or a
dimension is cheap and reversible. `extend-component` never does** — a variant axis or a props-API
change is what consumers write against, and it cannot be taken back without a breaking change.
`already-expressible` has nothing to be provisional about. That is the whole per-kind policy, and
the adapter's *Gap policy* row may widen or narrow it.

A provisional ships a chosen value with a **named replacement** and one **stable id** —
`prov-<component>-<what it decides>`, derived so run five re-derives it identically — carried
across four surfaces: the marker comment at the point of use, the tracker item, the spec's
*Provisional decisions* index, and the run record. All four or none. **The row stays in whichever
section its outcome put it in**; the index cross-references it rather than taking it, so a
provisional Figma gap is still designer work in *Figma fixes*.

**This skill specs the marker and never places it** — it writes no component code, so the
implementer places it. Which is why the spec's index, not the marker, is the record that exists
from run 1.

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
Variant agents are driven by `../../agents/figma-variant-extractor.md`; the run's one artifact is
shaped by `references/component-spec-template.md`.

**Every phase up to and including the triage checkpoint runs before a single per-frame extraction
call is spent**, and the whole run's Figma cost up to the checkpoint is **three set-level
reads** — three, and never more than three — fixed regardless of how many variants the set draws.
That the number is **independent of N** is what makes the guarantee worth stating: a set drawing
120 frames costs the same three reads as one drawing four.

| Phase | Model | Does |
|---|---|---|
| **1 — Setup** | main thread | **Repo-role guard** · **node-shape gate** (one component set) · **the three set-level reads**, and never more than three: root `get_metadata` (shape + the whole lattice), root `get_variable_defs` (every named binding across the set), one wide root `get_screenshot` · **assemble the token list** from the *Token pipeline* row's source (catalog, where registered, validated + soft staleness-checked and contributing component/icon entries) · read the `## Design system` rows this skill needs · three Figma capability checks · identify the component under spec. |
| **1.5 — Cheap pass** | Opus, main thread, **no subagents** | Turn Setup's three set-level reads into the **spec skeleton**, **decomposed by axis and never by cell**: N color schemes + M sizes + K state deltas, each stated once. Bind every value to a named token where the dump supplies one, mark anything derived from a token *name* as **inference**, and flag the anomalies the dump can see. **Zero further Figma calls, and no subagent.** |
| **2 — Structure** | main thread | Derive the whole axis lattice from Setup's root response — drawn axes and values, drawn-vs-cross-product, duplicate/inconsistent Figma property values, the Figma vocabulary kept **verbatim**, and instance counts **computed, not observed**. Coverage self-check + logged tally. **Zero Figma calls of its own.** |
| **3 — Current state** | main thread | What the component already is — **source-first** through the variant-mechanism ladder, naming the file it resolved at; the catalog as **cross-check** with every disagreement recorded unresolved; **every prior provisional marker read back and cross-checked against the filed spec** (§3.4, the read that makes a re-run cheap); plus computable story coverage. **No Figma calls.** |
| **4 — Reconcile & triage** | Opus, main thread | One axis table (delta both ways, axis-name mapping as a claim) · the candidate list with every ⚠️ flag joined in and the lattice's instance counts · **four-outcome triage checkpoint plus the provisional modifier, before any per-frame extraction, run as an interview** — settled-by-the-run stated up front (**including every prior provisional, never re-asked**), then the open questions in **dependency-ordered rounds** — numbered, grounded, a recommendation each, never a table to mark up — the **shortlist** of frames worth verifying as the closing question. |
| **5 — Targeted verification** | `figma-tools:figma-variant-extractor` (Sonnet) ×K, **throttled** | **Budget guard first**: project the metered cost from the **shortlist** size and the agent's call discipline, state it against the seat's daily ceiling, and **stop deliberately** rather than die mid-fan-out. Then one agent per **shortlisted** variant frame — spawned to **verify the skeleton's slice for that frame**, not to re-derive it → structured JSON findings, resolved against the token list pasted verbatim into each spawn, fanned out in **waves** sized for the per-minute cap. A shortlist of **zero** is a valid, complete run. |
| **6 — Reconcile by concern** | Opus, main thread | Make each concern consistent across the skeleton and the verified frames — one color→token map, one type/spacing picture, one icon inventory. Where a verification finding contradicts the skeleton, **the finding wins and the contradiction is recorded**. A finding that creates a **new, untriaged candidate** goes back to the user as a short follow-up interview before the spec is written; zero new candidates → no follow-up. No Figma re-traversal. |
| **7 — Pattern precedent** | research subagents (Sonnet) | One per **extend-component** gap — **that outcome only** — APG → headless libraries → shadcn, walked in full. Spends **no Figma call**, so it runs **in parallel with Phase 5** and never enters its budget. |
| **8 — The component spec** | Opus, main thread | Write **one** component spec per `references/component-spec-template.md`, including the **extraction-coverage disclosure**: which sections the cheap pass wrote, which frames were verified, which deliberately were not, and every instance count marked **computed from the lattice**. `0 of N` is disclosed honestly, as a complete spec rather than an empty one. |
| **9 — Filing** | main thread | Branch on the adapter's `Tracker:` line. The spec files as a plain `[SPEC]` work item (ADO) / an ordinary issue (GitHub) on **this repo's own tracker rows**, parented to the scope ticket where one was given, deduped by the component set's node id and updated in place. **One item per provisional** on the *Gap tracker* row's target, deduped on its slug — so a second run creates zero new items of either kind. |

(A catalog that has drifted from the design system, or a project that wants one: author or
refresh it with `figma-tools:ds-catalog`, then re-run Setup. Its **absence** no longer stops a
run — the token list does.)

**Two species of stop, and only one of them is real.** A gate belongs on this list when **the run
cannot produce anything valid** — the wrong repo, the wrong node, no capability, no existence
source, a cost that would die mid-fan-out. Those stay hard, because a spec written with no
existence source is a spec that invents token names.

**An incomplete *input* is not one of them.** Figma has not defined a variable yet; a token does
not exist on this side; Figma and the code disagree; the file carries two generations of variable
names at once. Those are not "the run is invalid" — they are the normal state of every real design
file, and blocking there is what stops anyone running this on component two. They resolve into
**provisional decisions** (Phase 4.3), not stops. The one input gap that still earns a stop is a
change to the **component's API**, because consumers write against it.

**STOP gates — none of these is automatable:**

1. **`Repo role:` is `consumer`, or the row is absent** → stop, with a one-line redirect to
   `figma-tools:figma-to-spec`. Before any Figma read. Not a warning, not overridable
   (Setup step 1).
2. **The node is not one component set** → stop: *one component set per run*. A page-shaped
   node and a node holding several component sets are both refused **by decision, not by
   omission**. A lone component is fine — it is the 1-variant case (Setup step 2).
3. **`figma-dev-mode` absent** → stop. There is no fallback (Setup step 5).
4. **No existence source resolves at all** — no token source behind the *Token pipeline* row, no
   registered catalog, nothing enumerable → stop, naming each thing looked for and where (Setup
   step 3c). Separately: a **registered** catalog that fails
   `../figma-to-spec/references/catalog-contract.md` → stop, naming the path and the rule that
   failed (Setup step 3d). Staleness alone never stops a run, and a *missing* catalog is not a
   stop.
5. **No variant-mechanism ladder in the adapter** → ask the user for it; never infer the
   mechanism from the code. `ds-catalog` is what writes the row (Setup step 4).
6. **Human triage checkpoint** (Phase 4.3) → **an interview, not a form**: present the candidate
   map once, state what the run's own reads already settled (reopenable, never re-asked), then
   ask the open questions in **dependency-ordered rounds** — numbered, each grounded in quoted
   evidence, each with a recommended answer, and never a table to mark up — until every candidate
   is marked
   **already-expressible** / **extend-component** / **extend-tokens** / **fix-figma**, every
   legacy flag (match-as-is vs modernize) and every catalog-vs-source disagreement is settled,
   and anything the run surfaced that this skill has no rule for has been asked, never silently
   dropped. **Every decision records a one-line rationale** — the user's answer as given — in
   the spec's *Triage record*, and the shortlist is the closing question.

   **This is the gate the provisional modifier shrinks.** Every candidate still gets exactly one
   of the four outcomes, and an eligible one may additionally be marked **provisional** — a value
   shipped now, a replacement named, an id issued. `extend-tokens` and `fix-figma` are eligible;
   **`extend-component` never is, and that is the stop that is still earned.** Decisions a prior
   run already settled are **stated in the opening "settled by the run" list and not re-asked** —
   without that, run five costs what run one cost.

   Two negatives hold at this gate: **no tracker write has happened** — not a write, not a draft,
   and no search that is a step toward one, on either tracker, with **one named read-only
   exception**: Phase 3.4's fetch of the already-filed spec, which creates nothing and is what
   makes the re-read possible — and **no per-frame extraction call has been spent** (the three
   set-level reads are the fixed pre-checkpoint cost).
7. **The projected metered cost exceeds the ceiling** (Phase 5.1) → stop **before the first
   spawn**, naming the shortlist size, the floor and worst-case projections, the ceiling and
   where it came from, and how many frames would fit — then re-triage narrower. Exceeding a Figma
   rate limit is a hard stop with **no documented retry-after**, so a run that discovers the
   ceiling by hitting it dies mid-fan-out with a partial verification and a day's wait. Verifying
   a prefix of the shortlist and stopping half-way is **not** an alternative: it produces a spec
   whose *Token delta* and *Figma fixes* omit whatever the budget ran out before reaching, which
   is indistinguishable from a component that had no findings there. A shortlist that projects
   over the ceiling at these sizes is usually a triage that was not done — single digits is the
   target, and dozens is the signal to re-triage rather than to buy budget.

The four extraction rules the regression fixtures protect apply here unchanged — **never
resolve a fill by hex**, **never record absolute x/y coordinates**, **never match across
property kinds**, **never enumerate the interior geometry of an icon** — and they are normative
in `../../agents/figma-variant-extractor.md` and
`../figma-to-spec/references/resolution-rules.md`, never restated here.

## Idempotency & output

Re-running re-derives everything from the node: extraction is a pure function of the component
set plus the token list. Filing dedups by **searching the filing target for the component set's
node id** — never by title, because a component gets renamed — and **updates the existing item
in place**, writing its id back into the spec. A second run on the same component set creates
**zero** new tracker items, and that now covers provisional items too — they dedup on their own
slug, which is derived rather than counted for exactly this reason.

**What a re-run must not do is re-ask.** Phase 3.4 reads back every provisional marker in the repo
and cross-checks it against the filed spec's index; the survivors are **stated as settled** at the
checkpoint rather than put up again. That read costs nothing — Phase 3 makes no Figma call — and it
is what keeps run five cheaper than run one. A run that re-opens settled decisions is a run people
start clicking through, which is the same argument that made *Triage record*'s rationale mandatory.

Write under a run directory (suggest the scratchpad or a user-named dir): **one
`component-spec.md`, and nothing else**. There is deliberately **no `gaps/` directory** — in a
library the gap and the spec are the same document, so every gap is a section of the spec and its
rationale a row in *Triage record*. A second artifact would give one decision two homes that can
disagree.

Screenshots **are** taken and are **not** persisted. The cheap pass takes **one wide set-level
shot** in Setup, and the orchestrator takes a **targeted shot only where a specific question
needs pixel evidence** — each one justified out loud. **The variant agent takes none**: visual
evidence is the orchestrator's, because `get_screenshot` **does not upscale** — a 48px node
renders at 48px — so a wide set-level shot carries far more information per token than any
per-variant shot, and a single-node shot must be **upscaled locally** to be readable at all. The
layout tree plus auto-layout intent remain the durable truth; the image is evidence, not the
record.

## What this skill verifies vs what it cannot

It verifies that every child of the component set landed in the lattice or was explicitly pruned
with a reason, that every design property it did extract was **resolved** against the token list,
and that the component's current state was read through the adapter's stated mechanism rather
than guessed. **It does not claim every variant frame was verified** — verification is scoped to
the shortlist triage kept, deliberately, and the spec says which frames those were.

**What the verification pass exists to cover is a fixed list, because the cheap pass has five
known blind spots and only these five:**

1. **Unbound raw-hex fills** — invisible in a variable dump, which by construction lists only what
   *is* bound. Catching them is the whole point of the spec's *Figma fixes* section and the most
   dangerous of the five.
2. **Which layer of which frame binds which token** — a name implies an attribution; it does not
   confirm one.
3. **Icon and frame geometry** — sizes, auto-layout, padding, stroke alignment.
4. **Per-cell consistency** — a frame labelled `Size=medium` that is actually 36px.
5. **Effects** beyond what the variable dump lists.

**A value taken from a token *name* rather than from a per-property binding is inference, and it
is flagged as inference** — in the skeleton, in the findings, and in the spec. It is usually
right, which is exactly why an unflagged one is dangerous: nobody re-checks a value that reads
as verified.

**It does not claim the component came out perfect, and it never could** — no real Figma file is
complete, and a skill whose value rested on that claim would fail on the first one it met. What it
does claim is narrower and holds: **every deviation from the design is recorded, attributed and
findable**, from the marker, the ticket, the spec or the run record. So the number to watch is not
how few provisionals a run produced — it is **how many unmarked deviations there are**, and that
one can genuinely be zero.

It cannot verify that the design is right, that an inferred component identity is correct
without the user's yes, or that the eventual code renders faithfully. **Nor does it verify a
precedent it cites** — the research subagent reports what published sources say about a
component class, which is evidence for an API shape and never proof that the shape fits this
library; the deviations line exists for exactly that gap. One limit is specific to
this skill and worth saying plainly: **story coverage is only as computable as the story
convention allows.** An axis whose `argTypes` entry is not a select is reported *not computable
— verify manually*, and never guessed at from story export names, which are proven unreliable
as a coverage signal.

The regression **fixture format** and **expected-findings assertion style** live in
`references/regression/`; concrete fixtures are per-project (they pin real node IDs, and are
graded against one library's conventions) and are optionally registered in the adapter.
Re-running them is a **documented pre-release step** — triggered by any change to an extraction,
enumeration or triage rule, before that change ships — and explicitly **not CI**, which cannot
drive a live authenticated Figma session.
