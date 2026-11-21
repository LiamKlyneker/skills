---
name: prove-branch
description: Run the automated QA pass on the checked-out branch of a web project. It resolves the ticket, the pull request and the preview deployment from the branch alone, and reads the acceptance criteria from the highest product source the branch reaches. It maps the diff to the touched pages, tracing changed shared code by symbol to a sample of the pages that render it, and derives a page's KNOWLEDGE.md where it is missing or stale. It resolves the data each flow starts from, in user words, to an item an earlier run made, an item a recipe in the project's QA folder makes on staging, or a link from the developer, learning a missing recipe from the code, the screens and the developer while writing nothing to staging. After one approval gate it makes those items under write rules, drives the flows against one target per app, grades the evidence in a cold context, records every item it made, and posts one receipt to the ticket, or to the pull request when the branch names none. It stops with a question wherever the branch is ambiguous, and on a failure asks fix now or file. It never needs qa:setup-env to have run. Runs on user invocation only; neither loop ever invokes it. Invoke /qa:prove-branch with no argument, in a fresh session on the implemented branch.
disable-model-invocation: true
---

# prove-branch

**Prove the branch from the branch.** A developer opens a fresh session on a branch whose
implementation is finished and runs `/qa:prove-branch` with **no argument**. Everything the pass
needs — the ticket, the pull request, the preview deployment it runs against, the acceptance
criteria it proves — is found from the checked-out branch and the project adapter. Where the branch
does not say exactly one thing, the skill **stops and asks**; it never guesses.

**It is an external tester.** It writes nothing into the project under test: no test ids, no spec
files, no fixtures, no configuration, no feature-flag overrides committed anywhere, no app code. The
project's tracked tree is the same after a run as before it, except for a touched page's
`KNOWLEDGE.md`, which the run derives or regenerates when it must (`## Knowledge`) and never commits. What a run produces lives on the
tracker and in folders git excludes. The one change a pass can lead to is a fix-now commit the
developer asks for after grading, which a worker makes (`## On a Fail`).

**It makes the data a flow starts from, and only after the gate.** It reads what the project
already knows — each touched page's `KNOWLEDGE.md`, and the recipes and the made-items file in the
project's QA folder — and starts every flow from an item an earlier run made, or from one a recipe
makes now on staging (`## Arranging`) — learning a recipe it does not have first (`## Learning a
recipe`) — or, where the project forbids staging writes or no recipe makes the item, from a link the
developer gives at the gate. An arrange driver makes each item under the write rules of
`## Driving` → *The write rules*, and the receipt lists every item the run made. Its writes to a
knowledge file are the derive of a touched page's file (`## Knowledge`) and a developer's own answers,
written back (`### Write-backs`), so no run asks the same thing twice.

**It runs on user invocation only.** Neither `work-on-prd` nor `work-on-spec` invokes it, and
nothing else may: ADR 0012 keeps every QA pass on demand, and ADR 0020 applies that to this
plugin.

**A fresh session.** The pass judges the branch as built, so it starts from the branch and the
tracker, never from the conversation that wrote the code.

## Project facts

Every project-specific value comes from the **project adapter** at
`<repo-root>/.claude/project/adapter.md` — read it; never hardcode one here. This skill reads five
sections and nothing else:

| Adapter section | What for |
|---|---|
| `## Repo` | the `Tracker:` line (absent means `github`), which decides the resolver keys and where the run's pull request lives; the optional `Ticket source:` line, which decides where the ticket is read and what key 4 looks for; the default branch; the tracker sub-section's locators — on `github` the *Issue tracker / PRs* row, on `azure-devops` the *Organisation*, *Work-item project*, *Repo project*, *Repository* and *Title prefixes* rows |
| `## Commands` | the read-only and verify commands the skill may run without asking |
| `## Verify ladder` | what a sub-step must name to be executable, and what the skill can verify without a human |
| `## QA` | the rows below, by name |
| `## Sources of truth` | the **project explorer agent** for on-demand elaboration and for the trace of shared code to the pages that render it (`### Shared code`) — `Explore` where it says None |

From `## QA`, by row name:

| Row | What for |
|---|---|
| *Session method* | how a flow signs in — `api` against the endpoint written after the value, or `manual` |
| *Credential environment variables* | per role, the **names** of the variables holding its username and password. Read them from the backticked tokens: roles are unquoted labels separated by ` · `, each followed by `→` and two backticked variable names, and everything after the em dash is guidance. The skill reads only names here and **never reads a credential value from the adapter** |
| *Staging URL* | the base URL of this app's staging environment, where an arrange driver makes an item of this app (`## Arranging`) |
| *QA folder* | the folder that holds the project's recipes and its made-items file; `.claude/project/qa/`, beside the adapter, when the row is absent (`### The QA folder`) |
| *Staging writes* | optional: `yes` or `no`; absent or any other value reads as `no`. Only `yes` lets a run make an item on staging; on `no` the run arranges nothing and asks the developer for links (`### Resolve each flow's data`) |
| *Sibling apps* | optional: the other apps of the product, each with its repo folder name, its staging URL and the roles that belong to it (`### Which role and which app`). This skill is the row's only writer (`## Learning a recipe` → *Recording a sibling app*) |
| *Preview URL pattern* | how the pull request's preview deployment URL is formed, or `pr-comment` — read in `## The target` |
| *Preview basic auth* | optional: the **names** of the two variables holding the HTTP Basic Auth in front of the preview — read as [`browser-readiness.md`](../references/browser-readiness.md) → *Preview Basic Auth* says |
| *Feature-flag override* | how one session turns a flag on or off, or `none` |
| *Browser automation consent* | read as [`browser-readiness.md`](../references/browser-readiness.md) → *Consent* says |

A missing `## QA` section stops the run at `## The target`, after the run is resolved, so the stop
can name the branch it was run on.

`[PRD]`, `[SPEC]` and `[FINDINGS]` below are shorthand for the adapter's *Title prefixes* row. On
`azure-devops` the prefix is load-bearing, so read it from the row; if the row names different
prefixes, they win.

On `azure-devops` the work-item and pull-request reads go through the Azure DevOps MCP server
(`mcp__ado__*`). Tool and parameter names vary by server version; where a named tool or field is
missing, discover the equivalent from the running server and announce the substitution. A read that
cannot be performed at all is a stop, never a silent omission.

## Pending mode

When at least one adapter section has, as its whole body, the line
`Pending: this repo has no code yet. Run /<plugin>:setup again after the first code lands.`, this step cannot run: it needs
the adapter's verify commands. Change nothing, print this line, and stop. There is no scaffold exception.

> Pending mode: this step needs the adapter's verify commands, and they do not exist until the first code lands. Run /qa:setup again, then run this step again.

## Resolving the run

The run is two things: the **ticket** the run is anchored to — the item the receipt, the findings
and a fix-now commit name — and the **pull request** the preview deployment belongs to. Both are
found from the branch. The criteria come from the product source the ticket reaches, which
`## Criteria` finds; a branch that names no ticket still runs, on its pull request alone.

### First, read the branch

First fetch the default branch, `git fetch origin <default-branch>`, with `<default-branch>` from
`## Repo`. A fetch moves only the remote-tracking ref, never the working tree, so it needs no yes. A
fetch that fails is a stop: say so. **Every range in this skill compares against
`origin/<default-branch>`, never the local ref.** A local default branch behind the remote puts
commits that already merged into the range, and their `(#N)` suffixes read as tickets.

Then three reads, all read-only, before any key is tried:

- the branch: `git branch --show-current`. An empty result is a detached `HEAD` — stop, say so.
- the commit subjects on the branch: `git log origin/<default-branch>..HEAD --format='%s'`.
- the **open pull requests whose head is this branch**:
  - `github`: `gh pr list --repo <owner>/<repo> --state open --head <branch> --json number,headRefName,headRefOid,title,body,url`
  - `azure-devops`: `mcp__ado__repo_pull_request` listing active pull requests whose source branch
    is `refs/heads/<branch>`, against the **repo project** and **repository** — never the
    work-item project.

None of these is a stop on its own result. A branch with no pull request still runs the keys, so
the stop that follows can say everything the branch did and did not carry.

### Four keys, in order

Try the keys in this order. **The first key that yields exactly one hit wins**, and no later key is
tried. A hit is one distinct ticket: three commits carrying the same `(#12)` are one hit, and two
commits carrying `(#12)` and `(#13)` are two.

1. **`PRD: #<n>` in the pull request's body** — `github` only. A whole line of the open pull
   request's body, the machine block's resume key that `work-on-prd` writes:

   ```bash
   gh pr list --repo <owner>/<repo> --state open --head <branch> --json number,body \
     --jq '.[] | {number, prd: [.body | split("\n")[] | select(test("^PRD: #[0-9]+[ \t\r]*$")) | capture("#(?<n>[0-9]+)").n]}'
   ```

   **Match the whole line, never a substring** — `PRD: #12` is a prefix of `PRD: #127`, and a
   substring match hands you somebody else's run. The hit is the PRD `#<n>`, and the pull request
   is the one whose body carried it.

2. **The `[SPEC]`'s `ArtifactLink` to the pull request** — `azure-devops` only. For the open pull
   request on this branch, read its linked work items, and fetch each with `mcp__ado__wit_work_item`
   (`action: "get"`), `expand: "relations"` and **no** `fields` filter — the two are mutually
   exclusive, and a filter suppresses relations. Keep a work item when its title carries the
   `[SPEC]` prefix **and** its relations carry an **`ArtifactLink`** named `Pull Request` whose url
   is a `vstfs:///Git/PullRequestId/…` artifact id with **the pull-request id as its last segment**.
   `work-on-spec` puts that link on the `[SPEC]` when it opens the pull request, so the link is the
   `[SPEC]`'s own statement of which run is its. The hit is that `[SPEC]`.

3. **A `(#N)` suffix on the branch's commit subjects** — every tracker. A subject ending in `(#N)`
   is a commit for ticket `N`; the orchestrators and `work-on-task` write it as the last characters
   of the subject. The hit is ticket `N`.

4. **The ticket-source key** — every tracker. The ticket key that `../_shared/ticket-source.md` §3
   names for the system the adapter's `Ticket source:` line selects, or the `Tracker:` line where
   there is no `Ticket source:` line: for `jira`, an issue key in the form §2 accepts (`ABC-123`);
   for `azure-devops`, an `AB#<id>` work-item mention. For `github` the key is the issue number,
   which is key 3's shape — a bare number found in free text is not a ticket key, so this key adds
   nothing there and reports itself as such.

   Read the key only from the places that **declare** which ticket the branch implements:

   - the open pull request's title;
   - the branch's commit subjects;
   - a **label line** in the open pull request's body — a whole line that is a label, a colon and
     the key, and nothing else, such as `Jira: ABC-123` or `Ticket: AB#4512`;
   - for `jira` only, the branch name, where the key is a whole token: `ABC-123-fix-foo` and
     `feature/ABC-123` carry `ABC-123`, and `ABC-1234-x` does not carry `ABC-123`.

   The hits are the distinct keys across all four places together, never one place at a time. A
   title and a commit that name the same key are one hit, and a title and a commit that name two
   keys are two, which is a stop. **A key in any other line of the body is not a hit**: prose that
   mentions a related ticket for background or for follow-up work does not say which ticket the
   branch implements. This holds for `AB#<id>` too, although Azure Boards links every mention.

A key that does not apply to this tracker reports `not applicable` and counts as yielding nothing.

### No key wins

When no key yields exactly one hit, the result depends on what the keys and the pull requests
found:

- **Every key found nothing, and the branch has exactly one open pull request** — the run has
  **no ticket**. It is not a stop: the run continues on that pull request, and `## Criteria` reads
  the criteria from it or from the diff.
- **A key found several hits** — a stop. The branch names more than one ticket, and only the
  developer knows which this pass proves.
- **Every key found nothing, and the branch has no open pull request or several** — a stop. There
  is no pull request to anchor the run to, or no way to choose one.

### The stop

Name the branch, say what each key found, and ask the developer which ticket and pull request this
run is for:

```
prove-branch cannot resolve the run for branch `<branch>`.
  open pull requests on this branch: <none | #12 | #12, #15>
  key 1 (PRD: #<n> in the PR body): <none | not applicable | #40, #41>
  key 2 ([SPEC] ArtifactLink): <none | not applicable | …>
  key 3 ((#N) commit suffix): <none | #227, #228>
  key 4 (ticket-source key): <none | not applicable | ABC-12, ABC-14>
  key 4, body prose only, not counted: <none | ABC-9>
Which ticket and pull request should this pass prove?
```

Omit the prose line where key 4 does not apply.

The developer's answer resolves the run; record that it came from the developer, not a key.

A key that resolves the ticket while the branch has **no open pull request, or several**, is also a
stop: name the branch, the ticket and the pull requests found, and ask. A pass with no pull request
has no preview deployment to run against.

