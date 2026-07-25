---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead — and for anything beyond a single known file, **don't explore on this (the main) thread**: fan the exploration out to recon subagents first (next section). This thread is the orchestrator and the interviewer; it does not do the raw digging.

Project facts (repo names, explorer agents, token map, access-policy source) come from `../_shared/project-adapter.md` — read it first; never hardcode project specifics in this skill.

## Recon fan-out (run FIRST — gated)

Before interviewing, delegate exploration to a small set of **read-only Sonnet-class subagents**, each scoped to one area, each returning a **condensed brief (~1–2K tokens, never raw file dumps)**. This keeps this thread's context full of *dialogue*, not code — the fix for both recurring failures: shallow exploration that misses details on bigger repos or across a service boundary, and asking me questions the code already answers.

**Gate — run recon IF any of:** the plan crosses the project's contract boundary (the related repo/service named in the adapter), OR it spans ≥2 areas/features, OR an area is large/unfamiliar, OR a question needs external/web knowledge. **SKIP** for a single-known-file change or a pure copy/visual one-off — say you skipped it and why, and fall back to loading `CONTEXT.md` inline (see Context Loading).

**Decompose** the plan into **2–5** areas (one per decision-tree branch / codebase area) — do **not** over-split; over-spawning is the top anti-pattern. Map each area to a lane and spawn all lanes in **one parallel batch** (one message, multiple `Agent` calls):

| Lane | Agent (`subagent_type`) | Owns |
|------|-------------------------|------|
| Project code | the **project explorer** named in the adapter (fallback: `Explore`) | this repo — one feature/package area per agent |
| Contract boundary | the **contract-boundary explorer** named in the adapter (fallback: `general-purpose`) | the sibling repo / service that owns the API contract or data layer. Spawn **exactly one**; skip entirely if the adapter lists no related repo. |
| External web | `web-researcher` | open web — library/API behavior, platform guidelines, best practice, pricing |

- **Web-research rule:** when a question can't be answered from the codebase and needs the open web, delegate to `web-researcher` — **never run web searches inline on this thread**, and don't invent a grill-specific research agent.
- **Task-prompt template (per agent):** every spawn states **objective · scope/sources (which dirs/repo) · output format · explicit non-goals** — the non-goals are what stop two parallel explorers from covering the same ground. Keep each prompt's *scope* tight; state read-only + report-once + condense discipline in the prompt if the agent definition doesn't already carry it.

**Each brief returns fixed sections**: (1) patterns/conventions found (`file:line`), (2) **already answered by the code** — questions this area settles, with the precedent as evidence, (3) genuinely-open questions, (4) manifest feedstock (UI Primitive + Token candidate rows; contract/access rows from the boundary lane).

**Consolidate on this thread** before interviewing:
- **Surface a short "Resolved by the code" list up-front** — the questions recon settled, each with its precedent. Do **not** silently drop them: I can reopen any row if a precedent is stale or wrong. Everything on this list is a question you will *not* ask.
- The **open-questions** set drives the interview.
- The **manifest feedstock** pre-populates the hard-gate tables below, so those gates *confirm* rather than build from scratch.

Guardrails: cap ≈5 explorers; don't split exploration into artificial sub-phases; explorers report only at completion (no mid-task coordination); every explorer is read-only; briefs stay condensed.

## Context Loading

**When recon ran, this is already done** — each explorer reads its area's scoped `CONTEXT.md` first, so this thread does **not** bulk-load them. This section is the **fallback for recon-skipped grills**: if the `scoped-context` skill is available, use it to load the relevant `CONTEXT.md` files before interviewing. If it isn't, read them directly.

**Conditionally load the design source of truth:** if (and only if) this grill implements from a Figma file or other visual design, resolve primitives and tokens against the project's real component library via its UI-profile skill or Figma → code map (named in the adapter / `CLAUDE.md`) — hard traps live there, not here. **Skip it for pure-data / logic grills** — it's noise there.

**Conditionally load the access-policy source of truth:** if (and only if) this grill's planned code **reads or writes a table**, inspect the live access policies before the interview, from the source the adapter names (migrations, a policy console, or an MCP that can list per-operation policies). This feeds the Data & Access Manifest below. **Skip it for grills whose code touches no table at all** (pure visual/copy/client-only) — mirror of the UI manifests' scoping.

## Design-to-code triage (run before engineering questions)

When the task involves implementing from a Figma file or other visual design, do this **before** asking any implementation/architecture questions. **Recon boundary:** explorers are *code-only* — they can seed the primitive/token side from the component library, but **enumerating visual variants and states from the design stays on this thread**. Don't expect an explorer to have walked the pixels.

