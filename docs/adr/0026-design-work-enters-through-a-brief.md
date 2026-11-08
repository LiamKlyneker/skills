# ADR 0026 — Design work enters through a brief

- **Status**: Accepted
- **Date**: 2026-11-08
- **Context**: issue #257, which follows the library-repo brief from PRD #258

## Context

`figma-to-spec` and `figma-component-to-spec` wrote a design spec of their own, beside the
implementation spec for the same work. Both were specs and nothing kept them aligned, so they
drifted. Since PRD #258 a brief also covers a library repo, so the design-spec skills are no longer
the only route there.

## Decision

**One spec per piece of work, with a design section inside it, on both trackers.** The design
route into the spec chain is the brief: `figma-to-brief` or `prototype-to-brief` writes it, the
grill resolves it, and the grill's output is the one spec.

**`figma-to-spec`, `figma-component-to-spec` and their two extractor agents are deleted.**

**`prototype-to-spec` is renamed `prototype-to-brief`**, because it always wrote a brief. It gains
the `Repo role:` branch `figma-to-brief` has.

**`figma-to-brief` owns what it used to borrow.** `catalog-contract.md` and `resolution-rules.md`
move into its `references/`. The node-read rules from the region extractor become
`references/figma-read-discipline.md`. The triage section of the resolution rules is removed,
because it fed a checkpoint that no longer exists.

**Adapter rows with no reader are removed**: `Gap policy`, `Gap tracker`, `Provisional expiry`,
`Story convention`, `Design-spec target` and `Downstream implementer`. A brief decides nothing and
the grill is the human gate, so a stop-and-ask policy has no consumer. `Provisional marker` stays,
because `design-component` reads it. Existing adapters keep any of these rows; nothing reads them.

## Rejected alternatives

**Keep the design-spec skills beside the brief.** Two routes to a spec is the drift this removes.

**Generalise `figma-to-spec` into the universal spec producer**, option (b) of #17. It would keep
the second spec artifact and is dead with this decision.

## Consequences

`figma-tools` moves to `6.0.0`, a breaking change: two skills are gone and one is renamed. Earlier
ADRs keep the old skill names, because they record the state at the time they were written.
