# The `[FINDINGS]` Work Item

The shape of the work item an Azure DevOps QA pass writes its failures into, and the one place
that says how it is found again.

Two skills share it: **`ado-workflow:manual-qa` is its only writer** — it creates the item and
appends each finding — and **`ado-workflow:triage` is its only reader**, which walks the findings,
files a `[TASK]` for each one being fixed, writes the rest up as a comment on the parent, and closes
the item. Neither owns the shape alone, so it lives here.

The plugin carries this file so the pointer resolves from inside any of its skills
(`../references/findings-item.md`) and from a marketplace install cache alike — no skill borrows a
reference out of a sibling skill's directory.

**Project facts come from the project adapter** at `<repo-root>/.claude/project/adapter.md` →
`## Repo` → `### Azure DevOps`: the organisation, the **work-item project**, the **work-item
type**, the board states and the title prefixes. Nothing below hardcodes one.

`[SPEC]`, `[TASK]`, `[FINDINGS]` and `[BUG]` are **shorthand for the adapter's *Title prefixes*
row**, written out for readability. If that row names different prefixes, they win.

**What the MCP does here is narrow, and worth saying out loud: it reads a work item, appends a
finding to it, creates it, and closes it. It never judges whether a finding is correct.** The
human decides a flow failed; `triage` and the human decide what a finding is. Every call below is
bookkeeping on a decision a person already made.

## One per run, created lazily

**One item per *run*, never one per `[SPEC]`.** A run is the slice of `[TASK]`s a single
`work-on-spec` loop landed, and it is the unit a pass covers — one pass, one findings item.

**It is created on the first failure of a pass and not before.** A pass that finds nothing creates
nothing: no item, no empty item, no "no findings" placeholder. An item created up front would put a
work item on the board for every clean pass, and every one of them would have to be opened to learn
it was empty.

A second run against the same `[SPEC]` gets its **own** item. The first is never reopened, never
appended to, and never edited.

## Shape

| Property | Value |
|---|---|
| Work-item type | the adapter's **work-item type** — the same one the `[SPEC]` and `[TASK]`s use |
| Parent | the **parent work item the `[SPEC]` hangs off** (its `Hierarchy-Reverse`) — a User Story or PBI depending on the process. So the item is a **sibling of the `[SPEC]`**, never a child of it |
| Title | `[FINDINGS] <spec title, prefix stripped> — run of <YYYY-MM-DD>` |
| Findings | in **`System.Description`**, Markdown |
| State at creation | the adapter's **pickable** state — nothing else is meaningful, since this item is not work |

Create it with **`wit_work_item_write`, `action: "add_child"`**, against the adapter's **work-item
project**: that one call sets `System.Parent` *and* writes the hierarchy relation
([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) §0 and §3), so
there is no follow-up link write. Pass **`format: "Markdown"`** for the description.

If the running server's `add_child` will not take a `format` argument, that is the *tool names come
from the running server* case: say so in the run, and fall back to `action: "create"` — which §1
confirms takes a per-field `format` — plus the `type: "parent"` link from §3. Never drop the format
flag to make a call succeed; a body that lands as HTML takes the whole contract with it.

**Then verify the hierarchy before reporting** (§5): re-fetch the parent with `expand: "relations"`
and no `fields` filter, and confirm the new item appears as `Hierarchy-Forward`.

Two back-references, both cheap, both worth writing:

- the `Spec: #<spec-id>` line at the top of the description — the same line `to-spec-tasks` writes
  on a `[TASK]`, so provenance reads identically on both;
- the `Related` link back to the `[SPEC]` that the bare `#<spec-id>` in that line creates on its
  own. **This is one of the two places a bare `#NNNN` is wanted** — the chip and the relation are
  both the point. Everywhere else in this document, ids are backticked.

Neither back-reference is how the item is found. That is the next section, and it is deliberately
not either of these.

## How `triage` finds it — decided, once, here

**`triage` scans the parent's children for the `[FINDINGS]` title prefix.** That is the route, and
it is now the only automatic one. The prefix is **load-bearing on this tracker by design** — every
kind of child under that parent is the same work-item type, so the prefix is the only thing that
separates a findings item from a `[TASK]` or a `[BUG]`, and it is the adapter's *Title prefixes*
row that supplies the literal.

