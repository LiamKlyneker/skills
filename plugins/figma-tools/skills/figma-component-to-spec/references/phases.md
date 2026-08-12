# Phase bodies

The full procedure for each phase of `figma-component-to-spec`. SKILL.md carries the contract,
the model tiers, the phase overview, and the STOP gates; load the section here for the phase
you are running.

Normative elsewhere, never restated here: the region-agent extraction contract and the
`bindingVerified` / degraded-color-mode rules live in
`../../../agents/figma-region-extractor.md`; resolution and tolerance rules in
`../../figma-to-spec/references/resolution-rules.md`; the required shape of a project catalog
in `../../figma-to-spec/references/catalog-contract.md`; existence itself in the project
catalog Phase 0 resolves. Those three files are **shared with `figma-to-spec` and
`ds-catalog`** — read them at those paths. A second copy of a contract is the failure this
plugin's layout exists to prevent.

---

## Phase 0 — Setup (main thread)

1. **Repo-role guard — first, before any Figma read, and it is a STOP.**

   Read `<repo-root>/.claude/project/adapter.md`, `## Design system`, the `Repo role:` row.

   - `library` → continue.
   - `consumer`, **or no `Repo role:` row at all** → **stop**, with one line and nothing else:

     > This repo's `Repo role:` is `consumer` (an absent row means `consumer`), so a component
     > spec written here would edit a design system this repo only consumes. Use
     > `figma-tools:figma-to-spec` instead.

     Do not read a Figma node first, do not offer a `--force`, and do not offer to write the
     row as part of this run. The role is an **intent** and the row is the record of it; a
     skill that flips it to keep itself runnable has removed the only guard there is. If the
     user believes this really is a library repo, the fix is to set the row — via
     `install-skills` or `ds-catalog` — and re-invoke.
   - **No adapter, or no `## Design system` section** → a different failure, and say which:
     this project has not been wired. Point at `install-skills`. Never infer the role from a
     `components/` directory, a package name, or an exports map.

   `figma-to-spec` carries the mirror image of this gate and refuses in a `library` repo,
   naming this skill. The two guards are written to be read together: exactly one of the pair runs
   in any given repo, and an adapter with no role row runs the consumer-side skill exactly as
   it did before the row existed.

2. **Node-shape gate — one component set per run. Also a STOP.**

   Require the Figma node URL arg; ask if missing. Confirm the shape with `get_metadata`
   **before anything else reads the node**, and classify it:

   - **One component set** (`COMPONENT_SET`) → the intended input. Continue.
   - **A lone component** (`COMPONENT`, not inside a set) → fine. This is the **1-variant
     case**: treat it as a component set of one, whose single region carries
     `variant:default` unless the layer name declares a variant value.
   - **A page, section, or a frame holding unrelated content** → **refuse**: *one component set
     per run*. Name what was found so the user can re-invoke against the right node.
   - **A node holding several component sets** → **refuse**, same line, and **list the sets
     with their node IDs** so the next invocation is a copy-paste rather than a hunt. Several
     sets are several specs; merging them produces one spec that is wrong about all of them.

   This refusal is **by decision, not by omission**. A run per component set is what keeps a
   spec's variant axes the axes of exactly one component.

   **Where the node is genuinely ambiguous, ask — do not assume.** The common ambiguous shape
   is a wrapper frame containing exactly one component set (a documentation frame, a page of
   examples). Ask whether to spec the set inside it; if the answer resolves to exactly one
   component set, continue with that node id. If the wrapper holds a set plus loose example
   instances, say so and ask which node is canonical.

   **Record the file's version id or last-modified timestamp** as you first reach the file —
   whichever the tooling exposes, both when both are. It is the baseline the spec pins, and
   captured at the end of a run it would already be a different value. Unavailable → carry
   `unknown — <why>` forward rather than dropping it.

