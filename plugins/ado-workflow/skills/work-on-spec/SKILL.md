---
name: work-on-spec
description: Orchestrate a whole `[SPEC]` end-to-end on Azure DevOps — pick each `[TASK]`, move it across the board, spawn a fresh worker subagent per task, verify, commit, maintain one draft pull request — pausing per the chosen gate. Use when the user says `work on spec` with a work-item number or URL, or passes /work-on-spec a `[SPEC]`. Re-entrant — the same command cold-starts and resumes.
---

# Work On Spec

Run a whole `[SPEC]` in one session: orchestrator (this session's model) + one fresh worker
subagent per `[TASK]`. The human stays in the creative loop (grill / spec / tasks) and the QA
gate.

The Azure DevOps sibling of `work-on-prd`. Same shape, different tracker: board states instead
of labels, work-item links instead of `Closes` keywords, an Azure Repos pull request instead of
a GitHub one.

## Invocation

`/ado-workflow:work-on-spec <spec-url|id> [--gate=task|events|end]`

**Invocation name depends on the install route.** From a plugin (marketplace install or a
skills-dir link) every skill in this plugin is namespaced: `/ado-workflow:work-on-spec`,
`/ado-workflow:next-task-to-implement`, and so on. Only a bare symlink into a config's `skills/`
directory — the pre-plugin route — gives the unprefixed `/work-on-spec`. The same rule governs
the agent type; see Loop step 5. Unprefixed names below are shorthand for whichever form your
route provides.

- `<spec-url|id>` — the `[SPEC]` work item (id or URL; strip query strings). **Mandatory** — if
  no argument is passed, ask; never guess one. One `[SPEC]` per loop — no parallel specs.
- `--gate` (default `events`):
  - `task` — pause for human approval after every worker report.
  - `events` — run free; pause only on: verify failure after retries · deviation from spec ·
    destructive/irreversible action · ambiguity.
  - `end` — pause only at QA (loop end).
  - Graduation path: task → events → end.
- **Regardless of gate**: a `[TASK]` with unmet `## External steps` always pauses and asks the
  human.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` — read it first and hardcode none of it here. From
`## Repo` → `### Azure DevOps`: the organisation, the **work-item project**, the **repo
project**, the team, the repository, the work-item type, the **three board states**, the title
prefixes and the **branch pattern**. From the rest of the adapter: the `## Commands` table, the
verify ladder, the `## Project gates` registry, and the QA-doc convention — for the *shape* of a
QA entry only; this loop writes no file at its path (see *Loop end*).

**Abort** if the adapter is missing, or if its `Tracker:` line is anything other than
`azure-devops` (an absent line means `github` — that project wants `work-on-prd`). Guessing an
organisation or a project does not error; it returns an empty result that reads like a spec with
no tasks, or writes somewhere nobody is looking.

`[SPEC]`, `[TASK]` and `[QA]` below are **shorthand for the adapter's *Title prefixes* row**,
written out for readability. If that row names different prefixes, they win — here, and in every
title filter this skill applies.

### The two-project trap

The work items and the code live in **different ADO projects of the same organisation**, which
is why the adapter carries two project fields. Get this right at every call site:

- Work-item calls (`wit_*`) pass the **work-item project**.
- Repository and pull-request calls (`repo_*`) pass the **repo project** plus the adapter's
  **repository** name.

A call that assumes the repo belongs to the work item's project looks in the wrong place and
returns an **empty result rather than an error** — a repo that appears not to exist, a pull
request that appears not to have been created. Where the adapter genuinely names the same
project twice, that is still two reads of two fields, not one field used twice.

### Tool names come from the running server

This skill names the `mcp__ado__*` tools it calls, but the server's tool set and parameter names
vary by `@azure-devops/mcp` version. If a named tool or field is not there, **discover the
equivalent from the server rather than skipping the step**, and announce the substitution in the
run. A step that cannot be performed at all is a pause, never a silent omission — the loop's
guarantees (re-entrancy, work-item closure on completion) are exactly what those calls buy.

## Readiness: the ADO MCP server

Requires the Azure DevOps MCP server (`mcp__ado__*` tools).

**Before starting:**

1. Check memory — the server may already be recorded as configured for this project.
2. If not in memory, probe: call `mcp__ado__core_list_projects` with `top: 1`.
   - Responds → proceed; save to memory: `ADO MCP active for this project`.
   - Fails → set it up. See [`ado-mcp-setup.md`](../references/ado-mcp-setup.md). **Read it
     before concluding the server is missing** — a probe failure has two causes, and the likelier
     one is a server running correctly under the wrong key, which this probe cannot distinguish
     from no server at all.

## Non-negotiables (circuit breakers)

- Max **2 self-fix attempts** per worker; attempts must be announced in the worker report.
- **2 consecutive failed `[TASK]`s** → full stop with summary.
- **Never** force-push, amend, or rewrite published history. **Never** complete, merge or publish
  the pull request — it stays a **draft** for its entire life. **Never** close the `[SPEC]`.
- `git reset --hard` / `git clean` only ever on the spec branch, only to discard a stale claim's
  uncommitted work.

## What the loop must not write

- The **`[SPEC]` advances exactly once and then stops.** On the first `[TASK]` claim of the whole
  spec it moves to the claimed state; after that it is never written again — not advanced, not
  closed, not commented into a status feed. The human runs QA against it and may add `[TASK]`s
  afterwards, and a spec parked in the claimed state is what says "this is being run".
- **No field of the parent work item is ever written.** It is read twice — walked to find the
  spec's siblings (per the eligibility mechanics), and read at loop end for its acceptance
  criteria. The only thing that touches it is the hierarchy relation the `[QA]` item creates from
  its own side at loop end, the same way `to-spec-tasks` places a `[TASK]`. No field, no state, no
  comment: it belongs to Product.
- **No status feed.** The loop's only writes to work items are board-state moves on `[TASK]`s, the
  single `[SPEC]` move above, escalation comments on failed `[TASK]`s, and the one `[QA]` item at
  loop end.

## Setup (idempotent — cold start and resume are the same code path)

State lives in git + Azure DevOps only (branch commits, board states, PR body). Zero
session-resident state: killing the session loses nothing but uncommitted worker output, which is
discarded by design.

0. **Keep-awake** (local-Mac convenience only; no-op elsewhere): prevent the machine from
   sleeping through the long run. Idempotent — safe on resume, never stacks a second process;
   guarded so it silently does nothing where `caffeinate` is absent (Linux server/CI).

   ```bash
   command -v caffeinate >/dev/null && ! pgrep -F /tmp/work-on-spec.caffeinate.pid >/dev/null 2>&1 && { caffeinate -dimsu & echo $! > /tmp/work-on-spec.caffeinate.pid; }
   ```

1. **Fetch state**: the `[SPEC]` and its `[TASK]`s per
   [`../_shared/ado-eligibility.md`](../_shared/ado-eligibility.md) — resolve the spec, walk
   spec → parent → siblings, filter to this spec's `[TASK]`s, parse each description. Read it
   with [`../_shared/eligibility-policy.md`](../_shared/eligibility-policy.md); neither half
   decides a pick alone. Every read passes `expand: "relations"` and **no** `fields` filter.
   Zero `[TASK]`s → tell the user to run `/ado-workflow:to-spec-tasks` first, stop. Cycle in
   `Blocked by` → report it, stop.
2. **Branch**: name it from the adapter's **branch pattern**, with the `[SPEC]` work-item id and
   a slug from its title (e.g. `spec/<id>-<slug>`). Check it out if it exists (local or remote),
   else create it from an up-to-date default branch. One branch per spec, on both a cold start
   and a resume — the pattern is what makes the resume find the same branch.

   **Strip the title's prefix before slugging** — slug `dark-mode`, never `spec-dark-mode`. A
   `[SPEC]` title always carries one here, so this is not an edge case; and a run whose computed
   name stops matching the branch its work is on opens a *second* branch and a *second* pull
   request, reconstructs zero commits, and re-runs every landed `[TASK]` without erroring. Strip
   any leading `[…]` bracket group rather than the literal string, so an adapter naming a
   different prefix is handled too.
3. **Pull request** (one per spec): list the repository's open pull requests for this source
   branch — **repo project + repository, not the work-item project**. If one exists, adopt it;
   **never open a second**. If none exists, push (empty commit `spec AB#<id>: loop start` if the
   branch has no commits ahead) and create it with `isDraft: true`, targeting the adapter's
   default branch. Body skeleton:

   ```
   Runs [SPEC] AB#<id>: <title>

   ## Tasks
   - [ ] AB#<t1> <title>
   - [ ] AB#<t2> <title>

   Linked work items close on PR completion — see the completion options, not a keyword line.

   QA: (added at loop end)

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

   Then wire it per *Pull-request wiring* below. On a resume, re-run that wiring against the
   adopted PR: it is idempotent, and it repairs a PR whose completion options a human toggled.
4. **Reconstruct**: a `[TASK]` is done ⇔ a commit referencing it exists on the branch. **Board
   state is cache; commits are truth.** The reference lives in the commit *body* (normative form
   in [`../../agents/spec-worker.md`](../../agents/spec-worker.md) mandate 5), so grep the full
   message, not the subject:

   ```bash
   git log <default-branch>..<spec-branch> -E --grep="AB#<id>([^0-9]|$)" --oneline
   ```

   The `([^0-9]|$)` guard is load-bearing: a bare `AB#12` pattern also matches `AB#1234`, which
   would report a task as done because a different one was. Repair drifted state to match commits
   — a `[TASK]` with a commit and a pickable state moves to committed-awaiting-merge, and its PR
   checkbox gets ticked. Never repair in the other direction: a state without a commit is not
   evidence of anything.
5. **Stale claim** (a `[TASK]` in the claimed state with no matching commit — a previous run died
   mid-task): discard uncommitted work (`git reset --hard && git clean -fd`, spec branch only),
   move the `[TASK]` back to the pickable state. It restarts with a fresh worker via the normal
   pick path — no partial-work recovery, re-entrancy not recovery.

## Pull-request wiring

The completion options are what replace the GitHub side's un-queryable repo setting, and they
are why this adapter needs no one-time human precondition at all. Two things must be true of the
PR at all times:

- **Every `[TASK]` id and the `[SPEC]` id are attached to it** as linked work items. The `[SPEC]`
  is attached at creation; each `[TASK]` is attached on its success path, as it lands.
- **Its completion options transition linked work items** (`transitionWorkItems`, alongside
  whatever merge strategy the repo already uses). Armed this way, a human completing the PR by
  hand closes every attached `[TASK]`.

The ADO MCP server does **not** expose one tool per operation. Both halves go through
`mcp__ado__repo_pull_request_write`, discriminated by an `action` argument, against the
**repo project + repository**:

| Operation | Call |
|---|---|
| Create the PR | `repo_pull_request_write`, `action: "create"` — takes `repositoryId`, `sourceRefName`, `targetRefName`, `title`, and optionally `isDraft`, `description`, `labels`, and **`workItems` (space-separated ids)** |
| Arm / re-arm completion options | `repo_pull_request_write`, `action: "update"` — carries `transitionWorkItems`, `autoComplete`, `mergeStrategy`, `deleteSourceBranch`, and also flips `isDraft` and `status` |
| Attach a work item after creation | `mcp__ado__wit_work_item_link_write`, `action: "link_to_pull_request"` — takes `workItemId`, `pullRequestId`, `repositoryId`, and `projectId` **as a GUID, not a name** |

Two consequences worth planning around. `workItems` on `create` means the `[SPEC]` can be
attached in the same call that opens the PR, with no second round trip. And each `[TASK]` landing
later needs `wit_work_item_link_write`, which wants the project **GUID** — read it from the
adapter rather than passing the project name, which fails.

**`transitionWorkItems` defaults to `true`.** The risk is therefore not that you forget to arm
it; it is armed unless you actively disarm it. That inverts the failure mode: anything you attach
to this PR *will* be transitioned on completion, which is what makes the `[QA]` rule in *Loop end*
load-bearing rather than cautionary.

Then **read the PR back and confirm** — attached ids present, flag set. Do not trust the write; an
ignored field is the cheapest thing in this whole loop to get wrong and the most expensive to
notice, because the loop keeps working perfectly and only the closure at the end silently doesn't
happen.

If the server version exposes no field for one of them, that is the pause case from *Tool names
come from the running server*: say which one, record it in the PR body as a step the human must
take at completion time, and carry on. Never report the PR as wired when it isn't.

The commit-to-work-item links are a separate, free mechanism: each worker commit carries
`AB#<id>` in its body, so Azure DevOps links the commit to the `[TASK]` on push without the loop
doing anything. That link is not a substitute for attaching the work item to the PR — it does not
transition anything.

## Loop (per `[TASK]`)

1. **Pick** the next eligible `[TASK]` per
   [`../_shared/eligibility-policy.md`](../_shared/eligibility-policy.md) and
   [`../_shared/ado-eligibility.md`](../_shared/ado-eligibility.md) (open ∧ blockers done;
   picking order as specced) — applying the **orchestrated-mode exception**: a blocker **inside
   this spec** is also satisfied when its commit exists on the spec branch, observed with the
   grep in Setup step 4, not by reading `System.State`. Tasks close on PR completion rather than
   on commit, so without this every `Blocked by` chain would deadlock the loop. None eligible but
   open blocked `[TASK]`s exist → report the blocking chain; if the blockers are outside this
   spec, pause for the human. None open at all → go to **Loop end**.
2. **External steps**: any unmet `- [ ]` under `## External steps` → pause, list them, wait for
   the human. Always, regardless of gate.
3. **Claim**: move the `[TASK]` to the adapter's **claimed** state. On the **first** claim of the
   run, also move the `[SPEC]` to the claimed state if it is not already past pickable — once,
   ever (see *What the loop must not write*).
4. **Route model**: apply [`../_shared/model-effort-heuristics.md`](../_shared/model-effort-heuristics.md)
   **in orchestrated mode** — the default flips: workers start Sonnet-class and *upgrade* to
   Opus-class on the file's heavier/risk signals. Announce the routing call (tier + matched
   signals) before spawning.
