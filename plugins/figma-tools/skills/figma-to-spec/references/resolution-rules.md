# Resolution & tolerance rules

How a region agent decides whether a Figma property **resolves** to the design system,
**near-misses** it (human call), or is **off-system** (gap). Applied against the **project
catalog** Phase 0 resolved and validated (shape: `catalog-contract.md`) — never against a
filename this file names. Status vocabulary: ✅ resolves · ⚠️ flag / confirm · ❌ gap.

## Candidate filtering — property kind first, before any comparison

**Every match starts by narrowing the catalog to the entries that can legally apply to the
property in hand.** Value proximity and name similarity are consulted only *inside* that
filtered set, never across the whole catalog.

A stroke width's candidates are the dimension entries that describe strokes and borders. A
text fill's candidates are the text/foreground colors. A background fill's are the surface
colors. A gap's are layout spacing (see the split below), not a control's internal padding
family.

The reason is that an unscoped match is a nearest-number search over a bag of unrelated
tokens, and the numbers collide constantly: a 2px stroke lands perfectly on a 2px spacing
step, a near-white text color lands perfectly on a white background token. Both matches
score flawlessly and are semantically wrong, and — this is the damaging part — they emit as
✅ rather than as a flag. The implementer inherits a value that renders correctly today and
breaks silently the first time either token moves for reasons that have nothing to do with
this design.

1. **Derive the property kind from the Figma property, not from its value** — fill · stroke ·
   text fill · gap · padding · radius · size. A number never tells you which kind it is;
   only the property it was read from does.
2. **Filter, then compare.** ΔE, nearest-dimension distance, and name matching all operate on
   the filtered set. There is no "widen the net if nothing scores well".
3. **An empty filtered set is a real answer**, not a prompt to try another kind: the design
   system has no token of that kind. Resolve it as the layout-scale case or a ❌ gap by the
   rules below — never by borrowing a token whose kind doesn't apply.
4. **The kind boundaries are the catalog's**, read from each tier's stated purpose and the
   entries' own naming (`catalog-contract.md` requires both). Where a catalog genuinely
   doesn't separate two kinds, record that in the finding's note rather than inventing the
   split — an invented boundary is the same failure in the other direction.

## Status of a matched entry — every status resolves; `legacy` and `deprecated` also flag

Applies to **every** match made by the rules below — component, variant value, token,
typography utility, icon. The catalog stamps entries `current` / `legacy` / `deprecated` /
`unused`
with an optional `successor:`; that field, its default, its cascade from a tier or component
to the entries under it, and the invariant that **a status value never makes an entry
invisible to a match** are all defined in `catalog-contract.md`. This section defines only
what to *do* once a match lands on one.

| Matched entry's status | Outcome | What the finding says |
|---|---|---|
| `current`, or no status field | ✅ resolves | the entry, plainly |
| `legacy` | ✅ resolves **+ ⚠️ flag** | "on-system but legacy; successor is `<successor>`" |
| `deprecated` | ✅ resolves **+ ⚠️ flag** | "on-system but deprecated; successor is `<successor>`" |
| `unused` | ✅ resolves, **no flag** | the entry, plainly — optionally noting it had no consumers until now |

**`unused` is not a weak `legacy`, and it does not flag.** It says the entry ships and nothing
consumes it yet; a design that uses it is the first consumer, which is the best outcome
available, not a warning. Flagging it would train a reader to treat "on-system" as a problem.
The two values are defined apart in `catalog-contract.md` for exactly this reason.

- **It is never a ❌ gap.** The design uses something the design system has. False-gapping a
  legacy component — reporting "needs building" for a component that ships today — is the
  exact failure this rule exists to prevent: it sends a human to triage an invented gap and,
  worse, invites a build-local duplicate of an existing component.
- **No `successor:` recorded** → flag it anyway and say so: "on-system but legacy; no
  successor recorded". A legacy entry with nowhere to go is a real state (`catalog-contract.md`
  makes the pointer optional precisely because inventing one is worse), and it is exactly the
  case a human should see.
- **A legacy match is not a triage decision.** Resolution reports "matched, and it's legacy";
  the Phase C checkpoint decides **match-as-is** (spec the legacy entry, it works) vs
  **modernize** (spec the successor, and note the design still shows the old one). Never make
  that call during extraction — the modernize call needs the ticket's scope, which extraction
  doesn't have.
- **Preference between tiers still applies first.** If both a `current` and a `legacy` entry
  match, take the `current` one and don't flag; the flag exists for when legacy is the *only*
  match, or the closest one by the rules below.

## Colors / tokens

1. **Read the bound variable NAME, never the hex.** Use `get_variable_defs` + the
   `use_figma` binding read (call discipline in `../agents/figma-region-extractor.md`). Two
   semantics routinely alias one primitive — matching on value is a coin flip that
   silently collapses the tier.
