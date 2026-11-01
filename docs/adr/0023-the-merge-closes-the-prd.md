# ADR 0023 — The merge closes the PRD

- **Status**: Accepted
- **Date**: 2026-11-01
- **Context**: PRDs left open after their run's PR was squash-merged, with every child closed

## Context

`work-on-prd` closes a PRD's children through the `Closes` line in the PR body's machine block.
The PRD itself was never on that line, and GitHub does not close a parent issue when its
sub-issues close. Every merged run therefore left its PRD open, and the only route to closing it
was a human remembering to.

The case for leaving the PRD open is fair: a human closing the PRD by hand is a deliberate
"this is finished" signal, and it is what Azure DevOps does with the `[SPEC]`. On GitHub nothing
reads that signal. The PRD's state is not an input to any skill, and in practice the manual close
did not happen.

## Decision

Loop end appends `closes #<prd>` to the machine block's `Closes` line, after the children, when no
child of the PRD is open. `triage` removes the entry when it links a merge-blocker after loop end,
Setup step 4 removes it whenever a resume finds an open child, and the next loop end restores it. A merge with an open child therefore closes what landed and leaves the PRD open.

The loop still never closes the PRD itself. GitHub does, on merge.

Azure DevOps is unchanged: the `[SPEC]` is closed by hand after QA.

## Rejected alternatives

**A GitHub Action that closes a parent once its last sub-issue closes.** It works without the
loop's help, but it has to be installed in every consumer repo, and ADR
[0007](0007-a-marketplace-not-an-estate-manager.md) keeps this repo out of consumer setup.

**`closes #<prd>` from PR open.** Simpler, but a PR merged early closes the PRD while children are
still open, and those children then sit under a closed parent.
