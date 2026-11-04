# ADR 0024 — Nights run the loops unattended

- **Status**: Accepted
- **Date**: 2026-11-03
- **Context**: PRD #263 (sprint planning and unattended night runs), issues #264 to #268

## Context

The loops (`work-on-prd`, `work-on-spec`) pause for a human at several points. Running them on a
headless server at night needs every pause to resolve without one, and needs a hard limit on a run
nobody watches. Five choices came out of that. Each has a fair alternative that was rejected.

## Decision

**Skip over stop.** Under `--unattended`, a failed child, a deviation or an ambiguity gets the
existing escalation comment, the `needs-human` label, and one unchecked line in the child's
`## External steps`. The loop then continues, and the existing rule skips a child with an unmet
external step. Stop is kept for the cases where continuing is unsafe: zero children, two open PRs
for one parent, a branch-name collision, a blocker outside the parent, the second consecutive
failure. The accepted cost is that one undecidable child leaves a partly built PRD. The rejected
alternative is to stop on every pause: it is simpler, but one bad child then ends the whole night.

**External steps over a label filter.** The skip works through `## External steps`, which the pick
already reads. `needs-human` is a scanning convention like `needs-qa`; nothing in the pick path
reads it. A failure therefore stays out of the next night until a human ticks the line. The
rejected alternative is a label filter in the pick: it makes a label gate scheduling, which this
repo refuses on both trackers, and a mistyped label would silently empty or fill the pick.

**Caps in the caller over caps in the skill.** The night script owns the limits: an outer
`timeout`, `--max-turns`, and a high `--max-budget-usd` as a last fence only. The dollar figure is
a client-side estimate and is unverified behind some billing backends, so nothing relies on it.
The skill keeps only the zero self-fix rule at the boot, screenshot and end-to-end rungs. The
consecutive-failure counter stays in the session. The rejected alternative is a budget the skill
counts for itself: the agent would judge its own limit, and the limit would stop working exactly
when the agent is confused.

**A private plan file over tracker state.** The schedule lives in `.sprint/plan.md` at the root of
the projects directory, which is not a repo. The night script reads only that file and calls no
tracker API. Coworkers see ordinary PRs and issues and nothing about the schedule. The accepted
cost is that the plan exists on one machine and a second machine does not see it. The rejected
alternative is to keep state in labels or a board column: it is shared and survives a lost disk,
but it publishes a private schedule and puts the night script in the tracker business.

**An unattended Stop ends the session with `kill -TERM "$PPID"`.** The Stop path prints the
existing final report, then runs that command from Bash. No `claude -p` flag lets the model set
its exit code, and the night script reads the exit code as its only signal: 0 sets `ran`, anything
else sets `needs-human`. The human chose this over a stop marker in the result JSON that the script
would parse. The marker is rejected because it adds a parse contract this design refused. Accepted
costs:

- A stopped run writes no result JSON, so the night report has no cost or turn data for it. The
  transcript survives under the pre-assigned session id.
- The caller's allow-list must permit `Bash(kill:*)`. Under `--permission-mode dontAsk` a missing
  entry makes the kill fail, the session exits 0 and the row reads `ran`, a silent false success.
  `night.sh` therefore adds `Bash(kill:*)` to the allow-list when the env file omits it.
- The kill is untested under Linux PID namespaces. The first real night is the test.

## Consequences

Everything is additive or behind a flag, so the plugins take minor bumps and every default
behaviour is unchanged. A change to `install/adapter.template.md` counts as a change to every
plugin that symlinks `install/`, so `figma-tools` and `qa` take patch bumps. The first real night
answers two questions this record cannot: how the permission classifier behaves over a long run,
and what a skill's interactive question does under a mode that denies prompts.
