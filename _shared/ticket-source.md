# Ticket source

How a skill that **reads** a ticket gets its body. One rule, cited by every skill that takes a
`<ticket-ref>` argument and never restated in one. A skill that **files** work does not read this
file: filing goes to the tracker the adapter's `Tracker:` line names, and nothing here changes
that.

Reading a ticket and filing work are two separate facts about a project, and one project can keep
them on two systems — tickets in Jira, work filed on GitHub. The adapter's `## Repo` section
therefore carries two lines: `Tracker:` is where work is **filed**, and the optional
`Ticket source:` is where tickets are **read**. An absent `Ticket source:` line means tickets are
read from the `Tracker:` line, so an adapter that never gains the line reads exactly as it did.

## 1. Resolution order

Take the first step that applies, and stop there.

1. **A local file.** `<ticket-ref>` is a path to a file that exists, relative to the working
   directory or absolute. Read the file; its contents are the ticket body. **No tracker is
   called** — not the ticket source, not the filing tracker — which is what lets a run work
   offline against a ticket someone put on disk.
2. **The `Ticket source:` line**, where the adapter carries one. Fetch from the system it names,
   per §2.
3. **The `Tracker:` line**, where there is no `Ticket source:` line. An absent `Tracker:` line
   means `github`, per the adapter template. Fetch per §2.

A `<ticket-ref>` that looks like a path but names no existing file is **not** read as a file and
is **not** an error at step 1. It falls through to steps 2 and 3, where it fails as an
unresolvable ref. Say both facts in the STOP: no file at that path, and no ticket under that ref
in the system the adapter names.

A URL whose host does not belong to the system step 2 or 3 selected is a STOP, naming the URL and
the system. Never switch systems on the strength of a URL: the adapter is the only statement of
where tickets live.

## 2. One reader per system

| System | Line value | Ref forms accepted | Fetch |
|---|---|---|---|
| `jira` | `jira · site <host>` | an issue key (`ABC-123`); a URL carrying `/browse/<KEY>` or `selectedIssue=<KEY>` | Atlassian MCP `getJiraIssue`, `cloudId` = the site from the line, `issueIdOrKey` = the key, `fields: ["*all"]`, `expand: "names"`, `responseContentFormat: "markdown"`, `updateHistory: false` |
| `github` | `github · repo <owner>/<repo>`, or as the `Tracker:` fallback the `### GitHub` *Issue tracker / PRs* row | an issue number; an issue URL | `gh issue view <n> --repo <repo> --json number,title,body,url` |
| `azure-devops` | `azure-devops · org <org> · project <project>`, or as the `Tracker:` fallback the `### Azure DevOps` *Organisation* and *Work-item project* rows | a work-item id; a work-item URL | `mcp__ado__wit_work_item` (`action: "get"`) against that org and project |

**A `Ticket source:` line carries its own locator**, because a project whose tickets live
outside its filing tracker has no sub-section for that system: the adapter keeps only the filing
tracker's. A line that names the same system as `Tracker:` is redundant — leave it out.

### Jira

- **`cloudId` is the site host** from the line, e.g. `example.atlassian.net`. The MCP accepts it
  in place of the cloud UUID, so the adapter never stores a UUID.
- **`issueIdOrKey` takes a key, never a URL.** Pull the key out of a URL before the call:
  the path segment after `/browse/`, or the `selectedIssue` query value on a board URL.
- **Acceptance criteria live in one of two places**, and the skill checks both:
  1. a **custom field** whose display name contains `Acceptance Criteria`, case-insensitively.
     The default field set omits every custom field, which is why the call asks for `*all`, and
     the response's `names` map — present because of `expand: "names"` — is what turns a
     `customfield_<n>` id into that display name. Never hardcode a custom-field id: it differs
     per site.
  2. a section of the **description** headed `Acceptance criteria`, in any heading level or
     case, or a bold line of that text.

  Where both carry text, both are the filter's input, the custom field first. Where neither does,
  the ticket is **still valid input**: the description and summary are the filter's input, and
  the skill's no-component scoring path applies, with its `⚠ inferred` mark.
- **An unreachable Atlassian MCP is a STOP**, named as such, not a ticket that does not exist —
  say that the server is not connected and that a local file path is the offline route.

### GitHub and Azure DevOps

The acceptance criteria are where those trackers already keep them: the issue body on GitHub; the
`AcceptanceCriteria` field on Azure DevOps where the work-item type carries one, and otherwise the
description. Either way, a ticket with no acceptance-criteria text is still valid input, on the
same `⚠ inferred` terms as Jira.

## 3. The ticket key

Every path a skill derives from the ticket — a brief, its screenshot directory, a grill file —
keys on one string, the **ticket key**, and every consumer of that path uses the same string.

| Resolved by | Ticket key |
|---|---|
| a local file | the file's name without its extension, slugged |
| `jira` | the issue key as Jira writes it, e.g. `ABC-123` |
| `github` | the issue number |
| `azure-devops` | the work-item id |

Slugging lowercases nothing a tracker capitalises — a Jira key keeps its case — and replaces any
character outside `A–Z a–z 0–9 . _ -` with `-`. A key that is a number stays a number.

## 4. What this file does not cover

- **Filing.** No skill reads `Ticket source:` to decide where work goes. A brief's proposed DS
  gaps, a `[DESIGN-SPEC]`, a PRD and a `[SPEC]` all file against the `Tracker:` line's rows.
- **Workflow items a loop reads back.** A PRD's children, a `[SPEC]`'s `[TASK]`s and a run's
  `[FINDINGS]` item are work the loop filed itself, so they live on the filing tracker and are
  read from there. This file is for the ticket a human hands a skill as input.
