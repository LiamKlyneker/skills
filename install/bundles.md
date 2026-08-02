# Bundles

What `install-skills` bootstraps. A **bundle** is a named set of skills that are only
useful together, described here by the one thing no distribution mechanism can deliver:
**which `##` sections of the project's adapter they need filled**, plus any gate template
the set implies.

That mapping is the whole point. It is what makes the install interview finite and
bundle-specific instead of asking every question every time, and it has no home anywhere
else. The installer **reads this file** rather than hardcoding a section list.

**Bundles do not list skills.** Getting the skills themselves onto a machine is the
platform's job — `/plugin marketplace add LiamKlyneker/skills` and `/plugin install`. The
catalog owns the inventory; this file owns the questions.

## Bundle is not plugin

Two separate namespaces, and they are only *sometimes* the same set. Never let a reader
assume otherwise:

| Bundle | Distributed as | Same set? |
|---|---|---|
| `prd-workflow` | the `prd-workflow` plugin | **No** — the bundle is the five loop skills, and the plugin also ships `manual-qa` and `triage`, which the `prd-qa` bundle asks for instead. It read **Yes, today** right up until `triage` moved in from `lk`; nothing about the bundle changed, the plugin simply grew past it |
| `ado-workflow` | the `ado-workflow` plugin | **No** — the bundle is the four `[SPEC]`-loop skills and the `spec-worker` agent, and the plugin also ships `manual-qa` and `triage`, which the `ado-qa` bundle asks for instead. It read **Yes, today** right up until those two were born in it; nothing about the bundle changed, the plugin simply grew past it — the same way `prd-workflow` did |
| `prd-qa` | two skills of the `prd-workflow` plugin | **No** — the bundle is `manual-qa` + `triage`, two of the seven skills `prd-workflow` ships. Installing the plugin is not adopting the bundle, and the bundle does not want the plugin's other five. `prd-workflow` therefore maps to **two** bundles, which is exactly why the plugin's name being shared with one of them proves nothing |
| `ado-qa` | two skills of the `ado-workflow` plugin | **No** — the bundle is `manual-qa` + `triage`, two of the six skills `ado-workflow` ships, and it asks a section the loop bundle does not. Same shape as `prd-qa`, one tracker over |
| `grill` | two skills of the `lk` plugin | **No** — the bundle is `grill` + `deep-grill`, the two `lk` skills that read a project fact. The plugin ships five, and the other three ask for nothing |
| `figma-tools` | the `figma-tools` plugin | Yes, today |

`figma-tools` was called `figma` here until the plugin took that name and then had to give
it up: `figma@claude-plugins-official` already owns it, and the clash stops the plugin
loading outright. The bundle followed the plugin rather than keeping a name that now points
at somebody else's integration. A bundle and a plugin sharing a name still does not make
them the same set; where the table says "yes" it is reporting today's lists, not a rule.

`grill`, `prd-qa` and `ado-qa` are the standing proof that the two namespaces come apart,
and they now prove it from both directions and on both trackers. `grill` is a **pair of
skills inside `lk`** — a bundle smaller than the plugin that carries it. `prd-qa` and
`ado-qa` are **two skills inside a plugin that is also named after a different bundle**, so
`prd-workflow` and `ado-workflow` each answer to two bundles at once while being neither of
them. The only row left saying "yes" is `figma-tools`, and it says *today*. A bundle is a
set of adapter questions; a plugin is a unit of distribution. Nothing requires them to line
up, and here they demonstrably do not.

## Schema

One `##` section per bundle, named by its slug. Every field is a bold-labelled list
item, exactly these keys, in this order:

| Field | Meaning |
|---|---|
| **Status** | `ready` — bootstrappable. `pending #N` — refuse and point at the issue. |
| **Adapter sections** | `##` headings of `<repo-root>/.claude/project/adapter.md` this bundle needs filled. Empty means the bundle is adapter-free — no adapter, no interview, no questions. |
| **Gates** | Gate templates to offer, and where they land. Optional by definition — a gate exists only where a project has a silent-failure class. |

Section headings are matched by **prefix**, so `## Sources of truth` matches the
template's `## Sources of truth (recon + hard gates)`. A project whose adapter spells the
parenthetical differently still matches, which is the point — the heading's tail is prose
and free to change.

## Which tracker a bundle implies

The adapter template is **tracker-parametric**: `## Repo` and `## One-time repo
preconditions` each carry a `### GitHub` and an `### Azure DevOps` sub-section, and a
filled adapter keeps exactly one of the two. Which one is not a question worth asking
twice, because the bundle already answers it:

