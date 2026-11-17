---
name: proposal-review
description: >
  Walk a human reviewer through one pull request in a proposal or standards repo (RFCs, standards,
  tech radar, ADR-style records that bind other projects) by the proposal's effect on the projects
  it governs: confirm the affected repos and the claims to check, check each claim in those repos
  through the tracker API, corroborate every fact in the main thread, sort the findings into
  priority buckets, discuss the ones the reviewer picks, and post one review in the reviewer's voice
  only after the reviewer approves the whole batch. Read-only towards every project. Runs on user
  invocation only; no loop invokes it. Invoke /lk:proposal-review [<pr>]
disable-model-invocation: true
---

# proposal-review

**Help one human review one proposal by what it does to the projects it governs, and post exactly
the review that human approved.**

A proposal repo holds documents that bind other projects: RFCs, standards, a tech radar, ADR-style
records. A pull request there reads as prose, and its own repo's process is easy to check. What it
claims about the projects it governs is not: the duplication it says exists, the setup it proposes
to share, the versions and tooling it assumes. This skill checks those claims in the affected repos
and leads the review with what it found.

**Nothing reaches the reviewer that the main thread did not check itself.** Subagents locate facts;
they never supply them. `## Corroboration` is the rule, and every section below obeys it.

**It is read-only towards every project.** It writes nothing into the proposal repo or into any
affected repo: no file, no branch, no configuration. It reads affected repos through the tracker
API only, never through a local clone, and never pulls. What a pass produces lives on the tracker,
as one review on the proposal PR, and nowhere else.

**It builds on automated reviewers and on the proposal repo's own process; it does not replace
them.** Process conformance is a secondary section. The effect on the projects leads.

**It runs on user invocation only.** No loop invokes it — not `work-on-prd`, not `work-on-spec`,
not `sprint-plan`'s night run — and nothing else may.

## Invocation and input

`/lk:proposal-review [<pr>]`

Before resolving the PR, read `../references/pr-review-posting.md` §Invocation and input.

## Project facts

Before the first read, read `../references/pr-review-posting.md` §Project facts.

The tracker those facts name is the tracker for **every** repo this pass reads. An affected repo
the same tracker's tools cannot reach is listed **not reachable** — a flag, not a stop.

## Corroboration

**A subagent report is a list of places to look, never a source of facts.** The main thread
reproduces each fact before it reaches the walkthrough, a bucket or a draft:

| The report says | The main thread |
|---|---|
| **confirmed** or **contradicted**, at `repo:path:line` | re-reads that `repo:path:line` itself, at the commit SHA the pass reads |
| **not found** | re-runs the subagent's key search itself; "not found" stands only if it comes back empty again |
| a web source behind a walkthrough line or a finding | fetches that source itself |

**A fact the main thread cannot reproduce is dropped** from the table, the buckets and the drafts,
and listed in the walkthrough's flags as **reported, not reproduced**, with what the report said and
what the re-read showed.

This covers every row of the claims table and every cited web source, not only the facts a finding
rests on.

## Reading

**Identify the reviewer first.** Re-review detection needs it.

- `github`: `gh api user --jq .login`
- `azure-devops`: the signed-in identity of the MCP server, as the server exposes it (discover and
  announce the tool when it is not obvious).

Then read the proposal PR in the main thread, in this order:

1. **The PR description and what it links** — the issue, the ticket, the discussion. Follow each
   link one level.
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

   **Wrong-skill stop.** When the diff contains code, or the documents name no other project, stop
   and say so in one line, suggesting `/lk:human-review <pr>` instead. Nothing else runs.
4. **The proposal repo's own process document and standards** — the file that says how a proposal
   is written, reviewed and accepted (a `README`, a `CONTRIBUTING`, a template, a process RFC), and
   any standard the proposal must follow. Read them from the tracker at the default branch. None
   found is a flag.

**Intent comes from the PR alone**: its description, its links, its comments. Never from the
conversation, from memory, or from a guess at what the author meant.

**Anything missing outside the diff is a flag, never a stop.** A dead link, a linked item the
session cannot reach, no process document: note it, and list it in the walkthrough under the
section it affects. The diff and the PR itself are the only reads whose failure stops the pass.

## The confirm message

**One message, numbered 1–6, prefilled by the skill. No subagent runs before the reviewer
answers.** A wrong claim list wastes the whole read phase, so it is settled first. The reviewer
replies **"ok"**, or corrects items by number; apply the corrections and continue without asking
again unless a correction leaves a mapping unclear.

1. **This is a proposal review** — one line on what the proposal decides.
2. **The affected repos** — the review's scope. Derive each one from the names in the proposal by
   searching the proposal repo's organisation:
   - `github`: `gh search repos <name> --owner <owner> --json fullName,description,isArchived`, and
     `gh repo view <owner>/<candidate> --json name,description,defaultBranchRef` to settle a
     candidate.
   - `azure-devops`: the repositories of the organisation through `mcp__ado__repo_repository`.

   One clear match is listed as `owner/repo` (or the ADO repository). **Whenever a mapping is
   unclear** — no match, several matches, an archived match — list the name with its candidates and
   ask in this item. Never guess a repo. A repo the tracker's tools cannot reach is listed **not
   reachable**.
