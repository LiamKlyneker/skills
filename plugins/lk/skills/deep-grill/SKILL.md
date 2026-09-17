---
name: deep-grill
description: >
  Interview the user relentlessly about a plan until every branch of the decision
  tree is resolved — always fanning the exploration out to read-only recon subagents
  first, so every question is grounded in the code instead of guessed. Carries the
  fidelity-ledger rules: one round-one question per non-`DS as-is` ledger row with
  the screenshot read, an evidence rule for "already matches" claims, a per-state
  container rule, and a `## Fidelity decisions` block at consensus. Invoke
  /lk:deep-grill.
disable-model-invocation: true
---

# Deep Grill

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Map it as a **design tree**: every decision branches into the decisions that hang off it.

## Rounds and the frontier

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for my answers before the next.

A question whose answer depends on another question still open in this round belongs to a **later** round. Each round of answers reshapes the tree: recompute the frontier and ask again.

**A round is numbered questions, never a form.** Each carries its own recommended answer. Asking me to fill in a table or mark up a list is not a round — that hands back the reconciliation the recon fan-out below exists to do for me.

```
❓ **Q1** — **<question title>**: <question body — may be several paragraphs, and may offer choices>

➡️ <your recommended answer, and one line on why>

---

❓ **Q2** — **<question title>**: <question body>

➡️ <your recommended answer, and one line on why>
```

**Facts are your job, never mine.** If a question can be answered by exploring the codebase, explore instead of asking — and for anything beyond a single known file, **don't explore on this (the main) thread**: fan the exploration out to recon subagents (below). This thread is the orchestrator and the interviewer; it does not do the raw digging.

Project facts (repo names, explorer agents, access-policy source) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it first; never hardcode project specifics in this skill. Its `## Project gates` table also tells you which **extra hard gates** this project runs alongside the Data & Access Manifest below; run each one whose trigger this plan matches, following the adapter's pointer to it. Never assume a gate file's name — a project that registers none has none.

## Inputs — grill *from* the specs, don't rebuild them

Before anything else, ask what already exists and read it. A grill that re-derives a document someone already wrote wastes the interview on settled questions.

