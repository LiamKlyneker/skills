---
name: figma-component-to-spec
description: >
  Turn one Figma component set into an implementation spec for the design-system
  library that owns the component. Runs only in a `library` repo, refuses anything
  that is not a single component set, fans each variant frame out to a Sonnet region
  agent, and reads what the component already is — catalog-first, source-second —
  via the adapter's variant-mechanism ladder.
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

## Phases

Read `references/phases.md` for the phase you are running — it carries the full procedure.
Region agents are driven by `../../agents/figma-region-extractor.md`.

| Phase | Model | Does |
|---|---|---|
| **0 — Setup** | main thread | **Repo-role guard** · **node-shape gate** (one component set) · resolve catalog (arg → adapter pointer → ask) + validate against the shape contract + soft staleness check · read the `## Design system` rows this skill needs · three Figma capability checks · identify the component under spec. |
| **A — Variants are the regions** | main thread | Enumerate the component set's variant frames. One variant frame = one region = one `variant:<name>` source-node role. Coverage self-check + logged tally. |
| **B — Variant agents + current state** | `figma-tools:figma-region-extractor` (Sonnet) ×N parallel, plus main thread | One agent per variant frame → structured JSON findings. In parallel, on the main thread: what the component already is — **catalog-first, source-second** via the variant-mechanism ladder — plus computable story coverage. |
| **C — Synthesis & triage** | — | **Not in this slice.** The run ends after Phase B with the extraction bundle and the current-state read, and says so. |

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
6. **End of Phase B** → stop and report. Triage and the component spec are the next slice, and
   presenting extraction as a spec would be the failure this gate prevents.

The four extraction rules the regression fixtures protect apply here unchanged — **never
resolve a fill by hex**, **never record absolute x/y coordinates**, **never match across
property kinds**, **never enumerate the interior geometry of an icon** — and they are normative
in `../../agents/figma-region-extractor.md` and
`../figma-to-spec/references/resolution-rules.md`, never restated here.

## Idempotency & output

Re-running re-derives everything from the node: extraction is a pure function of the component
set plus the catalog. Nothing is filed in this slice, on either tracker. Write under a run
directory (suggest the scratchpad or a user-named dir); the per-variant findings and the
current-state read are the durable artifacts until Phase C lands.

Screenshots are **not** persisted — `get_screenshot` returns an inline image, not a path.
Variant agents view it inline; the layout tree plus auto-layout intent are the durable truth.

## What this skill verifies vs what it cannot

It verifies that every variant frame in the component set was extracted or explicitly pruned,
that every design property was **resolved** against the catalog, and that the component's
current state was read through the adapter's stated mechanism rather than guessed.

It cannot verify that the design is right, that an inferred component identity is correct
without the user's yes, or that the eventual code renders faithfully. One limit is specific to
this skill and worth saying plainly: **story coverage is only as computable as the story
convention allows.** An axis whose `argTypes` entry is not a select is reported *not computable
— verify manually*, and never guessed at from story export names, which are proven unreliable
as a coverage signal.
