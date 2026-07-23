# Expected findings — the pass/fail contract

One case per fixture in `fixtures.md`. Each line is a **checkable assertion** tied to the
defect it guards. Grade a run by walking the list against the produced `page-spec.md` +
region findings: every MUST has to hold. A single MUST failure = the run regressed; find
which edit caused it (the repo has per-version history — `git log`/`git bisect` the skill).

**This is run at will, not on a schedule.** Trigger it after any edit to the skill you want
to trust, or before stamping a new version. Grade by hand, or hand the produced spec + this
file to a grader agent and have it return pass/fail per line.

---

## CASE-01 — matches FIXTURE-01 (configurations list, degraded)

### B1 — hidden state-bearing nodes are NOT dropped
- [ ] **MUST** — the **expired-config warning** (the hidden warning Chip / banner on the
      list) appears in the spec, in the region's **Data states** subsection. Its absence is
      the exact silent-correctness failure v1.6.0 fixes.
- [ ] **MUST** — the region agent returns a non-empty `hiddenVariants` array for the region
      that carries it (`visible:false`, `kind: chip|banner|…`, `represents:` the state).
- [ ] **MUST** — the Phase A coverage tally is `log()`ged and reports **≥1 hidden-variant
      kept** (`N children → M regions, K excluded, J hidden-variants kept`).
- [ ] SHOULD — status chips on the cards (machine/customer indicators) are captured, not
      pruned as noise.

### B2 — enumeration descends through the content wrapper
- [ ] **MUST** — the primary node yields **≥3 content regions** (feature Top Bar, card
      list, and the card/empty affordances) — **not one mega-region**.
- [ ] **MUST** — the `SidebarNavigation` content-wrapper is **recursed into**, not emitted
      as a single region; the real regions are its descendants.
- [ ] **MUST** — the coverage self-check passes: every `get_metadata` child at every depth
      lands in a region or is listed as pruned scaffolding (nothing unaccounted for).

### Friction-3 — token crosswalk (no invented utilities)
- [ ] **MUST** — every `text-*` / `bg-*` / token emitted in the spec **exists in the
      bundled catalog**. Specifically **no `text-grey-500`** (or any `text-<primitive>`) —
      primitives are largely CSS-var-only and have no `text-*` utility home.
- [ ] SHOULD — colors resolve to the **semantic** tier where one exists (`bg-surface-*`),
      primitive-only matches are flagged, never silently accepted.

### Chrome scoping
- [ ] **MUST** — the global left nav / app `SidebarNavigation` chrome is **excluded**, while
      the feature **Top Bar** (page title + search) is kept as its **own region** (thin
      feature header ≠ global chrome).

### Degraded-mode disclosure
- [ ] **MUST** — the run **announces degraded color mode up front** (binding-read absent).
- [ ] **MUST** — **every** color carries `binding-unverified`; none is presented as
      confirmed on-system.

### Triage gate (no premature writes)
- [ ] **MUST** — the run **STOPs at the Phase C triage checkpoint**; **zero ADO writes**
      happen before the user triages (no `[SPEC]`, no PBIs auto-filed).

---

## How to read a failure

- A **B1/B2 MUST** failing = a silent-correctness regression (required content missing / a
  region collapsed). Highest severity — the spec looks complete but isn't.
- A **Friction-3 MUST** failing = the spec emits a token that doesn't exist; the implementer
  inherits a wrong value that looks on-system.
- A **gate MUST** failing = the skill wrote to ADO before human triage — a process breach,
  not just a content bug.
