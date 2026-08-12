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

## Status of a matched entry — `legacy` and `deprecated` resolve, and always flag

Applies to **every** match made by the rules below — component, variant value, token,
typography utility, icon. The catalog stamps entries `current` / `legacy` / `deprecated`
with an optional `successor:`; that field, its default, its cascade from a tier or component
to the entries under it, and the invariant that **a status value never makes an entry
invisible to a match** are all defined in `catalog-contract.md`. This section defines only
what to *do* once a match lands on one.

| Matched entry's status | Outcome | What the finding says |
|---|---|---|
| `current`, or no status field | ✅ resolves | the entry, plainly |
| `legacy` | ✅ resolves **+ ⚠️ flag** | "on-system but legacy; successor is `<successor>`" |
| `deprecated` | ✅ resolves **+ ⚠️ flag** | "on-system but deprecated; successor is `<successor>`" |

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
2. **Prefer semantic.** If a semantic token (Tailwind-classed, **consumer form —
   unprefixed**, e.g. `bg-surface-button-primary`) matches → ✅. Emit the unprefixed form;
   the `g-` prefix is grimme-ui's internal build only (catalog's Class-prefix note).
3. **Only a primitive/alias matches** (e.g. `--g-color-grey-100`,
   `--g-primary-full-default`) → recommend it, but **⚠️ flag** — a primitive binding
   looks right and breaks theming silently. (Only Button is on the semantic layer today,
   so this flags a lot. That's correct signal, not noise.)
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
   24/16/12/8/4px). grimme-ui has **no general layout-spacing token scale**; its dimension
   tokens are **component-scoped** (button/chip/input internals). So generic layout spacing
   maps to the **Tailwind spacing scale** (`gap-4`, `p-3`, `space-y-2`, …) and is **✅ not a
   DS concern — do not flag it.** Flagging every layout gap against dimension tokens is a
   false positive; the nearest-token test does **not** apply here.
2. **Component-internal dimension** — a control's own padding, height, radius, icon box.
   *This* resolves against catalog **dimension** tokens; off-system → ⚠️ flag / ❌ gap by the
   same "is there a nearest token" logic as colors.

The test: *is this the space **between** things (layout → Tailwind), or a **fixed dimension
of one control** (→ dimension token)?*

**Typography** resolves against the catalog's **enumerated `text-*` utility classes**
(consumer form — unprefixed: `text-h1`…`text-h6`, `text-body1/2/3`, `text-caption`,
`text-overline`, `text-button`, …). The catalog now lists the full set, so **match by name**;
❌ gap only type with no `text-*` home (a genuinely novel size/role). **Never emit the `g-`
prefixed form** — that's grimme-ui's internal build, not the consumer API (catalog's
Class-prefix note). Weight stays **literal** (Figma keeps it in `fontName.style`, bound to
nothing — tokenising it invents a tier the file doesn't have).

## Icons (layered resolution)

1. **SystemIcon** — the Figma icon matches a `SYSTEM_ICONS` key in the catalog → ✅ use
   `<SystemIcon name="..." />`.
2. **FontAwesome equivalent** — no SystemIcon, but the consuming app (mygrimme-frontend)
   has a clear FA equivalent → record the FA icon for the app layer. (FA is app-only;
   **never** propose adding FA to grimme-ui.)
3. **Gap** — generic, reusable, grid-conforming icon with no SystemIcon and ideally ≥2
   consumers → ❌ gap: add a new `SYSTEM_ICONS` key (raw SVG) to grimme-ui.
4. **Custom / one-off SVG** — not reusable → note "inline locally as interim" in the
   page spec's interim-fallback field; not a DS gap.

Ambiguous near-duplicate (looks like an existing SystemIcon but not sure) → ⚠️ flag for
the user, don't auto-decide.

## Component matching (inferred — v1 is loose)

grimme-ui has no Code Connect and no name↔code map, so **infer**:

1. Parse the Figma layer name by common conventions — slash-separated
   `Component/Variant/Size`, or a bare `ComponentName`.
2. Match the parsed component against the catalog's components; match parsed
   variant/size against that component's recorded **cva** axes.
3. **Cross-check** the region screenshot against the component's Storybook render.
4. **Confidence gate:**
   - High (name + cva + visual all agree) → ✅ record `<Component props/>`.
   - Low (name mismatch, unknown variant, or visual disagreement) → ❌ **unknown-component
     gap**, AND surface the parsed mapping so the user can confirm/correct. Never silently
     force a low-confidence match.
5. A Figma **instance** inside a region may itself already be a DS primitive — check its
   name against the catalog before classifying it as build-needed.

Components resolve against **grimme-ui only**. Never treat `@grimme/buttery` as a
component source.

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
"one-off hero treatment for this landing page only", "expressible as surface-2 + gap-4 +
text-h3", not "not needed".

That line plus the written-back ticket IDs is the **whole dedup story across runs**. A re-run
regenerates the spec from scratch; without a recorded rationale it re-surfaces a deviation
that was already argued out, and the human re-litigates a decision they made last month with
none of the context that produced it. Rationale-less triage makes the second run cost as
much as the first.

### Stop & ask the human

Deviation might be intentional; can't state drawbacks/alternatives; icon in an ambiguous
near-dup band; semantic intent unclear; or a compose-from-tokens candidate whose constituent
values don't all resolve cleanly.
