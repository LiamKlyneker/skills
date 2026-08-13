# Phase bodies

The full procedure for each phase of `figma-component-to-spec`. SKILL.md carries the contract,
the model tiers, the phase overview, and the STOP gates; load the section here for the phase
you are running.

Normative elsewhere, never restated here: the variant-agent extraction contract and the
`bindingVerified` / degraded-color-mode rules live in
`../../../agents/figma-variant-extractor.md`; resolution and tolerance rules in
`../../figma-to-spec/references/resolution-rules.md`; the required shape of a project catalog,
**where a project registers one**, in `../../figma-to-spec/references/catalog-contract.md`.
Those last two are **shared with `figma-to-spec` and `ds-catalog`** — read them at those paths.
A second copy of a contract is the failure this plugin's layout exists to prevent.

**Existence is the one thing that moved, and it is no longer a catalog.** It is the **token list
Setup assembles and hands to every spawn**, and Setup's step 3 is the normative statement of what
that list covers, where each part of it comes from, and when the run stops for want of one.

**The phases are named and numbered, not lettered, and the order is the whole design.** Setup ·
Structure · Current state · Reconcile & triage all complete **before a single metered extraction
call is spent** — the human checkpoint sits ahead of the expensive step, not behind it. A
component set is a **lattice, not a list of unknowns**: one `get_metadata` on the set root
returns every variant frame with its property assignments, which is the entire axis lattice in
one response, so the spec's most important section needs zero per-frame extraction to write.

---

## Phase 1 — Setup (main thread)

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
     case**: treat it as a component set of one, whose single frame carries
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

   **This `get_metadata` is the only metered Figma read the whole pre-checkpoint half spends,
   and it is not two jobs — it is one.** A `get_metadata` on a component set root returns its
   variant frames **with their property assignments**, so confirming the node's shape and
   reading the entire axis lattice are the same call. **Keep the whole response.** Phase 2
   derives everything it needs from it and never re-reads; no phase before the checkpoint makes
   a per-frame call. Reaching for a second `get_metadata` before the checkpoint means something
   upstream dropped this response, not that another one is needed.

   **Record the file's version id or last-modified timestamp** as you first reach the file —
   whichever the tooling exposes, both when both are. It is the baseline the spec pins, and
   captured at the end of a run it would already be a different value. Unavailable → carry
   `unknown — <why>` forward rather than dropping it.

