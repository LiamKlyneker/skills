---
name: prove-branch
description: Run the automated QA pass on the checked-out branch of a web project — resolve the ticket, the pull request and the preview deployment from the branch alone, read the acceptance criteria from the highest product source the branch reaches and the touched pages' KNOWLEDGE.md, start every flow from a state the project's accounts.md already holds — stopping with the one command to run, `/qa:build-knowledge` or `/qa:setup-states`, where either file falls short, and never creating data — drive and grade flows against the preview, and post one receipt to the ticket, or to the pull request when the branch names no ticket; it stops with a question wherever the branch is ambiguous, and on a failure asks fix now or file. Runs on user invocation only; neither loop ever invokes it. Invoke /qa:prove-branch with no argument, in a fresh session on the implemented branch.
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
project is the same after a run as before it. What a run produces lives on the tracker, never in
the tree. The one change a pass can lead to is a fix-now commit the developer asks for after
grading, which a worker makes (`## On a Fail`).

**It never creates data.** It reads what the project already knows — each touched page's
`KNOWLEDGE.md` and the project's `accounts.md` — and starts every flow from a state those files
name. Where they fall short it stops and names the one command that fills the gap. Its only writes
to either file are a developer's own answers, written back (`### Write-backs`), so no run asks the
same thing twice.

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
| `## Sources of truth` | the **project explorer agent** for on-demand elaboration — `Explore` where it says None |

From `## QA`, by row name:

| Row | What for |
|---|---|
| *Session method* | how a flow signs in — `api` against the endpoint written after the value, or `manual` |
| *Credential environment variables* | per role, the **names** of the variables holding its username and password. Read them from the backticked tokens: roles are unquoted labels separated by ` · `, each followed by `→` and two backticked variable names, and everything after the em dash is guidance. The skill reads only names here and **never reads a credential value from the adapter** |
| *Known accounts* | the path of the project's `accounts.md`; `<repo-root>/.claude/project/accounts.md`, beside the adapter, when the row is absent |
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

## Resolving the run

The run is two things: the **ticket** the run is anchored to — the item the receipt, the findings
and a fix-now commit name — and the **pull request** the preview deployment belongs to. Both are
found from the branch. The criteria come from the product source the ticket reaches, which
`## Criteria` finds; a branch that names no ticket still runs, on its pull request alone.

### First, read the branch

Three reads, all read-only, before any key is tried:

