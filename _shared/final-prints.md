# Final Prints

Shared reference for what a skill says to the human in its **last print of the session**. Reference this file from a print block; don't copy it. Per-skill layouts stay per-skill — this is a **filter, not a format**.

## The filter

The tracker and the pull request are one click away and always more current than a print. So the print carries **what the browser cannot show**, and drops what it can:

- **Keep**: escalations · a skip and its reason · a failure and its reason · a deviation a reviewer needs to know about · the next slash command.
- **Cut**: ids, titles and urls of things this session just wrote · re-listings of a set that is already visible on the board or the PR · a scope recap of a body just posted.

The test is not "is this true" — it all is. It is **would the human learn this by opening the thing they are about to open anyway.**

### One URL

**One URL per final print, at most**: the single artifact the human should open next. Never a URL that is one click away from that one — a PR link plus its branch link, or a parent plus its children, is the second URL not earning its place.

### An id needs a reason

An id may carry its title **only when the human must act or decide on it now** — a recommendation, an escalation, a task that failed. Re-listing a set that was created or completed is banned, however tidy the list looks: `#61 #62 #63 created` is the board, printed twice.

### Counts

Cut the count when the list is on screen — "9 tasks done" beside nine visible rows says nothing. Keep it when the count **is** the finding: `2 skipped — reasons below`.

## The protected class

**An exception is never a valid conciseness cut.** Every skip, failure, deviation and escalation that surfaced during the run produces its own line, always, however long the list runs. Dropping one to tighten the print is the one move this file exists to forbid — the whole point of trimming the echo is to leave room for these.

When you cannot tell whether something is a deviation or noise, **print it**.

## The one formatting rule

The deliberate single exception to "no layout rules here": **every final print closes with the next slash command, id included, on its own clean line**, ready to copy-paste and nothing else on it.

```
/prd-workflow:work-on-prd #140
```

Not prose wrapped around it, not "you can now run …", not a bare skill name the human has to complete. The command line is the last thing on screen because it is the only thing they will act on.

## Scope

This governs a skill's **final session print to the human**, and nothing else. It never applies to:

- **Agent-judged reports** — a worker's report to an orchestrator stays complete, per `CLAUDE.md`. Its reader is a judge with no tracker to open.
- **Pre-creation approval gates** — a slice list shown before anything is written is the human's only chance to see it. Nothing there is an echo.
- **Tracker-posted artifacts** — a `manual-qa` receipt, a `triage` parent comment, a `[FINDINGS]` body. Those have their own contracts and their own readers.
