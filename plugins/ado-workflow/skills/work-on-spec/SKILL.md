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
either tracker any more and names no QA path: this loop's whole QA output is a **`needs-qa` tag on
the `[SPEC]`** plus a printed `ado-workflow:manual-qa` invocation, so it writes no file, creates no
work item and posts no QA comment at all (see *Loop end*).

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
- **The `[SPEC]` takes exactly one other write, at loop end**: the **`needs-qa` tag** (*Loop end*
  §1), written once per run. **No QA comment is posted** — this loop composes no QA pass, and the
  comment it used to write is gone with the template that shaped it; `manual-qa` composes a pass in
  its own session, from the branch. Nothing is ever commented onto the `[SPEC]` by this loop, and
  no progress or per-`[TASK]` commentary goes anywhere near it.
- **No field of the parent work item is ever written.** It is read to walk the spec's siblings
  (per the eligibility mechanics), and for nothing else. Loop end used to re-read it to confirm a
  `[QA]` item's hierarchy link had landed, and before that to lift its **acceptance criteria**
  into a coverage checklist; the `[QA]` item is gone and both reads went with it. Adding a child
  relation to the parent is still allowed and unchanged — a child places it from its own side,
  the way `to-spec-tasks` places a `[TASK]`. No field, no state, no comment: it belongs to
  Product.
- **No status feed.** The loop's only writes to work items are board-state moves on `[TASK]`s, the
  single `[SPEC]` state move above, escalation comments on failed `[TASK]`s, and the `needs-qa`
  tag on the `[SPEC]` at loop end.

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
now the `needs-qa` tag on the `[SPEC]` plus whatever `manual-qa` writes during a pass, and none of
it is touched by the `[SPEC]` being transitioned, so there is nothing left here to keep off the PR
(*Loop end* §2 has the reasoning in full).

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

Three things, in order: the QA handoff, the pull-request body, the final summary.

### 1. The QA handoff — the tag, then the invocation

**Create no work item, commit nothing, and post no QA comment.** This loop no longer composes a QA
pass. `ado-workflow:manual-qa` composes one on demand, in its own session, from what actually landed
on the branch — the diff, the commits and the `AB#<id>` reference each one carries — so a script
written *here*, before the code existed, could only describe what the run planned to make testable.
The loop has moved three times: a committed markdown document, then a per-run `[QA]` work item beside
the `[SPEC]`, then a per-run tickable comment on the `[SPEC]`. It does none of them now, and none of
the machinery any of them needed survives here — no template, no heading rules, no step anchors, no
never-edit rule and no carve-outs from it, no second-run link-back. Loop end's entire QA output is a
tag and a printed line.

- **Tag the `[SPEC]`** `needs-qa` — **iff at least one `[TASK]` in this run reported something a
  human can exercise** (worker report contract, item 4). The tag means **"not yet QA'd"** and
  nothing else: it is the operator's queue, and `manual-qa` is what removes it. A WIQL query on
  `[System.Tags] CONTAINS 'needs-qa'` returns every `[SPEC]` awaiting a pass **regardless of state**,
  so an item the pull request has already transitioned is still in it — which is why the tag, and
  not a state, is the queue. A run of nothing but bumps, config and refactors earns no tag; say so
  in the final summary, so the absence reads as a decision and not a forgotten step.

  `System.Tags` is a single semicolon-separated string, so this is a **read-modify-write**: read the
  `[SPEC]`'s current tags, append `needs-qa`, write the whole list back. Writing the tag on its own
  replaces every tag the item had. Re-tagging an item that already carries it is a no-op, which is
  what makes a second run against the same `[SPEC]` safe.

  ```
  wit_work_item_write  { action: "update", project: <work-item project>,
                          updates: [{ id: <spec-id>, op: "add",
                                      path: "/fields/System.Tags",
                                      value: "<the existing tags>; needs-qa" }] }
  ```

  **Then read `System.Tags` back and confirm** before reporting it applied. Same reason every other
  write in this loop is read back: a swallowed failure leaves a run nobody is queued to test, and
  that looks exactly like a run that finished cleanly.

  **No one-time human precondition on this tracker.** GitHub's `needs-qa` is a **label**, which a
  human must create once before `work-on-prd` can apply it. An Azure DevOps **tag** is created
  implicitly the first time it is used, so there is nothing to arrange in advance and nothing that
  can fail because a vocabulary entry is missing.

- **Print the invocation**, for the human to run when they judge the run worth a pass:

  ```
  /ado-workflow:manual-qa <spec-id>
  ```

