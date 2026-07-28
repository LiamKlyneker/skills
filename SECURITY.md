# Security Policy

## What this repository actually is

This repo publishes **Claude Code skills and plugins**. A skill is not documentation
that a human reads and decides about — it is a set of instructions that an agent
loads and acts on, with that agent's tools, in the user's own working directory, on
the user's own machine. Some skills here spawn subagents; one (`install-skills`)
ships an executable, `scripts/doctor.sh`.

So the threat model is closer to a package registry than to a docs site. A change to
prose *is* a change to behaviour. Treat it that way when reading a diff, and when
deciding whether to install.

## Trust model when installing

Installing a plugin from this marketplace copies it into your config's cache, pinned
to the git commit that was `HEAD` at install time. That pin is the security boundary:

- You are trusting this repository's state **at the moment you install**.
- Later commits here cannot reach you until you reinstall or update.
- The skills-dir route (a symlink into a config's `skills/`) has **no** pin — edits
  in the working tree are live on the next session launch.

If you did not write a skill, read it before you run it. `INSTALL.md` describes both
routes in full.

## Reporting a vulnerability

Use **[private vulnerability reporting](https://github.com/LiamKlyneker/skills/security/advisories/new)**
on this repository's Security tab. Please do not open a public issue for anything in
the "in scope" list below.

Expect an initial response within about a week. This is a personal repository
maintained in spare time, not a staffed product; there is no bounty.

## In scope

- Instructions in a skill or agent that would cause an agent to **exfiltrate data** —
  sending file contents, environment variables, credentials, or repository contents
  to a third party.
- Prompt injection embedded in skill prose, examples, or fixture text — content
  crafted so an agent reading it treats it as an instruction.
- A skill that would run **destructive or irreversible commands** outside what the
  user asked for: force-pushing, deleting branches or files, rewriting history,
  pushing to remotes, or publishing.
- Anything in `install-skills/scripts/doctor.sh` — command injection, unsafe path
  handling, writing outside the target project.
- A `marketplace.json` or `plugin.json` whose `source` resolves somewhere other than
  where its name implies.
- Credentials, tokens, or private data committed to this repository.

## Not in scope

- A skill producing low-quality output, or advice you disagree with. Open a normal
  issue.
- A skill needing broad tool permissions to do its stated job. `work-on-prd` commits
  and pushes because that is what it is for — the mitigation is the permission prompt
  in your own harness, not this repo.
- Vulnerabilities in Claude Code itself, or in the Figma/GitHub tooling these skills
  drive. Report those to their own maintainers.
- Anything requiring push access to this repository, which only the maintainer has.

## Supported versions

`main` only. There are no release branches and no backports; fixes land on `main` and
reach you when you reinstall.
