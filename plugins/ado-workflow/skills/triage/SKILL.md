---
name: triage
description: Spec-scoped triage on Azure DevOps — take the findings `ado-workflow:manual-qa` logged in a run's `[FINDINGS]` work item, confirm each against the `[SPEC]`, its `[TASK]`s and the code, pinpoint root cause via a cheap subagent, then file cold-runnable `[BUG]` work items under the same parent and close the findings item. Invoke /ado-workflow:triage with a `[SPEC]` id to promote a run's QA findings into executable work items.
disable-model-invocation: true
---

# triage

The **investigate + promote** half of the Azure DevOps QA loop. `manual-qa` — the capture phase —
composes a run's pass from what landed on the branch, drives it flow by flow, and appends each
failure to that run's `[FINDINGS]` work item; `triage`
*confirms, roots-causes, and promotes* the survivors into **cold-runnable `[BUG]` work items** — one
per finding — then **closes the findings item**.

The sibling of `prd-workflow:triage`, and not a second call site of it. Same cadence and the same
two non-negotiables; different tracker, and one structural difference that changes the shape of the
whole skill: **there is one findings item per run, not one comment per failure.** So there is no
per-finding comment to skip, no marker to write back, and no `**Triaged:** #N` line anywhere.

Its edge over a generic triage is **decision context**: it loads the `[SPEC]`, its `[TASK]`s, the
touched `CONTEXT.md` and the locked decisions — so it can tell a real defect from a gap that was
**deferred on purpose**, and route a finding to the repo that actually owns it.

**Every skill in this plugin is namespaced**, on every route — installed from the marketplace or
loaded with `claude --plugin-dir`: `/ado-workflow:triage`, `/ado-workflow:manual-qa`, and so on.
There is no unprefixed form.

**What the MCP does here is narrow, and stating it is the point: it reads a work item, creates a
work item, and closes one. It never judges whether a finding is correct.** The
verdict on every finding is this session's, confirmed against the code and agreed with the human —
never inferred from the fact that a call succeeded.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` — read it; hardcode none of it here. From `## Repo` →
`### Azure DevOps`: the organisation, the **work-item project**, the **work-item type**, the board
states and the title prefixes; plus `## Repo` → *Related repos* for the contract boundary,
`## Commands` and `## Verify ladder` for what a filed `[BUG]` must tell a worker, and
`## Sources of truth` for the explorer agents.

**Abort** if the adapter is missing, or if its `Tracker:` line is anything other than
`azure-devops` (an absent line means `github` — that project wants `prd-workflow:triage`).

`[SPEC]`, `[TASK]`, `[FINDINGS]` and `[BUG]` are **shorthand for the adapter's *Title prefixes*
row**. If that row names different prefixes, they win — here, and in every title filter this skill
applies. On this tracker the prefix is load-bearing rather than decorative; `## A [BUG] is filed,
not scheduled` below is where that matters most.

## Readiness: the ADO MCP server

Requires the Azure DevOps MCP server (`mcp__ado__*` tools).

**Before starting:**

1. Check memory — the server may already be recorded as configured for this project.
2. If not in memory, probe: call `mcp__ado__core_list_projects` with `top: 1`.
   - Responds → proceed; save to memory: `ADO MCP active for this project`.
   - Fails → set it up. See [`ado-mcp-setup.md`](../references/ado-mcp-setup.md). **Read it before
     concluding the server is missing** — a probe failure has two causes, and the likelier one is a
     server running correctly under the wrong key, which this probe cannot distinguish from no
     server at all.

**Tool names come from the running server.** The `mcp__ado__*` tools and parameter names vary by
`@azure-devops/mcp` version. If a named tool or field is not there, discover the equivalent rather
than skipping the step, and announce the substitution. A step that cannot be performed at all is a
stop, never a silent omission.

## Two non-negotiables