1. **Enumerate every distinct visual variant and state.** Do not generalize from one screenshot. Walk every state the view can be in — loading, empty, error, populated, signed-out vs signed-in. If the user shares a single Figma URL or node, ask whether sibling/child nodes cover variants you haven't seen, and fetch screenshots of each one.
2. **Build a variant table.** For every variant (per-card, per-section, per-state) capture: base color, gradient/decoration colors, direction/origin, intensity, any texture or blend. Present the table back to the user and ask them to confirm or correct it before moving on.
3. **Propose a vertical slice, not a horizontal plan.** Recommend picking one representative variant, implementing it end-to-end (including the reusable primitive's API), and only then propagating to the rest. Iterating on real pixels for one card will shape the primitive's knobs far better than enumerating everything up-front. Confirm with the user before locking in a multi-section plan.
4. **Record the design-reference pointers.** For every distinct area/screen, capture the node **URL** and its **node name** (from `get_metadata`). These flow downstream into the PRD's `## Design reference` and, after build, into the page's `CONTEXT.md` `## Design reference` table — so a cold implementation/verify session can find the target with zero conversation context.

## Manifest gates (HARD GATES — design tasks only)

Right after the variant table, build the **UI Primitive Manifest** and the **Token Manifest** per `../_shared/ui-manifests.md` — full classification rules (✅/⚠️/❌, "earn the abstraction" homes, never-improvise-a-token) and table formats live there. In this skill both run **interactively**: present each table back to the user and resolve every ⚠️/❌ row during the interview.

**Start from the recon feedstock** — the explorer briefs already proposed candidate rows. Confirm and interrogate them and fill gaps; don't build the tables cold.

Both are **hard gates**: do not conclude the grill while any primitive or token row is unresolved.

Only after the variant table, both manifests, and the vertical-slice approach are agreed on should engineering questions (motion tech, perf gates, breakpoints, reduced-motion, etc.) begin.

## Data & Access Manifest (HARD GATE — data tasks only)

Run this for any grill whose planned code **reads or writes a table** — a new table, new columns, **or a new CRUD operation on a table the code already uses**. That last case is the one that bites: adding an UPDATE or DELETE to a table that until now was only ever SELECTed/INSERTed is *not* a schema change, so it slips past every "does the schema shape change?" check — and a default-deny access policy then **silently** blocks the write. Real instance: a conversations table shipped with only SELECT and INSERT policies, so every timestamp bump and every delete was denied for months without one error surfacing.

Where the UI manifests catch improvised *components/tokens*, this catches improvised *data access* — the write path nobody checked was actually permitted. **Skip it only for grills whose code touches no table at all** (pure visual/copy/client-only). Do not self-exempt by feel: if you can't say "the planned code touches zero tables," run the manifest.

Enumerate **every** table the planned code touches, one row **per CRUD operation actually exercised** — SELECT / INSERT / UPDATE / DELETE, each checked independently (a table with a SELECT policy is *not* "covered" for UPDATE). For each row, resolve before the grill is "done":

- **Client** — which client runs the op: **user-scoped** (access policy applies) or **privileged / service-role** (policy bypassed, e.g. cron/GC jobs). Get this wrong in either direction and you lose: a user-scoped write with no matching policy is silently blocked; a privileged write where user-scoping was intended is an accidentally-unscoped write. Name the client per row.
- **Access policy exists for *this* operation?** — not "the table has policies," but specifically a policy for *this* operation matching the acting user, verified against the source the adapter names. A missing policy on a user-scoped op is a ⚠️ that needs a migration **before** the feature ships. For privileged ops the policy is bypassed by design — mark n/a and confirm the bypass is intentional.
- **State/status transitions** — if the op writes a status or state-machine column, confirm the allowed transitions match the DB constraint or an app-level guard. Grep for an existing transition map before inventing one.
- **Errors are checked, not swallowed** — the write path must inspect the failure the data client returns and surface it, never return void. A swallowed error is exactly what lets an access-policy gap ship invisibly. Every write row must confirm the caller checks it.

This is a **hard gate**: do not conclude the grill while any row is ⚠️ (gap) or ❌ (unchecked). Present the manifest back to the user as a table and get confirmation:

| Table | Operation | Client | Access policy exists? | Status |
|-------|-----------|--------|-----------------------|--------|
| conversations | UPDATE | user-scoped | ❌ no update policy | ⚠️ blocks silently — needs migration |
| ops | UPDATE (status) | user-scoped | ✅ owner-scoped policy | ✅ covered — transitions guarded |
| ops | UPDATE (GC reap) | privileged (cron) | n/a — bypassed by design | ✅ covered — bypass intended, error checked |

Status ∈ ✅ covered / ⚠️ gap (needs migration or fix) / ❌ unchecked (policy state not yet verified — must resolve). Only after every row is ✅ is the Data & Access Manifest done.
