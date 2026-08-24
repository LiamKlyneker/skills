---
name: deep-grill
description: >
  Interview the user relentlessly about a plan until every branch of the decision
  tree is resolved — always fanning the exploration out to read-only recon subagents
  first, so every question is grounded in the code instead of guessed. Invoke
  /deep-grill.
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
- **No spec, but the work is design-driven?** Say so and recommend producing the design spec first rather than improvising the design side mid-interview. Grill the engineering decisions that don't depend on it in the meantime.
- **Prior PRDs, issues, ADRs.** Ask for pointers and read them; a decision already recorded is not an open question.

Carry the spec pointers through the interview — whatever this grill feeds downstream should be able to reference the design spec by URL/node rather than restating it.

## Recon fan-out (spawn FIRST — always; don't block on it)

Delegate exploration to a small set of **read-only Sonnet-class subagents**, each scoped to one area, each returning a **condensed brief (~1–2K tokens, never raw file dumps)**. This keeps this thread's context full of *dialogue*, not code — the fix for both recurring failures: shallow exploration that misses details on bigger repos or across a service boundary, and asking me questions the code already answers.

**This step is unconditional.** Invoking this skill *is* the request for grounded questions, so there is no path that skips recon and interviews from guesses. A narrow plan scales the fan-out **down**, never to zero.

**Spawning the batch is a barrier; *finishing* it is not.** A running explorer is one unsettled prerequisite, not a stop-the-world. So spawn every lane, then open the first round immediately with whatever is already askable — the plan's framing, scope and intent, the decisions no explorer could settle anyway. Only the questions downstream of a given area wait for that area's brief. Fold each brief in as it lands and recompute the frontier.

**Decompose** the plan into **1–5** areas (one per decision-tree branch / codebase area) — do **not** over-split; over-spawning is the top anti-pattern, and a single-area plan is one explorer, not three. Map each area to a lane and spawn all lanes in **one parallel batch** (one message, multiple `Agent` calls):

| Lane | Agent (`subagent_type`) | Owns |
|------|-------------------------|------|
| Project code | the **project explorer** named in the adapter (fallback: `Explore`) | this repo — one feature/package area per agent |
| Contract boundary | the **contract-boundary explorer** named in the adapter (fallback: `general-purpose`) | the sibling repo / service that owns the API contract or data layer. Spawn **exactly one**; skip entirely if the adapter lists no related repo. |
| External web | `web-researcher` | open web — library/API behavior, platform guidelines, best practice, pricing |

- **Web-research rule:** when a question can't be answered from the codebase and needs the open web, delegate to `web-researcher` — **never run web searches inline on this thread**, and don't invent a grill-specific research agent.
- **Task-prompt template (per agent):** every spawn states **objective · scope/sources (which dirs/repo) · output format · explicit non-goals** — the non-goals are what stop two parallel explorers from covering the same ground. Keep each prompt's *scope* tight; state read-only + report-once + condense discipline in the prompt if the agent definition doesn't already carry it.

**Each brief returns fixed sections**: (1) patterns/conventions found (`file:line`), (2) **already answered by the code** — questions this area settles, with the precedent as evidence, (3) genuinely-open questions, (4) manifest feedstock (contract/access rows from the boundary lane — tables touched, clients used, policies observed).

**Consolidate on this thread** as each brief lands — before the round that depends on it, not before the interview starts:
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

## Done

The interview is done when the frontier is empty **and** every gate row above is ✅ — every branch of the design tree visited, every store/operation resolved, nothing left silently assumed. A ⚠️ or ❌ row is an unsettled decision like any other: it keeps the frontier non-empty. **Do not act on the plan until I confirm we have reached shared understanding.**