- the branch: `git branch --show-current`. An empty result is a detached `HEAD` — stop, say so.
- the commit subjects on the branch: `git log <default-branch>..HEAD --format='%s'`, with
  `<default-branch>` from `## Repo`.
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
   there is no `Ticket source:` line, found in the commit subjects and in the open pull request's
   body: for `jira`, an issue key in the form §2 accepts (`ABC-123`); for `azure-devops`, an
   `AB#<id>` work-item mention. For `github` the key is the issue number, which is key 3's shape —
   a bare number found in free text is not a ticket key, so this key adds nothing there and reports
   itself as such.

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
Which ticket and pull request should this pass prove?
```

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
   check or the posting comment names for that preview. Compare it with `HEAD`.
3. **Stop and ask the developer for a URL** when the section is there but the *Preview URL
   pattern* row is absent, when no URL resolves, when the
   URL does not answer, when the preview was built from a commit other than `HEAD`, or when the
   built-from commit cannot be read at all. Say which of these it is, and give the URL and commit
   you found.

**A `401` that challenges for HTTP Basic Auth is an answer, not a URL that does not answer** — from
a resolved URL or one the developer gave. Apply
[`browser-readiness.md`](../references/browser-readiness.md) → *Preview Basic Auth* → *Detect the
challenge* before anything else, and carry the credentials on every later request against the target.

**Record two values now: the target URL and the SHA tested.** The SHA tested is the built-from
commit when it matches `HEAD`. A URL the developer supplies is recorded with the commit the
developer states it serves, marked `developer-stated`. The receipt names both.

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
`azure-devops`: `git diff <default-branch>...HEAD`, since the MCP exposes no diff tool. Any planned
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
- the target URL and the SHA tested, with `developer-stated` where it applies;
- the criteria, numbered, each with its source — the product source, a follower, a child, the
  pull request, or `inferred` — and, when the product source gave none, that the children's
  criteria stand alone.

## Knowledge

Before composing, read what the project knows about the pages the branch touches. The two formats
are defined once, in [`knowledge-file.md`](../references/knowledge-file.md) and
[`accounts-file.md`](../references/accounts-file.md); read both, and where this skill and either
file seem to disagree, that file wins.

### The touched page folders

List the changed paths with `git diff --name-only <default-branch>...HEAD`. A **page folder** is a
folder holding a route entry file that the framework renders as a page. Each changed path belongs to
its nearest page folder at or above it: a change under `app/shelves/components/` touches the page
folder `app/shelves`. A changed path with no page folder above it touches no page.

Read the `KNOWLEDGE.md` in every touched page folder. **A touched page folder with no
`KNOWLEDGE.md` is a stop**, before any flow is composed. Name every such folder, and print the
command for each, alone on its line:

```
prove-branch cannot compose flows for `<page folder>`: it has no KNOWLEDGE.md.
/qa:build-knowledge <page folder>
```

Then say to run `/qa:prove-branch` again once the file exists. **Never run `build-knowledge`
yourself**: deriving a page writes a file into the tree, and that is the developer's command to
run. This skill writes to a knowledge file only through `### Write-backs`. No driver starts, and no
receipt is posted, since nothing was tested.

### `accounts.md`

Find it through the adapter's *Known accounts* row, or beside the adapter when the row is absent.
Read its `## Orgs` and `## States` tables; `## Preparing states` resolves flows against them. **A
missing `accounts.md` is a stop** once a composed flow starts from a state: it prints `/qa:setup`,
which writes the empty file, and nothing else is written or asked.

## Composing the flows

The composer turns the criteria and the diff into a short list of **flows**. It reads six things,
all already in hand: the numbered criteria and the Out of Scope items from `## Criteria`, the diff,
the commit subjects on the branch, the touched pages' `KNOWLEDGE.md` files, and the project's
`accounts.md`. **It reads nothing
else to write the flows** — not the wider codebase, not the running app.

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

A **flow** is a run of sub-steps that share a starting state and end somewhere the next flow can
begin from. Each flow has:

- a **name** — what is being exercised, in the ticket's words;
- an explicit **`start from:` line** — a state id from the page's `KNOWLEDGE.md` `## States` with
  the state in user words beside it, or a prior flow by number, and the role the flow signs in as;
- **sub-steps**, numbered `<flow>.<k>`, each naming one **action** and one **observable result** —
  something the page shows or the app answers, which a driver can see is there or is not;
- **attribution** — the tickets whose code the flow exercises: the `(#N)` suffixes or ticket-source
  keys on the commits that touched the files involved, or the resolved ticket itself when the branch
  carries one ticket.

```
Flow 2 — <name>
start from: S4 — <the state, in user words> — as <role>
attribution: #228, #229
  2.1  <action> → <observable result>
  2.2  <action> → <observable result>
```

A sub-step whose result is not observable — "the data is saved correctly", "the error is handled" —
is not a sub-step. Rewrite it as what the page shows, or leave its criterion uncovered.

**The first flow is always "get running"**: open the target URL from `## The target` with each
role's scenario loaded (`## Scenarios`), and see the app signed in as that role — one sub-step per
role the pass uses. Its line is `start from: the target URL`, the one flow that starts from neither
a state nor a prior flow. A later flow that needs no particular data starts from it:
`start from: flow 1 completed, as <role>`.

**A cross-flow dependency is named in `start from:`**, never left implicit. A flow that starts from
a prior flow inherits that flow's state, and cannot run when that flow cannot.
A flow starts from a prior flow only when its criterion is about what that flow did. Data a flow
merely needs to exist is a state, started from by id: never make it by driving another flow's
actions first, since that creates data the pass does not own.

