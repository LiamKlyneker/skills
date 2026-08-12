# Expected findings — the pass/fail contract

One case per fixture in `fixtures.md`. This file documents the **assertion style**; like the
fixture format it is plugin-side, while the concrete cases are per-project and live wherever
that project keeps its fixtures.

## The style

- **One case per fixture, cited by the fixture's ID.** A case with no fixture grades nothing;
  a fixture with no case cannot be graded.
- **Every line is a single checkable assertion**, written as a tickable `- [ ]` box, and tied
  to the defect it guards. "The spec looks right" is not an assertion.
- **`MUST` vs `SHOULD`.** A `MUST` failing means the run regressed — stop and find the edit
  that caused it (`git log` / `git bisect` the skill; the repo has per-version history). A
  `SHOULD` is a quality signal that is worth reading but does not fail the run.
- **Name the artifact each line is graded against** — the produced `page-spec.md`, a gap file,
  or the **raw region-agent findings**. These disagree, and that disagreement is itself
  informative: synthesis re-flagging something an agent got wrong is diligence, not a pass.
  Grade the raw findings wherever the assertion is about extraction.
- **Assert on the property, not on the prose.** The output is LLM-generated, so a line that
  requires an exact word will fail on a run that was correct. Grade "a per-card state chip
  surfaces in Data states", not "the word *expired* appears".
- **Assert absences explicitly.** Several of the rules below are only visible as things that
  *didn't* happen (no cross-kind token match, no gap for a legacy component, no findings for
  vector interiors). An absence nobody wrote down is an absence nobody checks.
- **Run at will, and as the pre-release step in `fixtures.md`** — after any edit to the skill
  you want to trust, before a version is stamped. Grade by hand, or hand the produced spec
  plus this file to a grader agent and have it return pass/fail per line.

## Assertions any case should carry

Rule-level lines every project's case is expected to include, adapted to its own catalog and
page. These guard the rules in `../resolution-rules.md` and the region-agent contract, so they
are the ones a rule edit is most likely to break:

- **Property-scoped matching** — no value resolves to a token of a different property kind: no
  stroke width resolving to a layout spacing step, no text color resolving to a background/
  surface token. Graded on the raw findings, where each resolved value carries the
  `propertyKind` it was filtered on.
- **Legacy resolution, not false-gapping** — a design element matching a catalog entry stamped
  `legacy` / `deprecated` appears as **resolved + flagged** with its successor named, and
  produces **no gap file**. A gap for a component the catalog contains is a `MUST` failure.
- **Vector-geometry exclusion** — an icon or illustration produces no color/spacing findings
  for its interior path data, while its **own box size and applied color** still resolve
  normally. Both halves are asserted; the exclusion swallowing the usage-site color is its own
  regression.
- **Version pin** — the page spec's `Extracted against:` line carries a Figma file version or
  last-modified timestamp (or an explicit `unknown — <why>`), never nothing.
- **Triage outcomes and rationale** — the checkpoint offers all three outcomes, and every
  non-escalated gap file carries a one-line rationale. A blank rationale on a
  compose-from-tokens or build-local decision is a failure: it is what a re-run reads to avoid
  re-litigating the deviation.
- **No invented vocabulary** — every token, utility and variant value emitted in the spec
  exists in the catalog the run resolved.
- **Triage gate** — zero tracker writes happen before the human triages.

## How to read a failure

- A **silent-correctness `MUST`** failing (required content missing, a region collapsed, a
  value resolved to the wrong property kind) is the highest severity: the spec looks complete
  and isn't, so nobody catches it by reading.
- A **vocabulary `MUST`** failing means the spec emits something that doesn't exist; the
  implementer inherits a wrong value that looks on-system.
- A **gate `MUST`** failing means the skill wrote to the tracker before human triage — a
  process breach, not just a content bug.

---

## Worked example — CASE-01, matching FIXTURE-01 (configurations list, degraded)

Illustrative, and specific to that project's page and catalog. It shows the style applied.

### B1 — hidden state-bearing nodes are NOT dropped
- [ ] **MUST** — a **hidden status/warning Chip representing a per-card config state** (the
      list encodes an expired/outdated-configuration state as a `visible:false` Chip/banner)
      lands in the spec's region **Data states** subsection. Grade on *a per-card config
      state Chip surfacing*, not on the literal word "expired" — the hidden Chips carry no
      tool-extractable text, so the label is inferred from position + warning tokens. Its
      absence is the exact silent-correctness failure v1.6.0 fixes.