5. **Spawn worker**: Agent tool, `subagent_type: ado-workflow:spec-worker` (see *Agent type by
   route* below), `model` per the routing call, `run_in_background: false`. Flat hierarchy —
   workers never spawn workers. Isolation is total, and tighter here than on the GitHub side: the
   worker is denied every ADO tool, so **anything it needs from the tracker must be in its
   prompt**. The **mandates and the report contract live in
   [`../../agents/spec-worker.md`](../../agents/spec-worker.md)** — never restate them in the
   prompt, which carries only the per-call inputs:
   - The **full `[TASK]` body** (incl. `## Worker context`, `## QA notes`, acceptance criteria).
   - The **full `[SPEC]` body**. A `[TASK]` is deliberately slim and points at its spec for
     architecture, file inventories and prior art; a worker that cannot call the tracker cannot
     follow that pointer, so the orchestrator resolves it. Paste the spec as fetched — do not
     summarise it.
   - The **full contents of the project adapter**. The adapter only; a gate it registers goes in
     the prompt **only** when this `[TASK]` triggers it — pasting every gate into every worker is
     the tax that keeps gates out of the adapter in the first place.
   - The **branch name** and the **work-item id** for the `Work-item: AB#<id>` commit trailer.
   - The **routing call** you announced in step 4.

   **Agent type by route — get this right before you fall back.** A plugin namespaces every
   component it provides, so installed from the marketplace *or* linked as a skills-dir plugin
   the type is **`ado-workflow:spec-worker`**. Only a hand-placed `.claude/agents/spec-worker.md`
   (the pre-plugin route) registers the bare `spec-worker`. Try the namespaced name first and the
   bare name second; treating the bare name as primary is what silently produced a whole run of
   `general-purpose` workers once already on the GitHub loop.

   *Detachable — expect to need this*: agent registration lags. A file added to an agents
   directory that already existed resolves after a few minutes; a **newly created** agents
   directory does not resolve at all for the rest of the session, and a plugin enabled mid-session
   does not register its agents until the next session. So if **neither** type name resolves, do
   not wait and retry — read `../../agents/spec-worker.md` and paste its body (everything below
   the frontmatter) into a `general-purpose` agent for the whole run. Same contract, one source of
   truth. On this route the tool denial is prose, not enforcement, so state in the prompt that the
   worker must not call any `mcp__ado__*` tool. **Announce which of the three paths the run took**
   — namespaced, bare, or detached — because a detached run looks identical to a real one in the
   output, and that is the only signal that the agent did not resolve.
