---
name: manual-qa
description: Drive a `[SPEC]`'s QA comment step by step on Azure DevOps — narrate each step, wait for an explicit outcome, tick the box on a pass, and on a failure append a self-contained finding to the run's `[FINDINGS]` work item. Invoke /ado-workflow:manual-qa with a `[SPEC]` id or URL to run or resume a manual QA pass.
disable-model-invocation: true
---

# manual-qa

Drive the **QA comment** a `work-on-spec` run posted on a `[SPEC]` — one step at a time, gated on
the human's word — and capture what fails in that run's `[FINDINGS]` work item. This is the
**capture phase** of the Azure DevOps QA loop. Triage (confirm, root-cause, promote to `[BUG]`s)
happens **later, in a separate session**, via `ado-workflow:triage`.

The sibling of `prd-workflow:manual-qa`, and not a second call site of it. Same shape, different
tracker: a work-item comment instead of an issue comment, one `[FINDINGS]` item instead of a
`### [FINDING]` comment per failure, a tag instead of a label. Every literal below is this
tracker's; none of the GitHub mechanics carry across, and the `<!-- 75 80 -->` id trailer does not
exist here at all.

**Every skill in this plugin is namespaced**, on every route — installed from the marketplace or
loaded with `claude --plugin-dir`: `/ado-workflow:manual-qa`, `/ado-workflow:triage`, and so on.
There is no unprefixed form. Unprefixed names below are shorthand for whichever form your route
provides.

**What the MCP does here is narrow, and stating it is the point: it reads a comment, ticks a box,
appends a finding, and creates a work item. It never judges whether anything is correct.** Only the
human's observation in the running app decides an outcome.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` — read it; never hardcode one here. This skill reads four
things and nothing else:

| Adapter section | What for |
|---|---|
| `## Repo` → `### Azure DevOps` | organisation, **work-item project**, **work-item type**, board states, title prefixes |
| `## Verify ladder` | the **L5** rung, which defines what a step must name to be executable at all (see *A structurally unexecutable step is a finding*) |
| `## Sources of truth` | the **project explorer agent** for on-demand elaboration — `Explore` where it says None |
| `Tracker:` line | **abort** if it is anything other than `azure-devops` (an absent line means `github` — that project wants `prd-workflow:manual-qa`) |

`[SPEC]`, `[TASK]`, `[FINDINGS]` and `[BUG]` are **shorthand for the adapter's *Title prefixes*
row**, written out for readability. If that row names different prefixes, they win. On this tracker
the prefix is load-bearing rather than decorative — all four kinds are the same work-item type under
one parent — so a filter reading the wrong prefix returns an empty set, not an error.

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

**Tool names come from the running server.** This skill names the `mcp__ado__*` tools it calls, but
the server's tool set and parameter names vary by `@azure-devops/mcp` version. If a named tool or
field is not there, discover the equivalent from the server rather than skipping the step, and
announce the substitution. A step that cannot be performed at all is a stop, never a silent
omission.

## Three non-negotiables

1. **Capture, don't solve.** `<the-line>` says exactly where investigation stops. The driver adds
   gating, not licence to debug.
2. **Every finding is self-contained.** A cold `triage` session reads the `[FINDINGS]` item, not
   this conversation. Symptom, evidence, a `path:line` pointer, a labelled root-cause *hypothesis*,
   classification, repro — plus which step and which `[TASK]` it came from.
3. **A `[x]` is a receipt, and it means exactly one thing**: a human executed that step and
   observed it pass. Nothing else ever ticks it — not "probably fine", not silence, not a change of
   subject. Tick state is the only record the pass ever happened, so a false tick is a false
   receipt.

## Input: one `[SPEC]`

**One input, no branching, no selection logic.** The user passes a `[SPEC]` work-item id or URL —
strip query strings. If they pass nothing, ask; never guess one, and never go hunting for a spec.
Fetch it with `mcp__ado__wit_work_item` (`action: "get"`), `expand: "relations"` and **no** `fields`
filter (the two are mutually exclusive), and confirm the type and the `[SPEC]` title prefix before
anything else.

