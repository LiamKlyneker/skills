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

**Every skill in this plugin is namespaced**, on every route — installed from the
marketplace or loaded with `claude --plugin-dir`: `/ado-workflow:work-on-spec`,
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
verify ladder, and the `## Project gates` registry. The adapter carries no QA convention on
either tracker any more and names no QA path: this loop's QA artifact is a **comment on the
`[SPEC]` plus a `needs-qa` tag on it**, so the loop writes no file and creates no work item at
all (see *Loop end*).

**Abort** if the adapter is missing, or if its `Tracker:` line is anything other than
`azure-devops` (an absent line means `github` — that project wants `work-on-prd`). Guessing an
organisation or a project does not error; it returns an empty result that reads like a spec with
no tasks, or writes somewhere nobody is looking.

`[SPEC]`, `[TASK]` and `[FINDINGS]` below are **shorthand for the adapter's *Title prefixes* row**,
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

- The **`[SPEC]`'s board state advances exactly once and then stops.** On the first `[TASK]` claim
  of the whole spec it moves to the claimed state; after that the state is never written again —
  not advanced, not closed. The human runs QA against it and may add `[TASK]`s afterwards, and a
  spec parked in the claimed state is what says "this is being run".
- **The `[SPEC]` takes exactly two other writes, both at loop end**: the run's **QA comment** and
  the **`needs-qa` tag**. Together they are the whole QA artifact (*Loop end* §1), they are
  written once per run, and they are not a status feed — nothing else is ever commented onto the
  `[SPEC]`, and no progress or per-`[TASK]` commentary goes anywhere near it.
- **No field of the parent work item is ever written.** It is read to walk the spec's siblings
  (per the eligibility mechanics), and for nothing else. Loop end used to re-read it to confirm a
  `[QA]` item's hierarchy link had landed, and before that to lift its **acceptance criteria**
  into a coverage checklist; the `[QA]` item is gone and both reads went with it. Adding a child
  relation to the parent is still allowed and unchanged — a child places it from its own side,
  the way `to-spec-tasks` places a `[TASK]`. No field, no state, no comment: it belongs to
  Product.
- **No status feed.** The loop's only writes to work items are board-state moves on `[TASK]`s, the
  single `[SPEC]` state move above, escalation comments on failed `[TASK]`s, and the QA comment
  plus `needs-qa` tag on the `[SPEC]` at loop end.

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
to this PR *will* be transitioned on completion. There used to be a rule in *Loop end* built
around that — the `[QA]` work item was never attached, because completion would have closed the
QA pass on the human's behalf. **That rule is retired** along with the item. The QA artifact is
now a comment plus a `needs-qa` tag on the `[SPEC]`, and both survive the `[SPEC]` being
transitioned untouched, so there is nothing left here to keep off the PR (*Loop end* §2 has the
reasoning in full).

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

   **Agent type — get this right before you fall back.** A plugin namespaces every component
   it provides, so the type is **`ado-workflow:spec-worker`** however the plugin was loaded:
   installed from the marketplace, or via `claude --plugin-dir`. There is no unprefixed form;
   the bare `spec-worker` only ever came from a hand-placed `.claude/agents/` file on the
   retired pre-plugin route. Use the namespaced name; treating the bare name as primary is what silently produced a whole run of
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

Three things, in order: the QA comment, the pull-request body, the final summary.

### 1. The QA comment — one per *run*

**Create no work item, and commit nothing.** The QA artifact is a **Markdown comment on the
`[SPEC]`**, plus the **`needs-qa` tag on that same `[SPEC]`**. This loop has moved twice: it once
wrote a markdown document to a path in the adapter, then it created a per-run `[QA]` work item
parented beside the `[SPEC]`. It does neither now — the adapter names no QA path, and **no `[QA]`
work item is created anywhere in this skill**. There is no longer a reference document describing
the shape of one, either — if you find something telling you to read one, or to write a file at a
QA path, it predates this section. Everything normative about the artifact is here.

**No one-time human precondition on this tracker.** GitHub's `needs-qa` is a **label**, which a
human must create once before `work-on-prd` can apply it. An Azure DevOps **tag** is created
implicitly the first time it is used, so there is nothing to arrange in advance and nothing that
can fail because a vocabulary entry is missing.

