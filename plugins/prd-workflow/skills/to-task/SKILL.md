---
name: to-task
description: >
  Publish one self-contained task from a grill's consensus, skipping the
  PRD → to-prd-tasks ceremony. Transcribes the settled decisions into a `[TASK]` issue a
  cold worker can implement — and, when the grill worked from a design brief, embeds the
  pinned screenshots, pastes the fidelity ledger rows in scope as build instructions and
  ends with the scorecard as a screenshot-pair verify checklist. Use when a conversation
  has reached consensus on work one worker session can carry. Invoke /prd-workflow:to-task.
---

# To Task

```
/prd-workflow:to-task [<ticket>] [<brief-path>] [--out <path>]
```

Takes the **current conversation** — any session that has reached a settled consensus, usually a
`deep-grill` — and publishes **one** implementation task to the project tracker.

Use it instead of `to-prd` → `to-prd-tasks` when the work is a single task that one worker session can
carry: a small feature, a bug fix, a refactor, a design-fidelity pass. There is no PRD, no sub-issue
tree. One task, one commit, one verify pass.

Do **not** interview. The decisions are already made; this skill only transcribes the consensus into
a shape a cold worker can implement. The body is read by a machine, so nobody is asked to confirm it
before it is filed.

## Inputs

| Input          | Where it comes from |
| -------------- | ------------------- |
| `<ticket>`     | optional argument — a ticket key from the project's ticket source. Goes in the title. |
| `<brief-path>` | optional argument — the design brief the grill read. Given, the skill runs in **ledger mode**: the brief is the source of the fidelity ledger rows and the pinned prototype SHA. |
| `--out`        | optional argument — a path. Given, the title and body go to that file and **no** issue is created; absent, the issue is filed. |
| The consensus  | this conversation. Source of the decisions, the scope boundary and — in ledger mode — `## Fidelity decisions`. |
| Project facts  | `<repo-root>/.claude/project/adapter.md` — tracker, title prefixes, verify ladder, repo discipline. Never hardcode these. |
| Scorecard      | ledger mode only — the file the adapter's `Fixed scorecard` row names, `## Scorecard`, when the adapter registers that row and the file has one for this ticket. |

**Telling the two positional arguments apart.** Both are optional and neither has a flag, so take
them by shape: an argument that names an existing file is the brief; anything else is the ticket
key. Two arguments that both name files, or a brief path that does not exist, is a stop — say which
and do not guess.

## Preflight

Before writing a single line of the body:

1. Read the adapter. Take the tracker from its **`Tracker:`** / `Issue tracker / PRs:` rows, the
   **`[TASK]`** prefix from its `## Repo` → *Title prefixes* row, and the **L2 floor** command from
   its `## Verify ladder`.
2. Find the consensus in the conversation: what is being built, the decisions taken and their
   reasons, and what was explicitly left out.
3. **Stop on an unresolved decision the task depends on.** List each one and stop — do not fill the
   gap with a judgement of your own. A question nobody answered is not a decision.
4. Settle **scope**: what this one task covers. Everything else the conversation raised goes under
   `## Out of scope` by name, so a reader can tell "not this task" from "forgotten".
5. Explore the codebase for what `## Worker context` needs: the real paths the change touches, the
   scoped `CONTEXT.md`(s), prior art. Paths come from the repo, never from memory.

**Ledger mode** — a `<brief-path>` was given. Also, before writing:

6. Read `<brief-path>` in full. Pull out: the pinned prototype repo + SHA, the prototype path, the
   spec / component-state URLs. The `## Fidelity ledger` rows are not read into prose here: they are
   printed by the extraction command in `../_shared/fidelity-ledger.md` §1 when the ledger section
   is written, and pasted from that output with every column intact. Note the ledger's column order;
   the issue keeps it. If the adapter's L3 row says visual verify is deferred, the screenshot pairs
   are still written into the issue — they are the run's scoring instrument, not an automated gate.