### Say what was picked

**Before anything else**, state the ticket and the pull request picked: the ticket (its key and
title), the key that resolved it, and the pull request (number or id, head branch, title).

With no ticket, say `ticket: none`, give each key's result on the stop block's lines, and say that
the criteria come from the pull request's title and body or from the diff alone, every one
`inferred` unless the pull request's body carries an acceptance-criteria list.

## Session hygiene: check and report, stop on anything unexpected

Before reading the target, confirm and say what you found:

- the pull request's head branch is the one checked out (`git branch --show-current`);
- the pull request is open — `github`: `gh pr view <n> --repo <owner>/<repo> --json state,isDraft,headRefOid`; `azure-devops`: the pull request's status from `mcp__ado__repo_pull_request`;
- the tree is clean (`git status --short`);
- the ref every range compares against: `origin/<default-branch>`, fetched in *First, read the
  branch*;
- the pull request's head commit is `HEAD` (`git rev-parse HEAD`) — a local commit that is not
  pushed is a commit the preview cannot have built.

Anything unexpected — a dirty tree, a detached `HEAD`, a closed or completed pull request, the
wrong branch, unpushed commits — **say so and stop for the developer**. The skill runs read-only and
verify commands from the adapter's `## Commands` freely; anything that changes the working tree or
starts a long-lived process it proposes and waits for a yes.

## The target

The pass runs against the pull request's **preview deployment**. **The skill never boots the app.**
A local target happens only when the developer asks for one in this session; the developer starts
it and gives the URL, and the skill uses that URL.

**An adapter with no `## QA` section is a stop**, before any URL is looked for. prove-branch drives
a web preview deployment and nothing else, and a project without the section — a native app, a
library — has none to drive. Say so, and print the command for a web project alone on its line:

```
prove-branch cannot run on `<branch>`: the adapter has no `## QA` section.
prove-branch drives a web preview deployment only. For a web project, add the section with:
/qa:setup
```

**Never ask for a URL in this case**, and never take one offered: the session method and the
credential variables live in the same section, so a URL alone cannot sign a flow in. No receipt is
posted.

1. **Find the URL** from the adapter's `## QA` → *Preview URL pattern* row:
   - a **pattern**: substitute the pull-request number for `<pr-number>`, and confirm the URL
     answers before using it;
   - **`pr-comment`**: read the pull request's comments — `github`: `gh pr view <n> --repo <owner>/<repo> --json comments`; `azure-devops`: the pull request's threads through the MCP — and take
     the preview URL from the most recent comment that posts one.
2. **Read the commit the preview was built from** — the commit the deployment record, the status
   check or the posting comment names for that preview. Compare it with `HEAD`. For a **pattern**,
   when a comment on the pull request posts a preview URL, compare that URL's host with the
   pattern URL's host: the built-from commit a comment names belongs to the comment's URL, not to
   the pattern's.
3. **Stop and ask the developer for a URL** when the section is there but the *Preview URL
   pattern* row is absent, when no URL resolves, when the
   URL does not answer, when the preview was built from a commit other than `HEAD`, when the
   built-from commit cannot be read at all, or when a pattern URL's host differs from the host a
   comment posts. Say which of these it is, and give the URL and commit you found.
   For a pattern URL that does not answer or whose host differs, also give the comment's URL and
   its built-from commit beside the pattern URL, say that the adapter's *Preview URL pattern* row
   looks stale, and name `pr-comment` as a value that follows the comment. Never switch to the
   comment's URL without the developer's answer.

**A `401` that challenges for HTTP Basic Auth is an answer, not a URL that does not answer** — from
a resolved URL or one the developer gave. Apply
[`browser-readiness.md`](../references/browser-readiness.md) → *Preview Basic Auth* → *Detect the
challenge* before anything else, and carry the credentials on every later request against the target.

**Record two values now: the target URL and the SHA tested.** The SHA tested is the built-from
commit when it matches `HEAD`. A URL the developer supplies is recorded with the commit the
developer states it serves, marked `developer-stated`. The receipt names both.

### One target per app

**A run has one target per app.** The app under test is `this app`, and its target is the target URL
above. Each other app is an entry of the adapter's *Sibling apps* row, and its target is the staging
URL that entry gives. The arrange phase drives staging only (`## Arranging`), so an arrange drive,
a check and a screen read open this app at the adapter's *Staging URL* row and a sibling app at its
entry's staging URL.

| App | Target of a flow under test | URL of an arrange drive, a check and a screen read |
|---|---|---|
| `this app` | the target URL — the preview | the *Staging URL* row |
| a *Sibling apps* entry, by its label | the entry's staging URL | the entry's staging URL |

**These URLs are the only origins a driver of this run may open.** The skill gives each driver the
URL of each app its flow names, by app label, and the driver never takes an origin from a page
(`qa-driver` → mandate 9). An app the adapter does not list has no target, and no sub-step is
composed in it. A *Staging URL* row that is absent leaves this app with no arrange URL: a recipe
made in this app then makes its flows Unable to verify, with the reason `the adapter has no Staging
URL row`, and the remedy `/qa:setup`.

## Criteria

**The criteria come from the highest product source the run reaches.** The ticket anchors the run,
but it is not always where the product is described: a `[SPEC]` and its `[TASK]`s are written for
implementation agents, carry mostly code-level criteria, and never restate the product's scope.

Read every item through `../_shared/ticket-source.md` — its one reader per system (§2) and where
each system keeps acceptance criteria. The resolving key decides the system: keys 1, 2 and 3
resolve an item the loop filed, read from the `Tracker:` line (§4), and key 4 resolves a ticket on
the system its key belongs to, read from the `Ticket source:` line. An item reached by walking up
lives on the same system as the item it was reached from.

### The ladder

Take the first rung the run reaches:

1. **The product source** — the item that says what the user gets:
   - a `jira` ticket resolved by key 4: that ticket;
   - on `azure-devops`: the parent of a resolved item whose title carries one of the *Title
     prefixes* row's prefixes, found by `### Walking up`; a resolved item with no prefix is the
     product source itself;
   - on `github`: the PRD key 1 resolved; for key 3, the issue's parent, found by
     `### Walking up`, or the issue itself when it has no parent — a standalone `[TASK]`.
2. **The pull request's title and body**, when the run has no ticket.
3. **The diff alone**, when the pull request's title and body say nothing a user could observe —
   an empty body, a title that names only code.

### Walking up

**On `azure-devops`**, from a resolved `[SPEC]` or `[TASK]`:

1. Read its `System.Parent` — the `Hierarchy-Reverse` relation on the fetch with
   `expand: "relations"` and no `fields` filter — and fetch the parent the same way.
2. Check the parent's **title**: it carries none of the *Title prefixes* row's prefixes. Never
   check a work-item type name; process templates disagree about them, and `to-spec` checks its
   lead the same way.
3. Find the `[SPEC]`: the resolved item, or for a `[TASK]` the `[SPEC]` its `Spec: #<id>` line
   names. Read the items on the `[SPEC]`'s `Implements decisions for:` line, under `## Scope`.
   The parent must be the **first** item there. A line that is missing or names no item counts
   as a disagreement.
4. **Every further item on that line is a follower** — the group case `to-spec` writes. Fetch
   each one the same way. Each must carry a `Related` link whose url ends in the `[SPEC]`'s id.
   A follower's criteria and Out of Scope join the parent's, attributed to that follower.

**On `github`**, key 1 already gives the PRD. For key 3, read the issue's parent:

```bash
gh api graphql -F n=<n> -f o=<owner> -f r=<repo> \
  -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){parent{number title}}}}' \
  --jq '.data.repository.issue.parent'
```

A `null` parent means the issue itself is the product source.

**These are stops**, each one before any flow is composed:

- the `[SPEC]` or `[TASK]` has no parent;
- the parent carries a title prefix;
- the parent is not the first item on the `[SPEC]`'s `Implements decisions for:` line;
- a follower has no `Related` link to the `[SPEC]`.

```
prove-branch cannot find the product source for `<resolved item>`.
  <the check that failed, with the ids it read>
Which work item holds the acceptance criteria for this run?
```

The developer's answer gives the product source; record that it came from the developer.

### The criteria list

- **The product source's criteria come first.** A GitHub PRD has no acceptance-criteria section:
  its criteria are its `## User Stories`, one criterion per story. Every other item keeps them
  where `../_shared/ticket-source.md` §2 says.
- **Each follower's criteria follow**, attributed to that follower.
- **Each landed child's acceptance criteria join** — a PRD's children, or a `[SPEC]`'s `[TASK]`s —
  attributed to that child. A child's user-visible criteria are often more exact than the product
  source's, so they stay.
- **The `[SPEC]` body gives no criteria.** Every implementation decision in it is in the diff.
- **A product source with no criteria** leaves the children's criteria alone on the list. Say so
  in the print and in the receipt.
- **Rung 2**: the pull request's acceptance-criteria list where its body carries one, attributed to
  the pull request; otherwise criteria inferred from its title and body. **Rung 3**: criteria
  inferred from the diff.

**An item with no criteria and no child criteria is still valid input.** Infer the criteria from
its description and summary, and label each one `inferred`. An inferred criterion is the skill's
reading, never the item's own words, and the receipt keeps the label.

### Out of Scope

Read the product source's **Out of Scope**, and each follower's, the way acceptance criteria are
found: a field whose name contains `Out of Scope` or `OutOfScope`, case-insensitively, then a
section of the description or body headed `Out of Scope`, in any heading level or case. An item
with neither sets no limit. The items are handed to `## Composing the flows`, which they limit.

**The diff is the authority.** Read it — `github`: `gh pr diff <n> --repo <owner>/<repo>`;
`azure-devops`: `git diff origin/<default-branch>...HEAD`, since the MCP exposes no diff tool. Any planned
`## QA notes` in a child issue was written before the code existed; read it for intent and let the
diff overrule it.

## What a run prints

Once the run, the target and the criteria are resolved, print them before composing the flows:

- the ticket, the key that resolved it, and the pull request — or `ticket: none`;
- the **anchor**: the item the receipt, the findings and a fix-now commit will name — the ticket,
  or the pull request when there is none;
- the **product source**: its id and title and how it was reached — the resolving key, the
  `[SPEC]`'s parent, the issue's parent, the developer — with each follower; or the rung the run
  fell to;
- the **Out of Scope** items, each with its source, or `none`;
- the hygiene results;
- the target URL and the SHA tested, with `developer-stated` where it applies, and the targets
  of the run, one per app (`### One target per app`);
- the criteria, numbered, each with its source — the product source, a follower, a child, the
  pull request, or `inferred` — and, when the product source gave none, that the children's
  criteria stand alone.

## Knowledge

Before composing, read what the project knows about the pages the branch touches and the items it
can make. The three formats are defined once, in [`knowledge-file.md`](../references/knowledge-file.md),
[`recipe-file.md`](../references/recipe-file.md) and
[`made-items-file.md`](../references/made-items-file.md); read all three, and where this skill and
one of those files seem to disagree, that file wins.

### The touched page folders

List the changed paths with `git diff --name-only origin/<default-branch>...HEAD`. A **page folder** is a
folder holding a route entry file that the framework renders as a page. Each changed path belongs to
its nearest page folder at or above it: a change under `app/shelves/components/` touches the page
folder `app/shelves`. A changed path with no page folder above it is shared code, and
`### Shared code` traces it to the pages that render it.

Read the `KNOWLEDGE.md` in every touched page folder, and in every page `### Shared code` selects to
drive. A page the trace reaches and does not select is not a touched page: it is neither read nor
derived. **A page folder whose file is missing, is not
in the four-table shape, or was derived before the page changed is derived again by this run, and the
run continues.** Nothing is a stop and no command is printed for the developer to type. Per page
folder:

| The folder's file | The run |
|---|---|
| missing | **derives** it |
| not in the shape [`knowledge-file.md`](../references/knowledge-file.md) fixes — it has a `## How a state is made` table, a `Known account` or `Seeder (for a human)` column, an `Apps read:` line, or a question asking which item on staging holds a state | **regenerates** it |
| in the shape, and the page changed since its `Derived at:` commit: `git diff --name-only <sha>..HEAD -- <page folder>` lists a path, or the sha is not in the repository | **regenerates** it |
| in the shape, and that command lists nothing | reads it, and derives nothing |

To derive or regenerate, read [`../build-knowledge/SKILL.md`](../build-knowledge/SKILL.md) →
`## Deriving` for a derive and `## Regenerate` for a regenerate, and apply it to the page folder
exactly as `/qa:build-knowledge <page folder>` would, with no `--repo`, touching nothing those
sections do not touch. **Never restate those sections here.** The backend read does not run, so a
question about a backend rule stays open and `### Open questions` raises it. The run then reads the
file it wrote. Say each derive or regenerate in the next print: the page folder, the mode, and what
a regenerate dropped from an old-shape file. A derive is never committed.