6. **Judge the report**: commit exists on branch (same grep as Setup step 4) · verify evidence is
   real (spot-check: re-run the L2 command if evidence looks thin) · deviations acceptable · the
   `[TASK]`'s acceptance criteria covered.
7. **Gate** per `--gate` mode (see Invocation). On pause: present the report + your judgement,
   wait for the human.
8. **Success path**: push the branch → move the `[TASK]` to the adapter's
   **committed-awaiting-merge** state → attach its id to the pull request (see *Pull-request
   wiring*) → tick its checkbox in the PR body. The PR stays a draft.
9. **Failure path** (worker exhausted its 2 attempts, or report judged unacceptable): discard
   uncommitted work (reset/clean, spec branch only) → move the `[TASK]` back to the **pickable**
   state (failure is a backward transition, not a new state) → post an **escalation comment** on
   the work item: what was tried, what failed, evidence → pause per gate (`task`/`events` pause;
   `end` records and continues) → increment the consecutive-failure counter; at 2, full stop with
   summary. A success resets the counter. A failed `[TASK]` is not re-picked in this run unless
   the human unblocks it.

## Loop end (no eligible `[TASK]`s left)

Three things, in order: the `[QA]` work item, the pull-request body, the final summary.

### 1. The `[QA]` work item — one per *run*

