# QA — PRD #16: plugins + marketplace

Manual pass for [PR #28](https://github.com/LiamKlyneker/skills/pull/28), branch
`prd/16-publish-skills-repo-as-plugins`. Run it start to finish before merging.

**All nine children are covered here.** [PR #27](https://github.com/LiamKlyneker/skills/pull/27)
merged six of them — #18, #19, #20, #21, #22, #23 — and their sections stay below as
the record. PR #28 adds the last three on the same branch.

| Issue | Landed in | Why the order |
|---|---|---|
| #24 cutover | #28 | Needed #27 merged first: its committed project settings need a **GitHub** marketplace source, and a GitHub source clones the **default branch**. |
| #25 install guide | #28 | Documents commands that only work once #24 has run. |
| #26 contract | #28 | Deletes the compat shims, which had to outlive the cutover. |

**Merging PR #28 closes PRD #16.** The three `Closes` keywords in its body fire on
merge, and #26 was the last slice the PRD was waiting on.

The estate this pass verifies — which config holds which plain skill, which repo
enables which plugin — is recorded in [`docs/estate-inventory.md`](../estate-inventory.md).

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

## #24 — cutover: repoint three repos and three configs onto the plugins

**What shipped.** Every consumer now gets the workflow from a plugin instead of from
a symlink. All 15 legacy skill links and both `prd-worker` agent links are gone from
`liamklyneker`, `neonplace` and `neonplace-ios`; each of the three enables
`prd-workflow@liamklyneker` in **committed** project settings instead (pushed to
`main` in each — three commits outside this repo). This repo self-hosts via
skills-dir mode: one symlink, `.claude/skills/prd-workflow -> ../../plugins/prd-workflow`,
which `claude plugin list` reports as `prd-workflow@skills-dir · Scope: project` and
which keeps edit-in-place authoring working. `~/.claude` lost its `figma-to-spec`
skill link and its `figma-region-extractor` agent link — `figma-tools@liamklyneker`
is installed user-scope there and provides both.

**Scope changes against the issue body.** Two configs, not three: `~/.claude-schmiede`
is out (it refuses project/local settings writes into a symlinked `.claude`, and it
does not use this workflow). And `doctor` needed a fix to land this — see below.

**Exercise it. Steps 1–3 are the ones nobody has observed yet; do those first.**

1. **`prd-worker` resolves by type where it should.** Fresh session in
   `~/creative-ghost/neonplace`, then `~/creative-ghost/neonplace-ios`, then
   `~/liam-klyneker/liamklyneker`. Spawn a `prd-worker` **by type**. All three now get
   it from the plugin, and none of them has a `.claude/agents/prd-worker.md` any more,
   so this is the whole safety net. **A missing agent degrades silently to
   `general-purpose`** — that is how `neonplace` ran bare workers for weeks — so
   confirm the type resolves rather than assuming a successful run proves it.
2. **`prd-worker` does NOT resolve where it should not.** Same check in
   `~/creative-ghost/reeckon` (no `enabledPlugins`, never wired). It must be absent.
   `claude plugin list` there already reports `prd-workflow@liamklyneker` as
   `✘ disabled`, but that is the setting, not the live agent table. This is the
   direction that actually matters: `prd-worker` commits.
3. **This repo's own loop still works.** Fresh session here; `prd-worker` must resolve
   from `prd-workflow@skills-dir`. This repo also lost its `.claude/agents/prd-worker.md`,
   and it is where the PRD loop runs, so a miss here stalls #25 and #26. If it is
   missing, the one-line rollback is
   `ln -s ../../plugins/prd-workflow/agents/prd-worker.md .claude/agents/prd-worker.md`.
4. **Skills resolve, namespaced.** In each of the three consumer repos, confirm the
   five skills appear as `prd-workflow:<skill>` and that `/prd-workflow:work-on-prd`
   loads. In this repo they come from the skills-dir plugin instead.
5. **Edit-in-place still works.** Edit a line in `plugins/prd-workflow/skills/to-prd/SKILL.md`
   here, start a session **in this repo**, and confirm the edit is live with no
   reinstall. Then confirm it is **not** live in `neonplace` — the marketplace copy is
   pinned to a committed SHA (`ac7a89ab018a`), which is correct and will surprise you
   once.
6. **Nothing project-owned was collateral damage.** `neonplace/.agents/skills/` still
   has `building-luar-ui`, `data-types-colocation`, `triage`, `verify-ui`;
   `neonplace-ios/.agents/agents/` still has `grill-explorer`, `grill-web-explorer`.
7. **TeamSnap config.** Nothing changed there and nothing needed to —
   `prd-workflow@liamklyneker` is installed `local`-scope and enabled from
   `organization-frontend-v2/.claude/settings.local.json` (gitignored, zero git
   footprint). Confirm from a `claude-ts` session that the skills load. The
   `claude plugin` CLI **cannot** check this — it always reads `~/.claude` regardless
   of `CLAUDE_CONFIG_DIR`.

**Edge cases.**

- **`~/.claude-schmiede/skills/figma-to-spec` is a live hazard for #26.** It still
  points at the top-level `figma-to-spec` shim, which #26 deletes. Schmiede was ruled
  out of scope for #24, so it was deliberately left alone rather than broken — but #26
  must either install `figma-tools` there (user scope; project/local writes are
  refused into that symlinked `.claude`) or delete the link, or Schmiede sessions lose
  `figma-to-spec` with a dangling link and no error.
- **`doctor` had to learn skills-dir mode to let this land.** It treated every entry in
  `.claude/skills/` as a skill, so it resolved `../_shared/` from the *plugin root* and
  invented three `SHARED` failures the moment this repo self-hosted via a plugin. It
  now recognises an entry carrying `.claude-plugin/plugin.json` as a plugin root and
  registers the skills one level down at their real paths. Both directions were
  re-checked: a real directory shadowing a plugin-provided skill still reports `FORK`,
  and a dangling link still reports `DANGLING`.
- **Do not add an apostrophe to a `#` comment inside a `$( )` in `doctor.sh`.** macOS
  ships bash 3.2, which does not strip comments before scanning for quotes — one
  apostrophe there is a syntax error reported 100+ lines away. There is a comment in
  the script saying so; keep it.
- **`--scope project` behaved this time.** It wrote `enabledPlugins` only into the
  project's own `.claude/settings.json` and left `~/.claude/settings.json` untouched,
  so "install broadly, enable narrowly" holds. Diff `~/.claude/settings.json` before
  and after if you ever re-run it — #21 found it leaking to user level once.
- `neonplace/.agents/agents/` is now an empty directory. Left in place on purpose: a
  **newly created** agents directory does not register mid-session, so deleting it
  would make a future project-owned agent there harder to add, not easier.
- The three repos' skill links were gitignored in `neonplace` and `neonplace-ios`, so
  only `liamklyneker` shows deleted symlinks in its commit. The other two commits are
  the settings file alone. That is expected, not an incomplete cutover.

---

## #25 — install guide; correct the docs the migration falsified

**What shipped.** A top-level **`INSTALL.md`**: marketplace, per-config install,
per-project enablement, skills-dir live authoring, adapter bootstrap, verify, and
three traps. `install/README.md` narrowed to what a *project* owns and points at it.
`README.md`, `CLAUDE.md`, `.claude/project/adapter.md` and
`install/adapter.template.md` no longer claim one-directory-per-skill or
symlink-per-project delivery. The adapter's `## Commands` gained the
`claude plugin validate` line as a named L2 rung.

**The guide's home was a judgement call.** `install/` is the templates-a-project-fills-in
directory; an estate-wide distribution guide is not a template, so it went top-level
where `README.md` can point at it directly.

**Exercise it — read it cold.** The whole test is following it without consulting
anything else. A step that only makes sense if you already did the migration is the
failure mode.

1. **Traps 1 and 2, hands on.** `CLAUDE_CONFIG_DIR=/tmp/throwaway claude plugin list`
   and `… marketplace list` — both must report `~/.claude`'s inventory and leave the
   throwaway directory empty, matching the transcript in the guide. Then
   `claude plugin validate plugins/prd-workflow` — exactly one warning, the omitted
   `version`.
2. **The parts nobody could verify without an interactive session** (see below) — do
   these in a scratch repo you can throw away:
   - `/plugin marketplace add LiamKlyneker/skills` in a config that does not have it,
     and confirm it registers as **`liamklyneker`**.
   - `/plugin install prd-workflow@liamklyneker`, pick a scope, restart, and confirm
     the skills appear as `prd-workflow:<skill>`.
   - Hand-write `enabledPlugins` into a scratch repo's `.claude/settings.json` and
     confirm a session there sees the plugin while a sibling repo does not.
   - `ln -s` a plugin directory into a scratch `.claude/skills/`, and confirm
     `claude plugin list` reports it as `<name>@skills-dir · ✔ loaded`.
3. **No surviving symlink-delivery claims.** `grep -rn -i symlink --include="*.md" .`
   Every remaining hit should be one of: a plain skill (still symlinked, still true),
   the `skills/_shared` symlink inside a plugin, a compat shim #26 deletes,
   `doctor`'s failure classes, or this QA doc's own history.
4. **Cross-references resolve.** Every relative link in the changed files.

**Edge cases.**

- **Nothing was installed, uninstalled or reconfigured for this issue**, deliberately —
  the estate is in a verified good state that #26 depends on. Every claim in the guide
  is either quoted from a command run read-only against the live estate, or taken from
  the #21/#24 records. Step 2 above is the part that has *not* been walked end to end
  in this pass.
- **The scope rule in the guide contradicts the PRD's "install broadly, enable
  narrowly."** That phrasing was written for `~/.claude`, which is multi-tenant. In a
  single-tenant config (`~/.claude-teamsnap`, `~/.claude-schmiede`) **user scope is the
  narrow option**, and project scope in a client repo writes a committed settings file —
  the exact footprint user story 3 exists to avoid. The guide states tenancy as the rule.
  Read it that way rather than reconciling it with the PRD's sentence.
- **The `--scope project` user-level leak recorded under #21 did not reproduce in #24**
  and is not repeated in the guide. If it ever recurs, the guide is what needs correcting.
- **Trap 3 is new to the documentation** — a repo whose `.claude` is *itself* a symlink
  refuses both project and local scope (`SymlinkWriteRefusedError`). Only user scope
  works there. Do not confuse it with `neonplace`'s shape, which has a real `.claude/`
  with links *inside* it and installs fine.
- `figma-component/references/install.md` still describes the pre-plugin symlink route.
  Deliberately untouched — that skill is deprecated and #9/#14 decide what survives.
  It is linked into no project and cannot be auto-invoked.
- `install/adapter.template.md` was not in #25's file list but carried the same
  falsified claims, and it is the file every *new* project's adapter is copied from.
  Fixed for that reason.

---

## #26 — contract: delete the shims, sweep the leftovers, fix the agent type

**What shipped.** All six top-level compat shims (`to-prd`, `to-issues`, `next-prd-issue`,
`work-on-prd`, `work-on-issue`, `figma-to-spec`) and the nested
`skills/work-on-prd/agents/prd-worker.md` are deleted; `work-on-prd/SKILL.md` now addresses
the agent at its real path, `../../agents/prd-worker.md`. **A defect found at pickup is
fixed in the same slice**: plugin components register **namespaced**, so
`subagent_type: prd-worker` had stopped resolving and both skills were still asking for the
bare name. `prd-workflow:prd-worker` and `figma-tools:figma-region-extractor` are now the
stated primaries. `~/.claude-schmiede/skills/figma-to-spec` was repointed past the shim.
New: [`docs/estate-inventory.md`](../estate-inventory.md).

**Exercise it. Steps 1–3 have never been observed and are the whole point of the pass.**

1. **`prd-worker` resolves by type in marketplace mode.** Fresh session in
   `~/creative-ghost/neonplace`, then `neonplace-ios`, then `~/liam-klyneker/liamklyneker`.
   List the available agent types and read the name — it must be
   **`prd-workflow:prd-worker`**. Skills-dir mode (this repo) is proven; the **cache path is
   not**, and it is a different code path. Same check for
   `figma-tools:figma-region-extractor` under `~/.claude`.
2. **Negative control.** Same check in `~/creative-ghost/reeckon`, which never enabled the
   plugin. `prd-worker` must resolve under **neither** name. This is the direction that
   matters — `prd-worker` commits.
3. **TeamSnap.** A `claude-ts` session in `organization-frontend-v2`: the five skills load as
   `prd-workflow:<skill>`, and `deep-grill` / `how-i-write` / `pinpoint` load as plain skills.
   The `claude plugin` CLI **cannot** inspect that config — this is the only way to know.
4. **The full PRD workflow end to end, on the plugin path only** (the L5 pass this ladder
   asks for once per PRD). Run `/prd-workflow:work-on-prd` on a small real PRD in a consumer
   repo. **Confirm the run announces the namespaced path**, not the detached one — the skill
   now announces which of the three it took, and a detached run is otherwise
   indistinguishable from a real one. A `general-purpose` fallback here means step 1 lied.
5. **Nothing loads where it shouldn't.** `deep-grill`, `how-i-write` and `pinpoint` in all
   three configs; `grill-me`, `scoped-context`, `qa-prd-log`, `triage-prd`, `install-skills`
   **only** under `~/.claude`. Cross-check against `docs/estate-inventory.md` — if a session
   disagrees with that table, the table is what gets corrected.
6. **Schmiede still has `figma-to-spec`.** Session in a Schmiede repo: the skill loads
   (unprefixed — it is on the symlink route, not the plugin route) and can read
   `references/phases.md` and `../_shared/`. Phase 0 must announce the **inline fallback**
   for region agents, because that config has no `figma-tools` plugin and therefore no agent.

**Edge cases.**

- **The two nested agent links were not symmetrical.** `prd-workflow`'s was pure compat and
  is deleted; `figma-tools`' `skills/figma-to-spec/agents/figma-region-extractor.md`
  **stays**, because the skill's own docs address the agent from inside the skill
  (`../agents/…` from `references/`) and those paths must resolve in a cache copy too. Both
  plugin READMEs now say so. Do not "finish the job" by deleting the figma one.
- **Sweep 2's deletions were already done by #24** and were verified as no-ops here: no
  hand-placed agent symlink survives in any config. Nothing was deleted for sweep 2 in this
  slice; the work was the type-name fix.
- **A detached `work-on-prd` run is silent by design.** That is why step 4 checks the
  announcement rather than the outcome. The #25 run took the detached path and looked
  perfectly normal.
- The `doctor` reachability message can name the wrong config (it scans all three and reports
  the first match). Cosmetic, reported, **not** fixed here — it needs its own issue.
- `figma-component/` and `tokens-init/` remain untouched at the top level, deprecated and
  linked nowhere, pending #17.

## After the pass

- PR #27 merged; `Closes` fired for the six children it carried.
- All nine children are now on this branch. Merging PR #28 fires the remaining three
  `Closes` keywords and **closes PRD #16**. Nothing is left after it.
- #21 steps 1–4 were the prerequisite for #24 and are done: the marketplace registers
  as `liamklyneker` and both plugins install from it.