### Shared code

A changed path with no page folder above it is traced to the page folders that render it. **The trace
follows the symbol, never the file**: a general utilities file holds many symbols, and a file-level
trace would reach every page that imports any of them.

1. **Name the changed symbols.** Read the diff of each such path
   (`git diff origin/<default-branch>...HEAD -- <path>`) and list the exported declarations whose
   lines changed, each with its path. A declaration the diff does not touch adds nothing, even beside
   one that changed. A changed path that declares nothing a page can import — a script, a
   configuration file, a test, a document — has no symbol and reaches no page.
2. **Dispatch the project explorer agent**, once, with the changed symbols and the repo's absolute
   path. Where the adapter's `## Sources of truth` names no agent, the agent is `Explore`. The
   trace is a read of the code and the agent writes nothing. Ask for, per symbol, the page folders
   that render it, following each importer up to the route entry file of a page, in the order the
   import chain reaches them, nearest first. The agent's report is the trace.
3. **Select the pages to drive: three at most**, in this order, a page taking a place only once
   and a tier taking only the places left:
   1. the pages a criterion names, by the page's name or route, or because a result the criterion
      states rests on the page;
   2. the pages whose folder already holds a `KNOWLEDGE.md`, read before any derive;
   3. the pages in the order the trace reported them.

   A page folder the diff touches directly is driven anyway and takes no place. When the trace
   reaches three pages or fewer, it selects all of them.

A page the trace selects is a touched page for the rule above, and flows are composed for it as for
any touched page. The **pages not driven** are the pages the trace reached and did not select. The
approval gate shows both lists and the developer may change them, and the receipt names the pages
not driven.

A branch whose shared code reaches no page — no symbol, or a symbol no page renders — and which
touches no page folder reaches no page. **It composes no flow**, not even `get running`, and drives
nothing. Say so in the next print, with each changed path and why it reached no page, and post the
receipt (`## Receipt`), which says the branch reaches no page.

### The QA folder

Find it through the adapter's *QA folder* row, a path relative to the repo root, or at
`.claude/project/qa/` beside the adapter when the row is absent. Read every recipe file in it and
its `made-items.md`; `## Arranging` resolves flows against them. **A missing folder, a folder with
no recipe, and a missing `made-items.md` are not stops**: the project then holds no recipe or no
made item yet, and a flow that needs one resolves as `### Resolve each flow's data` says.

**Before the first write into the folder, exclude it**, as `## Scenarios` → *The scenario directory*
excludes that directory, with `<qa-folder>` the folder's path relative to the repo root:

```bash
exclude="$(git rev-parse --git-path info/exclude)"
grep -qxF '/<qa-folder>/' "$exclude" 2>/dev/null || printf '/<qa-folder>/\n' >> "$exclude"
```

Never add the line to `.gitignore` instead. Then create the folder when it is missing, write
`made-items.md` with the format's heading and empty table when it is missing, and confirm
`git check-ignore -q <qa-folder>/made-items.md` succeeds. If it fails, say so and stop before any
arrange driver starts. The skill writes the exclude line without asking, and says that it did.

The run writes into the folder only these: a made-items row for each item it makes or each link a
developer gives, the `used` or `gone` status of a row, the `Last proved` cell of a recipe option that
a drive made, a learned recipe or option once a drive made its item (`## Driving` → *Arrange
drivers*), and the `Failed` line of a recipe whose drive failed (`### A recipe that fails`). It
deletes no made-items row and changes a recipe file in no other way. **It never writes into a
sibling repo.**

## Composing the flows

The composer turns the criteria and the diff into a short list of **flows**. It reads six things,
all already in hand: the numbered criteria and the Out of Scope items from `## Criteria`, the diff,
the commit subjects on the branch, the touched pages' `KNOWLEDGE.md` files, and the QA folder's
recipes and made-items file. **It reads nothing else to write the flows** — not the wider codebase,
not the running app.

### Flows test the ticket, not the app

Every flow exists because it checks at least one criterion. **The count follows the criteria**: a
ticket with two criteria gets a short pass, and nothing the ticket does not ask about earns a flow —
no tour of neighbouring screens, no regression sweep. The diff decides how a criterion is checked:
which screen, which control, which result.

**Out of Scope limits what a flow asserts.** No sub-step states a result that an Out of Scope item
from `## Criteria` excludes — not as the action's result, and not as a detail of another result.
Where a flow passes through an excluded area, its sub-steps assert what the criterion asks and say
nothing about the rest. An observation in an excluded area — a grader gap, or something the
developer points out — goes to the receipt's **Noted** section with the item it falls under, and
is never a verdict.

### What a flow is

A **flow** is a run of sub-steps that share a starting point and end somewhere the next flow can
begin from. Each flow has:

- a **name** — what is being exercised, in the ticket's words;
- an explicit **`start from:` line** — the data the flow starts from, in user words, as an item and
  its options (`### The data a flow starts from`), or a prior flow by number, and the role the flow
  signs in as;
- **sub-steps**, numbered `<flow>.<k>`, each naming one **action** and one **observable result** —
  something the page shows or the app answers, which a driver can see is there or is not. In a flow
  that crosses apps, **every sub-step names its app** — `this app`, or a *Sibling apps* label — and
  its role where that differs from the `start from:` line's;
- **attribution** — the tickets whose code the flow exercises: the `(#N)` suffixes or ticket-source
  keys on the commits that touched the files involved, or the resolved ticket itself when the branch
  carries one ticket.

```
Flow 2 — <name>
start from: <item> — <options, or none> — as <role>
attribution: #228, #229
  2.1  <action> → <observable result>
  2.2  <action> → <observable result>
```

```
Flow 4 — <name>
start from: flow 1 completed, as owner
attribution: #230
  4.1  in this app: <action> → <observable result>
  4.2  in admin, as admin: <action> → <observable result>
```

A sub-step whose result is not observable — "the data is saved correctly", "the error is handled" —
is not a sub-step. Rewrite it as what the page shows, or leave its criterion uncovered.

**Every name a sub-step types starts with `qa-setup`**, as every name an arrange drive types does,
so a person who shares staging recognises what the pass made. It is the one write rule of a flow
under test: a flow stays free to pay, delete or change an item, because a criterion can ask for it.
A criterion about a name that cannot start with `qa-setup` leaves its sub-step uncovered, with that
reason.

**A sub-step is in an app the adapter lists**, with a target (`### One target per app`). A result
that only an app with no *Sibling apps* entry shows leaves its criterion uncovered, with the reason
`<app> is not in the adapter's Sibling apps row`; `## Learning a recipe` → *The app question* is
where an app is added.

**The first flow is always "get running"**: open the target URL from `## The target` with each
role's scenario loaded (`## Scenarios`), and see the app signed in as that role — one sub-step per
role the pass uses, a role of a sibling app opening that app's target and naming the app. Its line is `start from: the target URL`, the one flow that starts from neither
an item nor a prior flow. A later flow that needs no particular data starts from it:
`start from: flow 1 completed, as <role>`.

**A cross-flow dependency is named in `start from:`**, never left implicit. A flow that starts from
a prior flow inherits where that flow ended, and cannot run when that flow cannot.
A flow starts from a prior flow only when its criterion is about what that flow did. Data a flow
merely needs to exist is an item, which `## Arranging` resolves and an arrange driver makes.

**The role** a flow signs in as is the one its criterion names. Where none is named, it is the first
role the adapter's *Credential environment variables* row lists; where that row lists no role, the
pass uses one role, `default`.

### Flow boundaries

Boundaries follow **cohesion**: same screen, same role, same starting point. **Never "by child" and
never "every N sub-steps".** A child that touched three unrelated surfaces earns sub-steps in three
flows; three children that changed one screen share one.

3–7 sub-steps is a smell test, not a rule. A one-sub-step flow is fine. A flow past a dozen
sub-steps is usually two flows whose shared starting point has not been named yet.

**A flow crosses apps only when its criterion does**: a result that one app shows of what a
sub-step did in another. Then the sub-steps stay in one flow, so the item the first app made is the
item the second app shows; split, the second flow would start from an item the run arranged instead.
A flow whose criterion lives in one app stays in that app.

### A branch that changes how an item is made

When the diff touches a page folder that is one of a recipe's `Made in` screens, the branch changes
how that item is made. A touched page folder is one of those screens when the recipe's `Made in`
line names `this app` and the page's `KNOWLEDGE.md` `Route:` matches the path of the recipe's start
URL, or its page name is a screen the `Made in` line names.

**Compose a flow that makes the item on the target and opens it where `Seen in` says**:

- its name, `make <item> — <options, or none>`, with no `setup` word: it is a flow under test;
- `start from:` the recipe's `Needs` items, made by `## Arranging` as any flow's item is, or flow 1
  when the `Needs` line reads `none` — `— as <the recipe's Role>`;
- one sub-step per step of the recipe — its shared steps, then the steps of each option a criterion
  names — in `this app`, each step's result as the observable result;
- a last sub-step in the `Seen in` app, as a role of that app (`### Which role and which app`): open
  the item the way the `Seen in` line says → the item shows under its `qa-setup` name.

This is the one exception to "arrange always drives staging" (`## Arranging`): **making that item
is the flow under test**, so it runs on the preview and the grader sees it. When the `Seen in` line
names another app, the item reaches that app only through staging's data, so the flow needs a
target confirmed as staging (`### Staging or not`) and is otherwise Unable to verify, with the
reason `target is not confirmed as staging`.

The item this flow makes is the branch's work, not the recipe's: it writes no `made-items.md` row,
no `Last proved` date and no `Failed` line. A step that does not show its result is a Fail like any
other, graded from the evidence.

### The coverage map

Beside the flows, build a table from **every** criterion to the sub-steps that check it:

| # | Criterion | Source | Checked by | Status |
|---|---|---|---|---|
| 1 | `<criterion>` | #228 | 2.1, 2.3 | covered |
| 2 | `<criterion>` | inferred | — | uncovered — `<why no sub-step can check it>` |
| 3 | `<criterion>` | story #5100 | 3.2 | ambiguous — `<the readings, and the one 3.2 checks>` |
| 4 | `<criterion>` | PRD #40 | — | not in this branch |
| 5 | `<criterion>` | #229 | — | not browser-observable |

- **Not in this branch**: the diff does not touch what the criterion describes — a user story
  another child delivers, a story criterion a later branch carries.
- **Not browser-observable**: the criterion is about code — tests, lint, documentation, file
  layout, generated types — and no page could show it.
- **Uncovered**: the branch touches the criterion and a user could see it, yet no sub-step checks
  it. Say why in the row. Never stretch a sub-step to claim a criterion it does not observe. A
  criterion that only a page the run did not drive shows (`### Shared code`) is uncovered, with the
  reason `<page folder> is not among the pages this run drives`.
- **Ambiguous**: the criterion admits more than one reading with different observable results, or
  names no result at all. Give the readings and say which one a sub-step checks, if any.
- A criterion checked only by sub-steps in Unable-to-verify flows is marked
  `unable to verify — flow <n>`.

**Uncovered and ambiguous criteria are escalations.** Both are shown at the approval gate and both
are handed to `## Receipt`. **Not in this branch and not browser-observable are not escalations**:
they are shown in the map and listed under the receipt's **Noted**. A row carries a status, never a
confidence figure.

### The data a flow starts from

A flow that needs particular data says so on its `start from:` line **in user words, as an item and
its options**: `shelf — with a waitlist`. Find what the flow's first sub-step needs in the page's
`KNOWLEDGE.md` — the state whose `State, in user terms` cell fits, and the `What the user sees` and
`What the user can do` rows that cite it — and write it as the item a user would name:

- **the item** — the name of the recipe that makes it, when a recipe file in the QA folder makes it
  (`shelf`, from `shelf.md`); otherwise the item in user words, in the same kebab form;
- **the options** — the option names of that recipe's `## Options` table the flow needs, or `none`
  when the item alone is enough.

A state id is a label inside the knowledge file and never a key into another file, so it never
appears on the line. Never stretch an item to fit. A flow that needs a shelf with an overdue loan
does not start from a shelf with no loans.

- **a prior flow** — nothing to resolve; the flow follows that flow's outcome.
- **an item** — resolved, checked and made by `## Arranging`.

## Learning a recipe

An item a flow starts from that no `fresh` row fits, and that no recipe in the QA folder makes as the
flow needs it, is **learned during the run**: its recipe, or its missing option, is found and drafted
before the gate, shown at the gate, and saved only once a drive after "go" made the item.

**Nothing is learned unless the adapter's *Staging writes* row reads `yes`.** On any other value no
drive can prove a recipe, so the item goes straight to a link at the gate (`### A link from the
developer`).

### What is learned

