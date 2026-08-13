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

One bundle is the exception, and it is an exception to *who answers*, not to *when*:
`figma-tools` implies **either** tracker, so on a fresh copy step 3a asks the human and
settles it before the interview proper begins. Everything below then behaves identically —
one branch asked, one branch already gone from the file.

So it is not a question, and the other tracker's questions are not asked. Asking a GitHub
project for its board state names is the first failure mode from the top of this file, with
the added insult that the answers would go into a sub-section that is no longer in the
file. Everything else in the adapter is tracker-agnostic and is asked identically either
way.

## Inference table

| Adapter section | Read this | Ask only for |
|---|---|---|
| `## Repo` | **GitHub**: `gh repo view --json nameWithOwner,defaultBranchRef`; plus, for the two optional rows below, the PR template on disk (`.github/pull_request_template.md` and its casings, the root and `docs/` variants, then a `.github/PULL_REQUEST_TEMPLATE/` directory) and the branch convention the repo already uses (`git branch -r`, or the head branches of the last handful of merged PRs). **Azure DevOps**: the default branch from git and nothing else — the tree states none of the rest | related repos / contract boundaries on either tracker — nothing states these reliably. **Title prefixes on either tracker**: offer the defaults (`[PRD]`·`[TASK]`·`[BUG]` on GitHub, `[SPEC]`·`[TASK]`·`[FINDINGS]`·`[BUG]` on ADO — neither tracker has a `[QA]` prefix) and only ask whether this repo already uses different words — one confirmation, not four questions. On ADO the answer is load-bearing rather than cosmetic, since every kind of child is the same work-item type and the prefix is all that separates them, so read it back. On Azure DevOps, the whole `### Azure DevOps` block as well: org, the **two** projects (work items and repo — ask for both even when they are the same, since querying the wrong one returns empty rather than an error), team, repository, work-item type, the three board states, and the branch pattern. **On GitHub only**, the two optional rows `Branch pattern:` and `PR template:` — one confirmation each of what the read above turned up, never a cold question, and "we have neither" is a finished answer. The `prd-workflow` question set below carries the discovery ladder |
| `## Commands` | `package.json` scripts · `Makefile` targets · `Package.swift` + schemes · `Cargo.toml` · `pyproject.toml`. Package manager from the lockfile (`pnpm-lock.yaml` → pnpm, `bun.lockb` → bun, …) | the screenshot command — it is usually unscripted, and "none, use the browser tools interactively" is a real answer |
| `## App facts` | language + version, framework + version, path aliases, generated-vs-source files, strict flags — all from the manifests and config files | **the fragile part.** The subsystem that breaks silently and that no linter catches. This is the highest-value line in the adapter and it is never in a file |
| `## Design system` | the design-system dependency and its version from the manifests · a Tailwind config's `prefix` · an existing catalog file if the repo already has one. **Never the repo role** — a `components/` directory is not evidence of a library, and the tree cannot tell you which side of the design system a repo is on | the **repo role** first (`consumer` or `library`; absent means `consumer`), because a `consumer` answer deletes three rows instead of asking about them. Then, **only when the answer is `library`**, the three convention rows: the **variant mechanism** as a ladder in the icon ladder's shape (primary declaration → fallback → the shapes that are the implementation rather than the declaration, plus the trap this repo has), the **token pipeline** (is there a generator, and what source does it consume? — "None, the CSS is hand-edited" is a real answer and it changes what a spec may say), and the **story convention** (where stories live, and are `argTypes` generated from the variants or hand-written?). Then, for either role: the **catalog pointer** if no file announces itself — never guess a filename, since this row is the only place it is ever named. The **fingerprint command** ("None — staleness unchecked" is a real answer). The **three class-prefix facts** as three questions, not one: the Tailwind class prefix, the CSS variable prefix, and the form an app actually writes — a design system that prefixes internally and emits unprefixed is the normal case, and reading one answer as all three makes every spec recommend a class that does not exist. The **icon ladder**, in order, including where each source may be used — ask for sources plural, since one is the exception. Then the two optional rows, once each: is there a best-practices doc a spec should cite, and does a skill implement filed specs? **"No" to either is a complete answer** — leave the row out and never warn |
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

Then `## Repo`'s two optional `### GitHub` rows, which decide what a run's branch and pull
request look like **to the team**: `Branch pattern:` and `PR template:`. Both are
**discovered first and confirmed second** — the infer-first rule at the top of this file
applies to them more than to anything else here, because both answers are sitting in the
repo and asking cold teaches the user the installer never looked.

**`PR template:` is a ladder, and a path beats a copy at every rung.** The loop reads the
path at run time, so a path keeps tracking the team's file as they edit it; a copy is
frozen the moment it is taken.

1. **The standard file.** `.github/pull_request_template.md`, its casings, and the root and
   `docs/` variants GitHub also honours. Found one → record its path, confirm in one line,
   done.
2. **A multi-template directory** — `.github/PULL_REQUEST_TEMPLATE/`. This rung *is* a real
   question, because there is more than one answer: which of these does a PRD's pull request
   use? Record that one file's path, never the directory.
3. **The team's own PR-opening skill or docs** — a project skill or slash command that opens
   PRs, or a `CONTRIBUTING.md` section that dictates the body. Where it *reads* a file,
   record that file's path; the template is still a path, it was just reached indirectly.