**There is no write-back into a QA comment, and there is no QA comment.** This document used to
name the run-context line of `work-on-spec`'s per-run QA comment as the primary lookup, with the
first failure of a pass appending a ``` · findings `#<id>` ``` clause to it as a never-edit
carve-out. The loop posts no such comment any more, so both halves are gone: `manual-qa` creates
the item and appends findings to it, and writes nothing anywhere else to say the item exists.

So `manual-qa`, on the **first failure of a pass**, does exactly one write — it creates the item
(above) — and names the new item's id **backticked, in the terminal and in its end-of-pass
receipt** on the `[SPEC]`. That receipt is free-form output: it is a courtesy to a human reading
back, **not** a lookup route, and nothing parses it.

**What the scan cannot do, stated plainly**, because the route it replaced could:

- **It cannot say which run.** One parent carries every `[SPEC]`'s findings items and every run's,
  so a scan returns N and has to narrow. What narrows it is what the item itself carries — the spec
  title and run date in its title, and the `Spec: #<spec-id>` line at the top of its description —
  and `triage` says which item it picked and which run that is, rather than assuming the newest.
- **It cannot distinguish a clean pass from a failed search.** No matching item means no failure was
  recorded, which is the common case; but that is an inference from an absence rather than a stated
  fact, so `triage` reports which parent it scanned and what it matched on, and lets the human
  correct it.

Both costs are accepted rather than overlooked. The alternative was a lookup that only worked
because the loop first published a script it had no business writing.

**Walking the `[SPEC]`'s relations is still not a route.** It narrows to a spec, not to a run — the
same ambiguity one level down — and the relation set is not trustworthy: a bare `#NNNN` anywhere in
any body silently creates a `Related` link
([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) §2), so a `[SPEC]`'s
relations accumulate items nobody linked on purpose.

A **pasted id** is the shortcut, and it is the input worth offering whenever the scan is ambiguous:
a human who hands `triage` a `[FINDINGS]` id has answered the question, and the lookup is skipped
entirely. That is an input shortcut, not a second discovery route.

## The body

The head is written at creation; each finding is appended after it.

<findings-template>

Spec: #12805

