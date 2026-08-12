# Catalog shape contract

The **interface** between this skill and a project's design-system catalog. The catalog is a
per-project artifact living in the consuming repo; this file is the plugin-side shape it is
written against, and it is the only thing about a catalog the plugin knows.

Three parties, one contract:

- **Written against it** — whatever authors the catalog (an authoring skill, or a human with
  a text editor). A catalog that satisfies this file is usable; one that doesn't is rejected.
- **Read against it** — Phase 0, which resolves a catalog and **validates** it before any
  Figma read happens, and the resolution rules, which match Figma properties against its
  entries.
- **Never touching it** — Phase D. Filing targets are adapter rows, not catalog contents.

The catalog answers exactly one question: **does this exist in the design system, and in what
consumer-facing form?** It is an *existence* source, not a usage guide. HOW to use a component
is a separate concern, cited by the page spec from whatever usage-rules source the adapter
registers (absent → cited from nothing, which is fine).

## Where the catalog lives — a pointer, never a filename

The catalog is registered in the consuming repo's adapter
(`<repo-root>/.claude/project/adapter.md`), in its `## Design system` section, exactly the way
a project gate is registered in `## Project gates`: **the registry is the only place the file
is named.** No skill and no reference doc in this plugin — including this one — may hardcode a
catalog filename, path, or location. Follow the pointer or ask.

Phase 0's resolution order is **passed arg → the adapter's catalog pointer → ask the user**,
in that order and no further. There is no fallback beyond *ask*: never resolve a catalog from
inside this plugin, and never reconstruct one by reading the design system's source at run
time. A run without a valid catalog stops.

Two adapter rows this contract defers to rather than duplicating, both referenced by role and
never by literal value:

- **the fingerprint command** — the recipe that recomputes the stamp defined below. The
  catalog carries the *value*; the adapter carries the *recipe*.
- **the icon resolution ladder** — which icon source a project prefers, and what happens when
  none matches. The catalog says what *exists*; the adapter says which order to try. One
  source of truth each.

## Scope: Tailwind-first, and that is a licence, not a hedge

This version of the contract **assumes a Tailwind-based design system**, specifically:

1. Design tokens are **CSS custom properties** reachable from the Tailwind theme.
2. Tokens reach consumers as **utility classes** emitted from that theme, and the catalog can
   state a class name per token.
3. Spacing **bifurcates**: generic layout rhythm comes from the Tailwind spacing scale, while
   component-internal dimensions (control heights, internal padding, radii, icon boxes) come
   from the DS's own dimension tokens. Where the line falls is a project fact the catalog
   states; that it falls *somewhere* is assumed here.

A design system that is not Tailwind-based — CSS-in-JS themes, a Sass-variable API, a
platform toolkit — is **out of scope for this version**, not a degraded mode. Such a project
should get a clear "not this version" rather than a catalog that half-fits: the sections below
would validate while the resolution rules matched against a class vocabulary the project never
emits, and every spec would read as on-system while being unimplementable.

## Required sections

Section headings are **literal**, so validation is mechanical. Everything *inside* them is the
project's vocabulary.

| Section | Required | Carries | Why the skill needs it |
|---|---|---|---|
| Title line + fingerprint stamp | yes | the catalog's name, the fingerprint value, the generation date | staleness is checkable at all |
| `## Conventions` | yes | the project's **current** standard at a glance | tells a reader which of several coexisting ways is the one to spec against |
| `## Components` | yes | every component in the consumer API, with its variant axes and their valid values | component matching, and variant-value existence checks |
| `## Tokens` | yes | N named tiers, each enumerated, each with its consumer-facing form | token resolution and tier preference |
| `## Typography` | yes | the text utilities in consumer-facing form, with the properties each sets | matching a Figma text style |
| `## Icons` | yes | every icon **source** (plural), each enumerated or bounded | the icon ladder has something to walk |

A section whose answer is genuinely "this project has none of these" is written as
`None — <what is used instead>`. **An explicit `None` is a real answer; an absent section is
not**, because absence and "nobody wrote it down" are indistinguishable to a reader, and
"not in the catalog" is the skill's only evidence that something does not exist.

## Title line and fingerprint stamp

Line 1 carries the name, the fingerprint value, and the generation date:

```
# <name> catalog (fingerprint: <hash> · generated: <YYYY-MM-DD>)
```

Immediately below it, a short source note: which repo or package the catalog was read from,
and **what the fingerprint covers** — the set of files whose contents produce the hash.

Two rules about the stamp:

- The hash is **content-only**. Hashing anything path-dependent makes the stamp differ between
  two checkouts of the same commit, which turns every staleness check into a false warning.
