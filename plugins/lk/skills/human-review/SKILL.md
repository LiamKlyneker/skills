---
name: human-review
description: >
  Walk a human reviewer through one pull request: read the PR, its comments, its diff and the code
  around it in the main thread, explain the problem and the approach as one walkthrough with the
  findings sorted into priority buckets, discuss the findings the reviewer picks one at a time, and
  post one review in the reviewer's voice only after the reviewer approves the whole batch. Builds
  on what automated reviewers already said rather than replacing them, and writes nothing into the
  project. Runs on user invocation only; no loop invokes it. Invoke /lk:human-review [<pr>]
disable-model-invocation: true
---

# human-review

**Help one human review one pull request, and post exactly the review that human approved.**

The reviewer runs `/lk:human-review` on a pull request. The skill reads the PR and its context,
explains what the PR is for and how it goes about it, sorts what it found into buckets, and then
discusses only the findings the reviewer picks. Every comment it posts is a draft the reviewer saw
and approved, in the reviewer's voice, posted as one review.

**It is read-only towards the project.** It writes nothing into the project under review: no file,
no comment in code, no configuration, no branch. It does not check out the branch and runs nothing
from it. What a pass produces lives on the tracker, as one review, and nowhere else.

**It builds on automated reviewers; it does not replace them.** Bots that check style, naming and
standards already comment on the PR. The skill reads what they said, skips what they covered, and
spends the pass on what a human is for: is this the right problem, the right approach, and a safe
change.

**The main thread reads the code itself.** The decisions in a review rest on the facts of the
code, so the session that decides holds those facts first-hand.

**It runs on user invocation only.** No loop invokes it — not `work-on-prd`, not `work-on-spec`,
not `sprint-plan`'s night run — and nothing else may.

## Invocation and input

`/lk:human-review [<pr>]`

Before resolving the PR, read `../references/pr-review-posting.md` §Invocation and input.

## Project facts

Before the first read, read `../references/pr-review-posting.md` §Project facts.

## Reading

**Read everything in the main thread. No subagent reads the diff or the code**, because a subagent
returns a summary, and a review decided from a summary cannot verify its own findings.

**Identify the reviewer first.** Re-review detection needs it.

- `github`: `gh api user --jq .login`
- `azure-devops`: the signed-in identity of the MCP server, as the server exposes it (discover and
  announce the tool when it is not obvious).

Then read in this order:

1. **The PR description and what it links** — the issue, the ticket, the design. Follow each link
   one level.
   - `github`: `gh pr view <n> --repo <owner>/<repo> --json title,body,author,headRefName,headRefOid,baseRefName,url,additions,deletions,changedFiles,files`
   - `azure-devops`: `mcp__ado__repo_pull_request` for the PR by id, with its linked work items.
2. **Every existing comment and review on the PR**, with each author's login and account type.
   - `github`: `gh pr view <n> --repo <owner>/<repo> --json comments,reviews` for the conversation
     and the reviews, plus `gh api --paginate repos/<owner>/<repo>/pulls/<n>/comments` for the
     inline review comments.
   - `azure-devops`: the PR's threads through `mcp__ado__repo_pull_request_thread`.

   **If the reviewer already has comments or reviews on the PR, go to `## Re-review` now**, before
   anything else is read or said.
3. **The full diff.**
   - `github`: `gh pr diff <n> --repo <owner>/<repo>`
   - `azure-devops`: the PR's iterations and changes through the MCP, reading each changed file at
     the source and the target commits.

   **When the diff is documents only and the documents name other projects**, suggest
   `/lk:proposal-review` in one line, and continue unless the reviewer stops the pass.
4. **For each touched file, the surrounding code** the diff calls into, or whose contract the diff
   changes: the callers of a changed signature, the function a new line calls, the type a change
   widens. Fetch it from the tracker at the PR's head commit (`gh api repos/<owner>/<repo>/contents/<path>?ref=<head-sha>`
   on `github`; the file at the source commit through the MCP on `azure-devops`), or read it from
   the working tree **only when the PR's branch happens to be checked out already**. **Never a
   repo-wide read**: follow what the diff touches, one hop, and stop.
5. **The `CONTEXT.md` of each touched directory**, through `lk:scoped-context`: the directory and
   its parents up to the repo root, only the files relevant to the change.

**Intent comes from the PR alone**: its description, its links, its comments. Never from the
conversation, from memory, or from a guess at what the author meant. When the PR gives nothing to
judge the approach against — an empty description, no link, no comment that states the goal — ask
the reviewer for one line of intent before judging:

> *"The PR does not say what it is for. In one line, what should it achieve?"*

**Anything missing outside the code is a flag, never a stop.** No `scoped-context` skill, no
`CONTEXT.md`, a dead link, a linked item the session cannot reach: note it, and list it in the
walkthrough under the section it affects. The diff and the PR itself are the only reads whose
failure stops the pass.

## The walkthrough and the buckets