`work-on-prd` posts a comment on the PRD issue and labels it; this loop posts a comment on the
`[SPEC]` and tags it. The two arrived at the same shape, but they are **siblings, not a shared
file with two call sites**: every literal below is this tracker's, and none of the GitHub
mechanics carry across — in particular that loop's `<!-- 75 80 -->` id trailer, which does not
survive here at all.

The person running QA reads this comment, but they are not its only consumer:
**`ado-workflow:manual-qa` parses it**, so parts of the template below are load-bearing string
contract rather than house style.

**What the consumer depends on.** Five literals; each is written here, by `manual-qa`, or by both:

| Literal | Written by | Read by |
|---|---|---|
| the **run-context line** + the **`## Steps` heading**, as a pair | loop end | identifying the QA comment among the `[SPEC]`'s comments — never a fragile substring, and `## Before you start` cannot serve because it is conditional |
| the step anchor `- [ ] <n>. ` — bracket, space, number, dot, space | loop end | locating the single line to rewrite; continuous numbering from 0 is what makes it unique |
| **checkbox state** `[ ]` / `[x]` | loop end, then `manual-qa` | resume position, and the end-of-pass check |
| the **backticked owning-`[TASK]` id** on each step | loop end | lifted into the finding's attribution |
| the terminal failure suffix ` — **failed**` | `manual-qa` | resume position; distinguishes a step nobody has run yet from one that ran and failed |

Change any of those five and you must change them in `manual-qa` in the same commit. Everything
else here — the section order, the sources, the earning rule — is normative because it is right,
not because a parser depends on the wording.

**There is no hidden id trailer, and that is not an oversight.** GitHub's mechanism does not port.
In a **comment**, an HTML comment is stripped out of the API read entirely — write `<!-- 75 -->`
and it is simply not in the body `manual-qa` reads back, so the attribution it exists to carry is
gone with it. In a **description** it survives only entity-escaped, which renders visibly on
screen. Ids therefore ride **in the open, backticked**, in the step text itself.

**One per run, never one per `[SPEC]`.** A run covers exactly the slice of `[TASK]`s that just
landed. A second run against the same `[SPEC]` posts a **second comment** and **never edits the
first**. That is the whole point of a per-run artifact rather than a committed document: a
document at a fixed path accumulates every run's output, goes stale silently, and gives the human
no way to tell which half they already tested.

**Why a comment, and what it buys.** The operator gets one queue from a WIQL query on
`[System.Tags] CONTAINS 'needs-qa'` — every `[SPEC]` awaiting a manual pass, **regardless of
state**, so an item the pull request has already transitioned is still in it. They open the
`[SPEC]` and the steps sit in its Discussion, beside the `[TASK]`s they describe. The receipt is
**tick state**: every box `[x]`, no failure suffix anywhere, and the tag removed. Removing
`needs-qa` is a human action nothing enforces and nothing simulates — do not remove it yourself,
and do not post a second comment announcing the pass is done.

**Ticking is not authoring.** The never-edit rule has **exactly three carve-outs**, all records of
a pass rather than acts of authorship, and all of them `manual-qa`'s to write:

1. **Checkbox state.** Every step is a `- [ ]` item and `[ ]` ↔ `[x]` may change after posting, so
   a tester records progress in place and resumes a partial pass instead of restarting it.
2. **The terminal failure suffix** — ` — **failed**`, plus its pointer to the logged finding —
   appended at the **end** of a step's line when that step failed. It is **append-only**: the step
   text and its backticked id stay byte-identical, nothing is re-rendered or reflowed, and the box
   stays `[ ]`. It is **reversible** — re-testing that step and passing drops the suffix and ticks
   the box in one write, which is the only reason "every box ticked, no suffix left" can mean
   "everything passed".
3. **The `[FINDINGS]` reference in the run-context line, written once.** The line names the run's
   `[FINDINGS]` item, and that item **does not exist when this comment is posted** — `manual-qa`
   creates it lazily, on the first failure of the pass. So this contract permits exactly one
   write-back into the run-context line: the reference to that item, the first time there is one.
   Every failure in a run points at the same item, so per-step links would be noise; the line
   names it once and the steps do not repeat it.

