---
name: work-on-prd
description: Orchestrate a whole PRD end-to-end — pick each child issue, spawn a fresh worker subagent per issue, verify, commit, maintain one PR — pausing per the chosen gate. Use when the user says `work on PRD` with a number, or `run the PRD`, or passes /work-on-prd a PRD number/URL. Re-entrant — the same command cold-starts and resumes.
---

# Work On PRD

Run a whole PRD in one session: orchestrator (this session's model) + one fresh worker subagent per child issue. The human stays in the creative loop (grill / PRD / issues) and the QA gate.

Project facts (repo, title prefixes, commands, verify ladder) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it first; never hardcode project specifics in this skill.

`[PRD]`, `[TASK]` and `[BUG]` below are **shorthand for the adapter's *Title prefixes* row**, written out for readability. If that row names different prefixes, they win — here, in every title filter this skill applies, and in the prefix it strips before slugging the branch. This loop creates no titled QA issue, so the row's QA prefix is not one of the names it uses.

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

Three things, in order: the QA comment, the PR body, the final summary.

### 1. The QA comment — one per *run*

**Commit nothing, and create no issue.** The QA artifact is a **comment on the PRD issue**, plus the **`needs-qa` label on the PRD**. This loop has moved twice: it once wrote a markdown document to a path in the adapter and committed it to the branch, then it filed a standalone `[QA]` issue. It does neither now — the adapter names no path, and **no `[QA]` issue is created on GitHub any more**. Everything below is normative and is this skill's own — the shape of the comment and the GitHub mechanics both. `work-on-spec` files a `[QA]` **work item** against Azure DevOps (`ado-workflow`'s `skills/references/qa-item.md`); the two loops are siblings, not a shared file and two call sites, and they have deliberately diverged here — this change is GitHub's alone and none of it carries across. The only consumer is the person running QA: **no skill parses this comment**, and nothing reads a previous run's except the second-run link below, so "normative" means the section order, the sources and the earning rule are fixed — not that a parser depends on the wording.

**Why a comment, and what it costs.** The operator filters the issue list on `needs-qa` and gets one queue: every PRD awaiting a manual pass. They open the PRD, and the steps sit directly beneath the natively-rendered sub-issue list — next to the children they describe, in the one place a reader of the PRD already is. What that costs is the **closable receipt**. A closed `[QA]` issue was proof the pass had been run; a comment has no closable state, so nothing in the tracker records completion. That loss is accepted deliberately, not overlooked: **removing `needs-qa` is what "done" looks like**, a human action nothing enforces, and the operator may reply to the comment to record the pass — convention, not machinery, and no skill checks for it. Do not add anything to simulate the receipt.

**One per run, never one per PRD.** A run covers exactly the slice of children that just landed. A second run against the same PRD posts a **second comment** and **never edits the first**. That is the whole point of a per-run artifact rather than a committed document: a document at a fixed path accumulates every run's output, goes stale silently, and gives the human no way to tell which half they already tested. A per-run comment describes one testable slice.

**Posting while `needs-qa` is still applied → link back first.** The label already being on the PRD means an earlier pass is **outstanding** — nobody has worked it yet. The new comment's **first line is a permalink to that earlier comment**, so an outstanding pass is never silently buried under a fresher one. Still one comment per run, still never edit or delete the earlier one, and leave the label where it is (re-applying it is a no-op). Find the earlier one with the newest comment carrying the template's `## Steps` heading, which is present in every QA comment by construction:

```bash
gh api repos/<owner>/<repo>/issues/<n>/comments --jq '[.[] | select(.body | contains("## Steps"))] | last | .html_url'
```

**What earns a step.** A landed child earns a step **only if a human can exercise it in the running app**. Dependency bumps, config changes, pure refactors, internal-only work and setup contribute **nothing**: no step, and **no standalone "nothing to test here" line, paragraph or section**. Those lines are the entire reason the committed documents this replaces reached 440 lines — every landed issue earned a section whether or not anybody could act on it, so the sections that mattered were buried among the ones that didn't. Such a child gets its **one line in `## What landed`** and nothing more; that line may carry a short parenthetical — `(nothing to test by hand)`, a few words, inline — and that is the *only* form the idea is allowed to take. The moment it becomes its own line or section, the rule has been broken. Applied honestly, most runs produce a comment far shorter than the list of things they landed. That is the intended shape, not a sign something was missed.

**Nothing testable in the whole run → post nothing and label nothing.** If **no** child in the run produced anything a human can exercise, there is no comment and no `needs-qa` — an empty QA comment is worse than none, being a thing a person has to open and read in order to learn nothing, and a label pointing at it puts a PRD in the queue that has no pass to run. Say so explicitly, in both places the comment would otherwise have been linked: the **final summary** ("no QA comment: nothing in this run is manually testable", plus the list of children the run landed), and the **pull request body**, where the `QA:` line would have gone — the same sentence. Silence in either place reads as a forgotten step rather than a decision.

**The body:**

<qa-template>

<first line only when `needs-qa` is already applied: Earlier QA pass still outstanding: <permalink to it>>

<one line of run context: the branch, the pull request, how many children landed>

## What landed

- <id> — <one line on what shipped>  (nothing to test by hand)

## Before you start

- <the thing that will look broken and is not, and why>

## Steps