### Picking the comment

Load the `[SPEC]`'s comments with **one** call — `mcp__ado__wit_work_item`,
`action: "list_comments"`, against the adapter's **work-item project**.

A QA comment is identified by **two markers together**, never a fragile substring:

- the **run-context line** it opens with — ``Run of `[SPEC]` #<spec-id> — <n> `[TASK]`s landed
  <date> · PR …``
- the **`## Steps` heading**, present in every QA comment by construction (`## Before you start` is
  conditional, so it cannot be the marker)

Take the **newest** comment carrying both. Then **say which one you picked** — its run-context line,
how many steps it holds, and whether it already names a `[FINDINGS]` item — *before* doing anything
else. A driver that silently picks the wrong run walks a human through a slice they already tested.

Both markers are written by `work-on-spec`'s `## Loop end`, which is the normative writer of this
comment; its parse-contract table lists every literal this skill reads and writes. Change one there
and it changes here in the same commit.

### The QA comment is self-sufficient

Its run-context line carries **the pull request the run landed on** and, once there has been a
failure, **the `[FINDINGS]` item**. That is the whole of the run context, and **nothing else is
fetched**: no pull-request body, no diff, no `[TASK]` bodies, no search.

**Total I/O for a pass:**

| Occasion | Calls |
|---|---|
| Load | 1 × `wit_work_item` (`get`) + 1 × `wit_work_item` (`list_comments`) |
| Per step confirmed | 1 × `list_comments` + 1 × `wit_work_item_comment_write` (`update`) |
| First failure only | 1 × `wit_work_item_write` (`add_child`) + 1 × parent re-fetch to verify + 1 × comment read-modify-write for the reference |
| Per finding | 1 × `wit_work_item` (`get`) + 1 × `wit_work_item_write` (`update_batch`) + 1 × comment read-modify-write for the suffix |

No subagent by default. No polling, ever.

### No upfront exploration

Do **not** read the diff, the `[TASK]`s, or the code before starting. Elaboration is **on demand
only** — when the human asks what a step means — and it is delegated, never done on this thread:

- Spawn **one throwaway subagent** per question: the **Agent** tool with the explorer agent from the
  adapter's `## Sources of truth` (`Explore` where it says None), Haiku-class, thoroughness
  "medium". Speak in tiers per [`../_shared/model-effort-heuristics.md`](../_shared/model-effort-heuristics.md).
- Ask for a **condensed report**: paths, symbols, the one thing that answers the question. Do not
  read, grep or glob yourself — the point is to keep the QA thread clean.
- **It must name its source.** Relay the answer in that form — *"the comment doesn't say; from the
  diff on this branch: …"* — so the human always knows whether they are hearing the QA comment or an
  inference from code.

Three hard limits on elaboration: it **never rewrites a step**, it is **never written back into the
comment**, and it is **never the basis for judging pass/fail**.

### Session hygiene: check and report, never act

Before step 0, confirm and say what you found:

- the branch the run landed on is the one checked out (`git branch --show-current`) — the adapter's
  **branch pattern** plus the `[SPEC]` id says what it should be;
- the pull request named in the run-context line is open and still a draft.

If either is wrong, or anything else is unexpected — dirty tree, detached HEAD, a completed pull
request — **say so and stop for the human**. Never `git checkout`, never `git stash`, never start
the app. The tester owns their machine; this skill owns the bookkeeping.

## `## Before you start` folds into step 0, and ticks nothing

If the chosen comment has a `## Before you start` section, read it verbatim as the lead-in of the
**same message** that presents step 0 — there is no separate acknowledgement turn to wait on. The
human's step-0 outcome is what confirms it landed. It has no checkbox and it ticks nothing.

Skipping it produces a **false finding on step 1**, because that section is the "this will look
broken and is not" warning: the migration the tester has to run first, the flag that is off, the
`[TASK]` deliberately left for a human. A tester who never heard it logs the known gap as a defect
and burns a triage round-trip on it.

No such section → say so in one clause and go straight to step 0.

## Driving the pass

