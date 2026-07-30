---
name: install-skills
description: Bootstrap a project's adapter (`.claude/project/adapter.md`) for a skill bundle, and diagnose an install that has rotted. Use when adopting the PRD workflow (or another bundle) in a new repo, when the adapter is missing or half-filled, when skills look forked or a gate pointer is dead, or when the user asks to diagnose or repair the skills wiring in a project. It does not place skills — plugins come from the marketplace.
---

# Install Skills

Two modes, and only two — the two jobs no distribution mechanism can do for you:

- **`install <bundle>`** — bootstrap `<repo-root>/.claude/project/`: the adapter, the
  interview that fills it, and any gate the bundle offers.
- **`doctor`** — say when an install has rotted, in the failure classes that fail silently.

## What this skill does not do

**It does not place skills.** The platform does that, and does it better — installation,
versioning and updates are all things it has and a pile of symlinks never did:

- **Plugin** → `/plugin marketplace add LiamKlyneker/skills`, then `/plugin install
  <plugin>` from a session running under the config directory you want it in. Plugins are
  stored per config directory, so personal / client / other is an independent decision each
  time.
- **Plain skill, or live authoring** → a symlink into that config's `skills/` directory,
  pointing at your clone. Edits land immediately; nothing is copied.
- **Plugin that must travel with a repo** (collaborators, CI, cloud agents) → committed
  project settings, not a symlink only one laptop has.

So there is no `update` mode here, no copy-in mode, and nothing writes outside
`.claude/project/`. If you are asked to put skills somewhere, name the route above and
stop — do not hand-roll it.

The layout being bootstrapped is settled elsewhere and is not up for negotiation here: a
project owns exactly one directory (`<repo-root>/.claude/project/`), and **a project never
owns a `_shared/`**. See `../install/README.md`.

Bundles are defined in `../install/bundles.md`. **Read that file — never hardcode a
section list.** A bundle names *adapter sections*, not skills; see that file for why the
two are separate namespaces from the plugins.

## Resolving canonical

Both modes need the path to the canonical skills repo on this machine — the adapter
template, the gate templates and `doctor.sh` all live there.

- If this skill was reached through a symlink, its own physical location *is* canonical:
  `cd "$(dirname <this SKILL.md>)/.." && pwd -P`.
- Otherwise ask. Never guess a clone path.

If the target project *is* the canonical repo, stop: it bootstraps nothing into itself.

---

## `install <bundle>`

### 1. Resolve the ground truth

Repo root (`git rev-parse --show-toplevel`) and default branch. If the target is not a git
repo, stop and say so — every workflow bundle assumes one.

`gh repo view --json nameWithOwner,defaultBranchRef` answers both **on a GitHub-tracked
project**. An Azure DevOps one has no `gh` remote and never will: take the default branch
from git, and everything else from the interview. Which case you are in is the bundle's
call, settled in step 3a — not a guess from whether `gh` happened to succeed.

### 2. Read the bundle

Look it up in `../install/bundles.md`. **Status `pending #N` → refuse**, name the issue,
and stop. Do not partially bootstrap, and do not substitute a neighbouring bundle.

### 3. The adapter

If the bundle's **Adapter sections** field is empty, the bundle is adapter-free — create
no `.claude/project/`, run no interview, skip to step 5.

Otherwise copy `../install/adapter.template.md` → `<repo-root>/.claude/project/adapter.md`
**only if absent**. A filled adapter is the project's own work and is never overwritten,
never re-templated, never reordered. If one already exists, read it and treat the
interview as a gap-fill for the bundle's required sections only.

#### 3a. Settle the tracker

The template is **tracker-parametric**: `## Repo` and `## One-time repo preconditions` each
ship a `### GitHub` and an `### Azure DevOps` sub-section, and a filled adapter keeps
exactly one of the two — two sub-sections means every skill gets two answers to the same
question. Which one is not a question worth asking, because the bundle already decided it:
read the *Which tracker a bundle implies* table in `../install/bundles.md`, the same way
you read **Adapter sections**. Never hardcode the mapping here.

**A fresh copy — the file did not exist and you created it this run:**

