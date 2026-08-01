---
name: manual-qa
description: Drive a PRD's QA comment step by step — narrate each step, wait for an explicit outcome, tick the box on a pass, and on a failure post a self-contained [FINDING] comment to the PR and annotate the step. Also the ad-hoc capture path for a finding noticed outside any step. Invoke /prd-workflow:manual-qa with a PRD URL to run or resume a manual QA pass.
disable-model-invocation: true
---

# manual-qa

Drive the **QA comment** a `work-on-prd` run posted on a PRD — one step at a time, gated on the human's word — and capture what fails as findings on that run's PR. This is the **capture phase** of the PRD QA loop. Triage (confirm, root-cause, promote to issues) happens **later, in a separate session**, via `triage-prd`.

It **supersedes `qa-prd-log`**. Capture is not a separate skill: it is what this driver does when a step fails, and ad-hoc capture is this same skill invoked with nothing to drive (see `## Ad-hoc capture`). `qa-prd-log`'s two load-bearing blocks — `<the-line>` and `<comment-template>` — live here now, as sections of this skill.

Project facts come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it; never hardcode them here. This skill reads three of its sections and nothing else:

| Adapter section | What for |
|---|---|
| `## Repo` | the issue tracker and PR repo — where the QA comment lives and where findings are posted |
| `## Verify ladder` | the **L5** rung, which defines what a step must name to be executable at all (see *A structurally unexecutable step is a finding*) |
| `## Sources of truth` | the **project explorer agent** for on-demand elaboration — `Explore` where it says None |

## Three non-negotiables

1. **Capture, don't solve.** `<the-line>` says exactly where investigation stops. It has not moved: the driver added gating, not licence to debug.
2. **Every comment is self-contained.** A cold `triage-prd` session reads the comment, not this conversation. Symptom, evidence, a `file:line` pointer, a labelled root-cause *hypothesis*, classification, repro — plus, here, which step and which children it came from.
3. **A `[x]` is a receipt, and it means exactly one thing**: a human executed that step and observed it pass. Nothing else ever ticks it — not "probably fine", not silence, not a change of subject. A false tick is a false receipt, and the comment is the only record the pass ever happened.

## Input: one PRD URL

**One input, no branching, no selection logic.** The user passes a PRD URL (or issue number). If they pass nothing, this is ad-hoc capture — see that section — not a prompt to go hunting for a PRD.

### Picking the comment

Load the PRD's comments with **one** call:

```bash
gh issue view <prd-number> --json comments --jq '.comments[] | {url, createdAt, body}'
```

A QA comment is identified by **two markers together**, never a fragile substring:

- the **run-context line** it opens with — ``Branch `prd/<n>-<slug>` · PR #<n> · <count> issues landed``
- the **`## Steps` heading**, present in every QA comment by construction (`## Before you start` is conditional, so it cannot be the marker)

Take the **newest** comment carrying both. Then **say which one you picked** — its permalink, its run-context line, and how many steps it holds — *before* doing anything else. A driver that silently picks the wrong run walks a human through a slice they already tested.

### Deriving the comment id (the trap)

`gh issue view --json comments` returns `id` as the **GraphQL node id** (`IC_kwDO…`), not the REST id the read-modify-write path needs. Do not pass it to `gh api`; it does not 400, it 404s, which reads as "no such comment".

The REST id is the numeric tail of the comment's own permalink — `…/issues/85#issuecomment-5078204371` → `5078204371`. Take it from the `url` field you already fetched. Measured against this repo's API, not assumed.

### The QA comment is self-sufficient

Its run-context line carries **the branch to check out and the PR to post findings to**. That is the whole of the run context, and **nothing else is fetched**: no PR body, no diff, no child issues, no search.

**Total I/O for a pass:**

| Occasion | Calls |
|---|---|
| Load | 1 × `gh issue view <prd> --json comments` |
| Per step confirmed | 1 × `GET` + 1 × `PATCH` on the comment |
| Per finding | 1 × `POST` (PR comment) + 1 × `PATCH` (the suffix) |

No subagent by default. No PR fetch. No polling, ever.

### No upfront exploration

Do **not** read the diff, the children, or the code before starting. Elaboration is **on demand only** — when the human asks what a step means — and it is delegated, never done on this thread:

