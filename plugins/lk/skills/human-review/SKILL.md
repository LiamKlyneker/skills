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

- **`<pr>` is a PR number** (`142`, `#142`): the PR of that number in the repo the adapter names.
- **`<pr>` is a PR URL**: strip any query string or fragment first. On `github`, take the owner,
  the repo and the number from the URL path (`https://github.com/<owner>/<repo>/pull/<n>`); the
  URL wins over the adapter's locator. On `azure-devops`, take the pull request id from the URL
  path (`…/_git/<repository>/pullrequest/<id>`).
- **No argument**: resolve the PR from the checked-out branch, as `qa:prove-branch` does.
  1. `git branch --show-current`. An empty result is a detached `HEAD`; treat it as "no PR on the
     branch".
  2. List the open PRs whose head is that branch:
     - `github`: `gh pr list --repo <owner>/<repo> --state open --head <branch> --json number,headRefName,headRefOid,title,url`
     - `azure-devops`: `mcp__ado__repo_pull_request` listing active pull requests whose source
       branch is `refs/heads/<branch>`, against the **repo project** and **repository**.
  3. Exactly one hit is the PR. More than one is the same stop as none, listing the hits in the
     question.

**When the branch has no PR, or the argument resolves to nothing, stop with one question:**

> *"I could not find a pull request for `<branch or argument>`. Which PR do you want to review? A number or a URL works."*

Take the answer as the argument and resolve again. Never guess a PR.

## Project facts

The skill reads the **project adapter** at `<repo-root>/.claude/project/adapter.md`, section
`## Repo`, and **nothing else in the adapter**:

| From `## Repo` | What for |
|---|---|
| the `Tracker:` line | `github` or `azure-devops`; **absent means `github`** |
| `github` sub-section → *Issue tracker / PRs* | `<owner>/<repo>`, where the PR lives |
| `azure-devops` sub-section → *Organisation*, *Repo project*, *Repository* | where the PR lives — the **repo project**, never the work-item project |

**This skill introduces no adapter row and no adapter section.** It needs none: bot accounts are
told apart by account type (`## The walkthrough and the buckets`), and the reviewer's identity
comes from the tracker.

**On `github`** every read and the post go through `gh`.

**On `azure-devops`** every read and the post go through the Azure DevOps MCP server's
`mcp__ado__repo_pull_request*` tools, against the repo project and repository. Tool and parameter
names vary by server version; where a named tool, action or field is missing, discover the
equivalent from the running server and announce the substitution. A read that cannot be performed
at all is a stop, never a silent omission.

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

**The reviewer names the ids to discuss.** Take them in the order given, **one finding per
message**:

1. **Show the lines**: quote the diff hunk the finding is about.
2. **State the concern.**
3. **Propose an outcome**, and why.
4. **Wait** for the reviewer.

There are **four outcomes**:

| Outcome | What happens |
|---|---|
| **post** | the finding becomes an inline comment in the draft batch |
| **drop** | the finding is gone; nothing posts for it |
| **research** | compare the PR's approach with the alternatives, then decide again |
| **double check** | ask the reviewer to run something and report the result, then decide again |

**Research**, and only when the reviewer agrees to it: spawn **one** `web-researcher` subagent with
`model: sonnet`. Brief it with the question, the PR's approach, and the alternative in mind. It
returns a short comparison of the approaches, with sources, into the thread. The finding then takes
an outcome like any other. **The comparison itself is never posted**; at most, a post outcome
carries the alternative and one link into the summary comment. This is the only subagent the skill
ever spawns.

**Double check**: name exactly what to run and what result would confirm or clear the finding.
The reviewer runs it and reports. **The skill never runs it.**

A question to the author (`Q…`) the reviewer picks takes post or drop the same way. A post puts it
in the draft batch as an inline comment or in the summary comment, whichever fits.

**Findings the reviewer did not pick are dropped.** Nothing posts that the reviewer did not look
at. When the reviewer says they are done, go to the drafts.

## The drafts and the post

**Every draft in one message**: each inline comment with its file and line, the summary comment,
and the proposed verdict. **One yes approves the batch.** The reviewer may instead edit some drafts
and then approve; apply the edits, show the changed drafts, and take the yes.

**Every posted text is drafted through `lk:how-i-write`**: the inline comments and the summary
comment, in the reviewer's voice.

**Inline comments are plain prose.** No Conventional Comments label (`issue:`, `nit:`,
`suggestion:`), no "blocking" wording, no commit hash, no id (`H1`, `Q2`). The labels, the buckets
and the ids exist only inside the session.

**The summary comment**:

- names the items the reviewer wants done before merge, when there are any, and says why — this is
  the only place a blocking signal lives, once, in words. Most reviews name none.
- carries praise in proportion to the PR's size and how unusual the work is, and the scale is
  steep. A routine PR gets no named praise: at most a bare *"LGTM!"* or *"nice work"*. Praise that
  names a detail is for a large PR or unusual work — a hard bug, a clever design, a large cleanup —
  and stays at one or two items. A human reviewer does not list what an ordinary PR does well, so
  named praise on one reads as an unsupervised AI review. The walkthrough's Praise list informs the
  reviewer and does not have to reach the summary.
- when a research finding's outcome was post, carries the alternative and one link.

**The verdict**:

| Verdict | When |
|---|---|
| **Comment** | the default |
| **Approve** | the summary names nothing to do before merge |
| **Request changes** | only when the reviewer says so |

```markdown
### Inline comments
1. `<file>:<line>` — <comment text>
2. `<file>:<line>` — <comment text>

### Summary comment
<summary text>

### Verdict
Comment

Post this review? (yes, or tell me what to change)
```

### Posting

**One review, posted once, after the yes.** Never per draft, never partly.

**`github`** — write the payload to the scratchpad and post it as **one** review:

```json
{
  "commit_id": "<head sha, headRefOid>",
  "event": "COMMENT",
  "body": "<summary comment>",
  "comments": [
    { "path": "<file>", "line": <line>, "side": "RIGHT", "body": "<comment text>" }
  ]
}
```

```bash
gh api repos/<owner>/<repo>/pulls/<n>/reviews --method POST --input <scratchpad>/review-<n>.json
```

`event` is `COMMENT`, `APPROVE` or `REQUEST_CHANGES`. `line` is the line number in the PR's head
version of the file; a comment on a removed line uses `"side": "LEFT"` and the base line number.

**`azure-devops`** — against the repo project and repository:

1. **One thread per inline comment** through `mcp__ado__repo_pull_request_thread_write`, each
   carrying the file path and the line.
2. **One summary thread** through `mcp__ado__repo_pull_request_thread_write`, with the summary
   comment, **posted last**: only after every inline thread has landed. Azure DevOps lists the
   newest thread first, so the summary stays on top only when it lands last. The inline threads
   may post in parallel.
3. **The vote**, through the reviewer-vote action of `mcp__ado__repo_pull_request_write`:

   | Verdict | Vote |
   |---|---|
   | Comment | no vote |
   | Approve | Approved |
   | Request changes | Waiting for author |

**Never set a thread status.** Every thread, the summary included, takes the Azure DevOps default
(`Active`), and the author resolves it. A summary created as `Closed` hides an item the reviewer
wants done before merge.

Before posting on `azure-devops`, write the drafts to `<scratchpad>/review-<id>.md` as well, so
they survive a failure.

**A post that fails is a stop.** Say what failed and name the scratchpad path that holds the
drafts, so nothing is lost. Never retry a partial post on `azure-devops` without telling the
reviewer which threads already landed.

**The final print**: the review URL, the verdict, and the number of inline comments.

## Re-review

**Detection**: the reviewer's own comments or reviews are already on the PR (read in step 2 of
`## Reading`). Before anything else, say it and ask one question:

> *"This looks like a re-review: you already commented on this PR. Do you want a delta pass, over only what changed since your last review, or a full pass?"*

A full pass runs `## Reading` from step 3 as usual. **On a delta pass**, find the base:

- **`github`**: the base is the `commit_id` of the reviewer's latest review —
  `gh api --paginate repos/<owner>/<repo>/pulls/<n>/reviews`, filtered to the reviewer's login,
  latest `submitted_at`. The diff is:

  ```bash
  gh api repos/<owner>/<repo>/compare/<base>...<head> -H "Accept: application/vnd.github.diff"
  ```

- **`azure-devops`**: the base is the date of the reviewer's last comment. The delta is the commits
  pushed after that date, read from the PR's commits and iterations through the MCP.

**When neither gives a clean base** — no review with a commit id, a force-push that orphaned the
base so the compare fails, no dated comment — **fall back to a full pass and say so.**

Then read steps 4 and 5 of `## Reading` for the files the delta touches.

**The delta walkthrough has three sections**, replacing the five:

1. **What changed since** the base.
2. **Which earlier comments the changes answer**, each named by file and line.
3. **Which earlier comments stay open.**

**The buckets then hold only new findings.** An earlier comment the author ignored is listed as
still open in section 3, **never re-filed as a finding**.

**Nothing is posted to record the reviewed commit.** The base is read from the tracker on the next
pass, never written.

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