- **A recipe**: the QA folder has no file named for the item.
- **An option**: the recipe file has no `## Options` row for an option the flow names. Only that
  option's steps are learned; the recipe's header lines, its shared steps and its other options stay
  as they are.
- **A recipe again**: the recipe file carries a `Failed` line, written when a drive of it failed in an
  earlier run ([`recipe-file.md`](../references/recipe-file.md)). The whole recipe is learned again,
  with the old file and its failing step as material, and no command from the developer.
- **A needed recipe**: an item a recipe being learned or used names on its `Needs` line, when the QA
  folder has no recipe for it. It is learned the same way, to the end of the chain.

A recipe that failed **in this run** is never learned again in this run (`## Driving` → *A recipe
that fails*).

### Before the gate the run only reads

Learning reads code, reads screens and asks the developer. **It writes nothing to staging**: the
screen read is a look, read-only for its driver. Before the gate learning writes only the draft of each
learned recipe, in the arrange folder (*The draft*), a *Sibling apps* entry the developer confirmed
(*Recording a sibling app*), and a role on an entry when the screen read first signs in to that app
(*Recording a sibling app's role*). Nothing reaches the QA folder before a drive made the item.

### The sources, in order

1. **The code**: this repo and each sibling app's repo that sits beside it, read by the read-only
   `qa:qa-chain-searcher` agent (*The code read*).
2. **The screens**: a read-only look on staging confirms what the code said and reads what it could
   not (*The screen read*).
3. **The developer**: one question for what neither answered (*The recipe question*).

A later source fills only what the earlier ones left open. A step the code read `confirmed` and the
screen read showed is never asked.

### The code read

List the repos to read, this repo first. This repo is `this app`. Then each app the adapter's
*Sibling apps* row lists, at its folder beside this repo — the folder with the entry's folder name in
this repo's parent folder. A listed app whose folder is not there is not read, and the gate names
it. For each sibling repo, its recipe folder is the *QA folder* row of that repo's own adapter, at
`<sibling repo>/.claude/project/adapter.md`, or `.claude/project/qa/` when that adapter has no such
row.

**Dispatch one `qa:qa-chain-searcher` agent** with every item to learn — each with its name, the
options the flows need, the route of the page whose flow starts from it, and the description of the
state that page needs with the rows that show it, from the page's `KNOWLEDGE.md`; for a recipe
learned again, also the old recipe file and the step it failed at — and the repos listed above, each
with its absolute path, its label and, for a sibling repo, its recipe folder. The agent writes
nothing and runs nothing; this skill turns its report into drafts.

The type is **`subagent_type: qa:qa-chain-searcher`**, always with the `qa:` prefix. A
`subagent_type` that does not resolve raises no error: the call runs as `general-purpose`, which
carries neither the agent's model pin nor its tool denials. Pass no `model`; the agent pins its own.

### Sibling apps

An item whose report reads `not found`, or whose steps stop at a step the agent placed `elsewhere`,
may be made in an app not read yet. **Look for evidence of one in three places:**

- a backend answer in the page's `KNOWLEDGE.md` that names another system;
- an origin this app links to, from the agent's `elsewhere` lines;
- a front-end repo in the folder beside this one: a folder whose package manifest names a web
  framework, not yet listed in the *Sibling apps* row.

### Made in and Seen in

The two lines hold the connection between two apps, at the level of the item
([`recipe-file.md`](../references/recipe-file.md)). Learn them from three sources, in this order,
and take the first that answers:

1. **A recipe file for the same item in a sibling repo** beside this one, which the code read reports
   as its `sibling recipe:` line. Its `Made in` and `Seen in` lines are material for the draft. The
   file is read and never written.
2. **A criterion that no page of this app can show**: a result the criterion names that no page
   folder of this repo renders, by the touched pages' `KNOWLEDGE.md` and the code read. It makes the
   run ask once which app shows it, in *The app question*.
3. **A link that leaves the app**: an origin the code read placed `elsewhere`. It is a hint only. The
   run proposes it in *The app question* and at the gate, and does not trust it until a drive made
   the item.

With none of the three, both lines name the app the code read found the item made in.

### The app question

When an app has evidence, an item has none, or a criterion needs an app named, **ask the developer
one question**, once per run, covering every open item:

- **for each app with evidence**: the evidence, quoted; the label proposed for it; its repo folder
  name; and the staging URL proposed from the origin this app links to, or a request for one when no
  link names it. The developer answers yes, no, or a correction to any of the three values.
- **for each criterion no page of this app can show**: which app shows it, by its label.
- **for each item with no evidence**: which repo makes it, as a path, or "none".

Never read an app the developer did not agree to. On a yes or a path, dispatch the agent once more,
for the items still open, with this repo first and each agreed app after it. On "none", or a no, the
item is not learned (*When nothing is learned*).

### Recording a sibling app

On a yes, write the app into the adapter's `## QA` section, on the *Sibling apps* row, as the
template gives it: the label, the repo folder name and the confirmed staging URL. Add the row when
it is absent, and add an entry to it when it is present; never change or remove an entry. **The row
holds no path on disk**: a path the developer gave is read in this run only, and a later run finds the
folder beside this repo. An app given as a path is recorded only when the developer gave its staging
URL in the same answer; its label is the folder name. Recording an app writes no role: the roles a
tester uses in the app are added by *Recording a sibling app's role*. With no adapter, or one with no
`## QA` section, write no row, and print the entry the developer confirmed.

### Recording a sibling app's role

The role a tester signs in as in a sibling app is added to that app's entry **when a run first needs
to sign in to that app** as that role. Learning a recipe never signs in for this write: the run
applies this subsection when it signs in to a sibling app (`## Scenarios` → *A session for each
host*), and nothing else writes it.

- The role is a label of the *Credential environment variables* row, written unquoted as that row
  writes it. A label the row does not list is never written.
- The entry gains `, roles: <label>` after its staging URL the first time, and each later role is
  added to that list as `, <label>`, in the order the runs needed them, as the template gives it.
- A label belongs to one app: a label another entry already lists is never written, and the run
  that needed it stops and names both apps.
- **Add only.** Never change or remove an entry's label, folder name, staging URL or a role it
  already lists, and never touch another entry or another row. An entry that already lists the role
  is left as it is.
- With no *Sibling apps* entry for the app, write nothing: the app is recorded by *Recording a
  sibling app* first.

### The draft

Turn each item's report into a draft recipe, in the format of
[`recipe-file.md`](../references/recipe-file.md), at `<arrange folder>/recipes/<item>.md`
(`## Driving` → *The run folder*):

- `Made in`: the app's label, or `this app`, and the screens the steps use, in user words. Its
  `starts at` URL is the one *The recipe question* settles.
- `Seen in`, `Needs` and `Returns` from the report, in user words; `Needs` names recipes in kebab
  case.
- `Role`: a label of the *Credential environment variables* row. A role the code names that the row
  does not list is asked in *The recipe question*.
- **The steps in the words on the screen**: the control by its quoted label, each input quoted, never
  a selector, a test id, a component name or a code word. Every name a step types starts with
  `qa-setup`. A reported code word is paraphrased, never copied.
- Each option's row reads `—` under `Last proved`: no drive has proved it.
- For a learned option, the draft is the existing recipe file with the new option's row added.

The draft is what the gate shows and what an arrange driver drives. It reaches the QA folder only
after a drive made the item.

### The screen read

For each draft, **one `qa:qa-driver` look on staging**, dispatched as `## Driving` → *The agent
types* says, once `## Scenarios` has settled a session for the draft's role on the host of its
`Made in` app (*A session for each host*) and `## Driving` → *Playwright MCP readiness* has passed.
The looks run beside the checks of `### Checking a made item`, by the readiness rule for one browser
context per driver.

- **The flow**: the name `learn <item>`, the word `look` on its own line under the name, which makes
  every sub-step read-only for the driver; `start from:` the `Made in` app's staging URL `— as
  <role>`; and one sub-step per step of the draft, in order, **up to the first step that would write**:
  reach the step's screen as a user would, by the names the draft gives → the step's control shows
  under its label. The step that would write is read for its control and never used.
- The prompt carries what *Dispatching the drivers* lists: the flow, the role and its session path,
  `none` as the ids of the starting state, the app's staging URL as the target URL, and the flow's
  folder in the arrange folder.
- **The skill reads the look's evidence itself**, as it reads a check's: each sub-step's
  `snapshot.md`, and its `screenshot.png` where the snapshot does not settle it. A label the screen
  shows differently from the code takes the screen's words. A screen the look did not reach, or a
  control it did not find, stays open for *The recipe question*.
- The URL of the first step's screen, as the look reached it, is proposed as the recipe's start URL.

Steps after the first write are not read on screen: they stay as the code read gave them, and the
drive after "go" proves them.

### The recipe question

After the screen reads, **ask the developer one question**, once per run, covering every draft, and
only for what the code and the screens left open:

- **the start URL** of each new recipe and each recipe learned again: the URL the screen read
  reached, proposed for a yes, or the route pattern the code read found, with a request for the URL.
  The developer gives it once; the recipe keeps it.
- **each step or option the two sources left open**, quoted as the draft holds it, for a yes, a
  correction, or "none";
- **the role**, when the code names one the *Credential environment variables* row does not list:
  which label of that row signs in as it.

Never ask for an id of an item, an org or an account: the start URL carries whatever the app needs
to scope the data. A learned option takes its start URL from the existing recipe and asks none.

### When nothing is learned

An item is not learned when the code read reports `no path`; when every read ends `not found` and
the developer answers "none" or no; or when *The recipe question* leaves its start URL, a step or its
role open. It then resolves from the next source, a link at the gate. With no link, the flow is
Unable to verify, with the reason `no made item "<item>" <with options>, no recipe in the QA folder
makes it, the run could not learn one: <the reason>, and the developer gave no link`.

A needed recipe that is not learned makes every flow that needs the chain resolve the same way.

## Arranging

Every flow that starts from an item has that item resolved before the gate and made after it. The
run's order is:

1. **Before the gate, read only.** Resolve each flow's item from the files (`### Resolve each
   flow's data`), read the code for each recipe or option to learn and ask *The app question*
   (`## Learning a recipe`), settle the scenarios (`## Scenarios`), check that each made item the
   run would use again still exists (`### Checking a made item`) beside the screen read of each
   draft, and ask *The recipe question*. **Nothing is written to staging before "go".**
2. **The gate** lists the items the run will use again and the items it will make, each with its
   whole `Needs` chain and the steps of each recipe learned in this run, the items it asks the
   developer to link, and the open questions that block a flow (`## The approval gate`).
3. **After "go"**, arrange drivers make the items, one at a time, in `Needs` order (`## Driving` →
   *Arrange drivers*). The flow drivers start after the last of them returns.

**Arrange always drives staging. Only the flows under test drive the preview.** A bug in the branch
under test therefore cannot break the making of its own start data. The one exception is an item
whose making the branch changes: making it is a flow under test, on the preview (`## Composing the
flows` → *A branch that changes how an item is made*), and only its `Needs` items are arranged.

### Staging or not

The target decides whether an item on staging is there for the flows:

- The pull request's preview deployment resolved in `## The target` is staging: it reads staging's
  data.
- A developer-stated URL is staging only when the developer says so in this session. When they have
  not, ask once, before resolving any item, whether the target reads staging's data. The question is
  about the target and names no item.
- A target the adapter or the developer names as production resolves no item.

On a target that is not staging, every flow that starts from an item is Unable to verify, with the
reason `target is not confirmed as staging`.

### Resolve each flow's data

For each flow's item and options, take **the first source that answers**, in this order:

| Source | The flow |
|---|---|
| a row of `made-items.md` whose `Item` is the item, whose `Options` hold every option the flow names, whose `Status` is `fresh`, and whose item still exists (`### Checking a made item`) — a `developer` row as much as a `run` row. When several rows fit, take the most recent `Made` and say which | **uses the item again** |
| a recipe file named for the item, carrying no `Failed` line, whose `## Options` table has a row for every option the flow names, when the adapter's *Staging writes* row reads `yes` | **makes the item** after the gate, by that recipe and its `Needs` chain (`### The Needs chain`) |
| a recipe or an option the run learns now, when the *Staging writes* row reads `yes` (`## Learning a recipe`) | **makes the item** after the gate, by the draft and its `Needs` chain, and saves the recipe or option once the drive made the item |
| a link the developer gives at the gate (`### A link from the developer`) | **uses the link**, recorded as a row with origin `developer` |
| none of these | is **Unable to verify** |

**A target that forbids staging writes arranges nothing.** When the *Staging writes* row is `no` or
absent, no recipe makes an item and none is learned: the second and third sources never answer, no
arrange driver is dispatched and no `Needs` chain is resolved. A flow that no `fresh` row fits is
resolved by the fourth source.

An Unable-to-verify flow carries one of these reasons, with its remedy:

| Found | Reason | Remedy |
|---|---|---|
| no fitting `fresh` row, no recipe for the item or the option, none learned, and no link given at the gate | `no made item "<item>" <with options>, no recipe in the QA folder makes it, the run could not learn one: <the reason>, and the developer gave no link` | a link to the item at the gate, or a recipe for the item with that option in the QA folder, in the format of [`recipe-file.md`](../references/recipe-file.md) |
| no fitting `fresh` row, and no link given at the gate, while the *Staging writes* row is not `yes` | `the adapter's Staging writes row is not yes, so the run makes no item, and the developer gave no link for "<item>" <with options>` | a link to the item at the gate, or the row set to `yes`, which `/qa:setup` asks |
| a recipe whose chain cannot be made | the reason `### The Needs chain` or `### Which role and which app` gives | the recipe named in the reason, fixed |

The made item's steps are its recipe's shared steps, then the steps of each option the flow names,
in the order the `## Options` table lists them.

**Two flows share one item only when neither has a sub-step that changes data.** Otherwise each
flow takes its own row, or its own drive, so that a flow that changes its item cannot change the
start of another flow driven beside it.

A flow that starts from an Unable-to-verify flow is Unable to verify too, naming that flow.

### A link from the developer

An item no recipe can make and the run could not learn, or any item on a project that forbids
staging writes, is a **link the developer gives at the gate**, never one the skill goes looking for.

- **The gate asks once per item.** It lists each item the run needs that no `fresh` row fits — and
  that no recipe makes and none was learned for, when the *Staging writes* row is `yes` — with the
  options each flow names,
  the flows that start from it and the role they sign in as, and asks for a link to each. An item the
  developer answers with no link is Unable to verify, with the reason of the table above. Showing the
  gate again after an edit never asks for that item again.
- **A link becomes a row** of `made-items.md` when it is given: `Item` and `Options` as the flow
  names them, `Link or ids` the link as given, `Role` the role of the flow that starts from the
  item, `Made` today's date, `Origin` `developer`, `Status` `fresh`. A developer's link has no
  `qa-setup` name, and the row records none.
- **The row is checked like any other** (`### Checking a made item`), before "go": the link must
  open on the item's app and show an item. A link that shows no such item takes `gone <today's date>`,
  the flow is Unable to verify with the reason `the link for "<item>" shows no such item`, and the
  developer is not asked again.
- **The run trusts what the developer says the item holds.** It does not check that the item has
  the options the flow names. A flow that fails for that reason fails as any flow does, and the
  receipt's items section names the link.
- **A developer row follows the rules of every row.** A later run uses it only while it is `fresh`
  and the item still exists, and `### Marking used items` marks it `used` when a flow changed it.

### The `Needs` chain

A recipe whose `Needs` line names other recipes is made after the items they make. Resolve each
needed item the same way, to its end, before the gate: a `fresh` row of that item, whatever its
options, or else its recipe's shared steps alone, learned first when the QA folder has none or it
carries a `Failed` line (`## Learning a recipe`). A needed recipe that is not in the QA folder and
was not learned, or a chain that reaches the same recipe twice, makes every flow that needs the chain Unable to verify,
with the reason `recipe "<name>" needs "<needed item>", which <no recipe in the QA folder makes ·
needs "<name>" again>`.

The order of making is the `Needs` order: a needed item before the item that needs it. Each arrange
driver passes the link or ids its item returned to the next driver of the chain, as the ids of that
driver's starting state. An item two chains need in the same run is made once and serves both.

### Checking a made item

**Every `fresh` row the run would use again is checked before the gate**: the item still exists.
The check runs after `## Scenarios` has settled the row's role's session for the staging host
(*A session for each host*), and after `## Driving` → *Playwright MCP readiness* has passed.

- **One `qa:qa-driver` per row**, dispatched as `## Driving` → *The agent types* says, with a flow
  in its input contract: the name `check <item>`, the word `look` on its own line under the name,
  which makes every sub-step read-only for the driver, `start from:` the row's link `— as <role>`,
  and one sub-step: open the link → the item shows under its `qa-setup` name. The checks may run in
  parallel, by the readiness rule for one browser context per driver.
- The prompt carries what *Dispatching the drivers* lists: the flow, the role and its session path,
  the row's `Link or ids` as the ids of the starting state, the staging URL of the item's app as the
  target URL, and the flow's folder in the arrange folder (`## Driving` → *The run folder*).
- **The skill reads a check's evidence itself.** A check decides where a flow starts, never a
  verdict, and the grader never sees it. Read the sub-step's `snapshot.md`, and its `screenshot.png`
  where the snapshot does not settle it.

| The evidence shows | The row |
|---|---|
| the item, under its `qa-setup` name | is used again |
| no such item: a not-found page, an empty place, another item | takes `gone <today's date>` in its `Status`, and the flow resolves from the next source |
| no answer: the driver reported `session not accepted` or `preview auth not accepted` | is not used and keeps its status; the flow resolves from the next source |

### Which role and which app

- **An arrange drive signs in as its recipe's `Role`**, a label of the *Credential environment
  variables* row. A label the row does not list makes every flow that needs the recipe Unable to
  verify, with the reason `recipe "<name>" signs in as <role>, which the Credential environment
  variables row does not list`. No skill creates a user.
- **A role label belongs to one app**, and is unique in the project:
  1. the app whose *Sibling apps* entry lists the label under `roles:`;
  2. otherwise the app the recipe's `Made in` line names, when it names a sibling app's label;
  3. otherwise this app.

  Two different apps for one label, by those three, is a stop that names the label and both apps.
- **A recipe made in an app the adapter does not list** — its `Made in` app is neither this app nor
  an entry of the *Sibling apps* row, after *The app question* recorded what the developer
  confirmed — makes every flow that needs it Unable to verify, with the
  reason `recipe "<name>" is made in <app>, which the adapter's Sibling apps row does not list`.
- **The drive starts at the URL on the recipe's `Made in` line.** Its origin is the drive's target
  URL, by `## The target` → *One target per app*: this app's *Staging URL*, or a sibling app's
  staging URL from its entry. A start URL on any other origin makes the recipe's flows Unable to
  verify, with the reason `recipe "<name>" starts outside staging`.
- **A sub-step of a flow under test in a sibling app signs in as a role of that app**, by the same
  three rules, and that app's target is its staging URL.

### Open questions

Each touched page's `KNOWLEDGE.md` lists its open questions. A question is **open** while its
`Answer` cell reads `—`. An open question **blocks a flow** when its `Blocks` cell names a state the
flow starts from or a state whose rows a sub-step's result rests on, or when a cell the flow rests on
cites it in brackets. A question that blocks no flow of this run is not raised.

A flow with an open question that blocks it and no answer by "go" is **Unable to verify**, with the
reason `open question <Qn> of <page folder>: "<the question>"`, and the remedy `answer it at the
gate, or run /qa:build-knowledge <page folder> --fact "<Qn>: <answer>"`. The developer may answer
it at the gate (`## The approval gate`) or accept Unable to verify.

An answer is written by `### Write-backs`. The answer then changes what the page does, so the flows
and sub-steps it touches are read again from the updated file and recomputed before the gate is shown
again.

### Write-backs

A developer's answer during a run is written to the file it belongs to, so no later run asks again.
Besides the derive in `## Knowledge`, this is the **only write** this skill makes to a knowledge file:

- **An answer to an open question** of the page's `KNOWLEDGE.md` (`Q<n>`). Write it through
  `qa:build-knowledge`'s update mode: read
  [`../build-knowledge/SKILL.md`](../build-knowledge/SKILL.md) → `## Update mode` and apply it to the
  page folder exactly as `/qa:build-knowledge <page folder> --fact "<Qn>: <answer>"` would, touching
  nothing that mode does not touch. Name that command in the print.

An answer that is not a fact — a guess, a "probably" — is not written; ask the one question that
would make it one. Say each write-back in the next print: the file, the question, and the origin. A
write-back is never committed.

### Handed over

- To `## The approval gate`: every flow with its resolved item — used again, with its row, made,
  with its recipe or its draft and its whole `Needs` chain, or linked by the developer — the items
  to ask a link for, each *Sibling apps* entry recorded, the open questions that block a flow, and the Unable-to-verify flows with their reasons and
  remedies.
- To `## Driving`: the items to make, in `Needs` order, each with its recipe or its draft, its
  options, its app, its role and its start URL; and the flows that are ready, each with the link or ids of its item,
  or the item it waits for.
- To `## Receipt`: the Unable-to-verify flows with their reasons and remedies, every row marked
  `gone`, and the uncovered and ambiguous criteria.

No Unable-to-verify flow is driven.

## Scenarios

A **scenario** is a saved login session for one role plus a short description of it. The pass signs
in through scenarios only: no flow, sub-step or driver ever handles a credential.

Scenarios are settled after `### Resolve each flow's data` has resolved every flow's item and
`## Learning a recipe` has drafted every recipe it learns, since the flows, the recipes and the
drafts name the roles, and before `### Checking a made item`, the screen read and
`## The approval gate`.

### The scenario directory

Scenarios live in **`.qa-scenarios/`** at the root of the project's working tree, one directory per
role:

| Path | What it holds |
|---|---|
| `.qa-scenarios/<role>/session.json` | the saved session, as a **Playwright storage-state file** (`cookies` and `origins`), the form the driver loads |
| `.qa-scenarios/<role>/session-<host>.json` | a saved session for one more host of the run, only when `session.json` fails the cover test for it (*Reuse or capture*) |
| `.qa-scenarios/<role>/scenario.md` | the description: the role, the session method, the origin each session file was captured against, and the date captured |

`<role>` is the role's label in lower case, with every character outside `a-z`, `0-9` and `-`
replaced by `-`.

**On the first run, exclude the directory before creating it**, so it never shows in `git status`:

```bash
exclude="$(git rev-parse --git-path info/exclude)"
grep -qxF '/.qa-scenarios/' "$exclude" 2>/dev/null || printf '/.qa-scenarios/\n' >> "$exclude"
```

`--git-path` finds the right file in a linked worktree too, where `.git` is a file. Never add the
line to `.gitignore` instead: that is a tracked change to the project. Then create the directory
under `umask 077`, so only the developer's user can read a session, and confirm both
`git check-ignore -q .qa-scenarios/` succeeds and `git status --short` shows nothing but this run's
write-backs. If either
check fails, say which and stop.

The skill writes the exclude line and creates this directory without asking, and says that it did.
Neither reaches the repository, and a later run reuses both.

### Reuse or capture

A saved session is keyed by role. **The cover test runs once per role and host**: for each role the
flows and the arrange drives use, and for each host a driver of this run opens with that role,
before anything else uses it. The hosts are those of the run's targets (`## The target` → *One
target per app*): the target's host for a sub-step of a flow under test in this app, a sibling
app's staging host for a sub-step in that app, and the staging host of the item's app for a check,
a screen read or an arrange driver (`### Which role and which app`).

