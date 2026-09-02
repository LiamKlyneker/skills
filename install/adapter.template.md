# Project Adapter — TEMPLATE

Single home for every project-specific fact the skills need. Workflow skills (`work-on-prd`, `to-issues`, `next-prd-issue`, `work-on-issue`) reference this file and never hardcode these values, and so does every other skill that needs a project fact — each reading only the sections its own bundle declares, never the whole file. Porting the workflow to another repo = install the plugin + fill in this file, nothing else.

> **This is a template.** Copy it to `<repo-root>/.claude/project/adapter.md` and fill every `<placeholder>` with your project's real values before running `work-on-prd`. Delete rows that don't apply; add rows the workflow needs. Nothing else in the skills should mention a tool, path, or command by name — if it does, lift it into this file.

> **Pick your tracker first.** Two sections here — `## Repo` and `## One-time repo preconditions` — carry a `### GitHub` and an `### Azure DevOps` sub-section. Fill the one that matches your tracker and **delete the other**; a filled adapter that keeps both gives every skill two answers to the same question. Everything in between is tracker-agnostic and is never forked.

**Canonical source:** skill *logic* is canonical in **`LiamKlyneker/skills`** and reaches a project as an installed plugin from marketplace `liamklyneker`. There is nothing to back-port — an installed copy is a regenerated cache keyed by the plugin's version, never a place to edit. Project *facts* live in `<repo-root>/.claude/project/`, which is the one directory skills resolve from the repo root, and they resolve it against the project the session is running in regardless of how the skill was delivered. A project never owns a `_shared/`: `../_shared/…` from any skill can therefore only ever mean the canonical global-reference files in the skills repo.

## Repo

- Tracker: `<github|azure-devops>` — **an absent `Tracker:` line means `github`.** Every adapter written before this line existed is a GitHub project, so a filled adapter that never gained the line still reads unambiguously, and needs no edit.
- Default branch: `<main>`
- Related repos (cross-repo issues, API contracts): `<owner>/<other-repo>` — or "None"

Then exactly one of the two sub-sections below, matching the `Tracker:` line. Delete the other.

### GitHub

Tracker `github`, and what an adapter carrying no `Tracker:` line falls back to.

- Issue tracker / PRs: `<owner>/<repo>` (GitHub, via `gh`)
- PRs must target the default branch — `Closes` keywords only fire against it.
- Title prefixes: `[PRD]` · `[TASK]` · `[BUG]` · `[FINDINGS]` — literal, at the start of the title. A **human scanning convention, not a filter**: `[PRD]` is a parent, `[TASK]` a planned child, `[BUG]` a triaged finding, `[FINDINGS]` a disposable per-run issue `manual-qa` writes findings to. A PRD's children are its **native sub-issues**, so nothing keys on a title — `[FINDINGS]` issues are free-standing and never linked as one. There is no `[QA]` prefix on GitHub — `work-on-prd` only labels the PRD `needs-qa` and prints the `manual-qa` invocation; a human runs that on demand. A project that also runs `figma-tools` gains one more, `[DESIGN-SPEC]`, written by that bundle alone and filed against the *design-spec target* row below. Change them here if this repo uses different ones; never in a skill.
- Triage labels: `needs-triage` → `ready-to-start` → `state:in-progress` → `state:done-on-branch`. All four must exist in the repo. The vocabulary is normative in `work-on-prd`'s `## Label vocabulary`; it is restated here so a cold session holding only this adapter knows which tracker and which labels to use without asking. Rename them if this repo already uses different words — keep the four roles.

Two rows that decide what a run's branch and pull request look like **to the team**. Both are **optional and independent**, and both are read by `prd-workflow` alone. An adapter that declares neither behaves exactly as it did before these rows existed — so leaving either out is a finished answer, not a gap, and nothing warns about an absent row:

- Branch pattern *(optional)*: `<gh-branch-pattern>` — the branch a run creates, written in this file's own placeholder notation. The only tokens anything substitutes are `<n>` (the PRD's issue number) and `<slug>` (its title, slugged, with the leading `[…]` group stripped), and **every placeholder is optional** — a pattern that uses neither, like `release`, is legal. E.g. `feat/<slug>`. **Absent → `prd/<n>-<slug>`.** Purely cosmetic: nothing resolves a run *by* this name, so changing it mid-flight costs nothing.
- PR template *(optional)*: `<path-to-pr-template>` — this project's pull-request template, as a **repo-relative path to one file** (`.github/pull_request_template.md`, or a single file inside a `.github/PULL_REQUEST_TEMPLATE/` directory). **A path is strongly preferred**, because the loop then reads the team's live file and the PR body keeps tracking it as the team edits it. Only when the project has no template file anywhere does this row instead carry a **content snapshot**: write the literal word `snapshot` as the value and the template body fenced beneath the row. `doctor` reports a snapshot as possibly stale on every run, deliberately — nothing can tell it when the real template moved on. **Absent → the loop's own PR skeleton.** The loop takes the template's *structure* only; draft state, target branch and its own bookkeeping stay the orchestrator's.

Two filing rows only `figma-tools` reads. A project that never runs it deletes both; a project that does fills both, because they answer different questions:

- Design-spec target: `<owner>/<repo>` — where a `figma-to-spec` page spec files, as a `[DESIGN-SPEC]` issue. When Phase 0 was given a scope issue, the spec is linked as that issue's **native sub-issue** — the link is what makes it a child, so its body carries no `## Parent` section.
- DS-gap backlog: `<owner>/<design-system-repo>` — where an **escalated** design-system gap files, one issue per gap. **Routinely a different repo from the row above**, because a gap belongs to the design system rather than to the code being specced. Where the two genuinely are the same repo, write the same value twice — never leave one implied.

### Azure DevOps

Tracker `azure-devops`. Work items are reached through the Azure DevOps MCP server (`mcp__ado__*`). None of the facts below are discoverable from the repo, which is why every one of them is listed here rather than left for a skill to infer — a skill that hardcodes any of them is a bug.

- Organisation: `<ado-org>` — the org segment of the `dev.azure.com` URL
- **Work-item project**: `<ado-workitem-project>` — the ADO project the `[SPEC]` / `[TASK]` / `[FINDINGS]` / `[BUG]` work items live in, and where `ado-workflow:triage` posts its end-of-pass comment on the parent
- **Repo project**: `<ado-repo-project>` — the ADO project the git repo lives in

  These are two separate fields on purpose, and they frequently differ. Querying the wrong one returns an empty result rather than an error, so the failure looks like a spec with no tasks or a repo that does not exist. Where the two genuinely are the same project, write the same value twice — never leave one implied.
- Team: `<ado-team>` — the team whose board the states below belong to. Boards are per-team, so the state names only mean anything alongside it.
- Repository: `<ado-repository>` — the git repository's name inside the **repo project**
- Work-item type: `<ado-workitem-type>` — the **one** type `[SPEC]`, `[TASK]`, `[FINDINGS]` and `[BUG]` items are all created as — a **task-level** type, e.g. `Task`, not a requirement-level one (`User Story`, `Product Backlog Item`), which is what the parent above these four is. One type for all four is deliberate; the *Title prefixes* row below says why, and why the prefix rather than the type is what tells them apart. Note that a `Task` carries no `AcceptanceCriteria` field, so a `[TASK]`'s acceptance criteria live in its description.
- Board states — `System.State` is a per-process string, not a boolean, and the names differ between ADO processes, so name this board's three:
  - Pickable (open, unclaimed): `<ado-state-pickable>`
  - Claimed (a run is working it): `<ado-state-claimed>`
  - Committed, awaiting merge: `<ado-state-committed>` — where a `[TASK]` sits once its commit is on the branch but the PR has not completed. Work items close on PR completion, not on commit, so this state is **not** terminal and an orchestrated run must not read it as done.

  Every other state on the board counts as terminal. Where a board names none of these, ADO's stock terminal states are `Closed`, `Done`, `Resolved` and `Completed`.