- Spawn **one throwaway subagent** per question: the **Agent** tool with the explorer agent from the adapter's `## Sources of truth` (`Explore` where it says None), `model: "haiku"`, thoroughness "medium". Same shape as `pinpoint`.
- Ask for a **condensed report**: paths, symbols, the one thing that answers the question. Do not read, grep or glob yourself — the point is to keep the QA thread clean.
- **It must name its source.** Relay the answer in that form: *"the comment doesn't say; from the diff on this branch: …"* — so the human always knows whether they are hearing the QA comment or an inference from code.

Three hard limits on elaboration: it **never rewrites a step**, it is **never appended to the comment**, and it is **never the basis for judging pass/fail**. Only the human's observation in the running app decides that.

### Session hygiene: check and report, never act

Before step 0, confirm two things and say what you found:

- the branch from the run-context line is the one checked out (`git branch --show-current`)
- the PR from the run-context line is open (`gh pr view <n> --json state,isDraft`)

If either is wrong, or anything else is unexpected — dirty tree, detached HEAD, a closed PR — **say so and stop for the human**. Never `git checkout`, never `git stash`, never start the app. The tester owns their machine; this skill owns the bookkeeping.

## `## Before you start` folds into step 0, and ticks nothing

If the chosen comment has a `## Before you start` section, read it verbatim as the lead-in of the **same message** that presents step 0 — there is no separate acknowledgement turn to wait on. The human's step-0 outcome is what confirms it landed. It has no checkbox and it ticks nothing — there is nothing to record on its own.

Skipping it produces a **false finding on step 1**, because that section is the "this will look broken and is not" warning: the dangling symlink a later child repairs, the flag that is off, the child deliberately left for a human. A tester who never heard it logs the known gap as a defect and burns a triage round-trip on it.

No such section → say so in one clause and go straight to step 0.

## Driving the pass

Steps are read **verbatim**, never paraphrased — the wording in the comment is the wording that was verified against what shipped. Narrate the position on every turn: **"step 3 of 9"**. GitHub renders its "3 of 7 tasks" counter for issue *bodies* only, never comments, so the artifact carries no visible progress indicator and the driver is the only one there is.

Two terminal states per step, and no others:

| Outcome | Effect |
|---|---|
| **Pass** | `[ ]` → `[x]`, advance |
| **Fail** | post a `[FINDING]` comment to the PR, append the failure suffix, leave the box `[ ]`, advance |

- **Never advance without an explicit signal.** Not from silence, not from a change of subject, not from "ok". If the next thing the human says is not an outcome for the current step, answer it and re-present the step.
- **Natural language, not keywords.** Read intent — "yeah that showed up fine", "nope, nothing rendered", "it did the thing" are all outcomes. There is no vocabulary to memorise and no magic word.
- **But never tick on ambiguity.** "I think so", "looks about right", "close enough" are not outcomes. Ask **one** clarifying question naming the expected result the step states, and wait. Asking costs a turn; a false tick costs the receipt.

### There is no "skip" state

A step the tester cannot get to right now stays a plain `[ ]` and **resume offers it again**. Nothing is written. Adding a third state would put something in the comment that means neither "passed" nor "failed", and the resume rule below would stop working.

### A structurally unexecutable step is itself a finding

A step that **cannot name a config dir, a command and an expected result** — the adapter's L5 rung — is not a step this project can test. That is not a skip and not a shrug: **log it as a finding**, classification `bug (this repo)` against the run that wrote it, so it gets a paper trail and a trip through triage instead of evaporating. Then advance like any other failure.

### "Blocked" is not a step state

It is the human stopping. **Record nothing.** The comment already holds the ticks, the suffixes, and — by subtraction — the position. Say where they got to, and stop.

### Resume needs nothing else

One `GET` of the one comment. **The first step that is `[ ]` *and* carries no failure suffix is where you are.** No PR comment scan, no cross-referencing, no memory of the earlier session. A pass abandoned halfway resumes cold.

## The write path

Every write to the QA comment is a **strict single-line read-modify-write**. Six rules, all load-bearing:

1. **Fresh `GET` immediately before every write.** Never `PATCH` from a body held in context since the pass began. A stale body written back silently reverts human edits — and violates `work-on-prd`'s never-edit contract by accident rather than intent, which is the worse kind.

   ```bash
   gh api repos/<owner>/<repo>/issues/comments/<comment-id> --jq .body > <scratch>/qa.md
   ```

2. **Substitute exactly one line, anchored on the step number.** Steps are numbered continuously from 0 across the whole run, so the anchor `- [ ] 3. ` — bracket, space, number, dot, space — is unique. Keep the trailing dot-space in the anchor or `1.` also matches `10.`. The **step text and its `<!-- 75 80 -->` trailer stay byte-identical**, as does every other line and the trailing newline. **Never re-render the body from a model-held structure**; edit the one line in the file you just fetched.

   ```bash
   gh api repos/<owner>/<repo>/issues/comments/<comment-id> -X PATCH -F body=@<scratch>/qa.md
   ```