3. **Resolve the existence source and assemble the token list.** This is what the run hands
   every later extraction spawn, and it is a **hard requirement**. The *artifact* changed; the
   *guarantee* did not.

   **3a — What the list must cover.** Five kinds, because the variant agent's return schema has
   an array for each and **an entry that is not on the list does not exist**:

   - **tokens by tier** — semantic, alias, primitive;
   - **typography utilities**, enumerated;
   - **dimension tokens** — spacing, radius, size;
   - **the components this library ships**, with their recorded variant axes and listed values;
   - **the icon sources the icon resolution ladder names, with their entries.**

   Tokens alone are not enough, and the last two are the reason: the agent emits a
   `components[]` and an `icons[]` array, and each needs an existence source of its own or every
   nested instance and every icon comes back a gap.

   Write every entry in the project's **consumer-facing emission form** — the adapter's
   *Consumer-facing emission form* row, which is a separate fact from the Tailwind class prefix
   and from the CSS variable prefix. The agent emits an entry exactly as the list writes it and
   never re-prefixes one, so a list assembled in the library-internal form produces a spec
   recommending classes no consumer can write.

   Also record, per entry, the **status** the source stamps it with (`current` / `legacy` /
   `deprecated` / `unused`) and its `successor` where one is recorded. An entry with no recorded
   status reads as `current`. This is what lets a legacy match resolve-with-a-flag instead of
   false-gapping as something the library must build.

   **3b — Where each part comes from.** **Read the adapter's *Token pipeline* row and read the
   token source it names.** That row already answers "where do the tokens live", directly, and
   in a library repo one file read gives the token, typography and dimension parts of the list —
   which is exactly what the catalog was standing in for. Components and icon entries come from
   the **catalog where one is registered**, and otherwise are enumerated once from the library
   itself: components from the design system's own component directory (the *Design-system
   source* row names it, and in a library repo it names this repo), read through the primary
   rung of the **variant mechanism** ladder so the axes and values come from the declaration
   rather than from a filename; icons from each source the **icon resolution ladder** names, in
   the order it names them.

   **A part with no resolvable source is written into the list as `<kind>: none resolvable —
   <why>` and announced up front. Do not leave it out.** An omitted section and an empty one
   read identically to the agent — both mean *nothing of this kind exists here* — so every
   finding of that kind returns as a gap. Announcing it is what lets triage read those gaps as
   **unresolved existence** rather than as real absences the library must fill.

   **3c — At least one existence source must resolve. No existence source at all is a hard
   STOP.** The list may be assembled from the token source, from a catalog, from an enumeration
   you actually performed, or from any combination — but never from what you already know about
   design systems.

   **The catalog's hard STOP was never about the catalog. It was about keeping the extractor
   training-blind**, and that property does not require a catalog: it requires the agent to be
   handed **an explicit list it may not add to**. Without an explicit existence source, nothing
   stops a spec citing a spacing scale, a token name or an icon set from a well-known public
   design system this library never had — and it will read as entirely plausible to every human
   who reviews it, which is precisely why nobody catches it.

   So: no *Token pipeline* row and no source behind it, no registered catalog, and nothing
   enumerable → **stop**, name each thing that was looked for and where, and offer the two ways
   forward: write the *Token pipeline* row (via `install-skills` or `ds-catalog`), or generate a
   catalog with `figma-tools:ds-catalog`. Never proceed on a partial list without announcing
   which part is missing (3b), and never proceed on no list at all.

   **3d — A registered catalog is still validated, and still soft-staleness-checked. It is
   demoted, not banned.**

   - *Resolve* it exactly as before: **passed arg → the adapter's registered catalog pointer →
     ask the user**, in that order and no further. The `## Design system` registry is the only
     place a catalog is ever named — never hardcode a filename, never reconstruct one by reading
     the design system's source at run time. **No pointer and no arg is no longer a stop**: note
     "no catalog registered — existence resolved from the *Token pipeline* source" and continue.
   - *Validate* whatever did resolve against
     `../../figma-to-spec/references/catalog-contract.md`, and **a registered catalog that fails
     it is a hard STOP** — name the resolved path, the rule that failed, and what to change,
     then offer the two ways forward (fix it, or point the run at a different one). A project
     that registered a catalog is asserting it is valid; a malformed one is a **defect**, not an
     absence, and degrading onto half-read data produces a spec that reads as fully resolved.
   - *Staleness* stays **soft and never fatal**. Fingerprint command registered → run it,
     compare to the catalog's line-1 stamp; match notes "catalog current", mismatch **soft-warns**
     ("catalog may lag the live design system — regenerate it with `figma-tools:ds-catalog`") and
     continues; no command, or the source unreachable → note "staleness unchecked" and continue.
     What changed is the *consequence*: the catalog is a **cross-check** now (Phase 3), not the
     primary current-state read, so a stale one degrades a cross-check rather than the answer.
     Say the warning out loud in Phase 3's output anyway.

   **3e — The revisit condition, written as a row read rather than a preference.** Whether a
   derived catalog is worth having here is decided by one adapter row, and it is testable:

   - *Token pipeline* names **a generator and the source file it consumes** → one read gives the
     token set, and a derived catalog is **redundant for existence**. This is the shape the
     demotion was designed for.
   - *Token pipeline* reads **`None — <how tokens are edited instead>`** → there is **no single
     file whose read gives the token set**. The run reconstructs it across every file that row
     lists, on every run, and **a derived catalog starts paying for itself again**. Say so at the
     checkpoint and point at `figma-tools:ds-catalog`.

   That is a condition on one row, not a judgement about catalogs in general, and it is what a
   later reader re-tests rather than re-argues.

