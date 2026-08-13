# Phase bodies

The full procedure for each phase of `figma-to-spec`. SKILL.md carries the contract, the
model tiers, the phase overview, and the STOP gates; load the section here for the phase
you are running.

Normative elsewhere, never restated here: the region-agent extraction contract and the
`bindingVerified` / degraded-color-mode rules live in `../agents/figma-region-extractor.md`; resolution
and tolerance rules in `resolution-rules.md`; the required shape of a project catalog in
`catalog-contract.md`; existence itself in the project catalog Phase 0 resolves.

---

## Phase 0 — Setup (main thread)

**Before step 1 — the repo-role guard, and it is a STOP.** Read
`<repo-root>/.claude/project/adapter.md`, `## Design system`, the `Repo role:` row, before any
Figma read.

- **`consumer`, or no `Repo role:` row at all** → continue with step 1. **An absent row means
  `consumer`**, so every adapter written before that row existed — and every project that never
  answered the question — runs this skill exactly as it always did. Absence is the answer here,
  never a warning and never a question.
- **`library`** → **stop**, with one line and nothing else:

  > This repo's `Repo role:` is `library` — it *is* the design system, so a page spec written
  > here would file gaps against itself. Use `figma-tools:figma-component-to-spec` instead.

  Not a warning, not overridable, and not automatable past: a library repo has no DS-gap
  backlog to escalate to that isn't itself, so a run here produces a spec whose whole triage
  vocabulary is wrong. Never offer to rewrite the row to keep the run alive — the role is an
  intent and the row is its record.

This is the mirror image of `figma-component-to-spec`'s Phase 1 step 1, which refuses in a
`consumer` repo and names this skill. Exactly one of the pair runs in any given repo.

1. Require the Figma node URL arg. Ask if missing. **Record the file's version id or
   last-modified timestamp** as you first reach the file — whichever the tooling exposes,
   both when both are. It is the baseline the page spec pins (`page-spec-template.md`'s
   `Extracted against:` line) and the thing a later design-QA pass compares against; captured
   at the end of a run it would already be a different value. Unavailable → carry
   `unknown — <why>` forward rather than dropping it.