- [ ] **MUST** — the region agent returns a non-empty `hiddenVariants` array for the region
      that carries it (`visible:false`, `kind: chip|banner|…`, `represents:` the state).
- [ ] **MUST** — the Phase A coverage tally is `log()`ged and reports **≥1 hidden-variant
      kept** (`N children → M regions, K excluded, J hidden-variants kept`).
- [ ] SHOULD — status chips on the cards (machine/customer indicators) are captured, not
      pruned as noise.

### B2 — enumeration descends through the content wrapper
- [ ] **MUST** — the primary node yields **≥3 content regions** — expected: **Top Bar**,
      **search/filter row**, **card list** (+ an **empty state** region off the state node)
      — **not one mega-region**. Grade on the ≥3 count against the actual regions above.
- [ ] **MUST** — the **`Side bar` content wrapper (`11044:27568`)** is **recursed into**,
      not emitted as a single region; the real regions are its descendants. (Do not confuse
      it with the separately-named global **`Sidebar Navigation` (`11044:27681`)**, which is
      chrome and MUST be excluded — see Chrome scoping below.)
- [ ] **MUST** — the coverage self-check passes: every `get_metadata` child at every depth
      lands in a region or is listed as pruned scaffolding (nothing unaccounted for).

### Friction-3 — token crosswalk (no invented utilities)
- [ ] **MUST** — every `text-*` / `bg-*` / token emitted in the spec **exists in the
      catalog the run resolved**. Specifically **no `text-<primitive>`** — primitives are
      largely CSS-var-only and have no `text-*` utility home.
- [ ] SHOULD — colors resolve to the **semantic** tier where one exists (`bg-surface-*`),
      primitive-only matches are flagged, never silently accepted.

### Property-scoped matching (graded on the raw findings — an absence)
- [ ] **MUST** — **no stroke or border width resolves to a layout spacing step**, and **no
      text color resolves to a surface/background token**. Every resolved value carries the
      `propertyKind` it was filtered on; a value whose resolved token belongs to another kind
      is a failure even when the numbers match exactly.
- [ ] **MUST** — where the catalog has **no token of the required kind**, the finding is a gap
      or a Tailwind-scale layout value — never a borrowed token from another kind.

### Legacy awareness (no false gaps)
- [ ] **MUST** — any element matching a catalog entry stamped `legacy` / `deprecated`
      resolves with `flagReason: "legacy-entry"` and reads "on-system but legacy; successor
      is X" (or "no successor recorded"), and **no gap file is written for it**.

### Vector geometry
- [ ] **MUST** — no color/spacing/dimension findings are emitted for the **interior paths** of
      icon nodes; `notes` records that the exclusion was applied.
- [ ] **MUST** — each icon's **own box size** and **applied color** still resolve normally.

### Version pin
- [ ] **MUST** — `page-spec.md` carries an `Extracted against:` line with a Figma file version
      and/or last-modified timestamp, or an explicit `unknown — <why>`.

### Chrome scoping
- [ ] **MUST** — the global left nav / app `SidebarNavigation` chrome is **excluded**, while
      the feature **Top Bar** (page title + search) is kept as its **own region** (thin
      feature header ≠ global chrome).

### Degraded-mode disclosure
- [ ] **MUST** — the run **announces degraded color mode up front** (binding-read absent).
- [ ] **MUST** — in the **region-agent raw findings** (the source of truth, not just the
      synthesized spec), **every** color object carries `bindingVerified: false` with
      `status: "flag"` + `flagReason: "binding-unverified"`. None is presented as confirmed
      on-system (`status:"resolves"` / `bindingVerified:true` = FAIL). Check the raw findings
      because agent output and synthesis can disagree — synthesis re-flagging a leak is
      diligence, not a pass. Mechanically checkable: `bindingVerified` is a required,
      non-droppable field in the region-agent schema.

### Triage gate (no premature writes)
- [ ] **MUST** — the run **STOPs at the Phase C triage checkpoint**; **zero ADO writes**
      happen before the user triages (no `[DESIGN-SPEC]`, no PBIs auto-filed).
- [ ] **MUST** — the checkpoint offers **three** outcomes (build-local / compose-from-tokens /
      escalate) and asks the reusable-vs-one-off question; every non-escalated gap file carries
      a one-line rationale.