4. **While the adapter is open, read the rest of `## Design system` and keep it.**

   - **Icon resolution ladder** — needed **verbatim** by every extraction spawn; the variant
     agent reads no project file it was not handed. It also decides which icon sources step 3b
     enumerates. Icon sources with no stated order → ask the user rather than picking one.
   - **Variant mechanism** (library-only) — the ladder Phase 3 walks, and it is now the
     **primary** current-state read rather than a fallback behind the catalog. **Absent → ask the
     user for it and offer `ds-catalog` to write the row.** Never infer the mechanism by reading
     the code: the shapes that look like the declaration are usually its implementation, which
     is precisely what the ladder's ordering exists to separate.
   - **Token pipeline** (library-only) — **does double duty now.** It names the token source
     step 3 just read, *and* it decides how literal a token delta may be phrased when the spec
     is written. Absent → ask; and note that an absent row is also the 3c question, because
     nothing else names the token source.
   - **Story convention** (library-only) — scopes Phase 3's story-coverage read. Absent → ask;
     with no answer, story coverage for the whole run is reported *not computable — verify
     manually*, which is a real result and not a failure.
   - **The three class-prefix rows** — build-internal, custom-property, and consumer-facing
     prefixes are **three separate facts and are not interchangeable**; collapsing them is how
     a spec recommends a class the design system never emits, and the consumer-facing one is the
     form step 3a writes the token list in.
   - The two optional rows — *usage-rules source*, *downstream implementer*. **An absent
     optional row is the answer, not a warning**: no usage-rules source means the spec cites
     nothing, and no downstream implementer means a human picks the spec up.

5. **Confirm capability — three separate checks (see SKILL.md Prerequisites).**

   (a) Ensure **`figma-dev-mode`** is present — STOP if not, no fallback. (b) Try to make the
   binding read (`use_figma`) available (load `/figma-use` if reachable). If it isn't, continue
   in **degraded color mode** per `../../../agents/figma-variant-extractor.md` step 3 — and
   **announce it up front** so the user knows token tiers are unconfirmed. In a library repo
   that announcement carries extra weight: the tiers being read are the ones this repo defines.
   (c) Check whether the **`figma-variant-extractor` subagent** is available, **under either
   type name**: `figma-tools:figma-variant-extractor` (the normal route — the plugin namespaces
   it) or the bare `figma-variant-extractor` (hand-placed in an `agents/` directory).
   Registration happens at session start, so a just-installed plugin may not resolve until the
   next session. Present → Phase 5 spawns it by the name that resolved. Absent under **both**
   names → Phase 5 uses the documented inline fallback. **Announce which path the run is
   taking** — a missing agent must never be silent, because an unresolvable `subagent_type`
   degrades to `general-purpose` rather than erroring.

   **`figma-region-extractor` is not checked here, by decision.** It is the page-side agent and
   it belongs to `figma-to-spec`; a component run that found it and spawned it would be handing
   a page contract a variant frame.

6. **Identify the component under spec — against the existence source.**

   Match the component set to its entry in the token list assembled in step 3: the entry's name,
   its recorded variant axes and values, and its status. Three outcomes, all of them fine, none
   of them silent:

   - **Confident match** → record the entry and carry it into Phase 3 as one input to the
     current-state read.
   - **Low-confidence match** → surface the parsed mapping and **ask the user to confirm**.
     Never call an inferred match confirmed without their yes.
   - **No entry matches** → this is a **new component**, which is the interesting case in a
     library repo. Record it as new; do not force it onto the nearest name, and do not treat
     the absence as a defect in the existence source until Phase 3's source read says otherwise.

   Also accept **optional scope context** — a ticket URL and/or freetext ("only the new
   `destructive` variant"). It drives emphasis and intent; it does **not** override canvas
   values (context = *what to look at*; Figma = *the design values*). Freetext beats the ticket
   where they conflict; a conflict about *which node is canonical* goes back to step 2 and is
   asked, never picked.

## Phase 2 — Structure (main thread — zero Figma calls of its own)

**A component set is a lattice, not a list of unknowns.** The `get_metadata` Setup already made
on the set root returned every variant frame **with its property assignments**, which is the
entire axis lattice in one response. So this phase spends **no Figma call at all** — not a
second root read, and above all **not one per frame**. Enumeration stopped being a discovery
phase and became a read, which is what makes the spec's *Variant axes* section — its most
important — free.

Everything below is derived from that one response.

1. **The variant frames, and the role each carries.** Each variant frame is exactly one
   extraction unit, tagged with the source-node role **`variant:<name>`** — the role
   `../../../agents/figma-variant-extractor.md` defines, and the reason it exists: viewports
   collapse into responsive behaviour, states into a region's data states, and **variants into
   the props of one component**. Reading a variant as a state is how one component becomes two
   in a spec.

   **`<name>` is the variant's property assignment, taken verbatim from Figma** — the component
   set's own vocabulary (`Variant=Primary, Size=Medium` → `variant:Variant=Primary,Size=Medium`;
   strip only whitespace, never case). The lone-component case from Setup step 2 carries
   `variant:default`. **Nothing is spawned here.** Which of these frames is ever extracted is
   Phase 4's decision and Phase 5's spend.