| Bundle | Implies `Tracker:` |
|---|---|
| `prd-workflow`, `prd-qa` | `github` |
| `ado-workflow`, `ado-qa` | `azure-devops` |
| `figma-tools` | neither — adapter-free, so there is no `Tracker:` line to write |
| `grill` | neither — a grill is tracker-agnostic recon that runs *before* `to-prd` or `to-spec`, so there is nothing tracker-shaped to write |

The installer reads this table rather than hardcoding the mapping, exactly as it reads
**Adapter sections** rather than hardcoding a section list. A project runs one tracker, so
a bundle whose implied tracker contradicts an **existing** adapter's `Tracker:` line is a
conflict to surface and stop on — never something to resolve by rewriting the line or
deleting a section. See the `install-skills` skill's own `SKILL.md`, step 3a, for the one
narrow case in which a tracker sub-section is deleted at all.

**"Neither" is not a licence to pick one.** `figma-tools` never reaches the question — it is
adapter-free, so no adapter is created. `grill` does reach it, being the one bundle that
needs a section but no tracker: it writes no `Tracker:` line and deletes neither `###`
sub-section, leaving the choice to whichever tracker-bound bundle is installed next. That
later install finds an adapter with no `Tracker:` line and **both** sub-sections still
present, which is the gap-fill case in step 3a and not a contradiction to stop on.

---

## `prd-workflow`

The PRD → issues → implementation loop. The reason the adapter exists.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section, so a partial adoption can drop questions:

| Section | Wanted by |
|---|---|
| `## Repo` | all five workflow skills — including the **title prefixes**, which every one of them either writes or filters on |
| `## Commands`, `## Verify ladder` | `to-issues`, `work-on-prd`, `work-on-issue` |
| `## App facts` | `work-on-prd` (pasted into every worker prompt) |
| `## Project gates` | `to-prd`, `to-issues` |
| `## Repo discipline` | `work-on-prd`, `work-on-issue` |
| `## One-time repo preconditions` | `work-on-prd` (the `Closes #N` setting) |

Every row names a skill this plugin ships. `## Sources of truth` used to be here too, for
`deep-grill` alone — it moved to the `grill` bundle, which is where a project that runs the
interviews answers for it.

## `ado-workflow`

The same loop against an Azure DevOps board: `[SPEC]` → `[TASK]`s → implementation, run by
`work-on-spec`. `prd-workflow`'s sibling, and it needs almost the same facts.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## App facts`, `## Verify ladder`, `## Project gates`, `## Repo discipline`, `## One-time repo preconditions`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | all four workflow skills — and it carries far more here than on GitHub, though the gap has narrowed: both trackers now register **title prefixes** there. The `### Azure DevOps` sub-section holds the org, the **two** projects (work items and repo, routinely different), the team, the repository, the work-item type, the three board states, the title prefixes and the branch pattern. None of it is discoverable from the tree, which is why every one of them is a question |
| `## Commands`, `## Verify ladder` | `to-spec-tasks` (every `[TASK]` names its own verify command), `work-on-spec`, and `spec-worker` through the adapter `work-on-spec` pastes into each worker prompt |
| `## App facts` | `work-on-spec` (pasted into every worker prompt) |
| `## Project gates` | `to-spec`, `to-spec-tasks` |
| `## Repo discipline` | `work-on-spec`, and `spec-worker` for the scoped `CONTEXT.md` rule |
| `## One-time repo preconditions` | all four — its `### Azure DevOps` sub-section names the MCP server key and the exact spelling of the board states, and both fail *silently* when wrong: a server under the wrong key reads as unconfigured, and a near-miss state name is a no-op rather than an error |

**This bundle's section list and `prd-workflow`'s are now the same set**, and neither asks
anything about QA. They used to differ by exactly one row, back when `work-on-spec` created
a per-run `[QA]` work item while `work-on-prd` committed a document to a path the adapter
named. **Neither loop does either any more**: both end a run by posting a tickable comment
on the parent artifact and marking it `needs-qa`, and the `[QA]` work item is retired. So
that row was removed from the template and from both lists rather than added to this one —
do not restore it to either. The shape of a QA artifact ships with the plugins —
`work-on-prd`'s `## Loop end` for GitHub, `work-on-spec`'s own `## Loop end` for ADO, plus
`plugins/ado-workflow/skills/references/findings-item.md` for the work item a failed ADO
pass writes into — and none of it is something an installer can ask a human for; the
argument is ADR 0006, carried to this tracker by ADR 0011.