Steps are read **verbatim**, never paraphrased — the wording in the comment is the wording that was
verified against what shipped. Narrate the position on every turn: **"step 3 of 9"**. The work-item
form renders no progress counter for a comment's task list, so the driver is the only one there is.

Two terminal states per step, and no others:

| Outcome | Effect |
|---|---|
| **Pass** | `[ ]` → `[x]`, advance |
| **Fail** | append a finding to the run's `[FINDINGS]` item, append the failure suffix, leave the box `[ ]`, advance |

- **Never advance without an explicit signal.** Not from silence, not from a change of subject, not
  from "ok". If the next thing the human says is not an outcome for the current step, answer it and
  re-present the step.
- **Natural language, not keywords.** Read intent — "yeah that showed up fine", "nope, nothing
  rendered", "it did the thing" are all outcomes. There is no vocabulary to memorise.
- **But never tick on ambiguity.** "I think so", "looks about right", "close enough" are not
  outcomes. Ask **one** clarifying question naming the expected result the step states, and wait.
  Asking costs a turn; a false tick costs the receipt.

### There is no "skip" state

A step the tester cannot get to right now stays a plain `[ ]` and **resume offers it again**.
Nothing is written. A third state would put something in the comment that means neither "passed" nor
"failed", and the resume rule below would stop working.

### A structurally unexecutable step is itself a finding

A step that **cannot name an entry point, a command and an expected result** — the adapter's L5 rung
— is not a step this project can test. That is not a skip and not a shrug: **log it as a finding**,
classification `bug (this repo)` against the run that wrote it, so it gets a paper trail and a trip
through triage instead of evaporating. Then advance like any other failure.

### "Blocked" is not a step state

It is the human stopping. **Record nothing.** The comment already holds the ticks, the suffixes and
— by subtraction — the position. Say where they got to, and stop.

### Resume needs nothing else

One `list_comments` call. **The first step that is `[ ]` *and* carries no failure suffix is where
you are.** No relation walk, no cross-referencing, no memory of the earlier session. A pass
abandoned halfway resumes cold. If the run-context line already names a `[FINDINGS]` item, that is
the run's item — reuse it; do not create a second one.

## The write path

Every write to the QA comment is a **strict single-line read-modify-write**. Six rules, all
load-bearing:

1. **Fresh read immediately before every write.** `wit_work_item` (`action: "list_comments"`), take
   the comment's current body, edit that. Never write from a body held in context since the pass
   began — a stale body written back silently reverts human edits, and violates `work-on-spec`'s
   never-edit contract by accident rather than intent, which is the worse kind.
2. **Substitute exactly one line, anchored on the step number.** Steps are numbered continuously
   from 0 across the whole run, so the anchor `- [ ] 3. ` — bracket, space, number, dot, space — is
   unique. Keep the trailing dot-space or `1.` also matches `10.`. **The step text and its
   backticked `[TASK]` id stay byte-identical**, as does every other line. **Never re-render the
   body from a model-held structure**; edit the one line in the body you just fetched.
3. **Write with `wit_work_item_comment_write` (`action: "update"`), passing
   `format: "Markdown"`.** Every time. A read never reports a stored format
   ([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) §8), so nothing
   downstream can discover it; `work-on-spec` set it at post time and every later write restates it.
   Drop the flag once and the comment lands as HTML, and the headings, checkboxes and code spans
   this contract is made of arrive as literal text.
4. **Already-ticked is success, not an error.** The anchor matches `- [x] 3. ` instead → the step is
   already recorded as passed. Proceed without rewriting and without complaining.
5. **Read the comment back and verify before advancing.** Confirm the anchored line reads the way
   you intended *and* that a step you did not touch is still intact. A write returning is not
   evidence it landed as meant.
6. **Never poll.** The driver advances on the user's word, full stop.

**The comment API strips raw markup, and that makes a careless write destructive.** Angle brackets
arrive as `&lt;` / `&gt;` by construction, because `work-on-spec` escapes them at synthesis time —
so they survive a round trip *only if you preserve the bytes you fetched*. Re-render or "clean up"
the body and every escaped token in every untouched step is stripped on the way back out, and the
UI renders the sanitised text (§8), so the damage reads as a sentence that was always worded that
way. Vanishing text, not visible junk. Substituting one line and touching nothing else is the whole
mitigation.