3. **Already-ticked is success, not an error.** The anchor matches `- [x] 3. ` instead → the step is already recorded as passed. Proceed without rewriting and without complaining.
4. **Verify from the `PATCH` response before advancing.** The response carries the new `body`; confirm the anchored line reads the way you intended. `PATCH` returning is not evidence the write landed as meant — reading it back is. A denied write must surface, never be assumed.
5. **A `403` with `x-ratelimit-remaining: 0` stops the pass and says so.** Re-run with `gh api -i` to see the headers if the failure is unclear. Never retry-loop into a secondary rate limit; tell the human what happened and where they got to.
6. **Never poll.** The driver advances on the user's word, full stop. There is no waiting on GitHub for anything.

**The driver owns the boxes for the duration of a pass** — tell the tester this in as many words, once, at the start. GitHub offers no `If-Match` and no optimistic concurrency on comment `PATCH`, so a human ticking in the browser mid-pass is a silent last-write-wins race. Fresh-GET-per-write plus that one sentence is the whole mitigation, and there is no better one available.

## The failure suffix

A failed step is annotated **in place**, step text untouched:

```
- [ ] 3. search for a landed change → expect it in results <!-- 75 --> — **failed**, see [FINDING](<permalink>)
```

- **Pure append**, after the id trailer. The driver never parses a line apart and reassembles it — that is the operation class that reformats things by accident.
- **Not strikethrough.** Struck-through text reads as *cancelled / no longer applies*, which is the opposite of what happened; it mutates the step text; and it has no clean undo.
- **Reversible, and that is what makes the receipt work.** If the step is later re-tested and passes, **one** write flips `[ ]` → `[x]` **and drops the suffix** — so the comment can genuinely reach all-ticked, and "every box ticked" keeps meaning "everything passed".
- **One `PATCH`, not two.** Post the finding **first**, so the permalink exists, then write the suffix in a single substitution.
- The box stays `[ ]`. `[x]` continues to mean exactly one thing (non-negotiable 3).

## Findings

**The marker is `### [FINDING] <one-line symptom>`, hardcoded here.**

It is deliberately **not** registered in the adapter's *Title prefixes* row. Those prefixes are a decorative human scanning convention; this is a **parse contract** — `triage-prd` reads the PR's comments looking for exactly this string. Making it project-configurable would let a project edit it and get a `triage-prd` that silently finds zero findings and reports a clean PR.

**One finding per turn. Never batch.** Post it, report the permalink and a one-line recap, write the suffix, then move to the next step.

<the-line>
### Where investigation stops

> **Investigate only far enough to classify and route — never to solve.**
> *One decisive probe, not a full investigation.*

**In bounds (do at capture):**
- Confirm the symptom (the human saw it, or one quick check).
- **One decisive probe** *when it changes classification or routing* — e.g. a single `curl` against the open API endpoint to prove a bug is server-side rather than client-side. That probe earns its place because it routes the finding to the right repo.
- Grab the **`file:line`** where the symptom surfaces.
- Check the PRD / `CONTEXT.md` / code comments for **deferred-on-purpose**.
- One **root-cause hypothesis**, clearly labelled as hypothesis, kept separate from observed facts.

**Out of bounds (defer to `triage-prd`):**
- Tracing the full call graph to pin the exact broken line.
- Reproducing many permutations beyond the one that decides routing or severity.
- Reading another repo's handler to find the precise fix.
- Writing or testing a fix.
- Spawning code-exploration subagents. If a finding needs a deep code dive just to be *understood*, that is the signal it belongs in `triage-prd`. (The on-demand elaboration subagent is not an exception: it answers "what does this step mean", never "why did it break", and never decides an outcome.)
</the-line>

<routing>
### Routing (which repo/owner)

- **This-repo bug** → a real defect in the code of the repo under test. Post to the PR; `triage-prd` will open an issue here.
- **Contract-boundary bug** → the symptom is in this app but the cause sits on the other side of the API boundary, in the repo named by the adapter's `## Repo` → *Related repos*. Prove it with the one decisive probe where feasible and say so explicitly — `triage-prd` investigates over there and files the issue in that repo, cross-linked back. Do **not** fix or file across the boundary from here.
- **Deferred-by-design** → not a bug. Say what was deferred, cite the code comment or PRD note, and what the follow-up slice needs. (If it was in `## Before you start`, it should not have reached a finding at all.)
- **Works-as-intended / enhancement** → capture the desire, mark it as not-a-defect.