**The role** a flow signs in as is the one its criterion names. Where none is named, it is the first
role the adapter's *Credential environment variables* row lists; where that row lists no role, the
pass uses one role, `default`.

### Flow boundaries

Boundaries follow **cohesion**: same screen, same role, same starting state. **Never "by child" and
never "every N sub-steps".** A child that touched three unrelated surfaces earns sub-steps in three
flows; three children that changed one screen share one.

3–7 sub-steps is a smell test, not a rule. A one-sub-step flow is fine. A flow past a dozen
sub-steps is usually two flows whose shared starting state has not been named yet.

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
  it. Say why in the row. Never stretch a sub-step to claim a criterion it does not observe.
- **Ambiguous**: the criterion admits more than one reading with different observable results, or
  names no result at all. Give the readings and say which one a sub-step checks, if any.
- A criterion checked only by sub-steps in Unable-to-verify flows is marked
  `unable to verify — flow <n>`.

**Uncovered and ambiguous criteria are escalations.** Both are shown at the approval gate and both
are handed to `## Receipt`. **Not in this branch and not browser-observable are not escalations**:
they are shown in the map and listed under the receipt's **Noted**. A row carries a status, never a
confidence figure.

### Start states from the knowledge file

A flow that needs particular data starts from **a state id in its page's `KNOWLEDGE.md`**. Pick the
state whose `State, in user terms` cell is what the flow's first sub-step needs, using the
`What the user sees` and `What the user can do` rows that cite it. Write the id and the state's
words on the `start from:` line, so the developer reads what the flow needs without opening the
file.

- **a prior flow** — nothing to resolve; the flow follows that flow's outcome.
- **a state id** — resolved against `accounts.md` in `## Preparing states`.
- **no state in the file fits** — the flow is **Unable to verify** now, with the reason
  `the page's KNOWLEDGE.md names no state "<what the flow needs>"`, and the remedy
  `/qa:build-knowledge <page folder>`, the regenerate that derives the state. Compose it in full
  anyway, so the developer sees exactly what could not be checked.

Never stretch a state to fit. A flow that needs a team with an overdue loan does not start from a
state whose team has no loans.

## Preparing states

Every flow that starts from a state is resolved to a known instance of it in `accounts.md` before
the gate. **The skill never creates data, never walks the app looking for data, and never asks the
developer for a URL, an org id, an order number or any other id of a state** — finding those is
`qa:setup-states`'s job.

### Staging or not

The target decides which `accounts.md` rows apply, by their `Env` column:

- The pull request's preview deployment resolved in `## The target` is staging: `staging` rows
  apply.
- A developer-stated URL is staging only when the developer says so in this session. When they have
  not, ask once, before resolving any state, whether the target is staging. The question is about
  the target and names no id.
- A target the adapter or the developer names as production resolves no row: no skill writes `prod`
  rows yet, and a prod row permits read-only flows only.

On a target that is not staging, every flow that starts from a state is Unable to verify, with the
reason `target is not confirmed as staging`.

### Resolve each state

For each flow's state id, find the `## States` rows whose `Env` applies, whose `Page` is the page's
`Route:` line and whose `State` is the id. A row whose `Last verified` reads `stale …` counts as no
row. When several rows qualify, take the most recently verified and say which. Each state comes out
as one of these:

| Found | Outcome |
|---|---|
| a row | the flow is **ready**. The row's `Org` and `Ids` are its starting state's ids, shown on an `account:` line under `start from:` |
| no row, and the state cannot be made in this app | the flow is **Unable to verify**: `state S<n> "<the state, in user words>" <is set in another application · needs time to pass · needs a payment to fail>, and accounts.md has no row for it`. Its remedy names the state's `Seeder (for a human)` hint from `KNOWLEDGE.md`, as written, as the fast path for a human to make the state — or `none known` — and then `/qa:setup-states <page folder> S<n>` to record it |
| no row, otherwise | a **missing account** — `### The missing-account stop` |

