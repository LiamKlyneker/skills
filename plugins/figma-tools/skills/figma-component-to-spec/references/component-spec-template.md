# Component spec template

Fill this in **Phase 8**, from the reconciled findings. It is **the run's single artifact** — one
component spec per component set — filed in **Phase 9** as a plain `[SPEC]` work item (ADO) or an ordinary issue
(GitHub), and sliced from there by the tracker's existing chain (`ado-workflow:to-spec-tasks`,
`prd-workflow:to-issues`) with no new machinery.

**There is no `gaps/` directory, and one must never be produced.** In a consumer repo a gap
file exists because the gap belongs to *someone else's* backlog and travels there without the
page spec. Here the gap and the spec are the same document: the thing that is missing is missing
from **this** repo, and the work of adding it is the work this spec describes. So every gap is a
**section** below — a row in *Variant axes*, a line in *Token delta*, an item in *Figma fixes* —
and the triage rationale that would have lived in a gap file lives in *Triage record*. A second
artifact would give the same decision two homes that can disagree.

**One thing in this template varies by project, and only one: how literal the token delta may
be.** That is the adapter's `## Design system` → *Token pipeline* row, read in **Phase 1** and
applied in **Phase 8** — a generator plus its source file means the spec states the **literal source
edit**; no generator means a **coordinated file-edit list**, every file that must change
together, named. Both shapes are written out below. Pick the one the row dictates and delete the
other. Never pick by looking at the repo.

**The `Extracted against:` line is required and is not decoration.** A spec is a snapshot of a
Figma file that keeps moving; without the version it was read at, a later reviewer cannot tell an
implementation defect from a design that changed after the spec was written, and the Changelog
below stops being a diff between two known design states. Record whichever the tooling exposes
(version id preferred, last-modified timestamp otherwise), both when both are. Neither readable →
write `unknown — <why>`; never drop the line.

---

# <Component> — component spec

**Figma component set:** <url> · **node id:** `<id>` · **Scope ticket:** <#id | "none">
**Token-list entry:** `<entry name>` | **new component — no entry**
**Generated:** <YYYY-MM-DD> · **Filed as:** <tracker id once filed | "not yet filed">
**Extracted against:** Figma file version `<version id>` · last modified `<ISO timestamp>`
**Extraction coverage:** <K> of <N> variant frames extracted — see *Extraction coverage*
**Run capabilities:** color binding <verified | ⚠ degraded — token tiers unconfirmed> · catalog
<current | ⚠ may lag the design system | staleness unchecked> · pattern research <performed |
⚠ unavailable — reason>

## Changelog

*(update runs only — omit for a brand-new spec)* Diffed **spec-vs-spec** against the prior
baseline, never against code:

- <axis / prop / token>: <old> → <new>

Unchanged: <everything else>. No prior baseline → "n/a — new spec".

## Overview

<2–4 sentences: what the component is, which axes the Figma set draws, and the posture — how
much of it the library already expresses and what has to change for the rest.>

## Extraction coverage

**Which variant frames this spec was written from, and which it deliberately was not.** A run
extracts only the frames the Phase 4 triage checkpoint kept, so a spec written from 3 of 24
frames is **normal** — but it reads as a scoping decision only if it says so, and reads as full
coverage otherwise. **Never omit this section**, and never write "full coverage" as shorthand
for a kept set that happened to be everything: write `24 of 24`.

| Variant frame | Role | Extracted | Why not |
|---|---|---|---|
| `1234:5678` — Variant=Primary, Size=Medium | `variant:Variant=Primary,Size=Medium` | yes | — |
| `1234:5690` — Variant=Secondary, Size=Large | `variant:Variant=Secondary,Size=Large` | **no** | triaged already-expressible — no unresolved value pointed at this frame |
| `1234:5702` — Variant=Destructive, Size=Small | `variant:Variant=Destructive,Size=Small` | **no** | dropped when the budget guard narrowed the triage (Phase 5.1) |

**What a narrow extraction does not cost this spec.** *Variant axes* below — the axes, their
values, drawn-vs-cross-product and the instance counts — is **computed from the variant lattice**
that Setup's single root `get_metadata` returned, before any frame was extracted. Per-frame
extraction feeds exactly two sections, *Token delta* and *Figma fixes*, and only those two narrow
with the kept set.

**Instance counts are computed, never observed.** Every count below is lattice arithmetic — how
many variant frames a value appears in across the **drawn** set — and never a count of frames
this run extracted. A count derived from extracted frames shrinks with the triage and tells a
reviewer the opposite of the truth about how load-bearing a value is.

| Axis | Value | Instances (computed) |
|---|---|---|
| `variant` | `primary` | 4 |
| `size` | `md` | 6 |

