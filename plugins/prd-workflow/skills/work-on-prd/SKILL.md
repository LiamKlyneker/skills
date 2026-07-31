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

1. **Fetch state**: PRD + children per `../_shared/prd-eligibility.md`. Zero children → tell the user to run `/to-issues` first, stop. Cycle in `Blocked by` → report it, stop.
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

1. **QA doc** at the adapter's QA-doc path: one section per completed issue — what shipped · how to test in the running app (issue `## QA notes` refined by the worker's report) · edge cases the worker flagged. Commit it to the branch, push.
2. **PR body**: link the QA doc, final checklist state.
3. **Final summary** to the human: issues done / skipped / failed · deviations worth reading · escalations. Leave the PR open (still draft) for human QA (verify ladder L5: run the QA doc start-to-finish on the branch, then merge manually). The PRD issue is **not** closed by the loop — `Closes` keywords fire on merge.
4. **Release keep-awake** (mirror of Setup step 0; no-op if never started): let the machine sleep again.

   ```bash
   [ -f /tmp/work-on-prd.caffeinate.pid ] && kill "$(cat /tmp/work-on-prd.caffeinate.pid)" 2>/dev/null; rm -f /tmp/work-on-prd.caffeinate.pid
   ```

## Label vocabulary

Normative home for the label vocabulary — `to-issues` and `next-prd-issue` apply/read these; change them here first.

`ready-to-start` (pickable) → `state:in-progress` (claimed) → `state:done-on-branch` (committed, awaiting merge). Merge auto-closes via the PR's Closes line. One state per axis; always remove-before-add. Precondition (one-time, human): the repo setting "auto-close issues with merged linked pull requests" must be on — see the adapter.