**One message holds the walkthrough and the buckets.** When the walkthrough is wrong, the reviewer
corrects it in the reply and the skill re-buckets. That costs a round trip rarely, instead of one
on every PR.

The walkthrough has **five fixed sections, in this order**, on every PR:

1. **The problem** — one concrete scenario, before and after, with a named actor: *"Before: Ana
   saves a draft with an empty title and loses it on reload. After: the draft keeps its body and
   gets a default title."* One scenario, not a list of changed behaviours.
2. **The approach** — how the PR solves it: the shape of the change, the files that carry it, the
   decision it rests on.
3. **The tests** — what the tests prove, and what they do not.
4. **The risks** — rollback (can this be reverted cleanly, and what does a revert leave behind),
   observability (how anyone would know it is broken in production), compatibility (callers, data,
   clients, other services).
5. **Already said on the PR** — what humans and bots already raised, **listed separately by account
   type**:
   - `github`: a **bot** is an author whose `type` is `Bot`, or whose login ends in `[bot]`;
     everything else is a human.
   - `azure-devops`: a **bot** is a service identity; everything else is a human.

   No adapter row names bot accounts; account type is enough.

**A PR too large to review well is flagged** in the walkthrough, with its size, and the pass
continues. The reviewer decides whether "split this" is the review.

Below the walkthrough, **five lists, each item with an id**:

| List | Ids | What goes in it |
|---|---|---|
| High | `H1`, `H2`, … | a wrong approach, a correctness bug, or an unhandled risk |
| Medium | `M1`, `M2`, … | should change, but the PR can merge without it |
| Low | `L1`, `L2`, … | a thought or a preference |
| Questions to the author | `Q1`, `Q2`, … | what the reviewer cannot judge without the author's answer |
| Praise | — | what the PR does well, only when sincere |

**Questions are not findings.** They stay out of the three buckets.

**Never repeat a point an existing comment already made.** Where a finding extends an existing
comment, say so and build on it — *"extends `<login>`'s point on `<file>`: …"* — instead of filing
it as new.

**The skill does not check out the branch and runs nothing.** Where a finding is crucial and only a
run can confirm it, mark it **double check** in the bucket, so the reviewer knows the skill could
not prove it from reading.

Each finding names its file and line, and says the concern in one or two sentences.

```markdown
## <PR title> (#<n>)

**The problem.** Before: <actor> <does X> and <bad result>. After: <actor> <does X> and <good result>.

**The approach.** <the shape of the change, the files, the decision it rests on>

**The tests.** Prove: <…>. Do not prove: <…>.

**The risks.** Rollback: <…>. Observability: <…>. Compatibility: <…>.

**Already said.** Humans: <login> on <file:line>: <point>; … Bots: <login>: <point>; …

<flags: too large, missing CONTEXT.md, dead link, … — only when any>

### High
- **H1** `<file>:<line>` — <concern>. <double check, when it needs a run>
### Medium
- **M1** `<file>:<line>` — <concern>.
### Low
- **L1** `<file>:<line>` — <thought>.
### Questions to the author
- **Q1** <question>
### Praise
- <what is good>

Which ids do you want to discuss?
```

An empty list prints as `none`, never disappears.

## The discussion

Before the first finding is discussed, read `../references/pr-review-posting.md` §The discussion.
Research there is the only subagent the skill ever spawns.

## The drafts and the post

Before the drafts, read `../references/pr-review-posting.md` §The drafts and the post, including
§Posting.

## Re-review

On detection, read `../references/pr-review-posting.md` §Re-review: the question, the full-pass
route, and the delta base with its fall-back to a full pass.

Then read steps 4 and 5 of `## Reading` for the files the delta touches.

**The delta walkthrough has three sections**, replacing the five:

1. **What changed since** the base.
2. **Which earlier comments the changes answer**, each named by file and line.
3. **Which earlier comments stay open.**

**The buckets then hold only new findings.** An earlier comment the author ignored is listed as
still open in section 3, **never re-filed as a finding**.

The discussion, the drafts and the post are unchanged.

## What it never does

- **Never checks out the branch, runs tests, boots the app or opens a preview.** It asks the
  reviewer to double check instead.
- **Never spawns a subagent to read code.** Web research on `sonnet`, on demand, with the
  reviewer's agreement, is the only subagent.
- **Never posts a label, blocking wording, a hash, an id or a marker.** The blocking signal, when
  any, lives once in the summary comment, in words.
- **Never posts per draft or partly.** One batch, one yes, one review.
- **Never posts a finding the reviewer did not look at.**
- **Never repeats what an existing comment already said.** It builds on it.
- **Never reads anything in the adapter beyond `## Repo`, and never adds an adapter row.**
- **Never writes into the project under review.**
- **Never takes intent from anywhere but the PR**, and asks when the PR gives none.
- **Is never invoked by a loop.** On demand only.
- **Never configures or replaces an automated reviewer.** It reads their comments and skips what
  they covered.