- **Design spec.** If the work implements from a design and a spec already exists, **read it and grill from it**. The variants, states, tokens, primitives and design-system gaps are resolved there — treat those rows as answers, not as questions, and quote the spec when a decision leans on one. Do **not** re-enumerate variants or rebuild primitive/token manifests on this thread; that is the spec's job and duplicating it invites two conflicting sources of truth.
- **Design brief.** A path to a design brief is the same kind of input, produced either by `figma-tools:prototype-to-spec` from a designer's code prototype or by `figma-tools:figma-to-brief` from a design canvas. Read it the same way, with one addition: **its `## Element → DS mapping` rows carry a confidence, and the confidence decides what happens to the row.**

  | Confidence | Treated as | In the interview |
  |---|---|---|
  | `exact` | resolved by the brief | **never asked.** It goes on the "Resolved by the code" list with the brief as its precedent, exactly like a recon finding. |
  | `likely` | a proposal | **one confirm question each, batched into a single round-one item.** Not one question per row — a table of proposals confirmed in one exchange. |
  | `OPEN` | a real decision | **a round-one question**, with the three standard answers below. |

  Rows under `## DS gaps (proposed, not filed)` are round-one questions on the same terms. Nothing in a brief has been filed anywhere, so every one of them is still open.

  The three standard answers to an `OPEN` element or a proposed gap, and they are the same three either way:
  1. **Build it local**, colocated, per the primitive-home ladder.
  2. **Extend or build it in the design system**, and file the gap on the adapter's DS-gap backlog **as a blocker** — which is what makes it a ❌/⚠️ row in the PRD's `## UI Primitives`, and therefore a blocking issue when `to-issues` runs.
  3. **Override the prototype** — the ticket is allowed to disagree with it, and frequently should.

  A brief's `## Overrides` section is **facts, not questions**. The ticket already won there; re-asking hands back a decision that was made before the brief was written.

  **The `## Fidelity ledger` outranks the mapping confidence.** A brief may also carry a `## Fidelity ledger` section: one row per visual element, with its states, its exact copy, its tokens, its layout facts in words, its source — a source line range in the prototype, or a Figma node `<fileKey>:<nodeId>` — the DS candidate, and a **fidelity class** — `DS as-is` / `DS with overrides` / `local component` / `DS change` / `OPEN`. The confidence table above measures name match; the ledger measures visual match. Where both describe the same element, the ledger wins. A row marked `exact` in `## Element → DS mapping` but not `DS as-is` in the ledger is **still asked**.

  **Every ledger row whose class is not `DS as-is` is its own round-one question.** One question per row. Do not batch them, do not fold several rows into one table, and do not treat a `DS with overrides` row as a confirm — each row is a real decision with its own screenshot. Each such question must:

  1. **Name the element and the state(s)** the row covers.
  2. **Describe the DS candidate's default chrome** — what the component renders out of the box (checkboxes, "Select All", group headers, trigger styling, its own search input, its own padding). Take this from the catalog overlay's "Default chrome" note for that component; if the overlay is silent, take it from the ledger's notes. Never assume a composite renders nothing of its own.
  3. **State the ledger's layout facts** — stack direction, divider placement, padding owner, row anatomy, radius — in the ledger's own words, so the delta between the DS default and the design is visible in the question itself.
  4. **Offer the standard answers**: (a) use the DS component as-is; (b) use it **with overrides** — and the question names which override; (c) **build local**; (d) **change the DS** and file the gap on the adapter's DS-gap backlog as a blocker; (e) **override the design** — the ticket wins over the prototype.

  **A container decision is stated per state (HARD RULE).** When the ledger holds two or more states, every decision about a **container** around ledger elements — a page shell, a panel, a section card, a list wrapper, the page surface — is stated per state. A decision read off one state's frame names that state, and says explicitly what every other state gets, including "no container" where the other state draws none. **A per-state disagreement on a container fact is its own round-one question**: when the ledger's rows say one state binds a fill, a radius, a padding or a border and another state does not, ask that disagreement separately from the per-row questions above, and quote both states' cells in the question. Reason: a tab-bar row held a container fill for one state and "binds no fill" for the other; the grill wrote one page-wide panel decision off the first state's frame, and the second state shipped inside a panel its design never draws.

  **Read the screenshot before asking.** For every such row, read the design as an image, one image per state: for a prototype brief, fetch the raw PNG at the brief's pinned SHA into the scratchpad; for a canvas brief, open the PNG the brief saved on disk for that state, at the screenshot path its pin line carries (`.claude/briefs/<ticket>/screenshots/<state>.png`). Then write the question from what the design shows — not from what the brief's prose says. A question written without the image describes the text, and the text is the thing that already lost fidelity once.

  **Evidence rule for "matches" claims (HARD RULE).** A claim of the form "this already matches the design" — in an answer, in a recon brief, or in your own consolidation — is accepted **only** if it cites either (a) a ledger row whose fidelity class is `DS as-is`, or (b) a render: a screenshot of the running app next to the design. **A class name, a component name, or a prop read out of the repo's source is not evidence of a visual match.** Source recon proves which component is mounted; it proves nothing about what that component paints. When the only support for a "matches" claim is code recon, mark the row unresolved and ask it. Reason: Run 0 wrote false "already matches" facts ("multi-select already matches", "separators match the design") into an implementation issue straight out of code recon, and every one of those elements failed its screenshot pair. The same bar applies to layout: a class name or a component name surfaced by recon is **not a layout fact** — the ledger is. Recon may state "the app currently renders X"; it may never state "the design is X", and a class it found may never be carried into a decision, an answer or anything this grill hands downstream. Reason: Run 1's recon surfaced the current `sui-min-w-[120px]` label width, which then reached the issue as the design's fixed 124px column and shipped wrong.