2. **Prefer the most-derived tier the catalog offers** — its semantic tier over an alias over a
   primitive, in the order the catalog's `## Conventions` states. A match there → ✅, emitted
   **exactly as the catalog writes it**. The catalog is always written in the project's
   consumer-facing form (`catalog-contract.md`), so copying an entry verbatim is the whole
   rule: never re-prefix, un-prefix, or otherwise transform an entry on its way into a spec.
   Where the design system's library-internal form differs from what an app writes, the
   adapter's *Tailwind class prefix*, *CSS variable prefix* and *consumer-facing emission form*
   rows are the three separate facts that say so — and a spec recommends the consumer form.
3. **Only a primitive/alias tier matches** → recommend that entry, but **⚠️ flag** — a
   primitive binding looks right and breaks theming silently. A design system whose semantic
   tier covers only a few components will flag a lot; that is correct signal, not noise.
   A tier the catalog marks **`CSS var only`** emits as a `var()` escape hatch, never as a
   utility class the project doesn't produce.
4. **Raw hex, no binding** → recommend the nearest catalog token by color distance, and
   **always ⚠️ flag**: a detached-variable hex is indistinguishable from an off-system
   hex post-hoc, so a human confirms intent.

### Color distance tolerance (dedup + off-system decision)

Compare the observed color to its nearest catalog token in **CIELAB ΔE**:

| ΔE       | Meaning                | Action                                  |
|----------|------------------------|-----------------------------------------|
| `< ~1–2` | imperceptible          | **auto-merge** — same token, no gap     |
| `1–5`    | barely noticeable      | **⚠️ flag "confirm intent"** — human    |
| `> 5`    | clearly different      | **❌ off-system gap**                    |

(If ΔE is impractical, RGB euclidean distance is an acceptable proxy: `<20` auto-merge,
`20–50` flag, `>50` gap.) Never auto-accept a near-miss — the whole point of the band is
that a machine can't tell an intentional new shade from a sloppy one.

## Typography & spacing

**Spacing splits in two — classify before resolving:**

