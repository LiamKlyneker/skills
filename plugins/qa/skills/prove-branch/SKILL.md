---
name: prove-branch
description: Run the automated QA pass on the checked-out branch — resolve the ticket, the pull request and the preview deployment from the branch alone, read the ticket's acceptance criteria, and stop with a question wherever the branch is ambiguous. Runs on user invocation only; neither loop ever invokes it. Invoke /qa:prove-branch with no argument, in a fresh session on the implemented branch.
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
the tree.

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
| *State catalog* | the named states a flow may `start from:`, the ids that identify each, and how to reach it |
| *Preview URL pattern* | how the pull request's preview deployment URL is formed, or `pr-comment` — read in `## The target` |
| *Feature-flag override* | how one session turns a flag on or off, or `none` |
| *Browser automation consent* | `yes` records that the skill may drive a real browser against the preview |

A missing `## QA` section is not a stop at this point: `## The target` stops when it needs the
*Preview URL pattern* row and finds none.

`[PRD]`, `[SPEC]` and `[FINDINGS]` below are shorthand for the adapter's *Title prefixes* row. On
`azure-devops` the prefix is load-bearing, so read it from the row; if the row names different
prefixes, they win.

On `azure-devops` the work-item and pull-request reads go through the Azure DevOps MCP server
(`mcp__ado__*`). Tool and parameter names vary by server version; where a named tool or field is
missing, discover the equivalent from the running server and announce the substitution. A read that
cannot be performed at all is a stop, never a silent omission.

## Resolving the run

The run is two things: the **ticket** whose criteria the pass proves, and the **pull request** the
preview deployment belongs to. Both are found from the branch.

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

### The stop

**Zero or several hits at every key is a stop.** Name the branch, say what each key found, and ask
the developer which ticket and pull request this run is for:

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

1. **Find the URL** from the adapter's `## QA` → *Preview URL pattern* row:
   - a **pattern**: substitute the pull-request number for `<pr-number>`, and confirm the URL
     answers before using it;
   - **`pr-comment`**: read the pull request's comments — `github`: `gh pr view <n> --repo <owner>/<repo> --json comments`; `azure-devops`: the pull request's threads through the MCP — and take
     the preview URL from the most recent comment that posts one.
2. **Read the commit the preview was built from** — the commit the deployment record, the status
   check or the posting comment names for that preview. Compare it with `HEAD`.
3. **Stop and ask the developer for a URL** when the row is absent, when no URL resolves, when the
   URL does not answer, when the preview was built from a commit other than `HEAD`, or when the
   built-from commit cannot be read at all. Say which of these it is, and give the URL and commit
   you found.

**Record two values now: the target URL and the SHA tested.** The SHA tested is the built-from
commit when it matches `HEAD`. A URL the developer supplies is recorded with the commit the
developer states it serves, marked `developer-stated`. The receipt names both.

## Criteria

Read the ticket through `../_shared/ticket-source.md` — its resolution order (§1), its one reader
per system (§2) and where each system keeps acceptance criteria. The resolving key decides the
system:

- keys 1, 2 and 3 resolve an item the loop filed, which lives on the filing tracker and is read
  from the `Tracker:` line (`../_shared/ticket-source.md` §4);
- key 4 resolves a ticket on the system its key belongs to, read from the `Ticket source:` line.

Where the ticket is a PRD or a `[SPEC]` with children, each landed child's acceptance criteria join
the list, attributed to that child.

**A ticket with no acceptance-criteria list is still valid input.** Infer the criteria from the
description and summary, and label each one `inferred`. An inferred criterion is the skill's
reading of the ticket, never the ticket's own words, and the receipt keeps the label.

**The diff is the authority.** Read it — `github`: `gh pr diff <n> --repo <owner>/<repo>`;
`azure-devops`: `git diff <default-branch>...HEAD`, since the MCP exposes no diff tool. Any planned
`## QA notes` in a child issue was written before the code existed; read it for intent and let the
diff overrule it.

## What a run prints

Once the run, the target and the criteria are resolved, print them before composing the flows:

- the ticket, the key that resolved it, and the pull request;
- the hygiene results;
- the target URL and the SHA tested, with `developer-stated` where it applies;
- the criteria, numbered, each with its source — the ticket, a child, or `inferred`.

## Composing the flows

The composer turns the criteria and the diff into a short list of **flows**. It reads four things,
all already in hand: the numbered criteria from `## Criteria`, the diff, the commit subjects on the
branch, and the adapter's *State catalog*. **It reads nothing else to write the flows** — not the
wider codebase, not the running app.