2. **The drawn axes and their values, in Figma's vocabulary, verbatim.** Every distinct property
   name across the assignments is an axis; every distinct value on it is a value. Where the
   response carries the assignments only as the frame's layer name (`Size=Medium, State=Hover`),
   parse the name — it is the same one response, and parsing it costs no call.

   **Do not translate a name or a value into the library's or the catalog's vocabulary here.**
   `Variant=Primary` ↔ `variant="primary"` is a **claim about two naming schemes**, established
   as a finding in Phase 4 against the current-state read. Pre-applying it here destroys the
   evidence for it — a mapping applied silently in Phase 2 cannot be questioned in Phase 4,
   because by then there is only one vocabulary left on the table.

3. **Drawn vs cross-product, said out loud.** Multiply the value counts per axis; compare
   against the number of frames actually drawn. A design system routinely draws a deliberate
   subset, so a gap here is **normal and not a defect** — and it is exactly what triage asks
   about, so state both numbers and name which combinations are absent.

4. **Duplicate or inconsistent Figma property values — recorded, never normalised.** From the
   same response, flag: two frames carrying identical assignments; values differing only in case
   or whitespace (`Primary` and `primary` on the same axis); an axis present on some frames and
   missing on others; a frame whose assignment contradicts its own layer name. Each is a
   candidate `fix-figma` for the checkpoint. Silently normalising any of them destroys the only
   evidence that the Figma library has a problem.

5. **Instance counts, computed from the lattice rather than observed.** A value drawn at 4 sizes
   × 5 states is known to appear **20 times** — without extracting 20 frames. Record a count per
   `(axis, value)` and per combination from the lattice arithmetic, and mark it in the run's
   record as **computed**, never observed. This is what makes extracting a subset later cost the
   spec nothing it consumes: the counts synthesis carries were never a by-product of extraction.

6. **Completeness self-check, and the tally.** Every child of the component set must land in
   exactly one variant frame, **or** be explicitly listed as pruned with a reason — the only
   legitimate prunes are non-variant scaffolding a designer left inside the set (a note frame, a
   spacer). If a child is unaccounted for, you dropped a variant. **`log()` the coverage tally**:

   ```
   N variant frames → M axes × <values each> = P cross-product, K pruned (<reason each>)
   ```

   so a miss is visible rather than silent.

**What this phase does *not* do**, and each omission is a decision rather than a gap:

- **No Figma call.** Not one. A per-frame read here would put the run's whole cost back in front
  of the checkpoint, which is the thing this shape exists to prevent.
- **No axis-name translation** (step 2 above) — the mapping is a Phase 4 finding.
- **No content-vs-chrome classification.** A component set has no app chrome. Every variant
  frame is content.
- **No wrapper recursion.** Enumeration stops at the variant frames. What is *inside* one is
  the variant agent's job in Phase 5, not this phase's — descending further would split one
  component across several agents and produce a spec of its parts.
- **No `spec-only` / `excluded` dispositions.** Every variant frame enters the lattice. Which
  ones are worth a metered call is a human decision taken at the Phase 4 checkpoint, not a
  silent prune taken here.

## Phase 3 — Current state (main thread — no Figma calls)