A state **cannot be made in this app** when its `State, in user terms` cell says it is set in
another application, needs time to pass ("more than 90 days ago", "more than 14 days overdue"), or
needs a payment to fail. Never run its seeder: the hint is for a human.

A flow that starts from an Unable-to-verify flow is Unable to verify too, naming that flow.

```
Flow 3 — <name>
start from: S4 — the team has an archived shelf — as owner
  account: team `t-301` · archived shelf `s-40` (accounts.md, last verified 2026-10-20)
attribution: #228
  3.1  <action> → <observable result>
```

### The missing-account stop

**Any missing account is a stop before the gate.** Name every one in one message, then end the
turn:

```
prove-branch cannot start these flows: accounts.md has no <env> row for their state.
  flow <n> — <flow name>: S<n> — <the state, in user words> (page <route>)
/qa:setup-states <page folder> S<n> S<m>
```

One command per page folder, alone on its line, carrying every missing state id of that page. Then
say to run `/qa:prove-branch` again once the states are recorded. No scenario is captured, no driver
starts, and no receipt is posted.

**The stop asks for no id and invites none.** It names the command that finds the state, and
nothing else: no question, and no offer to take a team, an org, a URL or an id instead. A developer
who answers with an instance anyway is recorded by `### Write-backs`.

### Write-backs

A developer's answer during a run is written to the file it belongs to, so no later run asks again.
These are the **only writes** this skill makes to either file:

- **An instance, named after the missing-account stop** — "team `t-301` has archived shelf `s-40`".
  Append one `accounts.md` `## States` row: the `Env` from `### Staging or not`; the org, which is
  the `## Orgs` row for that `Env` unless the developer names another; the page's route; the state
  id; the ids the developer named, in user words; today's date (`date +%F`) as `Last verified`; and
  origin `developer, <today's date>`. Never change or delete another row. Then resolve the flow from
  the new row and carry on.
- **An answer to an open question** of the page's `KNOWLEDGE.md` (`Q<n>`). Write it through
  `qa:build-knowledge`'s update mode: read
  [`../build-knowledge/SKILL.md`](../build-knowledge/SKILL.md) → `## Update mode` and apply it to the
  page folder exactly as `/qa:build-knowledge <page folder> --fact "<Qn>: <answer>"` would, touching
  nothing that mode does not touch. Name that command in the print.

An answer that is not a fact — a guess, a "probably" — is not written; ask the one question that
would make it one. Say each write-back in the next print: the file, the row or the question, and the
origin. A write-back is never committed.

### Handed over

- To `## The approval gate`: every flow with its resolved state, and the Unable-to-verify flows with
  their reasons and remedies.
- To `## Driving`: the flows that are ready, each with the ids of the state it starts from — the
  `accounts.md` row's org and ids.
- To `## Receipt`: the Unable-to-verify flows with their reasons and remedies, and the uncovered and
  ambiguous criteria.

No Unable-to-verify flow is driven.

## Scenarios

A **scenario** is a saved login session for one role plus a short description of it. The pass signs
in through scenarios only: no flow, sub-step or driver ever handles a credential.

Scenarios are settled after `## Preparing states` has resolved every flow's state, since the flows
name the roles, and before `## The approval gate`.

### The scenario directory

Scenarios live in **`.qa-scenarios/`** at the root of the project's working tree, one directory per
role:

| Path | What it holds |
|---|---|
| `.qa-scenarios/<role>/session.json` | the saved session, as a **Playwright storage-state file** (`cookies` and `origins`), the form the driver loads |
| `.qa-scenarios/<role>/scenario.md` | the description: the role, the session method, the origin the session was captured against, and the date captured |

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
They are the only things it writes on the developer's machine, neither reaches the repository, and
a later run reuses both.

### Reuse or capture

