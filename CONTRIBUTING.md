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
will be declined. `SECURITY.md` covers the threat model.

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

## Running an eval suite

A plugin whose manifest carries `experimental.evals` ships eval cases under
`plugins/<plugin>/evals/`. They run against the working tree, never an installed copy.

A case that replays a recorded conversation declares `context.history_file`, and the
runner resolves that path inside the case directory before any scaffold script runs — so
the transcript has to be there already. It is gitignored, and this places it:

```bash
plugins/prd-workflow/evals/prepare-history.sh
```

Then the suite:

```bash
command claude plugin eval plugins/<plugin> \
  --ablation none --scaffold --no-publish \
  --runs 1 --threshold 1.0 --max-cost-usd 5 \
  --model claude-sonnet-5 --judge-model claude-sonnet-5 \
  --allow-tools Write Bash
```

Every flag is deliberate, and the two the runner defaults differently are the ones to
keep typing: `--ablation` defaults to with-without and `--judge-model` to Haiku.

- `--ablation none` — these suites score the skill's behaviour, not the delta against a
  no-plugin arm, and the baseline arm doubles the cost.
- `--scaffold` — the cases place the fixture workspace with
  `plugins/prd-workflow/evals/scaffold-fixture.sh`, and without this flag each case runs
  against an empty workspace and fails for the wrong reason.
- `--no-publish` — a local run is not a report.
- `--model claude-sonnet-5` is the gate: a suite passes there or it does not pass.
  Re-running on `claude-haiku-4-5` is advisory — a cheaper model failing a case is a
  signal about the prose, not a regression.
- `--judge-model claude-sonnet-5` — the graders read skill prose against a repo's
  wiring, which the default judge is too small for.
- `--allow-tools Write Bash` — only the read-only tools are granted by default, and a
  case whose skill writes a file or shells out scores zero without this. A case's own
  `allowed_tools` narrows what the child may use; it cannot widen past this grant.

`claude` is a shell function on the maintainer's machine, so `command claude` is what
reaches the binary. The runner writes scores to `plugins/<plugin>/evals/results/` and
records MCP stand-ins into `plugins/<plugin>/evals/mocks/`; both are gitignored.

The scaffold script copies the fixture from a `skills-fixture` checkout beside this
repo and clones it from GitHub when there is none. It prints which source it used —
pass `--dry-run` to see that without placing anything. `prepare-history.sh` resolves
its source the same way and takes the same flag.

## Pull requests

Contributors fork and open a PR — nobody outside the maintainer has push access, so
that is the only route. Keep PRs to one concern. CI runs on fork PRs with a read-only
token and no secrets.

Changes reach `main` by pull request, maintainer included — a skill edit is a
behaviour change and gets a readable diff and a green CI run before it lands. `main`
also blocks force-pushes and deletion for everyone, with no bypass actors.
