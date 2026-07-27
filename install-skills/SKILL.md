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

Repo root (`git rev-parse --show-toplevel`), remote (`gh repo view --json nameWithOwner`),
default branch (`gh repo view --json defaultBranchRef`). If the target is not a git repo,
stop and say so — every bundle assumes `gh`.

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

### 4. Interview — infer first, ask for the rest

Read `references/interview.md`. The rule: anything a file already states, read; only
ask for what no file in the repo can answer. Asking for a test command that is sitting
in `package.json` is how an install earns a reputation for being tedious.

Fill only the sections the bundle requires. That list is what keeps the interview finite
and bundle-specific rather than asking every question every time.

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
<canonical>/install-skills/scripts/doctor.sh [--repo <path>] [--bundle <slug>] [--quiet]
```

Deterministic on purpose — every check here is mechanical, and a check that is
paraphrased differently on each run is not a check. Run the script; do not re-implement
its checks by hand or "spot-check" a subset.

| Label | Means |
|---|---|
| `FORK` | a real directory where a symlink belongs, **shadowing a canonical skill of the same name**. A real directory with no canonical counterpart is a skill the project genuinely owns — reported as `INFO`, not a problem |
| `BANNED` | a project-owned `_shared/` — shadows canonical for any copied skill |
| `DANGLING` | a symlink under `.claude/` whose target is gone |
| `HOLE` | an installed skill reads the adapter, and there isn't one |
| `UNFILLED` | the adapter still carries the TEMPLATE marker or template placeholders |
| `POINTER` | the adapter's `## Project gates` table registers a gate whose file does not exist as a sibling of `adapter.md` |
| `SHARED` | a skill reads `../_shared/x.md` that does not resolve from where it sits |
| `MISSING` | a bundle skill reachable neither in the repo nor from a global config dir |

Exit 0 clean · 1 problems · 2 usage error.

The script still carries checks written for the old placement model, and `--bundle` still
reads a manifest field that no longer exists; #23 removes both. Until then, treat a label
not in the table above — and any `--bundle` complaint — as noise from that transition
rather than a finding, and run it without `--bundle`.

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
- **No `gh` remote** → the workflow bundles are unusable without one. Say so rather than
  filling `## Repo` with a guess.
- **The project is the canonical repo** → refuse.
- **Target has no `.claude/` at all** → normal; that is a fresh bootstrap.