3. **Resolve, validate, then staleness-check the project catalog** — three parts, in this
   order. The catalog is a per-project artifact in the consuming repo, never a file inside this
   plugin. In a `library` repo it describes *this* repo's own design system, which changes
   nothing about the procedure.

   **3a — Resolve: passed arg → the adapter's registered catalog pointer → ask the user.** In
   that order, and no further. The pointer lives in `## Design system`, registered the way a
   gate is registered in `## Project gates` — **that registry is the only place the catalog is
   named.** Never hardcode a catalog filename, and never reconstruct one by reading the design
   system's source at run time. Read the resolved file in.

   **3b — Validate against `../../figma-to-spec/references/catalog-contract.md`. Hard STOP on
   failure.** Run that file's numbered validation rules **before any further Figma read**. A
   malformed catalog fails loudly and specifically: name the resolved path, the rule that
   failed, and what to change, then offer the two ways forward (fix the catalog, or point the
   run at a different one). Never degrade and never proceed on partial data — a spec built on a
   half-read catalog reads as fully resolved, which is exactly what this gate prevents.

   **3c — Staleness: soft, never fatal.** If the adapter registers a **fingerprint command**,
   run it and compare to the catalog's line-1 stamp. Match → note "catalog current". Mismatch →
   **soft-warn** ("catalog may lag the live design system — regenerate it with
   `figma-tools:ds-catalog`") and **continue**. No fingerprint command, or the source
   unreachable → note "staleness unchecked" and continue. A stale catalog matters more here
   than in a consumer repo — Phase B's current-state read is catalog-first — so **say the
   warning out loud in the Phase B output too**, and still never hard-fail on it.

4. **While the adapter is open, read the rest of `## Design system` and keep it.**

   - **Icon resolution ladder** — needed **verbatim** by every Phase B spawn; the region agent
     reads no project file it was not handed. Icon sources in the catalog with no stated order
     → ask the user rather than picking one.
   - **Variant mechanism** (library-only) — the ladder Phase B walks. **Absent → ask the user
     for it and offer `ds-catalog` to write the row.** Never infer the mechanism by reading the
     code: the shapes that look like the declaration are usually its implementation, which is
     precisely what the ladder's ordering exists to separate.
   - **Token pipeline** (library-only) — decides how literal a token delta may be phrased.
     Record it now; it is consumed when the spec is written. Absent → ask.
   - **Story convention** (library-only) — scopes Phase B's story-coverage read. Absent → ask;
     with no answer, story coverage for the whole run is reported *not computable — verify
     manually*, which is a real result and not a failure.
   - **The three class-prefix rows** — build-internal, custom-property, and consumer-facing
     prefixes are **three separate facts and are not interchangeable**; collapsing them is how
     a spec recommends a class the design system never emits.
   - The two optional rows — *usage-rules source*, *downstream implementer*. **An absent
     optional row is the answer, not a warning**: no usage-rules source means the spec cites
     nothing, and no downstream implementer means a human picks the spec up.

5. **Confirm capability — three separate checks (see SKILL.md Prerequisites).**

   (a) Ensure **`figma-dev-mode`** is present — STOP if not, no fallback. (b) Try to make the
   binding read (`use_figma`) available (load `/figma-use` if reachable). If it isn't, continue
   in **degraded color mode** per `../../../agents/figma-region-extractor.md` step 4 — and
   **announce it up front** so the user knows token tiers are unconfirmed. In a library repo
   that announcement carries extra weight: the tiers being read are the ones this repo defines.
   (c) Check whether the **`figma-region-extractor` subagent** is available, **under either
   type name**: `figma-tools:figma-region-extractor` (the normal route — the plugin namespaces
   it) or the bare `figma-region-extractor` (hand-placed in an `agents/` directory).
   Registration happens at session start, so a just-installed plugin may not resolve until the
   next session. Present → Phase B spawns it by the name that resolved. Absent under **both**
   names → Phase B uses the documented inline fallback. **Announce which path the run is
   taking** — a missing agent must never be silent, because an unresolvable `subagent_type`
   degrades to `general-purpose` rather than erroring.

6. **Identify the component under spec — catalog first.**

   Match the component set to its **catalog entry**: the entry's name, its declared variant
   axes and values, and its `status:`. Three outcomes, all of them fine, none of them silent:

   - **Confident match** → record the entry and carry it into Phase B as the primary
     current-state answer.
   - **Low-confidence match** → surface the parsed mapping and **ask the user to confirm**.
     Never call an inferred match confirmed without their yes.
   - **No entry matches** → this is a **new component**, which is the interesting case in a
     library repo. Record it as new; do not force it onto the nearest name, and do not treat
     the absence as a catalog defect until Phase B's source read says otherwise.

   Also accept **optional scope context** — a ticket URL and/or freetext ("only the new
   `destructive` variant"). It drives emphasis and intent; it does **not** override canvas
   values (context = *what to look at*; Figma = *the design values*). Freetext beats the ticket
   where they conflict; a conflict about *which node is canonical* goes back to step 2 and is
   asked, never picked.

## Phase A — Variants are the regions (main thread)

`get_metadata` on the component set → enumerate its **variant frames**. Each variant frame
becomes exactly one region, tagged with the source-node role **`variant:<name>`** —
the role `../../../agents/figma-region-extractor.md` defines alongside `primary`,
`viewport:<bp>` and `state:<name>`, and the reason it exists: viewports collapse into
responsive behaviour, states into a region's data states, and **variants into the props of one
component**. Reading a variant as a state is how one component becomes two in a spec.

**`<name>` is the variant's property assignment, taken verbatim from Figma** — the component
set's own vocabulary (`Variant=Primary, Size=Medium` → `variant:Variant=Primary,Size=Medium`;
strip only whitespace, never case). Do not translate it into the catalog's or the code's
vocabulary here: the mapping between Figma's axis names and the library's is a **finding**,
established in Phase B against the catalog, and pre-applying it would destroy the evidence for
it. The lone-component case from Phase 0 step 2 carries `variant:default`.

**What this phase does *not* do**, and each omission is a decision rather than a gap:

- **No content-vs-chrome classification.** A component set has no app chrome. Every variant
  frame is content.
- **No wrapper recursion.** Enumeration stops at the variant frames. What is *inside* one is
  the region agent's job, not this phase's — descending further would split one component
  across several agents and produce a spec of its parts.
- **No `spec-only` / `excluded` dispositions.** There is one disposition: every variant frame
  fans out. A variant a run should ignore is a scoping question for the human, asked, not a
  silent prune.

**Completeness self-check (before fan-out).** Every child of the component set must land in
exactly one region, **or** be explicitly listed as pruned with a reason — the only legitimate
prunes are non-variant scaffolding a designer left inside the set (a note frame, a spacer). If
a child is unaccounted for, you dropped a variant. **`log()` the coverage tally**:

```
N variant frames → M regions, K pruned (<reason each>)
```

so a miss is visible rather than silent. A component set whose enumerated variant count
disagrees with the axis cross-product implied by its variant properties is worth saying out
loud — a design system routinely draws a subset deliberately, and the gap between drawn and
possible is exactly what Phase C will ask about.

## Phase B — Variant agents + current state (Sonnet ×N parallel, plus main thread)

Two reads run side by side: **what Figma draws** (the agents) and **what the component already
is** (the main thread). Neither waits on the other.

### B1 — Spawn one agent per variant

One agent per variant frame, each scoped to that frame's node id, driven by
`../../../agents/figma-region-extractor.md` — normative for the call discipline, the extraction
contract, and the return schema. Each returns **structured findings** (the JSON schema in that
file, so synthesis merges deterministically).

**How to spawn (per variant).** Agent tool, `subagent_type: figma-tools:figma-region-extractor`
(try the namespaced name first; a hand-placed `agents/` file registers the bare
`figma-region-extractor` instead), `model: 'sonnet'` passed explicitly,
`run_in_background: false`. The extraction contract lives in the agent, so the per-call prompt
carries **only the seven inputs** — region node ID · region layer name · source-node role
(here always `variant:<name>`) · Figma file/page URL · **absolute** catalog path · **absolute**
resolution-rules path · the adapter's **icon resolution ladder, pasted verbatim**. The agent
hard-STOPs with `{"error": "missing input: <name>"}` if any is absent, so a malformed spawn
fails loudly instead of hallucinating catalog contents.

**Why the ladder is pasted rather than pointed at.** Every other input is a path or a node id;
this one is a project fact, and the agent is deliberately adapter-blind — it reads no project
file it wasn't handed. The main thread read the adapter in Phase 0, so it pastes the row's text
into each spawn. A ladder this plugin restated instead would be one organisation's icon module
shipped to every consumer.

End every per-call prompt with this exact line — the schema sits in the agent's system prompt
rather than at the end of the prompt, and without it JSON-only compliance drifts:

```
Return only the JSON object defined in your instructions — no prose before or after.
```

**If the agent is unavailable** (Phase 0 step 5c said so): fall back to `general-purpose` with
`model: 'sonnet'`, and build the prompt by reading `../../../agents/figma-region-extractor.md`
and pasting **everything below its frontmatter**, then appending the seven inputs and the line
above. Never keep a second copy of the contract — read it from the one file.

**Session lifetime.** `figma-dev-mode` sessions can expire on long parallel runs. On session
loss, re-auth and **re-run only the affected variant agent** — extraction is per-variant and
idempotent.

### B2 — The current-state read: catalog-first, source-second

This is the half that makes a component spec a *delta* rather than a description, and the order
is load-bearing.

**The catalog is primary.** The entry identified in Phase 0 step 6 is the statement of what
axes and values this component has. Start there, always, and record for each axis: its values,
each value's `status:` (`current` / `legacy` / `deprecated` / `unused`) and any `successor`.

**Source is fallback and cross-check — never a parallel derivation.** Read it by walking the
adapter's **variant mechanism ladder in its order, stopping at the first rung that resolves**,
and honour whatever **trap** that row names (a runtime alias map outside the declaration, a
values list that lives in a stylesheet, an axis that only exists in `.d.ts`). Three outcomes:

- **Catalog silent, source has it** → fill the hole, marked **`source-derived — not in the
  catalog`**. That marking is what stops a later reader mistaking it for a catalog fact, and it
  is a signal the catalog needs a refresh.
- **Both present and agreeing** → the ordinary case. Record once, noting it was cross-checked.
- **Both present and disagreeing** → **record both, side by side, as a disagreement.** Do not
  pick. Do not let source silently win because it is "closer to the truth" — one of the two is
  wrong and which one is a human decision, taken at triage. A run that resolves this quietly
  produces a spec whose baseline nobody can trust.

Never walk further down the ladder after a rung resolves, and never substitute a mechanism you
inferred from the code for the one the row names — the shapes that look like the declaration
(conditional `className` branches, a switch on a prop) are typically its *implementation*.

### B3 — Story coverage, scoped to what is computable

Locate stories via the adapter's **story convention** row. Coverage is computed **per primary
axis**, one way and one way only:

> `argTypes[<axis>].options` — the values the story declares as selectable — **diffed against
> the values actually passed in each story's `args`.**

Report per axis: declared options, values exercised by at least one story, and **values with no
story**.

**Story export names are explicitly ruled out as a coverage signal.** Naming an export
`Destructive` is not evidence that the `destructive` value is exercised, and the absence of
such an export is not evidence that it isn't — one story routinely covers several values, and
export names drift from the values they were named after. Do not read them, do not fall back to
them, and do not report a coverage number derived from them.

**An axis with no select `argType`** — hand-written `argTypes` that omit it, a boolean, a
free-text control, or no `argTypes` block at all — is listed **"not computable — verify
manually"**, per axis, with the reason. That is the honest result. A guessed coverage figure
is worse than none, because a spec that claims an axis is covered stops anyone from checking.

### End of Phase B — the bundle Phase C consumes

Phase B hands forward, and none of it is a spec yet:

- the per-variant findings bundle (one entry per `variant:<name>` region),
- the coverage tally from Phase A,
- the current-state read: catalog axes and values, what came from source and how, and **every
  disagreement, unresolved** — resolving one here would take a decision that belongs to the
  human at the Phase C checkpoint,
- story coverage per axis, including every *not computable* axis,
- and which capability path the run took (agent type resolved or fallback; degraded color mode
  or not; catalog current, stale, or unchecked). All three travel into the spec's header:
  a spec written under degraded color mode says so on its face.

**Do not present any of this as a component spec, and do not write to the tracker.** The
component spec is Phase C's output and filing is Phase D's, gated behind the human checkpoint.

## Phase C — Synthesis, triage & the spec (Opus, main thread)

Four things happen here in order, and the order is the whole design: reconcile, **stop for the
human**, research what the human chose, then write. Research after triage rather than before is
deliberate — precedent research is the expensive step, and a gap the human triages as
`fix-figma` or `already-expressible` never needs any.

### C1 — Reconcile the two reads into one axis table

Merge the variant findings (what Figma draws) with the current-state read (what the component
already is) into a single per-axis picture: for each axis, the library's existing values with
their `status:` and `successor:`, the values actually drawn, and the delta in both directions.

**The axis-name mapping is a finding, recorded, not applied silently.** Phase A kept Figma's
vocabulary verbatim for exactly this moment: `Variant=Primary` ↔ `variant="primary"` is a claim
about two naming schemes, and it is written down as a claim. Where a Figma axis has no library
counterpart at all, that is a candidate axis, not a mis-parse.

Two results here are **not** deltas and are recorded as findings instead: a value the library
has that Figma does not draw (a deliberate subset is normal), and a Phase B **disagreement**
between catalog and source, which stays unresolved and travels to the checkpoint as a question.

### C2 — Reconcile by concern, not by variant

The variant agents extracted locally; this pass makes each *concern* consistent across the whole
component set — one color→token map (the same fill must not resolve two ways across two variant
frames), one type/spacing picture, one icon inventory. **Extract by variant, reconcile by
concern.** It reasons over already-extracted findings: no Figma re-traversal, no second MCP read.

Dedup candidates across variants by the tuple `(property kind, resolved value, nearest match,
axis)` and carry an instance count — the same missing token appearing in four variant frames is
one line in the spec, not four, and the count is what tells a reviewer how load-bearing it is.
Color tolerance is `resolution-rules.md`'s, unchanged: ΔE `< ~1–2` auto-merges, `1–5` flags
"confirm intent", `> 5` is off-system.

### C3 — Assemble the candidate list

One row per candidate: what was observed, in which variants and how many times, what it nearest
resolves to in the catalog, whether the value was **bound** in Figma or raw, and a **recommended
outcome** from the four below. The recommendation is a recommendation; the human decides.

Every ⚠️ flag from Phase B joins the list too — near-misses, ambiguous icons, suspected
intentional deviations, and every `legacy` / `deprecated` match — because each is a question only
a human can close.

### C4 — STOP: the human triage checkpoint, four outcomes

**Present the whole candidate list and stop. No tracker write happens before this** — not a
search, not a draft, not a placeholder item. On either tracker.

The user marks every candidate exactly one of:

- **already-expressible** — the library already says this, or already composes it from what it
  has. Nothing changes. The spec records *how* it is expressed so nobody reaches for a raw value
  later. Available only when every constituent resolves ✅ on its own; one raw value in the
  composition means this is that value's candidate instead.
- **extend-component** — a variant axis, a value on an existing axis, or a props-API change.
  **This is the only outcome that triggers C5's pattern research**, because it is the only one
  that invents API surface.
- **extend-tokens** — the value has to enter the token layer, phrased through the adapter's
  *Token pipeline* row (C6).
- **fix-figma** — the **Figma library itself** is wrong: an unbound fill, a raw hex where a
  variable belongs, a detached instance, a variant frame contradicting its own property
  assignment. Designer-side work. It rides the same tracker item as the code work — it blocks the
  same change — but it lands **only** in the spec's *Figma fixes* section and never in a code
  section.

**The question that separates them**, and it is not the consumer skill's question:

> **Where does this have to change — the component's API, the token layer, the Figma library, or
> nowhere, because the system already says it?**

`figma-to-spec`'s checkpoint asks *is this genuinely reusable across the product, or one-off to
this design?* and marks **escalate** / **compose-from-tokens** / **build-local**
(`../../figma-to-spec/references/resolution-rules.md` → `## Triage outcomes`, which is the
consumer-mode set — **reference it, never edit it**). That question answers nothing here. In the
repo that *is* the design system everything is reusable by definition, there is nobody to
escalate to, and "build it locally" and "extend the component" are the same act. Four outcomes
about *where the edit lands* is the library-side equivalent, not a relabelling of three.

Two rules carry over from the consumer checkpoint unchanged, and they are the load-bearing ones:

1. **No tracker write before this gate.**
2. **Every decision records a one-line rationale** — all four outcomes, including
   `already-expressible`, in the spec's *Triage record*. That line is what stops the next run
   re-litigating a settled call; a rationale-less triage makes run five cost what run one cost.
   "Not needed" is not a rationale.

Also settled here, at the same stop:

- **Every `legacy` / `deprecated` flag: match-as-is or modernize.** Match-as-is specs the legacy
  value because it ships. Modernize specs the successor and notes that the design still draws the
  old one — and it generates **extend-component / extend-tokens sections in this same spec**,
  never a separate artifact. A legacy match still resolved and still flagged; it was never a gap.
- **Every catalog-vs-source disagreement from Phase B**: which of the two is wrong. Record the
  answer and its rationale. A disagreement the human defers stays open in the *Triage record* and
  the axis row it touches is marked blocked — an open disagreement is a real state, and a spec
  that hides one has a baseline nobody can trust.
- **Every collision between the design and the standard** the ladder will cite (a control with no
  keyboard affordance, an axis that fights the APG pattern's model) — a checkpoint question,
  never silently followed *and* never silently "fixed".

### C5 — Pattern precedent research, one subagent per extend-component gap

**Precedent is a phase, not an outcome.** The point is that a specced props API follows the
industry's established shape instead of being invented from one variant frame — a frame shows
what the component *looks like* in one state and says nothing about what its API should be.

**The ladder, walked in order: ARIA APG → headless libraries → shadcn.** Unlike the icon ladder,
this one does **not** stop at the first rung — each rung answers a different question, and a
lower rung never overrides a higher one on the same question:

1. **ARIA APG** — the **behaviour spec**: roles, keyboard interaction, focus management. Where a
   pattern exists it is authoritative and a library's convenience does not override it.
2. **Headless libraries** — the **API shape**: what is a prop vs a sub-component, controlled vs
   uncontrolled, what the parts are called. Consult **whichever this repo already depends on
   first** (the adapter's variant-mechanism row and the repo's own manifest say which), then the
   others as precedent only.
3. **shadcn** — the **naming and declaration convention** for variant axes, which is the closest
   published analogue to how most libraries in this shape declare theirs.

**How to spawn (per gap, parallelisable).** Agent tool, `subagent_type: general-purpose`,
`model: 'sonnet'` passed explicitly, `run_in_background: false`. One spawn per
**extend-component** gap; they are independent, so spawn them together.

**The researcher is repo-blind and Figma-blind by design** — it reads no project file and no
Figma node, so the prompt carries everything it may use, and nothing else:

- the **component class in plain words** ("a segmented single-select control", not the repo's
  name for it),
- the **specific change** under consideration — the axis, the value, or the props-API shape,
- this library's **existing axis vocabulary for that component**, so precedent comes back
  phrased against the names in play rather than the reference library's,
- the **ladder above, verbatim**, including which headless library this repo already depends on.

Return shape, requested explicitly, and short — **distil, do not dump**, timeboxed, 3–6 sources
actually read:

- `behaviorSpec` — the APG pattern name + URL, or `none applies — <why>`
- `apiPrecedent` — library + the shape it uses + URL
- `namingPrecedent` — how the axis is named/declared there + URL
- `deviations` — where this design or this library's idiom forces a departure from the standard
- `sources` — the URLs read

**A gap with no precedent says so.** `none found — searched <what>` is the required answer when
the ladder returns nothing; the props rows it would have supported are then marked a local
invention in the spec. Never synthesise a plausible-sounding precedent: an invented one launders
a guess as an industry standard, and nobody re-checks a cited standard.

**No web access** → the *Pattern precedent* section reads `unavailable — <why>`, every
extend-component API is flagged unresearched, and the run continues. That is a real result and
not a failure; a silently unresearched API is the failure.

### C6 — Write the component spec

One spec, per `component-spec-template.md`, into the run directory. **No `gaps/` directory** —
in a library the gap and the spec are the same document, so every gap is a section: a row in
*Variant axes*, a line in *Token delta*, an item in *Figma fixes*, and its rationale in *Triage
record*.

Two things are read from the adapter rather than decided here:

- **The token delta's literalness is the *Token pipeline* row's call, never the repo's shape.** A
  generator plus its source → state the **literal source edit** in that file's own format, and
  say to regenerate rather than hand-edit the output. `None` → a **coordinated file-edit list**,
  every file that must change together, named. Choosing by reading the tree instead of the row
  puts the edit in a file the build overwrites — and that failure does not error.
- **Whether a story edit is part of the change** is the *Story convention* row's call. Generated
  `argTypes` mean the new value appears for free; hand-written ones mean the story edit is part
  of the change and belongs in the acceptance criteria.

Also: carry the run's capability path into the header (degraded color mode, catalog staleness,
research availability), keep every *not computable* story axis as its own row, and diff
**spec-vs-spec** against a prior spec — the local file or the previously filed item — for the
Changelog. Never spec-vs-code: reconciling against live code is the implementer's job, and this
skill stays a pure function of the component set plus the catalog.

## Phase D — Filing (gated — only after triage)

**Filing is tracker-parametric. Read the adapter before writing anything.** The `Tracker:` line
in `## Repo` selects the profile — `github` or `azure-devops`, and **an absent line means
`github`**. Run that profile and ignore the other entirely.

**The filing target is this repo's own tracker rows — not the two `figma-tools` filing rows.**
`Design-spec target` and `DS-gap backlog` are `figma-to-spec`'s: a page spec is filed where the
consuming code is tracked, and an escalated gap where the design system lives. Here they answer
nothing. The design system *is* this repo, so there is nobody to escalate to and no second
destination; the spec is ordinary work in this repo's own tracker, filed where every other
work item here is filed. Read the plain `## Repo` rows — GitHub: `Issue tracker / PRs`; ADO:
*Organisation*, *Work-item project*, *Work-item type*, *Title prefixes*, board states.

**The design-spec prefix `figma-to-spec` files under is never written by this skill, on either
tracker.** It is consumer-mode-only and marks a spec whose implementer is somewhere else. A
component spec filed under it is invisible to the slicing chain that would pick it up, which is a
dead end that looks exactly like a successful run. File the right type in the first place and the existing chains —
`ado-workflow:to-spec-tasks`, `prd-workflow:to-issues` — consume it unchanged. **No file under
`ado-workflow` or `prd-workflow` is touched to make this work.**

### Dedup first — on both trackers, before any write

**Search the filing target before creating anything.** Match on the **Figma component set's node
id**, carried in the spec body, not on the title: a component gets renamed and a title match then
files a duplicate under the new name. Where the local spec header already records a filed id,
prefer it and still verify the item exists (a run directory outlives nothing).

- **Found** → **update it in place.** Rewrite the body from the new spec; never open a second.
- **Not found** → create it, then **write the returned id back** into the spec header.

That search plus the write-back is the **entire zero-new-items guarantee**: a second run on the
same component set must create **zero** new tracker items.

**The node-id fingerprint rides differently on each tracker, and this is not cosmetic.** On
GitHub an HTML comment survives the API read, so the fingerprint may be a comment trailer. **On
Azure DevOps HTML comments are stripped out of a work item's read**, so it must ride **in the
open, backticked**, in a visible line of the description — a fingerprint written as a comment
there is a fingerprint that does not exist on the next run's search.

### GitHub profile (`Tracker: github`, or no `Tracker:` line)

- **The component spec → an ordinary issue** on the repo the `Issue tracker / PRs` row names,
  via `gh`. **Not a design-spec issue.** Prefix it only if the adapter's *Title prefixes* row names
  one that applies — GitHub prefixes are a human scanning convention that nothing filters on, so
  an unprefixed title is a correct title.
- Apply the **first label in the adapter's *Triage labels* row** (`needs-triage`, in the
  vocabulary that row uses today) so the spec enters the normal triage flow, exactly as a filed
  PRD does. No such row → apply nothing.