1. **Reuse** a session file of the role — `session.json`, then any `session-<host>.json` — when
   its cookies cover the host, at least one of them is unexpired, and the host accepts it: a
   request made with the session loaded, to a page or endpoint of that host a signed-out visitor
   cannot use, comes back signed in — not a redirect to sign-in, not a `401` or a `403`.
2. **Otherwise capture it**, by the method *A session for each host* names, against the host's
   base URL: into `session.json` when the role has no session file that serves another host, and
   into `session-<host>.json` when `session.json` serves another host of this run.

**A role with no session file is captured here like any other, and the run goes on.** A project
where `/qa:setup-env` never ran is not a stop: the run signs in and learns its recipes itself.

**A session file that passes the test for several hosts serves all of them, and no second file is
captured.** Give a driver the file that covers the host it opens. Say for each role and host whether
its session was reused or captured, and which file serves it.

**A session is a secret too.** Never print `session.json` or read it into this conversation. Inspect
it only through a command that prints cookie names, domains and expiry, never a value.

### `api` — one sign-in call

Read the role's two variable names from the *Credential environment variables* row. A role the
flows use that the row does not list is a stop that names the role. **When a named variable is unset
in the shell, stop and name it** — the role and the variable — and tell the developer to set it and
run again. Never ask for a value. If the developer types a credential into the session anyway, do
not use it and do not repeat it; say to set the variable instead.

Make the sign-in call against the endpoint written after `api` in the *Session method* row,
resolved against the base URL of the host being captured when it is a path. **Reference each credential by its variable name
in the command**, so the shell expands it and the command text never holds a value:

```bash
umask 077
curl -sS -o /dev/null -w '%{http_code}\n' -c .qa-scenarios/<role>/jar.txt \
  [-u "$<BASIC_USER_VAR>:$<BASIC_PASS_VAR>"] \
  --data-urlencode "<username-field>=$<USERNAME_VAR>" \
  --data-urlencode "<password-field>=$<PASSWORD_VAR>" \
  '<base-url><sign-in-endpoint>'
```

