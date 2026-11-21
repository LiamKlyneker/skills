---
name: setup-repo
description: >
  Turn a brainstorm session that has no repository into a GitHub repo: one first commit holding a
  `README.md` of what the session settled, issue #1 holding what is still open, and the next steps
  printed. Asks only for the repo facts the session and `gh` did not give, shows a plan, and creates
  nothing before approval. Writes no framework code, no adapter and no `.gitignore`. Use at the end
  of a brainstorm about a new product, from a directory that is not a git repo. Invoke
  /lk:setup-repo.
disable-model-invocation: true
---

# setup-repo

**The conversation is the source. This skill moves what a brainstorm settled into a new repo, and
records what it left open.**

By the time this runs, the brainstorm is over. No workflow skill runs outside a git repo, so this
skill is the bridge: it creates the repo, writes the settled decisions where the next session will
read them, and files the open questions where the next grill will answer them. It is not a
scaffolder and not a second grill.

Two rules govern everything it writes:

- **Introduce no fact the conversation does not hold.** Where the session left something
  unsettled, it is an open question for issue #1, not a gap to fill in the `README.md`.
- **Never answer an open question.** Record it. Answering it here makes this skill a second, weaker
  grill, and the real grill that follows will not know which answers nobody chose.

## 1. Sort the conversation

From the conversation so far, build three lists:

- **Settled decisions**, each with the reason the session gave for it. A decision with no reason in
  the session keeps no invented one; write it without a reason.
- **Open questions** — everything raised and not settled, including choices the session named and
  deferred, such as the stack.
- **Risks** — what the session said could go wrong.

Also collect **what the product is**, in the session's own terms, and **every design asset that
exists as a file on disk** — a pasted image, a sketch, an exported mock — by the path the
conversation shows for it. An asset with no file on disk is described in the `README.md` only if a
settled decision depends on it, and is not copied.

**If the session holds no brainstorm** — it is empty, or never discussed a product — stop and say
so. Do not interview the user to build one; the brainstorm is the input, not this skill's job.

## 2. Find the repo facts

**Check `gh auth status` first.** Without auth, stop and say `gh` is not authenticated; create
nothing.

Read the login and the orgs:

```bash
gh api user --jq .login
gh api user/orgs --jq '.[].login'
```

Four facts are needed: **repo name**, **owner** (the login or one of the orgs), **visibility**
(`private` or `public`), and **local path** (an absolute directory that does not exist yet, or
exists and is empty).

**Ask only for the ones the session did not settle.** A name the brainstorm chose is not asked
again; an owner is not asked when the user has no orgs and the login is the only choice. Ask the
missing ones together, in one question, with the login and the orgs offered as the owner choices.

Then check, before the plan:

- `gh repo view <owner>/<name>` fails. When it succeeds, a repo with that name already exists
  under the owner, and the plan waits until the user picks another name;
- the local path is not inside an existing git repo (`git -C <parent> rev-parse` fails) and is
  empty or absent.

## 3. Write the files, then show the plan

**Write every file to `<scratch>/setup-repo/` before the plan**, where `<scratch>` is the session
scratchpad directory the harness names, or a fresh temp directory when it names none:
`README.md`, `issue-title.txt`, `issue-body.md`. The text the user approves is byte-identical to the
text that lands.

### `README.md`

```
# <product name>

<what the product is, in two to five sentences, in the session's terms>

## Decisions

- **<decision>.** <reason>
- ...
```

It holds **what the product is and the settled decisions with their reasons, and nothing else**.
No open question, no risk, no "to be decided" line, no next steps. When the commit carries an asset,
the `README.md` links it by its path in the repo.

### Issue #1

Title: a plain line naming the work, such as `Open questions and risks from the brainstorm`. **No
title prefix and no label** — the new repo has no adapter, so no prefix is registered for it, and
this skill never hardcodes one.

Body:

```
Settled decisions: https://github.com/<owner>/<name>/blob/<default-branch>/README.md

## Open questions

- <question> — <what the session said about it, if anything>
- ...

## Risks

- <risk>
- ...
```

It **repeats no settled decision**. One home per fact: a decision held in both places can disagree
after the first grill.

### The plan

Show, then wait for an explicit yes:

- `<owner>/<name>`, visibility, local path;
- the files of the first commit — `README.md`, and each asset copied to `assets/<file name>`;
- the title of issue #1;
- the full text of `README.md` and the issue body.

**Create nothing before the approval.** The repo is outward-facing and, under a public owner,
visible the moment it exists. A change the user asks for is made in the scratch files and the plan
is shown again. A no ends the run with nothing created.

## 4. Create the repo

From the parent of the local path:

```bash
mkdir -p <local-path>
cp <scratch>/setup-repo/README.md <local-path>/README.md
# for each asset:
mkdir -p <local-path>/assets && cp <asset-path> <local-path>/assets/<file name>
git -C <local-path> init -b main
git -C <local-path> add README.md assets
git -C <local-path> commit -m "Initial commit: README of the brainstorm's decisions"
gh repo create <owner>/<name> --<visibility> --source <local-path> --remote origin --push
```

Leave out `assets` from the `add` when no asset was copied. **The first commit holds `README.md`
and the copied assets, and nothing else** — no `.gitignore`, no licence, no adapter, no CI, no
framework file. Each of those depends on a stack or a setup step that has not happened yet.

## 5. File issue #1

```bash
gh issue create --repo <owner>/<name> \
  --title "$(cat <scratch>/setup-repo/issue-title.txt)" \
  --body-file <scratch>/setup-repo/issue-body.md
```

Replace `<default-branch>` in the body with the branch the push created before filing. Never pass
`--label`.

## 6. Print the next steps

End with this, in this order, with the real values filled in:

```
Created <repo-url>, issue #1: <issue-url>

Next steps:
1. Start a new Claude Code session in <local-path>.
2. Run /lk:setup for the `grill` bundle, then /prd-workflow:setup for the `prd-workflow` bundle.
3. Run /lk:grill on issue #1.

Risk on step 2: the repo has no code yet, so setup can ask for facts that do not exist, such as
the verify commands. If it does, run /lk:setup now and run /prd-workflow:setup after the grill.
See https://github.com/LiamKlyneker/skills/issues/342.
```

Nothing is created or edited after this print.
