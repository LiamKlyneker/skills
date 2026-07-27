# The install interview

Filling the adapter is the only part of an install that needs a human. Everything else is
symlinks. So the interview has exactly one job: **ask the smallest number of questions
that no file in the repo can answer.**

Two failure modes, and the second is the common one:

- Asking for a value that is sitting in `package.json`. Tedious, and it teaches the user
  the installer hasn't looked at their repo.
- Inferring a value that only a human knows — the verify floor, the fragile subsystem,
  the house rule that looks like a smell. A confidently wrong adapter is worse than an
  empty one, because `doctor` can see an empty one.

Read the repo first. Then ask. Cap it around six questions; if you need more, you are
asking things you could have read.

## Inference table

| Adapter section | Read this | Ask only for |
|---|---|---|
| `## Repo` | `gh repo view --json nameWithOwner,defaultBranchRef` | related repos / contract boundaries — nothing in the tree states these reliably |
| `## Commands` | `package.json` scripts · `Makefile` targets · `Package.swift` + schemes · `Cargo.toml` · `pyproject.toml`. Package manager from the lockfile (`pnpm-lock.yaml` → pnpm, `bun.lockb` → bun, …) | the screenshot command — it is usually unscripted, and "none, use the browser tools interactively" is a real answer |
| `## App facts` | language + version, framework + version, path aliases, generated-vs-source files, strict flags — all from the manifests and config files | **the fragile part.** The subsystem that breaks silently and that no linter catches. This is the highest-value line in the adapter and it is never in a file |
| `## Verify ladder` | candidate L2 from the test/build scripts | confirmation that L2 is the real floor, and what L3 evidence looks like. A repo with no test suite is a legitimate answer — record *why*, so no worker treats it as a gap to fill on the side |
| `## QA doc convention` | existing `docs/qa/` or similar, if present | the path convention. Offer `docs/qa/prd-N.md` as the default |
| `## Sources of truth` | agents available in `.claude/agents/` and `~/.claude/agents/` | the access-policy source — where per-operation policies actually live (migrations, IaC, a console, an MCP). "None — no data layer" is a real answer and closes the question |
| `## Project gates` | — | one question: *is there a class of breakage here that ships silently and no test catches?* Default is **None**. A gate invented at install time to look thorough will never be run |
| `## Repo discipline` | root `CLAUDE.md` · presence of scoped `CONTEXT.md` files · barrel-file layout | the conventions that read as smells but are deliberate. Ask directly: *what would a new contributor "clean up" that they shouldn't?* |
| `## One-time repo preconditions` | — | nothing. Tell the human to verify GitHub's "auto-close issues with merged linked pull requests" setting in the web UI — it is queryable through neither the REST repo object nor the GraphQL `Repository` type, so it is a human check or it is nothing |

## Baselines are part of the answer

When a lint or test command already emits warnings on a clean tree, record the count and
where they are. Without a baseline, the first worker to run L2 either "fixes" pre-existing
warnings as drive-by scope or treats its own new ones as pre-existing. Both are silent.

## Per-bundle question sets

Ask only for the sections the bundle declares in `../install/bundles.md`.

**`prd-workflow`** — the full set. The three that carry the most weight, in order:

1. The fragile subsystem (`## App facts`).
2. The verify floor, and what L3 evidence is when there's no screenshot command.
3. The deliberate-looking-wrong conventions (`## Repo discipline`).

**`prd-qa`** — `## QA doc convention` and `## Verify ladder` only. If the repo already ran
a `prd-workflow` install, both are filled: confirm, don't re-ask.

**`figma`** — none. The bundle is adapter-free. The only question worth asking is whether
this project wants its own `ui-manifests.md` gate, and the honest default is no until it
has been burned once.

## Writing the answers down

Write prose, not form-filling. The adapter is pasted verbatim into every `work-on-prd`
worker prompt, so it is read by an agent with no other context about this repo — a row
that says `pnpm test` teaches nothing, and a paragraph explaining that there is no test
suite, that `pnpm build` *is* the typecheck, and which two warnings are baseline, changes
what every worker does.

Delete template rows that don't apply. An adapter with "None — no contract boundary" is
finished; an adapter with `<subagent_type>` still in it is not, and `doctor` will say so.