3. **Branches to read besides the default branch**, per repo. Prefilled with `none`, or with a
   branch the proposal names.
4. **Related open PRs** in the proposal repo, listed by the skill for the reviewer to pick:
   - `github`: `gh pr list --repo <owner>/<repo> --state open --json number,title,url,author`
   - `azure-devops`: active pull requests of the repository through `mcp__ado__repo_pull_request`.

   Exclude this PR. Prefilled with `none picked`.
5. **Research on the web** — the approach to research, or `none`. Prefilled with a one-line
   suggestion when the proposal adopts a practice or a tool others have tried, and `none`
   otherwise.
6. **The claims to check**, each with an id (`C1`, `C2`, …) and the repos it applies to:
   - the duplication or the problem the proposal states;
   - the setup it proposes to share;
   - the versions and tooling it assumes;
   - the candidates it lists for later.

```markdown
## Proposal review — <PR title> (#<n>)

1. **Proposal review.** <what it decides, one line>
2. **Affected repos (scope).** `<owner>/<repo>`, `<owner>/<repo>`, … <unclear: "<name>" → `<a>` or `<b>`?> <not reachable: …>
3. **Branches besides the default.** `<owner>/<repo>`: `<branch>` · … — or none
4. **Related open PRs.** #<n> <title> · #<n> <title> — none picked
5. **Web research.** <the approach> — or none
6. **Claims to check.**
   - **C1** <claim> — <repos>
   - **C2** <claim> — <repos>

Reply "ok", or correct by number.
```

## Checking the claims

**Every read of an affected repo goes through the tracker API**, at the default branch, plus any
branch item 3 names. Never a local clone, never a pull, never a checkout.

- `github`: `gh api repos/<owner>/<repo>/contents/<path>?ref=<ref>` for a file and `gh search code`
  for a search.
- `azure-devops`: the ADO MCP repo-file tool for a file and its code-search tool for a search.

**Pin the commit first.** Before any subagent runs, resolve the head SHA of each branch to read
(`gh api repos/<owner>/<repo>/commits/<branch> --jq .sha` on `github`; the branch's latest commit
through `mcp__ado__repo_branch` on `azure-devops`). Every read in the pass, the subagents' and the
main thread's, uses that SHA as the ref, so a re-read sees what the subagent saw and a permalink
points at the evidence.

**Code subagents: up to 3, split by claim, not by repo.** Each runs as `general-purpose` with
`model: sonnet`. Group the confirmed claims into at most three sets and brief one subagent per set
with:

- its claims, by id and text, and the repos each applies to;
- each repo's branches and pinned SHAs, and the tracker's read tools above as the **only** tools it
  may use on those repos;
- a cap of **about 15 file reads per claim**;
- the return shape: per claim and repo, the result — **confirmed**, **contradicted**, **not found**
  or **not checked** — the `repo:path:line` and the quoted line, **no opinion**, and **every search
  it ran**, verbatim.

**Search covers the default branch only.** On a named branch a search proves nothing, so a claim
there that file reads did not settle is **not checked on `<branch>`**, never **not found**.

**Web research**: when the reviewer agreed to item 5, spawn **one** `web-researcher` with
`model: sonnet`, in parallel with the code subagents. Brief it with the approach item 5 names and
the proposal's decision. It returns common practices, known failure modes and sources. A
discussion-time research outcome later continues this same researcher through `SendMessage` rather
than spawning a second; when no research ran up front, that outcome spawns the one researcher then.

**Related PRs**: for each PR the reviewer picked in item 4, read the description and the diff in
the main thread, and **not their links**. A conflict between a related PR and this proposal becomes
a finding.

**Then corroborate**, per `## Corroboration`, before anything is written to the reviewer.

## The walkthrough and the buckets

**One message holds the walkthrough and the buckets.** When the walkthrough is wrong, the reviewer
corrects it in the reply and the skill re-buckets.

The walkthrough has **five fixed sections, in this order**:

1. **The proposal** — what it decides, with **one concrete before/after scenario in an affected
   project**: *"Before: the `billing` service pins its own lint config and drifts from the others.
   After: it extends the shared config and a rule change lands everywhere at once."*
2. **Effect on the projects** — one row per claim and repo: the claim, the repo, the result
   (**confirmed**, **contradicted**, **not found**, **not checked**) and the `repo:path:line`. A
   **not found** row names the searches that came back empty, so the reviewer can trust or dispute
   it. A repo the reviewer removed in item 2 shows **not checked, outside scope**.
3. **Industry practice** — only when research ran: the practices and failure modes the main thread
   reproduced, each with its source.
4. **Process conformance** — the proposal against the repo's own process document and standards.
5. **Already said** — what humans and bots already raised, listed separately by account type:
   - `github`: a **bot** is an author whose `type` is `Bot`, or whose login ends in `[bot]`;
     everything else is a human.
   - `azure-devops`: a **bot** is a service identity; everything else is a human.

