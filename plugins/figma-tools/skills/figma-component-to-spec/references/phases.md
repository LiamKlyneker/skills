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

### End of Phase B — stop and report

This slice ends here. Report:

- the per-variant findings bundle (one entry per `variant:<name>` region),
- the coverage tally from Phase A,
- the current-state read: catalog axes and values, what came from source and how, and **every
  disagreement, unresolved**,
- story coverage per axis, including every *not computable* axis,
- and which capability path the run took (agent type resolved or fallback; degraded color mode
  or not; catalog current, stale, or unchecked).

**Do not synthesise, do not triage, and do not present any of this as a component spec.**
Synthesis, the human triage checkpoint, and the spec template are the next slice.