1. **Generic layout spacing** — gaps/padding between *siblings or regions* (page rhythm:
   24/16/12/8/4px). **Where the catalog's `## Conventions` puts the bifurcation line** — and
   it is required to put it somewhere (`catalog-contract.md`) — generic layout rhythm is the
   **Tailwind spacing scale**'s business (`gap-4`, `p-3`, `space-y-2`, …) and is **✅ not a DS
   concern — do not flag it.** This is the common shape: a design system's dimension tokens are
   routinely component-scoped (a control's internals) with no general layout scale at all.
   Flagging every layout gap against component dimension tokens is a false positive; the
   nearest-token test does **not** apply here.
2. **Component-internal dimension** — a control's own padding, height, radius, icon box.
   *This* resolves against catalog **dimension** tokens; off-system → ⚠️ flag / ❌ gap by the
   same "is there a nearest token" logic as colors.

The test: *is this the space **between** things (layout → Tailwind), or a **fixed dimension
of one control** (→ dimension token)?*

**Typography** resolves against the catalog's **enumerated typography utilities**, which the
contract requires in consumer-facing form and in full. Match **by name** first; where the
design's text style carries the designer's name rather than the design system's — the common
case — match on the properties each utility sets (size, line-height, weight, tracking). ❌ gap
only type with no utility home at all (a genuinely novel size/role), and a catalog that says
`None — <how text is styled instead>` means there is no utility vocabulary to match against, so
say that rather than inventing one. Emit each utility **exactly as the catalog writes it** —
never re-prefixed into a library-internal form. Weight stays **literal** (Figma keeps it in
`fontName.style`, bound to nothing — tokenising it invents a tier the file doesn't have), and a
composite utility the catalog marks as carrying its own breakpoints is never written with a
responsive prefix.

## Icons (layered resolution — the layers are the project's)

**The ladder is not in this file and must never be written into it.** Which icon sources a
project has, in what order it tries them, and what a no-match becomes are the adapter's *icon
resolution ladder* row; what each source *contains* is the catalog's `## Icons` section, one
`###` subsection per source. Two sources of truth, one each, deliberately: a ladder hardcoded
here would name one organisation's icon module and silently mis-resolve every other project's.

The rules that *are* this file's:

1. **Walk the ladder in the order the row gives, and stop at the first source that matches.**
   Order is the whole point — a project that prefers its in-house set to a third-party library
   gets a different (correct) answer from one that prefers the reverse. Never re-order it
   because a later source looks like a closer match.
2. **A match resolves ✅ in that source's own reference form**, copied from the catalog's
   subsection for it — the component call, import, or class the catalog records. Never invent a
   reference form for a source.
3. **Respect where a source may be used.** The catalog records this per source (available to
   consuming apps but forbidden inside the design system, or the reverse). An icon resolved
   from an app-layer-only source is recorded as an app-layer decision and **never** proposed as
   an addition to the design system.
4. **A no-match becomes exactly what the ladder's last step says** — typically ❌ a gap against
   the design system's own icon set, or a locally inlined one-off. Where the row spells out the
   threshold between them (generic and reusable, ideally ≥2 consumers, vs. one-off), apply it;
   where it doesn't, ⚠️ flag the choice for the human rather than picking. A one-off inline SVG
   goes in the page spec's interim-fallback field and is **not** a DS gap.
5. **Resolve the icon as a whole.** Its interior vector geometry is drawing data, not design
   decisions (normative in `../agents/figma-region-extractor.md`); its own box size and the
   color applied at its instance resolve normally.

Ambiguous near-duplicate (looks like an existing catalog icon but not certainly) → ⚠️ flag for
the user, don't auto-decide.

## Component matching (inferred — deliberately loose)

Absent a published Figma-name↔code mapping — which neither design system this skill was built
against had, and which the catalog therefore does not carry — **infer**:

1. Parse the Figma layer name by common conventions — slash-separated
   `Component/Variant/Size`, or a bare `ComponentName`.
2. Match the parsed component against the catalog's components; match parsed
   variant/size against that component's recorded **variant axes and their listed values**.
   The catalog is the closed set — a value it doesn't list does not exist, however plausible
   the project's naming scheme makes it look.
3. **Cross-check** the region screenshot against how the component actually renders, wherever
   the project makes that visible (a component workbench, a docs page, the running app).
4. **Confidence gate:**
   - High (name + variant values + visual all agree) → ✅ record `<Component props/>`.
   - Low (name mismatch, unknown variant, or visual disagreement) → ❌ **unknown-component
     gap**, AND surface the parsed mapping so the user can confirm/correct. Never silently
     force a low-confidence match.
5. A Figma **instance** inside a region may itself already be a DS primitive — check its
   name against the catalog before classifying it as build-needed.

Components resolve against **the catalog only** — the one design system the adapter's
*design-system source* row names. Another library the app happens to depend on is not a
component source, however many components it ships: the catalog is the existence answer, and
anything outside it is a gap or a build-local, never a silent third option.

## Triage outcomes (feeds the Phase C checkpoint — user decides)

**Three outcomes, not two.** These are *recommendations* the synthesis presents; the user
makes the call at the checkpoint.

- **escalate** (→ a DS ticket): ≥2 consumers OR clearly reusable/semantic; OR a near-miss
  delta needing a human (ΔE 1–5); OR a generic icon with a 2nd consumer. The design system
  is missing something it should have.
- **compose-from-tokens** (no ticket, nothing to build): the thing is off-catalog *as a named
  entry* but **fully expressible with tokens and utilities that already exist** — the
  of-the-system snowflake. A one-off arrangement of existing surface, spacing and type
  tokens is not a design-system gap; it is a page composing the system as intended. Record
  the composition (which tokens, in what arrangement) in the page spec so the implementer
  doesn't reach for a raw value, and record the decision so a re-run doesn't re-open it.
  **This outcome is only available when every constituent value resolves ✅ on its own** — a
  composition containing one raw hex is not compose-from-tokens, it is that hex's gap.
- **build-local** (no DS ticket, code to write here): single-consumer / one-off /
  page-specific *and* not expressible from existing tokens — escape-hatch naming + a `TODO`
  linking the (would-be) ticket + an API that mirrors the eventual DS component so it's
  codemod-swappable later.

Two things that are **not** outcomes because they never reach the checkpoint as gaps:
**auto-merge** (ΔE `< ~1–2` — same token, no gap at all) and a **legacy match**, which
resolves with a flag per the status section above; the checkpoint decides match-as-is vs
modernize on it, but it is not one of the three.

### The question the checkpoint asks

For every gap, in the industry's own framing:

> **Is this genuinely reusable across the product, or is it inherently one-off to this
> design?**

Reusable → **escalate**. One-off → **compose-from-tokens** if existing tokens already
express it, **build-local** if they don't. Asking it this way, rather than "should we add
this to the DS?", is what keeps the of-the-system snowflake out of the backlog: a design can
be unlike anything in the library and still be entirely of the library.

### Every non-escalated decision records a one-line rationale

**Required, in the gap file, for both `compose-from-tokens` and `build-local`** (an escalated
gap carries its reasoning in the ticket it produces). One line, naming the specific reason —
"one-off hero treatment for this landing page only", or "expressible as <the catalog's surface
token> + <a layout gap> + <the heading utility>", naming each entry as the catalog writes it.
Not "not needed".

That line plus the written-back ticket IDs is the **whole dedup story across runs**. A re-run
regenerates the spec from scratch; without a recorded rationale it re-surfaces a deviation
that was already argued out, and the human re-litigates a decision they made last month with
none of the context that produced it. Rationale-less triage makes the second run cost as
much as the first.

### Stop & ask the human

Deviation might be intentional; can't state drawbacks/alternatives; icon in an ambiguous
near-dup band; semantic intent unclear; or a compose-from-tokens candidate whose constituent
values don't all resolve cleanly.