### Flows test the ticket, not the app

Every flow exists because it checks at least one criterion. **The count follows the criteria**: a
ticket with two criteria gets a short pass, and nothing the ticket does not ask about earns a flow —
no tour of neighbouring screens, no regression sweep. The diff decides how a criterion is checked:
which screen, which control, which result.

### What a flow is

A **flow** is a run of sub-steps that share a starting state and end somewhere the next flow can
begin from. Each flow has:

- a **name** — what is being exercised, in the ticket's words;
- an explicit **`start from:` line** — a state named in the adapter's *State catalog*, or a prior
  flow by number, and the role the flow signs in as;
- **sub-steps**, numbered `<flow>.<k>`, each naming one **action** and one **observable result** —
  something the page shows or the app answers, which a driver can see is there or is not;
- **attribution** — the tickets whose code the flow exercises: the `(#N)` suffixes or ticket-source
  keys on the commits that touched the files involved, or the resolved ticket itself when the branch
  carries one ticket.

```
Flow 2 — <name>
start from: `<catalog state>` as <role>
attribution: #228, #229
  2.1  <action> → <observable result>
  2.2  <action> → <observable result>
```

A sub-step whose result is not observable — "the data is saved correctly", "the error is handled" —
is not a sub-step. Rewrite it as what the page shows, or leave its criterion uncovered.

**The first flow is always "get running"**: open the target URL from `## The target` with each
role's scenario loaded (`## Scenarios`), and see the app signed in as that role — one sub-step per
role the pass uses. Its line is `start from: the target URL`, the one flow that starts from neither
the catalog nor a prior flow. A later flow that needs no particular data starts from it:
`start from: flow 1 completed, as <role>`.

**A cross-flow dependency is named in `start from:`**, never left implicit. A flow that starts from
a prior flow inherits that flow's state, and cannot run when that flow cannot.

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
| 3 | `<criterion>` | ticket | 3.2 | ambiguous — `<the readings, and the one 3.2 checks>` |

- **Uncovered**: no sub-step checks the criterion, usually because nothing a browser shows can
  confirm it. Say why in the row. Never stretch a sub-step to claim a criterion it does not observe.
- **Ambiguous**: the criterion admits more than one reading with different observable results, or
  names no result at all. Give the readings and say which one a sub-step checks, if any.
- A criterion checked only by sub-steps in Unable-to-verify flows is marked
  `unable to verify — flow <n>`.

**Uncovered and ambiguous criteria are escalations.** Both are shown at the approval gate and both
are handed to `## Receipt`. A row carries a status, never a confidence figure.

### Start states against the catalog

Check each flow's `start from:` against the *State catalog* as soon as the flow is composed:

- **a prior flow** — nothing to check; the flow follows that flow's outcome.
- **a catalog state** — checked against the target in `## Preparing states`.
- **a state not in the catalog** — the flow is **Unable to verify** now, with the reason
  `state "<what the flow needs>" is not in the adapter's state catalog`. Nothing can create a state
  the catalog does not name, so the flow is neither prepared nor driven. Compose it in full anyway,
  so the developer sees exactly what could not be checked.

Never stretch a catalog state to fit. A flow that needs a team with an overdue invoice does not
start from a catalog state whose team has no invoices.

## Scenarios

A **scenario** is a saved login session for one role plus a short description of it. The pass signs
in through scenarios only: no flow, sub-step or driver ever handles a credential.

Scenarios are settled after the flows are composed, since the flows name the roles, and before
`## Preparing states`, which signs in with them.

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
`git check-ignore -q .qa-scenarios/` succeeds and `git status --short` is still empty. If either
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
  --data-urlencode "<username-field>=$<USERNAME_VAR>" \
  --data-urlencode "<password-field>=$<PASSWORD_VAR>" \
  '<target-url><sign-in-endpoint>'
```

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

## Preparing states

Before any driver starts, confirm every flow's starting state on the target the way a tester would:
through the app or its API, signed in with the flow's scenario. Never through a database, an admin
console a tester would not have, or the project's code.

### Staging or not

Data is created **only against a staging target**:

- The pull request's preview deployment resolved in `## The target` is staging.
- A developer-stated URL is staging only when the developer says so in this session. Ask at the
  approval gate, when a flow needs data created there.
- **Data is never created against a URL the adapter or the developer names as production**, whatever
  else says otherwise.

A missing state on a target that is not staging leaves its flow Unable to verify, with the reason
`target is not confirmed as staging`.