**Two absences this section exists to keep honest**, because from the outside both look exactly
like a clean result: a value whose drawn frames all went un-extracted carries **no** *Token
delta* and **no** *Figma fixes* findings, and that silence is **not** evidence it is on-system;
and a frame skipped because the budget guard narrowed the triage is recorded here with that as
its reason, never dressed up as a design judgement.

## Variant axes

**Existing vs. to-add, in one table.** *Existing* is the Phase 3 current-state read (**source
first, catalog as cross-check**); *drawn* is what the Figma component set actually contains. A
value in both columns is already expressible and changes nothing.

| Axis (library) | Axis (Figma) | Existing values | Drawn in Figma | To add | Outcome | Source of "existing" |
|---|---|---|---|---|---|---|
| `variant` | `Variant` | `primary`, `secondary` (`legacy`, successor `subtle`) | Primary, Secondary, Destructive | `destructive` | extend-component | catalog, cross-checked in source |
| `size` | `Size` | `sm`, `md`, `lg` | Medium, Large | — | already-expressible | catalog |

- **The axis-name mapping is a finding, not a preprocessing step.** Figma's vocabulary and the
  library's are recorded side by side because a rename is itself a decision someone made; a spec
  that silently translates one into the other destroys the evidence for it.
- **A value the library has and Figma does not draw is not a gap** — record it in the row and
  say so. A design system routinely draws a deliberate subset.
- **Status travels with the value.** A `legacy` / `deprecated` existing value carries its
  status and `successor:` here, plus the triage call made on it: **match-as-is** (spec the
  legacy value, it ships) or **modernize** (spec the successor). A modernize decision produces
  extend-component / extend-tokens rows *in this same spec* — never a second artifact.
- **How many times a value is drawn is in *Extraction coverage* above, and it is computed from
  the lattice** — never a count of the frames this run extracted.
- **A Phase 3 catalog-vs-source disagreement never appears silently resolved.** It appears as a
  row whose "Source of existing" cell reads `⚠ catalog says X, source says Y — resolved at
  triage in favour of <which>, see Triage record`, or, where the human deferred it, as an open
  question in *Triage record* and an axis row marked blocked.

## Props API

The surface a consumer writes. **Naming parity is the default and a departure from it is a
decision that gets a line here:** Figma property = component prop = story arg.

| Prop | Type | Default | Change | Precedent |
|---|---|---|---|---|
| `variant` | `'primary' \| 'secondary' \| 'destructive'` | `'primary'` | value added | see *Pattern precedent* → <ladder rung> |
| `asChild` | `boolean` | `false` | new | see *Pattern precedent* → headless |

- Every **new or changed** prop cites a *Pattern precedent* entry, or states plainly that none
  was found and this shape is a local invention — which is a real answer and the one a reviewer
  most needs to see.
- Emit every token, utility and class **exactly as the token list writes it** — consumer-facing
  form, per the adapter's three class-prefix rows. Never re-prefix on the way into a spec.
- Where the adapter's variant mechanism names a **trap** (a runtime alias map outside the
  declaration, a values list in a stylesheet, an axis that exists only in `.d.ts`), name the
  file that trap lives in here. A props change that lands in the declaration and misses the
  trap type-checks and ships broken.

## Story list

Computed in Phase 3, one way only: `argTypes[<axis>].options` diffed against the values actually
passed in story `args`. **Story export names are not a coverage signal** and no row here may be
derived from one.

| Axis | Value | Story today | Action |
|---|---|---|---|
| `variant` | `primary` | covered | none |
| `variant` | `destructive` | none | add — <per the adapter's story convention> |
| `iconOnly` | — | **not computable — no select `argType`** | verify manually |

**Whether a story edit is part of this change at all is the adapter's *Story convention* row,
not a guess.** A repo whose `argTypes` are generated from the variant declaration gets the new
value in its story for free and this table's Action column says so; a repo with hand-written
`argTypes` needs the story edited, and that edit is part of the acceptance criteria below.

## Token delta

*Empty is a valid answer — write "none" and keep the heading.* Every entry here came out of
triage as **extend-tokens**; a raw value that came out as **fix-figma** belongs in the next
section and must not appear in this one.

**Shape A — the adapter's *Token pipeline* row names a generator and its source.** State the
literal source edit; the emitted CSS and utilities are build output nobody hand-edits.

> Source: `<the file the row names>`
>
> ```
> <the literal addition, in that file's own format>
> ```
>
> Then regenerate with `<the generator the row names>`. Do not hand-edit the generated output.

**Shape B — the row says `None`.** There is no single source whose edit propagates, so name
every file that must change together:

