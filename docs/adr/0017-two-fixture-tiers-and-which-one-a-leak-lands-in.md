# ADR 0017 — Two fixture tiers, and which one a leak lands in

- **Status**: Accepted
- **Date**: 2026-09-22
- **Context**: PRD #203, implemented by #206–#209
- **Supersedes**: ADR [0015](0015-eval-suites-against-a-synthetic-fixture.md), **on its
  fixture clause only** — "a frozen issue plus the scaffolded fixture app for
  `work-on-task`". Everything else in 0015 stands, the synthetic fixture itself first of
  all: the fixture repo, the privacy rule, `--ablation none`, the run policy, and the
  platform constraints the fixture design works around.

## The reasoning that got us here, and where it stops

ADR 0015 gave every case the same fixture: the whole synthetic workspace, placed by
`scaffold-fixture.sh`. That was right for the suite it was written for. The first cases
were about hops that read a real prototype tree and a real adapter, the workspace was the
only thing that could feed them, and one shared fixture meant one thing to keep correct.

It stops being right when a case is about a single sentence of contract. Issues #194 and
#195 were two halves of one leak — an off-grid px value flowing unflagged through brief,
grill, issue and code. The transformation under test is a value in and a flagged ledger
row out. Testing it against the full workspace meant planting an off-grid value in a React
component, regenerating nine screenshots because the plant changed how a row renders,
holding a file at an exact line count because a frozen issue cites a source slice from it,
and moving two lines of a handoff README so the brief could not read a grid-aligned value
instead. None of that had run a grader yet.

The grill also found that the split is not the one the cost suggests. Every case 0015
describes is **already single-hop**; nothing here runs two hops in sequence. The expensive
part is the fixture, not the chain.

## Decision

**A case tests one contract sentence against a micro stub. The full workspace is earned,
not the default.**

### The boundary

A leak earns the full workspace only when the leak is about **fixture shape**: the skill
reading the wrong file, ignoring a pointer the adapter gave it, or mis-walking the
prototype tree. Anything else — a value that should have been flagged, a row that should
have been a grill question, a halt that should have happened — is one contract sentence,
and it goes to a micro stub.

The question to ask of a new leak is whether the *input's shape* is what the case is
about. If a hand-written seventeen-line component reproduces the leak, the workspace would
only be scenery.

### Placement and naming

Both tiers live in the same directory, told apart by tag. A case is
`plugins/<plugin>/evals/<skill>-<behaviour>/`, flat, carrying `tags: [micro]` or
`tags: [full]`. A micro case owns its stub under its own `fixture/`, and micro cases share
nothing with each other — a stub drifting to serve a second case is how a micro tier grows
back into a workspace. Every case carries a tier tag alongside any per-skill tag, and the
six full-workspace cases carry `full`, which costs the gate nothing: it selects on `micro`.

A micro case grades the artifact the skill produced — the brief, the file on disk, the
last message. `tool_used` belongs to the full tier, where which file was read is the point.

### The gate

Before any plugin version bump, every micro case in that plugin passes:

```bash
command claude plugin eval plugins/<plugin> \
  --ablation none --scaffold --no-publish \
  --runs 1 --threshold 1.0 --max-cost-usd 5 \
  --model claude-sonnet-5 --judge-model claude-sonnet-5 \
  --allow-tools Write Bash Edit --tag micro
```

Every flag carries its weight, and the bare `claude plugin eval plugins/<plugin> --scaffold
--tag micro` scores 0.00: only read-only tools are granted by default, so a skill that writes
its brief or edits a component writes nothing. `--allow-tools Write Bash Edit` is what makes
the run real, and `command claude` is what reaches the binary past a `$PWD`-switching shell
function. CONTRIBUTING.md's "Running an eval suite" section explains each of the other flags.

The full tier runs on demand, when a change touches how a skill reads the prototype tree,
the adapter, or the fixture app. It is not part of the bump gate. Mechanical gating — a
`workflow_dispatch` job carrying a credential — stays deferred exactly as 0015 left it,
for 0015's reason: a public repo's fork PRs must never see one.

### The worked example

Three cases, the first of the tier, all green at `--runs 1` on `claude-sonnet-5` for
USD 1.42 and nine minutes together:

- `plugins/figma-tools/evals/prototype-to-spec-off-grid-flagged` — a padding between two
  steps of a non-uniform spacing scale survives raw into the ledger, carries `⚠ off-grid`
  with the nearest token and the delta, gets a proposed DS-gap row, and becomes a grill
  question with both options. Micro: the input is one seventeen-line component.
- `plugins/prd-workflow/evals/work-on-task-off-grid-stops` — an issue with one `⚠ off-grid`
  row whose Decision cell is `OPEN`. The run hands the question back and writes nothing.
  Micro: a stub with one component, one 1.2KB screenshot and a `git init`.
- `plugins/figma-tools/evals/prototype-to-spec-hairline-token` — a 1px border resolving to
  the catalog's named hairline step by membership in the tier, never flagged. Micro: the
  catalog *is* the input.

By contrast, `prototype-to-spec-adapter` proves a skill follows the adapter's pointers
rather than its own defaults by giving one prototype two sets of files to find. That is
fixture shape, and it keeps the workspace.

### What a micro case proves, and what it does not

**A micro case verifies the outcome a contract sentence promises. It does not by itself
prove the sentence is load-bearing.** `prototype-to-spec-hairline-token` could not be made
red: three local reverts of the membership wording in `prototype-to-spec/SKILL.md` each
scored 1.00, because the run resolves the value against the catalog's token table whatever
the surrounding prose says. The case stays as a regression check on the outcome, and the
claim it supports is the narrower one.

**Grade the artifact, not the narration.** In the red probe of
`work-on-task-off-grid-stops`, every `last_message` grader passed while the file graders
went red: the run named the flag, the raw value and the missing decision in its self-audit,
and wrote the substitution into the component anyway.

## Consequences

- A micro case costs cents and minutes — USD 0.33 to 0.56 per run here, against USD 1.79
  for the full-fixture `work-on-task-self-audit-skipped`. The gate is cheap enough to run
  every time, which is the only reason it can be one.
- `scaffold-fixture.sh`, `prepare-history.sh` and the `skills-fixture` repo keep their
  roles unchanged, for the full tier.
- **`figma-to-brief` is reachable by neither tier.** It carries the same `⚠ off-grid`
  contract as `prototype-to-spec`, and its input is the local `figma-dev-mode` MCP server
  against a file open in Figma Desktop — which the eval child, with no network and no
  credential, cannot have. The path out is the one 0015 already uses for every external
  party: freeze the extraction, and give the skill an entry point that accepts it. Filed
  as #212, standalone, because it needs a `SKILL.md` change and PRD #203 makes none.

## Rejected alternatives

**Convert the existing six cases as part of this decision.** Rejected because the stub
shape had run nothing when the decision was made. Three cases first, then one standalone
issue per conversion, so a stub shape that turns out to be wrong is wrong in three places
rather than nine.

**Add a cross-hop or integration tier.** Rejected because nothing runs two hops in
sequence today, and a tier with no case in it is a name for work nobody has done. The
cross-hop leaks `plugins/prd-workflow/evals/fixtures/leaks.md` narrates stay narrated.

**Keep one tier and make the shared fixture cheaper.** Rejected because the fixture's cost
is what it is for: it plays a real design system, a real app with a real verify ladder and
a real prototype, and a case about fixture shape needs all three. Thinning it would take
the full tier's coverage away to pay for the micro tier's speed, when the two can simply
sit side by side.
