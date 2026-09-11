---
name: ds-catalog
description: >
  Author a project's design-system catalog — the existence source `figma-to-spec`
  resolves every component, token, type utility and icon against. Explores the
  design system read-only, enumerates what a declaration file states, interviews the
  human where static reading runs out, writes a generated half plus a hand-owned
  overlay conforming to the shape contract, and registers the fingerprint recipe in
  the project adapter. Invoke /figma-tools:ds-catalog.
disable-model-invocation: true
---

# DS Catalog

Produce the one artifact `figma-to-spec` cannot run without: this project's **design-system
catalog**. The catalog answers a single question — *does this exist in the design system, and
in what consumer-facing form?* — and a run without a valid one stops. This skill is how a
project gets one.

Three outputs, and all three are required for the run to have finished:

1. **The generated half**, enumerated by `scripts/generate_catalog.py` from the design system's
   own declarations and theme stylesheet. Regenerated, never hand-edited.
2. **The overlay**, written from the interview: `## Conventions`, every `status:` and
   `successor:`, and the `## Idiom mapping` table. Hand-owned, and the thing a re-run protects.
3. **The fingerprint recipe**, written into the consuming project's adapter — the recipe that
   recomputes the generated half's stamp, without which staleness is permanently unchecked.

Both files go where the adapter's catalog pointer says, and together they satisfy
`../figma-to-spec/references/catalog-contract.md`; its *One document, two files* section is
normative for the split and is never restated here.

## Two halves, and the interview owns the one that matters

**The interview is the designed path for the overlay. It is not the fallback for a parser that
failed, and enumeration is not a change of mind about that.**

Splitting the catalog draws the line where the evidence already drew it. A declaration file
does state, mechanically and completely, *which components are exported, under what names,
with which props, and which of those props are unions of string literals*; a theme stylesheet
does state which custom properties exist and what they are worth. Re-asking a human for any of
that is the interview failure mode that matters — asking for a value sitting in a file, which
teaches the human to skim, and skimming is how a wrong answer gets waved through. It is also
what made every design-system bump cost an interview.

What a declaration file does **not** state is everything below.

Read-only probes of two real design systems each defeated mechanical extraction, and did it
differently every time: variant axes declared in stylesheets rather than in any parseable
component signature; a typography scale that exists only as a plugin call; an exports map that
filters what is actually public, in both directions; two icon systems side by side, one of them
living in the consumers rather than in the design system; deprecated values that still work
through a runtime remap. A parser that handled all five would be a parser for **one** design
system — the per-project fork this whole abstraction exists to avoid.

So the shape is: **generate what is stated, read everything else readable, then ask about the
rest, then write the overlay.** Enumeration narrows the questions and supplies the evidence each
one carries; it never decides a question it cannot see, and the generator's `## Unresolved`
section is precisely its list of those. The five shapes above are named, probed and carried
through the interview by `references/static-reading-failures.md` — the extraction contract this
skill hands to every explorer it spawns, and the file that says which parts of a generated half
are trustworthy.

Two consequences worth stating up front:

- **Nothing a human owns reaches disk before the interview.** The generated half is written
  early and freely — it is derived, it is reproducible, and a wrong one is fixed by fixing its
  inputs and re-running. The overlay is written once, at the end, from answers.
- **A silent omission is the failure mode this skill exists to prevent.** Every probe ends
  either *confirmed, by this file* or *asked*. "Not found" is not an outcome — for four of the
  five shapes, not-found is exactly what the failure looks like from inside a parser.

## Supersedes

This skill **replaces the per-project catalog generators that came before it** — skills that
produced one organisation's catalog by reading one organisation's repo layout, and lived in
that organisation's repo. Their subject matter survives here as the probe list; their hardcoded
knowledge of a particular exports map, token pipeline and icon module does not, and must not be
reintroduced. Nothing in this skill names a design system, a class vocabulary, a token tier or
a file path: every one of those is read from the adapter or asked. Retiring such a skill where
it lives is that repo's business — recorded here so the retirement is discoverable from the
thing that replaced it.

## Inputs