- Title prefixes: `[SPEC]` · `[TASK]` · `[FINDINGS]` · `[BUG]` — literal, at the start of the title, and what the skills filter a parent's children on. `[SPEC]` is the spec, `[TASK]` a unit of work the loop will pick up, `[FINDINGS]` a run's QA pass, `[BUG]` work filed by hand outside the loop. There is no `[QA]` prefix.

  **`[TASK]` is the only prefix any skill writes onto new work.** `ado-workflow:triage` files a QA finding it is fixing as a `[TASK]`, so the next `work-on-spec` run picks it up with no promotion step; a finding that is *not* being fixed becomes a human comment on the parent instead of a work item. `[BUG]` therefore stays a purely human prefix — registered so a hand-filed bug is recognisable on the board, and dropped by every eligibility filter until someone retitles it.

  **On Azure DevOps the prefix is load-bearing. On GitHub it is decorative — do not carry the GitHub habit across.** The `### GitHub` row above calls prefixes a human scanning convention that nothing keys on, because a PRD's children are native sub-issues. There are no sub-issues here: all four kinds are the **same work-item type**, sitting as siblings under the same parent, so the prefix is the *only* thing distinguishing a `[BUG]` from a `[TASK]`. Mistype one and the item is not merely mislabelled — it is invisible to every skill that walks the parent's children, and it looks like a spec with one slice fewer than it has. The mistype now cuts both ways: a `[TASK]` prefix on something nobody agreed to work schedules it into the next run.

  Why one type rather than the obvious types: a Task parented to a Task drops the parent off the taskboard and disables reordering board-wide, and where the project sets `bugsBehavior: 1` (bugs managed *with* requirements) a Bug-type item is requirement-level and renders as its own sibling swimlane instead of a child. One Task-type child per kind, distinguished by prefix, is what survives both.

  A project that also runs `figma-tools` gains one more, `[DESIGN-SPEC]`, written by that bundle alone and filed against the *design-spec target* row below.

  Change the words here if this org uses different ones; never in a skill.
- Branch pattern: `<ado-branch-pattern>` — e.g. `spec/<id>-<slug>`, where `<id>` is the `[SPEC]` work-item id

One row that decides what a run's pull request looks like **to the team**. It is **optional**,
and read by `ado-workflow` alone. An adapter that omits it behaves exactly as it did before the
row existed — so leaving it out is a finished answer, not a gap, and nothing warns about an
absent row:

- PR template *(optional)*: `<path-to-pr-template>` — this project's pull-request template, as a **repo-relative path to one file** (`.azuredevops/pull_request_template.md`, the `.vsts/` and `docs/` variants Azure Repos also honours, or a single file inside a `.azuredevops/pull_request_template/` directory). **A path is strongly preferred**, because the loop then reads the team's live file and the PR body keeps tracking it as the team edits it. A `../` path is legal and names the case where several sibling repos in one working folder share one template — the file is then outside the repo, so it exists only where that folder does, and an adapter carrying such a path is meaningful on the machines that have it and nowhere else. Only when the project has no template file anywhere does this row instead carry a **content snapshot**: write the literal word `snapshot` as the value and the template body fenced beneath the row. `doctor` reports a snapshot as possibly stale on every run, deliberately — nothing can tell it when the real template moved on. **Absent → the loop's own PR skeleton.** The loop takes the template's *structure* only; draft state, target branch and its own bookkeeping stay the orchestrator's.

Two filing rows only `figma-tools` reads. A project that never runs it deletes both; a project that does fills both, because they answer different questions:

- Design-spec target: `<ado-designspec-project>` — the ADO project a `figma-to-spec` page spec files into, as a `[DESIGN-SPEC]` work item. When Phase 0 was given a scope work item, the spec is filed as its **child**.
- DS-gap backlog: `<ado-ds-backlog-project>` — the ADO project whose backlog an **escalated** design-system gap files into, one item per gap. **Routinely a different project from the row above**, because a gap belongs to the design system rather than to the code being specced. Where the two genuinely are the same project, write the same value twice — never leave one implied.

## Commands

Every command a worker or the orchestrator runs. Keep the **Purpose** column stable (the skills refer to L2/L3 by name); swap the **Command** column for your stack.

| Purpose | Command |
|---|---|
| Build | `<build command>` |
| Test — **verify L2 floor** | `<test command>` |
| Boot the app (visual loop) | `<run/boot command>` |
| App screenshot | `<screenshot command>` |
| Install deps | `<dependency install command>` |

## App facts

- One or two lines of stack facts every worker should know before touching code (language + version, framework, the one file to edit vs. never touch, strict-mode flags, etc.).
- e.g. `<language + version> · <framework> · <the generated/config file to edit, never its raw output>`