- The `-u` line is there only when the adapter has a *Preview basic auth* row, with that row's two
  variable names; drop the brackets.
- The field names and the body format, form or JSON, follow what the endpoint accepts. When the diff
  does not show them, ask the developer for the shape of the request — field names and content
  type — never for a value.
- The response body is discarded and only the status code prints. Never add `-v`, `--trace` or any
  other option that echoes the request.
- A failed sign-in is a stop that names the role, the endpoint and the status. **Do not retry with
  changed input**: a lockout on a shared staging account stops everyone who uses it.
- Convert the cookie jar into the session file *Reuse or capture* named, with one command that
  prints only the cookie count.
  Each jar line becomes a cookie with its `name`, `value`, `domain`, `path`, `expires` (`-1` where
  the jar gives `0`), `secure`, `httpOnly` (from a `#HttpOnly_` prefix on the line) and
  `sameSite: "Lax"`; `origins` is an empty list. Then delete the jar.
- A sign-in that sets no cookie — a token returned in the body for the app to keep — cannot be
  saved as a session the driver loads. Stop, say so, and suggest `manual` for this project.

Then confirm the host accepts the new session, as in step 1 of *Reuse or capture*.

### `manual` — one login in a visible window

Propose the command and wait for a yes; it opens a browser window and runs until the developer
closes it:

```bash
npx playwright open --save-storage=.qa-scenarios/<role>/<session file> '<base-url>'
```

`<session file>` is the file *Reuse or capture* named, and `<base-url>` the base URL of the host
being captured.

Tell the developer which role to sign in as, to sign in in that window, and to close the window once
the app shows them signed in. Playwright writes the session when the window closes; the skill never
sees what was typed. When Playwright or its browser is not available, say which and stop — never
install anything into the project. Then confirm the host accepts the new session, as in step 1 of
*Reuse or capture*.

### A session for each host

A capture that *Reuse or capture* calls for uses the method of the app whose host it is:

- **A role of this app** signs in by the *Session method* row, against this app's target or its
  *Staging URL*.
- **A role of a sibling app signs in by `manual` only**, by *`manual` — one login in a visible
  window*, against the app's staging URL from its *Sibling apps* entry, whatever the *Session
  method* row says: there is no `api` sign-in for a sibling app.
- **The first time a run signs in to a sibling app as a role its entry does not list**, add the role
  to that entry, by `## Learning a recipe` → *Recording a sibling app's role*, touching nothing that
  subsection does not touch. Say the write in the print.

A role left with no session that covers the host a recipe needs makes every flow that needs the
recipe Unable to verify, with the reason `no saved session for <role> on <host>`; so does a role
left with no session for the host a sub-step of a flow under test opens, for that flow.

### No credential value leaves the shell

A credential value appears in **none** of these: the adapter, a flow, a sub-step, `scenario.md`, the
receipt, a prompt to a driver. The only files under `.qa-scenarios/` that hold anything secret are
the session files a sign-in produced.

**Handed over**, per role: the path to each of its session files, with the host it covers, and its
`scenario.md` description. A driver is given a path, never the file's contents and never a
credential.

## The approval gate

Show the composed pass **once**, whole:

- the target URL and the SHA tested;
- **the targets**, one per app the run uses, as `## The target` → *One target per app* gives them:
  each app's label, the target its flows under test drive, and the staging URL its arrange drives,
  checks and screen reads open;
- **the pages to drive**: each page `### Shared code` selected, in order, with its tier — `criterion`,
  `has a knowledge file` or `trace order` — and the symbol that reached it, then the pages not
  driven. The developer swaps, adds or drops a page; a page added is derived if it has no
  knowledge file (`## Knowledge`), the flows and the coverage map are recomputed, and the list is
  shown again;
- the flows, numbered, each with its name, `start from:` line, the `item:` line its item resolved
  to — `use again`, with the row's link or ids, or `make`, with the recipe and its options —
  attribution and sub-steps, each sub-step with its app in a flow that crosses apps. A flow that
  makes an item whose making the branch changes (`### A branch that changes how an item is made`)
  says so under its name, and says that it runs on the preview;
- **the items to use again**: each `made-items.md` row, with its link or ids, its role, its `Made`
  date and origin, and the flows that start from it;
- **the items to make**: each with its whole `Needs` chain in the order of making, and per item the
  recipe, its options, the app and the start URL, the role it signs in as, every `qa-setup` name
  its steps type, and the flows that start from it.
- **the steps of each new recipe**: for each recipe, option or recipe learned again in this run,
  under its item in the items to make, the draft whole — its `Made in`, `Seen in`, `Role`, `Needs`
  and `Returns` lines, its shared steps and the learned option's steps — with the source of each
  step, `code`, `screen` or `developer`, a step only a spec or a sibling recipe supports marked so,
  and a `Made in` or `Seen in` that rests on a link leaving the app marked as a hint. Say that the
  recipe is saved to the QA folder only after its drive made the item, and that an option no drive
  proves is not saved;
- **the *Sibling apps* entries** this run recorded, and each listed app whose folder is not beside
  this repo, so its code was not read; Say that the arrange drives create items only,
  change or remove nothing this run did not create, enter no payment details, and remove nothing
  afterwards;
- the made-items rows the checks marked `gone`;
- **the links to ask for**: each item the run needs that no `fresh` row fits and no recipe makes
  now, with its options, its flows and its role, and one request for a link to each
  (`### A link from the developer`). On a project that forbids staging writes this is every such
  item, and the gate says that the run arranges nothing;
- **the open questions that block a flow**: each question of a touched page's `KNOWLEDGE.md` with
  its id, its page folder, the flows it blocks and the readings of its `Question` cell, and for each
  an invitation to answer it or to accept Unable to verify for those flows (`### Open questions`);
- the coverage map, with uncovered and ambiguous criteria called out;
- the Unable-to-verify flows, each with its reason and remedy.

```
Flow 3 — <name>
start from: shelf — with a waitlist — as owner
  item: make — recipe shelf, option with a waitlist (needs: team, made first)
attribution: #228
  3.1  <action> → <observable result>

Item to make — shelf, option with a waitlist — learned in this run, saved after its drive
  Made in: admin · Shelves, New shelf · starts at <start URL>        (code, screen, developer)
  Seen in: this app · the shelf's link                               (sibling recipe)
  Role: owner · Needs: team · Returns: a link to the shelf
  1. On "Shelves", choose "New shelf"                                (code, screen)
  2. Type the name "qa-setup shelf" in "Name", then "Save"           (code)
  option with a waitlist: 3. Turn on "Waitlist", then "Save"         (code, likely)
```

The developer may edit — drop or add a flow, swap a page to drive, change a sub-step, settle an ambiguous criterion,
remove an item, give a link, answer an open question — or say go. A link is recorded and checked
before "go" (`### A link from the developer`); an answer is written through `### Write-backs`.
Removing an item to use again resolves its flows from the next source; removing an item to make
makes its flows Unable to verify, with the reason `the developer removed "<item>" at the gate`, and
saves no draft of it. A change to a learned recipe's step edits its draft, and the drive proves the
edited step. An edit is applied, a new flow's item is resolved by
`## Arranging`, the items, the coverage map and the Unable-to-verify list are recomputed, and the
changed list is shown again. **No driver that writes starts without go, and nothing is written to
staging before it.**

This is the pass's one approval gate. One "go" covers every arrange drive and every flow. No flow
and no item asks for approval again.

## Driving

Each item to make is made by its own arrange driver on staging, and each ready flow is driven by its
own `qa-driver` agent in a real browser against the target. The skill prepares the run folders,
checks that Playwright MCP is there, and dispatches the drivers. It never drives a flow or an
arrange drive itself and never judges what a flow driver saved. It reads a check's and an arrange
drive's evidence, because that evidence decides where a flow starts, never a verdict.

### The agent types

The two agents are dispatched as **`subagent_type: qa:qa-driver`** and
**`subagent_type: qa:qa-grader`**, always with the `qa:` prefix. A `subagent_type` that does not
resolve raises no error: the call runs as `general-purpose`, which carries neither agent's model
pin nor its tool denials, and the run still looks normal. Verifying a change to either agent
therefore includes reading both names back from the agent list of a fresh
`claude --plugin-dir plugins/qa` session. Pass no `model` on either call; each agent pins its own.

### The run folder

Every run gets a new folder inside the excluded scenario directory, created under `umask 077`:

```
.qa-scenarios/runs/<short SHA tested>-<UTC timestamp, YYYYMMDDTHHMMSSZ>/
  run.md
  flow-<n>/
    driver.md
    step-<k>/
      screenshot.png
      snapshot.md
      console.txt
      network.txt
      reload/          after a mutation: the same four files again
```

- **`run.md`** carries the ticket and the key that resolved it, the product source, the pull
  request, the target URL and the target of each other app the flows name, the SHA tested
  (marked `developer-stated` where it applies), the time
  the run started, and per driven flow its role and the link or ids of the item it starts from. It
  carries no credential and no session contents.
- The skill writes `run.md` and creates every `flow-<n>/step-<k>/` folder before any driver
  starts, so a driver only saves files into folders that exist.
- **`driver.md`** is the driver's report, saved verbatim by the skill when the driver returns.
- A run never reuses an earlier run's folder, and the skill deletes none. Since the folder sits
  under `.qa-scenarios/`, `git status --short` shows nothing but this run's write-backs
  (`### Write-backs`); confirm it after creating the folder, and stop if it shows anything else.

**The checks, the screen reads and the arrange drives get a folder of their own**, beside the run
folder and never inside it, so the grader, which reads the run folder, never sees how the data was
made:

```
.qa-scenarios/runs/<short SHA tested>-<UTC timestamp>-arrange/
  run.md
  recipes/<item>.md   the draft of each recipe learned in this run (## Learning a recipe)
  flow-<n>/           one per check, per screen read and per arrange drive, numbered in dispatch order
```

Both folders carry the same timestamp, taken when the first of them is created. The arrange
folder's `run.md` carries the target, the staging URLs, and per check, screen read or drive its
item, its recipe or draft and options, its role and the ids it starts from, with no credential and no session
contents. Its `flow-<n>/` folders have the run folder's shape.

### Playwright MCP readiness

Before any driver starts — a check before the gate, or an arrange or flow driver after it — run the
readiness check in
[`browser-readiness.md`](../references/browser-readiness.md) → *Playwright MCP readiness*, including
its rule for one browser context per driver. When it stops, the remedy it names ends with running
`/qa:prove-branch` again.

### The write rules

Every arrange drive holds to these five rules, which ADR 0028 and ADR 0029 record:

1. It creates items only.
2. Every name it types starts with `qa-setup`.
3. It never changes or removes an item it did not create in this run.
4. It never enters payment details.
5. It signs in only through the saved sessions of roles the adapter lists.

**No cleanup.** A run never deletes a `qa-setup` item, this run's or an earlier run's.

This skill holds all five when it composes a drive. The driver holds them again, on its own, for
every sub-step of a flow marked `setup` (`qa-driver` → mandate 11). A step that either one would
refuse is not performed, and the drive fails there (*A recipe that fails*).

**A flow under test holds one of them, rule 2**: every name it types starts with `qa-setup`
(`## Composing the flows` → *What a flow is*). The driver holds it again (`qa-driver` → mandate 12).

### Arrange drivers

**After "go", before any flow driver, one `qa:qa-driver` per item to make, one at a time, in
`Needs` order.** The next is dispatched only after the previous has returned and its item is
recorded, or its failure reported.

1. **Compose the drive as a flow** in the driver's input contract:
   - its name, `make <item> — <options>`, and the word `setup` on its own line under the name,
     which puts the driver under its mandate 11;
   - `start from:` the recipe's start URL, in its app, `— as <role>`;
   - one sub-step per step: the recipe's shared steps, then each option's steps. Each names its app
     and role, the screen by the name its step gives it, the action with the control by its quoted
     label and every input quoted, each name marked as a name, and the step's result as the
     observable result. A step that uses an item this one needs names it by the link or ids that
     item returned.
2. **Dispatch it** with the prompt *Dispatching the drivers* lists: the flow; the role and the path
   of the session file that covers the drive's host (*A session for each host*); the link or ids of
   each item it needs as the ids of its starting state, or `none`; the staging URL of each app its
   steps name, by app label (`## The target` → *One target per app*); and the flow's folder in the
   arrange folder. Never a credential
   value, never a session file's contents.
3. **Read the report and the evidence.** Save the report as `flow-<n>/driver.md` in the arrange
   folder. Read each sub-step's `snapshot.md`, and its `reload/` snapshot, against the step's
   result, and read what the recipe's `Returns` line names off the last screen: the link to the
   item, or its ids.

**Every sub-step performed, and each result shows**: the item is made. Record it
(*Recording made items*), set the `Last proved` cell of each option the drive made to today's date
in the recipe file, and dispatch the next drive.