- **No spec or brief, but the work is design-driven?** Say so and recommend producing one first rather than improvising the design side mid-interview — `figma-tools:figma-to-spec` for a spec from a canvas, `figma-tools:figma-to-brief` for a brief from a canvas, `figma-tools:prototype-to-spec` for a brief from a designer's code prototype. Grill the engineering decisions that don't depend on it in the meantime.
- **Prior PRDs, issues, ADRs.** Ask for pointers and read them; a decision already recorded is not an open question.

Carry the pointers through the interview — whatever this grill feeds downstream should be able to reference the design source rather than restating it. From a spec that means the URL and node; **from a brief it means its pin line and its screenshots** — a `Source: <repo>@<sha>` line with screenshot URLs pinned at that SHA for a prototype brief, or a `Pinned at figma <fileKey> · node <nodeId> · version <versionId or YYYY-MM-DD> · brief <path>` line with the saved PNG paths pinned at that version for a canvas brief. Either form is what lets the PRD's `## Design reference` point at something that cannot move.

## Recon fan-out (spawn FIRST — always; the interview waits for it)

Delegate exploration to a small set of **read-only Sonnet-class subagents**, each scoped to one area, each returning a **condensed brief (~1–2K tokens, never raw file dumps)**. This keeps this thread's context full of *dialogue*, not code — the fix for both recurring failures: shallow exploration that misses details on bigger repos or across a service boundary, and asking me questions the code already answers.

**This step is unconditional.** Invoking this skill *is* the request for grounded questions, so there is no path that skips recon and interviews from guesses. A narrow plan scales the fan-out **down**, never to zero.

**The whole batch is a barrier — spawning it *and* finishing it.** Spawn every lane at once, then wait: **Round 1 does not open until every brief has landed and been folded in**, and the "Resolved by the code" list below is built. There is no pre-recon round, not even for framing, scope or intent.

That costs you a couple of minutes of my time with nothing to answer, and it is worth it. The alternative — opening with "whatever is already askable" — assumes you can tell which questions recon is about to settle, and you can't: knowing a question is code-answerable means already knowing what the code says, which is the thing you spawned the explorers to find out. A round that guesses wrong has to be retracted, and I get two rounds where one would have done. Real instance: 6 questions went out before the briefs landed, 3 came back settled by the code and a 4th changed shape entirely, so the whole round was superseded.

Once the briefs are in, fold them all in at once and compute the frontier from the consolidated picture.

**Decompose** the plan into **1–5** areas (one per decision-tree branch / codebase area) — do **not** over-split; over-spawning is the top anti-pattern, and a single-area plan is one explorer, not three. Map each area to a lane and spawn all lanes in **one parallel batch** (one message, multiple `Agent` calls):

| Lane | Agent (`subagent_type`) | Owns |
|------|-------------------------|------|
| Project code | the **project explorer** named in the adapter (fallback: `Explore`) | this repo — one feature/package area per agent |
| Contract boundary | the **contract-boundary explorer** named in the adapter (fallback: `general-purpose`) | the sibling repo / service that owns the API contract or data layer. Spawn **exactly one**; skip entirely if the adapter lists no related repo. |
| External web | `web-researcher` | open web — library/API behavior, platform guidelines, best practice, pricing |

- **Web-research rule:** when a question can't be answered from the codebase and needs the open web, delegate to `web-researcher` — **never run web searches inline on this thread**, and don't invent a grill-specific research agent.
- **Task-prompt template (per agent):** every spawn states **objective · scope/sources (which dirs/repo) · output format · explicit non-goals** — the non-goals are what stop two parallel explorers from covering the same ground. Keep each prompt's *scope* tight; state read-only + report-once + condense discipline in the prompt if the agent definition doesn't already carry it.

