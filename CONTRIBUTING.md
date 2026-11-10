# Contributing

This is a personal skills repository, published as a plugin marketplace. Fixes and
small additions are welcome; before investing time in something large, open an issue
first — a skill that does not fit how the rest of these work is likely to be declined
no matter how well it is written.

## The one rule that shapes everything else

**Skill prose is executable.** An agent loads it and acts on it with its own tools, in
someone else's repository. A pull request here gets read the way code gets read, not
the way documentation gets read, and PRs that add instructions to fetch remote
content, send data anywhere, or run commands the skill's stated purpose does not need
will be declined. The single standing exception is a fetch inside the limits of
[ADR 0025](docs/adr/0025-a-skill-may-install-an-app-it-does-not-carry.md) — pinned to a
commit SHA, copy-only with nothing executed from the fetched tree, from a public source
repository — and a fetch outside those limits is declined like any other.
`SECURITY.md` covers the threat model.

That cuts both ways: if a review comment seems paranoid about a wording change,
that is why.

## Getting oriented

`CLAUDE.md` is the real map — read it first. The short version:

- Every skill lives **inside a plugin**, at `plugins/<plugin>/skills/<skill>/`. There
  is no other kind, and no other place to put one.
- `_shared/` is global reference only — docs true in every project. No templates, no
  project-specific values.
- `install/` is what a project gets wired with. `INSTALL.md` covers getting any of it
  onto a machine.
- Plugins namespace everything: `prd-workflow:work-on-prd`,
  `subagent_type: prd-workflow:prd-worker`. Naming an agent type wrong does **not**
  error — it silently degrades to `general-purpose` — so a run that completes is never
  evidence the type resolved.

## Before you open a PR

Run the same check CI runs:

```bash
python3 .github/scripts/validate_skills.py
```

It validates the marketplace catalog, plugin manifests, skill and agent frontmatter,
symlink integrity, and `_shared` references. Standard library only — please keep it
that way; this repo has no dependency manifest and should not grow one.

Then, for a skill change:

- Frontmatter `name` matches the directory name, and `description` says **when to
  invoke it**, not just what it does. The description is the only thing the model sees
  when deciding whether the skill applies.
- Actually run the skill end to end at least once. A skill that reads well and behaves
  badly is the normal failure mode here.
- Keep it generic. Address global reference as `../_shared/x.md` and the project as
  `<repo-root>/.claude/project/adapter.md`. Never name a project-specific gate file
  directly — follow the adapter's `## Project gates` registry. Hardcoding one
  project's filename forks the skill.
- Do not add a symlink that makes a skill *load* — not a top-level shim into
  `plugins/` (one skill under two names) and not a link under `.claude/skills/` (the
  retired self-host route). The validator fails on both. To work against the working
  tree, run `claude --plugin-dir plugins/<name>`. The packaging links inside
  `plugins/*/skills/` are a different thing and are required.
- Name fixtures only, never a consumer repo, ticket or path — in an issue, an eval case,
  a doc or a commit. See ADR 0027 (`docs/adr/0027-eval-cases-are-earned-by-a-failure.md`).

## Running an eval suite

A plugin whose manifest carries `experimental.evals` ships eval cases under
`plugins/<plugin>/evals/`. They run against the working tree, never an installed copy.

The suite:

```bash
command claude plugin eval plugins/<plugin> \
  --ablation none --scaffold --no-publish \
  --runs 1 --threshold 1.0 --max-cost-usd 5 \
  --model claude-sonnet-5 --judge-model claude-sonnet-5 \
  --allow-tools Write Bash Edit --tag <skill>
```

The adapter's eval gate row (`.claude/project/adapter.md`) is the command a branch runs, with the
`ANTHROPIC_API_KEY` prefix and one `--tag <skill>` per touched skill. Every flag is deliberate, and
the two the runner defaults differently are the ones to keep typing: `--ablation` defaults to with-without and `--judge-model` to Haiku.

- `--ablation none` — these suites score the skill's behaviour, not the delta against a
  no-plugin arm, and the baseline arm doubles the cost.
- `--scaffold` — a case's own `scaffold.sh` places its workspace, and without this flag each
  case runs against an empty workspace and fails for the wrong reason.
- `--tag <skill>` — an OR filter that scopes the run to the cases carrying the tag of a
  touched skill.
- `--no-publish` — a local run is not a report.
- `--model claude-sonnet-5` is the gate: a suite passes there or it does not pass.
  Re-running on `claude-haiku-4-5` is advisory — a cheaper model failing a case is a
  signal about the prose, not a regression.
- `--judge-model claude-sonnet-5` — the graders read skill prose against a repo's
  wiring, which the default judge is too small for.
- `--allow-tools Write Bash Edit` — only the read-only tools are granted by default, and a
  case whose skill writes a file or shells out scores zero without this. A case's own
  `allowed_tools` narrows what the child may use; it cannot widen past this grant.

`claude` is a shell function on the maintainer's machine, so `command claude` is what
reaches the binary. The runner writes scores to `plugins/<plugin>/evals/results/` and
records MCP stand-ins into `plugins/<plugin>/evals/mocks/`; both are gitignored.

A new case needs three things the dashboard (`dashboard/`) reads: a name of the form
`<skill>-<behaviour>`, which is how a case is filed under its skill; a `tags:` entry with the tag
of every skill the case's prompt invokes (`tags: [report]`); and a one-line `summary:` saying what
it checks, shown as the case's title. The runner ignores `summary:`.

## Adding an eval case

The default is no case. A case is added only when all four hold:

1. The failure came back after a fix. A first failure is fixed in prose.
2. The maintainer would not see the failure when it happens again: the path is unattended, a
   second skill or a script parses the output, or the output is public or irreversible.
3. A deterministic grader decides it in one run. No LLM grader, and no grader on wording.
4. No free check can prevent it instead: a validator rule, a script, a template or a redesign.

One exception: a failure the maintainer could never notice (private data in a public issue, a
broken contract in an unattended run) qualifies on its first plausible occurrence. Conditions 2 to
4 still hold.

When a failure returns after a fix, answer "redesign or eval" first: a free mechanical check that
makes it impossible comes before a case. An issue carrying a `Recurrence of #N` line needs that
answer in its pull request description. ADR
[0027](docs/adr/0027-eval-cases-are-earned-by-a-failure.md) has the argument.

## Pull requests

Contributors fork and open a PR — nobody outside the maintainer has push access, so
that is the only route. Keep PRs to one concern. CI runs on fork PRs with a read-only
token and no secrets.

Changes reach `main` by pull request, maintainer included — a skill edit is a
behaviour change and gets a readable diff and a green CI run before it lands. `main`
also blocks force-pushes and deletion for everyone, with no bypass actors.