- **Given a scope issue in Phase 0, link the new issue as its native sub-issue.** The link is
  what makes it a child, so the body carries **no `## Parent` section** — a hand-written parent
  beside a real link is a second source of truth that can disagree. The mechanics are documented
  once, in `prd-workflow`'s `to-issues` skill under *Link each child to the PRD as a native
  sub-issue*: create → link → **verify**, three `gh api` calls, and `sub_issue_id` takes the
  issue's **internal numeric `id`** (`--jq .id`), never its issue number — passing the number
  returns a bare `404` indistinguishable from "no such issue". Follow that file; do not
  reconstruct the sequence here. A `POST` that succeeded is not evidence the link landed: read
  the parent's sub-issue list back, and say out loud that you did.

### Azure DevOps profile (`Tracker: azure-devops`)

- **The component spec → a plain `[SPEC]` work item** in the *Work-item project*, created as the
  *Work-item type* the adapter names, with the `[SPEC]` prefix taken from the *Title prefixes*
  row — **never hardcoded here, and never the design-spec prefix**. On this tracker the prefix is
  load-bearing: it is the only thing distinguishing one kind of child from another, so a
  mistyped prefix returns an empty set to the next skill rather than an error.
- Create it in the board's **Pickable** state (the adapter names it) so `to-spec-tasks` and the
  orchestrated loop can pick it up without a human first moving it.
- **Given a scope work item in Phase 0, file the spec as its child.**
- Reference PRs as `!<id>` and work items as `#<id>` in any ADO text — separate id namespaces
  there, so a `#` in front of a PR number silently points at an unrelated work item.

### End of run — report

Report the filed id and whether it was created or updated, the four-outcome triage tally, every
open item (deferred disagreements, unresearched APIs, degraded color mode, a stale catalog), and
the run directory holding the spec. **Say plainly what the run did not verify:** that the design
is right, that an inferred component identity is correct without the user's yes, and that the
eventual code renders faithfully.