- **The project adapter**, `<repo-root>/.claude/project/adapter.md`, its `## Design system`
  section: the *Design-system source* row says what to explore, the *Catalog* row says where
  the output goes, and the class-prefix and icon-ladder rows carry what a previous
  install-time interview already established — including the *Repo role* row and, where that
  role is `library`, the variant-mechanism, token-pipeline and story-convention rows.
  `install-skills` writes that section; this skill owns the fingerprint recipe outright, and
  fills any of the role-gated rows the install never asked for (Phase 6 says which rows it may
  write, which it may only propose, and which it never touches).
- **The design system itself**, read-only: a repo path, a workspace package, or an installed
  copy of a published package.
- **The shape contract**, `../figma-to-spec/references/catalog-contract.md` — the required
  sections, the two-file split, the `status:` schema, and the eight validation rules the output
  must pass. Read it before writing anything. **Never restate it here**; it is one document with
  one owner, and a paraphrase that drifts is worse than a pointer.
- **The generator**, `scripts/generate_catalog.py`, bundled with this skill. It takes no
  skill-specific input and knows nothing about this workflow — deliberately, so a design system
  can eventually ship it and a project can stop generating its catalog from the outside.

Missing `## Design system` section entirely → say so, point at `install-skills`, and offer to
add the section from this run's answers. Never invent a catalog location: if no row names one,
ask where it goes and write the row.

## Scope gate — Tailwind-first, and that is a STOP

The contract assumes a Tailwind-based design system: tokens as CSS custom properties reachable
from the theme, reaching consumers as utility classes, with spacing bifurcated between the
framework's scale and the design system's own dimension tokens.

A design system that is not that shape — CSS-in-JS themes, a Sass-variable API, a platform
toolkit — gets **a clear "not this version"**, at Phase 0, before any exploration. It does not
get a catalog that half-fits: the sections would validate while every spec resolved against a
class vocabulary the project never emits, and each one would read as on-system while being
unimplementable. Say which assumption fails and stop.

## Phases

| Phase | Runs as | Does |
|---|---|---|
| **0 — Resolve** | main thread | Read the adapter's `## Design system`. Locate the design-system source · decide **author** vs **refresh** · run the scope gate. |
| **1 — Generate** | main thread | Locate the declaration file and the theme stylesheet · run `scripts/generate_catalog.py` · write the generated half. **No interview.** Its `## Unresolved` list joins Phase 3's probes. |
| **2 — Explore** | explorer subagents ×N, read-only, parallel | One per area, and **only for what the generated half could not settle**. Each carries `references/static-reading-failures.md`. Output: findings **plus an uncertainty ledger**. |
| **3 — Probe** | main thread | Walk all five failure shapes against the generated half. Every one resolves to *confirmed by <file>* or *a question*. |
| **4 — Interview** | main thread, with the human | Ask the questions, in catalog order, evidence attached. Statuses, successors, conventions and idiom rows come from here, and so does the **repo role** — with the three library conventions it gates. |
| **5 — Write the overlay** | main thread | `## Conventions`, the statuses, `## Idiom mapping`. First hand-owned disk write of the run. |
| **6 — Fingerprint** | main thread | Write the one-line recipe that reads the installed version · confirm it · write the adapter rows this run owns. |
| **7 — Validate** | main thread | Run the contract's eight validation rules against the **union** of the two files, and report. |

### Phase 0 — Resolve

Read the adapter section. Establish, in this order:

1. **The design-system source**, from its row. A path outside this repo is fine and common;
   note whether it is machine-local, because Phase 6's recipe inherits that limitation.
2. **Author or refresh.** If the *Catalog* row names a file, or a directory holding one, that
   already exists, this run is a **refresh** — see below, the rules differ and the difference
   matters.
3. **The evidence base.** A source checkout gives source, history and build config. An
   installed published package gives built output plus type declarations and no history — a
   thinner base, where variant axes may exist only in `.d.ts` and deprecations may exist
   nowhere at all. Say which one this run has, because it decides how much the interview is
   carrying.
4. **The scope gate** above.

### Phase 1 — Generate the enumerated half

`scripts/generate_catalog.py` takes a bundled declaration file, a theme stylesheet, a name and
the installed version, and writes `## Components`, `## Tokens`, `## Typography` and `## Icons`.
Run `--help` for its arguments; they are described there and not restated here.

**Locating its two inputs is this phase's real work**, and both are read from the
*Design-system source* row rather than guessed:

- **The declaration file** — the bundled `.d.ts` the package's manifest points its `types` /
  `exports` at. Prefer the bundled one over per-file declarations: it is the public surface the
  exports map actually produces, which is failure shape 3.
- **The theme stylesheet** — the file carrying the custom properties and, where the project
  emits them as rules, the text utilities. A project whose typography is a plugin call has none
  to give; that is failure shape 2, the generator reports the section as empty, and the
  interview settles it. **Never run the design system's build to produce one.**

Three rules about what comes out:

- **It is derived, so write it freely.** A wrong generated half is fixed by fixing an input and
  re-running, which is why the "nothing reaches disk first" rule does not cover it.
- **Never hand-edit it.** An edit survives exactly until the next bump, and it silently
  un-survives, which is worse than never making it. Anything that needs saying goes in the
  overlay, which wins on any section both files carry.
- **Its `## Unresolved` list is input to Phase 3**, item for item. Each entry is a place the
  declaration parsed cleanly and answered nothing — an unbounded `string` prop, a props type
  declared elsewhere — and each is exactly failure shape 1 wearing a type annotation.

A project whose design system ships no usable declaration file gets no generated half, and the
run reverts to what it always was: explore, probe, interview, write one catalog. **That is a
supported outcome, not a degraded one** — the contract makes the split optional — and the run
says which shape it produced.

### Phase 2 — Explore what generation could not settle

Fan out one explorer per area — **and only for areas the generated half left open.** A section
the generator enumerated completely needs no explorer, and spawning one to re-derive it is the
same waste as re-asking a human for it. Where there is no generated half at all, every area is
open and this phase is the whole read.

Use the explorer agent the adapter's `## Sources of truth` registers where it covers the
design-system source; otherwise `Explore`. Write tools denied.

**Read-only is literal.** Do not run the design system's build, its token generator, its
formatter or its package manager to make a fact easier to read. A generated artifact that is
stale on disk is itself a finding — carry it into the interview rather than regenerating it
into agreement.

Each explorer returns two things: findings **and an uncertainty ledger** — every place the read
ran out, with the file that ran out and why. The ledger is the deliverable that matters, and
with a generated half in hand it is very nearly the only one: the cheap half has already been
enumerated.

### Phase 3 — Probe the five

Walk `references/static-reading-failures.md` against the generated half and the explorers'
findings, all five shapes, every time. The generated half is **the thing being probed, not
evidence that settles a probe** — four of the five shapes are cases where a declaration parses
cleanly and says something false, so a confident generated entry is exactly what a probe is
looking at. Each one
ends as *confirmed, by this file* or *a question for Phase 4*. A shape that genuinely does not
apply to this project is confirmed-absent **with the evidence that shows it absent**, never
skipped for want of a hit.

### Phase 4 — Interview

Ask in the order the catalog is written — conventions, components, tokens, typography, icons —
so the human is answering one topic at a time and can see the document taking shape.

Rules that keep it finite and keep it honest:

- **Never ask what the repo already answered.** An interview that re-asks readable facts trains
  the human to skim, and skimming is how a wrong answer gets waved through.
- **Every question carries four things**: what the run found, the file that shows it, the
  specific ambiguity, and a default the human can accept in one word. "Which variants does
  Button have?" is a worse question than "the map in `<file>` gives four values; the props type
  accepts any string — is the map the complete set?"
- **One section per exchange.** Batch within a section; never mix sections in one message.
- **Statuses are asked here, not bolted on later.** `legacy` / `deprecated` / `unused` and the
  successor pointer come out of this conversation and nowhere else — there is no second document
  to reconcile afterwards, and no later pass that would catch a missed one. `unused` is the one
  a static read essentially never surfaces, because "nothing imports this" is a fact about the
  *consumers*, not about the design system: ask it rather than inferring it, and where nobody can
  say, the entry is `current`.
- **Never invent a successor.** A legacy entry with no replacement yet is a real state; record
  it as legacy with no successor. A dangling `successor:` fails validation rule 8 anyway.