**The `manual-qa` and `triage` skills this plugin also ships are not in this bundle.** They
are `ado-qa`, below, and they want a section no loop skill on the list above reads.

The row that looks like a GitHub leftover is real. `## One-time repo preconditions` survives
even though the ADO side has no analogue of GitHub's un-queryable auto-close setting (the pull request's completion options transition
the linked work items instead): what is left there is the MCP server and the board-state
spelling, both human-checked once.

## `prd-qa`

The QA loop that runs against a PRD branch before merge, in both halves: `manual-qa`
drives the run's QA comment step by step and captures what fails as findings on the PR,
and `triage` promotes the survivors into executable issues.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Verify ladder`, `## Sources of truth`, `## Repo discipline`
- **Gates:** none

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | both — `manual-qa` for which tracker holds the QA comment and which repo's PR takes the findings; `triage` for where it files, the `Related repos` it routes across the contract boundary, and the **title prefixes** it files bugs under |
| `## Verify ladder` | both — `manual-qa` reads the **L5** rung, which is what makes a step that cannot name a config dir, a command and an expected result a finding rather than a shrug; `triage` because every filed issue names its verify step |
| `## Sources of truth` | both — the project explorer agent, which `manual-qa` spawns for on-demand elaboration of a step and `triage` for root-causing, plus the contract-boundary one for `triage`'s cross-repo findings |
| `## Repo discipline` | `triage` — scoped `CONTEXT.md` loading |

The `[FINDING]` marker the two skills hand off on is deliberately **not** an adapter
question. It is a parse contract hardcoded in both, not a scanning convention: a project
that could edit it would get a `triage` that silently finds zero findings and reports
a clean PR.

**Pairs with `prd-workflow`, doesn't replace it.** `triage` files issues shaped like
`to-issues` children, so `work-on-prd` / `work-on-issue` execute them with no new
machinery. Adopting `prd-qa` alone is legal but leaves nothing downstream to run the
issues it files — say so rather than silently bootstrapping both.

The other direction is tighter still: `manual-qa` drives the QA **comment** a
`work-on-prd` run posted, so adopting `prd-qa` without the loop that writes one leaves it
with nothing to drive — its ad-hoc capture path still works, but that is the smaller half.

Note the asymmetry that creates: the two bundles are separate adoptions, but they arrive
in **one plugin**. Installing `prd-workflow` puts `manual-qa` and `triage` on the
machine whether or not `prd-qa` was adopted — a skill being present is not the same as its
adapter questions having been answered, and it is the adapter that decides whether it can
run.

`triage` degrades rather than breaks where the adapter says "None": no related repo
means every finding is a this-repo finding, and no contract-boundary explorer agent
means a cross-boundary root cause gets filed locally and flagged as unmodelled.

## `ado-qa`

`prd-qa`'s sibling, one tracker over: the QA pass that runs against a `[SPEC]`'s branch
before merge. `manual-qa` drives the run's QA comment on the `[SPEC]` step by step and
appends what fails to that run's `[FINDINGS]` work item; `triage` reads that one item,
promotes the survivors into `[BUG]` work items under the same parent, and closes it.

- **Status:** ready
- **Adapter sections:** `## Repo`, `## Commands`, `## Verify ladder`, `## Sources of truth`
- **Gates:** none

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Repo` | both — its `### Azure DevOps` sub-section gives the org, the **work-item project**, the work-item type and the board states; `manual-qa` also reads the `Tracker:` line and **aborts** unless it says `azure-devops`, and `triage` also reads *Related repos* for the contract boundary. The **title prefixes** matter more here than anywhere else on this page: see below |
| `## Commands` | `triage` — every `[BUG]` it files names the exact verify commands a cold worker will run, and this is the row `prd-qa` does not have |
| `## Verify ladder` | both — `manual-qa` reads the **L5** rung, which is what makes a step that cannot name an entry point, a command and an expected result a finding rather than a shrug; `triage` because every filed `[BUG]` names its verify step |
| `## Sources of truth` | both — the project explorer agent, which `manual-qa` spawns for on-demand elaboration of a step and `triage` for root-causing, plus the contract-boundary one for `triage`'s cross-repo findings |

That list is **derived from the two skills' own `## Project facts` tables**, not copied from
`prd-qa`. It differs from `prd-qa`'s in both directions: it **gains `## Commands`**, because
an ADO `[BUG]` body spells the verify commands out where the GitHub one points at the ladder;
and it **drops `## Repo discipline`**, because ADO `triage` reaches a scoped `CONTEXT.md`
through the `scoped-context` skill rather than through an adapter section.

