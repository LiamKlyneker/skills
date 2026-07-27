---
name: install-skills
description: Install a skill bundle from the canonical skills repo into any project, and check an existing install for rot. Use when adopting the PRD workflow (or another bundle) in a new repo, when an install looks broken or forked, when skills were copied instead of symlinked, or when the user asks to install, update, or diagnose skills in a project.
---

# Install Skills

One command to put a skill bundle into a repo, and one that says when an install has
rotted. Three modes: **`install`**, **`doctor`**, **`update`**.

The layout being installed is settled elsewhere and is not up for negotiation here — a
project owns exactly one directory (`<repo-root>/.claude/project/`), skills reach it by
symlink, and **a project never owns a `_shared/`** (the one exception is vendor mode,
below, and it is stamped). See `../install/README.md`.

Bundles are defined in `../install/bundles.md`. **Read that file — never hardcode a
skill list.** Adding a bundle there is the only thing adding a bundle should require.

## Resolving canonical

Everything below needs the path to the canonical skills repo on this machine.

- If this skill was reached through a symlink, its own physical location *is* canonical:
  `cd "$(dirname <this SKILL.md>)/.." && pwd -P`.
- Otherwise ask, and remember it in the stamp (vendor mode) — never guess a clone path.

If the target project *is* the canonical repo, stop: it installs nothing into itself.

---

## `install <bundle> [--vendor]`

### 1. Resolve the ground truth

Repo root (`git rev-parse --show-toplevel`), remote (`gh repo view --json nameWithOwner`),
default branch (`gh repo view --json defaultBranchRef`). If the target is not a git repo,
stop and say so — every bundle assumes `gh`.

### 2. Read the bundle

Look it up in `../install/bundles.md`. **Status `pending #N` → refuse**, name the issue,
and stop. Do not partially install, and do not substitute a neighbouring bundle.

### 3. Skip what is already reachable

Before linking anything, check each skill for an existing home:

- `<repo-root>/.claude/skills/<skill>` — already installed here.
- `~/.claude/skills/<skill>` or any `~/.claude-*/skills/<skill>` — installed globally, and
  a session in this repo will find it.

**A globally-installed skill must not be re-linked per project.** Report it as already
reachable and move on. Re-linking it is not harmless: it makes the project look like it
owns a decision it doesn't, and the project copy then has to be maintained.

### 4. Place the skills

Default is **symlink**:

```bash
mkdir -p .claude/skills
ln -sfn "<canonical>/<skill>" ".claude/skills/<skill>"
```

Use a relative target when the two repos are siblings under one parent, an absolute path
otherwise. `--vendor` copies instead — see `references/vendor.md` before using it.

Then the bundle's **Agents**, one symlink each, at the scope the manifest declares
(`user` → `~/.claude/agents/`, `project` → `<repo-root>/.claude/agents/`). Scope is a
safety property, not a preference: `prd-worker` commits, so it is project-scoped so a
stray auto-spawn from an unrelated repo is impossible. Tell the user a newly created
agents directory does not register until the next session.

### 5. The adapter

If the bundle's **Adapter sections** field is empty, the bundle is adapter-free — create
no `.claude/project/`, run no interview, skip to step 7.

Otherwise copy `../install/adapter.template.md` → `<repo-root>/.claude/project/adapter.md`
**only if absent**. A filled adapter is the project's own work and is never overwritten,
never re-templated, never reordered. If one already exists, read it and treat the
interview as a gap-fill for the bundle's required sections only.

### 6. Interview — infer first, ask for the rest

Read `references/interview.md`. The rule: anything a file already states, read; only
ask for what no file in the repo can answer. Asking for a test command that is sitting
in `package.json` is how an install earns a reputation for being tedious.

Fill only the sections the bundle requires. That list is what keeps the interview finite
and bundle-specific rather than asking every question every time.

### 7. Gates

Offer a gate only when the bundle declares one, or when the interview surfaced a real
silent-failure class. Copy the template to `.claude/project/<gate>.md`, then **register
it in the adapter's `## Project gates` table** — that registry is the only place a gate
is ever named, which is what keeps canonical skills generic instead of forked to hardcode
one project's filename.

### 8. Commit boundary

- `.claude/project/` — **committed**, always. It is the project's own facts.
- `.claude/skills/` — **gitignored** when symlinked (a symlink is machine-local; a
  collaborator cloning the repo gets a dangling link). **Committed** when vendored,
  together with `INSTALL-STAMP.md`.

Say which one applies and offer the `.gitignore` line. Do not commit anything yourself
unless asked.

### 9. Run `doctor` and report

Always. An install that does not end in a clean doctor run is not finished.

---

## `doctor`

```bash
<canonical>/install-skills/scripts/doctor.sh [--repo <path>] [--bundle <slug>] [--quiet]
```

Deterministic on purpose — every check here is mechanical, and a check that is
paraphrased differently on each run is not a check. Run the script; do not re-implement
its checks by hand or "spot-check" a subset.

| Label | Means |
|---|---|
| `FORK` | a real directory where a symlink belongs, unclaimed by any stamp |
| `BANNED` | a project-owned `_shared/` — shadows canonical for any copied skill |
| `DANGLING` | a symlink under `.claude/` whose target is gone |
| `HOLE` | an installed skill reads the adapter, and there isn't one |
| `UNFILLED` | the adapter still carries the TEMPLATE marker or template placeholders |
| `POINTER` | the adapter names a sibling file that does not exist |
| `SHARED` | a skill reads `../_shared/x.md` that does not resolve from where it sits |
| `STALE` | a vendored skill is N commits behind its stamped SHA |
| `DIVERGED` | a vendored skill was edited in place since its stamp |
| `MISSING` | a bundle skill reachable neither in the repo nor from a global config dir |

Exit 0 clean · 1 problems · 2 usage error.

Interpretation is yours, not the script's. In particular: a `FORK` is a decision, not a
delete. Someone edited that copy for a reason and the diff against canonical may contain
work worth back-porting. Report it, show the diff, and let the human decide — replacing a
fork with a symlink silently destroys whatever was in it.

---

## `update`

**Symlink mode** — re-point every link at the current canonical path (clones move), then
run `doctor`. Nothing else to do: a symlink is always live, which is the entire reason it
is the default.

**Vendor mode** — for each stamped skill, report *behind by N commits* and *locally
modified files* separately, because they need opposite responses: behind is a re-copy,
modified is a conversation. Never re-copy over local divergence without showing the diff
first. Details and the re-stamp sequence: `references/vendor.md`.

---

## Edge cases

- **Bundle skill already installed globally** → not a problem, and not something to
  "fix". Report and skip (step 3).
- **Adapter exists but predates the bundle** → gap-fill the missing sections; leave
  everything else alone, including sections the bundle doesn't require.
- **`doctor` finds a fork** → do not resolve it as part of an install. Stop, show the
  diff, hand it back.
- **No `gh` remote** → the workflow bundles are unusable without one. Say so rather than
  filling `## Repo` with a guess.
- **The project is the canonical repo** → refuse.
- **Target has no `.claude/` at all** → normal; that is a fresh install.