### Check each catalog state

For each catalog state a flow starts from, confirm on the target that the ids the catalog's *Ids*
column lists are there, as the flow's role, with a request that loads the role's session and prints
only the status and the ids it checked. Each state comes out as one of these:

| Found | Outcome |
|---|---|
| present | the flow is ready |
| missing, and *Reach it by* has steps | planned for creation, and listed in the QA-created data plan |
| missing, and *Reach it by* is `none` | the flow is **Unable to verify**: `state "<state>" is missing on the target and the catalog has no steps to create it` |
| the check could not be made | the flow is **Unable to verify**, with what failed |

A flow that starts from an Unable-to-verify flow is Unable to verify too, naming that flow.

### The one approval gate

Show the composed pass **once**, whole:

- the target URL and the SHA tested;
- the flows, numbered, each with its name, `start from:` line, attribution and sub-steps;
- the coverage map, with uncovered and ambiguous criteria called out;
- the Unable-to-verify flows, each with its reason;
- the QA-created data plan: for each state to be created, the catalog's steps, the role that runs
  them and the target — and for a developer-stated target, the question whether it is staging.

The developer may edit — drop or add a flow, change a sub-step, settle an ambiguous criterion,
decline a creation — or say go. An edit is applied, the coverage map and the Unable-to-verify list
are recomputed, and the changed list is shown again. **Nothing is created and no driver starts
without go.** A declined creation leaves its flow Unable to verify, with the reason
`creation declined by the developer`.

This is the pass's one approval gate. No flow asks for approval again.

### Creating missing states

After go, for each planned state:

1. Run the catalog's *Reach it by* steps on the target as written, as the flow's role.
2. **Name the data QA-created**: every name or title the steps set starts with
   `qa-created <short SHA tested>`, so anyone on staging can tell it from real data and trace it to
   this run.
3. Check the state again. When it is still missing, the flow is Unable to verify, with the reason
   `creation steps ran and state "<state>" is still missing`.
4. Record what was created: the state, each item's name and id, and the target.

The skill does not delete what it created; the record is how a human finds it.

### Handed over

- To `## Driving`: the flows that are ready, each with its role's scenario and the ids of the state
  it starts from — the catalog's ids, or the ids of the QA-created data.
- To `## Receipt`: the Unable-to-verify flows with their reasons, the uncovered and ambiguous
  criteria, and the QA-created data record.

No Unable-to-verify flow is driven.

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

- **`run.md`** carries the ticket and the key that resolved it, the pull request, the target URL,
  the SHA tested (marked `developer-stated` where it applies), the time the run started, and per
  driven flow its role and the ids of its starting state. It carries no credential and no session
  contents.
- The skill writes `run.md` and creates every `flow-<n>/step-<k>/` folder before any driver
  starts, so a driver only saves files into folders that exist.
- **`driver.md`** is the driver's report, saved verbatim by the skill when the driver returns.
- A run never reuses an earlier run's folder, and the skill deletes none. Since the folder sits
  under `.qa-scenarios/`, `git status --short` stays empty; confirm it after creating the folder,
  and stop if it does not.

### Playwright MCP readiness

Before any driver starts, confirm that **the Playwright MCP tools are present in this session** —
`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages` and
`browser_network_requests` at least. When they are not, stop and name the remedy: add the
Playwright MCP server, start a fresh session, and run `/qa:prove-branch` again. The shape is

```bash
claude mcp add playwright -- npx @playwright/mcp@latest --isolated --storage-state <path to a session.json>
```

and the exact flags are the ones the server documents at run time. **Isolated mode plus a
storage-state file is how a saved session reaches the browser**: the browser holds its profile in
memory, starts signed in from the scenario's `session.json`, and writes nothing back to it. The
server runs headed unless the developer asks for headless, so the developer can watch.

**One driver per flow means one isolated browser context per flow, loaded with that flow's role's
session.** Confirm the connected server gives each driver its own context. When it can give the
session only one browser, two drivers would act in the same page, so dispatch the drivers one at
a time, in flow order, and say why. A role whose session the server cannot load is a stop that
names the role.

Never install the server or a browser into the project, and never add the server without a yes.

### Dispatching the drivers

**One `qa:qa-driver` per ready flow.** The flows handed over by `## Preparing states` are the
ready ones; an Unable-to-verify flow is never driven.

- **Every flow that starts from a catalog state or the target URL is dispatched at once, in
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

## Receipt

Lands in a later slice.