## Design system

Read by `figma-tools` and by nothing else — delete the whole section in a project that never
runs it. It carries the facts that decide whether a value drawn in Figma **exists** in this
project's design system, and in what form an app writes it. None of it is inferable from the
tree at run time, which is why every line is here rather than left to a skill.

- Repo role: `<consumer|library>` — **an absent `Repo role:` row means `consumer`.** Which side of the design system this repo sits on: a `consumer` renders the design system and files gaps against it; a `library` **is** the design system, so a spec written here changes the thing everyone else resolves against. Every adapter written before this row existed belongs to a consumer repo, so an adapter that never gained the row still reads unambiguously and needs no edit. The role is an **intent, not an inference** — a repo that happens to contain a `components/` directory is not thereby a library — so it is always asked and never guessed from the tree.
- Design-system source: `<where the design system itself lives — repo path, workspace package, or published package + version>` — the thing a catalog is generated *from* and a gap is eventually built *in*. Or "None — `<how the design system is consumed instead>`". In a `library` repo this points at this repo itself.
- Catalog: `./<catalog>.md` — this project's design-system catalog: the existence source `figma-to-spec` resolves every component, token, type utility and icon against. **This row is the only place the catalog is ever named**, exactly as `## Project gates` is the only place a gate is named — skills follow the pointer and never a filename. A path relative to this file, or anywhere in the repo. Its required shape is the `figma-to-spec` skill's `references/catalog-contract.md`; a catalog that fails that contract stops the run loudly rather than degrading.
- Fingerprint command: `<the command that recomputes the catalog's stamp>` — the recipe behind the catalog's line-1 `fingerprint:` value. The catalog carries the *value*; this row carries the *recipe*, so the two never drift into two definitions. Hash **content only** — anything path-dependent differs between two checkouts of the same commit and turns every check into a false warning. Or "None — staleness unchecked", which is a real answer: the staleness check is soft and never fails a run.
- Class prefixes — **three separate facts, and they are not interchangeable.** A design system routinely prefixes its build internally, its CSS custom properties differently, and emits something else again to consumers; collapsing them is how a spec recommends a class the app cannot write:
  - Tailwind class prefix: `<prefix, or "None">` — what the Tailwind theme prefixes emitted utilities with, if anything.
  - CSS variable prefix: `<prefix, or "None">` — what the design tokens' custom properties are named with.
  - Consumer-facing emission form: `<the form an app actually writes, spelled out with one example>` — the form the catalog is written in and the form a spec must recommend. Where it differs from the library-internal form, say which is which and say it here rather than in a skill.
- Icon resolution ladder: `<source 1 → source 2 → … → what happens when none matches>` — the icon sources this project tries, **in order**. Multi-source by default: an in-house set plus a third-party library used by consuming apps is the common shape, and where a source may be used (app layer only, design system only, both) is part of the answer. The catalog says what each source *contains*; this row says which order they are tried in and what a no-match becomes.
- Usage-rules source *(optional)*: `<the best-practices doc or skill a page spec cites by stable name>` — the HOW, kept separate from the catalog's WHAT. A page spec **cites** it and never duplicates it, so a citation stands even where the source is not loaded. **Absent is not an error**: leave the row out and a spec cites nothing. Nothing warns about it.
- Downstream implementer *(optional)*: `<the skill or workflow that implements a filed spec>` — who picks a `[DESIGN-SPEC]` up. **Absent means a human.** Also not an error, also never warned about.

Four rows about **provisional decisions** — what happens when the *inputs* to a spec are
incomplete rather than the run being invalid. A design file that has not defined a variable yet,
a token that does not exist on this side, a Figma-vs-code disagreement: none of those makes a run
unable to produce anything valid, and blocking on them is what stops anyone running the skill a
second time. Instead an eligible gap **ships with a value chosen now**, carrying one stable id
across four surfaces — the marker comment at the point of use, the tracker item, the spec's
`## Provisional decisions` section, and the run record — so `grep` on the marker gives a live
inventory of every place the implementation is ahead of the design, and a later run reads those
markers rather than re-asking about them.