**Each brief returns fixed sections**: (1) patterns/conventions found (`file:line`), (2) **already answered by the code** — questions this area settles, with the precedent as evidence, (3) genuinely-open questions, (4) manifest feedstock (contract/access rows from the boundary lane — tables touched, clients used, policies observed).

**Consolidate on this thread** once every brief is in, before Round 1:
- **Surface a short "Resolved by the code" list up-front** — the questions recon settled, each with its precedent. Do **not** silently drop them: I can reopen any row if a precedent is stale or wrong. Everything on this list is a question you will *not* ask.
- The **open-questions** set drives the interview.
- The **manifest feedstock** pre-populates the Data & Access Manifest below, so that gate *confirms* rather than builds from scratch.

Guardrails: cap ≈5 explorers; don't split exploration into artificial sub-phases; explorers report only at completion (no mid-task coordination); every explorer is read-only; briefs stay condensed.

## Context Loading

**Recon covers this** — each explorer reads its own area's scoped `CONTEXT.md` before reporting, and the architectural context arrives folded into its brief. This thread does **not** bulk-load `CONTEXT.md` files itself; state the requirement in each spawn prompt instead.

**Conditionally load the access-policy source of truth:** if (and only if) this grill's planned code **reads or writes stored data**, inspect the live access policies before the interview, from the source the adapter names (migrations, an IaC definition, a policy console, or an MCP that can list per-operation policies). This feeds the Data & Access Manifest below. **Skip it for grills whose code touches no stored data at all** (pure visual/copy/client-only). If the adapter names no access-policy source and the plan does touch data, say so and ask where policies live rather than running the gate against nothing.

## Data & Access Manifest (HARD GATE — data tasks only)

Run this for any grill whose planned code **reads or writes stored data** — a new collection/table, new fields, **or a new operation on a store the code already uses**. That last case is the one that bites: adding a write or a delete to a store that until now was only ever read from and appended to is *not* a schema change, so it slips past every "does the schema shape change?" check — and a default-deny access policy then **silently** blocks the write. Real instance: a table shipped with read and create policies only, so every timestamp bump and every delete was denied for months without one error surfacing.

This catches improvised *data access* — the write path nobody checked was actually permitted. **Skip it only for grills whose code touches no stored data at all** (pure visual/copy/client-only). Do not self-exempt by feel: if you can't say "the planned code reads and writes nothing," run the manifest.

**Where the policy lives is per-project** — row-level policies in the database, rules on a document store, IAM on a bucket or queue, authorization middleware in front of an API. The adapter's access-policy source names it. If enforcement is in application code rather than the data layer, the manifest is unchanged; only the place you verify each row moves.

Enumerate **every** store the planned code touches, one row **per operation actually exercised** — read / create / update / delete, in whatever verbs the stack uses, each checked independently (a store with a read policy is *not* "covered" for update). For each row, resolve before the grill is "done":

- **Client** — which client runs the op: **user-scoped** (access policy applies) or **privileged** (policy bypassed — an admin key, service credential, or trusted backend job such as a cron/GC task). Get this wrong in either direction and you lose: a user-scoped write with no matching policy is silently blocked; a privileged write where user-scoping was intended is an accidentally-unscoped write. Name the client per row.
- **Access policy exists for *this* operation?** — not "the store has policies," but specifically a policy for *this* operation matching the acting user, verified against the source the adapter names. A missing policy on a user-scoped op is a ⚠️ that must be fixed **before** the feature ships, however that project ships policy changes (a migration, an IaC change, a console edit). For privileged ops the policy is bypassed by design — mark n/a and confirm the bypass is intentional.
- **State/status transitions** — if the op writes a status or state-machine field, confirm the allowed transitions match the store-level constraint or an app-level guard. Grep for an existing transition map before inventing one.
- **Errors are checked, not swallowed** — a denied write must reach the caller and be surfaced. Which failure to hunt for depends on the client: one that **returns** errors (a result/error pair) fails by having the result ignored and returning void; one that **throws** fails by a `catch` that logs and continues. Establish which shape this project's data client uses, then confirm every write row handles that shape. A swallowed error is exactly what lets an access-policy gap ship invisibly.

