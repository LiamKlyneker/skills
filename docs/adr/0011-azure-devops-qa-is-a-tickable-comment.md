# ADR 0011 — Azure DevOps QA is a tickable comment, and 0008's three platform claims were false

- **Status**: Accepted
- **Date**: 2026-08-02
- **Context**: PRD #87, implemented by #95–#99
- **Supersedes**: ADR 0008

## Read this first: 0008's plugin-membership half stands, and this record depends on it

ADR [0008](0008-prd-qa-skills-belong-to-prd-workflow.md) decided **two** things — where the
PRD-QA skills live, and that Azure DevOps had nothing to copy. The convention supersedes a record
whole, so the `Superseded by ADR 0011` line now sitting on 0008 would otherwise read as
re-opening the first. It does not.

**`manual-qa` and `triage` still belong to `prd-workflow`, not to `lk`**, for exactly 0008's
reason: writer and readers of a parse contract must ship in one version-bumped plugin, or a
consumer updates one and not the other and gets a pass reading a template nobody promised it.
`lk` stays at its stated criterion with no carve-out. Nothing moves plugins here.

That half is not merely intact — it is **the rule this record applies**. The two new Azure DevOps
skills go into `ado-workflow` because `work-on-spec` writes the literals they read.

What is superseded is the second half: 0008's conclusion that there was nothing for
`ado-workflow` to copy, *"now or later"*.

## The claim, and the three facts under it

0008 wrote, in its own words:

> - `plugins/ado-workflow/skills/references/qa-item.md` is prose sections with **no checkboxes**.
>   There is no tick-able state to drive, and it says outright that no skill parses it.
> - ADO access is **MCP-only**, by deliberate decision
>   (`plugins/ado-workflow/skills/references/ado-mcp-setup.md`).
> - `wit_work_item_write` (`action: "update"`) has **no `format` option and falls back to HTML**,
>   so editing a description is a destructive rewrite of the whole field rather than the
>   single-line append `manual-qa` depends on.
>
> No tick-able state, no safe append, nothing to parse — so there is nothing for `ado-workflow` to
> copy, now or later.

Every mechanical fact below was **measured on 2026-08-02 against a throwaway fixture** in a live
Azure DevOps organisation — Online Sales, Sprint 2026_11, items `12804`–`12809`, tagged
`zz-fixture-delete-me`. Not read from documentation: the docs were wrong twice during that grill,
and the API's `200` was wrong once.

### "No tick-able state" — false, and false on the day it was written

Azure DevOps renders a Markdown task-list item as a **real checkbox**, in a work-item comment and
in a description alike. The tester clicks it in the UI and the state persists, exactly as on
GitHub. Nothing about the platform changed between 0008 (2026-08-01) and the grill the following
day; this capability predates the record that denied it.

Where the claim came from is the part worth keeping. 0008 was reading
`references/qa-item.md` and observing, correctly, that **that document** had no checkboxes. That
is a property of an artifact this repo authored. It was written up as a property of the tracker.

### "Nothing to parse" — false, by the same category error

The evidence offered was that the document *"says outright that no skill parses it."* True — and
we wrote that sentence. A document nothing parses is a document we chose not to parse.

#97 replaced it. The QA comment `work-on-spec` now posts carries **five load-bearing literals**:
the run-context line paired with the `## Steps` heading (identification), the step anchor
`- [ ] <n>. `, checkbox state, the backticked owning-`[TASK]` id, and the terminal failure suffix
` — **failed**`. `ado-workflow:manual-qa` reads all five. `references/qa-item.md` is deleted.

### "No safe append" — the sub-claim is true; the conclusion is false

The one genuine platform fact 0008 named **survives, unamended**: `wit_work_item_write`
(`action: "update"`) has no `format` option and falls back to HTML. It is now written into two
skills as a hazard rather than a limit. Three measured facts turn it from a wall into a rule:

- **`action: "update_batch"` does accept a per-item `format`**, so a long-text field round-trips
  as Markdown. `_shared/ado-workitem-authoring.md` stated the limitation as general; #96
  corrected it.
- **The QA artifact is a comment, not a description.** `wit_work_item_comment_write`
  (`action: "update"`) takes `format: "Markdown"` directly, so the whole description path 0008
  reasoned about is not the path a tick goes down.
- **There is no append operation on a long-text field on any surface**, so every write is a
  genuine read-modify-write. Safety is not a feature the API offers; it is the discipline of
  substituting exactly one anchored line into the body you just fetched and never re-rendering
  from a model-held structure.

The grill also found a **sharper** hazard than the one 0008 named, and missing it was the real
cost of stopping at the docs: a comment's read path **strips** raw markup, the sanitiser does not
respect code spans, and the ADO UI renders a comment from its sanitised text rather than
`renderedText` — so `<div className="x">` comes back as `<div>` and the damage reads as a
sentence that was always worded that way. Angle brackets are escaped at synthesis time for
exactly this reason, and a careless re-render destroys every untouched step on the first tick.

**The correction is not that Azure DevOps turned out generous.** All three claims were about our
own artifact, dressed as claims about the tracker. Two of the three could have been falsified by
reading a file in this repo.

