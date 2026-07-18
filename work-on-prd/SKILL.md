---
name: work-on-prd
description: Orchestrate a whole PRD end-to-end — pick each child issue, spawn a fresh worker subagent per issue, verify, commit, maintain one PR — pausing per the chosen gate. Use when the user says "work on PRD #N", "run the PRD", or passes /work-on-prd a PRD number/URL. Re-entrant — the same command cold-starts and resumes.
---

# Work On PRD

Run a whole PRD in one session: orchestrator (this session's model) + one fresh worker subagent per child issue. The human stays in the creative loop (grill / PRD / issues) and the QA gate.

Project facts (repo, commands, verify ladder, QA-doc convention) come from `../_shared/project-adapter.md` — read it first; never hardcode project specifics in this skill.

## Invocation

`/work-on-prd #N [--gate=issue|events|end]`

- `#N` — PRD issue (number, `#N`, or URL; strip query strings). One PRD per loop — no parallel PRDs in v1.
- `--gate` (default `issue`):
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

1. **Fetch state**: PRD + children per `../_shared/prd-eligibility.md`. Zero children → tell the user to run `/to-issues` first, stop. Cycle in `Blocked by` → report it, stop.
2. **Branch** `prd/<n>-<slug>` (slug from the PRD title): check out if it exists (local or remote), else create from up-to-date `main`.
3. **PR** (one per PRD, targets `main` — required for `Closes` to fire): if none exists for the branch, push (empty commit `prd #N: loop start` if the branch has no commits ahead) and open a **draft PR**. Body skeleton:

   ```
   Runs PRD #<n>: <title>

   ## Children
   - [ ] #<c1> <title>
   - [ ] #<c2> <title>

   Closes line: (accumulated as issues land)

   QA doc: (added at loop end)

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

4. **Reconstruct**: an issue is done ⇔ a commit referencing `(#N)` exists on the branch. Labels/PR body are cache, not truth — repair them to match commits if drifted (check off children, fix labels).
5. **Stale claim** (`state:in-progress` label but no matching commit — a previous run died mid-issue): discard uncommitted work (`git reset --hard && git clean -fd`, PRD branch only), remove `state:in-progress`, re-add `ready-to-start`. The issue restarts with a fresh worker via the normal pick path — no partial-work recovery, re-entrancy not recovery.

## Loop (per issue)

1. **Pick** the next eligible child per `../_shared/prd-eligibility.md` (open ∧ blockers closed; picking order as specced) — with one orchestrated-mode relaxation: a blocker **inside this PRD** is also satisfied when its commit exists on the PRD branch (`state:done-on-branch`), since children only close on merge; without this, every `Blocked by` chain would deadlock the loop. None eligible but open blocked children exist → report the blocking chain; if the blockers are outside this PRD, pause for the human. None open at all → go to **Loop end**.
2. **External steps**: any unmet `- [ ]` under `## External steps` → pause, list them, wait for the human. Always, regardless of gate.
3. **Claim**: remove `ready-to-start`, add `state:in-progress` (remove-old-before-add-new — always this order; one state per axis).
4. **Route model**: apply `../_shared/model-effort-heuristics.md` **in orchestrated mode** — the default flips: workers start Sonnet-class and *upgrade* to Opus-class on the file's heavier/risk signals. Announce the routing call (tier + matched signals) before spawning.
5. **Spawn worker**: Agent tool, `general-purpose`, `model` per the routing call, `run_in_background: false`. Flat hierarchy — workers never spawn workers. Isolation is total: everything the worker needs must be in its prompt, the issue, or the repo. Prompt contains:
   - The **full issue body** (incl. `## Worker context`, `## QA notes`, acceptance criteria).
   - The **full contents of `../_shared/project-adapter.md`**.
   - Mandates: read the scoped `CONTEXT.md` before touching files in any directory (repo discipline) · work only on branch `prd/<n>-<slug>` · verify **L2 always** (adapter test command); **L3** (app boot + screenshot) if the issue is marked user-visible · commit **only after verify passes**, message ends with `(#N)` · one commit for the issue (fixups squashed locally before the commit exists; never amend an existing commit) · never push, merge, close issues, or touch labels/PR · max 2 self-fix attempts, each announced.
   - The **report contract**: ① what shipped · ② verify evidence (actual test/build output) · ③ deviation log — every place the implementation diverged from the issue spec and why · ④ refined QA notes (concrete steps for the QA doc) · ⑤ or an honest "could not finish X because Y" with attempts announced. No report theater — evidence over prose.
6. **Judge the report**: commit exists on branch · verify evidence is real (spot-check: re-run the L2 command if evidence looks thin) · deviations acceptable · AC covered.
7. **Gate** per `--gate` mode (see Invocation). On pause: present the report + your judgement, wait for the human.
8. **Success path**: push the branch → labels: remove `state:in-progress`, add `state:done-on-branch` → PR body: check the child off + append to the Closes line with the **keyword repeated per issue** — `Closes #41, closes #42` (a bare `#42` after a comma does NOT close).
9. **Failure path** (worker exhausted its 2 attempts, or report judged unacceptable): discard uncommitted work (reset/clean, branch only) → backward label transition: remove `state:in-progress`, re-add `ready-to-start` (failure is a backward transition, not a new label) → post an **escalation comment** on the issue: what was tried, what failed, evidence → pause per gate (`issue`/`events` pause; `end` records and continues) → increment the consecutive-failure counter; at 2, full stop with summary. A success resets the counter. A failed issue is not re-picked in this run unless the human unblocks it.

## Loop end (no eligible children left)

1. **QA doc** at the adapter's QA-doc path: one section per completed issue — what shipped · how to test in the running app (issue `## QA notes` refined by the worker's report) · edge cases the worker flagged. Commit it to the branch, push.
2. **PR body**: link the QA doc, final checklist state.
3. **Final summary** to the human: issues done / skipped / failed · deviations worth reading · escalations. Leave the PR open (still draft) for human QA (verify ladder L5: run the QA doc start-to-finish on the branch, then merge manually). The PRD issue is **not** closed by the loop — `Closes` keywords fire on merge.
4. **Release keep-awake** (mirror of Setup step 0; no-op if never started): let the machine sleep again.

   ```bash
   [ -f /tmp/work-on-prd.caffeinate.pid ] && kill "$(cat /tmp/work-on-prd.caffeinate.pid)" 2>/dev/null; rm -f /tmp/work-on-prd.caffeinate.pid
   ```

## Label vocabulary

`ready-to-start` (pickable) → `state:in-progress` (claimed) → `state:done-on-branch` (committed, awaiting merge). Merge auto-closes via the PR's Closes line. One state per axis; always remove-before-add. Precondition (one-time, human): the repo setting "auto-close issues with merged linked pull requests" must be on — see the adapter.