| File | Change |
|---|---|
| `<path>` | <the addition, verbatim> |
| `<path>` | <the matching addition, verbatim> |

> All of the above land in one change. A partial application leaves the design system with a
> token that exists in one layer and not the next, which renders correctly in whichever layer
> was edited first.

Delete whichever shape does not apply. **Choosing the shape by reading the repo instead of the
row is the failure this section exists to prevent** — it is exactly the case where the wrong
answer does not error, it just puts the edit in a file the build overwrites.

## Figma fixes

**Designer-side work, riding this same tracker item because it blocks the same change.** Every
item here is something wrong in the **Figma library itself** — an unbound fill, a raw hex where
a variable should be, a detached instance, a variant frame whose content contradicts its own
property assignment.

| Figma node | What's wrong | Fix | Blocks |
|---|---|---|---|
| `<node id>` — <layer name> | fill is raw `#0a5c2b`, bound to nothing | bind to `<the token list's entry, verbatim>` | the `destructive` row above |

**Nothing in this section is code work, and no item in it may also appear in *Variant axes*,
*Props API* or *Token delta*.** That separation is the point of the section: a raw value in the
Figma library looks exactly like a missing token from the code side, and specced as a token it
adds an entry the design system does not need while leaving the Figma file just as wrong. Where
a fix genuinely has a code half too, file the halves as two rows in two sections and say which
blocks which.

## Pattern precedent

*(one entry per **extend-component** decision — the ladder is ARIA APG → headless libraries →
shadcn, walked in that order)*

### <the gap — e.g. "the `destructive` variant axis value">

- **Behaviour spec (APG):** <the pattern name + URL, and what it fixes: roles, keyboard
  interaction, focus management> | **none applies — <why>**
- **API precedent (headless):** <library + the shape it uses, with URL — what is a prop vs a
  sub-component, controlled/uncontrolled, what the parts are called>
- **Naming precedent (shadcn):** <how the variant axis is named and declared there, with URL>
- **Deviations:** <where the Figma design or this library's existing idiom forced a departure
  from the standard, and which one won>
- **Sources:** <3–6 URLs actually read>

**"No precedent found" is written out, never filled in.** Where the ladder returns nothing —
the component class has no APG pattern, no headless analogue and no registry entry — this entry
reads `none found — searched <what>`, and the *Props API* rows it would have supported are
marked a local invention. An invented precedent is worse than none: it launders a guess as an
industry standard and nobody re-checks it.

## Triage record

Every Phase 4 triage decision, one line of rationale each. **Required for all four outcomes**, not just
the ones that produce work.

| Item | Outcome | Rationale | Decided |
|---|---|---|---|
| `variant=destructive` | extend-component | no existing value expresses a destructive action; APG + headless both model it as a variant, not a separate component | <YYYY-MM-DD, by whom> |
| `Secondary` fill | fix-figma | unbound hex in the library file; the token it should carry already exists | <YYYY-MM-DD, by whom> |
| `size=Medium` | already-expressible | `md` exists and matches; nothing to do | <YYYY-MM-DD, by whom> |

**Why the rationale is mandatory.** It is the entire dedup story across runs. A re-run
re-derives every one of these from the same node and the same catalog; the rationale is what
tells the human *this was already argued out, and here is why*, so the second pass costs less
than the first. Without it a settled call gets re-litigated with none of the context that
produced it, and a checkpoint that costs the same on run five as on run one is one people start
clicking through. "Not needed" is not a rationale.

## Acceptance criteria

The checklist that makes this spec sliceable by the tracker's existing chain. One criterion per
observable change; a reviewer must be able to check each without reading the Figma file.

- [ ] `<axis>` accepts `<value>`, declared through <the mechanism the adapter's variant row
      names> and through its trap where the row names one
- [ ] `<prop>` exists with the signature above, and the props API matches the cited precedent or
      documents its departure
- [ ] `<token>` exists in <the source the token pipeline row names> and regenerates cleanly
- [ ] A story exercises `<value>` *(where the story convention makes that a real edit)*
- [ ] The Figma fixes above are applied in the library file *(designer)*
- [ ] Nothing outside this component's axes changed

## Verification notes

What an implementer checks after building: the new axis value renders as the Figma variant frame
draws it, every token resolves to the value the design system defines rather than to a raw one,
existing values are untouched, and the component still renders wherever this design system
documents itself.

**Compare against the pinned baseline, not against "current Figma".** The `Extracted against:`
version at the top is the design this spec describes. If the file has moved on, a difference
between build and canvas may be a design change rather than a defect — check the version before
filing anything, and re-run the skill to re-baseline if it has.
