# Fidelity ledger — the contract every fidelity consumer imports

Shared by `to-task`, `work-on-task`, `to-prd`, `to-issues` and `work-on-issue` (prd-workflow),
`to-spec`, `to-spec-tasks`, `work-on-spec` and `spec-worker.md` (ado-workflow), `figma-to-brief`
and `prototype-to-spec` (figma-tools), and `deep-grill` (lk). Every fidelity rule lives here once,
so those consumers cannot drift from each other.

Each section is numbered. A skill that needs one cites it as "per `../_shared/fidelity-ledger.md`
§N" rather than restating it.

## §1 — Ledger row transport

The brief's ledger rows for this issue's elements, **pasted verbatim**, plus the grill's decision
and the instruction it produces.

**The rows are extracted by a command and pasted from its output. They are never retyped.** A row
re-emitted from context comes back shorter — a truncated Layout facts cell, a reworded Interaction
cell, a Fidelity class stripped of its tail — and that shortening is the single largest fidelity
leak this pipeline has measured. So print the rows, paste the printed bytes, and edit them in
exactly one place: the right-hand end.

**1 — Print the in-scope rows**, selecting them by the Element cell:

```
sed -n '/^## Fidelity ledger/,/^## /p' <brief-path> \
  | awk -F'|' 'NF>2 && $2 ~ /^[[:space:]]*(<element>|<element>|…)[[:space:]]*$/'
```

One alternative per in-scope element, spelled as the brief's Element cell spells it. Where an
element name carries regex punctuation, `grep -F` on a distinctive substring of each row does the
same job. Print every in-scope row in one command and read its output before pasting: a command
that prints fewer rows than the issue has elements in scope has a selector that does not match,
not a brief that is missing a row.

Where the rows' source is a tracker body rather than a file on disk — a spec's table, a parent
work item's — write that body to a file first and run the same command against it. The source
changes; the transport does not.

**2 — Paste that output** into the issue under the header row, byte for byte, keeping **every
column the brief has** — Element, States, Exact copy, Tokens, Layout facts, Interaction, Source, DS
candidate, Fidelity class, and any column the brief adds later. The header row and its separator
are copied from the brief the same way, with the two new headers appended.

**3 — Append two cells to each pasted line, and change nothing else.** Each printed line ends with
the brief's closing `|`, so the whole edit is ` <Decision> | <Instruction> |` added to its end:

| …brief's columns, verbatim… | Decision | Instruction |
| --------------------------- | -------- | ----------- |

- **Decision** — the class the grill settled in `## Fidelity decisions`. The cell **opens with
  exactly one of** `DS as-is` / `DS with overrides` / `local component` / `DS change` — that
  string, not a synonym, optionally in backticks. Where the grill named an override, ` — ` and the
  grill's own words follow it. `Build local`, `Local`, `Use the DS component` and every other
  paraphrase is a defect, and so is a cell that opens with the override words instead of the class.
- **Instruction** — imperative, and built only out of the row's own cells and that decision: "build
  local `<X>`", "use `<DS candidate>` + override `<the named override>`", "use as-is, no overrides".
  A `DS change` instruction names the DS repo issue it depends on.

**4 — Check the paste before publishing.** With N as the brief's column count, each pasted row cut
to its first N+1 pipe-separated fields is byte-equal to the row the command printed, cut the same
way. Run the step-1 command a second time against the written body and diff the two:

```
N=$(awk -F'|' '/^\| *Element *\|/ {print NF-2; exit}' <brief-path>)
diff <(<step 1, against the brief>    | cut -d'|' -f1-$((N+1))) \
     <(<step 1, against the body>     | cut -d'|' -f1-$((N+1)))
```

An empty diff is the pass. A row that differs is a defect: replace it with the printed bytes rather
than editing it towards them.

**A consumer that emits another markup.** Where the table is HTML rather than markdown pipes, the
conversion is mechanical and per cell — each cell of a printed line becomes one `<td>` holding that
cell's text character for character, with the escaping that consumer's section states. The check in
step 4 runs on the printed lines, before the conversion, and nothing is retyped at either step.