**A drive of a draft saves it** into the QA folder, as soon as the drive made the item, before the
next drive. Exclude the folder first (`### The QA folder`).

- **A new recipe** is written as `<item>.md`, with the `## Options` rows of the options this drive
  made, each with today's date under `Last proved`. An option no drive made is left out.
- **A learned option** gains its row in the existing recipe file, with today's date, and nothing
  else in the file changes.
- **A recipe learned again** replaces its file: the header lines with no `Failed` line, the shared
  steps, and the options this drive made with today's date. An old option row stays only when the
  shared steps are unchanged.

A drive of a draft that fails saves nothing (*A recipe that fails*).

### A recipe that fails

A drive fails at its **failing step**: the first sub-step the driver reports `not performed`, or the
first performed sub-step whose result does not show in its evidence, whichever comes first. A
driver that reports `session not accepted` or `preview auth not accepted` fails at its first step.

- **No second attempt in this run.** Never dispatch the drive again with a changed input or a
  different route. The one dispatch again is a driver that reported `missing input`: once, with the
  same flow and the input supplied.
- **The flows that needed it are Unable to verify**, every flow whose item is this one or needs it,
  with the reason `recipe "<name>" failed at step <k>, "<the step>": <what the screen showed, in
  user words>`. No later item of that chain is made.
- **The other flows continue.** Every other drive is dispatched as planned.
- **Remove nothing.** Report the failed recipe: the failing step, what the screen shows, and every
  item the drive created before it, by its `qa-setup` name and id, from the driver's `created:`
  list. These go to `## Receipt`. A failed drive writes no `made-items.md` row and no `Last proved`
  date.
- **Mark the recipe for the next run.** A drive of a recipe file that fails writes, or replaces, the
  file's `Failed` line with today's date and the failing step, so the next run learns the recipe
  again (`## Learning a recipe`); it changes nothing else in the file. A drive of a draft that fails
  saves no draft and writes no `Failed` line, because the QA folder holds no file for it.

### Recording made items

Write one `made-items.md` row for each item a drive made, as soon as its drive succeeds, so a later
stop loses nothing. The columns are the format's ([`made-items-file.md`](../references/made-items-file.md)):

- `Item` and `Options`: the recipe's name and the options the drive made;
- `Link or ids`: what the recipe's `Returns` line names, read off the screen, with the item's
  `qa-setup` name, then every other item the driver's `created:` list names, each with its
  `qa-setup` name and id;
- `Role`: the role of the flow that starts from the item, or the recipe's `Role` for an item made
  only as another item's need;
- `Made`: today's date; `Origin`: `run <short SHA tested>`; `Status`: `fresh`.

### Dispatching the drivers

**One `qa:qa-driver` per ready flow.** The flows handed over by `## Arranging` are the ready ones;
an Unable-to-verify flow is never driven, and neither is a flow whose recipe failed.

- **Every flow that starts from an item or the target URL is dispatched at once, in parallel**,
  after the last arrange driver has returned — all those `Agent` calls in one message.
- **A flow that starts from a prior flow** is dispatched when that flow's driver has returned, and
  only when that driver reported every sub-step `performed`. Otherwise the flow is Unable to
  verify, with the reason `flow <m> did not complete`, and goes to `## Receipt` undriven.

**The driver prompt carries exactly these:**

- the flow — number, name, `start from:` line and sub-steps, as approved at the gate;
- the role, and the **absolute path** to that role's session file for the host the driver opens —
  one path per role for a flow that signs in as several;
- the ids of the starting state: the link or ids of the item the flow starts from;
- **the target of each app the flow names**, by app label, from `## The target` → *One target per
  app*: `this app` with the target URL, and each sibling app a sub-step names with its staging URL.
  A flow in this app alone gets the target URL alone. These are the only origins the driver may
  open;
- the absolute path of the flow's folder, `<run folder>/flow-<n>/`.

**A driver prompt carries a session path, never a credential value** — not a password, not a
token, not a cookie, not the session file's contents. It carries nothing about the code either:
no diff, no file names, no commit subjects, no criteria.

When a driver returns, save its report as `flow-<n>/driver.md`. A driver that reports
`missing input` is re-dispatched once with the input supplied; a driver that reports
`session not accepted` makes its flow Unable to verify, with that reason.

### Marking used items

**When a flow driver returns, every `made-items.md` row its flow started from takes
`used <today's date>` in its `Status`** when the driver's report lists a performed sub-step with a
`reload/` folder. The driver reloads after every sub-step that changes data (`qa-driver` → mandate
5), so the mark needs no judgement. A row whose flow changed nothing stays `fresh`, and so does the
row of an item made only as another item's need. No row is deleted.

## Grading

**The skill never grades.** One `qa:qa-grader` call grades every driven flow, in a fresh context.

### What the grader is given

- the driven flows — number, name, `start from:` line and sub-steps;
- the criteria, numbered, each with its source;
- the coverage map;
- the absolute path of the run folder.

**What it is not given**: the diff, the code, the commit subjects, the ticket beyond its
criteria, the reasoning that produced the flows, the hygiene results, the scenarios, the arrange
folder and anything else about how the start data was made — the recipes, the checks, the arrange
drivers' reports and evidence, the made-items file — and anything from this conversation. The grader judges the evidence the way a tester who never saw the code
would.

### Checking the grader's table

The grader returns one row per sub-step — `Sub-step`, `Verdict`, `Artifact`, `Criteria`,
`Reason` — and a `gaps:` line. Before accepting it, check its format:

- every sub-step of every driven flow has exactly one row;
- every verdict is `Pass`, `Fail`, `Unable to verify` or `Human-only`;
- every **Pass names an artifact path** that exists under the run folder;
- no row and no gap carries a score, a percentage or a confidence figure.

A table that fails is **returned for correction**: dispatch `qa:qa-grader` once more with the same
inputs, the rejected table and each failed check. When the second table fails too, every row that
still fails becomes **Unable to verify**, with the reason `grader gave no valid verdict`. The skill
never repairs a row itself.

### Human-only sub-steps

A `Human-only` row goes to the developer, the way `manual-qa` drives a flow:

- **One flow at a time.** Present the flow whole — name, `start from:`, every sub-step — with the
  grader's verdicts on its other sub-steps and its artifact paths, and say the position: "flow 2
  of 4". Then ask for a verdict on its human-only sub-steps, each with what the grader said to look
  for.
- **Never advance without an explicit verdict.** Not on silence, not on a change of subject, not
  on "ok". When the reply is not a verdict, answer it and present the flow again.
- **Natural language, never on ambiguity.** "yep, the email arrived" is a verdict. "I think so" is
  not: ask one question naming the observable result the sub-step states, and wait.
- A verdict naming a failing sub-step makes that sub-step **Fail** and the human-only sub-steps
  before it **Pass**. Any after it are **Unable to verify**, with the reason
  `not checked — flow failed at <n>.<k>`, unless the developer gives them a verdict too.
- A developer verdict replaces the `Human-only` row, with `developer` in its `Artifact` column.

### Handed over

To `## Receipt`: the verdict table with every human-only row replaced by the developer's verdict,
the `gaps:` line, and the run folder's path.

## Escalation

Before driving, the developer answers what the run cannot settle alone: a stop that asks a
question, the question of `### Staging or not`, *The app question* and *The recipe question* of
`## Learning a recipe`, and at `## The approval gate` the links, the open questions and the go. After grading, the developer
gives the Human-only verdicts of `## Grading` and answers `## On a Fail`. Beside those, an
**escalation** is one of exactly four things, and nothing else:

1. an **Unable-to-verify** flow or sub-step — from `## Arranging`, `## Driving` or
   `## Grading`;
2. a **Fail**;
3. an **uncovered** criterion;
4. a criterion the composer found **ambiguous**.

**An item escalates for what it is, never for how sure anyone is.** No model confidence figure
raises, holds back or ranks an escalation, and none appears anywhere in the pass: not on a verdict,
a criterion, a receipt line or the final print. A Pass is never an escalation. A Human-only
sub-step is not one either, because the developer already gave its verdict in `## Grading`, and
neither is a criterion marked `not in this branch` or `not browser-observable`.

Every escalation reaches the developer in two places: in the receipt, in the receipt's order, and
as its own line in the final print. Uncovered and ambiguous criteria, the flows already Unable to
verify before driving are also shown at the approval gate. That
showing is a preview; the receipt still carries each one.

## Receipt

The receipt is **one free-form comment on the anchor**: the ticket the run resolved — the PRD, the
`[SPEC]`, or the ticket on the `Ticket source:` system — or, when the run has no ticket, the pull
request. Nothing parses it: it is output, never input, and no skill reads it back. **The product
source gets nothing** when it is not the anchor: the receipt names it, and no pointer goes on it.
**A run with a ticket writes nothing to the pull request**: no comment, no label, no review.

The receipt is posted once, after `## On a Fail` has settled every Fail, so it can say what
happened to each. A pass that stops before any arrange or flow driver starts posts no receipt,
since nothing was made or tested — except a branch that reaches no page (`### Shared code`), whose
receipt says so.

### What it carries

First, the head:

- the ticket, or `no ticket`, and the pull request;
- the **product source** and how it was reached, or the rung the run fell to, and when it gave no
  criteria, that the children's criteria stood alone;
- the **Out of Scope** items the composer kept to, or `none`;
- the **target URL** and the **SHA tested**, marked `developer-stated` where it applies;
- the run folder's absolute path. It is on the developer's machine, nothing in it is uploaded, and
  every artifact path in the receipt is under it;
- **completed** or **stopped early**, as `## End of pass` defines them, and for a stopped-early
  pass, where it stopped;
- **the pages not driven**: each page the trace reached and did not select, with the symbol that
  reached it, and each changed path of shared code that reached no page. A branch that reaches no
  page says `the branch reaches no page`, composes no flow, and carries nothing in the sections
  below but `none`;
- **the items the run made**: every `made-items.md` row this run wrote, with its item, options,
  link or ids and `qa-setup` name; every row it marked `used` or `gone`; every recipe and option
  this run learned and saved; every *Sibling apps* entry or role it recorded; and every recipe that
  failed, with its failing step, what the screen showed, each item the drive created before it, by
  its `qa-setup` name and id, and whether its `Failed` line was written. `none` when the run made
  nothing.

Then four sections, **in this order**, each present and reading `none` when empty:

1. **Unable to verify** — each Unable-to-verify flow and sub-step with its reason, then each
   uncovered and each ambiguous criterion with its coverage-map reason. Every item carries a
   **suggested remedy**: the one change that would make it checkable — the
   `/qa:build-knowledge <page folder> --repo <path>` command that reads a backend rule, the recipe to add or fix in the QA folder,
   the *Staging writes* row to set, the variable to set, the target to confirm as staging, the
   reading of the criterion to settle, or the check a human makes by hand.
2. **Fails** — each Fail sub-step with its flow's name, the grader's reason, its **artifact path**,
   and its lane from `## On a Fail`: the finding's link or id, the fix-now commit, or `no lane` with
   the reason.
3. **Passes, with coverage** — each criterion whose checking sub-steps all passed, with those
   sub-steps and their artifact paths. A sub-step the developer decided shows `developer` for its
   artifact.
4. **Noted** — what the pass saw that is not a verdict on this branch: each entry of the grader's
   `gaps:` line, and each Fail the developer said is **present on the base target too** — the
   default branch's deployment — so this branch did not cause it. The skill never drives the base
   target; each item says who placed it here, `grader gap` or `developer`. An observation in an
   Out of Scope area also names the item it falls under. Then, compactly, one line per status,
   the criteria marked `not in this branch` and those marked `not browser-observable`, by number.

Every criterion keeps its source wherever it appears, and an inferred one is labelled `inferred`.
The receipt carries no credential, no session contents and no cookie.

### Posting it

Write the body to the scratchpad, then post it to the system the ticket was read from, or to the
pull request when the run has no ticket:

| Anchor | Call |
|---|---|
| the pull request, `github` | `gh pr comment <n> --repo <owner>/<repo> --body-file <path>` |
| the pull request, `azure-devops` | a new thread on the pull request through `mcp__ado__repo_pull_request_thread_write`, against the **repo project** and **repository** |
| `github` | `gh issue comment <n> --repo <owner>/<repo> --body-file <path>` |
| `azure-devops` | `mcp__ado__wit_work_item_comment_write` (`action: "add"`) against the **work-item project**, with **`format: "Markdown"`** — without it the comment lands as HTML and its headings and code spans arrive as literal text. Escape angle brackets when writing the body, and use inline code spans, never fenced blocks: a fence in an Azure DevOps comment comes back empty. |
| `jira` | `mcp__atlassian__addCommentToJiraIssue`, with `cloudId` the site host from the `Ticket source:` line, `issueIdOrKey` the ticket key, `commentBody` the receipt and `contentFormat: "markdown"` |

