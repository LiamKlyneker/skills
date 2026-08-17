---
name: manual-qa
description: Compose a `[SPEC]` run's manual QA pass on Azure DevOps from what actually landed on the branch — the diff, the commits and the landed `[TASK]`s — as a short list of flows, then drive it one flow at a time, taking one verdict per flow and appending a self-contained finding to the run's `[FINDINGS]` work item on a failure. Invoke /ado-workflow:manual-qa with a `[SPEC]` id or URL to run a manual QA pass.
disable-model-invocation: true
---

# manual-qa

**Compose the pass, then drive it.** Given a `[SPEC]`, find that run's pull request, read what
actually landed on the branch, compose a short list of **flows**, and walk the human through them
one flow at a time — capturing what fails in that run's `[FINDINGS]` work item. This is the
**capture phase** of the Azure DevOps QA loop. Triage (confirm, root-cause, promote to `[BUG]`s)
happens **later, in a separate session**, via `ado-workflow:triage`.

**Nothing is read from a QA comment.** The pass is composed here, in this session, from the
as-built record — not from a script written before the code existed. That is the whole difference:
a planned step describes what a `[TASK]` was *supposed* to make testable; the diff describes what
there is to test.

The sibling of `prd-workflow:manual-qa`, and not a second call site of it. Same shape, different
tracker: a work item instead of an issue, one `[FINDINGS]` item instead of a `### [FINDING]`
comment per failure, a tag instead of a label, a local git read instead of `gh pr diff`. Every
literal below is this tracker's; none of the GitHub mechanics carry across.

**Ids ride in the open, backticked.** There is no hidden id trailer here and there must never be
one: in a work-item **comment** an HTML comment is stripped out of the API read entirely, so
`<!-- 75 80 -->` is simply not in the body anyone reads back, and the attribution it exists to
carry is gone with it. In a **description** it survives only entity-escaped, rendering visibly on
screen. Backticked in the open is the only form that works on both surfaces.

**Every skill in this plugin is namespaced**, on every route — installed from the marketplace or
loaded with `claude --plugin-dir`: `/ado-workflow:manual-qa`, `/ado-workflow:triage`, and so on.
There is no unprefixed form. Unprefixed names below are shorthand for whichever form your route
provides.

**What the MCP does here is narrow, and stating it is the point: it reads work items, appends a
finding, creates a work item, drops a tag and posts one receipt. It never judges whether anything
is correct.** Only the human's observation in the running app decides a verdict.

**No `--post` flag and no second-human path.** The loop is single-developer by design: the person
who ran it is the person testing it, in this session, on this machine.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` — read it; never hardcode one here. This skill reads five
things and nothing else:

| Adapter section | What for |
|---|---|
| `## Repo` → `### Azure DevOps` | organisation, **work-item project**, **repo project + repository**, work-item type, board states, **branch pattern**, default branch, title prefixes, related repos |
| `## Commands` | how to launch, build and check the thing — the sub-steps the driver can verify itself |
| `## Verify ladder` | **L5**, which defines what a sub-step must name to be executable at all, and **L2/L3**, which define what the driver can verify without the human |
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

1. **Capture, don't solve.** `<the-line>` says exactly where investigation stops. It has not moved:
   composing the pass added authorship, not licence to debug.
2. **Every finding is self-contained.** A cold `triage` session reads the `[FINDINGS]` item, not
   this conversation. Symptom, evidence, a `path:line` pointer, a labelled root-cause *hypothesis*,
   classification, repro — plus, here, which flow and sub-step and which `[TASK]`s it came from.
3. **A pass verdict is a receipt, and it means exactly one thing**: a human executed that flow and
   observed it work. Nothing else ever produces one — not "probably fine", not silence, not a
   change of subject. A false pass is a false receipt, and the receipt is the only record the pass
   ever happened.

## Input: one `[SPEC]`

**One input, no branching, no selection logic.** The user passes a `[SPEC]` work-item id or URL —
strip query strings. If they pass nothing, ask; never guess one, and never go hunting for a spec.
Fetch it with `mcp__ado__wit_work_item` (`action: "get"`), `expand: "relations"` and **no** `fields`
filter (the two are mutually exclusive, and a filter suppresses relations), and confirm the type and
the `[SPEC]` title prefix before anything else.

### Finding the run

The run's identity is its **pull request**, and the `[SPEC]` already points at it: `work-on-spec`
attaches the `[SPEC]` to the PR as a linked work item in the same call that opens it, which is what
puts the link on the item. So the relations you just fetched carry it — an **`ArtifactLink`** whose
name is `Pull Request` and whose url is a `vstfs:///Git/PullRequestId/…` artifact id; the **last
segment of that url is the pull-request id**. Fetch it with `mcp__ado__repo_pull_request`, against
the **repo project + repository**, never the work-item project.