## What 0008 got right, and is reused

**"A different skill answering to a different artifact, not a port."** Correct, and it held all
the way through the implementation. `ado-workflow:manual-qa` and `ado-workflow:triage` are
**siblings** of the GitHub pair, not second call sites — ADR
[0004](0004-shared-reference-and-skill-dependencies.md)'s rule that `_shared/` files are shared
and skills are not. None of the GitHub mechanics carry across: the `<!-- 75 80 -->` id trailer
does not survive at all, because an HTML comment is stripped out of a comment's API read
entirely, so ids ride **in the open, backticked**; failures accumulate in **one `[FINDINGS]` work
item per run** instead of a `### [FINDING]` comment per failure; and `needs-qa` is a **tag**,
created implicitly on first use, so this tracker gains no one-time human precondition where
GitHub needs a label created in advance.

**And it came out simpler than the original.** A fresh findings item per run means everything in
it is new by construction, so "already handled" is answered by the item being **closed** — one
field, read in the same fetch that loads the findings. GitHub's entire `**Triaged:** #N`
back-annotation channel is **absent here and must not be reintroduced**.

**ADR [0009](0009-the-qa-comment-is-a-parse-contract.md) ports whole.** The comment is a parse
contract on this tracker too; the never-edit rule has carve-outs that record a pass rather than
authoring it — three here rather than two, the third being the once-written `[FINDINGS]`
reference on the run-context line; and the receipt is *all boxes ticked, no failure suffix, tag
removed*. So does 0009's deliberate inversion: **`### [FINDING] ` is hardcoded in both ADO skills
and deliberately absent from the adapter**, because a project free to edit it would get a
`triage` that matches nothing and reports a clean pass.

**ADR [0003](0003-invocation-policy.md) is untouched.** Both new skills carry
`disable-model-invocation: true`. Invocation is still the isolation boundary.

## Consequences

- **The `[QA]` work item type is retired on Azure DevOps**, and with it the never-link rule that
  kept it off the pull request. Tick state is the receipt now, comments survive closure untouched,
  and the queue is a WIQL query on `[System.Tags] CONTAINS 'needs-qa'` — which returns the
  `[SPEC]` **regardless of state**. So `System.State` answers *is the code done* and the tag
  answers *has a human tested it*, and neither field has to lie.
- **The prefix registry grows to `[SPEC]` · `[TASK]` · `[FINDINGS]` · `[BUG]`**, and title
  prefixes are now **load-bearing on this tracker and decorative on GitHub**. That divergence is
  forced by the board, not chosen: Task → Task parenting is API-legal and product-hostile
  (the fixture returned `200` while the taskboard raised *"same category hierarchy … work item(s)
  12805 are not shown"*, removing the parent from the taskboard and disabling reordering
  board-wide), and Bug-type items are requirement-level here (`bugsBehavior: 1`), so a Bug
  parented to a User Story renders as a sibling swimlane. Everything the loop creates is
  therefore a **Task under the same parent User Story**, and the prefix is the only thing telling
  the kinds apart.
- **A `[BUG]` is filed, not scheduled — and the PRD had this backwards.** #87 assumed the prefix
  did not filter and that a `[BUG]` would be picked up like any other unstarted Task child.
  `_shared/ado-eligibility.md` §3 keeps a sibling only when its title starts with `[TASK]`, so
  the filter drops `[BUG]`s **on purpose**. `next-task-to-implement` needs no change — not
  because the prefix is inert, but because its filter already excludes them. Promotion is a
  **one-field retitle** `[BUG]` → `[TASK]`, the ADO analogue of GitHub's `deferred` →
  `ready-to-start` relabel.
- **Skill names collide across plugins deliberately.** `manual-qa` and `triage` exist on both
  sides, because they name an *activity* rather than an artifact — unlike `to-prd`/`to-spec` and
  `work-on-prd`/`work-on-spec`, where the noun differs. `validate_skills.py`'s name-uniqueness
  check relaxed from global to **per-plugin** (#95); the rule was verified to be this repo's
  alone, with `claude plugin validate --strict` passing on plugin and marketplace manifest
  against a deliberate duplicate. Its stated justification — *"the same skill discoverable under
  two routes"* — described the deleted top-level symlink shims, which its own symlink check
  already catches.
- **A new `ado-qa` bundle**, mirroring `prd-qa`. `ado-workflow` the plugin now answers to **two**
  bundles, exactly as `prd-workflow` does — the two ADO QA skills read `## Sources of truth`,
  which no `ado-workflow` *loop* skill does, so folding them in would interview every loop
  adopter about explorer agents nothing they installed reads.
- **`install-skills` was never optional among the version bumps**, whatever else moved:
  `install/bundles.md` is dereferenced into its cache copy, so a new bundle changes what that
  plugin ships. This branch in fact moved **all five**, the corrections to `_shared/` counting as
  a change to every plugin that symlinks it — ADR
  [0001](0001-version-the-plugins-and-enforce-the-bump.md)'s rule doing exactly its job.