An empty section prints `none`, never disappears.

Below the walkthrough, **five lists, each item with an id**:

| List | Ids | What goes in it |
|---|---|---|
| High | `H1`, `H2`, … | a contradicted claim the proposal depends on |
| Medium | `M1`, `M2`, … | a contradicted side claim; a process issue; a conflict with a related PR |
| Low | `L1`, `L2`, … | a process issue that is a thought or a preference |
| Questions to the author | `Q1`, `Q2`, … | a **not found** claim, and what the reviewer cannot judge without the author |
| Praise | — | what the proposal does well, only when sincere |

**A process issue never reaches High** unless the reviewer raises it there.

**Every finding anchors on a line of this proposal** — the `<file>:<line>` in the PR's diff that
makes the claim — and cites the evidence `repo:path:line` beside it. A conflict with a related PR
anchors on this proposal's line too, and names the related PR.

**Questions are not findings.** They stay out of the three buckets.

**Never repeat a point an existing comment already made.** Where a finding extends an existing
comment, say so and build on it — *"extends `<login>`'s point on `<file>`: …"* — instead of filing
it as new.

```markdown
## <PR title> (#<n>)

**The proposal.** <what it decides>. Before: <in `<repo>`, …>. After: <…>.

**Effect on the projects.**

| Claim | Repo | Result | Evidence |
|---|---|---|---|
| C1 <claim> | `<owner>/<repo>` | contradicted | `<repo>:<path>:<line>` |
| C2 <claim> | `<owner>/<repo>` | not found | searched: `<query>`, `<query>` |
| C3 <claim> | `<owner>/<repo>` | not checked on `<branch>` | — |

**Industry practice.** <practice or failure mode> — <source>; … — or none

**Process conformance.** <…> — or none

**Already said.** Humans: <login> on <file:line>: <point>; … Bots: <login>: <point>; …

<flags: not reachable, reported, not reproduced, no process document, dead link, … — only when any>

### High
- **H1** `<file>:<line>` — <claim> is contradicted by `<repo>:<path>:<line>`: <what the code shows>.
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

## The discussion

Before the first finding is discussed, read `../references/pr-review-posting.md` §The discussion.

## The drafts and the post

Before the drafts, read `../references/pr-review-posting.md` §The drafts and the post, including
§Posting.

**Each posted contradicted claim carries one permalink to its evidence**, at the commit SHA the
pass read — never a branch link, which drifts:

- `github`: `https://github.com/<owner>/<repo>/blob/<sha>/<path>#L<line>`
- `azure-devops`: `https://dev.azure.com/<org>/<project>/_git/<repository>?path=/<path>&version=GC<sha>&line=<line>&lineEnd=<line>&lineStartColumn=1&lineEndColumn=1`

## Re-review

On detection, read `../references/pr-review-posting.md` §Re-review: the question, the full-pass
route, and the delta base with its fall-back to a full pass. A full pass runs `## Reading` from
step 3, then the confirm message, as usual.

**On a delta pass**, read the delta diff, then send the confirm message with item 6 split in two:
the claims the delta adds or changes, which are the only ones checked again, and the claims it
leaves alone. Subagents run for the first group only.

**The delta walkthrough has four sections**, replacing the five:

1. **What changed since** the base.
2. **Effect on the projects** — the re-checked claims as in a full pass. Every other claim carries
   its earlier result, as the reviewer's earlier comments on the PR record it, marked **from the
   last pass, not checked again**; a claim no earlier comment records shows **from the last pass,
   not recorded**.
3. **Which earlier comments the changes answer**, each named by file and line.
4. **Which earlier comments stay open.**

**The buckets then hold only new findings.** An earlier comment the author ignored is listed as
still open in section 4, **never re-filed as a finding**.

The discussion, the drafts and the post are unchanged.

## What it never does

- **Never writes into any project** — not the proposal repo, not an affected repo.
- **Never reads a local clone, checks out a branch or pulls.** Affected repos are read through the
  tracker API only.
- **Never posts a fact the main thread did not reproduce.** A subagent's report locates; it does not
  attest.
- **Never posts the research as is.** At most one claim and one link from it reach the summary.
- **Never spawns more than the 3 code subagents and 1 web researcher.**
- **Never runs a subagent before the reviewer answers the confirm message.**
- **Never guesses a repo.** It asks whenever a mapping is unclear.
- **Never reads a related PR's links.** Description and diff, one level.
- **Never posts a label, blocking wording, a hash, an id or a marker.** The SHA inside an evidence
  permalink is the one exception. The blocking signal, when any, lives once in the summary comment,
  in words.
- **Never posts per draft or partly.** One batch, one yes, one review.
- **Never posts a finding the reviewer did not look at.**
- **Never reads anything in the adapter beyond `## Repo`, and never adds an adapter row.**
- **Is never invoked by a loop.** On demand only.
