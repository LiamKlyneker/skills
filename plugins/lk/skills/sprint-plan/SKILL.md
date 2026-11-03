---
name: sprint-plan
description: >
  Plan a sprint across several repos from the root of a projects directory: read the sprint's
  tickets from Jira by JQL, group them with the developer, and keep a private plan file in
  `.sprint/` that a night script runs the implementation loop from. A re-run merges new tickets
  and refreshes PR links without touching a row the developer edited. Invoke /lk:sprint-plan,
  optionally with a local sprint file to read instead of Jira.
disable-model-invocation: true
---

# sprint-plan

**Turn a sprint into an ordered plan of work items, one repo and one PR each, and keep that plan where a night run can read it.**

The skill runs at the **root of a projects directory**: a folder that holds several repos as child directories and is not itself a git repository. Everything it writes goes into the dotted folder `<root>/.sprint/`, which belongs to the developer and is never committed anywhere.

It **files nothing**. The ticket source is read-only: every PRD or spec a row points at is filed on that repo's own filing tracker by the usual skills. The plan file is the only state this skill keeps.

**Out of scope**, and not to be improvised: a ticket source other than Jira, a `--status` summary, and a chat notification.

## Invocation

`/lk:sprint-plan [<sprint-file>]`

- No argument: read the sprint from Jira (step 2).
- `<sprint-file>`: a local file holding the sprint's tickets, as `../_shared/ticket-source.md` §1 treats a local file. Read it instead of Jira and call **no** tracker. Its tickets stand in for the JQL search result. Where it states the site or the query, use them; otherwise ask, as on any first run.

## The plan file

`<root>/.sprint/plan.md`. The night script parses it, so its shape is a contract: section headings, column names and state names are literal.

```markdown
# Sprint plan

- Ticket source: `jira · site <host>`
- Sprint query: `<JQL>`

## Repo map

| Attribute | Value | Repo |
|---|---|---|
| component | Web | atelier-web |
| key | ATL-31 | atelier-api |

## Groups

| Id | Tickets | Repo | State | PRD | PR | Note |
|---|---|---|---|---|---|---|
| G1 | ATL-12, ATL-14 | atelier-web | planned | | | |

States: planned · grilled · runnable · running · ran · done · blocked · needs-human
```

- **Header.** The ticket-source site, the sprint's JQL, and the **repo map**: one row per ticket attribute (`component`, `label`, `epic`, `project`, or `key` for a single ticket) mapped to a child directory of the root. A ticket's repo is the first map row it matches.
- **Groups.** One row per work item, in the order they should run.
  - `Id`: `G1`, `G2`, … in creation order; never reused or renumbered.
  - `Tickets`: ticket keys, ascending, separated by `, `.
  - `Repo`: a child directory of the root.
  - `PRD`: `#<n>` for a GitHub PRD, the work-item URL for an Azure DevOps `[SPEC]`, or empty.
  - `PR`: the run's pull-request URL, or empty.
- **States**, with who sets each:

| State | Means | Set by |
|---|---|---|
| `planned` | grouped, nothing defined yet | this skill, on a new row |
| `grilled` | the grill is done | the developer |
| `runnable` | filed, sliced, readiness clear | `/prd-workflow:to-prd-tasks` on a yes, or the developer |
| `running` | a night run holds it | the night script |
| `ran` | the night run exited 0 | the night script |
| `done` | merged | the developer |
| `blocked` | waits on work outside the developer's control | this skill on a yes, or the developer |
| `needs-human` | a night run exited non-zero or could not start | the night script |

The `States:` line stays at the end of the file, verbatim.

**The snapshot.** Every time this skill writes `plan.md` it writes the same bytes to `<root>/.sprint/plan.snapshot.md`. Nothing else writes the snapshot, and nobody edits it. It is how a re-run knows which rows the developer changed.

## 1. Find the root

The root is the working directory. Check that it is **not** a git repository and that it has child directories. If it is a git repository, stop: say the skill runs one level above the repos, and name the parent directory.

`<root>/.sprint/plan.md` exists → this is a **re-run**; go to step 5. It does not exist → this is the **first run**.

## 2. Read the sprint

On a first run, ask for what the header needs and nothing else: the Jira site host and the sprint's JQL (offer `sprint in openSprints() AND project = <KEY>` as the default). Where a child repo's adapter has a `Ticket source:` line, offer its site.

Fetch with the Atlassian MCP's `searchJiraIssuesUsingJql`:

- `cloudId` = the site host, per `../_shared/ticket-source.md` §2's Jira rules. Never store a cloud UUID.
- `jql` = the sprint query, unchanged.
- `fields`: `summary`, `status`, `issuetype`, `parent`, `components`, `labels`, `issuelinks`.
- Page until no next-page token comes back. A truncated sprint is a silent miss.

An unreachable Atlassian MCP is a stop, named as such: say the server is not connected and that a local sprint file is the offline route.

## 3. Map tickets to repos

Match each ticket against the repo map. On a first run the map is empty: propose rows from the tickets' components or projects, one per child directory you can pair, and ask the developer to confirm them in one round.

**A ticket that matches no map row is asked about**, never guessed at: name the ticket and its summary, offer the likeliest child directory, and on the answer add a map row, keyed on the ticket's component where it has one and on its key otherwise.

## 4. Propose groups

Group the tickets into work items, each one repo and one PR:

- Same **epic** (the `parent`), same repo → one group.
- **Issue links**: `blocks` / `is blocked by` inside the sprint orders the groups; a ticket blocked by a ticket **outside** the sprint, or by another team's work, proposes the group as `blocked` and names the blocker in `Note`.
- **Component** and **labels** split a large epic or join loose tickets; say which attribute drove each proposal.

Present the proposal as one numbered list: group, tickets, repo, proposed order, proposed state, and one line on why. **Ask the developer to confirm, merge, split or reorder. Never decide alone**: nothing is written until they answer. Write the confirmed groups as rows with state `planned`, or `blocked` where they confirmed it.

Then on a first run, step 6 and step 7. On a re-run, step 7.

## 5. Re-run: merge, never overwrite

Read `plan.md` and `plan.snapshot.md`. A row is **developer-edited** when its `Id`, `Tickets`, `Repo` or `Note` cell differs from the same row in the snapshot, or the row is missing from the snapshot, or there is no snapshot at all. `State`, `PRD` and `PR` are not compared: the night script, `to-prd-tasks` and the developer all write them in the ordinary course of a sprint.

**A developer-edited row is left byte-for-byte as it is.** No ticket is added to it, its PR is not refreshed, and its state is not touched. Rows the developer deleted stay deleted, and their tickets count as planned.

Then:

1. **Re-read the sprint** (step 2, with the header's site and query; no questions).
2. **New tickets** are the ones in no row. Map them (step 3) and propose where each goes (step 4): into an existing row that is not developer-edited, or into a new row. A ticket whose natural group is a developer-edited row goes into a new row, and the proposal says so. Confirm before writing.
3. **Refresh PR links** on rows that are not developer-edited and carry a `PRD`:
   - GitHub `#<n>`: in `<root>/<repo>`, find the pull request whose body has the line `PRD: #<n>` — `gh pr list --state all --limit 500 --json url,body --jq '[.[] | select(.body | test("(^|\n)PRD: #<n>[ \t\r]*(\n|$)"))] | .[0].url'`. Match the whole line; `PRD: #12` is a prefix of `PRD: #127`.
   - Azure DevOps: the pull request linked from the `[SPEC]` work item.
   - No pull request found → leave the cell as it is.
4. **Write** `plan.md` with the merged rows, every other byte unchanged, then the snapshot.

## 6. First run only: the night script and the server checklist

Copy `scripts/night.sh` from this skill's base directory (the harness names it when it loads the skill) to `<root>/.sprint/night.sh`, and make it executable. Copy it on the first run only, or when the developer asks to refresh it: a plugin update changes no running night until the copy is refreshed.

Print the server checklist, filled in with this plan's repos:

```
Server checklist — do these by day, not at 03:00
- [ ] A dedicated clone per repo on the server, under the root: <root>/<repo> for each of <repos>. Nothing else uses those clones.
- [ ] A long-lived auth token: `claude setup-token`, stored as CLAUDE_CODE_OAUTH_TOKEN.
- [ ] <root>/.sprint/night.env, mode 0600: the token, NIGHT_MODEL (orchestrator), NIGHT_WORKER_MODEL (cheaper, for workers), NIGHT_ALLOWED_TOOLS (each project's git, tracker and test commands), the caps (NIGHT_MAX_RUNS, NIGHT_TIMEOUT_SECONDS, NIGHT_MAX_TURNS, NIGHT_MAX_BUDGET_USD), and PATH. `night.sh --help` lists every variable.
- [ ] The cron line: 0 1 * * * <root>/.sprint/night.sh >> <root>/.sprint/cron.log 2>&1
- [ ] On every filing tracker: the labels needs-human, needs-qa, needs-triage, ready-to-start, state:in-progress, state:done-on-branch.
- [ ] A dry run on the server: <root>/.sprint/night.sh --dry-run
```

## 7. Print the next command

End every run with the next command for each row that has one, in plan order, and nothing the plan file already shows:

| Row state | Next command |
|---|---|
| `planned` | `/lk:grill` in `<root>/<repo>`, then set the row `grilled` |
| `grilled` | `/lk:readiness` in `<root>/<repo>`, then `/prd-workflow:to-prd` (or the ADO spec skill), then `/prd-workflow:to-prd-tasks` |
| `runnable` | none by day; the night runs it, or `<root>/.sprint/night.sh --dry-run` to see the command |
| `ran` | review the PR, then `/prd-workflow:manual-qa #<prd>` where the PRD carries `needs-qa` |
| `needs-human` | read `<root>/.sprint/nights/<date>.md`, act on the escalation, then set the row `runnable` |
| `blocked` | none; name the blocker |

Print every row a re-run left untouched because the developer edited it, and every ticket still unmapped. Those are exceptions, and an exception is never cut for brevity.

## The night script

`.sprint/night.sh` is mechanical, which is the one reason this skill ships a script. It reads only the plan file and the 0600 env file beside it. For each `runnable` row in order, up to the night's run cap, it sets `running`, enters `<root>/<repo>`, and runs the loop headless:

`claude -p "<loop command> --gate=end --unattended"` with a pre-assigned session id, JSON output, a permission mode that denies rather than prompts, the env file's allow-list, a turn cap, a high dollar cap as a last fence only, all under an outer wall-clock `timeout`.

Exit 0 sets the row `ran`; any other exit sets `needs-human`. The exit code is the only thing it reads from the run. It writes `.sprint/nights/<date>.md` from the result JSON, with the cost estimate as information, and keeps the raw output beside it. A lock file makes an overlapping night exit at once. It calls no tracker, reads no git state and posts nothing. `night.sh --help` has its flags, its env variables and its exit codes; they are not restated here.