This is the half that makes a component spec a *delta* rather than a description, and **the
order inverted: source first, catalog second.** In a library repo the variant declaration in
source **is** the truth, and the catalog is a photocopy of it sitting in the same tree — an
artifact at its least trustworthy exactly where it is most load-bearing. Reading the declaration
directly removes that.

**This phase makes no Figma call whatsoever.** Everything it reads is in this repo.

### 3.1 — The source read, through the variant-mechanism ladder

Walk the adapter's **variant mechanism ladder in its order, stopping at the first rung that
resolves**, and honour whatever **trap** that row names (a runtime alias map outside the
declaration, a values list that lives in a stylesheet, an axis that only exists in `.d.ts`).

**Never walk further down the ladder after a rung resolves**, and **never substitute a mechanism
you inferred from the code** for the one the row names — the shapes that look like the
declaration (conditional `className` branches, a switch on a prop) are typically its
*implementation*, and specing against the implementation produces a delta against the wrong
file.

Record, per axis: its values, each value's **status** (`current` / `legacy` / `deprecated` /
`unused`) and any **successor**. Status and successor come from whichever source records them —
the declaration itself where it marks them (the trap the row names is frequently exactly this: a
deprecated-alias map outside the declaration), the token-list entry from Setup step 3 otherwise.
A value with no recorded status reads as `current`. **Name the file the ladder resolved at**, in
the phase output and in the spec: a current-state read whose source is unnamed cannot be
re-checked by anyone.

### 3.2 — The catalog as cross-check

Where a catalog resolved in Setup step 3d, compare it against the source read. Three outcomes,
and only one of them is silent:

- **Both present and agreeing** → the ordinary case. Record once, noting it was **cross-checked**.
- **Catalog silent, source has it** → record the source's answer plainly; it is a source fact,
  not a hole being filled. Mark it **`not cross-checked — catalog silent`**, which is also a
  signal the catalog needs a refresh.
- **Both present and disagreeing** → **record both, side by side, as a disagreement.** Do not
  pick. Do not let the catalog win because it is the older artifact, and do not let source win
  because it is "closer to the truth" — **one of the two is wrong, and which one is the human's
  call at the Phase 4 checkpoint.** A run that resolves this quietly produces a spec whose
  baseline nobody can trust.

**A value the catalog lists and the declaration does not is a disagreement, not an absence — but
check the trap rung first.** The commonest shape of exactly that is the trap the *Variant
mechanism* row already warned about: an alias map the declaration never lists. Walk the trap the
row names before recording the disagreement.

Where **no catalog resolved**, say so once — "no catalog registered; current state is the source
read, uncross-checked" — and continue. That is a real result, not a degradation: the source read
was the primary answer either way. Where a catalog resolved but Setup step 3d soft-warned it
stale, **repeat the warning here**, and say what it now costs: a stale cross-check, not a stale
answer.

### 3.3 — Story coverage, scoped to what is computable

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

### End of Phase 3 — the bundle Phase 4 consumes

None of it is a spec yet, and none of it cost a metered call:

- the lattice from Phase 2 — axes, values, drawn-vs-cross-product, computed instance counts,
  and every duplicate/inconsistent Figma property value;
- the current-state read — the file the ladder resolved at, axes and values with their status
  and successor, what was cross-checked, and **every disagreement, unresolved**;
- story coverage per axis, including every *not computable* axis;
- and which capability path the run took (agent type resolved or fallback; degraded color mode
  or not; existence source used; catalog current, stale, unchecked, or absent). All of it
  travels into the spec's header: a spec written under degraded color mode says so on its face.

**Do not present any of this as a component spec, and do not write to the tracker.**

## Phase 4 — Reconcile & triage (Opus, main thread)

Three things happen here in order, and the order is the whole point: reconcile, assemble the
candidate list, **stop for the human — before a single metered extraction call is spent.**

**This is not a new principle; it is an old one applied one level earlier.** The reasoning behind
"research after triage rather than before" was that precedent research is expensive and *a gap
the human triages as `fix-figma` or `already-expressible` never needs any*. Per-frame extraction
is far more expensive than research, and the same sentence is true of it. A run that extracts 120
frames and then asks which ones mattered has spent its whole budget answering a question the
human could have answered first.

### 4.1 — One axis table