2. **Resolve, validate, then staleness-check the project catalog** — three parts, in this
   order. The catalog is a **per-project artifact in the consuming repo**, never a file inside
   this plugin.

   **2a — Resolve: passed arg → the adapter's registered catalog pointer → ask the user.** In
   that order, and no further: resolution stops at *ask*, with no fallback beyond it. The
   pointer lives in `<repo-root>/.claude/project/adapter.md`'s `## Design system` section,
   registered the same way a gate is registered in `## Project gates` — **that registry is the
   only place the catalog is named.** Never hardcode a catalog filename or path here, and
   never reconstruct one by reading the design system's source at run time. Read the resolved
   file in.

   **2b — Validate against `catalog-contract.md`. Hard STOP on failure.** Run that file's
   numbered validation rules **before any Figma read**. A malformed catalog fails **loudly and
   specifically**: name the resolved path, the rule that failed, and what to change, then offer
   the two ways forward (fix the catalog, or point the run at a different one). Never degrade,
   never proceed on partial data, and never infer a missing section from the design system's
   source — a spec built on a half-read catalog reads as fully resolved, which is exactly the
   failure this gate exists to prevent.

   **2c — Staleness: soft, never fatal.** If the adapter registers a **fingerprint command**
   for this design system, run it and compare the result to the catalog's line-1 stamp. Match
   → note "catalog current". Mismatch → **soft-warn** ("catalog may lag the live design system
   — regenerate it") and **continue**. No fingerprint command registered, or the design-system
   source unreachable → note "staleness unchecked" and continue. **Never hard-fail on
   staleness.** The only hard STOPs in this area are 2a and 2b: no resolvable catalog at all,
   and a catalog that fails the shape contract.

   **2d — While the adapter is open, read the rest of `## Design system` and keep it.** The
   *icon resolution ladder* is needed verbatim by every Phase B spawn (the region agent never
   reads the adapter itself), the three *class-prefix* rows settle what form a spec may
   recommend, and the two optional rows — *usage-rules source*, *downstream implementer* —
   decide what the page spec cites and who picks it up. **An absent optional row is the answer,
   not a warning.** A missing icon ladder is different: with icon sources in the catalog and no
   stated order, ask the user rather than picking one.
3. **Confirm capability — three separate checks (see SKILL.md Prerequisites).** (a) Ensure
   **`figma-dev-mode`** is present — STOP if not. (b) Try to make the binding read
   (`use_figma`) available (load `/figma-use` if reachable). If it isn't, continue in
   **degraded color mode** per `../agents/figma-region-extractor.md` step 4 — and announce it up front so
   the user knows token tiers are unconfirmed. (c) Check whether the
   **`figma-region-extractor` subagent** is available, **under either type name**:
   `figma-tools:figma-region-extractor` when the `figma-tools` plugin provides it (the
   normal route), or the bare `figma-region-extractor` when it was hand-placed in an
   `agents/` directory. Registration happens at session start, so a just-installed plugin
   or a just-added file may not resolve until the next session. Present → Phase B spawns it
   by the name that resolved. Absent under **both** names → Phase B uses the documented
   inline fallback. **Announce which path the run is taking** — a missing agent must never
   be silent.
4. **Ask the user: "Is there a separate mobile/tablet node?"** A Figma node is one
   viewport — breakpoints are not node properties. If yes, take that URL too; if no,
   responsive will be *inferred* and the assumptions flagged.
5. **Accept optional scope context** — a **scope ticket** URL and/or freetext ("only the card
   grid + CTA"). The ticket is whatever this project's tracker calls one: a GitHub issue or an
   ADO work item, per the adapter's `Tracker:` line. This drives Phase A scoping and intent; it
   does **not** override canvas values (ticket/context = *what to look at*; Figma = *the design
   values*). If a ticket is given, fetch it and keep its id for Phase D, which files the
   `[DESIGN-SPEC]` under it — as a native sub-issue on GitHub, as a child work item on ADO.

   **Scope precedence:** freetext (the most recent explicit human instruction) **>** ticket
   scope **>** the Phase A layer-name heuristic. The ticket is context/default; freetext
   overrides it.

   **Conflict gate (STOP and ask — don't silently pick).** Two conflicts surface here, both
   cheap to resolve before any fan-out:
   - **Scope conflict:** the ticket scopes narrower/differently than the freetext (e.g. the
     ticket is "1/4" — search only — while the freetext also names create-button +
     card-actions from sibling stories). Surface both and ask which governs. Offer the
     third option the user may actually want: **spec the wider set, but mark the
     out-of-ticket regions `spec-only`** (fully specced, *not* integrated this pass — see
     Phase A dispositions).
   - **Node canonicity:** the ticket links a different primary node than the invocation URL.
     Default recommendation: the **invocation node** is the design source (Figma = values).
     Ask whether to (a) use the given node, (b) switch to the ticket's node, or (c) treat
     them as multiple nodes by role (step 6). Never assume.
6. **Accept additional nodes by role.** One implementation can span several nodes. Each
   extra node URL carries a role, read from the freetext context, on one of two axes:
   - **`viewport:*`** (mobile / tablet) — same design, different breakpoint (see step 4).
   - **`state:*`** (empty / loading / error / …) — same viewport, different **data state**
     (e.g. a populated list node + its empty-state node).
   Keep the axes separate: viewport nodes feed responsive notes; state nodes feed the
   region's **Data states** (Phase C). Infer the role from context; if ambiguous, ask —
   never merge a data-state node into the mobile/viewport slot.
7. **Determine the run mode — from the prompt, not the node.** Node geometry can *suggest*
   granularity but cannot tell you *intent* (a Card node might be a fresh build or a
   one-line padding tweak). Read the mode from the invocation:
   - **`page` (default)** — full decompose + fan-out + full page-spec; auto-files a
     `[DESIGN-SPEC]` on the adapter's tracker (Phase D).
   - **`component` (lean)** — the prompt scopes to a single node / component ("lean
     update", "single-component / single-node", "only X changed", "just this node",
     "already implemented — give me the delta"). No fan-out; emit a lean **component-delta
     spec** (one region blueprint + changelog); **files nothing unless the user explicitly
     asks** (local artifacts only); the triage checkpoint still runs — never silently
     accept an off-system value, even for one node.
   Node structure (child count / depth via `get_metadata`) is only a sanity check. If the
   prompt is silent and the node looks like a lone component, **confirm — don't assume**.

## Phase A — Decompose & scope (Sonnet)

`get_metadata` on the page node → enumerate region sub-nodes (hero, card grid, CTA,
table, form, footer, …). Produce a **region list with node IDs**. Do **not** feed the
whole page to one agent — the Figma MCP degrades badly on whole-page selections. One
region = one node ID = one downstream agent.

**Enumeration depth — descend through pass-through wrappers; don't stop at depth-1.** A
page node's direct child is often a single content-wrapper frame (e.g. `SidebarNavigation`,
`Content`, `Frame 427`) that holds every real region as a grandchild. Enumerating depth-1
there yields **one mega-region** and defeats the extract-by-region design. Rule: **if a node
has a single dominant content child (or a chrome-plus-one-wrapper shape), recurse into it;
treat a node with mixed, heterogeneous children (a top bar + a list + a CTA) as the region
boundary and stop.** Descend until you hit that boundary, then each heterogeneous child is
its own region.

**Completeness self-check (before fan-out).** After enumerating, assert coverage: every
`get_metadata` child — **visible and state-bearing hidden** (per `../agents/figma-region-extractor.md`),
at every depth — must land in exactly one region with a disposition, OR be explicitly listed
as pruned scaffolding. If any node is unaccounted for, you collapsed a wrapper or dropped a
hidden state — recurse again. `log()` the coverage tally (`N children → M regions, K
excluded, J hidden-variants kept`) so a miss is visible rather than silent. This is the guard
for the two failure modes above.

Then **scope** the list — a page node arrives with app chrome (left navbar, global
header/footer) that is noise for a feature spec:

1. Classify each region **content** vs **app-chrome** — heuristics on layer names
   (`Navbar`, `Sidebar`, `TopBar`, `Footer`), pinned/fixed position, and "repeats on
   every page" shape.
   - **Granularity / thin sub-headers:** a *thin* structural header that carries
     page-**feature** content (e.g. a feature "Top Bar" with the page title + a search
     field) is its **own region**, not chrome. A *repeated global* bar is chrome. When a
     node is genuinely ambiguous (neither clearly a region nor chrome), default to
     **including it as a region and `log()` the call**; only pause to ask if scope is fuzzy.
2. Fold in the Phase 0 scope context (scope ticket + freetext) per the **precedence** in
   Phase 0 step 5 (freetext > ticket > heuristic) — an explicit "only the card grid"
   overrides the heuristic.
3. **Assign each region one of three dispositions:**
   - **`in-scope`** — specced *and* handed off for implementation.
   - **`spec-only`** — fully specced (blueprint, tokens, layout, gaps) but flagged **not to
     be integrated this pass** ("leave as-is / UI-only"). This is the "spec the whole page,
     but don't build part X yet" case from the Phase 0 conflict gate. It still fans out to a
     Phase B agent and still runs triage — it just carries a banner downstream so the
     implementer (the adapter's *downstream implementer*, or a human) skips integration.
   - **`excluded`** — app chrome or clearly out of scope; not specced.
4. **Auto-skip when scope is explicit:** if the context names dispositions unambiguously,
   proceed and simply **`log()`** the `spec-only` and `excluded` regions. Only **pause for
   confirmation** when scope is fuzzy — present the annotated in-scope / spec-only / excluded
   list.
5. **Record the accepted dispositions** — they go into `page-spec.md` as a "Scope
   dispositions" note (in-scope / spec-only / excluded) so re-runs are deterministic and the
   scope is auditable.

Decompose **each provided node** (primary + any `viewport:*` / `state:*` nodes) this way,
and tag every resulting region with its source-node role so Phase C can group the same
region across viewports / data states. **`in-scope` and `spec-only` regions fan out to
Phase B; `excluded` regions do not.**

In **component mode** there is nothing to fan out: the node *is* the single region — skip
enumeration and hand it straight to one Phase B agent.

## Phase B — Region agents (Sonnet ×N, parallel)

One agent per region, each scoped to its sub-node, driven by
`../agents/figma-region-extractor.md` — which is normative for the call discipline, the
extraction contract, and the return schema. Each performs full extraction and returns
**structured findings** (the JSON schema in that file, so synthesis merges
deterministically).

**How to spawn (per region).** Agent tool, `subagent_type: figma-tools:figma-region-extractor`
(the plugin namespaces it; a hand-placed `agents/` file registers the bare
`figma-region-extractor` instead — try the namespaced name first),
`model: 'sonnet'` passed explicitly, `run_in_background: false`. The extraction contract
lives in the agent, so the per-call prompt carries **only the seven inputs** — region node ID
· region layer name · source-node role (`primary` / `viewport:<bp>` / `state:<name>`) ·
Figma file/page URL · **absolute** catalog path · **absolute** resolution-rules path · the
adapter's **icon resolution ladder, pasted verbatim**. The agent hard-STOPs with
`{"error": "missing input: <name>"}` if any is absent, so a malformed spawn fails loudly
instead of hallucinating catalog contents.

**Why the ladder is pasted rather than pointed at.** Every other input is a path or a node id;
this one is a project fact, and the agent is deliberately adapter-blind — it reads no project
file it wasn't handed. The main thread has already read the adapter in Phase 0, so it pastes
the row's text into each spawn. A ladder the plugin restated instead would be one
organisation's icon module shipped to every consumer.

End every per-call prompt with this exact line — the schema now sits in the agent's system
prompt rather than at the end of the prompt, and without it JSON-only compliance drifts:

```
Return only the JSON object defined in your instructions — no prose before or after.
```

**If the agent is unavailable** (Phase 0 step 3c said so): fall back to `general-purpose`
with `model: 'sonnet'`, and build the prompt by reading `../agents/figma-region-extractor.md`
and pasting **everything below its frontmatter**, then appending the six inputs and the line
above. Never keep a second copy of the contract — read it from the one file.

**What each agent extracts** (normative detail in the agent file; summarized here so this
phase reads standalone):

- **Component match** — infer from the Figma layer name (e.g. slash-separated
  `Component/Variant/Size`) → match against the catalog's components + their variant axes;
  cross-check the screenshot against however the project renders that component. Confident →
  record `<Component props/>`. Low confidence → record as an unknown-component gap and
  **surface the parsed mapping for user confirmation**.
- **Colors / tokens** — `get_variable_defs` + the `use_figma` binding read for bound
  variable **names** (never resolve a fill by hex — that silently collapses the token
  tier). Resolve per `resolution-rules.md`: prefer the **most-derived tier the catalog
  offers**; only a primitive/alias matches → recommend it but **flag**; raw hex with no
  binding → nearest + **always flag**.
- **Typography, spacing** — resolve against catalog dimension/type tokens; flag off-system.
- **Icons** — walk the adapter's **icon resolution ladder**, in its order, stopping at the
  first source that matches; the catalog says what each source contains. A no-match becomes
  whatever the ladder's last step says (typically a DS gap for a reusable icon, a local inline
  for a one-off). The ladder reaches the agent as an input, verbatim — it is never restated in
  this plugin.
- **Layout / placement** — capture the region's containment tree, child order, and
  **auto-layout intent** (direction, gap token, alignment, wrap) so an implementer can
  place every element without a screenshot. Capture *relative* intent, never absolute
  x/y coordinates (input-vs-output rule in `../agents/figma-region-extractor.md`).
  `get_screenshot` is viewed inline by the agent as a visual check during extraction; under
  `figma-dev-mode` it returns an inline image, **not a file path**, so it is **not
  persisted** — the layout tree is the source of truth, not a saved image.

**Session lifetime.** `figma-dev-mode` sessions can expire on long parallel runs (~10–15
min/agent). The call ordering (`get_design_context` LAST) front-loads the essential reads
so a late failure is non-fatal. On session loss, re-auth and **re-run only the affected
region agent** — extraction is per-region and idempotent.

## Phase C — Synthesis & triage (Opus, main thread or one Opus agent)

1. **Dedup / aggregate** gaps across regions by tuple `(property type, resolved value,
   nearest match, component)`. Color tolerance (CIELAB ΔE): `< ~1–2` → auto-merge (same,
   no gap); `1–5` → flag "confirm intent"; `> 5` → off-system gap. One gap = one ticket,
   carrying an aggregated consumer/instance count.
2. **Reconcile by concern.** Region agents extract locally; this pass makes each *concern*
   consistent across the whole page — one color→token map (the same hex must not resolve
   two ways), one component inventory, one type/spacing scale. Principle: **extract by
   region, reconcile by concern.** It reasons over already-extracted findings — no Figma
   re-traversal, no whole-page MCP read.
3. **Merge data states — from both sources.** A region's data states arrive two ways, and
   both feed the same **Data states** subsection (populated / empty / loading / error /
   warning): (a) **separate `state:*` nodes** — group regions that are the same region across
   them (e.g. populated list + empty-state list); (b) **`hiddenVariants`** returned within a
   single region — the `visible:false` state-bearing nodes (a warning banner, status chip,
   empty block) the region agent kept. Fold every hidden variant into its region's Data
   states; never let one vanish because it wasn't a separate node URL. This is a
   page/region-level content state — distinct from DS-owned component states, which stay
   DS-owned.
4. **Responsive** — if a mobile node was given, merge responsive notes; otherwise infer
   (table reflow, minor stacking) and record the assumptions explicitly.
5. **Changelog / delta (if a prior spec exists).** If a previous `page-spec.md` (run-dir)
   or a previously filed `[DESIGN-SPEC]` is found, diff **new spec vs old spec** — spec-vs-spec, never
   spec-vs-code — and emit a **Changelog** section (what changed: tokens, props, layout,
   copy; what stayed). Mark affected regions `△ changed`. No prior baseline → note "new
   spec, no prior" and skip. Computing the *code*-level delta is the implementer's job — the
   adapter's *downstream implementer* (or a human) reconciles this spec against live code and
   touches only what differs; this skill stays a pure function of the Figma node.
6. **Write the spec** per `page-spec-template.md`. **Page mode:** full region-by-region
   blueprint. **Component mode:** just the one targeted region's blueprint. Either way —
   catalog component + props, token per color/spacing/type, **layout/placement
   (containment tree + auto-layout intent)**, **data states** where state nodes were given,
   component states **only for new/unknown components**, responsive notes, and the
   **Changelog** from step 5 up top; gaps marked inline as `⚠ blocked on gap-NNN`; cite the
   relevant rules of the adapter's *usage-rules source* for HOW, by stable name, and cite
   nothing where no such row exists. Record the **Scope dispositions** (in-scope / spec-only /
   excluded); prefix every `spec-only` region's heading with a **`spec-only — not integrated
   this pass`** banner so the implementer skips it.
7. **Write `gaps/gap-NNN-*.md`** per `gap-spec-template.md`, one per deduped gap.
8. **STOP — human triage checkpoint.** Present the gap list. The user marks each one
   **escalate** / **compose-from-tokens** / **build-local** (the three outcomes in
   `resolution-rules.md`), answering the question that separates them: *is this genuinely
   reusable across the product, or inherently one-off to this design?* They also
   confirm/override every near-miss, suspected-intentional-deviation and ambiguous-icon flag,
   and decide **match-as-is vs modernize** on each legacy flag. **Record a one-line rationale
   in the gap file for every non-escalated decision** — that line plus the written-back IDs is
   what stops the next run re-litigating a deviation already settled. **No tracker write
   happens before this** — on either tracker, in either run mode.

## Phase D — Filing (gated — only after triage)

**Filing is tracker-parametric. Read the adapter before writing anything.** Two things decide
where this phase files, both in `<repo-root>/.claude/project/adapter.md` and neither of them
in this file:

1. **The `Tracker:` line** in `## Repo` — `github` or `azure-devops`, and **an absent line
   means `github`**. It selects one of the two profiles below; run that one and ignore the
   other entirely.
2. **Two filing rows**, inside that tracker's `###` sub-section of `## Repo`:
   - **design-spec target** — where the page spec files.
   - **DS-gap backlog** — where an escalated gap files.

   **They are separate rows and they routinely name different places**, because a design
   system's gaps belong to the design system rather than to the code being specced. Never file
   one against the other's row, and never infer either from the repo you happen to be running
   in. A row that is missing is a question for the user, not a default to invent.

Three things are true on both trackers, so they are stated once here:

- **Component mode files nothing by default** — no page spec, no gap tickets — unless the user
  explicitly asks. It produces local artifacts only, and it still triages.
- **Build-local gaps are not filed.** The page spec's interim-fallback field carries the local
  recommendation + a `TODO` marker (codemod-friendly API note so it's swappable to the DS
  component later).
- **Compose-from-tokens gaps are not filed either**, and there is nothing to build: the page
  spec carries the composition (which existing tokens, in what arrangement) so the implementer
  never reaches for a raw value. Both non-escalated outcomes still keep their gap file,
  carrying the triage rationale — the file is the record that the deviation was settled.

Whichever profile runs, **write every returned id back** into the gap spec files and into the
page spec's inline `blocked on gap-NNN` markers. That write-back plus the dedup search is the
entire zero-new-tickets guarantee on a re-run.

### GitHub profile (`Tracker: github`, or no `Tracker:` line)

- **Page spec → a `[DESIGN-SPEC]` issue** on the **design-spec target** repo, via `gh`.
- **If Phase 0 was given a scope issue, link the new issue as its native sub-issue.** The link
  is what makes it a child — the body carries **no `## Parent` section**, because a
  hand-written parent beside a real link is a second source of truth that can disagree.
  The mechanics are documented once, in `prd-workflow`'s `to-issues` skill under *Link each
  child to the PRD as a native sub-issue*: create → link → **verify**, three `gh api` calls,
  and `sub_issue_id` takes the issue's **internal numeric `id`** (`--jq .id`), never its issue
  number — passing the number returns a bare `404` indistinguishable from "no such issue".
  Follow that file; do not reconstruct the sequence here. A `POST` that succeeded is not
  evidence the link landed — read the parent's sub-issue list back and say so out loud.
- **Dedup on re-run:** search the design-spec target's issues for this node's existing spec and
  **update it in place — never open a second.** Match **either** prefix, `[DESIGN-SPEC]` or the
  legacy `[SPEC]`; on a legacy hit, update it **and retitle it** to `[DESIGN-SPEC]`. Only new
  issues are created with `[DESIGN-SPEC]`.
- **Escalated gaps → issues on the DS-gap backlog repo**, one per gap. Search that repo's
  issues first (title / fingerprint) and file only the new ones. These are *not* sub-issues of
  the page spec: a gap is the design system's work, tracked where the design system is.

### Azure DevOps profile (`Tracker: azure-devops`)

- **Page spec → an ADO `[DESIGN-SPEC]`** work item in the **design-spec target** project (reuse
  the `to-spec` pattern). If a scope ticket was given in Phase 0, file the `[DESIGN-SPEC]` as
  its **child**. On re-run, search for an existing linked spec and **update** it — never
  duplicate. **The dedup search must match *either* prefix — `[DESIGN-SPEC]` or the legacy
  `[SPEC]`.** The prefix was renamed; searching only the new one would miss a spec filed under
  the old name and file a duplicate, breaking the zero-new-tickets guarantee. On finding a
  legacy `[SPEC]`, update it in place **and retitle it** to `[DESIGN-SPEC]`. Only new tickets
  are created with `[DESIGN-SPEC]`.
- **Escalated gaps → PBIs** on the **DS-gap backlog** project. First **query available
  work-item types** (ADO MCP) to confirm PBI exists; **search the backlog** (title /
  fingerprint) to avoid duplicates; file only new ones.
- Reference PRs as `!<id>` and work items as `#<id>` in any ADO text — they are separate id
  namespaces there, so a `#` in front of a PR number silently points at an unrelated work item.