**The loop never invokes `manual-qa` itself.** On demand is the only trigger. The developer who just
watched the run is the one who decides whether it warrants a pass, and a driver that starts itself at
loop end is the checklist-nobody-works failure in a new costume.

### 2. Pull-request body

Replace the placeholder `QA:` line from Setup step 3 with the `manual-qa` invocation, and bring the
task checklist to its final state. Same call and same **repo project + repository** as every other
PR-shaped call (`mcp__ado__repo_pull_request_write`, `action: "update"`). It stays `isDraft: true`.

**The `QA:` line is the invocation** — literally `QA: run /ado-workflow:manual-qa <spec-id>`, the
same line §1 printed, with the `[SPEC]` named as `AB#<spec-id>` beside it if the description wants
the chip. Omit the line entirely when §1 applied no tag, and say in the final summary that nothing
in this run is manually testable. **After loop end this line is `manual-qa`'s alone** — the loop
writes it once and never touches it again.

**The workers' deviation logs land here too** — code-review notes, observations about the diff,
edge cases a reviewer should know about — in whichever part of the description takes notes on the
change. They have nowhere else to go: §1 posts nothing.

**The `[QA]` item's never-link rule is retired, and nothing replaces it.** It said: never attach
the `[QA]` work item to the pull request, because completion options transition every linked work
item and `transitionWorkItems` **defaults to `true`** (*Pull-request wiring*) — so a linked `[QA]`
item would close itself the moment a human completed the PR, a QA pass that marks itself done.
What that rule was protecting was **closure as the receipt**. It is not the receipt any more:
`manual-qa`'s free-form receipt comment and the tag it removes are, and neither is touched by the
`[SPEC]` being transitioned.

What auto-close would still cost is the **queue** — a closed item drops off the board — and the
tag is what solves that: a WIQL query on `[System.Tags] CONTAINS 'needs-qa'` returns the `[SPEC]`
**regardless of state**. So the two fields stop having to lie to each other: `System.State`
answers *is the code done*, the tag answers *has a human tested it*. Attach `[TASK]`s and the
`[SPEC]` to the PR exactly as *Pull-request wiring* says, and there is no third thing to keep off
it.

### 3. Final summary to the human

Printed to the session — the loop writes no status feed to the tracker. Filter:
`../_shared/final-prints.md`. Every `[TASK]` that landed is a child on the board and a commit on
the pull request the human is about to open, so the print is **the exceptions plus the handoff**,
never a roll-call of the tickets that worked:

```
Done — 7/9 landed. PR: <url>
Skipped   #12840 — blocked: needs the staging connection string set (your move)
Failed    #12843 — tests never green after 2 attempts; not on branch
Deviated  #12841 — reused the existing export job instead of a new queue; reviewer: check the retry path
Escalation — migration touches prod data, wants sign-off before completion
needs-qa tagged — something exercisable landed.
/ado-workflow:manual-qa <spec-id>
```

Rules for it:

- **Sections print only when non-empty.** A clean run is three lines: the tally, the `needs-qa`
  line, the command.
- **The mapping is exhaustive by contract.** Every worker report carrying a skip, a failure, a
  deviation or an escalation produces exactly **one line** here — one line each, fixed left-edge
  label column. Dropping one because the list ran long is never a conciseness move; that is the
  protected class in the shared filter.
- **The deviation lines are the alert, not the detail.** The workers' full deviation logs are
  already in the pull-request description (§2) — a line here says a reviewer needs to look, and
  where.
- **One URL, and it is the pull request.** Not the `[SPEC]`, not a `[TASK]`, not the branch: the PR
  is what the human opens next, it is left open and still a draft, and completing it by hand after
  QA (verify ladder L5) is what transitions the `[TASK]`s.
- **The QA handoff is a fact plus the command** — `needs-qa tagged`, or the explicit
  `no needs-qa — nothing in this run is manually testable`, with the reason. Then the invocation on
  its own clean line, last thing on screen.

This is a **sibling of `work-on-prd`'s summary, not a shared template**: same shape, ADO's own
dialect throughout — work-item ids where the other has issue numbers, *tagged* where it says
*applied*, `<spec-id>` where it says `#<prd-number>`. Nothing here is generated from the other side
and neither reads the other.

Everything in *What the loop must not write* still holds at the end: do not complete the pull
request, do not close the `[SPEC]`, do not remove the `needs-qa` tag you just applied, do not post
a QA comment or a receipt of any kind — `manual-qa` owns the pass, its receipt and the tag's
removal, and those are the only record in the tracker that it was ever run — and write no field of
the parent.

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