- The recipe that produces it lives in the adapter, not here and not in the catalog. The
  catalog records what the recipe returned.

Staleness is **soft**: a stamp that no longer matches produces a warning and the run
continues. A malformed or missing stamp is a *shape* failure and does stop the run — see
Validation.

## `## Conventions`

The one section written for a reader rather than a matcher: what is the project's standard
**today**, stated plainly enough that someone can spec a new value without reading the DS
source. It is prose, tables, or both.

What it must settle, wherever the answer isn't obvious from the entries themselves:

- Which tier a new value should come from, when several tiers coexist.
- How a token's name becomes its consumer-facing class — the mechanical rule, including any
  step that surprises (a category word kept or dropped, a prefix applied on one side of a
  package boundary and not the other).
- Where the **spacing bifurcation** falls: which spacing is the Tailwind scale's business and
  which resolves against DS dimension tokens.
- Whether consumer-facing and library-internal class forms differ, and which form the catalog
  is written in. **The catalog is always written in the consumer-facing form** — the form an
  app actually writes — because that is the form a spec is implemented in.
- Any migration in flight: which way is current, which way is on the way out, and how far
  adoption has actually got. A catalog that lists two ways and states neither as current makes
  every `status:` field below un-auditable.

## `## Components`

One row per component that exists in the **consumer** API. A table:

| Column | Required | Contents |
|---|---|---|
| Component | yes | the name a consumer renders |
| Reference | yes | how a consumer reaches it — import subpath, package path, or equivalent |
| Variant axes / values | yes | every axis and its valid values, or `—` for a component with no axis |
| Status | no | `current` when omitted — see Status below |
| Source | no | where it is defined, for a human chasing a discrepancy |

Rules:

- **Variants are recorded as stated, never parsed at match time.** The catalog is the closed
  set: a variant value not listed does not exist, and matching a Figma layer name against a
  *guess* at the project's naming scheme is how a spec acquires props that fail to compile.
- **`—` is not the same as blank.** A component with no variant axis says so; a blank cell
  reads as "nobody checked".
- Values are the **literal strings a consumer passes**, in the consumer's casing.
- An individual variant *value* may carry its own status (e.g. a renamed value kept as a
  runtime-mapped alias). Record it on the value, inline, not on the whole component.
- Exports that are not components (build config, style bundles, utility helpers) may be listed
  in a separate table, clearly marked. They never match a Figma layer, and they are not counted
  as components.

## `## Tokens`

**N tiers. The number and the names are the project's, not the plugin's.** Two-tier,
three-tier, and "three tiers plus a dimension family" are all valid; so is one flat tier. One
`###` subsection per tier, named by the project's own name for it, in the order the project
considers most-derived last (or states its own order in `## Conventions`).

Each tier subsection declares:

- **What the tier is for**, in one line, and whether it is meant to be consumed directly.
- **The consumer-facing form of its entries** — the CSS custom property, and the utility class
  each token produces. A tier that emits no class says **`CSS var only`** and why; that is a
  real answer and the resolution rules need it, because recommending a class that does not
  exist is worse than recommending an escape-hatch `var()`.
- **The entries, enumerated — no truncation, no "…and 40 more".** The catalog's value is that
  "absent from this list" means "does not exist"; a truncated list quietly converts every
  existence check into a coin flip. Value alongside name where the value is what a match is
  made on.
- **Tier status**, when a whole tier is legacy or deprecated. A tier-level status applies to
  every entry in it unless an entry overrides it.

Any token family with mechanical naming quirks — a category word repeated, a word dropped
on emission, a version suffix collapsed — is a `## Conventions` matter, stated once there
rather than annotated per entry.

## `## Typography`

The text utilities in **consumer-facing form**, enumerated, with the properties each one sets:
size, line-height, weight, letter-spacing, transform, and any built-in responsive steps.

Both halves matter. The names let a Figma text style match by name; the properties let one
match by value when the design's style name is the designer's rather than the DS's — the
common case.

Also state, where true:

- Which utilities are composites that carry their own breakpoints, and therefore must **not**
  be written with a responsive prefix.
- Companion scales that ship alongside (weight, tracking) and whether they *extend* or
  *override* the framework's defaults. A same-named class with a different value is a silent
  correctness bug in a spec.
- Anything present in a source map but not emitted as a class: **dead data is not an available
  style**, and saying so stops it being specced.

A project whose text styling is not utility-based writes `None — <how text is styled
instead>`.

## `## Icons`