For each role the flows use, before anything else uses it:

1. **Reuse** the saved session when `session.json` exists, its cookies cover the target's host, at
   least one of them is unexpired, and the target accepts it: a request made with the session
   loaded, to a page or endpoint a signed-out visitor cannot use, comes back signed in — not a
   redirect to sign-in, not a `401` or a `403`.
2. **Otherwise capture it again**, by the adapter's *Session method* row. A missing row, or a value
   that is neither `api` nor `manual`, is a stop that names the row.

Say for each role whether its scenario was reused or captured.

**A session is a secret too.** Never print `session.json` or read it into this conversation. Inspect
it only through a command that prints cookie names, domains and expiry, never a value.

### `api` — one sign-in call

Read the role's two variable names from the *Credential environment variables* row. A role the
flows use that the row does not list is a stop that names the role. **When a named variable is unset
in the shell, stop and name it** — the role and the variable — and tell the developer to set it and
run again. Never ask for a value. If the developer types a credential into the session anyway, do
not use it and do not repeat it; say to set the variable instead.

Make the sign-in call against the endpoint written after `api` in the *Session method* row,
resolved against the target URL when it is a path. **Reference each credential by its variable name
in the command**, so the shell expands it and the command text never holds a value:

```bash
umask 077
curl -sS -o /dev/null -w '%{http_code}\n' -c .qa-scenarios/<role>/jar.txt \
  [-u "$<BASIC_USER_VAR>:$<BASIC_PASS_VAR>"] \
  --data-urlencode "<username-field>=$<USERNAME_VAR>" \
  --data-urlencode "<password-field>=$<PASSWORD_VAR>" \
  '<target-url><sign-in-endpoint>'
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
- Convert the cookie jar into `session.json` with one command that prints only the cookie count.
  Each jar line becomes a cookie with its `name`, `value`, `domain`, `path`, `expires` (`-1` where
  the jar gives `0`), `secure`, `httpOnly` (from a `#HttpOnly_` prefix on the line) and
  `sameSite: "Lax"`; `origins` is an empty list. Then delete the jar.
- A sign-in that sets no cookie — a token returned in the body for the app to keep — cannot be
  saved as a session the driver loads. Stop, say so, and suggest `manual` for this project.

Then confirm the target accepts the new session, as in step 1 of *Reuse or capture*.

### `manual` — one login in a visible window

Propose the command and wait for a yes; it opens a browser window and runs until the developer
closes it:

```bash
npx playwright open --save-storage=.qa-scenarios/<role>/session.json '<target-url>'
```

Tell the developer which role to sign in as, to sign in in that window, and to close the window once
the app shows them signed in. Playwright writes the session when the window closes; the skill never
sees what was typed. When Playwright or its browser is not available, say which and stop — never
install anything into the project. Then confirm the target accepts the new session, as in step 1 of
*Reuse or capture*.

### No credential value leaves the shell

A credential value appears in **none** of these: the adapter, a flow, a sub-step, `scenario.md`, the
receipt, a prompt to a driver. The only file under `.qa-scenarios/` that holds anything secret is
the `session.json` a sign-in produced.

**Handed over**, per role: the path to its `session.json` and its `scenario.md` description. A driver
is given the path, never the file's contents and never a credential.

## The approval gate

Show the composed pass **once**, whole:

- the target URL and the SHA tested;
- the flows, numbered, each with its name, `start from:` line, the `account:` line its state
  resolved to, attribution and sub-steps;
- the coverage map, with uncovered and ambiguous criteria called out;
- the Unable-to-verify flows, each with its reason and remedy.

The developer may edit — drop or add a flow, change a sub-step, settle an ambiguous criterion — or
say go. An edit is applied, a new flow's state is resolved by `## Preparing states`, the coverage
map and the Unable-to-verify list are recomputed, and the changed list is shown again. **No driver
starts without go.**

This is the pass's one approval gate. No flow asks for approval again.

## Driving