**The deliberate divergence from `work-on-prd`.** That loop commits a QA document to the branch at
the adapter's QA-doc path. This one **commits nothing to the repo** — it creates a `[QA]` work
item and leaves the working tree alone. Do not port the committed-file behaviour and do not write
to the adapter's QA-doc path; the adapter's `## QA doc convention` still supplies the *shape* of a
QA entry (what shipped · how to exercise it in the running app · edge cases the worker flagged),
and no longer supplies a destination.

One per **run**, never one per `[SPEC]`. A run covers exactly the slice of `[TASK]`s that just
landed, so a second run against the same `[SPEC]` creates a **second** `[QA]` item and never edits
the first. That is the point of the divergence: a committed document accumulates and goes stale
silently, while a per-run item describes one testable slice and is closed by the human once tested.

#### What it is built from

Three sources, and nothing else:

1. Each worker's **refined QA notes** — item 4 of the report contract in
   [`../../agents/spec-worker.md`](../../agents/spec-worker.md). These are the steps; the
   `[TASK]`'s original `## QA notes` are what the worker refined, not a second source to merge.
2. Each worker's **deviation log** (item 3) and the edge cases it flagged. These are the gotchas.
3. The **parent work item's acceptance criteria** — the coverage checklist. Read on, this is the
   one that bites.