7. Settle where the verify rows come from, per `../_shared/fidelity-ledger.md` §5. Read the file
   the adapter's `Fixed scorecard` row names, when the adapter registers one, and use its
   `## Scorecard` rows and its `## Polish checklist` **only when that file carries them for this
   ticket**; both then go into `## Verify` verbatim. With no such row, or for any other ticket,
   derive the scorecard rows from the ledger per §5 and omit the polish checklist.
8. Find the grill's **`## Fidelity decisions`** block — the consensus list, one entry per ledger
   row, giving the decided class (`DS as-is` / `DS with overrides` / `local component` /
   `DS change`) and any named override.
9. **Stop if any of these is missing.** A ledger row with no decision, a decision with class
   `OPEN`, or no `## Fidelity decisions` block at all means the grill is not finished. Say which
   rows are unresolved and stop.

## Hard rules

In every mode:

- Reference **named symbols** (component, prop, handler, function) and real paths, never a line
  number.
- Introduce no fact the consensus does not hold. Where the task needs more detail than the
  conversation settled, that is an unresolved decision (preflight step 3), not a gap to fill.

In ledger mode, hard rules 1–9 of `../_shared/fidelity-ledger.md` §2 also apply. Read them before
writing the body; a body that breaks any of the nine is not published.

## Title

```
[TASK] <Feature> (<ticket>): <one-line scope>
[TASK] <Feature>: <one-line scope>
```

The second form when there is no ticket key. `[TASK]` is shorthand for the adapter's *Title
prefixes* row; if that row names a different prefix, it wins. `<Feature>` is the product-facing
name, `<ticket>` the ticket key, if any, and the one-line scope names **what** is in scope — the
elements, in ledger mode — not the technique.

Example: `[TASK] Shelf picker (SHELF-12): search band, option list, new shelf row`.

## Issue body

Write the body per `../references/task-body.md`: the **core** and **standalone** sections, plus the
**fidelity** sections in ledger mode. In ledger mode `## Changes` replaces `## What to build`.

`## Blocked by` reads "None - can start immediately" unless the consensus named a blocker.

In ledger mode, every screenshot block carries its fetch line and every source-slice block its
`gh api … | sed -n` fetch line, pinned to the brief's SHA, per `../_shared/fidelity-ledger.md` §3
and §4 — with or without `--out`, and even where the prototype sits in the same repository. The
fetch line is what `work-on-task`'s evidence gate runs; a slice with only a path has none.

## Publishing

**With `--out`, this whole section is one step: write the title on the first line, one blank line,
then the body verbatim, to that path.** Then go straight to the final print. Nothing is created and
the tracker is never called. Do not write the body anywhere else first. A sandbox with no network
and no tracker credential still produces the whole deliverable this way.

Without `--out`:

1. Write the finished body to a scratchpad file — never inline it into a shell argument, since the
   body contains backticks, pipes and markdown image syntax that a shell will mangle.
2. Create it:

   ```bash
   gh issue create \
     --repo <tracker> \
     --title "<title>" \
     --body-file <scratchpad>/task.md
   ```

3. Apply the project's filed-and-unclaimed triage label from the adapter's `Triage labels:` row
   only if the human asked for it.

## Final print

Filter: the issue is one click away and more current than any recap of it.

```
#<n> created: <url>
/prd-workflow:work-on-task <url>
```

With `--out`, there is no number and no url:

```
issue body written: <path>
/prd-workflow:work-on-task <path>
```

Those two lines close the print, bare — nothing after them. Above them, one line per **deviation** — in ledger mode, a ledger row left out of scope
because the grill never settled it, a scorecard element whose pass condition had no matching ledger
row, a screenshot whose fetch line could not be resolved at the SHA. In ledger mode, when no fixed
scorecard file carries a polish checklist for this ticket, print "no polish checklist for this
ticket" here. Print every one, even when it makes the print longer than the URL. No section recap,
no change list — the human is about to open the issue.