There is no paraphrase column. If you find yourself writing a shorter version of the Layout facts
cell, stop — that is the rewrite the extraction command exists to prevent.

**Figma briefs — the Source column and the pin line.** In a brief produced by `figma-to-brief` the
**Source** cell holds `<fileKey>:<nodeId>`, and that node is the **element** node — never a frame,
never a page root. A frame id in that cell is a broken row: send it back to the brief rather than
reading the frame. A consumer that copies the rows also copies the brief's pin line, character for
character:

```
Pinned at figma <fileKey> · node <nodeId> · version <versionId or YYYY-MM-DD> · brief <path>
```

The pin line is what lets a later session re-read the same design state. A row copied without it is
unpinned, and an unpinned row is an opinion.

## §2 — Hard rules

<hard-rules>
1. **No unbacked dismissal.** Never write "already matches", "near-imperceptible", "minor",
   "low priority", "CSS polish" or any equivalent about a visual item unless a ledger row of class
   `DS as-is` stands behind it. The ledger row is the evidence; a code-recon impression is not.
   Without that row the item is a normal numbered change with no hedging adverb attached.
2. **Never downgrade a scorecard element.** Every element named in the `## Scorecard` of the file
   the adapter's `Fixed scorecard` row names, when that row is present and covers this ticket, is a
   first-class numbered change and a verify row if it is in this issue's scope.
   It is never demoted to a footnote, a "polish" bucket, a parenthetical, or a priority marker.
3. **Symbols, never line numbers.** Reference `EligibilityCriteriaBuilder.tsx` → `DateOfBirthRow`,
   never `:242`. Line refs rot between the grill and the implementation session, and a stale one
   sends a cold worker to the wrong code with full confidence. No `file:line`, no `~:290-315`, no
   "around line N" — not even hedged with a drift disclaimer.
4. **Every visual instruction cites its ledger row.** Each numbered change that alters what the
   user sees names the ledger row it comes from and that row's decided class. An instruction with
   no ledger row behind it is an improvisation, and improvisation is what this pipeline exists to
   stop.
5. **Never translate a ledger fact into a utility class.** The ledger says "124px fixed width,
   wraps to multiple lines"; the issue says "124px fixed width, wraps to multiple lines". It does
   not say `sui-min-w-[124px]`, `sui-w-[124px]`, or any other class. Translating a fact into a class
   is the implementer's job, done against the source slice — a prototype line range or a Figma
   element node. Where the prototype source already holds the class, the slice carries it and the
   implementer copies it from there.
6. **Never name a DS component the ledger did not name.** The only DS component names allowed
   anywhere in the body are the ones standing in the ledger's **DS candidate** column or named by
   the grill's `## Fidelity decisions`. Do not add `IconButton`, `LabelButton`, `Badge`, `Input` or
   any other component to an instruction because it reads as the obvious primitive — each of those
   ships chrome the design may not have. When the ledger names no component, the instruction says
   "build local" and stops there.
7. **Never rename an icon.** Icon names are copied from the ledger character for character.
   `arrow_drop_down` is not `keyboard_arrow_down`; `close` is not `cancel`. An icon name that does
   not appear in the ledger or the decisions does not appear in the issue.
8. **`## Changes` adds no layout facts.** Every numbered change cites a ledger row and the grill
   decision for it, and restates only what those two contain. A px value, a radius, a token, a
   stack direction, a nesting or an anatomy that appears in neither is an invention — delete it, or
   go back to the brief and quote the row that holds it.
9. **Repo recon is not a fact source.** A class name, prop or component read out of the current app
   — by you, by the grill's recon lanes, or from an earlier run's code — is **not** a layout fact
   and may not appear in the ledger section, in `## Changes`, or in any instruction. The brief's
   ledger and the source slice — a prototype line range or a Figma element node — are the only
   layout-fact sources this issue has. This rule governs layout facts only; engineering facts
   (hooks, services, query keys, paths) come from repo recon as the PRD's
   `## Implementation Decisions` and the issue's `## Worker context` already allow.
