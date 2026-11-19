---
name: pr-feedback
description: >
  Pull the review feedback on the author's own pull request and triage it: fetch inline review
  threads, review bodies and conversation comments from humans and bots, strip bot noise, extract
  findings buried in review bodies, check each finding against the checked-out code, and end with a
  triage table and a proposed next step. Read-only: it edits nothing, posts nothing and resolves
  nothing; the author decides what happens next. Use when the author asks for the feedback, the
  comments or the bot review on their PR. Invoke /lk:pr-feedback [<pr>]
---

# pr-feedback

**Show the author what reviewers said on their own pull request, what of it is real, and what to do
about it. Then stop.**

`lk:human-review` and `lk:proposal-review` serve the reviewer. This skill serves the author: the
feedback has arrived, and the author wants it sorted. The skill fetches every comment, removes the
noise, checks each finding against the code, and proposes which findings to fix and which to answer
with a reply. **The author drives from there.** Fixing, replying and resolving are ordinary work the
author asks for afterwards, outside this skill.

**It is read-only.** It edits no file, makes no commit, posts no comment or reply, resolves no
thread and casts no vote. It does not draft replies, so it never calls `lk:scribe`.

**The main thread reads the code itself.** A verdict on a finding rests on the code at that line,
so the session that gives the verdict reads it first-hand. No subagent reads code.

## Invocation and input

`/lk:pr-feedback [<pr>]`

Before resolving the PR, read `../references/pr-review-posting.md` §Invocation and input.

## Project facts

Read the **project adapter** at `<repo-root>/.claude/project/adapter.md`, section `## Repo`, and
**nothing else in the adapter**:

| From `## Repo` | What for |
|---|---|
| the `Tracker:` line | `github` or `azure-devops`; **absent means `github`** |
| `github` sub-section → *Issue tracker / PRs* | `<owner>/<repo>`, where the PR lives |
| `azure-devops` sub-section → *Organisation*, *Repo project*, *Repository* | where the PR lives — the **repo project**, never the work-item project |

**No adapter file means `github`**, with `<owner>/<repo>` from
`gh repo view --json nameWithOwner --jq .nameWithOwner`. The skill runs in repos that were never
wired, and the remote is enough to find a GitHub PR. On `azure-devops` without an adapter, a PR URL
carries everything needed; with neither, stop and ask for the PR URL.

**This skill introduces no adapter row and no adapter section.** Bots are told apart by account
type (`## Sifting`), and the author's identity comes from the tracker.

**On `github`** every read goes through `gh`. **On `azure-devops`** every read goes through the
Azure DevOps MCP server's `mcp__ado__repo_pull_request*` tools, against the repo project and
repository. Tool and parameter names vary by server version; where a named tool, action or field is
missing, discover the equivalent from the running server and announce the substitution. A read that
cannot be performed at all is a stop, never a silent omission.

## Branch check

**Before any code is read**, the checked-out code must be the code the reviewers saw.

1. **The PR's head branch is the checked-out branch.** Compare `git branch --show-current` with the
   PR's head branch (`headRefName` on `github`; the source branch on `azure-devops`). When they
   differ, stop:

   > *"PR #`<n>` is on `<pr-branch>`, but `<current-branch>` is checked out. Check out `<pr-branch>` and run me again."*

2. **The local `HEAD` is the PR's head commit.** Run `git fetch origin <pr-branch>`, then compare
   `git rev-parse HEAD` with the PR's head sha (`headRefOid` on `github`; the last merge source
   commit on `azure-devops`). When they differ, use `git rev-list --left-right --count
   HEAD...origin/<pr-branch>` to name the state, and stop:

   | State | Message |
   |---|---|
   | behind | *"Your branch is `<n>` commits behind the PR. Pull the latest and run me again."* |
   | ahead | *"Your branch has `<n>` commits the PR does not have. Push them, or tell me to read the PR as it is on the remote."* |
   | diverged | *"Your branch and the PR have diverged (`<a>` local, `<b>` remote). Sync them and run me again."* |

**The skill never pulls, pushes, rebases or checks out.** It names the state and the author acts.

## Reading

**Read everything in the main thread, and paginate every list.** A bot that posts many comments
spills past the first page, and a finding on page two is as real as one on page one.

**Identify the author first**, for the `replied` mark:

- `github`: `gh api user --jq .login`
- `azure-devops`: the signed-in identity of the MCP server, as the server exposes it.

Then read three sources.

**`github`:**

1. **Review threads**, with their resolution state. Only GraphQL exposes it:

   ```bash
   gh api graphql --paginate -F owner=<owner> -F repo=<repo> -F n=<n> -f query='
     query($owner:String!,$repo:String!,$n:Int!,$endCursor:String){
       repository(owner:$owner,name:$repo){ pullRequest(number:$n){
         reviewThreads(first:50, after:$endCursor){
           pageInfo{ hasNextPage endCursor }
           nodes{ isResolved isOutdated path line originalLine
             comments(first:50){ nodes{ author{ login __typename } body url createdAt } } } } } } }'
   ```

2. **Review bodies**: `gh api --paginate repos/<owner>/<repo>/pulls/<n>/reviews`.
3. **Conversation comments**: `gh api --paginate repos/<owner>/<repo>/issues/<n>/comments`.