1. Write the `Tracker:` line in `## Repo` to the bundle's tracker.
2. **Delete the non-chosen tracker's `###` sub-section**, from both `## Repo` and `## One-time
   repo preconditions`, along with the template's own instructions to make the choice: the
   *Pick your tracker first* note near the top, and the "delete the other" sentence under
   each of those two sections. The choice is made; instructions to make it are exactly what
   keeps a filled adapter still reading like a template.
3. Everything between those two sections is tracker-agnostic. It is not forked, not
   duplicated, and not touched here.

**An adapter that already exists — delete nothing.** Read its `Tracker:` line; **absent
means `github`**, which is what every adapter written before that line existed is. Then:

- Tracker matches the bundle → gap-fill the bundle's missing sections and nothing else.
- Tracker contradicts the bundle → **stop and hand it back.** One project runs one tracker,
  and reconciling that is a human decision, not a rewrite.
- It carries both sub-sections, or neither → that is a gap-fill question to ask, never a
  licence to delete.

#### The never-delete boundary, stated because it looks like a contradiction

Step 3's never-overwrite rule and step 3a's deletion are about two different files, and the
deletion is the strictly narrower one. Never-delete governs **an existing adapter** — the
project's own work, filled in by a human. That file is never overwritten, never
re-templated, never reordered and never pruned, including sections the bundle does not
require. What 3a removes is a section of a **fresh template copy this run made seconds
ago**, which nobody has ever filled in.

All three conditions must hold or you delete nothing:

- the file did not exist when this run started, and you created it from the template;
- nothing has been written into it yet beyond the `Tracker:` line;
- what you remove is exactly the non-chosen tracker's `###` sub-sections plus the
  scaffolding naming that choice.

Miss any one of them and the rule is the plain one: **gap-fill only, delete nothing.** In
particular, an install run against a repo that already has a filled adapter deletes
nothing at all — not the other tracker's sub-section, not a stale row, nothing.

The deletion earns its narrow exception because the alternative is permanent noise: an
ADO-only repo that keeps the `### GitHub` sub-section keeps its `<owner>/<repo>`
placeholder forever, and `doctor` reports it `UNFILLED` on every run from then on. A check
that is always noisy is a check nobody reads.

### 4. Interview — infer first, ask for the rest

Read `references/interview.md`. The rule: anything a file already states, read; only
ask for what no file in the repo can answer. Asking for a test command that is sitting
in `package.json` is how an install earns a reputation for being tedious.

Fill only the sections the bundle requires. That list is what keeps the interview finite
and bundle-specific rather than asking every question every time.

**Ask one tracker's questions, never both.** The tracker settled in 3a decides which
branch of `## Repo` and `## One-time repo preconditions` the interview covers — GitHub's
`owner/repo` and label vocabulary, or Azure DevOps' org, two projects, team, repository,
work-item type and board states. The other branch is not asked, not inferred, and (on a
fresh copy) no longer in the file.

### 5. Gates

Offer a gate only when the bundle declares one, or when the interview surfaced a real
silent-failure class. Copy the template to `.claude/project/<gate>.md`, then **register
it in the adapter's `## Project gates` table** — that registry is the only place a gate
is ever named, which is what keeps canonical skills generic instead of forked to hardcode
one project's filename.

An adapter-free bundle whose gate is accepted needs an adapter after all, since the
registry lives in it: create one from the template with `## Project gates` filled and
leave the rest for whenever a bundle asks for it. Offering the gate is one yes/no question
— it is not the interview, and it does not turn into one.

### 6. Commit boundary

`.claude/project/` is **committed**, always. It is the project's own facts, it is the only
thing this skill writes, and it is the one part of the wiring that has no distribution
mechanism and never will.