1. **Every `[BUG]` is a cold-runnable fix plan.** A future `work-on-spec` run or a fresh session
   (no memory of this chat) must fix it with **no plan mode and no re-investigation**. So each one
   carries root cause (confirmed, not hypothesized), exact files plus prior art, the fix approach,
   and testable acceptance criteria — mirroring `to-spec-tasks`'s `[TASK]` body so a `spec-worker`
   consumes a bug identically to a planned slice.
2. **Never fix.** `triage` stops at filed work items. No code changes, no fix-tests. The fix belongs
   to a later run. (Mirror of `manual-qa`'s `<the-line>`, one phase later.)

## Context loading (once, up front)

Establish scope before the first finding, and hold it for the whole session. Every read passes
`expand: "relations"` and **no** `fields` filter — the two are mutually exclusive, and a filter
silently suppresses the relations this walk depends on
([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) §4).

- **The `[SPEC]`.** Its id or URL is the argument; ask if not given, never guess. Its description
  carries the cross-repo dependencies, the deferred / out-of-scope notes and the locked decisions.
- **Its `[TASK]`s**, per [`../_shared/ado-eligibility.md`](../_shared/ado-eligibility.md) — spec →
  parent → siblings, filtered to this spec's `[TASK]`s. This is the *owning-slice* attribution map,
  and it is nearly free because the parent fetch is the same one that finds everything else.
- **The parent work item**, read only — it is where a new `[BUG]` will be parented.
- **Touched `CONTEXT.md`** for the area under test (use the `scoped-context` skill if available),
  plus code comments in those files marked "deferred", "later slice", "no resolver yet",
  placeholder. Together with the `[SPEC]`'s description and its `[TASK]`s, this is what powers the
  gap classification below.

  **There is no QA comment to read.** `work-on-spec` posts none, and `manual-qa`'s end-of-pass
  **receipt** on the `[SPEC]` is free-form output that nothing parses — read it as context if it is
  there, for which flows ran and where a pass stopped, never as a source of findings. The findings
  are in the `[FINDINGS]` item. The `needs-qa` tag is worth noting — it means no pass has completed
  yet — but it changes no classification.

## Input: the run's `[FINDINGS]` item

**How this item is located is decided in [`findings-item.md`](../references/findings-item.md), and
that is the only place it is decided.** Read it first. The short form:

**Scan the parent's children for the `[FINDINGS]` title prefix.** That is the lookup, and it is the
only one — the run-context clause on a QA comment is gone with the comment itself. The prefix is
**load-bearing on this tracker by design** (the adapter's *Title prefixes* row): every kind of child
under this parent is the same work-item type, so the prefix is the only thing separating a findings
item from a `[TASK]` or a `[BUG]`. You already fetched the parent with `expand: "relations"` during
context loading, so the scan costs no extra call.

Three consequences worth having in hand:

- **The scan cannot say *which run* on its own** — the prefix says what kind of item something is,
  and one parent carries every `[SPEC]`'s findings items and every run's. Narrow with what the item
  itself carries: the spec title and run date in its own title, and the `Spec: #<spec-id>` line at
  the top of its description. Then **say which item you picked and which run it covers** before
  touching anything. More than one candidate survives the narrowing → name them all and ask; never
  assume the newest.
- **No `[FINDINGS]` item for this `[SPEC]` means no pass recorded a failure** — a clean pass creates
  none, which is the common case. Report "nothing to triage for that run" and stop rather than
  widening the search. Unlike the run-context clause this replaces, that is an inference from an
  absence rather than a stated fact, so say which parent you scanned and what you matched on, and
  let the human correct you.
- **A pasted `[FINDINGS]` id skips the lookup entirely.** A human who hands you an id has answered
  the question, and it is the shortcut worth offering when the scan is ambiguous. That is an input
  shortcut, not a second discovery route.

Then fetch the item and read `System.Description`. **Findings are the `### [FINDING] ` sections of
that field**, numbered from 1 in the order they were appended. That marker is a **parse contract**,
hardcoded in `manual-qa` and here, and deliberately absent from the adapter — a project free to edit
it would get a `triage` that reads the item, matches nothing, and reports a clean pass.

### An already-closed findings item is skipped outright

**Before the cadence, before any subagent, before any search: if the item is in a terminal state, a
previous session already triaged it.** Say so in one line, name the item, and stop.

This is the whole of the "don't re-promote" machinery, and it is one field read in the fetch you
already did. **There is no per-finding marker and none is to be added.** The GitHub sibling writes
`**Triaged:** #N` back onto each finding comment because those comments live on a pull request
forever; here a fresh item is created per run, so everything inside one is new by construction, and
"already handled" is "that item is closed". Reintroducing a back-annotation would add a channel that
can disagree with the state field, in exchange for nothing.

If a human has reopened a closed item deliberately, treat it as live and say that you noticed.

### Two fields `manual-qa` hands over

A finding carries two fields worth **consuming rather than re-deriving**:

| Field | Example | Use it for |
|---|---|---|
| `**From:**` | ``**From:** `#12805` `` | the **owning `[TASK]`**, lifted by `manual-qa` from the `AB#<id>` references in the commits the failing flow exercises — no derivation needed |
| `**Step:**` | `**Step:** flow 3 ("search and filter"), sub-step 2` | which flow of that pass, and which sub-step of it, failed. No permalink — the pass is composed in `manual-qa`'s session and posted nowhere, so there is nothing to link to |

**Both are absent on a finding captured outside any flow**, which has no flow and no attribution.
That is normal for an ad-hoc finding, not a defect in it: fall back to the `[TASK]` map from context
loading for the owning slice, and say you derived it rather than reading it.

Run provenance needs no field at all — the item **is** the run.

## Cadence (one finding per turn)

For each finding: **capture → validate (gap classification) → investigate (subagent) → dispose →
show card → user confirm/correct → next.** Loop until the user says done, then **board → publish →
close the item**. Never batch.

## Per-finding process

### 1. Capture

Record the finding, its number in the item, its `path:line` and its two handover fields.
**`manual-qa` already did the classification, hypothesis and evidence — inherit them as the warm
start; do not re-derive.**

### 2. Validate + gap classification (HARD GATE — before filing anything)

`manual-qa` labels root cause as *hypothesis*. This skill's first job is to decide what the finding
**is**, using the loaded decision context. Resolve from the `[SPEC]` / `[TASK]`s / `CONTEXT.md` /
code before asking the user:

| Verdict | Evidence | Action |
|---|---|---|
| **Real defect** | behavior deviates from intent, still reproduces on the branch | → bug track (investigate + file) |
| **Already planned** | an open `[TASK]` or a future-slice note already covers it | link it, **do not** dup |
| **Intentionally deferred / out-of-scope** | a `[SPEC]` decision or code comment says so | cite it — **not a bug** |
| **Genuine unplanned gap** | nothing in the `[SPEC]` / `[TASK]`s / decisions covers it | **propose a follow-up and ASK the user** before creating |

- **Bugs** go to the board and are confirmed at publish time.
- **Follow-ups / enhancements / deferred gaps always ask first** — never auto-file a new feature
  slice. State the scope and let the user say create / link-existing / leave-noted.

### 3. Investigate — one subagent per finding

Spawn **one read-only subagent per finding** (the token-saver: this session orchestrates and decides
only, never greps or blames itself). Use the project explorer agent named in the adapter's
`## Sources of truth`, or `Explore` where it says None.

- **Model:** **Sonnet-class** by default (it authors a fix plan). Drop to **Haiku-class** for a
  trivial or mechanical finding; **never Opus**. Speak in tiers per
  [`../_shared/model-effort-heuristics.md`](../_shared/model-effort-heuristics.md); for exact ids
  defer to `claude-api`.
- **The subagent gets no ADO tools.** Everything it needs from the tracker — the finding text, the
  owning `[TASK]`'s scope, the `[SPEC]`'s relevant decisions — goes in its prompt, resolved by this
  session. It reads code and returns a plan.
- **Warm start:** hand it `manual-qa`'s hypothesis and `path:line`. Its job is **confirm + plan**,
  not discover-from-scratch.
- **Job:**
  1. **Confirm the root cause** on the current branch — trace the call path; for a contract-boundary
     finding, re-run the decisive probe against the live endpoint.
  2. **Attribute to the owning `[TASK]`** — always. **Where the finding carries `**From:**`, that
     *is* the attribution**: it was lifted from the step's own id by the loop that wrote the step, so
     take it as given and say you took it from the field. Derive from the `[TASK]` map only when the
     field is absent, and say that too — the two are not equally authoritative, and a silent
     re-derivation can disagree with the step without anyone noticing.
  3. **Introducing commit `@<sha>` — only when it earns its place:** run `git blame` / `git bisect`
     **only for a regression** (worked before, broke) or when the diff reveals deliberate intent. For
     a never-worked or net-new-feature bug, **skip the archaeology** — the `path:line` plus the
     owning `[TASK]` already localize it.
  4. **Author the fix plan** — exact files, prior art to copy, the change, and testable acceptance
     criteria. This is what makes the `[BUG]` cold-runnable.
- **Return contract:** confirmed root cause · owning `[TASK]` · `@sha` (only if a regression) · fix
  plan · files/prior-art · acceptance criteria · which repo owns the fix.

<cross-repo>
### Contract-boundary findings — investigate and file in the related repo

The adapter names both halves: `## Repo` → *Related repos* says which repo owns the other side of the
API boundary, and `## Sources of truth` → *Contract-boundary explorer agent* names the read-only
agent that owns it. For a finding whose root cause is across that boundary:

- **Spawn that explorer agent** instead of the project one. It reads the actual handler code to
  confirm the cause, plus that repo's scoped `CONTEXT.md` and its own conventions.
- It files the issue **in the related repo**, native to **their** house style, with a
  **"Discovered via `<this org>/<spec-id>`"** back-link.
- **This side:** carry a pointer `[BUG]` naming the external dependency under its `## Blocked by`,
  so the chain is visible from the board. Nothing on this tracker closes an item in another repo;
  the pointer is closed by hand when the other fix ships.
- If the adapter says "None" for either field, there is no boundary to route across: file here and
  say plainly that the boundary is unmodelled, rather than guessing a repo.
</cross-repo>

### 4. Dispose + dedupe

- **Dedupe against the tracker** — `mcp__ado__search_workitem` (or a WIQL query via
  `mcp__ado__wit_query`) on the symptom's keywords, in the **work-item project**, before filing. A
  match makes this a `reject (duplicate)` pointing at it. This catches a finding that duplicates
  something filed by *another* route — a planned `[TASK]`, a hand-filed bug, a finding from a
  different `[SPEC]`. It is **not** what catches a re-triage; the closed-item skip in `## Input`
  does that, with no call at all.
- **Route** per the table below.
- **Know which id each disposition will carry**, because the `[BUG]` body names the finding it came
  from and the report groups by disposition.

<dispositions>
| Kind | Title | Where | State | Picked up by a later run? |
|---|---|---|---|---|
| **Merge-blocker** | `[BUG] …` | this org, **child of the same parent** as the `[SPEC]` | the adapter's **pickable** state | **no — not automatically.** See *A `[BUG]` is filed, not scheduled* |
| **Deferred / follow-up** *(after user OK)* | `[BUG] …` | same | the adapter's **pickable** state | no |
| **Contract boundary** | their style | **related repo**, "Discovered via …" | their style; local pointer `[BUG]` here | no — closed by hand |
| **Reject** (WAD / dup / invalid) | `[BUG] …` | this org, same parent | **file-then-close**, with a one-line rationale citing the decision | — |
</dispositions>

A reject is **filed and then closed**, not skipped. The rejection reasoning is the thing that stops
the same false finding being re-investigated next quarter, and a work item is where a human will look
for it.

### 5. Show the card, confirm, next

```
QA-<n>  [<classification> · <severity> · <disposition>]
Finding: <one-line symptom>          (finding <n> of #<findings-id>)
Owning [TASK]: #<id> (<what that slice built>)
Root cause: CONFIRMED — <cause>; <path>:<lines>
Commit: <sha — only if a regression; else "n/a (introduced by the feature slice)">
Disposition: <where it lands, under which parent, with which prefix>
```

Print the card plus the recommended disposition, get confirm/correct, ask for the next finding.

## Board + publish

When the user says done:

1. **Board** — every finding with verdict / owning `[TASK]` / disposition / target. Get approval
   before publishing.
2. **Publish.** For each `[BUG]` in this org, **one at a time**:

   - `mcp__ado__wit_work_item_write`, **`action: "add_child"`**, against the adapter's **work-item
     project**, with the **parent work item the `[SPEC]` hangs off** as the parent — so the `[BUG]`
     is a **sibling of the `[SPEC]`**, never a child of it. That one call sets `System.Parent` and
     writes the hierarchy relation (§0, §3), so no follow-up link write is needed.
   - `workItemType`: the adapter's **work-item type** — the same one `[SPEC]`s and `[TASK]`s use. Not
     a Bug-type item: under `bugsBehavior: 1` that is requirement-level and renders as its own
     sibling swimlane instead of a child.
   - `title`: the `[BUG]` prefix followed by the one-line symptom.
   - `description`: the body below, with **`format: "Markdown"`** and angle brackets escaped at
     synthesis time (§1). If the running server's `add_child` will not take a `format` argument, fall
     back to `action: "create"` plus the `type: "parent"` link from §3 — never drop the flag.
   - **Verify the hierarchy** (§5): re-fetch the parent with `expand: "relations"` and confirm the
     new `[BUG]` appears as `Hierarchy-Forward`. A write returning is not evidence it is parented.
   - Assign it to the current user (§6).

   Then start the next one. Filing them one at a time, each verified, is what keeps a silently
   unparented bug from being invisible on the board.
3. **Close the `[FINDINGS]` item** — see below. This is the last write of the session.
4. **Report** created ids grouped by disposition, e.g.
   `filed: #12840 #12841 · deferred: #12842 · <related repo>: 1 · closed as duplicate: #12843`,
   plus the findings item and the state it now carries. Say explicitly which findings ended with
   **no** work item at all — intentionally deferred, cited from the `[SPEC]` or a code comment —
   because those leave no trace outside the closed item's description.
5. **Remind** the human of what this skill cannot do: complete the pull request, close the `[SPEC]`,
   remove the `needs-qa` tag, or schedule a `[BUG]` into a run (next section).

### Closing the `[FINDINGS]` item

**Closed, never deleted**, and the mechanics — a state-only `action: "update"` write, why the
terminal state name is not an adapter value, and why plain `update` is safe for this one call — are
in [`findings-item.md`](../references/findings-item.md). Announce which terminal state you used, and
**read the state back** before reporting it closed.

**This is `triage`'s only write to the findings item.** Nothing is appended to it, no finding is
annotated, and its description is left exactly as `manual-qa` wrote it.

## A `[BUG]` is filed, not scheduled

**A `[BUG]` is not picked up automatically by a later run, and that is the design.**

[`../_shared/ado-eligibility.md`](../_shared/ado-eligibility.md) keeps a sibling only when its title
starts with `[TASK]` **and** it carries the spec back-reference. A `[BUG]` fails the first test on
purpose, so `next-task-to-implement` will not recommend it and `work-on-spec` will not pick it. That
is what the adapter's *Title prefixes* row means when it says the prefix is **load-bearing** on this
tracker and decorative on GitHub — all four kinds are the same work-item type under one parent, so
the prefix is the only thing telling a `[BUG]` from a `[TASK]`.

**Do not "fix" this by titling a bug `[TASK]`.** That silently enrolls an untriaged, unscheduled fix
into whatever run comes next, which is the outcome the split exists to prevent.

**Promotion is a deliberate act, and it is a one-field retitle.** The body below already carries the
`Spec: #<spec-id>` line and the `Related` link back to the `[SPEC]`, so the prefix is the *only*
thing standing between a `[BUG]` and eligibility. When Product schedules it, retitling `[BUG]` →
`[TASK]` puts it in the set with no other edit. Until then it sits on the board as a triaged,
unscheduled finding.

This is the ADO analogue of the GitHub side's `deferred` → `ready-to-start` relabel: the same gate,
carried by the title instead of a label. **`next-task-to-implement` therefore needs no change** —
not because the prefix is inert, but because its filter already drops `[BUG]`s deliberately.

## The `[BUG]` body (mirror `to-spec-tasks`'s `[TASK]` so a worker eats it identically)

<bug-template>

Spec: #<spec-id>
Findings: #<findings-id> (finding <n>)

## External steps

None — fully implementable from the editor.

## What to fix

&lt;the fix plan — current vs expected, and the change to make&gt;

## Root cause

Confirmed: &lt;the actual cause, traced — not a hypothesis&gt;.
Owning `[TASK]`: `#<id>` (&lt;what that slice built&gt;).
Introduced by: `<sha>` — &lt;one line&gt;.   ← ONLY if a regression; omit otherwise.

## Worker context

- **Verify**: the exact commands from the adapter's `## Commands` table (L2 test command; L3
  boot/screenshot command when user-visible).
- **User-visible**: y/n.

## QA notes

&lt;how to verify the fix in the running app — concrete steps, each with an observable result&gt;.

## Acceptance criteria

- [ ] &lt;testable exit condition — the behavior, phrased as a check&gt;
- [ ] &lt;verify ladder rung green&gt;

## Blocked by

None — can start immediately.

</bug-template>

Rules governing that template, deliberately outside the fence:

- **Five things are byte-identical to `to-spec-tasks`'s `[TASK]` template and must stay that way**:
  the `Spec:` line, `## External steps`, `## Blocked by` (all three parsed verbatim by
  `../_shared/ado-eligibility.md`), and `## Worker context` / `## QA notes` (which `work-on-spec`
  briefs a `spec-worker` from). Reword one there and it changes here in the same commit. That is
  what makes a promoted `[BUG]` runnable without a second template.
- `## What to fix` and `## Root cause` replace the `[TASK]` template's `## What to build`. Nothing
  parses either; they exist because a bug has a cause and a slice does not.
- **The two "None…" sentinels are parsed verbatim** — `None — fully implementable from the editor.`
  and `None — can start immediately.` Do not reword them, and do not leave the section out.
- **Acceptance criteria live in the description**, as a section. The Task work-item type has no
  `AcceptanceCriteria` field (§9); criteria aimed at that field land nowhere and read back as a bug
  authored without any.
- **`Findings: #<findings-id>` is deliberately bare**, unlike every other id in this plugin. The
  chip and the `Related` link it creates are both wanted: that link is the only thing tying a
  `[BUG]` back to the finding it came from, since nothing is written back onto the findings item.
  The owning `[TASK]` id in `## Root cause` stays **backticked** — that relation is noise.
- **Severity is technical impact, independent of priority**; both live in the body, not in tags.

Title: **`[BUG] <one-line symptom>`**, taken from the adapter's *Title prefixes* row.

## Boundary / handoff

- `triage` = **investigate + decide + file**. It does **not** fix, does **not** complete the pull
  request, does **not** close the `[SPEC]`, and does **not** remove the `needs-qa` tag — that tag is
  removed by the human who ran the pass, via `manual-qa`'s offer, and it is the only record in the
  tracker that a pass happened.
- The one work item it closes is the `[FINDINGS]` item it just emptied.
- A filed `[BUG]` waits for a human to schedule it (*A `[BUG]` is filed, not scheduled*).
- Related-repo issues are executed by that repo's own workflow, and nothing here closes them.