Findings from the QA pass on the run of 2026-08-02 — PR [<repo> PR 4711](https://dev.azure.com/<org>/<repo-project>/_git/<repo>/pullrequest/4711)

### [FINDING] 1 — <one-line symptom>

**Step:** flow 3 ("search and filter"), sub-step 2
**From:** `#12805`

**Symptom:** what the tester saw.

**Classification:** bug (this repo) · bug (contract boundary) · deferred-by-design · works-as-intended · enhancement
**Severity:** low / med / high

**Evidence:** the one decisive probe, the text on screen, the log line — the thing that removes ambiguity.

**Where:** `path:line` — where the symptom surfaces.

**Root-cause hypothesis:** *(labelled as hypothesis, kept separate from the facts above)*

**Repro:** numbered, exact steps.

</findings-template>

The rules governing that template are deliberately **outside** the fence. Copy the fence, not this
prose — instructions pasted inside a body template ship to the reader as work-item text.

- **`### [FINDING] ` is a parse contract**, hardcoded in `manual-qa` and `triage` and deliberately
  absent from the adapter. It is not a title prefix and it is not a scanning convention: a project
  free to edit it would get a `triage` that reads the item, matches nothing, and reports a clean
  pass. Bracket, the word, bracket, space — then the ordinal.
- **Findings are numbered from 1, continuously, in the order they were appended.** The writer gets
  the next ordinal by counting `### [FINDING] ` markers in the description it just read; it has to
  read the field before appending anyway (below), so this costs nothing.
- **`**Step:**` carries the position in the pass — flow number, flow name, sub-step number.** No
  permalink, and none is possible: `manual-qa` composes the pass in its own session and posts it
  nowhere, so there is nothing to link to. Run provenance needs no field either — the item **is**
  the run — so the field's whole job is saying where inside the pass it failed.
- **`**From:**` is the backticked owning-`[TASK]` id**, lifted by `manual-qa` from the `AB#<id>`
  references in the commits the failing flow exercises. Backticked for the same reason as
  everywhere else. Space-separated where the flow exercises more than one.
- **Both fields are omitted entirely on a finding noticed outside any flow** — there is no flow and
  no attribution to lift. Omit the lines; do not write "n/a".
- **Escape angle brackets at synthesis time** (§1). A description escapes rather than strips, so
  nothing is lost either way, but pre-escaping is what makes the body survive whichever call it
  later goes through.
- **Prefer inline code spans to fenced blocks for pasted output.** A fence in a *comment* comes back
  **empty** — measured on this tracker, and the reason the plugin puts commands in code spans. No
  equivalent has been measured for a description — treat that as unknown rather than safe. Where a multi-line paste is genuinely
  unavoidable, read the description back after the write and confirm the block survived.

## Why the description, and not comments

The two surfaces sanitise differently, and the difference decides this. A **description escapes**
markup and round-trips losslessly; a **comment strips** it, and the ADO UI renders a comment from
its sanitised text rather than its `renderedText` (§8) — so what the read path drops does not appear
on screen escaped, it simply is not there, and the sentence around it reads as though it were always
worded that way.

A findings body is the most markup-dense thing this plugin writes: pasted error text, element names,
generic types, file paths. `triage` has to read it faithfully or it root-causes the wrong thing. So
findings go where reading is lossless. The only thing this plugin still posts as a *comment* on a
work item is `manual-qa`'s free-form receipt, which nothing reads back — so a strip there costs a
sentence's polish, not a root cause.

## Appending a finding

**There is no append operation on a long-text field.** A JSON-Patch `op: "add"` against
`/fields/System.Description` replaces the whole field, so every append is a genuine
read-modify-write, and it takes the full discipline:

1. **Fresh read immediately before every write.** `wit_work_item` (`action: "get"`), `expand:
   "relations"` and **no** `fields` filter — the two are mutually exclusive and a filter suppresses
   relations (§4). Never write back a body held in context since the pass began.
2. **Append to the fetched text.** Existing findings stay byte-identical; nothing is re-rendered
   from a model-held structure, nothing is reflowed, no earlier finding is edited.
3. **Write with `wit_work_item_write`, `action: "update_batch"`, carrying `format: "Markdown"`
   per item.** Plain `action: "update"` has **no** `format` option and falls back to HTML (§1) —
   using it here would flip the field out of Markdown and strip every unescaped angle-bracketed
   token in every finding already recorded, not just the new one.
4. **Carry the format forward rather than probing for it.** A read never reports a stored format
   (§8), so an absent `multilineFieldsFormat` means *the format was not reported*, never *this field
   is HTML*. The create set it; every later write restates it.
5. **Read the description back and confirm the new finding is there** before moving on. A write
   returning is not evidence it landed as meant.

## After triage: closed, never deleted

`triage` closes the item when it has disposed of every finding. It does **not** delete it.

Triage *rejects* findings as well as promoting them — works-as-intended, deferred-by-design,
duplicate — and the rejection reasoning lives nowhere else. Delete the item and the next pass
re-reports the same false finding, and somebody re-investigates it from scratch. A closed work item
is a permanent record at no cost: it drops off the board, keeps its description, and stays reachable
from the `[SPEC]` by the `Related` link the `Spec:` line created.

Close it with a **state-only** write — `wit_work_item_write`, `action: "update"`, one `op: "add"` on
`/fields/System.State`. That call touches no long-text field, which is what makes plain `update`
safe for it. **Never bundle a description edit into the same call**; anything that writes the body
goes through `update_batch` with `format`, per the previous section.

The **terminal state name is not an adapter value.** The adapter names the three in-flight roles
(pickable, claimed, committed-awaiting-merge) and says every other state on the board is terminal —
it does not name which terminal state to use. Read the type's allowed states from the process
(`wit_work_item`, `action: "get_type"`), pick the item's terminal state, and **announce which one
you used**. If the write is refused, report it rather than trying a near-miss: a state name the
board does not have is a rejected write or a silent no-op depending on the call, and neither reads
as "you used the wrong vocabulary".

## There is no back-annotation onto this item

The GitHub sibling writes `**Triaged:** #N` back onto each finding comment, because those comments
live on a PR forever and a second pass has to tell a fresh finding from one it promoted last week.
**That channel does not exist here and must not be reintroduced.**

A fresh item per run means everything in it is new by construction. "Already handled" is answered by
the item being **closed** — one field, read in the same fetch that loads the findings, with nothing
to keep in sync. So:

- `triage`'s only write to this item is the state move that closes it.
- The finding → fix link is written **downward**, on the filed `[TASK]`, as a `Findings:
  #<findings-id> (finding <n>)` line in its body. The bare id is deliberate there — it is the second
  place the chip and the `Related` link are both wanted. A finding that became a comment rather than
  a work item writes no link at all, in either direction: the comment names no ids by design.
- A closed item a human chooses to reopen does not become a queue again: the next pass writes a new
  item.