#### Where the acceptance criteria come from

Parse them from the **parent work item's description**, under its `## Acceptance Criteria`
heading. **Never** from the dedicated acceptance-criteria field
(`Microsoft.VSTS.Common.AcceptanceCriteria`).

That field is unpopulated on this process, and reading it **does not fail** — it succeeds and
returns empty. So a `[QA]` item built from it has a well-formed coverage checklist with nothing in
it, and looks exactly like a correct one. Nothing downstream catches that: the human works through
the steps, ticks a checklist that lists no criteria, and the acceptance criteria of the thing that
just shipped are never checked by anybody. This is the one read in the whole loop where success is
not evidence — confirm you got criteria, not just a response.

The parent is the work item Setup step 1 already resolved from the `[SPEC]`'s `Hierarchy-Reverse`
relation; fetch it with `mcp__ado__wit_work_item` (`action: "get"`), `expand: "relations"` and **no `fields`
filter** ([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) §4).
Take each criterion **verbatim** — a paraphrased criterion is a different criterion, and the human
ticking it is agreeing to something Product never wrote.

Two failure modes to handle rather than paper over:

- **No `## Acceptance Criteria` heading in the parent's description** → omit the coverage section
  and say in the final summary that the parent carries none. Do not fall back to the dedicated
  field, and do not substitute the `[TASK]`s' own `## Acceptance criteria` sections — those are
  per-task, they are what the workers already verified, and promoting them produces a checklist
  that only restates the run.
