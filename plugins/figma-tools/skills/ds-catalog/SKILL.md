---
name: ds-catalog
description: >
  Author a project's design-system catalog — the existence source `figma-to-spec`
  resolves every component, token, type utility and icon against. Explores the
  design system read-only, interviews the human where static reading runs out,
  writes a catalog conforming to the shape contract, and registers the fingerprint
  recipe in the project adapter. Invoke /figma-tools:ds-catalog.
disable-model-invocation: true
---

# DS Catalog

Produce the one artifact `figma-to-spec` cannot run without: this project's **design-system
catalog**. The catalog answers a single question — *does this exist in the design system, and
in what consumer-facing form?* — and a run without a valid one stops. This skill is how a
project gets one.

Two outputs, and both are required for the run to have finished:

1. **The catalog**, written to wherever the adapter's catalog pointer says, conforming to
   `../figma-to-spec/references/catalog-contract.md`.
2. **The fingerprint recipe**, written into the consuming project's adapter — the recipe that
   recomputes the catalog's stamp, without which staleness is permanently unchecked.

## This is an interview, not an extraction

**The interview is the designed path. It is not the fallback for a parser that failed.**

Read-only probes of two real design systems each defeated mechanical extraction, and did it
differently every time: variant axes declared in stylesheets rather than in any parseable
component signature; a typography scale that exists only as a plugin call; an exports map that
filters what is actually public, in both directions; two icon systems side by side, one of them
living in the consumers rather than in the design system; deprecated values that still work
through a runtime remap. A parser that handled all five would be a parser for **one** design
system — the per-project fork this whole abstraction exists to avoid.

So the shape is: **read everything readable, then ask about everything else, then write.**
Static reading narrows the questions and supplies the evidence each one carries; it never
decides an existence question it cannot see. The five shapes above are named, probed and
carried through the interview by `references/static-reading-failures.md` — the extraction
contract this skill hands to every explorer it spawns.

Two consequences worth stating up front:

- **Nothing reaches disk before the interview.** A draft is a question list, never a catalog.
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
  fills any of the role-gated rows the install never asked for (Phase 5 says which rows it may
  write, which it may only propose, and which it never touches).
- **The design system itself**, read-only: a repo path, a workspace package, or an installed
  copy of a published package.
- **The shape contract**, `../figma-to-spec/references/catalog-contract.md` — the required
  sections, the `status:` schema, and the eight validation rules the output must pass. Read it
  before writing anything. **Never restate it here**; it is one document with one owner, and a
  paraphrase that drifts is worse than a pointer.

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
| **1 — Explore** | explorer subagents ×N, read-only, parallel | One per area: public surface · tokens · typography · components and their variant axes · icons. Each carries `references/static-reading-failures.md`. Output: draft entries **plus an uncertainty ledger**. |
| **2 — Probe** | main thread | Walk all five failure shapes against the draft. Every one resolves to *confirmed by <file>* or *a question*. |
| **3 — Interview** | main thread, with the human | Ask the questions, in catalog order, evidence attached. Statuses and successors come from here, and so does the **repo role** — with the three library conventions it gates. |
| **4 — Write** | main thread | The catalog, against the shape contract, in consumer-facing form, fully enumerated. First disk write of the run. |
| **5 — Fingerprint** | main thread | Design the recipe · run it twice from two directories · stamp line 1 · write the adapter rows this run owns. |
| **6 — Validate** | main thread | Run the contract's eight validation rules against what was just written, and report. |

### Phase 0 — Resolve

Read the adapter section. Establish, in this order:

1. **The design-system source**, from its row. A path outside this repo is fine and common;
   note whether it is machine-local, because Phase 5's recipe inherits that limitation.
2. **Author or refresh.** If the *Catalog* row names a file that exists, this run is a
   **refresh** — see below, the rules differ and the difference matters.
3. **The evidence base.** A source checkout gives source, history and build config. An
   installed published package gives built output plus type declarations and no history — a
   thinner base, where variant axes may exist only in `.d.ts` and deprecations may exist
   nowhere at all. Say which one this run has, because it decides how much the interview is
   carrying.
4. **The scope gate** above.

### Phase 1 — Explore, read-only

Fan out one explorer per area. Use the explorer agent the adapter's `## Sources of truth`
registers where it covers the design-system source; otherwise `Explore`. Write tools denied.

**Read-only is literal.** Do not run the design system's build, its token generator, its
formatter or its package manager to make a fact easier to read. A generated artifact that is
stale on disk is itself a finding — carry it into the interview rather than regenerating it
into agreement.