**Everything else stays forbidden**, and the list is not illustrative: no rewording a step (not
even a typo fix, not even to sharpen an expected result), no appending a new step to a posted
comment — a step that was missed belongs to the next run's comment — no deleting a comment, no
adding or removing a heading, no re-ordering or re-numbering steps, and no reply-comment that
amends the script. The comment says what that run shipped and what it claimed a tester could
exercise; the carve-outs record what a tester subsequently observed. They do not make the tester a
second author.

**What earns a step.** A landed `[TASK]` earns a step **only if a human can exercise it in the
running app**. Dependency bumps, config changes, pure refactors, internal-only work and setup
contribute **nothing**: no step, and **no standalone "nothing to test here" line, paragraph or
section**. Those lines are the entire reason the committed QA documents this replaces reached 440
lines — every landed item earned a section whether or not anybody could act on it, so the sections
that mattered were buried among the ones that didn't. Such a `[TASK]` gets **nothing at all**: not
a line, not a parenthetical, not a heading of its own. The single exception is a `[TASK]`
deliberately left for a human, or a slice deferred to a later run — something a tester would
otherwise chase as a defect. That earns **one line under `## Before you start`** and nothing more.
Applied honestly, most runs produce a comment far shorter than the list of things they landed.
That is the intended shape, not a sign something was missed.