**Icon sources are plural by default.** Both design systems probed while writing this contract
shipped two — an in-house inline set plus a third-party library used by consuming apps — and
assuming one source is the single most likely way to produce a spec that names an icon nobody
can render.

One `###` subsection per source, each carrying:

- **How an icon from this source is referenced in code** — the component call, the import, or
  the class, in consumer-facing form.
- **The set.** Enumerate it when it is closed and the project owns it. When the source is an
  external library with an open set, say so, name the library and the pinned version, and say
  how a candidate name is verified — an open set is a real answer, an unstated one is not.
- **Where it may be used.** A source available to consuming apps but forbidden inside the
  design system (or the reverse) is a fact that changes what a gap ticket should say.

The **order** the sources are tried in is the adapter's icon-resolution-ladder row, not this
section. The catalog says what exists; the adapter says what the project prefers.

## Status: `current` · `legacy` · `deprecated`

**Every entry kind carries a status** — component, individual variant value, token, whole
tier, typography utility, and icon entry — with an optional successor pointer:

```
status: current | legacy | deprecated        (default: current)
successor: <the entry that replaces it>      (optional)
```

Rules, defined once here and nowhere else:

- **Omitted means `current`.** An unannotated entry is not "unknown" — the vast majority of a
  catalog carries no status field at all, and requiring one per row would make catalogs
  unwritable.
- **`legacy`** — still works, still resolvable, no longer the way to do it.
  **`deprecated`** — on the way out: scheduled for removal, or warning at runtime.
- **Neither is the same as absent.** *Absent from the catalog* is the only thing that means
  "does not exist in the design system".
- **`successor:`** names its replacement in the same vocabulary the entry uses — a class name
  for a class, a variant value for a variant value, a component name for a component. It is
  optional because a legacy entry sometimes has no replacement yet, and inventing one is worse
  than admitting the gap.
- **Where it is written**: a `Status` column where the entry lives in a table; an inline
  `status: legacy · successor: <x>` suffix where the entry lives in a list; a line under the
  tier heading where a whole tier is legacy.
- **A tier-level or component-level status cascades** to entries that don't override it.

**What resolution does with a status is not defined here.** This contract's job is that the
data exists and is unambiguous. One invariant does belong here, because it keeps the two
concerns apart: **a status value never makes an entry invisible to a match.** The moment a
`legacy` entry stops matching, a documentation field has quietly become an existence field,
and designs drawn against the old component start reporting as gaps that need building — the
exact false-gap this field exists to prevent.

## Validation — Phase 0, loud failure only

Phase 0 validates the resolved catalog **before** any Figma read. Every rule below is a hard
STOP. There is no partial acceptance, no degraded mode, and no inferring a missing section
from the design system's source: a catalog that is wrong in one section is not evidence of
anything in the others, and a run that proceeds on partial data produces a spec that *looks*
resolved.

| # | Rule | Fails when |
|---|---|---|
| 1 | Title line carries a fingerprint value and a generation date | line 1 has no `fingerprint:` / `generated:` stamp |
| 2 | `## Conventions` present and non-empty | heading missing, or heading with no body |
| 3 | `## Components` present, with at least one entry, every entry stating its variant axes (`—` counts) | heading missing, table empty, or a blank variant cell |
| 4 | `## Tokens` present, with at least one named tier, each tier declaring its consumer-facing form and enumerating its entries | heading missing, no `###` tier, a tier with no form declared, or a truncated list |
| 5 | `## Typography` present — enumerated utilities, or an explicit `None — …` | heading missing, or present and empty |
| 6 | `## Icons` present — at least one source with its code reference, or an explicit `None — …` | heading missing, a source with no reference form, or an unbounded set with no verification route |
| 7 | Every `status:` value is one of the three | any other value, including a plausible synonym |
| 8 | Every `successor:` names an entry that exists in this catalog | a dangling successor pointer |

The STOP message names three things — **the resolved catalog path, the rule that failed, and
what to change** — and offers the two ways forward: fix the catalog, or point the run at a
different one. Never name a fallback: there isn't one.

## What this contract deliberately does not specify

- **The catalog's filename and location.** The adapter's pointer, always.
- **The fingerprint recipe.** The adapter's row; the catalog carries only its output.
- **Tier names, tier count, component inventory, icon sources, class vocabulary.** All project
  facts. A contract that named any of them would be one project's catalog wearing a schema's
  clothes.
- **The icon ladder's order.** The adapter's row.
- **How a catalog gets written.** The authoring concern, not the interface.
- **What resolution does with `status`, near-misses, or tier preference.** The resolution
  rules' concern — this file defines the data those rules read.