Each ready flow is driven by its own `qa-driver` agent in a real browser against the target. The
skill prepares the run folder, checks that Playwright MCP is there, and dispatches the drivers. It
never drives a flow itself and never judges what a driver saved.

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
  request, the target URL, the SHA tested (marked `developer-stated` where it applies), the time
  the run started, and per driven flow its role and the ids of its starting state. It carries no
  credential and no session contents.
- The skill writes `run.md` and creates every `flow-<n>/step-<k>/` folder before any driver
  starts, so a driver only saves files into folders that exist.
- **`driver.md`** is the driver's report, saved verbatim by the skill when the driver returns.
- A run never reuses an earlier run's folder, and the skill deletes none. Since the folder sits
  under `.qa-scenarios/`, `git status --short` shows nothing but this run's write-backs
  (`### Write-backs`); confirm it after creating the folder, and stop if it shows anything else.

### Playwright MCP readiness

Before any driver starts, run the readiness check in
[`browser-readiness.md`](../references/browser-readiness.md) → *Playwright MCP readiness*, including
its rule for one browser context per driver. When it stops, the remedy it names ends with running
`/qa:prove-branch` again.

### Dispatching the drivers

**One `qa:qa-driver` per ready flow.** The flows handed over by `## Preparing states` are the
ready ones; an Unable-to-verify flow is never driven.

- **Every flow that starts from a state or the target URL is dispatched at once, in
  parallel** — all those `Agent` calls in one message.
- **A flow that starts from a prior flow** is dispatched when that flow's driver has returned, and
  only when that driver reported every sub-step `performed`. Otherwise the flow is Unable to
  verify, with the reason `flow <m> did not complete`, and goes to `## Receipt` undriven.

**The driver prompt carries exactly these:**

- the flow — number, name, `start from:` line and sub-steps, as approved at the gate;
- the role, and the **absolute path** to that role's `.qa-scenarios/<role>/session.json` — one
  path per role for a flow that signs in as several;
- the ids of the starting state;
- the target URL;
- the absolute path of the flow's folder, `<run folder>/flow-<n>/`.

**A driver prompt carries a session path, never a credential value** — not a password, not a
token, not a cookie, not the session file's contents. It carries nothing about the code either:
no diff, no file names, no commit subjects, no criteria.

When a driver returns, save its report as `flow-<n>/driver.md`. A driver that reports
`missing input` is re-dispatched once with the input supplied; a driver that reports
`session not accepted` makes its flow Unable to verify, with that reason.

## Grading

**The skill never grades.** One `qa:qa-grader` call grades every driven flow, in a fresh context.

### What the grader is given

- the driven flows — number, name, `start from:` line and sub-steps;
- the criteria, numbered, each with its source;
- the coverage map;
- the absolute path of the run folder.

**What it is not given**: the diff, the code, the commit subjects, the ticket beyond its
criteria, the reasoning that produced the flows, the hygiene results, the scenarios, and anything
from this conversation. The grader judges the evidence the way a tester who never saw the code
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

The developer is pulled in for **exactly four things**, and for nothing else:

1. an **Unable-to-verify** flow or sub-step — from `## Preparing states`, `## Driving` or
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
happened to each. A pass that stops before any driver starts posts no receipt, since nothing was
tested.

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
  pass, where it stopped.

Then four sections, **in this order**, each present and reading `none` when empty:

1. **Unable to verify** — each Unable-to-verify flow and sub-step with its reason, then each
   uncovered and each ambiguous criterion with its coverage-map reason. Every item carries a
   **suggested remedy**: the one change that would make it checkable — the
   `/qa:setup-states <page folder> S<n>` or `/qa:build-knowledge <page folder>` command to run, the
   state's `Seeder (for a human)` hint for a state this app cannot make, the variable to set, the
   target to confirm as staging, the reading of the criterion to settle, or the check a human makes
   by hand.
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
before that, when the skill stops after a driver started, or when a fix-now commit landed: the
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
