---
name: work-on-prd
description: Orchestrate a whole PRD end-to-end — pick each child issue, spawn a fresh worker subagent per issue, verify, commit, maintain one PR — pausing per the chosen gate. Use when the user says `work on PRD` with a number, or `run the PRD`, or passes /work-on-prd a PRD number/URL. Re-entrant — the same command cold-starts and resumes.
---

# Work On PRD

Run a whole PRD in one session: orchestrator (this session's model) + one fresh worker subagent per child issue. The human stays in the creative loop (grill / PRD / issues) and the QA gate.

Project facts (repo, title prefixes, commands, verify ladder) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it first; never hardcode project specifics in this skill.

`[PRD]`, `[TASK]`, `[BUG]` and `[QA]` below are **shorthand for the adapter's *Title prefixes* row**, written out for readability. If that row names different prefixes, they win — here, in every title filter this skill applies, and in the prefix it strips before slugging the branch.

## Invocation

`/work-on-prd #N [--gate=issue|events|end]`

**Invocation name depends on the install route.** From a plugin (marketplace install or a
skills-dir link) every skill in this plugin is namespaced: `/prd-workflow:work-on-prd`,
`/prd-workflow:to-issues`, and so on. Only a bare symlink into a config's `skills/`
directory — the pre-plugin route — gives the unprefixed `/work-on-prd`. The same rule
governs the agent type; see Loop step 5. Unprefixed names below are shorthand for
whichever form your route provides.

- `#N` — PRD issue (number, `#N`, or URL; strip query strings). One PRD per loop — no parallel PRDs in v1.
- `--gate` (default `events`):
  - `issue` — pause for human approval after every worker report.
  - `events` — run free; pause only on: verify failure after retries · deviation from spec · destructive/irreversible action · ambiguity.
  - `end` — pause only at QA (loop end).
  - Graduation path: issue → events → end.
- **Regardless of gate**: an issue with unmet `## External steps` always pauses and asks the human.

## Non-negotiables (circuit breakers)

- Max **2 self-fix attempts** per worker; attempts must be announced in the worker report.
- **2 consecutive failed issues** → full stop with summary.
- **Never** force-push, amend, or rewrite published history. **Never** merge the PR. **Never** close the PRD issue.
- `git reset --hard` / `git clean` only ever on the PRD branch, only to discard a stale claim's uncommitted work.

## Setup (idempotent — cold start and resume are the same code path)

State lives in git + GitHub only (branch commits, issue labels, PR body). Zero session-resident state: killing the session loses nothing but uncommitted worker output, which is discarded by design.

0. **Keep-awake** (local-Mac convenience only; no-op elsewhere): prevent the machine from sleeping through the long run. Idempotent — safe on resume, never stacks a second process; guarded so it silently does nothing where `caffeinate` is absent (Linux server/CI).

   ```bash
   command -v caffeinate >/dev/null && ! pgrep -F /tmp/work-on-prd.caffeinate.pid >/dev/null 2>&1 && { caffeinate -dimsu & echo $! > /tmp/work-on-prd.caffeinate.pid; }
   ```

1. **Fetch state**: PRD + children per `../_shared/prd-eligibility.md` — the children are the PRD's **native sub-issues**, read back in one `gh api …/sub_issues` call. Everything that call returns is a child by construction: there are no filters, so nothing is dropped and there is nothing to report as dropped. Zero children → **nothing is linked to this PRD**, which is not the same as "never sliced". Stop, and tell the user to link the PRD's children as sub-issues — explicitly **do not** tell them to re-run `/to-issues`, and say so: re-slicing a PRD that already has children doubles every one of them, and that plausible-sounding message is the expensive wrong move this branch exists to prevent. Cycle in `Blocked by` → report it, stop.
2. **Branch** `prd/<n>-<slug>`: check out if it exists (local or remote), else create from up-to-date `main`.

   The slug comes from the PRD title **with the `[PRD]` prefix stripped first** — slug
   `extract-lk-plugin`, never `prd-extract-lk-plugin`. This is the whole reason the strip is
   specced rather than assumed: a PRD that gains the prefix while a run is in flight computes a
   *different* branch name than the one its work is on, so the resume opens a second branch and
   a second PR, Setup step 4 finds zero commits on it, and every landed issue is re-run from
   scratch. Nothing errors. Strip any leading `[…]` bracket group, not the literal string
   `[PRD]`, so an adapter that names a different prefix is handled too.
3. **PR** (one per PRD, targets `main` — required for `Closes` to fire): if none exists for the branch, push (empty commit `prd #N: loop start` if the branch has no commits ahead) and open a **draft PR**. Body skeleton:

   ```
   Runs PRD #<n>: <title>

   ## Children
   - [ ] #<c1> <title>
   - [ ] #<c2> <title>

   Closes line: (accumulated as issues land)

   QA: (added at loop end)

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

4. **Reconstruct**: an issue is done ⇔ a commit referencing `(#N)` exists on the branch. Labels/PR body are cache, not truth — repair them to match commits if drifted (check off children, fix labels).
5. **Stale claim** (`state:in-progress` label but no matching commit — a previous run died mid-issue): discard uncommitted work (`git reset --hard && git clean -fd`, PRD branch only), remove `state:in-progress`, re-add `ready-to-start`. The issue restarts with a fresh worker via the normal pick path — no partial-work recovery, re-entrancy not recovery.

## Loop (per issue)

1. **Pick** the next eligible child per `../_shared/prd-eligibility.md` (open ∧ blockers closed; picking order as specced) — with one orchestrated-mode relaxation: a blocker **inside this PRD** is also satisfied when its commit exists on the PRD branch (`state:done-on-branch`), since children only close on merge; without this, every `Blocked by` chain would deadlock the loop. None eligible but open blocked children exist → report the blocking chain; if the blockers are outside this PRD, pause for the human. None open at all → go to **Loop end**.
2. **External steps**: any unmet `- [ ]` under `## External steps` → pause, list them, wait for the human. Always, regardless of gate.
3. **Claim**: remove `ready-to-start`, add `state:in-progress` (remove-old-before-add-new — always this order; one state per axis).
4. **Route model**: apply `../_shared/model-effort-heuristics.md` **in orchestrated mode** — the default flips: workers start Sonnet-class and *upgrade* to Opus-class on the file's heavier/risk signals. Announce the routing call (tier + matched signals) before spawning.
5. **Spawn worker**: Agent tool, `subagent_type: prd-workflow:prd-worker` (see *Agent type by route* below), `model` per the routing call, `run_in_background: false`. Flat hierarchy — workers never spawn workers. Isolation is total: everything the worker needs must be in its prompt, the issue, or the repo. The **mandates and the report contract live in `../../agents/prd-worker.md`** — never restate them in the prompt, which carries only the per-call inputs:
   - The **full issue body** (incl. `## Worker context`, `## QA notes`, acceptance criteria).
   - The **full contents of the project adapter** (path at the top of this skill). The adapter only; a gate it registers goes in the prompt **only** when this issue triggers it — pasting every gate into every worker is the tax that keeps gates out of the adapter in the first place.
   - The **branch name** `prd/<n>-<slug>` and the **issue number** for the `(#N)` commit suffix.
   - The **routing call** you announced in step 4.

   **Agent type by route — get this right before you fall back.** A plugin namespaces every component it provides, so installed from the marketplace *or* linked as a skills-dir plugin the type is **`prd-workflow:prd-worker`**. Only a hand-placed `.claude/agents/prd-worker.md` (the pre-plugin route) registers the bare `prd-worker`. Try the namespaced name first and the bare name second; treating the bare name as primary is what silently produced a whole run of `general-purpose` workers once already.

   *Detachable — expect to need this*: `prd-worker` is project-scoped, and registration lags. A file added to an agents directory that already existed resolves after a few minutes; a **newly created** `.claude/agents/` does not resolve at all for the rest of the session, and a plugin enabled mid-session does not register its agents until the next session. So if **neither** type name resolves, do not wait and retry — read `../../agents/prd-worker.md` and paste its body (everything below the frontmatter) into a `general-purpose` agent for the whole run. Same contract, one source of truth. **Announce which of the three paths the run took** — namespaced, bare, or detached — because a detached run looks identical to a real one in the output, and that is the only signal that the agent did not resolve.
6. **Judge the report**: commit exists on branch · verify evidence is real (spot-check: re-run the L2 command if evidence looks thin) · deviations acceptable · AC covered.
7. **Gate** per `--gate` mode (see Invocation). On pause: present the report + your judgement, wait for the human.
8. **Success path**: push the branch → labels: remove `state:in-progress`, add `state:done-on-branch` → PR body: check the child off + append to the Closes line with the **keyword repeated per issue** — `Closes #41, closes #42` (a bare `#42` after a comma does NOT close).
9. **Failure path** (worker exhausted its 2 attempts, or report judged unacceptable): discard uncommitted work (reset/clean, branch only) → backward label transition: remove `state:in-progress`, re-add `ready-to-start` (failure is a backward transition, not a new label) → post an **escalation comment** on the issue: what was tried, what failed, evidence → pause per gate (`issue`/`events` pause; `end` records and continues) → increment the consecutive-failure counter; at 2, full stop with summary. A success resets the counter. A failed issue is not re-picked in this run unless the human unblocks it.

## Loop end (no eligible children left)

Three things, in order: the `[QA]` issue, the PR body, the final summary.

### 1. The `[QA]` issue — one per *run*

**Commit nothing.** This loop used to write a markdown document to a path in the adapter and commit it to the branch; it no longer does, and the adapter no longer names a path. Read `../_shared/qa-item.md` — it is normative for one-per-run, what earns a step, the nothing-testable rule, the body, step numbering and the two sources it is built from. Everything below is the GitHub mechanics that document deliberately leaves to this skill.

- **Create** with `gh issue create` against the adapter's issue-tracker repo.
- **Title**: `[QA] PRD #<n> — <the PRD title, prefix stripped>`. Two runs on the same PRD produce two issues with the same title; that is fine and expected, they differ by number and creation time. Never edit or reuse an earlier one to avoid a duplicate.
- **Run context line**: the branch, the PR, and how many issues landed — e.g. ``Branch `prd/52-extract-lk-plugin` · PR #63 · 9 issues landed``.
- **Ids in the body** are bare `#N` — GitHub autolinks them to issues in this repo, which is exactly where a tester needs to land.
- **Never linked to the PRD as a sub-issue**, and no `## Parent` section, no `ready-to-start`, no `state:*` label. The sub-issue link is the *only* thing child discovery reads (`../_shared/prd-eligibility.md`), so simply not writing one is what keeps the QA issue off the pick path — permanently and by construction, since `gh issue create` links nothing on its own. The three omissions are the second layer, for anything reading the issue by hand.
- **It never appears in the PR's `Closes` line.** This is the merge-survival invariant in `../_shared/qa-item.md`, and on GitHub the lever is that one line: a `Closes #N` naming the QA issue auto-closes the QA pass the moment the branch merges, before anybody runs it. The step below writes a `#N` into the PR body a few characters from a keyword that would do exactly that — link it under `QA:`, never after a closing keyword, and never let the QA number join the accumulated `Closes` list.

### 2. PR body

Replace the placeholder `QA:` line from Setup step 3 with a link to the `[QA]` issue — or with the no-QA sentence if none was created — and bring the children checklist to its final state. The PR stays a draft.

### 3. Final summary

To the human: issues done / skipped / failed · deviations worth reading · escalations · the `[QA]` issue by number and url, or the explicit "no `[QA]` issue created: nothing in this run is manually testable" with the reason. Leave the PR open (still draft) for human QA (verify ladder L5: run the `[QA]` issue start-to-finish against the branch, then merge manually). The PRD issue is **not** closed by the loop — `Closes` keywords fire on merge. Do not close the `[QA]` issue you just created; the human who runs it closes it.

Then release keep-awake — mirror of Setup step 0, no-op if never started:

```bash
[ -f /tmp/work-on-prd.caffeinate.pid ] && kill "$(cat /tmp/work-on-prd.caffeinate.pid)" 2>/dev/null; rm -f /tmp/work-on-prd.caffeinate.pid
```

## Label vocabulary

Normative home for the label vocabulary — `to-issues` and `next-prd-issue` apply/read these; change them here first.

`ready-to-start` (pickable) → `state:in-progress` (claimed) → `state:done-on-branch` (committed, awaiting merge). Merge auto-closes via the PR's Closes line. One state per axis; always remove-before-add. Precondition (one-time, human): the repo setting "auto-close issues with merged linked pull requests" must be on — see the adapter.