Merge the lattice (what Figma draws) with the current-state read (what the component already is)
into a single per-axis picture: for each axis, the library's existing values with their `status:`
and `successor:`, the values actually drawn, and **the delta in both directions**.

**The axis-name mapping is a finding, recorded as a claim, not applied silently.** Phase 2 kept
Figma's vocabulary verbatim for exactly this moment: `Variant=Primary` ↔ `variant="primary"` is a
claim about two naming schemes, and it is written down as one. Where a Figma axis has no library
counterpart at all, that is a **candidate axis**, not a mis-parse.

Two results here are **not** deltas and are recorded as findings instead:

- **a value the library has that Figma does not draw** — a deliberate subset is normal, and this
  is a finding about coverage, not a gap the library must fill;
- **a Phase 3 disagreement** between catalog and source, which stays unresolved and travels to
  the checkpoint as a question.

### 4.2 — The candidate list

One row per candidate: what the lattice and the current-state read establish, **the instance
count computed in Phase 2** (never a count of extracted frames), what it nearest resolves to in
the token list, and a **recommended outcome** from the four below. The recommendation is a
recommendation; the human decides.

Dedup candidates by the tuple **`(property kind, resolved value, nearest match, axis)`** and
carry the computed instance count on the surviving row — the same candidate appearing across four
variant frames is one line in the spec, not four, and the count is what tells a reviewer how
load-bearing it is.

**Every ⚠️ flag joins the list too**, because each is a question only a human can close:

- every duplicate or inconsistent Figma property value from Phase 2 step 4;
- every `legacy` / `deprecated` match from the current-state read;
- every unresolved catalog-vs-source disagreement from Phase 3;
- every axis reported *not computable* by story coverage;
- every part of the token list Setup step 3b could not resolve a source for — those are
  **unresolved existence**, not absences.

### 4.3 — STOP: the human triage checkpoint, four outcomes

**Present the whole candidate list and stop.** Two negatives hold at this gate:

1. **No tracker write has happened** — not a search, not a draft, not a placeholder item, on
   either tracker.
2. **No metered extraction call has been spent.** The only metered Figma read the run has made is
   Setup step 2's single `get_metadata` on the set root.

The user marks every candidate exactly one of:

- **already-expressible** — the library already says this, or already composes it from what it
  has. Nothing changes. The spec records *how* it is expressed so nobody reaches for a raw value
  later. Available only when every constituent resolves ✅ on its own; one raw value in the
  composition means this is that value's candidate instead.
- **extend-component** — a variant axis, a value on an existing axis, or a props-API change.
  **This is the only outcome that triggers pattern research**, because it is the only one
  that invents API surface.
- **extend-tokens** — the value has to enter the token layer, phrased through the adapter's
  *Token pipeline* row.
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
- **Every catalog-vs-source disagreement from Phase 3**: which of the two is wrong. Record the
  answer and its rationale. A disagreement the human defers stays open in the *Triage record* and
  the axis row it touches is marked blocked — an open disagreement is a real state, and a spec
  that hides one has a baseline nobody can trust.