1. <action to take in the running app> → expect <the observable result>  (<id>)
2. <action> → expect <result>  (<id>)

## Gotchas

- <edge case or deviation a worker flagged, and what it means for the tester>  (<id>)

</qa-template>

The rules governing that template are deliberately written **outside** the fence. Copy the fence, not this prose — instructions pasted inside a body template ship to the reader as comment text.

- **`## Before you start` is conditional.** Include it only when something will look broken and is not — a dangling symlink a later child repairs, a migration the tester has to run first, a feature flag that is off. **Omit the heading entirely** otherwise. A "None" under it is the 440-line habit in miniature.
- **`## Gotchas` is conditional** the same way. No deviations and no flagged edge cases means no heading.
- **`## Steps` is always present** — a QA comment exists because at least one child earned a step, so it always has content by construction.
- **`## What landed` lists only the children that earned no step**, one line each with the inline parenthetical, and is **conditional**: every child earned a step → omit the heading entirely. It is not a manifest of the run. The section existed so a reader could see something shipped and not go hunting for a step it never had, and the PRD's native sub-issue list — rendered directly above this comment, completion state and all — now does that job for everything else.
- **Steps are numbered continuously across the whole run**, in the order a human would sit down and work through them, not grouped by child and not restarted per section.
- **Every step carries the id of the child it came from**, so a failure routes straight back to the issue that caused it.
- **Every step states an expected observable result.** A step whose expected result is "it looks right" is not a step — either name what the tester should see, or the change did not earn a step in the first place.

**Built from two sources, and only two:** each worker's **refined QA notes** (item 4 of the report contract — these are the steps; the child's own `## QA notes` are what the worker refined, not a second source to merge back in), and each worker's **deviation log** (item 3) with the edge cases it flagged — these are the gotchas, and they are what `## Before you start` is built from when it appears at all. Nothing else: not the PRD's body, not the children's acceptance criteria, not the diff. A QA comment assembled from the artifacts instead of the reports describes what was *planned*; the reports are the only record of what was actually built.

Then the GitHub mechanics:

- **Post** with `gh issue comment <prd-number> --body-file <path>` against the adapter's issue-tracker repo. Write the body to a file first — `--body` on a shell line mangles a multi-line markdown body, and this one is all headings and lists.
- **Capture the permalink it prints.** `gh issue comment` writes the new comment's url to stdout; that url is what §2 puts in the PR body and §3 reports, and what a later run links back to.
- **Then label the PRD** `needs-qa` — `gh issue edit <prd-number> --add-label needs-qa`. Comment first, label second, always: the label is the queue signal, and a PRD in the queue with no comment under it sends the operator looking for steps that do not exist. Applying a label the PRD already carries is a no-op, which is what makes the second-run path above safe.
- **The label must already exist in the repo.** The loop applies it and cannot create it; `gh issue edit --add-label` against a missing label fails loudly, but a run that swallows that failure leaves a comment nobody is queued to find. It is a one-time human precondition — see the adapter.
- **Run context line**: the branch, the PR, and how many issues landed — e.g. ``Branch `prd/52-extract-lk-plugin` · PR #63 · 9 issues landed``.
- **Ids in the body** are bare `#N` — GitHub autolinks them to issues in this repo, which is exactly where a tester needs to land.

### 2. PR body

Replace the placeholder `QA:` line from Setup step 3 with the **permalink to the QA comment** — the url §1 captured, not an issue number — or with the no-QA sentence if no comment was posted, and bring the children checklist to its final state. The PR stays a draft.

### 3. Final summary

To the human: issues done / skipped / failed · deviations worth reading · escalations · the **QA comment permalink** and the note that the PRD now carries `needs-qa`, or the explicit "no QA comment: nothing in this run is manually testable" with the reason. Leave the PR open (still draft) for human QA (verify ladder L5: work the QA comment start-to-finish against the branch, then merge manually). The PRD issue is **not** closed by the loop — `Closes` keywords fire on merge. Do not remove `needs-qa` and do not reply to your own comment marking the pass done: the human who runs it owns both, and those are the only signals that it was ever run.

Then release keep-awake — mirror of Setup step 0, no-op if never started:

```bash
[ -f /tmp/work-on-prd.caffeinate.pid ] && kill "$(cat /tmp/work-on-prd.caffeinate.pid)" 2>/dev/null; rm -f /tmp/work-on-prd.caffeinate.pid
```

## Label vocabulary

Normative home for the label vocabulary — `to-issues` and `next-prd-issue` apply/read these; change them here first.

`ready-to-start` (pickable) → `state:in-progress` (claimed) → `state:done-on-branch` (committed, awaiting merge). Merge auto-closes via the PR's Closes line. One state per axis; always remove-before-add. Precondition (one-time, human): the repo setting "auto-close issues with merged linked pull requests" must be on — see the adapter.

Two families, and the difference is who clears the label. **`state:*` is machine state**: the loop applies it, the loop removes it, and a human touching one only confuses the reconstruction in Setup step 4. **`needs-*` means a human owes something** and only a human clears it — `needs-triage` on an untriaged issue, and **`needs-qa` on a PRD whose run has posted a QA comment** (Loop end §1). That is why `needs-qa` is not `state:qa-pending`: the loop applies it and then has no further business with it, and the operator's queue is exactly the set of PRDs carrying it. The loop never removes `needs-qa`, on this run or any later one.
