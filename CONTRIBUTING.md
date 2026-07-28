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

- A skill lives either **inside a plugin** (`plugins/<plugin>/skills/<skill>/`) or
  **at the top level** as a plain skill, one directory each.
- `_shared/` is global reference only — docs true in every project. No templates, no
  project-specific values.
- `install/` is what a project gets wired with. `INSTALL.md` covers getting any of it
  onto a machine.
- Plugins namespace everything: `prd-workflow:work-on-prd`,
  `subagent_type: prd-workflow:prd-worker`. Naming an agent type wrong does **not**
  error — it silently degrades to `general-purpose` — so any doc naming a subagent
  type must say which route it means.

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
- Do not add a top-level symlink into `plugins/`. It makes one skill discoverable
  under two names, which is exactly what the plugins migration removed.

## Pull requests

Contributors fork and open a PR — nobody outside the maintainer has push access, so
that is the only route. Keep PRs to one concern. CI runs on fork PRs with a read-only
token and no secrets.

The maintainer commits directly to `main`; that is deliberate and documented in
`CLAUDE.md`, not an oversight. `main` blocks force-pushes and deletion for everyone,
including the maintainer.