**Nothing testable in the whole run → post nothing and tag nothing.** If **no** `[TASK]` in the
run produced anything a human can exercise, there is no comment and no `needs-qa` — an empty QA
comment is worse than none, being a thing a person has to open and read in order to learn nothing,
and a tag pointing at it puts a `[SPEC]` in the queue that has no pass to run. Say so explicitly,
in both places the comment would otherwise have been named: the **final summary** ("no QA comment:
nothing in this run is manually testable", plus the list of `[TASK]`s the run landed) and the
**pull-request body**, where the `QA:` line would have gone — the same sentence. Silence in either
place reads as a forgotten step rather than a decision.

**The body:**

<qa-template>

Run of `[SPEC]` #<spec-id> — <n> `[TASK]`s landed <date> · PR [<repo> PR NNNN](https://dev.azure.com/<org>/<repo-project>/_git/<repo>/pullrequest/NNNN)

## Before you start

- <the thing that will look broken and is not, and why — or a `[TASK]` deliberately left for a human>

## Steps

- [ ] 0. <the setup a tester does once, before anything else> → expect <the observable result> (`#12805`)
- [ ] 1. <action to take in the running app> → expect <the observable result> (`#12805`)
- [ ] 2. <action> → expect <result> (`#12805` `#12810`)

</qa-template>

The rules governing that template are deliberately written **outside** the fence. Copy the fence,
not this prose — instructions pasted inside a body template ship to the reader as comment text.

**There are exactly two headings, one of them conditional, and there is no third heading, ever.**
Every section this artifact has ever grown was a place for content that turned out not to change
what the tester does — and the failure is not hypothetical: the real item this replaces grew a
`## New tKeys to register in DCJ` section, published under its own heading, describing work that
appears in no commit on any branch. The run invented it. A heading is an invitation to fill it.

- **The run-context line** carries no heading and is the comment's first line: the `[SPEC]`, how
  many `[TASK]`s landed, the date, the pull request, and — once `manual-qa` has created one — the
  run's `[FINDINGS]` item. It is the top half of the identifying pair, so it is never omitted.
- **`## Before you start` is conditional.** Include it only when something will look broken and is
  not — a dangling symlink a later `[TASK]` repairs, a migration the tester has to run first, a
  feature flag that is off, a `[TASK]` deliberately left for a human, a slice deferred to a later
  run. A **run-wide** deviation lands here too. **Omit the heading entirely** otherwise; a "None"
  under it is the 440-line habit in miniature.
- **`## Steps` is always present** — the comment exists because at least one `[TASK]` earned a
  step, so it has content by construction.
- **Every step is a `- [ ]` task-list item.** The tick is how a pass records progress and how a
  half-finished one resumes: `manual-qa` writes the box back as the human confirms each step.
- **Steps are numbered continuously across the whole run, starting at 0**, in the order a human
  would sit down and work through them — not grouped by `[TASK]`, not restarted per section.
  **Step 0 is the setup** a tester does once before anything else: the branch to check out, the
  environment to point at, the migration to run. No setup needed → the first real action is step 0.
- **Every step states an expected observable result.** A step whose expected result is "it looks
  right" is not a step — either name what the tester should see, or the change did not earn a step.
- **Every step carries the `[TASK]` it came from**, backticked, space-separated when a step came
  from more than one. The attribution is not optional: a failed step has to route back to the
  `[TASK]` that owns it, and that is the id `manual-qa` lifts into the finding it files.

**Three authoring rules, all measured, all silent when broken:**

- **Ids are backticked.** `` `#12805` `` renders as compact grey code — no chip, no link. A bare
  `#12805` becomes a **full-width chip** *and* silently creates a `Related` link between the two
  work items, so an eight-step comment quietly wires eight relations onto the `[SPEC]` and pushes
  the script off the page. **Exactly one bare mention is permitted**, the `[SPEC]` id in the
  run-context line, where both effects are wanted. The **pull request is never `#NNNN` at all**:
  that shortcut resolves to the *work item* of that number and sends the tester somewhere
  unrelated ([`../_shared/ado-workitem-authoring.md`](../_shared/ado-workitem-authoring.md) §2).
  Link it in full, with `<org>`, the **repo project** and `<repo>` from the adapter.
- **Angle brackets are always `&lt;` / `&gt;`**, escaped at synthesis time, before the body is
  sent (same reference, §1). A raw `<div className="x">` is **stripped to `<div>`** in the comment
  API's read, and `Array<string>` loses `<string>` outright — the sanitiser does **not** respect
  code spans, so backticks save nothing. This is the most bracket-dense body the plugin writes,
  and because `manual-qa` reads the comment, edits one line and writes it back, raw markup in
  *untouched* steps is destroyed on the first tick. The UI renders a comment's **sanitised** text
  rather than its `renderedText` (§8), so the damage reads as a sentence that was always worded
  that way — vanishing text, not visible junk.
- **Fenced code blocks are forbidden.** A fence containing markup comes back **empty**: the step's
  whole expected result is gone, leaving a blank grey box on screen. Put the command inline in a
  code span with its brackets escaped, or state it in prose.

**A deviation earns a place in this comment only if it changes what the tester does**, and where
it lands follows from that: a deviation attached to **one step** folds into that step's
expected-result clause, where the tester meets it at the moment it matters rather than twenty
steps early; a **run-wide** one becomes a `## Before you start` line. Everything else — code-review
notes, observations about the diff, "this table is duplicated in two skills" — goes in the
**pull-request description**. There is deliberately no heading left to park it under.

**Built from two sources, and only two:** each worker's **refined QA notes** (item 4 of the report
contract — these are the steps; the `[TASK]`'s own `## QA notes` are what the worker refined, not a
second source to merge back in), and each worker's **deviation log** (item 3) with the edge cases
it flagged, filtered by the rule above. Nothing else: not the `[SPEC]`'s body, not the `[TASK]`s'
acceptance criteria, not the diff. A QA comment assembled from the artifacts instead of the
reports describes what was *planned*; the reports are the only record of what was actually built.

Then the Azure DevOps mechanics:

- **Post** with `mcp__ado__wit_work_item_comment_write` (`action: "add"`), against the adapter's
  **work-item project** and the `[SPEC]`'s id, passing **`format: "Markdown"`**. Without that flag
  the comment lands as HTML and the headings, checkboxes and code spans this contract is made of
  arrive as literal text.
- **Carry the format forward rather than probing for it.** A read never reports a stored format
  (`../_shared/ado-workitem-authoring.md` §8), so nothing downstream can discover it — every later
  `action: "update"` on this comment, `manual-qa`'s ticks included, must pass `format: "Markdown"`
  again. It is stated here because the writer is the only place that knows.
