# The existence source

What a brief resolves every element, token, type utility, dimension and icon against, and where
it comes from. **There is one existence source and it has two origins**, chosen by the adapter's
`## Design system` → `Repo role:` row:

| `Repo role:`              | Origin                                                                                          | Pin in the brief      |
| ------------------------- | ----------------------------------------------------------------------------------------------- | --------------------- |
| `consumer`, or no row     | the **registered catalog**, through the `Catalog:` pointer                                      | `Catalog: <fingerprint>` |
| `library`                 | an **assembled list**, built from the library's own source as this file describes               | `Source: <git sha>[+dirty]` |

**The role is an adapter fact, never a run-time flag or a parameter**, and it is never inferred
from the tree: a `components/` directory is not evidence of a library, and neither is a package
name. An absent row means `consumer`, so an adapter written before the row existed reads
unambiguously and needs no edit.

Any skill that resolves a design against a design system reads this file for both halves. The
consumer half is short because the catalog already exists and its shape is
`catalog-contract.md`. The library half is most of this file,
because there the list is built at run time.

## The guarantee

**The run resolves only against the explicit list, and may not add to it.** An entry that is not
on the list does not exist, whatever the run knows about design systems in general.

That guarantee is the whole reason an existence source is required. Without one, nothing stops a
brief citing a spacing scale, a token name or an icon set from a well-known public design system
this project never had, and it reads as entirely plausible to everyone who reviews it — which is
why nobody catches it. A catalog is one way to supply the list; the guarantee needs only that
*some* explicit list exists and that the run treats it as closed.

## Consumer: the registered catalog

Resolve it through the adapter's `Catalog:` pointer, read every path it names and treat the
union as the catalog, then validate it against
`catalog-contract.md`. No catalog, a catalog that fails the
contract, or a named path that does not exist is a STOP. Nothing else in this file applies on the consumer side.

## Library: the assembled list

A library repo **is** the design system, so its own source is the authority on what exists, and
the list is assembled from it once per run, before any element resolves.

### What the list covers

Five kinds. A run that resolves a kind with no section on the list turns every finding of that
kind into a gap, so each kind is always present:

- **tokens by tier** — semantic, alias, primitive;
- **typography tokens and utilities**, enumerated;
- **dimension tokens** — spacing, radius, size;
- **the components this library ships**, each with its variant axes and their listed values;
- **the icon sources the icon resolution ladder names, with their entries.**

Write every entry in the adapter's **Consumer-facing emission form** — the form an app writes,
which is a separate fact from the Tailwind class prefix and from the CSS variable prefix. A run
emits an entry exactly as the list spells it, so a list in the library-internal form produces a
brief recommending classes no consumer can write.

Record, per entry, the **status** the source stamps it with (`current` / `legacy` /
`deprecated` / `unused`) and its successor where one is recorded. An entry with no recorded
status reads as `current`, so a legacy match resolves with a flag rather than reading as a gap.

### Where each part comes from

Three adapter rows in `## Design system` name the sources. All three are required in a library
repo; none of them is inferable from the tree.

1. **Tokens, typography and dimensions — the `Token pipeline` row.** Read the token source it
   names. A row naming a generator and the file it consumes means one read of that file gives
   all three parts. A row reading `None — <how tokens are edited instead>` names the files
   tokens are edited in, and the run reads every one of them; there is no single file whose read
   gives the set.
2. **Components and their axes — the `Variant mechanism` row.** Enumerate the components in the
   design system's own component directory, which the `Design-system source` row names (in a
   library repo, this repo). Read each component's axes and values through the **Variant
   mechanism** ladder, rung by rung in its stated order, stopping at the first rung that
   resolves and honouring the trap the row names. The axes come from the declaration, never from
   a filename and never from the conditional branches that implement them.
3. **Icons — the `Icon resolution ladder` row.** Enumerate the entries of each source the ladder
   names, in the order it names them, **once per run**. The list keeps the ladder's order, so an
   icon still resolves through the ladder's first source that carries it.

**A part whose source does not resolve is written into the list as
`<kind>: none resolvable — <why>`, and the run says so once, up front.** It is never left out:
an omitted section and an empty one read the same, and both say *nothing of this kind exists
here*. The marker is what lets the grill read the resulting gaps as unresolved existence rather
than as things the library must build.

### A registered catalog in a library repo

Optional. A library repo needs no catalog, because its source is the answer. Where the adapter's
`Catalog:` pointer names one anyway:

- **It is resolved and validated exactly as on the consumer side** — every path the pointer
  names, the union, the shape contract. A registered catalog that fails the contract, or names a
  path that does not exist, is a STOP on both sides: a project that registered a catalog is
  asserting it is valid, and a malformed one is a defect, not an absence.
- **It is a cross-check, never the primary answer.** It contributes component and icon entries
  to the list, and where it and the source disagree about an entry, the source wins and the
  disagreement is noted on the entry.
- **Where the token source resolves nothing, the catalog's token tiers stand in for the token,
  typography and dimension parts**, and the run says so once, up front. This is the one case in
  which a catalog supplies tokens in a library repo.

### What stops a library run

- **No token source behind the `Token pipeline` row, and no registered catalog** → STOP. Name
  each thing looked for and where: the row's value, each file it names and whether it exists, and
  the `Catalog:` pointer or its absence. Nothing is then left that could make the list explicit.
- **An absent `Variant mechanism`, `Token pipeline` or `Icon resolution ladder` row** → STOP,
  naming the row and `/figma-tools:setup` as what writes it. Never pick a mechanism or a token
  source by reading the code: the shapes that look like the declaration are usually its
  implementation.

### The pin, and what the brief carries

The list is pinned to the commit it was read from:

```
git rev-parse HEAD                  # the sha
git status --porcelain              # any output → append +dirty
```

The brief's header carries `Source: <sha>`, or `Source: <sha>+dirty` where the working tree has
uncommitted changes, followed by **the source paths the list was assembled from** — the token
source file or files, the component directory, each icon source, and each catalog path where a
registered catalog contributed.

**The assembled list itself is never written into the brief.** It is the run's working input, and
the source paths plus the sha are enough to rebuild it; a copy in the brief would be a second
source of truth that ages the moment the library changes.