**`azure-devops`:** the PR's threads through `mcp__ado__repo_pull_request_thread`. A thread whose
status is `Active` or `Pending` is open; every other status (`Fixed`, `Closed`, `WontFix`,
`ByDesign`) is resolved. A thread with a file context is an inline thread; one without is a
conversation comment. System threads — votes, pushes, policy and status updates — are noise.

## Sifting

**What is a finding**: a point a reviewer raised about the change that the author has not settled.
Everything else is either a mark on a finding or noise.

**Account type** tells a bot from a human. No adapter row and no list of bot names:

- `github`: a **bot** is an author whose `__typename` (or `type`) is `Bot`, or whose login ends in
  `[bot]`; everything else is a human.
- `azure-devops`: a **bot** is a service identity; everything else is a human.

**The rules, in order:**

1. **Skip resolved threads.** They are settled.
2. **Mark an outdated thread `outdated`** (`isOutdated` on `github`; on `azure-devops`, a thread
   whose file context no longer maps to the current iteration, when the server exposes it). Keep it:
   the code moved, but the point may still hold.
3. **Mark an open thread `replied`** when its last comment is the author's. Keep it: the reviewer
   may not have answered.
4. **Strip bot markup** before reading a bot's text: `<details>` and `<summary>` wrappers, HTML
   comments and hidden markers, badges, and collapsed sections. Read what is inside a collapsed
   section; that is often where the findings are.
5. **Extract findings embedded in review bodies and summary comments** as separate items, each with
   its file and line: sections such as "additional comments", "outside diff range", "nitpicks" and
   "duplicate comments". These sit outside the inline threads and are the ones most easily missed.
6. **Drop noise silently**: deploy previews, security or dependency scan passes, CI and coverage
   status, release-note poems, change walkthroughs and summaries that carry no finding, and
   acknowledgements ("thanks", "LGTM"). Count what was dropped; the report gives the count in one
   line.
7. **Merge duplicates.** Two reviewers on the same line making the same point are one item that
   names both sources.

## Checking

For each finding, in the main thread:

1. **Read the code at the line** in the working tree, and one hop around it: the function a line
   calls, the callers of a changed signature, the type a change widens. **Never a repo-wide read.**
2. **Read the `CONTEXT.md` of the touched directory**, through `lk:scoped-context`, when one exists.
   A missing `CONTEXT.md` is not a flag; most directories have none.
3. **Look for precedent in sibling code.** When the sibling component, handler or test does the
   same thing, say so: it is a common and valid reason to answer rather than fix, or to fix both
   together.
4. **Give a verdict**:

   | Verdict | Meaning |
   |---|---|
   | real | the point holds against the code |
   | false positive | the point does not hold; name why — for example, the bot matched on a name only, or read the old version of the line |
   | already handled | the current code already addresses it |
   | unsure | reading cannot settle it; name what would (a run, a test, the reviewer's answer) |

5. **Give a severity** to a real finding: **High** (a correctness bug, a security issue, a broken
   contract), **Medium** (should change, but the PR can merge without it), **Low** (a preference or a
   nit).
6. **Propose an action**:
   - **fix**: a real finding the author should change in this PR.
   - **reply**: everything else — a false positive, an already-handled point, a precedent, a nit the
     author can decline, an unsure point that needs the reviewer's answer, a real finding better
     deferred. The reason says what the reply would be about; the skill does not draft it.

## The report

**One message, in this shape**, then stop and wait for the author:

```markdown
## <PR title> (#<n>) — branch in sync at `<short sha>`

| id | source | where | finding | verdict | severity | action | reason |
|---|---|---|---|---|---|---|---|
| F1 | `<login>` (bot) | `<file>:<line>` | <the point, one line> | real | High | fix | <one line> |
| F2 | `<login>` (human) · replied | `<file>:<line>` | <…> | false positive | — | reply | <one line> |
| F3 | `<login>` (bot) · outdated | `<file>:<line>` | <…> | already handled | — | reply | <one line> |

**Proposed next step.** Fix F1 and F4 in one commit: <why they belong together>. Reply on F2 and F3:
<what the replies would say, in a few words>.

Dropped `<N>` items as noise (<the kinds, e.g. deploy preview, scan pass, walkthrough>).
```

- The `source` cell carries the `replied` and `outdated` marks.
- A finding with no file and line (a general point in a review body or the conversation) takes `—`
  in the `where` cell.
- **High rows come first**, then Medium, then Low, then the rest.
- **An empty table prints `none`**, with the noise line still below it.
- When the PR has no unresolved feedback at all, say so in one line and stop.

## What it never does

- **Never edits a file, commits, pushes, pulls, rebases or checks out.** The branch check names the
  state; the author syncs.
- **Never posts, replies, resolves a thread or votes**, on either tracker.
- **Never drafts a reply and never calls `lk:scribe`.** When the author asks for a reply afterwards,
  that is a new request.
- **Never spawns a subagent to read code.**
- **Never runs the app or the tests.** A point that only a run can settle gets the verdict `unsure`.
- **Never reads anything in the adapter beyond `## Repo`, and never adds an adapter row.**
- **Never names a bot to filter on.** Account type tells bots from humans; content tells noise from
  findings.
