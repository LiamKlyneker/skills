# Regression fixtures — pinned adversarial cases

Each fixture is a **frozen invocation** of `figma-to-spec`: the exact inputs a run gets, plus
the **capability profile** it must be run under (the same page grades differently with
binding-read present vs. absent, so the profile is part of the fixture — not an accident of
the day it was captured).

Run a fixture by invoking the skill with these inputs, then grade the produced spec against
the matching case in `expected-findings.md`. This is an **on-demand, graded re-run** — not
CI: every run needs live Figma MCP + auth, and the output is LLM-generated prose, so there's
no string to assert on. Grade line-by-line (by hand, or hand the spec + checklist to a
grader agent).

---

## FIXTURE-01 — configurations list (list + empty state), degraded color mode

The case the v1.6.0 blocker fixes were written against (see the QA report). It is the
hardest known page: it hides a required state as a `visible:false` sibling (B1) and buries
its real regions under a single content-wrapper frame (B2).

- **Run mode:** `page` (default)
- **Primary node:** `11044:27567` — configurations list (populated)
- **Additional node:** `11039:15398` — role `state:empty` — empty state
- **Scope ticket:** `#12100` (myGRIMME Core) — the `[SPEC]` files as its child
- **Freetext:** `"main configurations list, cards and its empty state"`
- **Catalog:** bundled `references/catalog.md` (no arg override)

**Capability profile (part of the fixture):**
- `figma-dev-mode` — **present** (`get_metadata`, `get_variable_defs`, `get_screenshot`,
  `get_design_context`)
- `use_figma` / `/figma-use` binding read — **absent** → run in **degraded color mode**
  (token names kept from `get_variable_defs`; every color flagged `binding-unverified`)

**Why this fixture exists:** it is the minimum reproduction of both blockers plus the token
crosswalk friction. A run that passes FIXTURE-01 proves the three highest-risk (silent-
correctness) defects stay closed. It does **not** prove the skill handles structurally
different pages — see the note at the bottom.

---

## Adding fixtures

Add a new case whenever a run surfaces a defect a current fixture doesn't reproduce — a
page shape not yet covered (form-heavy, data-table with reflow, real component instances) or
a capability profile not yet tested (binding-read **present**). One fixture per distinct
failure mode; give it a paired case in `expected-findings.md`. The current set is
deliberately `n=1` — treat that as coverage debt, not coverage.