**More than one, or none, is a stop**: say what you found and ask. If the relations carry no PR at
all, the one permitted fallback is to list the repository's open pull requests for the source branch
the adapter's **branch pattern** plus this `[SPEC]`'s id computes to — and a miss there is still a
stop, not a search. A `[SPEC]` whose run cannot be located is a `[SPEC]` this skill cannot compose a
pass for, and saying so is the correct outcome.

Then **say which PR you picked** — id, source branch, title — before reading anything else.

## Composing the pass

### What you read, and what it is for

Four reads, all of the branch that PR points at. **The diff and the commits come from the local
checkout, not the MCP** — the server exposes no diff tool, and the branch is checked out anyway
(see *Session hygiene*):

| Read | How | What it is |
|---|---|---|
| the diff | `git diff <default-branch>...<spec-branch>` | **the as-built record** — the only authority on what there is to test |
| the commits | `git log <default-branch>..<spec-branch> --format='%H %s%n%b'` | attribution: the `AB#<id>` reference in each commit **body** says which `[TASK]` owns that code |
| the landed `[TASK]`s | the `[SPEC]`'s siblings per [`../_shared/ado-eligibility.md`](../_shared/ado-eligibility.md) §2–3, kept where a commit on the branch references them | which slices are in this run at all |
| each `[TASK]`'s description | already in hand from that walk | acceptance criteria and planned `## QA notes` |

**The reference lives in the commit body, so grep the full message, not the subject**, and keep the
`([^0-9]|$)` guard when matching one id — a bare `AB#12` pattern also matches `AB#1234`, and
attribution silently credited to the wrong `[TASK]` is worse than none.

**Commits are truth, state is cache.** A `[TASK]` whose commit is on the branch is landed even
though its board state is still non-terminal — tasks close on pull-request completion, not on
commit. Do not filter this list by `System.State`.

The last two reads are **context, not the pass**. A `[TASK]`'s `## QA notes` was written before the
code existed and may describe something built differently or not at all; read it for intent and let
the diff overrule it. **There is no per-task write-back to read** — the workers' refined notes went
into a report the orchestrator consumed, and nothing durable holds them.

### What a flow is

A **flow** is a run of sub-steps that share a starting state and end somewhere the tester can safely
walk away from. Each flow has:

- a **name** — what the tester is exercising, in their words;
- an explicit **`start from:` line** — the shared setup or precondition the sub-steps assume;
- **sub-steps**, numbered within the flow, each naming an action and an observable result;
- **attribution** — the `[TASK]`s whose code this flow exercises, lifted from the `AB#<id>`
  references in the bodies of the commits that touched the files involved, and written **backticked**.

**The first flow is always "get running"**: whatever the adapter's `## Commands` and L5 rung say it
takes to have the thing in front of you — the launch command, the branch checked out, any config.
Everything after it starts from a running system.

**Cross-flow dependency is allowed, and must be named in `start from:`** — "start from: a completed
flow 2, app still running" is a fine precondition; leaving it implicit is not. A tester who reads
`start from:` and cannot get there has been handed a flow they cannot run.

### Flow boundaries

Boundaries follow **cohesion**: same screen, same config, same state. **Never "by `[TASK]`" and
never "every N sub-steps".** A `[TASK]` that touched three unrelated surfaces earns sub-steps in
three flows; three `[TASK]`s that all changed one screen share one.

3–7 sub-steps is a smell test, not a rule. A one-sub-step flow is fine — a single dependency bump
with one thing to look at is one flow with one sub-step, not padding to reach a quota. A flow that
has grown past a dozen sub-steps is usually two flows whose shared starting state you have not named
yet.

**Present the whole list first** — numbered flows, each with its name and `start from:` — so the
tester can see the shape of the pass and how long it is before committing to it.

### No upfront exploration beyond the four reads

The four reads above are the composition input, and that is all. Do **not** go reading the wider
codebase to write the flows. Elaboration *during* the pass — when the human asks what a sub-step
means — is **on demand only**, and delegated, never done on this thread:

- Spawn **one throwaway subagent** per question: the **Agent** tool with the explorer agent from the
  adapter's `## Sources of truth` (`Explore` where it says None), Haiku-class, thoroughness
  "medium". Speak in tiers per [`../_shared/model-effort-heuristics.md`](../_shared/model-effort-heuristics.md).
- Ask for a **condensed report**: paths, symbols, the one thing that answers the question. Do not
  read, grep or glob yourself — the point is to keep the QA thread clean.
