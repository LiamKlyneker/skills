# ADR 0018 — Reading a ticket is not filing work

- **Status**: Accepted
- **Date**: 2026-10-07

## Context

The adapter's `Tracker:` line answered two questions at once: where a skill **files** work, and
where a skill **reads** the ticket a human hands it. For a project that keeps both on one system
those are the same answer. For a project that reads its tickets from Jira and files its work on
GitHub, they are not, and one line cannot hold both.

Two skills read a ticket as input: `figma-to-brief` and `prototype-to-spec`. Each filters a design
down to what one ticket covers, so the ticket's body is the filter's input. `prototype-to-spec`
already accepted a local file in place of a tracker ref; `figma-to-brief` read Azure DevOps and
nothing else. No skill read Jira.

Every other skill that reads a work item reads one the loop filed itself — a PRD's children, a
`[SPEC]`'s `[TASK]`s, a run's `[FINDINGS]` item — or uses a ticket key only as a label and a path
segment (`deep-grill`, `to-task`). Those stay on the filing tracker.

## Decision

**Two lines.** `Tracker:` names where work is filed. An optional `Ticket source:` line in
`## Repo` names where tickets are read, and carries its own locator — the Jira site, or the repo
or org and project of another tracker — because the adapter keeps only the filing tracker's
sub-section. An absent `Ticket source:` line means the `Tracker:` line, so an adapter that never
gains it reads as before.

**One rule, written once**, in `_shared/ticket-source.md`, and cited by both reading skills:
a local file that exists → `Ticket source:` → `Tracker:`. The same file names the reader per
system, where each keeps its acceptance criteria, and the **ticket key** every derived path uses.

**Filing never reads `Ticket source:`.** A proposed DS gap, a `[DESIGN-SPEC]`, a PRD and a
`[SPEC]` all go to the `Tracker:` line's rows, and the next command a brief skill prints follows
`Tracker:` too.

## Considered and dropped

- **A third `Tracker:` value, `jira`.** It would make Jira a filing target, which no loop
  supports, and it would still fold reading and filing into one line.
- **Per-skill reading rules.** That is what produced one skill that took a local file and one
  that did not. Two copies of a rule drift; the shared file is the single home.
- **Inferring the source from the ref's shape** — an `ABC-123` key, an `atlassian.net` URL. A key
  pattern is not unique to one system, and a URL says where a link points, not which system a
  project trusts. The adapter states it; a URL on the wrong host is a STOP.

## Consequences

- A project that reads tickets from Jira and files on GitHub runs both brief skills, with the
  Atlassian MCP connected.
- An Azure DevOps or GitHub project with no `Ticket source:` line behaves exactly as before.
- `install-skills` asks one optional question for the `figma-tools` bundle, and "on the tracker"
  is a complete answer.
- A third skill that reads a ticket as input cites `_shared/ticket-source.md` and restates none of
  it.
