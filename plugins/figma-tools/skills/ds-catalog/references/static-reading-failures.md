# The five known static-reading failures

Read-only probes of two real design systems each defeated mechanical extraction, and did it
differently. Neither was pathological; both were ordinary, well-maintained repos. The five
shapes below are what defeated them, written as **probes**: what the shape looks like, why a
reader that only parses source misses it, what to read, and the question to ask when reading
does not settle it.

**This file is the extraction contract.** Phase 1 hands it to every explorer it fans out, the
way `figma-to-spec` hands `agents/figma-region-extractor.md` to a region agent. One source of
truth, whether the exploring is done by a subagent or by the main thread.

Two rules govern every probe:

1. **Each probe ends in a stated outcome** — *confirmed by reading* (with the file that
   confirmed it) or *a question for Phase 3*. There is no third outcome. "Nothing found" is
   never a result on its own: for four of these five, nothing-found is exactly what the
   failure looks like from inside a parser.
2. **A probe never writes.** Do not run the design system's build, its token generator, or
   its formatter to make a fact easier to read. A generated artifact that is stale on disk is
   itself a finding — say so, and ask.

The list is **open**. A sixth shape that defeats a read is a finding: record it in the run
report so the next project gets the probe for free.

---

## 1 — Variant axes declared away from the component's signature

**Shape.** The component's own signature says nothing useful: `variant?: string`, or a
spread-through prop, or no typed prop at all. The closed set of legal values lives somewhere
else — a `cva()` call, an SCSS module's exported class map, a lookup object keyed by string, a
class-name builder, a stylesheet whose selectors *are* the vocabulary.

**Why a reader misses it.** The signature parses cleanly and answers the question wrongly.
Nothing in it is malformed, so a parser reports a component with no variant axis, or with an
axis whose values are "any string".

**What to read.** Every styling file adjacent to the component, not just the component file.
Grep the prop name across the package and follow each hit. Look for an object whose *keys* are
the value vocabulary. Where a component composes another, read the inner one's axes too — a
wrapper routinely re-exports an axis it never declares.

**What to ask.** When the values are spread across more than one file, when the code accepts a
string it never enumerates, or when a value appears in a stylesheet with no call site: *is
this the complete set a consumer may pass, and are these the exact strings?*

**Cost of missing it.** The catalog records `—` (no axis) for a component that has three, or
records a guessed vocabulary. A spec then proposes a prop value that does not compile — and
the catalog's whole premise is that a value it does not list does not exist.

---

## 2 — Typography that exists only as a plugin call

**Shape.** The text utilities an app writes every day are emitted by a function — a Tailwind
`plugin(addComponents)` / `addUtilities` call, a `@layer components` block, a generated
stylesheet — rather than declared in the theme's own `fontSize` / `lineHeight` maps.

**Why a reader misses it.** The theme is the obvious place to read, and it comes back nearly
empty while the consuming apps are full of type utilities. The honest parser output is "this
design system has no typography scale", which is the opposite of true.

**What to read.** The framework config's `plugins` array, and every function in it, followed
into its own module. The built CSS, for what was *actually* emitted — a source map that feeds
the plugin is not the same set as the classes that exist. Any map declared but not exported is
dead data, and dead data is not an available style.

**What to ask.** When more than one typography route coexists (a legacy component, a plugin,
a token file part-way through a migration): *which of these is the current API, and how far has
adoption got?* Composite utilities that carry their own breakpoints also need confirming —
they must never be written with a responsive prefix, and only the human or the emitted CSS
knows which ones they are.

**Cost of missing it.** `## Typography` is written as `None`, and every text style in every
design then resolves as a gap that needs building.

---

## 3 — A public-surface map that filters, in both directions

**Shape.** The package's exports map, `files` list, barrel file, or publish config decides
what is reachable. It disagrees with the source tree in **both** directions: source files that
exist but are not exported (internal, never to be specced), and export keys that outlive the
source they pointed at (resolving to nothing at all).

**Why a reader misses it.** Reading the source tree over-reports; reading the exports map
under-reports and also over-reports, because a stale key looks exactly like a live one. Either
list alone is wrong, and the two are wrong in opposite directions, so neither is a safe default.

**What to read.** The exports map against the source tree, **both** directions, and then the
build's entry configuration — a file only reaches consumers if the build emits it *and* the
map names it. Where a built output is present, check that the artifact each key points at
actually exists. Version-control history explains the drift: a removal that cleaned the file
and not the key, or the reverse.

**What to ask.** Every disagreement, individually: *is this one internal by design, or a stale
key?* The human knows immediately and no amount of reading settles it — both look identical on
disk.

**Cost of missing it.** The catalog lists a component nobody can import, or omits one every
app already uses. Both are existence errors, and existence is the only thing the catalog is for.

---

## 4 — Two icon systems, side by side

**Shape.** An in-house inline set inside the design system, plus a third-party icon library
that the consuming apps depend on directly. Sometimes with a rule attached: one of them is
forbidden inside the design system, or forbidden in app code, and the rule lives in a
reviewer's head.

**Why a reader misses it.** Exploration is pointed at the design system, finds its icon module,
enumerates it, and stops. The second source is not in the design system at all — it is in the
consumers' dependency manifests. Nothing about the first source hints that a second exists.

**What to read.** The design system's own icon module *and* the dependency manifests of the
apps that consume it. Grep the consumers for icon imports and count the distinct libraries. For
a third-party library, find the pinned version — an open set is a real answer, but only with a
version and a stated way to verify a candidate name.

**What to ask.** *Which icon sources exist, where may each be used, and in what order should
they be tried?* Ask for sources **plural** — one source is the exception, not the rule. The
order itself belongs to the adapter's icon-resolution-ladder row, not to the catalog; ask for
it here because this is the conversation where the human knows the answer.

**Cost of missing it.** A spec names an icon nobody can render, or files a gap ticket for an
icon that ships in a library the app already installs.

---

## 5 — Deprecated values that still work through a runtime remap

**Shape.** A renamed variant value kept alive as an alias — mapped at runtime to its successor,
often with a development-mode warning. Or a deprecated component still exported, a token tier
superseded but still emitted, a whole family mid-migration with both spellings live.

**Why a reader misses it.** Both spellings work, so both parse as equals. A reader records two
sibling values with no relationship between them, or records only the new one and drops the old
— and the old one is precisely what a design drawn last year is drawn against.

**What to read.** The variant map, for values whose implementation forwards to another value
rather than carrying its own styles. Deprecation markers of every kind — annotations, warnings,
alias tables, comments. The changelog and version-control history for renames. Any migration
document the design system keeps for itself.

**What to ask.** Per entry: *is this current, legacy, or deprecated — and what replaces it?*
Legacy means it still works and is no longer the way to do it; deprecated means it is on the
way out. Never invent a successor: a legacy entry with no replacement yet is a real state and
recording it honestly beats a plausible guess.

**Cost of missing it.** Every entry defaults to `current`, the `status:` field becomes
decorative, and a design drawn against the old name resolves either as clean (wrong — it hides
a migration the implementer needs to know about) or as a gap that needs building (wrong — it
ships today). The status fields exist to prevent exactly that pair of failures, and they are
only ever as good as this conversation.