- **Unresolved at the end of the interview**: an unresolved question about **a whole section**
  stops the run — writing it either way is a lie in one direction, and the contract has no
  "unknown" state because *absent* already means *does not exist*. An unresolved question about
  **a single entry** resolves conservatively and visibly: if the code emits it, it exists; if
  nobody can say whether it is legacy, it is `current` (the schema's default) with no successor,
  and the run report says which entries landed that way.
- Confirm the **class-prefix facts and the icon ladder** against what the adapter already
  says. Where this run's evidence contradicts a row, that is a finding for Phase 6, not a
  silent correction.

**The role question, and the three it gates.** Ask these where the adapter's `## Design system`
has no answer yet — and only there; a row that is already filled is confirmed, not re-asked.

1. **What role does this repo play — `consumer` or `library`?** A consumer renders the design
   system; a library *is* it. **Never guessed from the tree.** The role is an intent, and a repo
   containing a `components/` directory is not thereby a library — a consumer's local components
   look identical from the outside. An absent row means `consumer`, so this question only ever
   *adds* information; it never has to be asked twice.
2. **Only when the answer is `library`**, three conventions of the design system's own source,
   each of which this run has probably just seen evidence for and none of which it can settle:
   - **The variant mechanism, as a ladder** — what declares a component's axes first, what the
     fallback is when that is absent, and which shapes are the *implementation* of a variant
     rather than its declaration. Ask for the trap explicitly: shape 5 in
     `references/static-reading-failures.md` is exactly this ladder's last rung, and a runtime
     alias map outside the declaration is the classic one.
   - **The token pipeline** — is there a generator, and what source does it consume? "None, the
     emitted CSS is hand-edited" is a real answer. This decides how literal a downstream spec's
     token delta may be, so it is worth one round of pressing.
   - **The story convention** — where stories live, and whether `argTypes` are generated from the
     variants or hand-written.

   In a `consumer` repo these three are not asked and not written; Phase 6 deletes them if a
   copied template left them behind.

### Phase 5 — Write the overlay

Write it beside the generated half, where the *Catalog* row points, against
`../figma-to-spec/references/catalog-contract.md`. It carries `## Conventions`, every `status:`
and `successor:`, `## Idiom mapping`, and **any section the generator could not produce** — a
typography scale that exists only as a plugin call is enumerated here, by hand, from the
interview.

Four things that decide whether the output is usable, all of them the contract's rules and
repeated here only because they are the ones a first run gets wrong:

- **Consumer-facing form throughout.** The form an app actually writes — never the
  library-internal form, even where the design system's own source is written in the other one.
- **Enumerate. No truncation, no "…and 40 more".** The catalog's entire value is that *absent
  from this list* means *does not exist*; one truncated list converts every existence check in
  the project into a coin flip.
- **`None — <what is used instead>` for a section this project genuinely has none of.** An
  explicit `None` is a real answer; an absent section is not.
- **`—` is not blank.** A component with no variant axis says so.

**Where the overlay restates an entry the generated half already carries, the overlay wins** —
that is the contract's rule and it is what makes an annotation possible at all. Restate only the
entry being annotated, never a whole section for tidiness: a section copied across in full stops
tracking the next regeneration, and does it silently.

**Four status shapes this skill may emit**, all of them defined in the contract's `## Status`
section and all four found in real design systems before they were written down. They are listed
here because a run that has the answer from Phase 4 and no way to write it down records nothing:

- **A successor across tiers or sections.** `successor:` names an entry *anywhere* in the
  catalog — a primitive superseded by a semantic token, a utility by a composite, a variant value
  by a different component. Qualify the target (`<tier or section> → <entry>`) wherever the bare
  string would match in two places; a pointer that resolves twice fails validation rule 8 the
  same as one that resolves nowhere.
- **A tier with no single successor.** Where a whole tier is retiring and its entries redistribute
  rather than moving as a block, write it explicitly under the tier heading —
  `status: legacy · successor: none — <where its entries go instead>`. Never leave the field bare
  to mean this: "no single successor" and "nobody filled this in" must not look alike, which is
  the entire reason the `none — …` form exists.
- **`unused`.** The entry ships, nothing consumes it. Distinct from `legacy`, never a synonym for
  it, and usually carrying no successor. Emit it only where the interview established it; the
  default for "nobody could say" is `current`.
- **A deprecated prop inside a `current` component.** Write the status on the axis, inline in the
  *Variant axes / values* cell — never in the row's `Status` column, which belongs to the
  component. Promoting a prop's status to the component is the failure the scoping rule exists to
  prevent: every spec touching any part of that component then reads as flagged, and the one prop
  that matters is buried.

`## Conventions` is the section written for a human rather than a matcher, and it is where the
interview's prose belongs: which way is current, how a token's name becomes its class including
the step that surprises, where the spacing bifurcation falls, and any migration in flight with
how far adoption actually got. A catalog that lists two ways and names neither as current makes
every `status:` field in it un-auditable. **It also names the tiers**, because the generator
groups custom properties by the first segment of their name and that grouping is arithmetic, not
the project's taxonomy — say which mechanical group is which real tier, and which of them a new
value should come from.

`## Idiom mapping` starts from the interview and grows from use. Seed it with what this run
already saw — the component a consumer reaches for when the design draws a popover, a chip row,
a range editor — and add a row every later time a run resolves one of those wrongly. An empty
table is a fine first state; leaving the section out entirely is also fine, and means idioms
resolve by name similarity alone.

### Phase 6 — Fingerprint, and the adapter write

The generated half carries the fingerprint **value**; the adapter carries the **recipe**. Design
the recipe here, because this run is the only thing that knows what the catalog was read from.

**Where there is a generated half, the recipe is a one-liner reading the installed version** —
the same value the generator stamped, read back the same way, typically the `version` field of
the design system's own installed manifest. It is exact, it is stable across checkouts by
construction, and it says exactly what the stamp is meant to say: *this enumeration is as
current as the package it was enumerated from.*

**Read the installed package's own manifest, never the dependency range.** A range resolves to a
different version on two machines and on two days, so a stamp built from one matches when
nothing is current and differs when nothing changed. The generator refuses a range outright for
this reason; a recipe that hands one back would reintroduce exactly what it refuses.

The hash-a-file-set recipe below is what a run **without** a generated half falls back to, and
it is still the right answer there.

**Choosing the file set** — where the recipe is a hash rather than a version read, the smallest set whose contents changing implies the catalog is now
wrong. Typically the public-surface declaration, the token definitions, the typography source
and the icon set. Not the whole repo: a set that churns daily produces a warning on every run
and trains everyone to ignore it. Not one file: it misses drift in the other four sections.
Whatever the set is, the catalog's source note states it — that note and this row are the same
decision written down twice on purpose, one where each reader looks.

**Three properties the command must have:**

- **Content-only.** Hash file *contents*, never anything that embeds a path — a recipe that
  prints filenames into the digest gives two checkouts of the same commit two different stamps,
  and every staleness check becomes a false warning. A commit hash fails differently and just
  as badly: it changes on every unrelated commit, and does not exist for a published package.
- **Deterministic order.** List the files explicitly, in a fixed order. A glob's expansion
  order is not guaranteed stable across shells and locales, and an unstable order is a stamp
  that differs from itself.
- **Runnable from the consuming project.** The row lives in this project's adapter and Phase 0
  of `figma-to-spec` runs it from here. If the design system is a machine-local checkout, the
  command only works on machines that have it — say so in the row rather than shipping a
  recipe that silently fails for the next person.

**Verify it before writing it down**: run it twice, from two different working directories, and
confirm the same value. That is the check that catches path-dependence, and it costs one
command.

Then write to the adapter's `## Design system` section:

| Row | This skill's authority |
|---|---|
| *Fingerprint command* | **Owns it.** Write the recipe. Nothing else in the system can — it is derived from the file set this run read. `None — staleness unchecked` is a real answer where no stable set exists, and the staleness check is soft, so it never fails a run. |
| *Catalog* | **Writes it when nothing names one yet** — a catalog no pointer reaches is not a deliverable. Point it at the **directory** where a split catalog's two files live, never at one of them: a pointer naming the generated half makes the overlay invisible, and every status in it silently stops applying. Where a row already exists and the catalog was written there, leave it byte-intact. |
| *Repo role* | **Writes it when no row exists**, from the Phase 4 answer and from nothing else — never from the tree. Where the row already says `consumer` or `library`, leave it alone; a role changes because a human decides it has, not because a run explored differently. |
| *Variant mechanism* · *Token pipeline* · *Story convention* | **Writes all three when the role is `library`** and the rows are absent, from the Phase 4 answers. Where the role is `consumer`, write none of them, and **delete only an unfilled one a copied template left behind** — a row still carrying its `<placeholder>` is noise `doctor` will report forever, while a row somebody actually filled is theirs and stays. Where a row already exists and this run's evidence contradicts it, propose rather than overwrite, exactly like the class-prefix rows below. |
| *Tailwind class prefix* · *CSS variable prefix* · *Consumer-facing emission form* · *Icon resolution ladder* | **Proposes, never silently changes.** Where this run's evidence contradicts what the row says, show the row, show the evidence, and let the human decide. These are three separate facts and one ordered list — collapsing any of them is how a spec recommends a class the app cannot write. |
| *Gap policy* · *Provisional marker* · *Gap tracker* · *Provisional expiry* | **Never touches, and never deletes.** All four default, so an absent row is a complete state and not a placeholder to tidy — the deletion rule for unfilled `library` rows above does **not** extend here. They are also not inferable: what a project is willing to ship provisionally is a policy, and a catalog run has no evidence about it. `install-skills` asks; a human edits. |
| *Design-system source* · *Usage-rules sources* · *Downstream implementer* · *`### Prototype source`* · everything outside `## Design system` | **Never touches.** The two optional rows degrade silently by design: absent means the spec cites nothing, and absent means a human implements. Neither is an error and neither gets a warning. |

### Phase 7 — Validate and report

Run the contract's eight validation rules against **the union of what was just written** — the
skill that writes runs the reader's gate, so a catalog never reaches `figma-to-spec` failing a
rule this run could have caught. Validating either half alone fails rules the other half
satisfies: the generated one has no `## Conventions` and the overlay has no `## Components`. Then report: what was written, which entries came from the interview rather than
from reading, which questions resolved conservatively, and anything the run could not settle.

## Refresh — a re-run is a diff, not a rewrite

Re-running against an existing catalog re-enumerates the mechanical sections, re-runs the
interview only for what changed or is newly ambiguous, re-stamps line 1, and reports the diff
for a human to scan.

**On a design-system bump, that is one command and a diff.** Re-run the generator, read the
diff of the generated half, and touch the overlay only where the diff shows something
**removed or renamed** — an entry that is gone takes any status written on it with it, and a
`successor:` pointing at a renamed entry now dangles and fails validation rule 8. A bump that
only *adds* entries needs no overlay edit at all, which is the whole point of the split and the
thing worth not undoing: a new component with no status is `current` by default, which is
correct.

Two things a refresh must not do:

- **Re-run the interview because the version moved.** The overlay's answers are about
  conventions and adoption, and a patch bump changes neither.
- **Hand-edit the generated half to match an expectation.** If the diff is wrong, an input is
  wrong; fix that and regenerate.

**The trap, and it is the one that matters: never drop a `status: legacy` annotation because
this run's static read did not rediscover it.** Statuses came out of a conversation. A fresh
read has no evidence of them by construction, so treating not-found as gone deletes exactly the
information the interview existed to capture — quietly, and in the section whose whole purpose
is to record what a reader cannot see. Human-authored `## Conventions` prose is protected the
same way: replaced only where this run has evidence that contradicts it, never reflowed or
re-toned for tidiness.

## STOP gates

1. **Not a Tailwind-based design system** (Phase 0) → stop, naming the assumption that fails.
   There is no degraded mode.
2. **No design-system source resolvable** → ask, then stop. Never explore a guess.
3. **An unresolved question about an entire catalog section** at the end of the interview →
   stop and say what is needed. A section written on a guess reads as authoritative forever.
4. **The written catalog fails a contract validation rule** (Phase 7) that this run cannot fix
   → report it as a failure rather than handing over a catalog that will stop the next
   `figma-to-spec` run at its Phase 0.

## What this skill verifies vs what it cannot

It verifies that every section of the contract is present and populated across the two files,
that every enumerated list is complete as far as the run could establish, that all five known
failure shapes were probed rather than skipped, and that the fingerprint recipe returns the
version the generated half is stamped with.

It cannot verify that the human's answers are right, that a design system did not change
between exploration and writing, or that an entry nobody could classify is genuinely `current`.
Those it names in the report instead of hiding — which is the same bargain
`figma-to-spec` makes at its own triage checkpoint, and for the same reason.
