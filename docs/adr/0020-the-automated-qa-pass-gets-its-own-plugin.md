# ADR 0020 — The automated QA pass gets its own plugin

- **Status**: Accepted
- **Date**: 2026-10-24
- **Context**: PRD #226, implemented from #227 on

## Context

ADR [0011](0011-azure-devops-qa-is-a-tickable-comment.md) placed the two Azure DevOps QA skills in
`ado-workflow`, applying a rule it inherited from ADR
[0008](0008-prd-qa-skills-belong-to-prd-workflow.md): **a QA skill lives in the plugin of the loop
whose literals it shares.** ADR [0012](0012-the-qa-pass-is-composed-from-the-branch.md) retired the
parse contract those literals once formed and kept the rule anyway, because `manual-qa` and
`triage` still share `### [FINDING]`, `[FINDINGS]` and `PRD: #<n>` with their loop. `CLAUDE.md`
names that plugin-membership half of 0011 as still load-bearing.

The rule's reasoning is sound and is stated here first. A writer and a reader of the same literal
that ship in two plugins can drift: a consumer updates one plugin and not the other, and the reader
looks for a string the writer no longer writes. A miss of that kind is silent — a triage pass that
matches nothing reports a clean run. Putting both ends in one version-bumped plugin makes them move
together by construction, and that guarantee costs nothing while the QA skill is mostly tracker
plumbing.

For `manual-qa` that held. Its tracker work — find the run, file a finding, post a receipt — was a
large share of the skill, the human drove every step, and the tracker-specific part was most of
what made the GitHub and Azure DevOps copies differ.

PRD #226 adds an automated pass, and its shape is different. The large parts are the composer,
which turns the diff and the ticket's acceptance criteria into flows with a coverage map; the
driver, which runs each flow in a real browser against the pull request's preview deployment; and
the grader, which judges the evidence in a cold context. None of those three knows which tracker
the ticket came from. The tracker-specific part shrinks to three points: resolve the run from the
branch, read the criteria, and post the receipt and any finding. Under 0011's rule the pass would
need a copy in `prd-workflow` and a copy in `ado-workflow`, and the two copies would be almost
entirely the same tracker-neutral code.

## Decision

**0011's plugin-membership rule is amended, not reversed.** It still governs a QA skill whose
substance is tracker plumbing; `manual-qa` and `triage` stay where they are. It no longer governs
a QA skill whose substance is tracker-neutral.

- **The automated pass lives in its own plugin, `qa`.** One skill, `prove-branch`, invoked as
  `/qa:prove-branch`, with a driver agent and a grader agent and evals under `plugins/qa/evals/`.
  It serves both trackers.
- **It reads the tracker from the adapter at its tracker points.** `Tracker:` and the ticket source
  come from `<repo-root>/.claude/project/adapter.md` when the skill resolves the run, reads the
  criteria and posts. A tracker difference is a branch inside those three points, never a second
  copy of the skill.
- **The shared literals are read where a skill reads them today.** `prove-branch` files
  `### [FINDING]` to the same per-run `[FINDINGS]` issue or work item that `manual-qa` writes, and
  finds the GitHub run by the same `PRD: #<n>` key. Those literals are now shared across a plugin
  boundary, and that is the cost this record accepts.
- **Both `manual-qa` copies stay** in `prd-workflow` and `ado-workflow`, unchanged, until
  `prove-branch` has completed a run on a real project. Their deprecation is a later change and
  earns its own record.
- **ADR 0012 holds.** Neither loop invokes the pass; it runs on user invocation only.

## Considered and dropped

- **A `prove-branch` copy in each workflow plugin.** It keeps 0011's rule literally and duplicates
  the composer, the driver contract and the grader contract in two places that would drift the
  same way the rule exists to prevent — only between two copies of one skill instead of between a
  writer and a reader.
- **Put the pass in `prd-workflow` and have Azure DevOps projects install it.** It ties an ADO
  project to a plugin whose loop it never runs and whose adapter interview asks GitHub questions.
- **Move the shared literals into the adapter.** It removes the cross-plugin coupling and recreates
  the failure 0009 and 0011 both named: a project free to edit `### [FINDING]` gets a `triage`
  that silently finds nothing.

## Consequences

- The marketplace has six plugins. `qa` starts at `0.1.0` and follows ADR
  [0001](0001-version-the-plugins-and-enforce-the-bump.md)'s bump rule from its first content
  change.
- A change to `### [FINDING]`, `[FINDINGS]` or `PRD: #<n>` now touches up to three plugins —
  `qa` and whichever workflow plugins write or read the literal — and every one of them bumps.
  The literals have not changed since 0012, and this record does not expect them to.
- `qa` symlinks `_shared/` like every other plugin, so a change under `_shared/` counts as a change
  to `qa` too.
- Until a real-project run completes, two ways to run a QA pass exist side by side. That overlap is
  deliberate and temporary; it ends with the deprecation record.