**Why this is its own bundle rather than rows on `ado-workflow`.** `## Sources of truth` is
not on that bundle's list — no `[SPEC]`-loop skill reads it — and both skills here do. Folding
them in would interview every ADO *loop* adopter about explorer agents nothing they installed
reads, and a bundle-specific interview is the entire reason this file exists. It is the same
asymmetry that produced `prd-qa` on the GitHub side and `grill` in `lk`, so this follows the
convention rather than inventing one.

The `[FINDING]` marker the two skills hand off on is deliberately **not** an adapter question,
for `prd-qa`'s reason exactly: a parse contract hardcoded in both, and a project free to edit
it would get a `triage` that reads the findings item, matches nothing, and reports a clean
pass.

**The title prefixes are load-bearing on this tracker**, and that makes the `## Repo` answer
higher-stakes than its GitHub counterpart. `[SPEC]`, `[TASK]`, `[FINDINGS]` and `[BUG]` are all
the same work-item type under one parent, so the prefix is the only thing telling them apart —
a wrong answer here returns an empty set rather than an error. Read it back to the human.

**Pairs with `ado-workflow`, doesn't replace it.** `triage` files `[BUG]`s shaped like
`to-spec-tasks`' `[TASK]`s, so a later `work-on-spec` run executes one with no new machinery
once a human retitles it — and `manual-qa` drives the QA **comment** a `work-on-spec` run
posted, so adopting `ado-qa` without the loop that writes one leaves it with nothing to drive.
The asymmetry `prd-qa` notes holds here too: the two bundles are separate adoptions but arrive
in **one plugin**, so installing `ado-workflow` puts both skills on the machine whether or not
`ado-qa` was adopted. A skill being present is not the same as its adapter questions having
been answered.

`triage` degrades rather than breaks where the adapter says "None": no related repo means
every finding is a this-repo finding, and no contract-boundary explorer agent means a
cross-boundary root cause gets filed locally and flagged as unmodelled.

## `grill`

The two interviews that run **before** either loop: `grill` inline on one thread, and
`deep-grill` with recon subagents and hard gates for anything that crosses a boundary.

- **Status:** ready
- **Adapter sections:** `## Sources of truth`
- **Gates:** none by default — `install/gates/gate.template.md` on request only

Which skill drives which section:

| Section | Wanted by |
|---|---|
| `## Sources of truth` | `deep-grill` only — the project explorer agent, the contract-boundary one, and the access-policy source its Data & Access Manifest gate reads before the interview starts |

**One section, and one skill wants it.** `grill` reads **nothing** from the adapter — it is
the lightweight inline interview and explores on the thread it is invoked from — so the whole
of this bundle's interview is `deep-grill`'s three sources of truth. Ask against the table,
not against the `lk` plugin's inventory.

That asymmetry is why this bundle exists at all. `## Sources of truth` used to ride along on
`prd-workflow` and `ado-workflow`, which meant every adopter of a loop was interviewed for
three agent names belonging to a skill they may never have installed. The section now lives
where the skill that reads it does.

`deep-grill` also reads the adapter's `## Project gates` registry and runs every gate whose
trigger the plan matches — but that is not an interview question here. A project with no
extra gates needs no such section, and a project that accepts the gate template gains
`## Project gates` as the place its gate is registered, by the same route `figma-tools`
reaches an adapter it otherwise does not need.

Adopting this bundle alone is entirely normal: a grill is useful with no loop downstream, and
its output is a conversation, not a tracker artifact. That is also why it implies neither
tracker — see *Which tracker a bundle implies* above.

## `figma-tools`

Figma → spec, and the UI-primitive skills that consume the same reference.

- **Status:** ready
- **Adapter sections:** —
- **Gates:** `install/gates/ui-manifests.template.md` → `.claude/project/ui-manifests.md`, optional

**Adapter-free.** These skills read global reference only, so a repo can run them with
no `.claude/project/` at all — the installer skips the interview entirely and asks
nothing. The optional `ui-manifests.md` gate is the exception: a project that wants its
own primitive homes, real token files and stack-specific traps named registers one, the
same way as any other gate. Accepting it is the one case where an adapter-free bundle
still ends up with an adapter, because the `## Project gates` registry lives there.

`tokens-init` and `figma-component` were the two deprecated top-level skills this bundle
superseded. They were part of no bundle and no plugin, and ADR
[0010](../docs/adr/0010-one-distribution-one-dev-mode.md) deleted them; #14 tracks what
the UI Primitive and Token manifests still need.