- **Then tag the `[SPEC]`** `needs-qa`. **Comment first, tag second, always**: the tag is the queue
  signal, and a `[SPEC]` in the queue with no comment under it sends the operator looking for steps
  that do not exist. `System.Tags` is a single semicolon-separated string, so this is a
  read-modify-write — read the `[SPEC]`'s current tags, append `needs-qa`, write the whole list
  back. Writing the tag on its own replaces every tag the item had. Re-tagging an item that
  already carries it is a no-op, which is what makes a second run against the same `[SPEC]` safe.

  ```
  wit_work_item_write  { action: "update", project: <work-item project>,
                          updates: [{ id: <spec-id>, op: "add",
                                      path: "/fields/System.Tags",
                                      value: "<the existing tags>; needs-qa" }] }
  ```

- **Read both back before reporting.** `mcp__ado__wit_work_item` (`action: "list_comments"`) for
  the comment, and a fetch of the `[SPEC]` for `System.Tags`. Same reason every other write in this
  loop is read back: a swallowed failure here leaves a comment nobody is queued to find, or a queue
  entry with nothing under it, and both look exactly like a run that finished cleanly.

### 2. Pull-request body

Replace the placeholder `QA:` line from Setup step 3 with a pointer to the QA comment — or with
the no-QA sentence if none was posted — and bring the task checklist to its final state. Same call
and same **repo project + repository** as every other PR-shaped call
(`mcp__ado__repo_pull_request_write`, `action: "update"`). It stays `isDraft: true`.

**Point at the `[SPEC]`, not at a comment permalink.** The `add` call returns the comment's REST
url, which is not the page a human opens, and this skill has no measured UI anchor for a work-item
comment to compose one from. Name the `[SPEC]` as `AB#<spec-id>` — the same form the body skeleton
from Setup step 3 already uses — and say where the steps are, e.g.
`QA: steps are in the Discussion of AB#12805, which now carries needs-qa`.

**The `[QA]` item's never-link rule is retired, and nothing replaces it.** It said: never attach
the `[QA]` work item to the pull request, because completion options transition every linked work
item and `transitionWorkItems` **defaults to `true`** (*Pull-request wiring*) — so a linked `[QA]`
item would close itself the moment a human completed the PR, a QA pass that marks itself done.
What that rule was protecting was **closure as the receipt**. It is not the receipt any more: the
tick state in the comment is, and a comment survives its work item being closed, untouched.

What auto-close would still cost is the **queue** — a closed item drops off the board — and the
tag is what solves that: a WIQL query on `[System.Tags] CONTAINS 'needs-qa'` returns the `[SPEC]`
**regardless of state**. So the two fields stop having to lie to each other: `System.State`
answers *is the code done*, the tag answers *has a human tested it*. Attach `[TASK]`s and the
`[SPEC]` to the PR exactly as *Pull-request wiring* says, and there is no third thing to keep off
it.

### 3. Final summary to the human

Printed to the session — the loop writes no status feed to the tracker. Report:

- `[TASK]`s **done** (id, title) · **skipped** (id, and why: unmet `## External steps`, blocked by
  something outside this spec) · **failed** (id, and the gist of the escalation comment).
- **Deviations worth reading** — from the workers' deviation logs, the ones that change what a
  reviewer or tester should expect. Not every line; the QA comment carries the tester-facing ones.
- **Escalations** — anything that paused the run, and anything still waiting on a human.
- The **QA comment** — that it was posted on the `[SPEC]`, and that the `[SPEC]` now carries
  `needs-qa` — or the explicit "no QA comment: nothing in this run is manually testable", with the
  reason.
- The **pull request, left open and still a draft**, with its url: it is completed by hand after
  QA (verify ladder L5), and completing it is what transitions the `[TASK]`s.

Everything in *What the loop must not write* still holds at the end: do not complete the pull
request, do not close the `[SPEC]`, do not remove the `needs-qa` tag you just applied, do not
reply to your own comment marking the pass done — the human who runs it owns both, and they are
the only record in the tracker that it was ever run — and write no field of the parent.

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