4. **A snapshot, and only when the first three found nothing.** Write the literal word
   `snapshot` as the row's value and the template body fenced beneath it. Say out loud that
   `doctor` will report it as possibly stale on every run from then on — that is the cost of
   a copy, and it is why the rungs above exist.

**`Branch pattern:`** — read the branch names the repo already uses and offer back what you
saw, as one confirmation rather than an open question: *"your merged PRs branch as `feat/…`
and `fix/…` — should a PRD run's branch be `feat/<slug>`?"* The only placeholders are `<n>`
(the PRD's issue number) and `<slug>`, and both are optional, so a constant like `release`
is a legal answer. Don't infer a pattern from one branch, and don't invent a semantic prefix
the repo does not already use — the loop makes one branch per PRD, not one per change kind.

**Neither row is a gap.** Absent, they leave the loop on `prd/<n>-<slug>` with its own PR
skeleton — exactly what every project got before the rows existed. Ask once each, take "no"
or "we don't have one" as a complete answer, leave the row out, and record no warning
anywhere. Same doctrine as `## Design system`'s two optional rows, and `SKILL.md` step 4
states it once for all four.

**`ado-workflow`** — the same set, and it is the one bundle where `## Repo` is a real
interview rather than a `gh` call. Its board facts are worth more care than anything else
here, because every one of them fails *silently*:

1. The `### Azure DevOps` block. Work-item project and repo project are two questions, not
   one. Board states are the names on **this team's** board, and a near-miss is a no-op,
   not an error — read them back for confirmation rather than accepting them once.
2. Then the same top three as `prd-workflow`: the fragile subsystem, the verify floor and
   its L3 evidence, and the deliberate-looking-wrong conventions.

The two optional rows in `prd-workflow`'s set are **GitHub-only and not asked here**: the
`### Azure DevOps` block carries its own `Branch pattern:` row, filled as part of step 1
above, and that side has no `PR template:` row at all.

Do not ask which tracker — the bundle already said. There is no QA path to ask for on
either tracker: GitHub posts a per-run QA comment on the PRD and labels it `needs-qa`,
Azure DevOps files a per-run `[FINDINGS]` work item, and neither writes a file.

**`prd-qa`** — a subset of `prd-workflow`'s sections, so if the repo already ran that
install every one is filled: confirm, don't re-ask. On a standalone install the one worth a
real question is `## Sources of truth` — specifically whether a **contract-boundary** repo
and explorer agent exist. `triage` routes cross-repo findings through them, and "None" is a fine
answer that makes every finding a this-repo finding; a *guessed* answer sends issues to
the wrong tracker.

**`figma-tools`** — two sections, and it is **the one bundle whose tracker is a question**
(`SKILL.md` step 3a): it files on both, so nothing can answer for it. Order the interview so
it makes sense to someone who has never read a skill:

1. **Which tracker does this project run?** One question, asked before anything else, because
   it decides which pair of filing rows the rest of `## Repo` even has.
2. **`## Repo`'s two filing rows**, in that tracker's own words: where a page spec files
   (*design-spec target*) and where an escalated design-system gap files (*DS-gap backlog*).
   Ask both even when the answer is the same value twice — the common case is that they
   differ, since a gap belongs to the design system rather than to the app being specced.
3. **Which role does this repo play?** `consumer` (it renders the design system) or `library`
   (it *is* the design system). One question, asked before the rest of `## Design system`,
   because it **gates** the three convention questions in step 4 — a `consumer` answer means
   those three rows are never asked about and never written. On a fresh copy of the template
   they are simply left out, which is ordinary filling; against an adapter that already exists
   nothing is removed, per step 3's deletion rule. Never infer it: a repo with a
   `components/` directory is not thereby a library, and the tree has no way to say which side
   of the design system it sits on. `consumer` is the default and what an absent row means, so
   an answer of "I don't know what that means" resolves to `consumer` safely.
4. **Only when the answer was `library`** — the three convention rows, one question each. Each
   is about the design system's own source, and none of them is readable:
   - **How does a component declare its variant axes?** Ask for a **ladder**, in the icon
     ladder's shape: what is tried first, what the fallback is when that is absent, and which
     shapes are the *implementation* of a variant rather than its declaration. Ask explicitly
     for the trap — the place where the mechanism lies, e.g. a runtime alias map outside the
     declaration that accepts values it never lists.
   - **Is there a token generator, and what source does it consume?** This one decides how
     literal a spec's token delta may be, so it is worth pressing on: a generator plus a source
     file → a spec states the literal source edit; **"None — the emitted CSS is hand-edited"**
     is an equally real answer → a spec states a coordinated file-edit list instead.
   - **Where do stories live, and are `argTypes` generated or hand-written?** Generated from the
     variants means adding a variant value needs no story edit; hand-written means it does, and
     a spec has to say so.
5. **The rest of `## Design system`**, per the inference row above: the catalog pointer first
   (nothing else in the section matters without it), then the fingerprint command, the three
   class-prefix facts, the icon ladder, and last the two optional rows.

That is more than the six-question cap for a `library` repo, and it is the one place here where
that is right: the cap exists to stop an installer asking for things it could have read, and
none of these four is in any file. A `consumer` repo — the common case — gains exactly one
question over what this bundle asked before.

The `ui-manifests.md` gate is still the offer at the end, and the honest default is still no
until this project has been burned once.

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