**The driver owns the boxes for the duration of a pass** — tell the tester this in as many words,
once, at the start. There is no optimistic concurrency on a work-item comment update, so a human
ticking in the browser mid-pass is a silent last-write-wins race. Fresh-read-per-write plus that one
sentence is the whole of it.

## The failure suffix

A failed step is annotated **in place**, step text untouched:

```
- [ ] 3. search for a landed change → expect it in results (`#12805`) — **failed**
```

- **A bare ` — **failed**` and nothing more.** No link, no finding number, no note. Every failure in
  a run points at the same `[FINDINGS]` item, and the run-context line names it once — a per-step
  pointer would repeat the same id on every failed line for nothing.
- **Pure append**, after the backticked id. The driver never parses a line apart and reassembles it
  — that is the operation class that reformats things by accident.
- **Not strikethrough.** Struck-through text reads as *cancelled / no longer applies*, which is the
  opposite of what happened; it mutates the step text; and it has no clean undo.
- **Reversible, and that is what makes the receipt work.** If the step is later re-tested and
  passes, **one** write flips `[ ]` → `[x]` **and drops the suffix** — so the comment can genuinely
  reach all-ticked, and "every box ticked, no suffix left" keeps meaning "everything passed".
- **One write, not two.** Create or locate the `[FINDINGS]` item and append the finding **first**,
  then write the suffix in a single substitution.
- The box stays `[ ]`. `[x]` continues to mean exactly one thing (non-negotiable 3).

## The `[FINDINGS]` item

**Its whole shape — one per run, lazy creation, the Task-under-the-parent placement, the
`### [FINDING] ` marker, the append path, and how `triage` finds it again — is
[`findings-item.md`](../references/findings-item.md). Read it before the first failure.** What
follows is only this skill's half.

**Create it on the first failure of the pass, and not before.** A clean pass creates nothing.

Then, in this order, once per run:

1. Create the item (`wit_work_item_write`, `action: "add_child"`, `format: "Markdown"`), and verify
   the hierarchy link landed.
2. **Write the reference into the run-context line** — ``` · findings `#<id>` ``` appended to the
   end of that line, backticked, exactly once. This is the **third never-edit carve-out**
   `work-on-spec`'s `## Loop end` declares, and it is permitted precisely because the item does not
   exist when the comment is posted. Same write path as a tick: fresh read, one line substituted,
   `format: "Markdown"`, read back.
3. Append the finding to the item's description.
4. Write the step's failure suffix.

Every later failure in the same pass skips 1 and 2 — the item already exists and the line already
names it. **Never create a second item for one run**, and never write the reference twice.

**One finding per turn. Never batch.** Append it, report the finding's number and a one-line recap,
write the suffix, then move to the next step.

**A finding noticed outside any step** goes into the same item, by the same path, with the
`**Step:**` and `**From:**` lines **omitted entirely** — there is no step and no attribution to
lift. It ticks nothing, because no step is being recorded.

<the-line>
### Where investigation stops

> **Investigate only far enough to classify and route — never to solve.**
> *One decisive probe, not a full investigation.*

**In bounds (do at capture):**
- Confirm the symptom (the human saw it, or one quick check).
- **One decisive probe** *when it changes classification or routing* — e.g. a single `curl` against
  the API endpoint to prove a bug is server-side rather than client-side. That probe earns its place
  because it routes the finding to the right repo.
- Grab the **`path:line`** where the symptom surfaces.
- Check the `[SPEC]` / `CONTEXT.md` / code comments for **deferred-on-purpose**.
- One **root-cause hypothesis**, clearly labelled as hypothesis, kept separate from observed facts.