- **A criterion no `[TASK]` in this run touched** → it still goes on the checklist, marked *not
  covered by this run*. The checklist measures the parent, not the run.

#### What contributes, and what doesn't

A `[TASK]` contributes steps only if it produced something a human can exercise in the running
app. Setup, dependency installs, config, pure refactors and internal-only changes contribute
**nothing** — not a step, and **not** a "nothing to test here" line. Those lines are what turn a QA
item into a document nobody reads to the end.

If **no** `[TASK]` in the run produced anything testable, create **no `[QA]` work item at all**.
An empty one is worse than none: it is a work item a human has to open, read and close in order to
learn nothing. Say so explicitly in the final summary — "no `[QA]` item: nothing in this run is
manually testable" plus the list of `[TASK]`s — and put the same sentence where the PR body's `QA:`
line would have gone.

#### The `[QA]` body

<!-- String contract: this template is the NORMATIVE copy of the `[QA]` body. Its only consumer
is the human running verify-ladder L5 against the branch — no skill parses it, and nothing reads
a previous run's `[QA]` item — so "normative" here means the section order and the three sources
are fixed, not that a parser depends on the wording. The final summary and the PR body reference
this item by id and url; neither restates its contents. -->

<qa-template>

Run of [SPEC] #<spec-id> — <n> [TASK]s landed <date>
PR: [<repo> PR NNNN](https://dev.azure.com/<org>/<repo-project>/_git/<repo>/pullrequest/NNNN)

## Steps

1. <action to take in the running app> — expected: <the observable result>  (#<task-id>)
2. <next action> — expected: <result>  (#<task-id>)

## Gotchas

- <edge case or deviation the worker flagged, and what it means for the tester>  (#<task-id>)

## Acceptance criteria coverage

- [ ] <criterion, verbatim from the parent's description> — steps 1–3
- [ ] <criterion> — **not covered by this run**

</qa-template>

Steps are numbered **continuously across the whole run**, in the order a human would sit down and
work through them, each carrying the `[TASK]` id it came from so a failure routes straight back to
the work item that caused it. Every step states its expected result; a step whose result is "it
looks right" is not a step.

Title: the adapter's `[QA]` prefix, the `[SPEC]` title, and the run's date. Two runs on the same
day produce two items with the same title — that is fine and expected, they differ by id and
creation time. Never reuse or edit an earlier one to avoid a duplicate.

Apply the authoring invariants **at synthesis time, before the body is sent**
([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md)):

- **§1, angle brackets.** This is the most bracket-dense body the plugin writes — QA steps are
  prose full of component names, elements and generic types, including the placeholders above.
  Escape every one of them as `&lt;` / `&gt;` before sending. `wit_work_item_write` (`action: "update"`) has no
  `format` option and falls back to HTML, so an unescaped token survives creation and then
  vanishes the first time anything edits the item.
- **§2, never a bare `#NNNN` for the pull request.** ADO autolinks it to the *work item* with that
  id and sends the tester somewhere unrelated. Link the PR in full, with `<org>`, the **repo
  project** and `<repo>` from the adapter. Bare `#<id>` is correct for the `[SPEC]` and `[TASK]`
  ids, and only for those — they really are work items in this org.

#### Create and link it

- `mcp__ado__wit_work_item_write` (`action: "create"`):
  - `project`: the adapter's **work-item project** (this is a work item, not a repo call)
  - `workItemType`: the adapter's **work-item type**
  - `title` / `description`: as above
  - `System.IterationPath`: inherit from the `[SPEC]`
- **Parent link is a separate call** (§3) — `mcp__ado__wit_work_item_link_write` (`action: "link"`)
  `{ id: <qa-id>, linkToId: <parent-id>, type: "parent" }`. Child of the **parent work item**, so
  the `[QA]` is a **sibling** of the `[SPEC]` and the `[TASK]`s, placed exactly as `to-spec-tasks`
  places a `[TASK]`. Setting `System.Parent` in the create call is a silent no-op and leaves it
  unparented.
- `Related` link back to the `[SPEC]`: `{ id: <qa-id>, linkToId: <spec-id>, type: "related" }`.
- **Verify before reporting it** (§5): re-fetch the parent with `expand: "relations"` and confirm
  the `[QA]` id is present as `Hierarchy-Forward`.
- Assign to the current user (§6) — the QA is the human's to run.

Adding a `[QA]` child to the parent does not disturb task discovery: the eligibility mechanics
filter the parent's children by the `[TASK]` prefix, so a `[QA]` sibling is invisible to the pick
path by construction.

### 2. Pull-request body

Replace the placeholder `QA:` line from Setup step 3 with a full link to the `[QA]` work item — or
with the no-QA sentence if none was created — and bring the task checklist to its final state. Same
call and same **repo project + repository** as every other PR-shaped call
(`mcp__ado__repo_pull_request_write`, `action: "update"`). It stays `isDraft: true`.

**Do not attach the `[QA]` item to the PR as a linked work item.** The PR's completion options
transition every linked work item, and `transitionWorkItems` **defaults to `true`**
(*Pull-request wiring*) — so this is not a risk you opt into by arming a flag, it is the default
behaviour of any PR you have not deliberately disarmed. A linked `[QA]` item would close itself
the moment the human completes the PR: a QA pass that marks itself done, which is exactly the
silent failure this whole section exists to avoid. `[TASK]`s are attached; the `[SPEC]` is
attached; the `[QA]` item is not — and it must not be passed in `workItems` on the create call
either, which is the easiest way to attach one without noticing.

### 3. Final summary to the human

Printed to the session — the loop writes no status feed to the tracker. Report:

- `[TASK]`s **done** (id, title) · **skipped** (id, and why: unmet `## External steps`, blocked by
  something outside this spec) · **failed** (id, and the gist of the escalation comment).
- **Deviations worth reading** — from the workers' deviation logs, the ones that change what a
  reviewer or tester should expect. Not every line; the `[QA]` item carries the tester-facing ones.
- **Escalations** — anything that paused the run, and anything still waiting on a human.
- The **`[QA]` work item**, by id and url — or the explicit "no `[QA]` item created: nothing in
  this run is manually testable", with the reason.
- The **pull request, left open and still a draft**, with its url: it is completed by hand after
  QA (verify ladder L5), and completing it is what transitions the `[TASK]`s.

Everything in *What the loop must not write* still holds at the end: do not complete the pull
request, do not close the `[SPEC]`, do not close the `[QA]` item you just created, and write no
field of the parent.

Then release keep-awake — mirror of Setup step 0, no-op if never started:

```bash
[ -f /tmp/work-on-spec.caffeinate.pid ] && kill "$(cat /tmp/work-on-spec.caffeinate.pid)" 2>/dev/null; rm -f /tmp/work-on-spec.caffeinate.pid
```

## Board states, and what a move means

The three state names are **adapter values, not constants** — `System.State` is a per-process
string and the names differ between ADO processes, so this skill only ever names the roles:

pickable (open, unclaimed) → claimed (a run is working it) → committed-awaiting-merge (its commit
is on the branch, the PR has not completed). Every other state on the board is terminal.

Board columns on this process map one-to-one onto work-item states, so a move is a **single state
write** — one field, one value:

```
wit_work_item_write  { action: "update", project: <work-item project>,
                        updates: [{ id: <id>, op: "add",
                                    path: "/fields/System.State",
                                    value: "<the adapter's state name>" }] }
```

There is no remove-before-add here and no risk of two states at once; that discipline is the
GitHub side's, where state is carried by labels. What replaces it as the thing to get right is
the spelling: ADO state names are per-process strings, a name the board does not have is a
rejected write or a silent no-op depending on the call, and neither reads as "you used the wrong
vocabulary". Take every name from the adapter, verbatim, and if a write is refused, report it
rather than trying a near-miss.

Nothing in this loop closes a work item. `[TASK]`s reach a terminal state when the human
completes the pull request and its armed completion options transition them; the `[SPEC]` is
closed by hand, after QA.