Each explorer returns two things: draft entries **and an uncertainty ledger** — every place
the read ran out, with the file that ran out and why. The ledger is the deliverable that
matters; the draft entries are the cheap half.

### Phase 2 — Probe the five

Walk `references/static-reading-failures.md` against the draft, all five, every time. Each one
ends as *confirmed, by this file* or *a question for Phase 3*. A shape that genuinely does not
apply to this project is confirmed-absent **with the evidence that shows it absent**, never
skipped for want of a hit.

### Phase 3 — Interview

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
  says. Where this run's evidence contradicts a row, that is a finding for Phase 5, not a
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

   In a `consumer` repo these three are not asked and not written; Phase 5 deletes them if a
   copied template left them behind.

### Phase 4 — Write the catalog

Write it to the location the *Catalog* row names, against
`../figma-to-spec/references/catalog-contract.md`. Four things that decide whether the output
is usable, all of them the contract's rules and repeated here only because they are the ones a
first run gets wrong:

- **Consumer-facing form throughout.** The form an app actually writes — never the
  library-internal form, even where the design system's own source is written in the other one.
- **Enumerate. No truncation, no "…and 40 more".** The catalog's entire value is that *absent
  from this list* means *does not exist*; one truncated list converts every existence check in
  the project into a coin flip.
- **`None — <what is used instead>` for a section this project genuinely has none of.** An
  explicit `None` is a real answer; an absent section is not.
- **`—` is not blank.** A component with no variant axis says so.

**Four status shapes this skill may emit**, all of them defined in the contract's `## Status`
section and all four found in real design systems before they were written down. They are listed
here because a run that has the answer from Phase 3 and no way to write it down records nothing:

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
every `status:` field in it un-auditable.

### Phase 5 — Fingerprint recipe, and the adapter write

The catalog carries the fingerprint **value**; the adapter carries the **recipe**. Design the
recipe here, because this run is the only thing that knows which files the catalog was read
from.

**Choosing the file set** — the smallest set whose contents changing implies the catalog is now
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
| *Catalog* | **Writes it when nothing names one yet** — a catalog no pointer reaches is not a deliverable. Where a row already exists and the catalog was written there, leave it byte-intact. |
| *Repo role* | **Writes it when no row exists**, from the Phase 3 answer and from nothing else — never from the tree. Where the row already says `consumer` or `library`, leave it alone; a role changes because a human decides it has, not because a run explored differently. |
| *Variant mechanism* · *Token pipeline* · *Story convention* | **Writes all three when the role is `library`** and the rows are absent, from the Phase 3 answers. Where the role is `consumer`, write none of them, and **delete only an unfilled one a copied template left behind** — a row still carrying its `<placeholder>` is noise `doctor` will report forever, while a row somebody actually filled is theirs and stays. Where a row already exists and this run's evidence contradicts it, propose rather than overwrite, exactly like the class-prefix rows below. |
| *Tailwind class prefix* · *CSS variable prefix* · *Consumer-facing emission form* · *Icon resolution ladder* | **Proposes, never silently changes.** Where this run's evidence contradicts what the row says, show the row, show the evidence, and let the human decide. These are three separate facts and one ordered list — collapsing any of them is how a spec recommends a class the app cannot write. |
| *Design-system source* · *Usage-rules source* · *Downstream implementer* · everything outside `## Design system` | **Never touches.** The two optional rows degrade silently by design: absent means the spec cites nothing, and absent means a human implements. Neither is an error and neither gets a warning. |

### Phase 6 — Validate and report

Run the contract's eight validation rules against the file just written — the skill that writes
runs the reader's gate, so a catalog never reaches `figma-to-spec` failing a rule this run could
have caught. Then report: what was written, which entries came from the interview rather than
from reading, which questions resolved conservatively, and anything the run could not settle.

## Refresh — a re-run is a diff, not a rewrite

Re-running against an existing catalog re-enumerates the mechanical sections, re-runs the
interview only for what changed or is newly ambiguous, re-stamps line 1, and reports the diff
for a human to scan.

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
4. **The written catalog fails a contract validation rule** (Phase 6) that this run cannot fix
   → report it as a failure rather than handing over a catalog that will stop the next
   `figma-to-spec` run at its Phase 0.

## What this skill verifies vs what it cannot

It verifies that every section of the contract is present and populated, that every enumerated
list is complete as far as the run could establish, that all five known failure shapes were
probed rather than skipped, and that the fingerprint recipe is reproducible from two
directories.

It cannot verify that the human's answers are right, that a design system did not change
between exploration and writing, or that an entry nobody could classify is genuinely `current`.
Those it names in the report instead of hiding — which is the same bargain
`figma-to-spec` makes at its own triage checkpoint, and for the same reason.