How the skills themselves reach this repo is a separate decision and a platform-level one
— see [What this skill does not do](#what-this-skill-does-not-do). Say which route applies
here so it is a decision rather than an omission. Do not commit anything yourself unless
asked.

### 7. Run `doctor` and report

Always. A bootstrap that does not end in a clean doctor run is not finished.

---

## `doctor`

```bash
<this-skill-dir>/scripts/doctor.sh [--repo <path>] [--bundle <slug>] [--quiet]
```

`<this-skill-dir>` is wherever this `SKILL.md` was loaded from — an install cache copy
or, in the canonical repo, `plugins/install-skills/skills/install-skills/`. The script
sits beside this file in both, and infers everything else it needs from its own
location, so never reconstruct the path from a repo root.

Deterministic on purpose — every check here is mechanical, and a check that is
paraphrased differently on each run is not a check. Run the script; do not re-implement
its checks by hand or "spot-check" a subset.

| Label | Means |
|---|---|
| `FORK` | a real directory where a symlink belongs, **shadowing a skill of the same name** — one in canonical, or one a reachable plugin provides. A real directory that shadows neither is a skill the project genuinely owns — reported as `INFO`, not a problem |
| `BANNED` | a project-owned `_shared/` — shadows canonical for any copied skill |
| `DANGLING` | a symlink under `.claude/` whose target is gone |
| `HOLE` | a skill reaching this repo reads the adapter, and there isn't one — from `.claude/skills/`, or from a plugin the repo's committed `.claude/settings.json` enables |
| `UNFILLED` | the adapter still carries the TEMPLATE marker or template placeholders, or is missing a `##` section the named bundle needs |
| `POINTER` | the adapter's `## Project gates` table registers a gate whose file does not exist as a sibling of `adapter.md` |
| `SHARED` | a skill reads `../_shared/x.md` that does not resolve from where it sits |
| `BUNDLE` | `--bundle` named a slug `install/bundles.md` does not define, or one whose **Status** is not `ready` |
| `MISSING` | a bundle offers a gate template that canonical does not ship |

`WARN` lines (a loose file in the skills directory, a manifest doctor could not read) count
as warnings, not problems. `OK` and `INFO` are neither, and `--quiet` hides them.

Exit 0 clean · 1 problems · 2 usage error.

**Where skills come from is a lookup, not a check.** A skill can reach a session from
`.claude/skills/`, from a plugin cache, from a skills-dir plugin, or from a plugin the
project enables in committed settings — so doctor reads all four and reports what it finds
as `INFO`. It never reports a plugin-provided skill as missing, and a repo with no
`.claude/skills/` at all is the normal post-plugin shape, not a broken one. What stays loud
is the shadowing: a real directory sitting on top of a skill something else already
provides.

### The double-load scan

Running both delivery routes for one skill in one place loads it twice. Doctor reports that
as `INFO` — it is a wiring decision, not a broken install — in two places:

- **Inside the repo**, for `.claude/skills/<name>` that a reachable plugin also provides.
- **In each config directory**, for `~/.claude*/skills/<name>` that a plugin installed in
  **that same config** also provides, and for a skills-dir plugin parked there whose plugin
  is *also* installed from a marketplace into that config.

The config-level half is scoped per config on purpose. The configs share no plugin state, so
a plugin cached under one says nothing about a symlink under another — asked globally the
check would flag a hand-placed `~/.claude/skills/<name>` because an unrelated plugin in a
*different* config happens to ship a skill of that name.

A plugin root inside the canonical repo is **source, not a second install**, so a link
pointing into a checkout is one copy and is never reported. That is what keeps this repo's
own `.claude/skills/prd-workflow` self-hosting link quiet.

**The scan announces what it walked**, one line per config directory, whether or not it
found anything:

```
INFO      double-load scan: ~/.claude/skills — 13 entries, 13 checked (skills: 11, skills-dir plugin roots: 2)
INFO      double-load scan: ~/.claude-schmiede/skills — 8 entries, 7 checked (skills: 7; skipped _shared)
INFO      double-load scan: ~/.claude-foo has no skills/ — nothing hand-placed there
```

Read the counts. `entries` is what `ls` would show, so it cross-checks directly; a directory
missing from the list, or a count that does not match, means the scan skipped input — and a
checker that skipped its input reads exactly like a clean one. That is the whole reason the
announcement exists. It runs before the layout section, so it still reports for a repo that
has no `.claude/` at all. `--quiet` suppresses it along with every other `INFO`.

Interpretation is yours, not the script's. In particular: a `FORK` is a decision, not a
delete. Someone edited that copy for a reason and the diff against canonical may contain
work worth back-porting. Report it, show the diff, and let the human decide — replacing a
fork with a symlink silently destroys whatever was in it.

---

## Edge cases

- **Asked to install the skills themselves** → not this skill's job any more. Name the
  marketplace or symlink route and stop.
- **Adapter exists but predates the bundle** → gap-fill the missing sections; leave
  everything else alone, including sections the bundle doesn't require.
- **Adapter-free bundle** → no `.claude/project/`, no interview, no questions. The gate
  offer is the only thing left, and it is optional.
- **`doctor` finds a fork** → do not resolve it as part of a bootstrap. Stop, show the
  diff, hand it back.
- **No `gh` remote** → the *GitHub* workflow bundles are unusable without one. Say so
  rather than filling `## Repo` with a guess. On `ado-workflow` it is expected, not a
  finding: that project's tracker facts come from the interview.
- **Existing adapter, other tracker** → stop. Never rewrite the `Tracker:` line and never
  delete a sub-section from a filled adapter; see step 3a.
- **The project is the canonical repo** → refuse.
- **Target has no `.claude/` at all** → normal; that is a fresh bootstrap.