**All four default, so an adapter that never gains them still reads unambiguously and needs no
edit** — the same doctrine as `Repo role:` above. Only `figma-component-to-spec` reads them today,
so `install-skills` asks for them only in a `library` repo; they are **not library-only in
principle** — a consumer repo has exactly the same problem — which is why they sit here rather
than in the library block below:

- Gap policy *(optional)*: `<which kinds of gap may ship provisionally, and which must stop and ask>` — the default disposition, **per kind**. Absent means the skill's own stated default: a gap that lands in the **token layer** or in the **Figma library** may ship provisionally, because a colour or a dimension is cheap and reversible — pick wrong and one line changes later. A gap that changes the **component's API** — a new variant axis, a new value on an axis, a props signature — **always stops and asks a human**, because consumers write against it and it cannot be taken back without a breaking change. Widen or narrow that here; the point of the row is that the policy is per kind rather than one global switch.
- Provisional marker *(optional)*: `<the literal comment syntax, per file type>` — what the marker at the point of use looks like, so it is **greppable and lintable** by this project's own tooling. Absent means `PROVISIONAL(<id>): <what should replace it>` inside whatever comment syntax the file already uses. Writing the lint that enforces it is this project's job, not the skill's; this row is what makes writing one possible.
- Gap tracker *(optional)*: `<where a provisional decision files, and under what prefix>` — the tracker and prefix a provisional's ticket is opened under, which is frequently **not** where the spec itself files: the spec is work in this repo, the gap it defers is often the design system's or the designer's. Absent means this repo's own `## Repo` rows — the same target the spec uses.
- Provisional expiry *(optional)*: `<how long before a provisional is surfaced as overdue>` — so something provisional since eight months ago gets raised rather than quietly becoming permanent. Absent means **no expiry is surfaced**, which is a real answer and nothing warns about it; the decision is still recorded and still findable, it simply never ages into a complaint.

Three rows only a **library** repo fills — the conventions of the design system itself, which
decide how a spec written *against this repo* is allowed to phrase a change. A repo whose
`Repo role:` is `consumer` (including one with no role row at all) **deletes these three**, the
same way a project that never runs `figma-tools` deletes the two filing rows in `## Repo`. This
applies to the three below and to nothing above it — the four provisional rows are not part of
this block. None of the three is inferable from the tree at run time, and a wrong answer here
does not error — it produces a spec whose edits land in the wrong file:

- Variant mechanism: `<source 1 → source 2 → … → what happens when none matches>` — how this
  library declares a component's variant axes and their values, **in the order a reader tries
  them**, plus any repo-specific trap. A **ladder, not a value**, exactly like the icon
  resolution ladder above: the primary mechanism first, the fallback path next, and the shapes
  that *look* like the mechanism but are the implementation of it last. E.g. "`cva()` in the
  component file → no `cva()` found → prop unions in the types file; conditional `className`
  branches are the implementation, never the declaration · trap: a runtime deprecated-alias
  map living outside the `cva` object, so an axis can accept values the `cva` call never
  lists".
- Token pipeline: `<the generator that consumes the token source, and the file it consumes — or "None — <how tokens are edited instead>">` — **this row decides how literal a spec's token delta may be.** A library with a generator that consumes a token source (JSON, YAML, a TS module) gets specs that state the **literal source edit**, because the emitted CSS and utilities are build output nobody hand-edits. A library with no generator gets a **coordinated file-edit list** instead — every file that must change together, named — because there is no single source whose edit propagates. Say which, and name the file either way.
- Story convention: `<where stories live, and how their argTypes are declared>` — e.g.
  "`*.stories.tsx` beside the component · `argTypes` generated from the `cva` variants, so a
  new axis value appears in the story with no story edit" versus "`stories/` at the package
  root · `argTypes` hand-written per story, so a new axis value needs the story updated too".
  A spec that adds a variant value has to say whether a story edit is part of the change, and
  this row is the only thing that can tell it.

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: `<test command>` passes.
- **L3 — user-visible issues**: L2 + `<boot command>` boots the app + a screenshot as evidence (`<screenshot command>`).
- **L4** (agent-driven interaction): out of scope v1.
- **L5 — human**: once per orchestrated run, against the branch, before merge. The run **composes no QA pass**: it labels the PRD (GitHub) or tags the `[SPEC]` (Azure DevOps) `needs-qa` and prints the `manual-qa` invocation. A human runs that on demand; `manual-qa` composes the pass from what actually landed, drives it flow by flow, and — on a failure — files findings on a disposable per-run `[FINDINGS]` issue (GitHub) or work item (Azure DevOps), then `triage` promotes the survivors into cold-runnable work. Say here what exercising this app actually means — `<which entry point, which command, what to look for>` — because the run's steps are written against it and a worker only knows what this line says.

