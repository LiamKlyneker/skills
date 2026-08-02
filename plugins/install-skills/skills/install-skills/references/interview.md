# The install interview

Filling the adapter is the only part of an install that needs a human — the platform
delivers the skills themselves. So the interview has exactly one job: **ask the smallest
number of questions that no file in the repo can answer.**

Two failure modes, and the second is the common one:

- Asking for a value that is sitting in `package.json`. Tedious, and it teaches the user
  the installer hasn't looked at their repo.
- Inferring a value that only a human knows — the verify floor, the fragile subsystem,
  the house rule that looks like a smell. A confidently wrong adapter is worse than an
  empty one, because `doctor` can see an empty one.

Read the repo first. Then ask. Cap it around six questions; if you need more, you are
asking things you could have read.

## The tracker branches the interview

Two sections are tracker-specific — `## Repo` and `## One-time repo preconditions` — and
the adapter keeps exactly one branch of each. The tracker is **already settled** by the
time the interview starts: `SKILL.md` step 3a takes it from the bundle (via the *Which
tracker a bundle implies* table in `../../install/bundles.md`) on a fresh copy, or reads
the existing adapter's `Tracker:` line, where **absent means `github`**.

So it is not a question, and the other tracker's questions are not asked. Asking a GitHub
project for its board state names is the first failure mode from the top of this file, with
the added insult that the answers would go into a sub-section that is no longer in the
file. Everything else in the adapter is tracker-agnostic and is asked identically either
way.

## Inference table

| Adapter section | Read this | Ask only for |
|---|---|---|
| `## Repo` | **GitHub**: `gh repo view --json nameWithOwner,defaultBranchRef`. **Azure DevOps**: the default branch from git and nothing else — the tree states none of the rest | related repos / contract boundaries on either tracker — nothing states these reliably. **Title prefixes on either tracker**: offer the defaults (`[PRD]`·`[TASK]`·`[BUG]` on GitHub, `[SPEC]`·`[TASK]`·`[FINDINGS]`·`[BUG]` on ADO — neither tracker has a `[QA]` prefix) and only ask whether this repo already uses different words — one confirmation, not four questions. On ADO the answer is load-bearing rather than cosmetic, since every kind of child is the same work-item type and the prefix is all that separates them, so read it back. On Azure DevOps, the whole `### Azure DevOps` block as well: org, the **two** projects (work items and repo — ask for both even when they are the same, since querying the wrong one returns empty rather than an error), team, repository, work-item type, the three board states, and the branch pattern |
| `## Commands` | `package.json` scripts · `Makefile` targets · `Package.swift` + schemes · `Cargo.toml` · `pyproject.toml`. Package manager from the lockfile (`pnpm-lock.yaml` → pnpm, `bun.lockb` → bun, …) | the screenshot command — it is usually unscripted, and "none, use the browser tools interactively" is a real answer |
| `## App facts` | language + version, framework + version, path aliases, generated-vs-source files, strict flags — all from the manifests and config files | **the fragile part.** The subsystem that breaks silently and that no linter catches. This is the highest-value line in the adapter and it is never in a file |
| `## Verify ladder` | candidate L2 from the test/build scripts | confirmation that L2 is the real floor, and what L3 evidence looks like. A repo with no test suite is a legitimate answer — record *why*, so no worker treats it as a gap to fill on the side |
| `## Sources of truth` | agents available in `.claude/agents/` and `~/.claude/agents/` | the access-policy source — where per-operation policies actually live (migrations, IaC, a console, an MCP). "None — no data layer" is a real answer and closes the question |
| `## Project gates` | — | one question: *is there a class of breakage here that ships silently and no test catches?* Default is **None**. A gate invented at install time to look thorough will never be run |
| `## Repo discipline` | root `CLAUDE.md` · presence of scoped `CONTEXT.md` files · barrel-file layout | the conventions that read as smells but are deliberate. Ask directly: *what would a new contributor "clean up" that they shouldn't?* |
| `## One-time repo preconditions` | — | nothing — but tell the human what to check, for this adapter's tracker only. **GitHub**: verify the "auto-close issues with merged linked pull requests" setting in the web UI; it is queryable through neither the REST repo object nor the GraphQL `Repository` type, so it is a human check or it is nothing. **Azure DevOps**: the MCP server must be registered under the key `ado` in the config directory the session runs under — under any other key every skill's readiness probe reports it unconfigured — and the three board states must exist spelled exactly as written in `## Repo` |

## Baselines are part of the answer

When a lint or test command already emits warnings on a clean tree, record the count and
where they are. Without a baseline, the first worker to run L2 either "fixes" pre-existing
warnings as drive-by scope or treats its own new ones as pre-existing. Both are silent.

## Per-bundle question sets

Ask only for the sections the bundle declares in `../../install/bundles.md`.

**`prd-workflow`** — the full set. The three that carry the most weight, in order:

1. The fragile subsystem (`## App facts`).
2. The verify floor, and what L3 evidence is when there's no screenshot command.
3. The deliberate-looking-wrong conventions (`## Repo discipline`).

**`ado-workflow`** — the same set, and it is the one bundle where `## Repo` is a real
interview rather than a `gh` call. Its board facts are worth more care than anything else
here, because every one of them fails *silently*:

1. The `### Azure DevOps` block. Work-item project and repo project are two questions, not
   one. Board states are the names on **this team's** board, and a near-miss is a no-op,
   not an error — read them back for confirmation rather than accepting them once.
2. Then the same top three as `prd-workflow`: the fragile subsystem, the verify floor and
   its L3 evidence, and the deliberate-looking-wrong conventions.

Do not ask which tracker — the bundle already said. There is no QA path to ask for on
either tracker: GitHub posts a per-run QA comment on the PRD and labels it `needs-qa`,
Azure DevOps files a per-run `[FINDINGS]` work item, and neither writes a file.

**`prd-qa`** — a subset of `prd-workflow`'s sections, so if the repo already ran that
install every one is filled: confirm, don't re-ask. On a standalone install the one worth a
real question is `## Sources of truth` — specifically whether a **contract-boundary** repo
and explorer agent exist. `triage` routes cross-repo findings through them, and "None" is a fine
answer that makes every finding a this-repo finding; a *guessed* answer sends issues to
the wrong tracker.

**`figma-tools`** — none. The bundle is adapter-free. The only question worth asking is
whether this project wants its own `ui-manifests.md` gate, and the honest default is no
until it has been burned once.

## Writing the answers down

Write prose, not form-filling. The adapter is pasted verbatim into every `work-on-prd`
worker prompt, so it is read by an agent with no other context about this repo — a row
that says `pnpm test` teaches nothing, and a paragraph explaining that there is no test
suite, that `pnpm build` *is* the typecheck, and which two warnings are baseline, changes
what every worker does.

Delete template rows that don't apply. An adapter with "None — no contract boundary" is
finished; an adapter with `<subagent_type>` still in it is not, and `doctor` will say so.

Two pieces of the copy are template machinery rather than project content, and filling
means removing them: the `# Project Adapter — TEMPLATE` marker (retitle it for the project
— `doctor` reads the word TEMPLATE in the first five lines as "copied, never filled") and
the trailing `doctor:not-a-placeholder` HTML comment. That comment's exemption list is
read from the **template**, never from your copy, so leaving it behind achieves nothing
except carrying its own `<token>` example into the file for the placeholder check to
report on every run.
