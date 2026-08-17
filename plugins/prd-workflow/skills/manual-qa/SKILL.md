---
name: manual-qa
description: Compose a PRD run's manual QA pass from what actually landed on the branch — the diff, the commits and the landed children — as a short list of flows, then drive it one flow at a time, taking one verdict per flow and posting a self-contained [FINDING] comment to the PR on a failure. Also the ad-hoc capture path for a finding noticed outside any flow. Invoke /prd-workflow:manual-qa with a PRD URL to run a manual QA pass.
disable-model-invocation: true
---

# manual-qa

**Compose the pass, then drive it.** Given a PRD, find that run's PR, read what actually landed on the branch, compose a short list of **flows**, and walk the human through them one flow at a time — capturing what fails as findings on that PR. This is the **capture phase** of the PRD QA loop. Triage (confirm, root-cause, promote to issues) happens **later, in a separate session**, via `triage`.

**Nothing is read from a QA comment.** The pass is composed here, in this session, from the as-built record — not from a script written before the code existed. That is the whole difference: a planned step describes what a slice was *supposed* to make testable; the diff describes what there is to test.

It supersedes `qa-prd-log`. Capture is not a separate skill: it is what this driver does when a flow fails, and ad-hoc capture is this same skill invoked with nothing to drive (see `## Ad-hoc capture`). `qa-prd-log`'s two load-bearing blocks — `<the-line>` and `<comment-template>` — live here, as sections of this skill.

**No `--post` flag and no second-human path.** The loop is single-developer by design: the person who ran it is the person testing it, in this session, on this machine.

## Project facts

Every project-specific value comes from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it; never hardcode one here. This skill reads four things and nothing else:

| Adapter section | What for |
|---|---|
| `## Repo` | the issue tracker and PR repo — where the PRD lives and where findings are posted |
| `## Commands` | how to launch, build and check the thing — the sub-steps the driver can verify itself |
| `## Verify ladder` | **L5**, which defines what a sub-step must name to be executable at all, and **L2/L3**, which define what the driver can verify without the human |
| `## Sources of truth` | the **project explorer agent** for on-demand elaboration — `Explore` where it says None |

## Three non-negotiables

1. **Capture, don't solve.** `<the-line>` says exactly where investigation stops. It has not moved: composing the pass added authorship, not licence to debug.
2. **Every comment is self-contained.** A cold `triage` session reads the comment, not this conversation. Symptom, evidence, a `file:line` pointer, a labelled root-cause *hypothesis*, classification, repro — plus, here, which flow and sub-step and which children it came from.
3. **A pass verdict is a receipt, and it means exactly one thing**: a human executed that flow and observed it work. Nothing else ever produces one — not "probably fine", not silence, not a change of subject. A false pass is a false receipt, and the receipt is the only record the pass ever happened.

## Input: one PRD URL

**One input, no branching, no selection logic.** The user passes a PRD URL (or issue number). If they pass nothing, this is ad-hoc capture — see that section — not a prompt to go hunting for a PRD.

### Finding the run

The run's identity is its **pull request**, found by the machine block's resume key in the PR body — the same key `work-on-prd` uses, and no new literal:

```bash
gh pr list --repo <owner>/<repo> --state open --json number,headRefName,body \
  --jq '[.[] | select(.body | test("(^|\n)PRD: #<n>[ \t\r]*(\n|$)"))] | .[] | {number, headRefName}'
```

**Match the whole line, never a substring** — `PRD: #12` is a prefix of `PRD: #127`, and a bare substring match hands you somebody else's run. More than one hit, or none, is a **stop**: say what you found and ask. A PR that predates the machine block carries no such line; that is a run this skill cannot locate, and saying so is the correct outcome.

Then **say which PR you picked** — number, head branch, title — before reading anything else.

## Composing the pass

### What you read, and what it is for

Four reads, all of the branch that PR points at:

| Read | Command | What it is |
|---|---|---|
| the diff | `gh pr diff <n>` | **the as-built record** — the only authority on what there is to test |
| the commits | `gh pr view <n> --json commits` | attribution: the `(#N)` suffix on each subject says which child owns that code |
| the landed children | the machine block's checklist, or issues labelled `state:done-on-branch` | which slices are in this run at all |
| each child's body | `gh issue view <c>` | acceptance criteria and planned `## QA notes` |

The last two are **context, not the pass**. A child's `## QA notes` was written before the code existed and may describe something that was built differently or not at all; read it for intent and let the diff overrule it. **There is no per-child write-back to read** — the workers' refined notes went into a report the orchestrator consumed, and nothing durable holds them.

### What a flow is

A **flow** is a run of sub-steps that share a starting state and end somewhere the tester can safely walk away from. Each flow has:

- a **name** — what the tester is exercising, in their words;
- an explicit **`start from:` line** — the shared setup or precondition the sub-steps assume;
- **sub-steps**, numbered within the flow, each naming an action and an observable result;
- **attribution** — the children whose code this flow exercises, lifted from the `(#N)` suffixes on the commits that touched the files involved.

**The first flow is always "get running"**: whatever the adapter's `## Commands` and L5 rung say it takes to have the thing in front of you — the launch command, the config dir, the branch checked out. Everything after it starts from a running system.

**Cross-flow dependency is allowed, and must be named in `start from:`** — "start from: a completed flow 2, app still running" is a fine precondition; leaving it implicit is not. A tester who reads `start from:` and cannot get there has been handed a flow they cannot run.

### Flow boundaries

Boundaries follow **cohesion**: same screen, same config, same state. **Never "by child" and never "every N sub-steps".** A child that touched three unrelated surfaces earns sub-steps in three flows; three children that all changed one screen share one.

3–7 sub-steps is a smell test, not a rule. A one-sub-step flow is fine — a single dependency bump with one thing to look at is one flow with one sub-step, not padding to reach a quota. A flow that has grown past a dozen sub-steps is usually two flows whose shared starting state you have not named yet.

**Present the whole list first** — numbered flows, each with its name and `start from:` — so the tester can see the shape of the pass and how long it is before committing to it.

### No upfront exploration beyond the four reads

The four reads above are the composition input, and that is all. Do **not** go reading the wider codebase to write the flows. Elaboration *during* the pass — when the human asks what a sub-step means — is **on demand only**, and delegated, never done on this thread:

- Spawn **one throwaway subagent** per question: the **Agent** tool with the explorer agent from the adapter's `## Sources of truth` (`Explore` where it says None), `model: "haiku"`, thoroughness "medium". Same shape as `pinpoint`.
- Ask for a **condensed report**: paths, symbols, the one thing that answers the question. Do not read, grep or glob yourself — the point is to keep the QA thread clean.
- **It must name its source**, and you relay it in that form: *"from the diff on this branch: …"* — so the human always knows they are hearing an inference from code, not the pass.

Two hard limits: elaboration **never rewrites a flow mid-pass**, and it is **never the basis for judging a verdict**. Only the human's observation in the running app decides that.

### Session hygiene: check and report, act only on the word

Before presenting flow 1, confirm and say what you found:

- the PR's head branch is the one checked out (`git branch --show-current`);
- the PR is open (`gh pr view <n> --json state,isDraft`);
- the tree is clean (`git status --short`).

Anything unexpected — dirty tree, detached HEAD, closed PR, wrong branch — **say so and stop for the human**. The driver runs read-only and verify commands from the adapter's `## Commands` freely; anything that changes the working tree or starts a long-lived process it **proposes and waits for a yes**. The tester owns their machine.

## Driving the pass

**Present flow *n* whole** — name, `start from:`, every sub-step — and narrate the position: **"flow 3 of 5"**. A flow presented a sub-step at a time is a flow the tester cannot plan a walk-away point in, which is the one thing flows exist to give them.

Within the flow, split the work:

- **Sub-steps the driver can verify itself** — the adapter's L2 and L3 rungs: commands with checkable output, a build, a file that must exist, a plugin that must appear in a listing. **Run them and paste the output.** Evidence, not a claim that they passed.
- **Sub-steps only a human can do** — anything requiring eyes on a running system. Ask for exactly those, having already shown the machine half.

### One verdict per flow

| Verdict | Effect |
|---|---|
| **Pass** | record it, move to flow *n+1* |
| **Fail at sub-step *k*** | post a `[FINDING]` comment to the PR naming flow *n*, sub-step *k*; move to flow *n+1* |

- **Partial progress inside a flow is not recorded.** A re-test reruns the whole flow — cheap by construction, because flows are short and start from a named state. There is no half-passed flow and no third verdict.
- **A failed flow does not block the next one.** Unless its failure makes a later flow's `start from:` unreachable, in which case say so and ask.
- **Never advance without an explicit verdict.** Not from silence, not from a change of subject, not from "ok". If the next thing the human says is not a verdict, answer it and re-present the flow.
- **Natural language, not keywords.** "yeah all four showed up", "died on the second one", "fine until the last bit" are all verdicts. There is no vocabulary to memorise.
- **But never record a pass on ambiguity.** "I think so", "looks about right", "close enough" are not verdicts. Ask **one** clarifying question naming the observable result the sub-step states, and wait.

### A structurally unexecutable sub-step is itself a finding

A sub-step that **cannot name a config dir, a command and an expected result** — the adapter's L5 rung — is not something this project can test. That is not a skip and not a shrug: **log it as a finding**, classification `bug (this repo)`, so it gets a paper trail and a trip through triage. Since this skill composed the sub-step, the finding is against this skill's composition or against a slice that landed nothing testable — say which.

### "Blocked" is not a verdict

It is the human stopping. Go to `## End of pass` and take the stopped-early branch: post the receipt, **leave `needs-qa` on**, say which flow they reached.

## Findings

**The marker is `### [FINDING] <one-line symptom>`, hardcoded here.**

It is deliberately **not** registered in the adapter's *Title prefixes* row. Those prefixes are a decorative human scanning convention; this is a **parse contract** — `triage` reads the PR's comments looking for exactly this string. Making it project-configurable would let a project edit it and get a `triage` that silently finds zero findings and reports a clean PR.

**One finding per turn. Never batch.** Post it, report the permalink and a one-line recap, then move to the next flow.

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

**Out of bounds (defer to `triage`):**
- Tracing the full call graph to pin the exact broken line.
- Reproducing many permutations beyond the one that decides routing or severity.
- Reading another repo's handler to find the precise fix.
- Writing or testing a fix.
- Spawning code-exploration subagents. If a finding needs a deep code dive just to be *understood*, that is the signal it belongs in `triage`. (The on-demand elaboration subagent is not an exception: it answers "what does this sub-step mean", never "why did it break", and never decides a verdict.)
</the-line>

<routing>
### Routing (which repo/owner)

- **This-repo bug** → a real defect in the code of the repo under test. Post to the PR; `triage` will open an issue here.
- **Contract-boundary bug** → the symptom is in this app but the cause sits on the other side of the API boundary, in the repo named by the adapter's `## Repo` → *Related repos*. Prove it with the one decisive probe where feasible and say so explicitly — `triage` investigates over there and files the issue in that repo, cross-linked back. Do **not** fix or file across the boundary from here.
- **Deferred-by-design** → not a bug. Say what was deferred, cite the code comment or PRD note, and what the follow-up slice needs.
- **Works-as-intended / enhancement** → capture the desire, mark it as not-a-defect.

If the adapter says "None" for related repos, there is no contract boundary to route to — everything is a this-repo finding.
</routing>

<comment-template>
### Comment template

Keep it lean — the canonical minimum is repro / expected / actual; the rest earns its place. Structure:

```
### [FINDING] <one-line symptom>

**Step:** flow 3 ("search and filter"), sub-step 2
**From:** #75 #80

**Symptom:** what the user sees.

**Classification:** bug (this repo) · bug (contract boundary) · deferred-by-design · works-as-intended · enhancement
**Severity:** low / med / high   (severity = technical impact, independent of priority)

**Evidence:** the one decisive probe / screenshot description / log — the thing that removes ambiguity.

**Where:** `<path>:<line>` — where the symptom surfaces.

**Root-cause hypothesis:** *(labelled as hypothesis, separate from the facts above)*

**Repro:** numbered, exact steps.
```

- `**Step:**` is the position in this pass — **flow number, flow name, sub-step number**. **No permalink**: the pass was composed in this session and posted nowhere, so there is nothing to link to. Do not invent a link and do not write "n/a"; the flow name is what makes the position legible to a cold reader.
- `**From:**` is the child issues whose code the flow exercises, written with the `#`, lifted from the `(#N)` suffixes on the commits that touched the files involved. The rendered `#N` is wanted here — one line, in one comment, where the expansion is useful.
- **Both fields are absent in ad-hoc mode**, where there is no flow and no attribution. Omit the lines entirely; do not write "n/a".
- Screenshots the user pastes cannot be embedded via `gh` (they are local) — describe them in words instead. If the user wants the image inline, they drag it into the comment on GitHub themselves.
- Post with `gh pr comment <n> --body-file <path>` (write the body to the scratchpad first; avoids shell-escaping issues), against the PR this pass is running on.
</comment-template>

## End of pass: the receipt, and `needs-qa`

Two artifacts, in this order:

1. **The receipt** — one **free-form** comment on the **PRD**: which flows ran, the verdict on each, links to any findings, and — if the pass stopped early — which flow they got to. Free-form means free-form: **nothing parses it**, it is output rather than input, and it has no template. `gh issue comment <prd-number> --body-file <path>`.
2. **The label.** A pass that ran every flow to a verdict → offer to remove it, and on a yes: `gh issue edit <prd-number> --remove-label needs-qa`. A pass that **stopped early** → post the receipt and **leave `needs-qa` on**, saying so in as many words. The label is the queue signal; an unfinished pass is still in the queue.

Findings do **not** hold the label on. A pass that ran every flow and found three bugs is a completed pass — the findings are `triage`'s queue, not QA's.

**A re-run composes fresh.** It reads the branch again — which has usually moved — and builds new flows rather than reconstructing the old ones. Then it **asks the human where to start**, offering the earlier receipt's stopping point as the obvious answer. There is no resume state to read, and that is deliberate: the alternative is a stored pass that drifts out of date against the branch it describes.

## The terseness floor

**Composing the pass does not license compressing it.** Every sub-step must be executable by a human reading it cold:

- a receipt or a finding outlives this session;
- a sub-step that only works because a model is there to interpret it is not a sub-step;
- and the driver reads sub-steps out as written.

The driver adds gating and bookkeeping, **not comprehension**. If you cannot write a sub-step that names a command, a place and an observable result, the honest output is a flow with fewer sub-steps — or the note that this slice has nothing a human can exercise.

## Ad-hoc capture

Invoked with no PRD URL, or a finding noticed outside any flow, this skill is just the capture half:

- Ask which PR the finding belongs to, if it is not obvious. That is the only context needed.
- Run the same cadence — confirm it is real, classify per `<routing>`, one decisive probe at most per `<the-line>`, post one self-contained comment per turn.
- **Omit** `**Step:**` **and** `**From:**` — there is no flow and no attribution to lift.
- Record nothing else. There is no pass being driven, so the finding is the whole output.

## Handoff to triage

The PR's `### [FINDING]` comments are this skill's only committed-to-the-tracker output; the receipt on the PRD is a human-readable record of the pass and nothing reads it back. A later `/prd-workflow:triage` session confirms each finding, roots it out, and promotes the survivors into cold-runnable children of the PRD. This skill never fixes anything and never files an issue.
