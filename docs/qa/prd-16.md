# QA — PRD #16: plugins + marketplace

Manual pass for [PR #27](https://github.com/LiamKlyneker/skills/pull/27), branch
`prd/16-publish-skills-repo-as-plugins`. Run it start to finish before merging.

**This pass covers six of the PRD's nine children** — #18, #19, #20, #21, #22, #23.
The remaining three are deliberately not here:

| Issue | Why it is not in this pass |
|---|---|
| #24 cutover | Its committed project settings need a **GitHub** marketplace source, and a GitHub source clones the **default branch**. The catalog only exists on this branch, so #24 cannot be done correctly until this PR merges. |
| #25 install guide | Documents commands that only work once #24 has run. |
| #26 contract | Deletes the compat shims, which must outlive the cutover. |

So the merge is deliberate, not premature: it unblocks the remaining three, which
land in a follow-up PR. **PRD #16 stays open until #26 deletes the shims.**

Config dir throughout is `~/.claude` (personal) unless stated. Working directory is
this repo unless stated.

---

## Before you start

```bash
git checkout prd/16-publish-skills-repo-as-plugins
bash -n install-skills/scripts/doctor.sh && bash install-skills/scripts/doctor.sh --repo .
claude plugin validate plugins/prd-workflow
claude plugin validate plugins/figma-tools
claude plugin validate .
```

Expect `clean — 0 problems` from doctor, and each `validate` to pass **with exactly
one warning per plugin manifest** — the deliberately omitted `version`. A *second*
warning is a real failure, not noise.

> `--strict` fails on all three by design. Omitting `version` makes the git commit
> the install cache key; setting one means a forgotten bump silently serves stale
> installs. The project's check is plain `validate` — see the adapter's `## Commands`.

---

## #18 — `prd-workflow` plugin (expand)

**What shipped.** The five PRD/issue skills and the `prd-worker` agent moved into
`plugins/prd-workflow/`. The five top-level directory names survive as compat
symlinks, so all 22 consumer links across four repos keep resolving with no
coordinated update. Shared reference sits at `skills/_shared -> ../../../_shared`.

**Exercise it.**

1. In a fresh session here, run `/to-prd` and `/next-prd-issue`. Both must load and
   behave exactly as before — the shims mean invocation names have not changed yet.
   A skill that cannot find itself shows up as the command not existing.
2. Let a skill actually **read a shared file** during the run — any PRD-eligibility
   step does. It must resolve `../_shared/prd-eligibility.md` without complaint.
   This is the two-hop symlink path and the highest-risk thing in the change.
3. In `~/creative-ghost/neonplace`, confirm `prd-worker` still resolves as an agent
   type. Same in `neonplace-ios`. **Check it by type** — a missing agent degrades
   silently to `general-purpose` rather than erroring, which is how `neonplace` ran
   bare workers for weeks.

**Edge cases.**

- The nested shim `skills/work-on-prd/agents/prd-worker.md` is the one path a casual
  look misses. Only `neonplace` and `neonplace-ios` use it, so a break there is
  invisible from this repo.
- The plugin is **not** registered in this repo's own `.claude/skills/`, on purpose.
  Adding it while the shims exist would double-register all five skills.
- `CLAUDE.md`, `README.md` and the adapter still describe the pre-plugin layout.
  Correct-but-stale, everything resolves; #25 owns fixing them.

---

## #19 — `doctor`: stop parsing adapter prose as a gate pointer

**What shipped.** The `POINTER` check is scoped to the adapter's `## Project gates`
table instead of the whole file, and strips real `../`-relative paths before matching
`./`-relative ones.

**Exercise it — both directions. A check that goes quiet on both is worse than the
original bug.**

1. Put a real path like `` `../_shared/prd-eligibility.md` `` in adapter prose
   **outside** `## Project gates`. Run `/install-skills doctor`. Expect **no**
   `POINTER` line.
2. Add a row to `## Project gates` naming a file you never created:
   `` | `test-gate` | `./test-gate.md` | always | ``. Re-run. Expect `POINTER` to
   fire and name it.
3. Undo both.

**Edge case.** The fix uses substring-stripping rather than a lookbehind regex,
because BSD `grep` on macOS has no `-P`. Keep that in mind if it is ever rewritten.

---

## #20 — `figma-tools` plugin (expand)

**What shipped.** `figma-to-spec` and `figma-region-extractor` moved into
`plugins/figma-tools/`. A top-level `figma-to-spec` shim keeps the three config-dir
links resolving.

**The plugin is named `figma-tools`, not `figma`.** `figma` is already taken by
`figma@claude-plugins-official` (Anthropic's own integration, enabled in `~/.claude`).
The clash is not marketplace-only — linking a second `figma` into a config's
`skills/` reports `Not loaded — the name "figma" is already taken`, which breaks the
skills-dir mode this repo depends on for live authoring.

**Exercise it.**

1. Personal-config session: `figma-to-spec` still appears and is invocable.
2. Schmiede-config session (`cd` into a Schmiede project so `$PWD` selects
   `~/.claude-schmiede`): same check.
3. From inside a `figma-to-spec` run, open `references/phases.md` and
   `references/catalog.md`.
4. Confirm `figma-region-extractor` resolves **by type**. Same silent-degradation
   trap as `prd-worker`.

**Edge cases.**

- Never rename this plugin back to `figma`.
- `figma-component/` and `tokens-init/` are untouched and stay that way until #9 and
  #14 decide what to salvage.

---

## #21 — marketplace catalog + the dereference proof

**What shipped.** `.claude-plugin/marketplace.json` at the repo root, publishing both
plugins under marketplace name **`liamklyneker`**. No `version` keys anywhere.

**The PRD's one unproven assumption is settled: the dereference works.** A symlink
that leaves the *plugin* but stays inside the *marketplace repo* is dereferenced and
copied. In the installed cache, `skills/_shared` is a real directory with four real
files, reachable via the runtime path a skill actually uses, and byte-identical to
canonical (all twelve sha256s matched across canonical and both plugin caches). #16's
escape hatch stays unused.

**Exercise it — do this AFTER merging**, because a GitHub source clones the default
branch and the catalog only reaches `main` on merge.

1. `/plugin marketplace add LiamKlyneker/skills` — confirm it registers as
   **`liamklyneker`** (the name comes from the manifest, not the directory).
2. `/plugin install prd-workflow@liamklyneker`, then restart.
3. Confirm the skills appear namespaced as **`prd-workflow:<skill>`**. This is the
   one piece never observed — the probe was removed before any session picked it up,
   and `plugin details` reporting the right inventory is necessary but not the same
   evidence.
4. Poke the shared reference hardest: run `/prd-workflow:next-prd-issue` (it reads
   `prd-eligibility.md`) from the **installed** copy, not the symlinked one, and
   confirm it does not quietly proceed without the file. A silently missing shared
   file is the exact failure this slice exists to rule out.

**Edge cases.**

- **`uninstall` does not delete the cache.** It orphan-marks it — the directory
  survives with `.orphaned_at` tombstones. Finish any probe with
  `rm -rf ~/.claude/plugins/cache/liamklyneker`.
- **The cache key is the git commit SHA**, so an installed copy pins to *committed*
  HEAD. Uncommitted working-tree edits are invisible to it. Correct behaviour, but it
  will surprise anyone debugging "my edit didn't take".
- Installing while this repo's symlinks are live makes all five workflow skills load
  twice. Expected — `doctor` reports it as `INFO`, not an error. Decide per config
  whether to keep the symlinks or the plugin, not both.
- **`--scope project` is not as contained as it sounds.** It also registers at user
  level and creates a cache dir, and its committed source is an absolute local path —
  which is why #24 needs a GitHub source and therefore needs this merge first.

---

## #22 — narrow `install-skills`; reshape `bundles.md`

**What shipped.** Symlink placement and vendor mode are gone (`references/vendor.md`
deleted, no stamps). What survives: adapter copy, gap-fill interview, gate
registration, `doctor`. `bundles.md` lost its `Skills`/`Agents` lists and keeps the
bundle → adapter-section mapping. The `figma` bundle is now `figma-tools`.

**Exercise it.**

1. `/install-skills doctor` in this repo, and against a wired consumer
   (`--repo ~/creative-ghost/neonplace`). Both work end to end, and the skill must
   **not** offer to place or update anything.
2. `/install-skills install prd-workflow` in a scratch repo with a `gh` remote.
   Expect: repo resolved → adapter template copied → interview → gate offer →
   `doctor`. **It must not create `.claude/skills/`, must not symlink anything, and
   must not mention `--vendor` or an `update` mode.** Asked where skills come from,
   it should name the marketplace and stop.
3. `/install-skills install figma-tools` — note the new name. Expect no interview at
   all beyond the optional `ui-manifests` gate offer. Say **no** first and confirm
   nothing is written; then repeat and say **yes**, and confirm it creates an adapter
   carrying only a filled `## Project gates`, after which `doctor` passes with no
   `POINTER`. That yes-path is new behaviour.
4. Run `/install-skills install prd-workflow` from inside this canonical repo — it
   must **refuse** rather than self-install.

**Edge case.** `install-skills` now describes routes it does not perform. Watch that
it does not "helpfully" fall back to writing symlinks if pushed — that would produce
a half-hand-rolled install `doctor` then reports as `FORK`.

---

## #23 — `doctor`: plugin awareness; drop the vendor-era checks

**What shipped.** `doctor` looks plugins up in four places (installed manifests,
versioned cache dirs, skills-dir plugins, repo-local `plugins/`) across **all three**
config dirs. Plugin-provided skills no longer read as `MISSING`; a real directory
shadowing one still reports `FORK`. All vendor-drift machinery deleted. The
bundle check no longer parses a `Skills` list.

**Exercise it — again, both directions matter.**

1. **Quiet where it should be.** In a repo with no `.claude/skills/` (the normal
   post-cutover shape), run `/install-skills doctor`. Expect `clean — 0 problems` and
   `INFO` lines, not a wall of `MISSING`. If that repo has an adapter, confirm
   `OK adapter present` **still appears** — doctor must keep checking the adapter, not
   skip it because no skills dir exists.
2. **Loud where it should be.** Copy a plugin-provided skill into `.claude/skills/`
   as a real directory. Use **`cp -RL`, not `cp -R`** — `cp -R` on a symlink copies
   the link and you get `DANGLING` instead, which tests nothing. Expect `FORK` naming
   the providing plugin's path. Use a skill with **no** counterpart in this repo
   (e.g. `figma-use` from `figma@claude-plugins-official`), otherwise you are testing
   the old canonical branch rather than the new plugin one.
3. `--bundle prd-workflow`, `--bundle prd-qa`, `--bundle figma-tools` all clean
   against this repo. `--bundle nosuch` must print `BUNDLE`.

**Edge cases.**

- `prd-qa` prints "no plugin named `prd-qa` is reachable" as `INFO`. Correct — that
  bundle ships as plain skills and has no plugin. Not a finding.
- doctor scans all three config dirs because it cannot know which one a session in
  the target repo will use. A plugin installed in only one config still reads as
  reachable. Deliberate.
- The `INFO … loads twice` line is the signal that a cutover is incomplete. It is
  **suppressed by `--quiet`**, so run without it when checking cutover state.

---

## After the pass

- Merge PR #27. The PRD issue stays **open** — `Closes` fires for the six children on
  merge; #24, #25 and #26 continue in a follow-up PR.
- First thing post-merge, do #21 step 1–4 above. That is simultaneously the QA for
  #21 and the prerequisite for #24.