- **It must name its source**, and you relay it in that form: *"from the diff on this branch: …"* —
  so the human always knows they are hearing an inference from code, not the pass.

Two hard limits: elaboration **never rewrites a flow mid-pass**, and it is **never the basis for
judging a verdict**. Only the human's observation in the running app decides that.

### Session hygiene: check and report, act only on the word

Before presenting flow 1, confirm and say what you found:

- the PR's source branch is the one checked out (`git branch --show-current`) — the adapter's
  **branch pattern** plus the `[SPEC]` id says what it should be;
- the pull request is open and still a draft;
- the tree is clean (`git status --short`).

Anything unexpected — dirty tree, detached HEAD, a completed pull request, the wrong branch — **say
so and stop for the human**. The driver runs read-only and verify commands from the adapter's
`## Commands` freely; anything that changes the working tree or starts a long-lived process it
**proposes and waits for a yes**. The tester owns their machine.

## Driving the pass

**Present flow *n* whole** — name, `start from:`, every sub-step — and narrate the position: **"flow
3 of 5"**. A flow presented a sub-step at a time is a flow the tester cannot plan a walk-away point
in, which is the one thing flows exist to give them.

Within the flow, split the work:

- **Sub-steps the driver can verify itself** — the adapter's L2 and L3 rungs: commands with
  checkable output, a build, a file that must exist, a work item that must be in a given state.
  **Run them and paste the output.** Evidence, not a claim that they passed.
- **Sub-steps only a human can do** — anything requiring eyes on a running system. Ask for exactly
  those, having already shown the machine half.

### One verdict per flow

| Verdict | Effect |
|---|---|
| **Pass** | record it, move to flow *n+1* |
| **Fail at sub-step *k*** | append a finding to the run's `[FINDINGS]` item naming flow *n*, sub-step *k*; move to flow *n+1* |

- **Partial progress inside a flow is not recorded.** A re-test reruns the whole flow — cheap by
  construction, because flows are short and start from a named state. There is no half-passed flow
  and no third verdict.
- **A failed flow does not block the next one.** Unless its failure makes a later flow's
  `start from:` unreachable, in which case say so and ask.
- **Never advance without an explicit verdict.** Not from silence, not from a change of subject, not
  from "ok". If the next thing the human says is not a verdict, answer it and re-present the flow.
- **Natural language, not keywords.** "yeah all four showed up", "died on the second one", "fine
  until the last bit" are all verdicts. There is no vocabulary to memorise.
- **But never record a pass on ambiguity.** "I think so", "looks about right", "close enough" are
  not verdicts. Ask **one** clarifying question naming the observable result the sub-step states,
  and wait.

### A structurally unexecutable sub-step is itself a finding

A sub-step that **cannot name an entry point, a command and an expected result** — the adapter's L5
rung — is not something this project can test. That is not a skip and not a shrug: **log it as a
finding**, classification `bug (this repo)`, so it gets a paper trail and a trip through triage
instead of evaporating. Since this skill composed the sub-step, the finding is against this skill's
composition or against a `[TASK]` that landed nothing testable — say which. Then advance like any
other failure.

### "Blocked" is not a step state

It is the human stopping. Go to `## End of pass` and take the stopped-early branch: post the
receipt, **leave `needs-qa` on**, say which flow they reached.

## The `[FINDINGS]` item

**Its whole shape — one per run, lazy creation, the Task-under-the-parent placement, the
`### [FINDING] ` marker, the append path, and how `triage` reads it — is
[`findings-item.md`](../references/findings-item.md). Read it before the first failure.** What
follows is only this skill's half.

**Create it on the first failure of the pass, and not before.** A clean pass creates nothing.

Then, in this order, once per run:

1. Create the item (`wit_work_item_write`, `action: "add_child"`, `format: "Markdown"`), and verify
   the hierarchy link landed.
2. Append the finding to the item's description, by that document's read-modify-write path.

Every later failure in the same pass skips 1 — the item already exists. **Never create a second item
for one run.**

**There is no run-context line to write the reference into any more.** That write-back was the third
never-edit carve-out on a QA comment this skill no longer reads, and a comment it never posts. The
run's `[FINDINGS]` id is instead named **in the end-of-pass receipt**, backticked, and reported in
the terminal at the moment of creation. `findings-item.md` already accepts a **pasted id** as
`triage`'s input, and that is the route until its discovery half is revised.

**One finding per turn. Never batch.** Append it, report the finding's number and a one-line recap,
then move to the next flow.

