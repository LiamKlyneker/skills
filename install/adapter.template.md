# Project Adapter — TEMPLATE

Single home for every project-specific fact the skills need. Workflow skills (`work-on-prd`, `to-issues`, `next-prd-issue`, `work-on-issue`) reference this file and never hardcode these values, and so does every other skill that needs a project fact — each reading only the sections its own bundle declares, never the whole file. Porting the workflow to another repo = install the plugin + fill in this file, nothing else.

> **This is a template.** Copy it to `<repo-root>/.claude/project/adapter.md` and fill every `<placeholder>` with your project's real values before running `work-on-prd`. Delete rows that don't apply; add rows the workflow needs. Nothing else in the skills should mention a tool, path, or command by name — if it does, lift it into this file.

> **Pick your tracker first.** Two sections here — `## Repo` and `## One-time repo preconditions` — carry a `### GitHub` and an `### Azure DevOps` sub-section. Fill the one that matches your tracker and **delete the other**; a filled adapter that keeps both gives every skill two answers to the same question. Everything in between is tracker-agnostic and is never forked.

**Canonical source:** skill *logic* is canonical in **`LiamKlyneker/skills`** and reaches a project either as an installed plugin from marketplace `liamklyneker` or as a symlink into a config's `skills/` directory. Either way there is nothing to back-port — an installed copy is a regenerated cache keyed by git commit, never a place to edit. Project *facts* live in `<repo-root>/.claude/project/`, which is the one directory skills resolve from the repo root, and they resolve it against the project the session is running in regardless of how the skill was delivered. A project never owns a `_shared/`: `../_shared/…` from any skill can therefore only ever mean the canonical global-reference files in the skills repo.

## Repo

- Tracker: `<github|azure-devops>` — **an absent `Tracker:` line means `github`.** Every adapter written before this line existed is a GitHub project, so a filled adapter that never gained the line still reads unambiguously, and needs no edit.
- Default branch: `<main>`
- Related repos (cross-repo issues, API contracts): `<owner>/<other-repo>` — or "None"

Then exactly one of the two sub-sections below, matching the `Tracker:` line. Delete the other.

### GitHub

Tracker `github`, and what an adapter carrying no `Tracker:` line falls back to.

- Issue tracker / PRs: `<owner>/<repo>` (GitHub, via `gh`)
- PRs must target the default branch — `Closes` keywords only fire against it.
- Title prefixes: `[PRD]` · `[TASK]` · `[BUG]` — literal, at the start of the title. A **human scanning convention, not a filter**: `[PRD]` is a parent, `[TASK]` a planned child, `[BUG]` a triaged finding. A PRD's children are its **native sub-issues**, so nothing keys on a title. There is no `[QA]` prefix on GitHub — `work-on-prd` posts the run's QA steps as a comment on the PRD and labels it `needs-qa`. Change them here if this repo uses different ones; never in a skill.
- Triage labels: `needs-triage` → `ready-to-start` → `state:in-progress` → `state:done-on-branch`. All four must exist in the repo. The vocabulary is normative in `work-on-prd`'s `## Label vocabulary`; it is restated here so a cold session holding only this adapter knows which tracker and which labels to use without asking. Rename them if this repo already uses different words — keep the four roles.

### Azure DevOps

Tracker `azure-devops`. Work items are reached through the Azure DevOps MCP server (`mcp__ado__*`). None of the facts below are discoverable from the repo, which is why every one of them is listed here rather than left for a skill to infer — a skill that hardcodes any of them is a bug.

- Organisation: `<ado-org>` — the org segment of the `dev.azure.com` URL
- **Work-item project**: `<ado-workitem-project>` — the ADO project the `[SPEC]` / `[TASK]` / `[QA]` work items live in
- **Repo project**: `<ado-repo-project>` — the ADO project the git repo lives in

  These are two separate fields on purpose, and they frequently differ. Querying the wrong one returns an empty result rather than an error, so the failure looks like a spec with no tasks or a repo that does not exist. Where the two genuinely are the same project, write the same value twice — never leave one implied.
- Team: `<ado-team>` — the team whose board the states below belong to. Boards are per-team, so the state names only mean anything alongside it.
- Repository: `<ado-repository>` — the git repository's name inside the **repo project**
- Work-item type: `<ado-workitem-type>` — the type `[SPEC]`, `[TASK]` and `[QA]` items are created as, e.g. `Product Backlog Item`, `User Story`, `Task`
- Board states — `System.State` is a per-process string, not a boolean, and the names differ between ADO processes, so name this board's three:
  - Pickable (open, unclaimed): `<ado-state-pickable>`
  - Claimed (a run is working it): `<ado-state-claimed>`
  - Committed, awaiting merge: `<ado-state-committed>` — where a `[TASK]` sits once its commit is on the branch but the PR has not completed. Work items close on PR completion, not on commit, so this state is **not** terminal and an orchestrated run must not read it as done.

  Every other state on the board counts as terminal. Where a board names none of these, ADO's stock terminal states are `Closed`, `Done`, `Resolved` and `Completed`.
- Title prefixes: `[SPEC]` · `[TASK]` · `[QA]` — literal, at the start of the title, and what the skills filter a parent's children on. Change them here if this org uses different ones; never in a skill.
- Branch pattern: `<ado-branch-pattern>` — e.g. `spec/<id>-<slug>`, where `<id>` is the `[SPEC]` work-item id

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

## Verify ladder

- **L2 — floor, every issue, non-negotiable**: `<test command>` passes.
- **L3 — user-visible issues**: L2 + `<boot command>` boots the app + a screenshot as evidence (`<screenshot command>`).
- **L4** (agent-driven interaction): out of scope v1.
- **L5 — human**: once per orchestrated run, against the branch, before merge. On GitHub the run posts the QA steps as a comment on the PRD issue and labels it `needs-qa`; the human works the comment start-to-finish and removes the label when done. On Azure DevOps the run files a `[QA]` work item and the human works it start-to-finish. Say here what exercising this app actually means — `<which entry point, which command, what to look for>` — because the run's steps are written against it and a worker only knows what this line says.

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
- Where skills come from: `<installed plugin + scope, or a symlink in .claude/skills/>`. Either way the skill files are not this project's to edit: a plugin cache is regenerated on install, and a symlink writes straight into the canonical repo. Project facts and gates live in `.claude/project/` instead, which is real and committed.

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

`<id>` and `<slug>` are branch-pattern notation: a filled `Branch pattern:` value is
itself a pattern (`spec/<id>-<slug>`), so those two survive filling by design.

**Delete this whole comment when you fill your copy.** doctor reads the exemption list
from the template, never from your adapter, so a copy of it here does nothing except
carry `<token>` into your file — where the placeholder check then reports it, forever.

doctor:not-a-placeholder <repo-root> <n> <id> <slug>
-->