## Sources of truth (recon + hard gates)

- **Project explorer agent**: `<subagent_type>` — read-only, one feature/package area per spawn. Or "None — use `Explore`".
- **Contract-boundary explorer agent**: `<subagent_type>` — owns the related repo/service above (API handlers, contract spec, data layer). Or "None — no contract boundary".
- **Access-policy source**: `<migrations path, IaC definition, policy console, or MCP>` — how to read the live per-operation policies for a store, wherever this project enforces them (database row policies, document-store rules, IAM, or authorization middleware). Or "None — no user-scoped data layer".

## Project gates

Extra hard gates this project runs, on top of the ones the skills already carry. Each one is a **sibling of this file** in `.claude/project/`, and this table is the **only** place it is named — canonical skills never name a project gate directly, they read this registry and follow the pointer. That is what keeps a skill like `to-prd` generic instead of forked to hardcode one project's filename.

Gates live in their own files rather than inline here for a concrete reason: `work-on-prd` pastes the **full contents of this adapter** into every worker prompt, so anything parked here is a tax on every worker, most of whom don't need it.

| Gate | File | Runs when |
|---|---|---|
| `<gate name>` | `./<gate>.md` | `<the trigger — the condition under which a plan must run it, and when it may be skipped>` |

Or "None — no gates beyond the ones the skills carry."

A project-flavored `ui-manifests.md` (concrete primitive homes, real token files, this stack's traps and test vehicle) is registered here the same way; the row schema itself stays canonical in `_shared/ui-manifests.md`.

## Repo discipline

- **CONTEXT.md**: read the scoped `CONTEXT.md` before touching files in any directory (see the `scoped-context` skill). Update it only if documented architecture changes.
- `<any house rules: export order, no barrel files, where generated code lives, etc.>`
- Where skills come from: `<installed plugin + scope>`. The skill files are not this project's to edit — a plugin cache is regenerated on install. Project facts and gates live in `.claude/project/` instead, which is real and committed.

## One-time repo preconditions (human)

Tracker-specific, and each one checked once by a human because none of it is
API-queryable. Keep the sub-section matching this adapter's `Tracker:` line and delete
the other, exactly as in `## Repo`.

### GitHub

- GitHub Settings → General → "Auto-close issues with merged linked pull requests" must be **on** (not API-queryable — check in the web UI once). If off, `Closes #N` silently does nothing.
- The `needs-triage` label must exist in the repo — `to-prd` applies it on CREATE.
- The `needs-qa` label must exist in the repo — `work-on-prd` applies it to the PRD at loop end and cannot create it.

### Azure DevOps

- The Azure DevOps MCP server (`mcp__ado__*`) must be configured and authenticated against the organisation named in `## Repo`, in the config directory the session runs under. Without it every work-item read fails at the first call.
- The three board states named in `## Repo` must exist on the team's board, spelled exactly as written there — ADO state names are per-process strings and a near-miss is a silent no-op, not an error.

<!--
`install-skills doctor` flags any `<token>` that appears in **both** this template and a
filled adapter, on the theory that it was never filled in. A few angle-bracket tokens here
are notation rather than placeholders and are legitimately still there after filling —
list them below so the check stays quiet about them and loud about everything else.

`<n>`, `<id>` and `<slug>` are branch-pattern notation: a filled `Branch pattern:` value
is itself a pattern (`feat/<slug>` on GitHub, `spec/<id>-<slug>` on Azure DevOps), so all
three survive filling by design.

**Delete this whole comment when you fill your copy.** doctor reads the exemption list
from the template, never from your adapter, so a copy of it here does nothing except
carry `<token>` into your file — where the placeholder check then reports it, forever.

doctor:not-a-placeholder <repo-root> <n> <id> <slug>
-->

