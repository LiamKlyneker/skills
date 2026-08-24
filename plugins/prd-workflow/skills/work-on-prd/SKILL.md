---
name: work-on-prd
description: Orchestrate a whole PRD end-to-end — pick each child issue, spawn a fresh worker subagent per issue, verify, commit, maintain one PR — pausing per the chosen gate. Use when the user says `work on PRD` with a number, or `run the PRD`, or passes /work-on-prd a PRD number/URL. Re-entrant — the same command cold-starts and resumes.
---

# Work On PRD

Run a whole PRD in one session: orchestrator (this session's model) + one fresh worker subagent per child issue. The human stays in the creative loop (grill / PRD / issues) and the QA gate.

Project facts (repo, title prefixes, commands, verify ladder) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it first; never hardcode project specifics in this skill.

`[PRD]`, `[TASK]` and `[BUG]` below are **shorthand for the adapter's *Title prefixes* row**, written out for readability. If that row names different prefixes, they win. This skill applies **no title filter** — the PRD's children are its native sub-issues — so the one place the row is mechanically load-bearing is the prefix stripped before slugging the branch (Setup step 2). Everywhere else the prefixes are a human scanning convention.

## Invocation

`/work-on-prd #N [--gate=issue|events|end]`

**Every skill in this plugin is namespaced**, on every route — installed from the
marketplace or loaded with `claude --plugin-dir`: `/prd-workflow:work-on-prd`,
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

**The run's identity is its pull request, not its branch name.** Step 1 finds the run by searching open PR bodies for the machine block's `PRD: #<n>` line, and every step after it works on whatever branch that PR points at. No step recomputes a name in order to *find* a run — see `## The machine block` for the contract, and Setup step 2 for why that makes the branch name cosmetic.

0. **Keep-awake** (local-Mac convenience only; no-op elsewhere): prevent the machine from sleeping through the long run. Idempotent — safe on resume, never stacks a second process; guarded so it silently does nothing where `caffeinate` is absent (Linux server/CI).

   ```bash
   command -v caffeinate >/dev/null && ! pgrep -F /tmp/work-on-prd.caffeinate.pid >/dev/null 2>&1 && { caffeinate -dimsu & echo $! > /tmp/work-on-prd.caffeinate.pid; }
   ```

1. **Fetch state**: PRD + children per `../_shared/prd-eligibility.md` — the children are the PRD's **native sub-issues**, read back in one `gh api …/sub_issues` call. Everything that call returns is a child by construction: there are no filters, so nothing is dropped and there is nothing to report as dropped. Zero children → **nothing is linked to this PRD**, which is not the same as "never sliced". Stop, and tell the user to link the PRD's children as sub-issues — explicitly **do not** tell them to re-run `/to-issues`, and say so: re-slicing a PRD that already has children doubles every one of them, and that plausible-sounding message is the expensive wrong move this branch exists to prevent. Cycle in `Blocked by` → report it, stop.

   **Then find the run, and find it by its pull request.** A run *is* its open PR: that PR's body
   carries the machine block, and the block carries a literal `PRD: #<n>` line (`## The machine
   block` below is the contract). One search over open PR bodies therefore answers both questions at
   once — is this a resume, and which branch is it on:

   ```bash
   gh pr list --repo <owner>/<repo> --state open --limit 500 --json number,headRefName,body \
     --jq '[.[] | select(.body | test("(^|\n)PRD: #<n>[ \t\r]*(\n|$)"))] | .[] | {number, headRefName}'
   ```

   **Match the whole line, never a substring.** `PRD: #12` is a prefix of `PRD: #127`, so a bare
   `contains` can resume the wrong run — and a wrong-run resume lands this PRD's commits on another
   PRD's branch and closes that PRD's children on merge. Anchor on the line, as above. Raise
   `--limit` above the repo's open-PR count: a truncated list is a silent miss, and a silent miss is
   exactly the duplicate branch and duplicate PR this design exists to remove. **Two matches → stop
   and report** both PR numbers; two open PRs claiming one PRD is a state no run should extend.

   **One hit → this is a resume.** Take that PR's `headRefName` as the branch — whatever it is
   called, including a name the adapter's pattern would never produce and a name a human renamed by
   hand after the fact. Check it out, skip step 2, skip step 3's open, go to step 4.

   **No hit → no run exists yet**, with one transitional exception below. There is **no
   name-recompute fallback**, and there is not going to be one: a crash between creating the branch
   and opening the PR orphans at most one empty branch, and that is accepted cheerfully as the price
   of never guessing at a name again.

   **Legacy adoption — the one transitional exception, written to be deleted.** A run that started
   before the machine block existed has a PR with no `PRD: #<n>` line in it, so the search misses it
   and a plain cold start would open a second branch and a second PR on top of live work. So on the
   **miss path only**, check once for the name the loop used to compute before the adapter row
   existed: `prd/<n>-<slug>` — the old default, **not** the adapter's pattern, because a legacy run
   predates the row. If that branch exists (local or remote), or an open PR has it as head:

   - **Adopt it exactly as it is.** Keep the branch name; do not rename it to what the pattern would
     now yield. The name is cosmetic, and renaming breaks nothing except every link a human already
     has.
   - **Retrofit the machine block** into that PR's body — append it, per `## The machine block` —
     reconstructing its checklist and `Closes` line from the branch's commits in step 4 rather than
     trusting whatever the old body said.
   - Branch but no PR → that is step 3's open, on the existing branch.
   - Then resume normally, and **announce that you adopted a legacy run**, under which name.

   **This rule fires at most once per legacy run**, because the first resume leaves the block in the
   body and every resume after that is found by the ordinary search. It ages out on its own as
   in-flight runs finish, and it is **meant to be deleted**: nothing depends on it, and a run that
   never needed it never enters this path. Delete it once no run predating the block can still be in
   flight.

2. **Branch**: name it from the adapter's optional **`Branch pattern:`** row, in the `### GitHub`
   sub-section of `## Repo`. Check the resulting name out if it exists (local or remote), else
   create it from up-to-date `main` — subject to the collision guard below. One branch per PRD, on
   a cold start and on a resume alike.

   **Step 1 may have handed you the branch already, and then none of this step runs.** A run found
   by its PR — or adopted as legacy — arrives with its branch name attached, whatever that name is;
   check it out and go on to step 4. Everything below is how a branch gets **created**, on a genuine
   cold start, and no name is ever recomputed for a run that already exists. That is what makes the
   adapter's claim that this row is purely cosmetic literally true, and it is worth naming the one
   path that looks like a counter-example: **Setup step 4 still reads commits on the branch**, but it
   reads them on the branch step 1 handed it, deriving *what landed* rather than *which run this is*.
   Nothing resolves a run by its name.

   **An absent row means `prd/<n>-<slug>`**, byte-for-byte the name every run used before the row
   existed. Absent is the common case and a finished answer; nothing warns about it. Present, the
   row is a pattern written in the adapter's own placeholder notation, and you substitute exactly
   two tokens into it: **`<n>`**, the PRD's issue number, and **`<slug>`**, its title slugged.
   **Both are optional** — a pattern naming neither, like `release`, is legal and yields that
   literal name. Substitute nothing else: anything else the row contains is part of the name, not
   a placeholder to fill.

   **`<slug>` is the full title, slugged — never truncated.** Lowercase it, collapse every run of
   non-alphanumerics to a single hyphen, drop leading and trailing hyphens, and keep every word.
   Length is not a reason to cut: a half-title slug is how two PRDs end up sharing a branch name,
   and it is the same word that gets cut both times. The one exception is a **pathological title**
   — roughly eight words or more, where the honest slug is a paragraph. There you still do not
   truncate; you **compose a short meaningful slug** from what the PRD is actually about
   (`customer-eligibility`, out of *Rework how customer eligibility is decided at checkout for
   partner accounts*) — and you **announce that you did it, and what you chose**, alongside the
   branch name. An announced short slug is a naming call the human can correct in one line; an
   unannounced one is a branch they cannot find and did not know to look for.

   **Strip the leading `[…]` bracket group from the title before slugging** — slug
   `extract-lk-plugin`, never `prd-extract-lk-plugin`. This is the whole reason the strip is
   specced rather than assumed: a PRD that gains the prefix while a run is in flight computes a
   *different* branch name than the one its work is on, so the resume opens a second branch and
   a second PR, Setup step 4 finds zero commits on it, and every landed issue is re-run from
   scratch. Nothing errors. Strip any leading `[…]` bracket group, not the literal string
   `[PRD]`, so an adapter that names a different prefix is handled too.

   **Collision guard — check it only when you are about to *create* the branch.** A pattern is
   free to collide in a way `prd/<n>-<slug>` never could: `feat/<slug>`, or a bare `release`, can
   name a branch that already exists and has nothing to do with this PRD. Step 1's search has already
   ruled out the ordinary resume by this point, so what is left here is a collision or a legacy run.
   So before creating, if
   the name is already taken, find out whose it is — an **open PR whose head is that branch and
   whose body runs a different PRD** means it belongs to that run. **Stop and report**: name the
   branch, the PR, and the PRD it is running, and ask the human for a different pattern or a
   different name. Do not improvise a suffix, and never stack two PRDs on one branch — the second
   PRD's commits land in the first one's PR, the first one's `Closes` line closes the second one's
   issues on merge, and Setup step 4 reconstructs "done" from a commit history that is two runs
   interleaved. The two innocent cases stay ordinary: an existing branch whose open PR runs *this*
   PRD is the resume this loop is built around, and an existing branch with **no** open PR is a
   cold start after one was closed — adopt either and carry on.
3. **PR** — **only on the cold-start path**; a run found by step 1 already has one. One per PRD,
   **draft**, targeting the default branch (required for `Closes` to fire). Push first, with an empty
   commit `prd #N: loop start` if the branch has no commits ahead, then open it.

   **The body is the team's template plus the machine block, from the first push.** There is no
   later presentation step and no close-and-reopen: what the loop opens is what the team reviews.

   **Resolving the template** — the adapter's optional **`PR template:`** row, in the `### GitHub`
   sub-section of `## Repo`:

   - **A repo-relative path**, the preferred and common case. Read that file **at PR-open time, from
     the branch**, so the body tracks the team's live template instead of a copy of it. Row present
     but the file missing → say so and fall through to the skeleton; never guess at another path.
   - **The literal word `snapshot`**, with the template body fenced directly beneath the row in the
     adapter. Use it, and note in the final summary that the PR was built from a snapshot nothing can
     tell you is still current.
   - **Absent** — the loop's own skeleton, which is now just its own two lines around the block:

     ```
     Runs PRD #<n>: <title>

     <the machine block>

     🤖 Generated with [Claude Code](https://claude.com/claude-code)
     ```

     The children checklist, the `Closes` line and the `QA:` line that used to sit here are not gone;
     they moved **into** the block. Writing them in both places would give the loop two checklists
     and two `Closes` lines to keep in step, and the day they disagree nothing would say which one
     the merge honours.

   **Instantiating it honestly.** Nothing has landed at PR-open time, so every prose section is
   genuinely unknown and the body has to say so rather than describe work that has not happened:

   - **Keep every heading the template has.** A section you cannot fill gets a one-line
     `_In progress — filled at loop end._` beneath it — never a deletion, never an invented summary.
     A reviewer who opens the PR on day one is owed an honest empty, and loop end §2 needs the
     heading to fill into.
   - **Leave the team's own checkboxes unticked.** They are the team's claims and the run has made
     none of them yet. Loop end ticks the ones that actually became true, and only those.
   - **Drop the template's own closing-keyword line** (`Closes #`, `Fixes #`, `Resolves #`) — the one
     line of the team's template the loop ever removes. Closing children is mechanics, the machine
     block owns it, and two closing-keyword lines in one body is a conflict nobody wrote deliberately.
   - **Leave instructional HTML comments alone.** They are the team's, they render as nothing, and
     stripping them makes the body diverge from the template it claims to be.
   - **The template never decides mechanics.** Draft state, the target branch, the `Closes` line and
     the machine block are the orchestrator's whatever the template says about any of them. A
     template asking for a ready-for-review PR, or a different base, does not get one.

   Then **append the machine block as the last thing in the body**, per `## The machine block`.

4. **Reconstruct**: an issue is done ⇔ a commit referencing `(#N)` exists on the branch. Labels/PR body are cache, not truth — repair them to match commits if drifted (check off children, fix labels).

   **The machine block joins that cache; it does not join the truth.** Its checklist and its `Closes`
   line get repaired against the commits exactly as labels and the old body checklist did, and are
   never read as evidence that an issue landed — a block that disagrees with the commits is simply
   wrong, and the commits win. The one line in it that is not cache is `PRD: #<n>`: that is the run's
   identifier, not a claim about what landed, and it is never rewritten.

5. **Stale claim** (`state:in-progress` label but no matching commit — a previous run died mid-issue): discard uncommitted work (`git reset --hard && git clean -fd`, PRD branch only), remove `state:in-progress`, re-add `ready-to-start`. The issue restarts with a fresh worker via the normal pick path — no partial-work recovery, re-entrancy not recovery.

## The machine block

One collapsed block, appended as the last thing in the PR body, holding everything the loop needs from that body and nothing a reviewer has to read. Everything above it belongs to the team.

**It is a parse contract — now the only one this loop writes — on the doctrine ADR 0009 stated for the QA comment and ADR 0012 kept after retiring it: a string two skills must agree on byte-for-byte is hardcoded, never registered in the adapter. Every literal in it is hardcoded here.** The adapter shapes the body *around* the block — the branch pattern, the PR template — and has no say inside it. There is no adapter row for any string below and there must never be one: the project free to edit the resume key is the project whose next resume finds nothing, cold-starts, and opens a second branch and a second PR over live work. That is the failure this whole design was built to remove, and handing it back to the adapter would be handing it back one row at a time.

| Literal | Parsed by | For what |
|---|---|---|
| **`PRD: #<n>`**, matched as a whole line | this skill, Setup step 1 | finding the run — the resume key, and the only search there is |
| the child anchor `- [ ] #<c> ` / `- [x] #<c> ` | this skill, Setup step 4 and Loop step 8 | ticking a landed child, and repairing the checklist against commits |
| the **`Closes` line**, keyword repeated per issue | **GitHub**, on merge | closing the children — the one consumer here that cannot be changed to match us |
| the `<summary>` text `Run bookkeeping — <code>work-on-prd</code>` | this skill, Loop step 8 and step 1's legacy retrofit | locating the block in a body to edit it, and knowing whether one is there already |
| `<details>`, `<summary>`, and the blank line after `</summary>` | GitHub's renderer | collapsing the block, and rendering markdown inside it at all |

Change any of those and you change them in the same edit at every site listed beside them. The three this skill parses have their writer and their reader in this one file and nowhere else, so nothing in the repo will notice if they drift — no validator covers a string that only a model reads. The other two have readers nobody here can edit.

**The block:**

```
<details>
<summary>Run bookkeeping — <code>work-on-prd</code></summary>

PRD: #<n>

- [ ] #<c1> <title>
- [x] #<c2> <title>

Closes #<c2>

</details>
```

Copy what is inside the fence, not the prose around it. The rules are deliberately outside it — instructions pasted into a body template ship to the reader as PR text.

- **`PRD: #<n>` is the resume key**, and the only line in the block that is an identifier rather than cache. Its own line, exactly that shape: `PRD`, colon, space, `#`, the number, nothing after it. Setup step 1 finds the entire run by matching this line, so a stray character here is not a cosmetic defect — it is the duplicate branch and duplicate PR, arriving silently.
- **The checklist is the children**, one `- [ ] #<c> <title>` per child, ticked as each lands. It is cache, repaired from commits by Setup step 4; see there for why it is never the truth about what landed.
- **The `Closes` line repeats the keyword per issue** — `Closes #41, closes #42`. A bare `#42` after a comma does **not** close, and nothing tells you: the PR merges, one issue closes, the other sits open looking like a loop that forgot it.
- **The `Closes` line lives inside the block, and that is verified rather than assumed.** A PR whose body carried a closing keyword *only* inside a `<details>` element was squash-merged into a repo's default branch: the PR's `closingIssuesReferences` already listed that issue **before** the merge, and after it the issue closed with `stateReason: COMPLETED`. Collapsing hides a keyword from the reader, not from the parser. There was a specced fallback — the `Closes` line sitting above the block, out in the open — and it was dropped on that evidence. Do not re-add it and do not re-run the experiment: the question needs a real merge to answer, and it has been answered under the conditions this loop actually uses (squash merge, default branch as target, repo auto-close at its default).
- **The blank line after `</summary>` is load-bearing.** Without it GitHub renders no markdown inside the element and the checklist arrives as literal text with no checkboxes.
- **Appended last, always.** After everything the template contributed, so a reviewer meets the team's PR first and the bookkeeping only if they open it.
- **One block per body.** Before appending one — at PR open, or at a legacy retrofit — check whether the body already carries a `<summary>` with that text. Two blocks is two `Closes` lines and two checklists disagreeing in the same body, and the retrofit is the path that would produce it, since it is the one place a block is appended to a body somebody else wrote.
- **Nothing else goes in.** Not the `QA:` line — loop end §2 places that in the body proper — not deviations, not the run's summary. Three things: the pointer, the checklist, the `Closes` line.

## Loop (per issue)

1. **Pick** the next eligible child per `../_shared/prd-eligibility.md` (open ∧ blockers closed; picking order as specced) — with one orchestrated-mode relaxation: a blocker **inside this PRD** is also satisfied when its commit exists on the PRD branch (`state:done-on-branch`), since children only close on merge; without this, every `Blocked by` chain would deadlock the loop. None eligible but open blocked children exist → report the blocking chain; if the blockers are outside this PRD, pause for the human. None open at all → go to **Loop end**.
2. **External steps**: any unmet `- [ ]` under `## External steps` → pause, list them, wait for the human. Always, regardless of gate.
3. **Claim**: remove `ready-to-start`, add `state:in-progress` (remove-old-before-add-new — always this order; one state per axis).
4. **Route model**: apply `../_shared/model-effort-heuristics.md` **in orchestrated mode** — the default flips: workers start Sonnet-class and *upgrade* to Opus-class on the file's heavier/risk signals. Announce the routing call (tier + matched signals) before spawning.
5. **Spawn worker**: Agent tool, `subagent_type: prd-workflow:prd-worker` (see *Agent type by route* below), `model` per the routing call, `run_in_background: false`. Flat hierarchy — workers never spawn workers. Isolation is total: everything the worker needs must be in its prompt, the issue, or the repo. The **mandates and the report contract live in `../../agents/prd-worker.md`** — never restate them in the prompt, which carries only the per-call inputs:
   - The **full issue body** (incl. `## Worker context`, `## QA notes`, acceptance criteria).
   - The **full contents of the project adapter** (path at the top of this skill). The adapter only; a gate it registers goes in the prompt **only** when this issue triggers it — pasting every gate into every worker is the tax that keeps gates out of the adapter in the first place.
   - The **branch name as Setup resolved it** — step 1's PR head on a resume, step 2's created name on a cold start. The actual name, never the adapter's pattern and never recomputed here. Plus the **issue number** for the `(#N)` commit suffix.
   - The **routing call** you announced in step 4.

   **Agent type — get this right before you fall back.** A plugin namespaces every component it provides, so the type is **`prd-workflow:prd-worker`** however the plugin was loaded: installed from the marketplace, or via `claude --plugin-dir`. There is no unprefixed form; the bare `prd-worker` only ever came from a hand-placed `.claude/agents/` file on the retired pre-plugin route. Use the namespaced name — treating the bare name as primary is what silently produced a whole run of `general-purpose` workers once already.

   *Detachable — expect to need this*: `prd-worker` is project-scoped, and registration lags. A file added to an agents directory that already existed resolves after a few minutes; a **newly created** `.claude/agents/` does not resolve at all for the rest of the session, and a plugin enabled mid-session does not register its agents until the next session. So if **neither** type name resolves, do not wait and retry — read `../../agents/prd-worker.md` and paste its body (everything below the frontmatter) into a `general-purpose` agent for the whole run. Same contract, one source of truth. **Announce which of the three paths the run took** — namespaced, bare, or detached — because a detached run looks identical to a real one in the output, and that is the only signal that the agent did not resolve.
6. **Judge the report**: commit exists on branch · verify evidence is real (spot-check: re-run the L2 command if evidence looks thin) · deviations acceptable · AC covered.
7. **Gate** per `--gate` mode (see Invocation). On pause: present the report + your judgement, wait for the human.
8. **Success path**: push the branch → labels: remove `state:in-progress`, add `state:done-on-branch` → PR body: **edit the machine block, and nothing else**. Tick that child in the block's checklist, and append it to the block's `Closes` line with the **keyword repeated per issue** — `Closes #41, closes #42` (a bare `#42` after a comma does NOT close). The team's prose stays exactly as PR open left it until loop end: an in-progress placeholder that stays honest for nine issues and is filled once beats a running summary rewritten nine times and read by nobody.
9. **Failure path** (worker exhausted its 2 attempts, or report judged unacceptable): discard uncommitted work (reset/clean, branch only) → backward label transition: remove `state:in-progress`, re-add `ready-to-start` (failure is a backward transition, not a new label) → post an **escalation comment** on the issue: what was tried, what failed, evidence → pause per gate (`issue`/`events` pause; `end` records and continues) → increment the consecutive-failure counter; at 2, full stop with summary. A success resets the counter. A failed issue is not re-picked in this run unless the human unblocks it.

## Loop end (no eligible children left)

Three things, in order: the QA handoff, the PR body, the final summary.

### 1. The QA handoff — the label, then the invocation

**Commit nothing, create no issue, and post no QA comment.** This loop no longer composes a QA pass. `manual-qa` composes one on demand, in its own session, from what actually landed on the branch — the diff, the commits and their `(#N)` attribution — so a script written *here*, before the code existed, could only describe what the run planned to make testable. The loop has moved three times: a committed markdown document, then a standalone `[QA]` issue, then a per-run comment on the PRD. It does none of them now, and none of the machinery any of them needed survives here — no template, no heading rules, no id trailers, no never-edit rule, no second-run link-back. Loop end's entire QA output is a label and a printed line.

- **Apply `needs-qa` to the PRD** — `gh issue edit <prd-number> --add-label needs-qa` — **iff at least one child in this run reported something a human can exercise** (worker report contract, item 4). The label means **"not yet QA'd"** and nothing else: it is the operator's queue, and `manual-qa` is what removes it. A run of nothing but bumps, config and refactors earns no label — say so in the final summary, so the absence reads as a decision and not a forgotten step. The label must already exist in the repo: the loop applies it and cannot create it, and `gh issue edit --add-label` against a missing label fails loudly. One-time human precondition — see the adapter.
- **Print the invocation**, for the human to run when they judge the run worth a pass:

  ```
  /prd-workflow:manual-qa #<prd-number>
  ```

**The loop never invokes `manual-qa` itself.** On demand is the only trigger. The developer who just watched the run is the one who decides whether it warrants a pass, and a driver that starts itself at loop end is the checklist-nobody-works failure in a new costume.

### 2. PR body

**Fill the template; never swap the body.** This is the one pass where the prose sections that PR open wrote as `_In progress — filled at loop end._` get their real content, from what actually landed — the same source the final summary uses, never the PRD's plan. Edit those sections **in place**: the body's structure is the team's template and stays as instantiated, headings, order and all. Do not regenerate the body from the template, and do not overwrite a section a human edited during the run — a reviewer who wrote in this body outranks the fill.

The same pass, four more things:

- **Tick the team's own checkboxes** that actually became true, and only those. One left unticked with a reason beside it is a fine outcome; one ticked because the template offered it is a false claim made in the team's own words.
- **The `QA:` line** — literally `QA: run /prd-workflow:manual-qa #<prd-number>`, the same invocation §1 printed. It goes in the template's own testing or QA section if it has one; absent that, on its own line directly above the machine block. Not *inside* the block: the block holds three things and this is not one of them. Omit the line entirely when §1 applied no label, and say in the final summary that nothing in this run is manually testable. **After loop end this line is `manual-qa`'s alone** — the loop writes it once and never touches it again; a completed pass replaces it with the link to its receipt on the PRD.
- **The workers' deviation logs** — code-review notes, observations about the diff, edge cases a reviewer should know about — land here, in whichever section of the template takes notes on the change. They have nowhere else to go — §1 posts nothing — so this is where a worker's deviation log lands.
- **The machine block's final state** — every landed child ticked, the `Closes` line complete. Loop step 8 has been maintaining both, so this is a check and not a rewrite; where it disagrees with the commits on the branch, the commits win (Setup step 4).

The PR stays a **draft**.

### 3. Final summary

Filter: `../_shared/final-prints.md`. Everything that landed is on the PR the human is about to open, so the print is **the exceptions plus the handoff** — never a roll-call of the children that worked.

```
Done — 7/9 landed. PR: <url>
Skipped   #12 — blocked: needs STRIPE_KEY set (your move)
Failed    #15 — tests never green after 2 attempts; not on branch
Deviated  #13 — reused ExportJob instead of new queue; reviewer: check retry path
Escalation — migration touches prod data, wants sign-off before merge
needs-qa applied — something exercisable landed.
/prd-workflow:manual-qa #<prd-number>
```

Rules for it:

- **Sections print only when non-empty.** A clean run is three lines: the tally, the `needs-qa` line, the command.
- **The mapping is exhaustive by contract.** Every worker report carrying a skip, a failure, a deviation or an escalation produces exactly **one line** here — one line each, fixed left-edge label column. Dropping one because the list ran long is never a conciseness move; that is the protected class in the shared filter.
- **The deviation lines are the alert, not the detail.** The workers' full deviation logs are already in the PR description (§2) — a line here says a reviewer needs to look, and where.
- **One URL, and it is the PR.** Not the PRD, not the branch, not a child issue: the PR is what the human opens next and everything else is one click from it.
- **The QA handoff is a fact plus the command** — `needs-qa applied`, or the explicit `no needs-qa — nothing in this run is manually testable`, with the reason. Then the invocation on its own clean line, last thing on screen.

Leave the PR open (still draft) for human QA (verify ladder L5: run `manual-qa` against the branch, work its flows, then merge manually). The PRD issue is **not** closed by the loop — `Closes` keywords fire on merge. Do not remove `needs-qa` and do not post a receipt of your own: `manual-qa` owns both, and they are the only signals that a pass was ever run.

Then release keep-awake — mirror of Setup step 0, no-op if never started:

```bash
[ -f /tmp/work-on-prd.caffeinate.pid ] && kill "$(cat /tmp/work-on-prd.caffeinate.pid)" 2>/dev/null; rm -f /tmp/work-on-prd.caffeinate.pid
```

## Label vocabulary

Normative home for the label vocabulary — `to-issues` and `next-prd-issue` apply/read these; change them here first.

`ready-to-start` (filed, unclaimed) → `state:in-progress` (claimed) → `state:done-on-branch` (committed, awaiting merge). Merge auto-closes via the PR's Closes line. One state per axis; always remove-before-add. Precondition (one-time, human): the repo setting "auto-close issues with merged linked pull requests" must be on — see the adapter.

**`ready-to-start` records that a child is unclaimed; it does not gate the pick.** Eligibility is *open ∧ every blocker done* (`../_shared/eligibility-policy.md`) and reads no label, so a child missing the label is picked anyway and a child carrying any other label is too. What keeps an issue out of a run is not being linked to the PRD as a sub-issue — the link is the sole input to discovery. The label earns its place in state reconstruction (Setup step 4) and in the claim / failure / stale-claim transitions, and nowhere else. **Do not add a label check to the pick path**; the one place that was ever documented as a gate turned out never to have been one.

Two families, and the difference is who clears the label. **`state:*` is machine state**: the loop applies it, the loop removes it, and a human touching one only confuses the reconstruction in Setup step 4. **`needs-*` means a human owes something** and only a human clears it — `needs-triage` on an untriaged issue, and **`needs-qa` on a PRD whose run landed something a human can exercise** (Loop end §1), where it means *not yet QA'd*. That is why `needs-qa` is not `state:qa-pending`: the loop applies it and then has no further business with it, and the operator's queue is exactly the set of PRDs carrying it. The loop never removes `needs-qa`, on this run or any later one — `manual-qa` does, at the end of a completed pass.
