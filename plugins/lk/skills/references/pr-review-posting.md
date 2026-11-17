# PR review: resolution, project facts, discussion, drafts and post

The steps `lk:human-review` and `lk:proposal-review` share. Each skill points here at the step that
uses a section. This file holds only what is identical in both skills.

## Invocation and input

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
carries the alternative and one link into the summary comment.

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

**Every posted text is drafted through `lk:scribe`**: the inline comments and the summary
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

**Nothing is posted to record the reviewed commit.** The base is read from the tracker on the next
pass, never written.