This is a **hard gate**: do not conclude the grill while any row is ⚠️ (gap) or ❌ (unchecked). Present the manifest back to the user as a table and get confirmation:

| Store | Operation | Client | Access policy exists? | Status |
|-------|-----------|--------|-----------------------|--------|
| `<record>` | update | user-scoped | ❌ none for update | ⚠️ blocks silently — needs a policy change |
| `<job>` | update (status) | user-scoped | ✅ owner-scoped policy | ✅ covered — transitions guarded |
| `<job>` | delete (cleanup) | privileged (scheduled job) | n/a — bypassed by design | ✅ covered — bypass intended, error checked |

Status ∈ ✅ covered / ⚠️ gap (needs a policy change or code fix) / ❌ unchecked (policy state not yet verified — must resolve). Only after every row is ✅ is the Data & Access Manifest done.

## Project gates (HARD GATES — whatever the adapter registers)

The manifest above is the gate every project gets. A project may register **its own** gates in the adapter's `## Project gates` table — the same shape, catching a silent-failure class specific to that stack (an API contract the app can drift from, a platform review rule). Read that table, run every gate whose trigger this plan matches, and treat each exactly like the one above: enumerate rows, resolve each, don't conclude the grill while any row is ⚠️/❌. The gate file itself carries its row schema; this skill never names one.

## Consensus output — `## Fidelity decisions`

When the brief carried a `## Fidelity ledger`, the grill's closing summary ends with a short `## Fidelity decisions` block: **one line per ledger row**, carrying the decided fidelity class and, where the decision was `DS with overrides`, the named override. This is the handoff — a downstream `/prd-workflow:to-task` or `/prd-workflow:to-prd` skill pastes this block verbatim into the issue as the per-element build instruction, so every row must be phrased as an instruction, not as a discussion.

Every ledger row appears, including the rows that stayed `DS as-is`. A row missing from this block is a row the implementer will decide alone.

**A container decision is one line per state, and it names its source row.** A decision about a container around ledger elements — a page shell, a panel, a section card, a list wrapper, the page surface — belongs in this block even where no ledger row holds the container itself. Its `State(s)` cell names the state the decision was read off; its `Override / note` cell says what every other state gets, including "no container" where the design draws none, and cites the ledger row it came from by that row's Element and States. A container line that claims every state without the other state's frame read is the defect this rule stops.

**An added visual property is marked.** A decision that adds a visual property the ledger does not hold for that row — a shadow, a border, a background, a radius, a hover surface — writes it in the `Override / note` cell as `added — not in the design: <property>`. A silent addition is a defect: this marker is what the implementer and the judge read to tell a decided addition from a leak. A property the row's own cells already hold needs no marker, because it is a fact rather than an addition.

```
## Fidelity decisions

| Element | State(s) | Decision | Override / note |
|---|---|---|---|
| <element> | <states> | DS as-is — `<Component>` | — |
| <element> | <states> | DS with overrides — `<Component>` | <the named override, e.g. hide Select All; divider on the row, not the container> |
| <element> | <states> | Build local | <what it replaces, and why the DS composite was rejected> |
| <element> | <states> | DS change | gap filed: <backlog ref> — blocker |
| <element> | <states> | Override the design | <what the ticket does instead> |
| <container> | <the state it was read off> | <decision> | <what every other state gets> — from ledger row <element> / <states> |
| <element> | <states> | Build local | <what it replaces> · added — not in the design: <property> |
```

## Done

The interview is done when the frontier is empty **and** every gate row above is ✅ — every branch of the design tree visited, every store/operation resolved, nothing left silently assumed. A ⚠️ or ❌ row is an unsettled decision like any other: it keeps the frontier non-empty. **Do not act on the plan until I confirm we have reached shared understanding.**
