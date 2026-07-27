# Phase bodies

The full procedure for each phase of `figma-to-spec`. SKILL.md carries the contract, the
model tiers, the phase overview, and the STOP gates; load the section here for the phase
you are running.

Normative elsewhere, never restated here: the region-agent extraction contract and the
`bindingVerified` / degraded-color-mode rules live in `../agents/figma-region-extractor.md`; resolution
and tolerance rules in `resolution-rules.md`; existence in `catalog.md`.

---

## Phase 0 — Setup (main thread)

1. Require the Figma node URL arg. Ask if missing.
2. **Resolve `catalog.md`** — arg override → else the bundled `references/catalog.md` → else
   ask. Read it in. Then run the **skill-free staleness check** (no `grimme-ui-catalog`
   invocation needed): if `~/schmiede-one/grimme-ui` is reachable, recompute the fingerprint
   over its source-of-truth files and compare to the catalog's line-1 stamp —

   ```
   cat \
     <(sed -n '/"exports"/,/^  }/p' ~/schmiede-one/grimme-ui/package.json) \
     ~/schmiede-one/grimme-ui/theme/tokens/primitives.generated.css \
     ~/schmiede-one/grimme-ui/theme/tokens/alias.generated.css \
     ~/schmiede-one/grimme-ui/theme/tokens/semantic.generated.css \
     ~/schmiede-one/grimme-ui/theme/tokens/dimensions.generated.css \
     ~/schmiede-one/grimme-ui/system_icons/_list.tsx \
     | shasum | cut -d' ' -f1
   ```

   The inner step is `cat`, not `shasum`, so the hash is **content-only** — no file paths in
   it. It matches the `grimme-ui-catalog` recipe exactly and reproduces on any machine.

   Match → note "catalog current". Mismatch → **soft-warn** ("bundled catalog may lag live
   grimme-ui — regenerate via `grimme-ui-catalog`") and **continue**. grimme-ui not reachable
   → note "bundled snapshot, staleness unchecked" and continue. **Never hard-fail on
   staleness.** The only hard STOP here is no resolvable `catalog.md` at all.
3. **Confirm capability — three separate checks (see SKILL.md Prerequisites).** (a) Ensure
   **`figma-dev-mode`** is present — STOP if not. (b) Try to make the binding read
   (`use_figma`) available (load `/figma-use` if reachable). If it isn't, continue in
   **degraded color mode** per `../agents/figma-region-extractor.md` step 4 — and announce it up front so
   the user knows token tiers are unconfirmed. (c) Check whether the
   **`figma-region-extractor` subagent** is available (it is the first non-bundled
   dependency this skill has — it must be installed into `~/.claude/agents/`, and a
   freshly installed agent takes a few minutes to register, so a just-installed one may
   not resolve yet). Present → Phase B spawns it by type. Absent → Phase B uses the
   documented inline fallback. **Announce which path the run is taking** — a missing agent
   must never be silent.
4. **Ask the user: "Is there a separate mobile/tablet node?"** A Figma node is one
   viewport — breakpoints are not node properties. If yes, take that URL too; if no,
   responsive will be *inferred* and the assumptions flagged.
5. **Accept optional scope context** — an ADO ticket URL and/or freetext ("only the card
   grid + CTA"). This drives Phase A scoping and intent; it does **not** override canvas
   values (ticket/context = *what to look at*; Figma = *the design values*). If a ticket
   is given, fetch it and keep its ID for Phase D (the `[DESIGN-SPEC]` files as its child).

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
   - **`page` (default)** — full decompose + fan-out + full page-spec; auto-files an ADO
     `[DESIGN-SPEC]` (Phase D).
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
2. Fold in the Phase 0 scope context (ADO ticket + freetext) per the **precedence** in
   Phase 0 step 5 (freetext > ticket > heuristic) — an explicit "only the card grid"
   overrides the heuristic.
3. **Assign each region one of three dispositions:**
   - **`in-scope`** — specced *and* handed off for implementation.
   - **`spec-only`** — fully specced (blueprint, tokens, layout, gaps) but flagged **not to
     be integrated this pass** ("leave as-is / UI-only"). This is the "spec the whole page,
     but don't build part X yet" case from the Phase 0 conflict gate. It still fans out to a
     Phase B agent and still runs triage — it just carries a banner downstream so
     `develop-ticket` / a human skips integration.
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

**How to spawn (per region).** Agent tool, `subagent_type: figma-region-extractor`,
`model: 'sonnet'` passed explicitly, `run_in_background: false`. The extraction contract
lives in the agent, so the per-call prompt carries **only the six inputs** — region node ID
· region layer name · source-node role (`primary` / `viewport:<bp>` / `state:<name>`) ·
Figma file/page URL · **absolute** catalog path · **absolute** resolution-rules path. The
agent hard-STOPs with `{"error": "missing input: <name>"}` if any is absent, so a malformed
spawn fails loudly instead of hallucinating catalog contents.

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
  `Component/Variant/Size`) → match against `catalog.md` components + cva variants;
  cross-check the screenshot against the component's Storybook render. Confident →
  record `<Component props/>`. Low confidence → record as an unknown-component gap and
  **surface the parsed mapping for user confirmation**.
- **Colors / tokens** — `get_variable_defs` + the `use_figma` binding read for bound
  variable **names** (never resolve a fill by hex — that silently collapses the token
  tier). Resolve per `resolution-rules.md`: prefer **semantic** token; only a primitive
  matches → recommend it but **flag**; raw hex with no binding → nearest + **always flag**.
- **Typography, spacing** — resolve against catalog dimension/type tokens; flag off-system.
- **Icons** — layered: SystemIcon (catalog) → FontAwesome equivalent → gap (add to
  grimme-ui SystemIcon). Custom SVG → note "inline locally as interim."
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
   or a linked ADO `[DESIGN-SPEC]` is found, diff **new spec vs old spec** — spec-vs-spec, never
   spec-vs-code — and emit a **Changelog** section (what changed: tokens, props, layout,
   copy; what stayed). Mark affected regions `△ changed`. No prior baseline → note "new
   spec, no prior" and skip. Computing the *code*-level delta is the implementer's job
   (`develop-ticket` reconciles this spec against live code and touches only what differs);
   this skill stays a pure function of the Figma node.
6. **Write the spec** per `page-spec-template.md`. **Page mode:** full region-by-region
   blueprint. **Component mode:** just the one targeted region's blueprint. Either way —
   grimme-ui component + props, token per color/spacing/type, **layout/placement
   (containment tree + auto-layout intent)**, **data states** where state nodes were given,
   component states **only for new/unknown components**, responsive notes, and the
   **Changelog** from step 5 up top; gaps marked inline as `⚠ blocked on gap-NNN`; cite the
   relevant `grimme-ui-components-best-practices` rules for HOW. Record the **Scope
   dispositions** (in-scope / spec-only / excluded); prefix every `spec-only` region's
   heading with a **`spec-only — not integrated this pass`** banner so the implementer skips
   it.
7. **Write `gaps/gap-NNN-*.md`** per `gap-spec-template.md`, one per deduped gap.
8. **STOP — human triage checkpoint.** Present the gap list. The user marks each
   **build-local** vs **escalate**, and confirms/overrides every near-miss,
   suspected-intentional-deviation, and ambiguous-icon flag. **No ADO write happens
   before this.**

## Phase D — Filing (gated — only after triage)

- **Page spec → ADO `[DESIGN-SPEC]`** in **myGRIMME Core** (reuse the `to-spec` pattern). If a
  scope ticket was given in Phase 0, file the `[DESIGN-SPEC]` as its **child**. On re-run,
  search for an existing linked spec and **update** it — never duplicate. **The dedup search
  must match *either* prefix — `[DESIGN-SPEC]` or the legacy `[SPEC]`.** The prefix was
  renamed; searching only the new one would miss a spec filed under the old name and file a
  duplicate, breaking the zero-new-tickets guarantee. On finding a legacy `[SPEC]`, update it
  in place **and retitle it** to `[DESIGN-SPEC]`. Only new tickets are created with
  `[DESIGN-SPEC]`. *(Component mode files nothing by default — no `[DESIGN-SPEC]`, no PBIs —
  unless the user explicitly asks; it produces local artifacts only.)*
- **Escalated gaps → PBIs** in **GRIMME Libraries**. First **query available work-item
  types** (ADO MCP) to confirm PBI exists; **search the backlog** (title / fingerprint)
  to avoid duplicates; file only new ones; **write the returned work-item IDs back**
  into the gap spec files and into the page spec's inline `blocked on gap-NNN` markers.
- **Build-local gaps** are not filed — the page spec's interim-fallback field carries the
  local recommendation + a `TODO` marker (codemod-friendly API note so it's swappable to
  the DS component later).

Reference PRs as `!<id>` and work items as `#<id>` in any ADO text (separate ID
namespaces — see `~/schmiede-one/CLAUDE.md`).