**A finding noticed outside any flow** goes into the same item, by the same path, with the
`**Step:**` and `**From:**` lines **omitted entirely** — there is no flow and no attribution to
lift. It records no verdict, because no flow is being recorded.

### The two attribution fields

`findings-item.md` owns the body template. Two of its fields are this skill's to fill, and only one
of them has changed shape:

- **`**Step:**` is the position in this pass — flow number, flow name, sub-step number**:
  `**Step:** flow 3 ("search and filter"), sub-step 2`. **No permalink**: the pass was composed in
  this session and posted nowhere, so there is nothing to link to. Do not invent a link and do not
  write "n/a"; the flow name is what makes the position legible to a cold reader.
- **`**From:**` is unchanged** — the **backticked** owning-`[TASK]` ids, space-separated where the
  flow exercises more than one, lifted from the `AB#<id>` references in the commits that touched the
  files involved. Backticked because a bare `#NNNN` silently wires a `Related` relation onto the
  work item; the description's one permitted bare mention is already spent on the `Spec: #<id>` line.

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
  exception: it answers "what does this sub-step mean", never "why did it break", and never decides
  a verdict.)
</the-line>

<routing>
### Routing (which repo/owner)

- **This-repo bug** → a real defect in the code under test. `triage` will file a `[BUG]` here.
- **Contract-boundary bug** → the symptom is in this app but the cause sits on the other side of the
  API boundary, in the repo named by the adapter's `## Repo` → *Related repos*. Prove it with the one
  decisive probe where feasible and say so explicitly — `triage` investigates over there and files
  in that repo, cross-linked back. Do **not** fix or file across the boundary from here.
- **Deferred-by-design** → not a bug. Say what was deferred, cite the code comment or `[SPEC]` note,
  and what the follow-up slice needs.
- **Works-as-intended / enhancement** → capture the desire, mark it as not-a-defect.

If the adapter says "None" for related repos, there is no contract boundary to route to —
everything is a this-repo finding.
</routing>

## End of pass: the receipt, and the `needs-qa` tag

Two artifacts, in this order:

1. **The receipt** — one **free-form** comment on the **`[SPEC]`**: which flows ran, the verdict on
   each, the run's `[FINDINGS]` id backticked if one was created, and — if the pass stopped early —
   which flow they got to. Free-form means free-form: **nothing parses it**, it is output rather
   than input, and it has no template. Post it with `mcp__ado__wit_work_item_comment_write`
   (`action: "add"`), against the adapter's **work-item project**, carrying **`format: "Markdown"`**
   — a comment posted without it lands as HTML and its headings and code spans arrive as literal
   text. **Escape angle brackets at synthesis time**, and **prefer inline code spans to fenced
   blocks**: a fence in a comment comes back empty (measured).
2. **The tag.** A pass that ran every flow to a verdict → offer to remove `needs-qa`, and on a yes,
   remove it. A pass that **stopped early** → post the receipt and **leave `needs-qa` on**, saying
   so in as many words. The tag is the queue signal; an unfinished pass is still in the queue.

Findings do **not** hold the tag on. A pass that ran every flow and found three bugs is a completed
pass — the findings are `triage`'s queue, not QA's.

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

**A re-run composes fresh.** It reads the branch again — which has usually moved — and builds new
flows rather than reconstructing the old ones. Then it **asks the human where to start**, offering
the earlier receipt's stopping point as the obvious answer. There is no resume state to read, and
that is deliberate: the alternative is a stored pass that drifts out of date against the branch it
describes. A second run against the same `[SPEC]` gets its own pass, its own receipt and its own
`[FINDINGS]` item.

**Never**: complete the pull request, close the `[SPEC]`, edit an earlier receipt, delete a comment,
or write any field of the parent work item. Tag removal and the receipt are the complete list of
what this skill writes to the `[SPEC]`.

## The terseness floor

**Composing the pass does not license compressing it.** Every sub-step must be executable by a human
reading it cold:

- a receipt or a finding outlives this session;
- a sub-step that only works because a model is there to interpret it is not a sub-step;
- and the driver reads sub-steps out as written.

The driver adds gating and bookkeeping, **not comprehension**. If you cannot write a sub-step that
names an entry point, a command and an observable result, the honest output is a flow with fewer
sub-steps — or the note that this `[TASK]` has nothing a human can exercise.

## Handoff to triage

The `[FINDINGS]` item is this skill's only output to the tracker besides the receipt on the `[SPEC]`
and the tag it removes; nothing reads the receipt back. A later `/ado-workflow:triage` session reads
that item, confirms each finding, root-causes it, and promotes the survivors into `[BUG]` work
items. **This skill never fixes anything and never files a `[BUG]`.**
