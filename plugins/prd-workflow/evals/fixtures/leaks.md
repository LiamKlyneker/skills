# Leaks the hand capture reproduced

One hand run of `prototype-to-spec` → `deep-grill` → `to-task` against the Vitrine fixture,
scored against the leaks the same chain produced on real work. Each line is one case the hop
cases are built from: what the leak is, in fixture vocabulary, and what the run actually
produced instead.

The three frozen artifacts of that run are `brief.md` and `issue.md` beside this file, and the
grill transcript at `evals/grill-history.jsonl` in the fixture repository.

## Brief hop — `prototype-to-spec`

- did not reproduce: brief reads only the spec files and skips the per-element handoff and the component source — the brief cites `design_handoff_shelf_picker/README.md` and 12 `.tsx:L` source slices
- did not reproduce: a composite classified `exact` by name match while its default chrome differs from the still — `ComboboxCommandInput` and `ComboboxContent` are classed `DS with overrides` / `DS change`, only primitives are `exact`
- did not reproduce: no source-slice fetch line per `local component` / `DS with overrides` row — the issue carries 24 fetch lines
- did not reproduce: stale handoff copy wins over the spec — "No shelves found." wins in both the brief and the issue

## Grill hop — `deep-grill`

- did not reproduce: grill inherits the brief's confidence and never puts the composite-vs-still delta in front of the human — Q4 to Q10 each asked one per non-`DS as-is` row with the DS default chrome spelled out
- did not reproduce: grill recon surfaces current-app classes and they land in the issue as design facts — no `w-72`, `px-4`, `h-10` or `py-3` appears in the issue's `## Changes`, and no "already matches" claim appears anywhere
- reproduced (grill, new): the grill recommended a DS change filed as a blocker for the search band (Q5) while rejecting a blocker for one panel (Q4) and one row (Q9) in the same round — the human overrode to overrides plus known deltas

## Issue hop — `to-task`

- did not reproduce: `to-task` re-summarises the ledger into a shorter layout column and loses facts — all 9 ledger rows are verbatim in the issue across all 9 brief columns; the issue adds `Decision` and `Instruction` only
- did not reproduce: `to-task` names a DS component the ledger's candidate column did not name, or invents keyboard behaviour — none found

## Across every hop

- did not reproduce: an icon renamed to its conventional name on any hop — `TallyMarkIcon`, `LoupeGlassIcon`, `DustCoverIcon`, `NewNicheIcon` survive brief and issue; no `CheckIcon` / `SearchIcon` / `PlusIcon`
- did not reproduce: consumer vocabulary in a fixture artifact — none in the brief or the issue

## Not exercised by this capture

- implementer self-audit against the ledger (`work-on-task`) and the app-side L3 render — both belong to the `work-on-task` hop