Keep the posted comment's URL: it is the final print's one URL. A post that fails is a stop that
says so and gives the scratchpad path of the body, so the receipt is not lost.

**A rerun composes fresh.** It reads the branch, the ticket and the target again and posts a new
receipt. It never reads, edits or replies to an earlier one.

## On a Fail

After grading, each Fail gets **one question: fix now or file.** Take the Fails one at a time, in
flow order. Present the flow's name, the sub-step, the grader's reason and the artifact path, then
ask. Answers are natural language — "fix it", "file that one". An answer that is neither gets one
clarifying question, never a guess.

The developer may instead say the failure is present on the base target too. That Fail goes to the
receipt's **Noted** section, and nothing is fixed or filed for it.

**Both lanes need the ticket on the filing tracker** — the system the `Tracker:` line names. Fix
now needs it because the worker's commit names it; file needs it because `triage` finds the
findings by it. When the run resolved a ticket on another system, such as a Jira ticket through
key 4, say that neither lane is available. Each Fail then goes to the receipt with
`no lane — the ticket is not on the filing tracker`.

**A run with no ticket has neither lane either**: no commit reference to name and no item for
`triage` to find the findings by. Report every Fail — flow, sub-step, grader's reason, artifact
path — and ask the developer what to do with them. What they do happens outside the pass; each
Fail goes to the receipt with `no lane — the run has no ticket`, beside the developer's answer.

A File answer is posted at once, one finding per turn (`### File`). The Fix-now answers are
collected and handed to one worker after the last Fail is answered (`### Fix now`).

### Fix now

Fix now hands the collected Fails to **one worker on this branch**, which commits once:

| `Tracker:` | `subagent_type` | Commit reference |
|---|---|---|
| `github` | `prd-workflow:prd-worker` | `(#<n>)` as the last characters of the subject, `<n>` the resolved ticket's issue number |
| `azure-devops` | `ado-workflow:spec-worker` | the `Work-item: AB#<id>` trailer, `<id>` the `[SPEC]`'s id |

The reference is the ticket the receipt goes to — on `azure-devops`, the `[SPEC]` (`### File`
says how to find it). A rerun's resolver therefore finds the same ticket.

**Before the first dispatch**, confirm that the type is in this session's agent list. A
`subagent_type` that does not resolve raises no error: the call runs as `general-purpose`, without
the worker's mandates. When the type is absent — its workflow plugin is not loaded — fix now is not
available: say so, and ask whether to file instead. Pass `model` per
`../_shared/model-effort-heuristics.md` in orchestrated mode, and announce the routing call before
dispatching.

The worker's mandates and report contract live in its agent file. The prompt carries only the
inputs that agent requires:

- **The issue body**, which the skill writes in place of a finding: a title naming the symptom;
  `## What to build`, holding for each Fail its flow's name and `start from:` line, the sub-steps up
  to the failing one, the result the sub-step states, what the grader saw instead, and the artifact
  path; `## Acceptance criteria`, holding each failing sub-step's stated result and the criteria the
  coverage map gives it; and `## Worker context`, holding the files the diff shows the flow touching
  and `**User-visible**: y`. For `spec-worker`, this body is the `[TASK]` body.
- **The full adapter**, the **branch name**, the **routing call**, and the reference above — the
  issue number for `prd-worker`, the work-item id for `spec-worker`.
- For `spec-worker` only, **the `[SPEC]` body**, which the skill fetches: the worker has no tracker
  access.

The prompt carries no credential and no session path.

**Three rounds at most.** A round is one dispatch. After each round, check for a new commit on the
branch that carries the reference, and check the tree with `git status --short`:

- **A commit landed** — fix now is done. Post the receipt, naming the commit, then take
  `## End of pass`, and **stop**. Tell the developer to push, wait for the preview to build the new
  `HEAD`, and run `/qa:prove-branch` again in a fresh session. The skill never pushes.
- **No commit** — show the worker's report. While rounds remain, ask whether to dispatch again,
  with that report added to the prompt. The skill never resets or cleans what a worker left in the
  tree.
- **No commit after the third round** — dispatch no more. Ask file or not for each of those Fails;
  one not filed goes to the receipt as `no lane — three fix-now rounds made no commit`.

### File

File posts the Fail as a `### [FINDING]` to the run's `[FINDINGS]` issue on GitHub or work item on
Azure DevOps, exactly as `manual-qa` does, and `triage` takes it from there.

**`### [FINDING]` and the `PRD: #<n>` line are hardcoded here and never read from the adapter.**
They are a parse contract: `prd-workflow:triage` and `ado-workflow:triage` match exactly these
strings, and a project free to edit them would get a `triage` that silently finds nothing and
reports a clean run. Both `manual-qa` copies write the same literals; ADR 0020 records that they
are shared across a plugin boundary.

The `[FINDINGS]` issue or item is created **lazily, on the pass's first filed Fail**. A pass that
files nothing creates nothing.

#### GitHub: find or create the `[FINDINGS]` issue

Search for the issue whose body carries the whole line `PRD: #<n>`, where `<n>` is the resolved
ticket's issue number — the PRD for key 1, the ticket for key 3. `/prd-workflow:triage #<n>`
finds the issue by the same line. **Match the whole line, never a substring** — `PRD: #12` is a
prefix of `PRD: #127`:

```bash
gh issue list --repo <owner>/<repo> --state all --limit 500 --json number,title,body,state \
  --jq '[.[] | select(.body | test("(^|\n)PRD: #<n>[ \t\r]*(\n|$)"))]'
```

`gh issue list` defaults to `--limit 30`. Raise `--limit` above the repo's issue count: a truncated
list is a silent miss, and a silent miss here creates a duplicate findings issue.

- **Exactly one open hit** — append to it. When `gh issue view <hit> --json state,stateReason`
  gives `stateReason` `"REOPENED"`, say so before appending: a reopened findings issue getting new
  findings is a surprise worth naming.
- **None open** — no hit, or every hit closed — create one.
- **More than one open** — stop and ask which.

**Creating it:**

- Title: `[FINDINGS] <ticket title, prefix stripped> — run of <YYYY-MM-DD>`.
- Body, exactly: one human sentence naming the ticket and the pull request the findings were found
  against, then the machine line `PRD: #<n>`, then the human line `PR: #<m>`. No finding goes in
  the body.
- **Free-standing** — never linked as a sub-issue of the ticket. A ticket's sub-issues are its
  work, and a findings issue linked there shows up to eligibility as an implementable child.
- **No labels.** The body's `PRD:` line is the finder.

`gh issue create --repo <owner>/<repo> --title "<title>" --body-file <path>`, with the body written
to the scratchpad first. Post each finding with
`gh issue comment <findings-number> --repo <owner>/<repo> --body-file <path>`, then report its
permalink and a one-line recap.

#### Azure DevOps: the run's `[FINDINGS]` work item

**One `[FINDINGS]` work item per pass.** The first filed Fail creates it, every later filed Fail in
the same pass appends to it, and a rerun creates its own. The shape belongs to the `ado-workflow`
plugin's `skills/references/findings-item.md`, the file `ado-workflow:triage` reads it by; where
that file and this section differ, that file wins.

**The `[SPEC]`** is the resolved ticket when its title carries the `[SPEC]` prefix. Otherwise it is
the `[SPEC]` named by the ticket's `Spec: #<id>` line. When neither gives one, ask the developer.

- **Create** with `wit_work_item_write`, `action: "add_child"`, against the **work-item project**,
  under the **parent of the `[SPEC]`** (its `Hierarchy-Reverse`), so the item is a sibling of the
  `[SPEC]`. Use the adapter's work-item type and its pickable state, and pass
  **`format: "Markdown"`**. Title: `[FINDINGS] <spec title, prefix stripped> — run of <YYYY-MM-DD>`.
  The description starts with the line `Spec: #<spec-id>`, then one line naming the pass and the
  pull request.
- **Verify the hierarchy**: fetch the parent with `expand: "relations"` and no `fields` filter, and
  confirm the new item is a `Hierarchy-Forward` relation. Name the item's id, backticked, in the
  terminal now and in the receipt later.
- **Append** each finding by read-modify-write: a fresh `wit_work_item` read (`action: "get"`,
  `expand: "relations"`, no `fields` filter); append to the fetched description and leave every
  earlier finding byte-identical; write with `wit_work_item_write`, `action: "update_batch"`,
  carrying `format: "Markdown"` — never plain `update`, which writes HTML and strips the earlier
  findings; then read the description back and confirm the new finding is there.
- **Number** each heading `### [FINDING] <ordinal> — <one-line symptom>`, where the ordinal is one
  more than the `### [FINDING] ` markers already in the description.

#### The finding

The template is `manual-qa`'s:

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

The fields are filled from the pass:

- **`**Step:**`** — the flow number, the flow's name and the sub-step number, from the approved
  pass. No permalink: the pass is posted nowhere.
- **`**From:**`** — the flow's attribution line. On GitHub, `#<n>` with the `#`. On Azure DevOps,
  backticked ids, `` `#<id>` ``, since a bare `#<id>` adds a relation to the work item.
- **`**Evidence:**`** — the artifact path the grader named, and the grader's reason in words. The
  path is on the developer's machine, so the words carry the evidence for every other reader.
  Screenshots are described, never embedded.
- **`**Symptom:**`** — what the artifact shows, from the grader's reason.
- **`**Repro:**`** — the target URL, the flow's `start from:` line and role, and its sub-steps up to
  the failing one.
- **`**Classification:**`**, **`**Severity:**`**, **`**Where:**`** and
  **`**Root-cause hypothesis:**`** — by `manual-qa`'s bounds: investigate only far enough to
  classify and route, with one decisive probe at most; take the `path:line` from the diff; label the
  hypothesis as one; never write or test a fix.

## End of pass

A pass that took a verdict on every sub-step of every driven flow, and an answer on every Fail, is
**completed** — unless fix now made a commit. A pass is **stopped early** when the developer stops
before that, when the skill stops after a driver started, when the branch reaches no page and no
flow was composed, or when a fix-now commit landed: the
branch has then moved past the SHA tested, and the rerun is the pass that proves it.

Unable-to-verify verdicts do not make a pass incomplete; they are on the receipt. **Findings do
not hold `needs-qa` on**: a pass that filed three findings is a completed pass, and the findings are
`triage`'s queue.

**A completed pass** reads whether the ticket carries `needs-qa`. When it does, offer to remove it,
naming the escalations still open, and **remove it only on an explicit yes**:

- `github`, a label: `gh issue view <n> --repo <owner>/<repo> --json labels`, then
  `gh issue edit <n> --repo <owner>/<repo> --remove-label needs-qa`.
- `azure-devops`, a tag: a **read-modify-write on `System.Tags`**, a single semicolon-separated
  string. Read the ticket's current tags, drop `needs-qa`, and write the whole remaining list back —
  a tag value written on its own replaces every tag the item had:

  ```
  wit_work_item_write  { action: "update", project: <work-item project>,
                          updates: [{ id: <ticket-id>, op: "add",
                                      path: "/fields/System.Tags",
                                      value: "<the remaining tags>" }] }
  ```

  Then read `System.Tags` back and confirm before reporting it removed.
- `jira`: a Jira ticket carries neither the label nor the tag, so the offer is skipped. Say so.
- no ticket: there is nothing to carry the label or the tag, so the offer is skipped. Say so.

**A pass that stopped early leaves `needs-qa` on**, and says so in the receipt and in the final
print.

The receipt, the `needs-qa` removal, and on a File answer the `[FINDINGS]` writes are the complete
list of what the pass writes to the tracker. It never closes the ticket, edits an earlier receipt,
or writes anything to the pull request but the receipt of a run with no ticket.

## Final print

The last print follows `../_shared/final-prints.md`: it carries what the browser cannot show.

- **One line per escalation** from `## Escalation`, and one per skip — a Fail with no lane, a lane
  that was not available, a skipped `needs-qa` offer — however long the list runs.
- Whether `needs-qa` was removed, or left on and why.
- After a fix-now commit: push, wait for the preview to build the new `HEAD`, rerun.
- **One URL**: the receipt comment's. The receipt names the findings issue or item, the pull request
  and the artifacts, so none of them gets a second URL.
- Cut the verdict table, the passes and the flow list: the receipt has them.

The last line is the next command, alone on its line:

| The pass | Last line |
|---|---|
| filed a finding, on `github` | `/prd-workflow:triage #<n>`, `<n>` the number on the `PRD:` line |
| filed a finding, on `azure-devops` | `/ado-workflow:triage <spec-id>` |
| made a fix-now commit, and filed nothing | `/qa:prove-branch` |
| left an escalation open, and filed and fixed nothing | `/qa:prove-branch`, the rerun once a remedy is applied |
| left nothing open | none — no skill has work left. The last line is `branch proven at <short SHA tested> — ready for review` |