If the adapter says "None" for related repos, there is no contract boundary to route to — everything is a this-repo finding.
</routing>

<comment-template>
### Comment template

Keep it lean — the canonical minimum is repro / expected / actual; the rest earns its place. Structure:

```
### [FINDING] <one-line symptom>

**Step:** 3 — <permalink to the QA comment>
**From:** #75 #80

**Symptom:** what the user sees.

**Classification:** bug (this repo) · bug (contract boundary) · deferred-by-design · works-as-intended · enhancement
**Severity:** low / med / high   (severity = technical impact, independent of priority)

**Evidence:** the one decisive probe / screenshot description / log — the thing that removes ambiguity.

**Where:** `<path>:<line>` — where the symptom surfaces.

**Root-cause hypothesis:** *(labelled as hypothesis, separate from the facts above)*

**Repro:** numbered, exact steps.
```

- `**Step:**` is run provenance — the step number plus a permalink to the QA comment it came from. A PR that has had more than one run carries more than one QA comment, and without this a finding cannot be traced back to the slice being tested when it was found.
- `**From:**` is the child issues that earned the step, lifted from its `<!-- 75 80 -->` trailer and written with the `#`. The rendered `#N` is wanted **here** — one line, in one comment, where the expansion is useful — and forbidden in a step trailer, where two expanded titles inline turn an instruction into a citation.
- **Both fields are absent in ad-hoc mode**, where there is no step and no trailer. Omit the lines entirely; do not write "n/a".
- Screenshots the user pastes cannot be embedded via `gh` (they are local) — describe them in words instead. If the user wants the image inline, they drag it into the comment on GitHub themselves.
- Post with `gh pr comment <n> --body-file <path>` (write the body to the scratchpad first; avoids shell-escaping issues), against the PR named in the run-context line.
</comment-template>

## End of pass, and `needs-qa`

**Tick state is the whole record. Never post a session-log comment** — not a summary, not a "pass complete", not a count. End-of-pass output goes to the **terminal only**: how many steps passed, which failed with their finding permalinks, and which are still outstanding.

**The skill *offers* to remove `needs-qa`; it never removes it unprompted.** All three conditions are readable from the comment already in hand — no extra call:

| Condition | Read from |
|---|---|
| every step is `[x]` | the body |
| no failure suffix anywhere | the body |
| no `Earlier QA pass still outstanding:` first line | the body |

- **All three hold** → offer, and on a yes: `gh issue edit <prd-number> --remove-label needs-qa`.
- **First two hold, third does not** → **still offer, and say so in the same sentence**. That line is a snapshot from posting time; only the human knows whether the earlier pass has since been worked.
- **Either of the first two fails** → do **not** offer at all. Report what is outstanding and leave the label alone.

**The driver drives exactly one QA comment and never touches another.** No chain-walking, no aggregate state across passes. If the chosen comment links an earlier outstanding pass, mention it once and carry on — re-invoking on that permalink is the human's call, not this skill's.

## The terseness floor

**This driver does not license further compression of the QA comment.** Every step must stay executable by a human with no skill available:

- the comment outlives any version of this skill;
- anyone installing `prd-workflow` may never invoke the driver;
- and the driver reads steps **verbatim**, so a step too terse for a human to act on is exactly as useless read aloud.

The driver adds **gating and bookkeeping, not comprehension**. If a step only works because a model is there to interpret it, the step is wrong — that is a finding, not a feature.

## Ad-hoc capture

Invoked with no PRD URL, or a finding noticed outside any step, this skill is just the capture half:

- Ask which PR the finding belongs to, if it is not obvious. That is the only context needed.
- Run the same cadence — confirm it is real, classify per `<routing>`, one decisive probe at most per `<the-line>`, post one self-contained comment per turn.
- **Omit** `**Step:**` **and** `**From:**` — there is no step and no trailer to lift.
- Tick nothing. There is no comment being driven, so there is nothing to record but the finding itself.

## Handoff to triage-prd

The PR's `### [FINDING]` comments are this skill's only committed-to-the-tracker output; the ticks and suffixes on the QA comment are its only record of the pass. A later `/prd-workflow:triage-prd` session confirms each finding, roots it out, and promotes the survivors into cold-runnable children of the PRD. This skill never fixes anything and never files an issue.