**Out of bounds (defer to `triage`):**
- Tracing the full call graph to pin the exact broken line.
- Reproducing many permutations beyond the one that decides routing or severity.
- Reading another repo's handler to find the precise fix.
- Writing or testing a fix.
- Spawning code-exploration subagents. If a finding needs a deep code dive just to be *understood*,
  that is the signal it belongs in `triage`. (The on-demand elaboration subagent is not an
  exception: it answers "what does this step mean", never "why did it break", and never decides an
  outcome.)
</the-line>

<routing>
### Routing (which repo/owner)

- **This-repo bug** → a real defect in the code under test. `triage` will file a `[BUG]` here.
- **Contract-boundary bug** → the symptom is in this app but the cause sits on the other side of the
  API boundary, in the repo named by the adapter's `## Repo` → *Related repos*. Prove it with the one
  decisive probe where feasible and say so explicitly — `triage` investigates over there and files
  in that repo, cross-linked back. Do **not** fix or file across the boundary from here.
- **Deferred-by-design** → not a bug. Say what was deferred, cite the code comment or `[SPEC]` note,
  and what the follow-up slice needs. (If it was in `## Before you start`, it should not have
  reached a finding at all.)
- **Works-as-intended / enhancement** → capture the desire, mark it as not-a-defect.

If the adapter says "None" for related repos, there is no contract boundary to route to —
everything is a this-repo finding.
</routing>

## End of pass, and the `needs-qa` tag

**Tick state is the whole record. Never post a second comment** — not a summary, not a "pass
complete", not a count. End-of-pass output goes to the **terminal only**: how many steps passed,
which failed and their finding numbers, and which are still outstanding.

**The skill *offers* to remove `needs-qa`; it never removes it unprompted.** Both conditions are
readable from the comment already in hand — no extra call:

| Condition | Read from |
|---|---|
| every step is `[x]` | the body |
| no failure suffix anywhere | the body |

- **Both hold** → offer, and on a yes, remove the tag.
- **Either fails** → do **not** offer at all. Report what is outstanding and leave the tag alone.

**There are two conditions here, not three.** The GitHub sibling has a third — an
`Earlier QA pass still outstanding:` first line. **That line does not exist on this tracker**, it
was deliberately not ported, and it is not among the literals `work-on-spec`'s loop end writes. Do
not read for it and do not reintroduce it.

Removing the tag is a **read-modify-write on `System.Tags`**, which is a single semicolon-separated
string: read the `[SPEC]`'s current tags, drop `needs-qa`, write the whole remaining list back.
Writing a tag value on its own replaces every tag the item had, so a careless write here silently
deletes tags nobody was thinking about.

```
wit_work_item_write  { action: "update", project: <work-item project>,
                        updates: [{ id: <spec-id>, op: "add",
                                    path: "/fields/System.Tags",
                                    value: "<the remaining tags>" }] }
```

Then **read `System.Tags` back and confirm** before reporting it removed.

**The driver drives exactly one QA comment and never touches another.** No chain-walking, no
aggregate state across passes. A second run against the same `[SPEC]` has its own comment, its own
findings item, and its own pass.

**Never**: complete the pull request, close the `[SPEC]`, edit a step's text, add or delete a step,
delete a comment, or write any field of the parent work item. The three carve-outs in
`work-on-spec`'s `## Loop end` — checkbox state, the failure suffix, the `[FINDINGS]` reference —
are the complete list of what this skill may write into that comment.

## The terseness floor

**This driver does not license further compression of the QA comment.** Every step must stay
executable by a human with no skill available:

- the comment outlives any version of this skill;
- anyone installing `ado-workflow` may never invoke the driver;
- and the driver reads steps **verbatim**, so a step too terse for a human to act on is exactly as
  useless read aloud.

The driver adds **gating and bookkeeping, not comprehension**. If a step only works because a model
is there to interpret it, the step is wrong — that is a finding, not a feature.

## Handoff to triage

The `[FINDINGS]` item is this skill's only output to the tracker besides the ticks and suffixes on
the comment. A later `/ado-workflow:triage` session reads that item, confirms each finding,
root-causes it, and promotes the survivors into `[BUG]` work items. **This skill never fixes
anything and never files a `[BUG]`.**