- **Every collision between the design and the standard** the precedent ladder will cite (a
  control with no keyboard affordance, an axis that fights the APG pattern's model) — a
  checkpoint question, never silently followed *and* never silently "fixed".

**What the checkpoint hands forward is a set of frames, not just a set of outcomes.** Each
surviving `extend-tokens` and `fix-figma` candidate points at the variant frames that must
actually be read to write it; their union is the **kept set** Phase 5 spends its calls on.
Candidates settled as `already-expressible` need no frame, and `extend-component` is an
API-shape question the lattice already answered. Confirm the kept set with the user in the same
breath as the outcomes — it is the number the next phase is budgeted against.

---

**Everything below runs only after that checkpoint.**

## Phase 5 — Targeted extraction (`figma-tools:figma-variant-extractor`, Sonnet ×N parallel)

**Spawn only on the frames the checkpoint kept.** One agent per kept variant frame, each scoped
to that frame's node id, driven by `../../../agents/figma-variant-extractor.md` — normative for
the call discipline, the extraction contract, and the return schema. Each returns **structured
findings** (the JSON schema in that file, so synthesis merges deterministically).

**How to spawn (per variant).** Agent tool, `subagent_type: figma-tools:figma-variant-extractor`
(try the namespaced name first; a hand-placed `agents/` file registers the bare
`figma-variant-extractor` instead), `model: 'sonnet'` passed explicitly,
`run_in_background: false`. The extraction contract lives in the agent, so the per-call prompt
carries **only the seven inputs** — variant frame node ID · variant frame layer name ·
source-node role (here always `variant:<name>`) · Figma file/page URL · **absolute**
resolution-rules path · the **token list Setup assembled, pasted verbatim** · the adapter's
**icon resolution ladder, pasted verbatim**. The agent hard-STOPs with
`{"error": "missing input: <name>"}` if any is absent, so a malformed spawn fails loudly instead
of inventing a design system.

**Why the token list and the ladder are pasted rather than pointed at — and why there is no
catalog path among the inputs.** Every other input is a path or a node id; these two are project
facts, and the agent is deliberately adapter-blind and catalog-blind — it reads no project file
it wasn't handed. An agent that reads project files is an agent whose blindness depends on which
file it happened to open. The main thread assembled the list in Setup step 3 and read the ladder
in step 4, so it pastes both into each spawn.

End every per-call prompt with this exact line — the schema sits in the agent's system prompt
rather than at the end of the prompt, and without it JSON-only compliance drifts:

```
Return only the JSON object defined in your instructions — no prose before or after.
```

**If the agent is unavailable** (Setup step 5c said so): fall back to `general-purpose` with
`model: 'sonnet'`, and build the prompt by reading `../../../agents/figma-variant-extractor.md`
and pasting **everything below its frontmatter**, then appending the seven inputs and the line
above. Never keep a second copy of the contract — read it from the one file.

**Session lifetime.** `figma-dev-mode` sessions can expire on long parallel runs. On session
loss, re-auth and **re-run only the affected variant agent** — extraction is per-variant and
idempotent.

## Phase 6 — Reconcile by concern (Opus, main thread)

The variant agents extracted locally; this pass makes each *concern* consistent across the frames
that were extracted — one color→token map (the same fill must not resolve two ways across two
variant frames), one type/spacing picture, one icon inventory. **Extract by variant, reconcile by
concern.** It reasons over already-extracted findings: no Figma re-traversal, no second MCP read.

Dedup across variants by the same tuple Phase 4 used — `(property kind, resolved value, nearest
match, axis)` — and carry the **instance count computed in Phase 2**, not a count of the frames
this phase happened to receive. That is the whole reason a narrow extraction costs the spec
nothing: the count was never a by-product of extraction. Color tolerance is
`resolution-rules.md`'s, unchanged: ΔE `< ~1–2` auto-merges, `1–5` flags "confirm intent",
`> 5` is off-system.

## Phase 7 — Pattern precedent research, one subagent per extend-component gap

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

## Phase 8 — Write the component spec (Opus, main thread)

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

Also: carry the run's capability path into the header (degraded color mode, existence source,
catalog staleness, research availability), keep every *not computable* story axis as its own row,
and diff **spec-vs-spec** against a prior spec — the local file or the previously filed item —
for the Changelog. Never spec-vs-code: reconciling against live code is the implementer's job,
and this skill stays a pure function of the component set plus the existence source.

## Phase 9 — Filing (gated — only after triage)

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
- **Given a scope issue in Setup, link the new issue as its native sub-issue.** The link is
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
- **Given a scope work item in Setup, file the spec as its child.**
- Reference PRs as `!<id>` and work items as `#<id>` in any ADO text — separate id namespaces
  there, so a `#` in front of a PR number silently points at an unrelated work item.

### End of run — report

Report the filed id and whether it was created or updated, the four-outcome triage tally, every
open item (deferred disagreements, unresearched APIs, degraded color mode, a stale or absent
catalog, any unresolved part of the token list), which variant frames were extracted and which
deliberately were not, and the run directory holding the spec. **Say plainly what the run did not
verify:** that the design is right, that an inferred component identity is correct without the
user's yes, and that the eventual code renders faithfully.