</hard-rules>

A body that breaks any of the nine is not published. Fix it and re-read before asking to create.

Run 1 lost most of its polish at exactly these nine points: the ledger was re-summarised into a
shorter column, `arrow_drop_down` came out as `keyboard_arrow_down`, "124px fixed" came out as
`sui-min-w-[124px]`, and `IconButton` / `LabelButton` arrived as build instructions the brief never
gave. The implementer worked from the issue alone, so the compressed copy was the only truth it had.

## §3 — Screenshot blocks

One block per in-scope state, screenshot embedded inline:

### `<step-id>` — <state name>

![<step-id>](https://raw.githubusercontent.com/<proto-owner>/<proto-repo>/<sha>/<proto-path>/spec/screenshots/<step-id>.png)

Scorecard element **#<n> <element name>** — <one line: what this screenshot is the target for>.

The prototype repo is **private** (`gh repo view <proto-owner>/<proto-repo> --json isPrivate`
confirms it), so a raw URL renders as a broken image for a human reader and `gh` cannot attach
uploads to an issue body. Keep the embedded raw URL anyway — it is the pinned address — and put
directly under every screenshot a fenced fetch line the implementer runs before touching code:

```
gh api "repos/<proto-owner>/<proto-repo>/contents/<proto-path>/spec/screenshots/<step-id>.png?ref=<sha>" --jq .download_url | xargs curl -sL -o "$SCRATCH/<step-id>.png"
```

and one sentence above the Design reference blocks: "Download every screenshot below and read it
as an image before implementing; humans open the state URLs on the preview instead." An
implementer that has not read the PNGs is implementing from prose, which is the failure this
pipeline exists to stop.

**Figma brief variant — the screenshot stays on disk.** Where the brief pins Figma nodes, nothing is
copied to the tracker: no attachment, no image tag, no url in the body. The block carries the PNG's
path on disk and the pinned Figma address, and nothing else:

### `<state-id>` — <state name>

Screenshot: `.claude/briefs/<ticket>/screenshots/<state-id>.png`

Pinned address: `https://www.figma.com/design/<fileKey>/?node-id=<nodeId>`.

Scorecard element **<n> — <element name>** — <one line: what this screenshot is the target for>.

The scorecard number never carries a `#`: on Azure DevOps `#<n>` autolinks work item n, so `#3` in a
task body silently links an unrelated ticket instead of naming scorecard element 3.

`figma-to-brief` saves one PNG per in-scope state at that path, on this machine. The brief, the spec
and the tasks are written for the implementer, and the implementer has the repo. A human who wants
to see the state opens the pinned Figma address.

The implementer reads each PNG from that path with the Read tool, as an image, before it writes
code — that is step 2 of the §6 evidence gate. A PNG the block names that is not on disk is a
**deviation to report, and the run stops there**: regenerate the brief with `figma-to-brief` so the
file exists, and never implement from the prose instead.

One sentence above the Design reference blocks: "Read every screenshot below as an image before
implementing; humans open the Figma node link instead."

## §4 — Source slices

One block per row whose Decision is `local component` or `DS with overrides`, built from that row's
**Source** column (`components/<file>.tsx:Lstart–Lend`):

#### `<element>` — `components/<file>.tsx:<L1>–<L2>`

```
gh api "repos/<proto-owner>/<proto-repo>/contents/<proto-path>/components/<file>.tsx?ref=<sha>" --jq .content | base64 -d | sed -n '<L1>,<L2>p'
```

One sentence above the blocks: "Run every fetch line below and read every slice before writing any
code — the slice is where the hotspots, the nesting, the icon sizes and the exact classes live; the
screenshots and this table cannot carry them." A slice is a **range**, never the whole file: the
implementer reads layout facts out of it, never control logic or overlay code.

A row whose Source column names no line range gets a block saying `source-only range missing — ask
before implementing`, not a fetch line for the whole file.

**Figma brief variant — the slice is a node read.** Where the row's **Source** column holds
`<fileKey>:<nodeId>`, the slice is the **element node**, never the frame or page root: a frame read
answers with the whole screen and buries the row's facts inside it.

#### `<element>` — figma `<fileKey>:<nodeId>`

```
mcp__figma-dev-mode__get_design_context(fileKey: "<fileKey>", nodeId: "<nodeId>", clientLanguages: "typescript", clientFrameworks: "react")
```

and, where the row's **Tokens** cell names a bound variable, the second read on the same node:

```
mcp__figma-dev-mode__get_variable_defs(fileKey: "<fileKey>", nodeId: "<nodeId>", clientLanguages: "typescript", clientFrameworks: "react")
```

`mcp__figma-dev-mode__get_metadata` (the node's own id, name, type and size) and
`mcp__figma-dev-mode__get_screenshot` (a render of that one node) are available on the same server
when a row is ambiguous without them. They are extra reads, so name them in the block only when the
row needs them.

Take layout facts out of the result and nothing else: auto-layout direction, padding, gap, corner
radius, size, icon name and icon size, text style, and the bound variables. Never prototype wiring,
never control logic, never overlay positioning.

One sentence above the blocks: "Run every node read below and read every result before writing any
code — the node is where the nesting, the hit areas, the icon names and sizes and the bound
variables live; the screenshots and this table cannot carry them."

A row whose Source column names no node id gets a block saying `node id missing — ask before
implementing`, not a read of the parent frame.

**Budget.** Every node read counts against the budget the adapter's Figma source rows state; only
`whoami` is free. Read each in-scope node once, and never walk a frame to find a node the ledger
should have named.

## §5 — Verify rows

**Vocabulary.** Where the ADO skills apply, "issue" in this section reads as "task" — the work-item
type the project adapter (`<repo-root>/.claude/project/adapter.md`) names for a spec child. The
rules are otherwise unchanged.

**Where the rows come from.** Scorecard rows come from the file the adapter's `Fixed scorecard` row
names, and only when the adapter registers that row and that file has a `## Scorecard` section for
this ticket. Otherwise derive them: one screenshot-pair checkbox per
in-scope ledger row whose Decision is not `DS as-is`, with the pass condition = that row's Layout
facts + Interaction cells verbatim, prefixed by the row's Element and State(s). Never paste another
ticket's scorecard. Polish checklist: same rule, only when the run entry is for this ticket;
otherwise omit it and say "no polish checklist for this ticket" in the final print.

A derived row is a scorecard row in every later sense — hard rule 2 protects it, the implementer
marks it `expected pass` / `cannot tell from code` like any other, and the judge scores it on the
pair.

**A derived row for an element that is not built.** Where the row's Decision or Instruction says
the element is not built — `Not built`, `Override the design — not built`, or any equivalent — the
pass condition is `absent from the app — <Element>`, followed by that row's Layout facts verbatim
as the description of what must be absent. It is one checkbox like any other derived row, and the
pair it is scored on passes when the app shows nothing where the design shows the element. The
implementer marks it `expected pass` when nothing renders.

**Screenshot pairs** — boot the app (`<adapter boot command>`), capture each state, and pair it
against the prototype PNG embedded above. A row passes on the **pair**, never on a text claim that
it matches.

- [ ] pair `<step-id>` vs app — <the scorecard row's pass condition, verbatim>
- [ ] pair `<step-id>` vs app — <pass condition>

One checkbox per scorecard element in scope, carrying that row's pass condition word for word from
that file — or, for a derived row, from the ledger cells named above. Do not paraphrase a
pass condition and do not merge two rows into one checkbox.

**Polish checklist** — copied verbatim from the current run's `## Polish checklist` in that same
file, one checkbox per item, in the file's order. It is scored alongside the scorecard
and is not optional, not a "nice to have", and not a footnote:

- [ ] <polish item, verbatim>
- [ ] <polish item, verbatim>

Take the items from the run entry for **this ticket** — the newest `## Run <n>` section under this
ticket that has a `## Polish checklist` block. If there is no such
entry, or it has no polish checklist, say so in the final print rather than writing one yourself.

## §6 — Implementer contract

<evidence-gate>
No file is created or edited until all three of these are done, in this order:

1. **Read the brief's `## Fidelity ledger` in full** — every row, every column, including rows the
   issue put out of scope. The issue's table is the same rows; the brief is where they live, and
   reading it is what catches a column the issue dropped.
2. **Run every screenshot fetch line in the issue and read each PNG as an image.** Not the URL, not
   the caption — the actual image, through the Read tool. A screenshot that will not fetch at the
   pinned SHA is a deviation to report, not a step to skip.
3. **Run every source-slice fetch line in the issue and read each slice.** These are line ranges out
   of the prototype component. They carry what neither the screenshots nor the table can: the click
   targets, the nesting, the icon names and sizes, the exact classes. Read layout facts out of them
   and nothing else — never copy control logic, state handling or overlay positioning code.

**Figma brief variant.** Where the brief pins Figma nodes, step 2 reads every PNG the issue's
screenshot blocks name, from its path on disk, as an image, and a PNG that is not on disk is the
deviation to report. Step 3 runs every node read the issue names and reads each result, taking the
hit areas, the nesting, the icon names and sizes and the bound variables out of them and nothing
else. The one line then reads: "read ledger (N rows), N screenshots, N nodes."

Then state, in **one line**, what was read: "read ledger (N rows), N screenshots, N source slices."

An implementer that skipped any of the three **may not proceed**. There is no partial version of
this gate: "I read most of them" is a failed gate. Say what is missing and stop.
</evidence-gate>

While implementing:

- **Layout facts come from the ledger row and the source slice. Never from the current app.** A
  class already in the repo tells you what ships today, which is the thing being changed. Do not
  carry an existing class forward because it looks close, and do not treat a Run-N class as a
  design fact.
- **Icon names are copied character for character** from the ledger and the slice.

<self-audit>
Write this table **before** running L2, with the code in its finished state. One line per ledger row
in scope — every row, including the ones you believe are trivially correct:

| Ledger row | Fact(s) | Rendered by (file:symbol) | matched / deviated | reason |
| ---------- | ------- | ------------------------- | ------------------ | ------ |

- **Ledger row** — the element name, as the ledger spells it.
- **Fact(s)** — the row's layout / interaction / token facts, short but not re-summarised away. A
  row with five facts gets five facts.
- **Rendered by** — the concrete `file:symbol` in your diff that paints it (`EligibilityValuePill.tsx:ValueChip`).
  Not a directory, not "the builder". A row with nothing to point at is a deviation.
- **matched / deviated** — one or the other. There is no "partially".
- **reason** — required on every `deviated`. Why the code departs from the row, and what you did
  instead.

**A deviation with no reason is a blocker.** Fix it, or stop and report it — never leave it standing
in the table as a note and carry on to the gate.
</self-audit>

Then tick the issue's `## Verify` checkboxes **from the code**, not from a render — the human scores
renders, and a text claim of a visual match is worth nothing here (this is exactly what Run 0 got
wrong). Two lists, both filled in the final print:

- **Scorecard rows in scope** — per row: `expected pass` (the code does what the pass condition
  describes, and you can name the symbol that does it) or `cannot tell from code` (the condition is
  about rendered appearance you cannot verify without the screenshot pair). A row derived per §5
  counts here exactly like a row taken from a fixed scorecard; there is no lighter treatment for a
  ticket that has no fixed scorecard.
- **Polish checklist items** — the same two markings, one line each, in the issue's order.

Never mark a row `pass`. `expected pass` is the strongest claim this session is allowed to make.
