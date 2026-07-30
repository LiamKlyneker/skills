# QA — PRD #52: extract the `lk` plugin, decouple the grills, version the marketplace

Run this start to finish on `prd/52-extract-lk-plugin-and-version-marketplace` before merging.
Verify ladder L5. Nine of ten children landed on this branch; **#61 is deliberately open** and is
the post-merge cutover.

PR #63. Commits, in order:

```
51f6731  Bring README and INSTALL to the packaged state (#60)
70a8d10  Correct ADR 0003's account of the pre-#54 invocation state (#59)
669ab44  Record the reversed and new decisions as ADRs (#59)
05ca41c  Drop qa-prd-log, triage-prd and install-skills to user-invoked (#54)
42ef0c6  Fail CI when a plugin changes without a version bump (#58)
868b5b1  Version all five plugins and backfill catalog metadata (#57)
8c00827  Give `grill` its own bundle and stop the workflow bundles claiming `## Sources of truth` (#56)
6a35610  Package `install-skills` as its own plugin, keeping `../install/…` resolving (#53)
139f4f9  Decouple the grills from the workflow plugins (#55)
ad3b3fe  Create the `lk` plugin and move the seven personal skills into it (#62)
```

---

## Read this before you start

**Three things will look broken and are not.** Do not file them.

1. **All fifteen plain-skill symlinks are dangling**, in all three config dirs. A symlink points
   at a *working-tree path*, so #62 and #53 broke every one the moment they moved the
   directories — no merge or install involved. `~/.claude` 8, `~/.claude-teamsnap` 3,
   `~/.claude-schmiede` 4. This is real and it means **`~/.claude-teamsnap` and
   `~/.claude-schmiede` have lost `deep-grill`, `how-i-write` and `pinpoint` right now.** #61
   fixes it by installing the plugins. Check with:

   ```bash
   for c in ~/.claude ~/.claude-teamsnap ~/.claude-schmiede; do
     for l in "$c"/skills/*; do t=$(readlink "$l" 2>/dev/null)
       [ -n "$t" ] && [ ! -e "$t" ] && echo "DANGLING: $l -> $t"; done; done
   ```

2. **`docs/estate-inventory.md` disagrees with `README.md` and `INSTALL.md`.** Deliberate — the
   inventory records *live wiring*, which does not change until #61, and its own rule is that it
   changes in the same commit as the wiring.

3. **`doctor` reports seven double-loads under `~/.claude`.** They are the dev installs
   coexisting with those dangling links. `INFO`, not a problem, and the run still ends
   `clean — 0 problems`. **See the known defect at the bottom** — `doctor` cannot currently tell a
   live double-load from a dead link.

**The environment this branch left live**, deliberately, so you can exercise things:

- marketplace `liamklyneker-dev` → `/Users/klyneker/liam-klyneker/skills`
- `lk@liamklyneker-dev` `1.0.0` and `install-skills@liamklyneker-dev` `1.0.0`, both **local**
  scope in this repo (gitignored `.claude/settings.local.json`)

**#61 tears all of that down.** Use `--scope local` for any dev install you add — project scope
writes an untracked, *non*-gitignored `.claude/settings.json` naming the dev marketplace
(`INSTALL.md` Trap 4).

**The single most important habit for this whole document**: after any edit to a skill, template
or manifest, **`uninstall --scope local` then `install`** before probing. Plain `install` at an
unchanged version is a silent no-op — it prints `✔ already installed` and copies nothing. A probe
against a stale cache will happily "confirm" the old behaviour. This bit the run twice.

---

## 0. Mechanical floor — run this first

```bash
cd /Users/klyneker/liam-klyneker/skills
python3 .github/scripts/validate_skills.py --base origin/main
bash plugins/install-skills/skills/install-skills/scripts/doctor.sh --repo . --quiet
for p in plugins/prd-workflow plugins/figma-tools plugins/ado-workflow plugins/lk plugins/install-skills .; do
  claude plugin validate --strict "$p"; done
```

Expect: validator `✓ … all valid` with `5 exempt`; doctor `clean — 0 problems`; six
`✔ Validation passed` with **zero** warnings.

---

## #62 — the `lk` plugin, and `grill-me` → `grill`

**What shipped.** `plugins/lk/` with seven skills: `grill` (renamed), `deep-grill`, `pinpoint`,
`how-i-write`, `qa-prd-log`, `triage-prd`, `scoped-context`.

**How to exercise it.** In this repo, fresh session: type `/lk:grill` and confirm it resolves.

**Edge case.** The PRD claimed a bare `/grill` would be "unreachable from any plugin". **Verified
false** — the platform resolves an unambiguous bare name *to* the namespaced skill; bare
`/deep-grill` resolved and echoed back as `/lk:deep-grill`, while `/grill-me` and `/nonsense-xyz`
both returned `Unknown command`. No decision changed, and ADR 0002 records it as corrected. Don't
restate the unreachability claim anywhere.

---

## #55 — grills decoupled from the workflow plugins

**What shipped.** Four prose edits under the rule *a skill names another skill only where output
would be wrong without it*: `to-spec`'s abort message, `to-prd`'s `## Data & Access`,
`plugins/prd-workflow/README.md`, `_shared/ui-manifests.md`.

**How to exercise it.**

1. Read `to-spec`'s new abort message cold, as someone who has never used this repo:
   *"No grill discussion detected. This skill publishes a grill that already happened — it does
   not run one. Have the design/engineering interview for the work item first, then invoke this
   skill again."* Does it say what is missing and what to do, without naming a command you may
   not have? That is the whole point.
2. Read `plugins/prd-workflow/skills/to-prd/SKILL.md`'s `## Data & Access` preamble and confirm it
   still conveys the manifest's shape (one row per operation) **and** the trap it catches (a new
   operation on an already-used store). Losing the attribution must not have cost the substance.
3. `grep -rn "/grill-me\|grill-me>" plugins/ _shared/` → must be empty.
4. `grep -rin "grill" plugins/` and skim. The ~15 common-noun uses ("the grill", "this grill
   produced") must all still be there. A sharp drop means the sweep went too far.

**Edge case.** The issue's literal AC (`grep -rn "grill-me\|deep-grill" plugins/ _shared/` returns
nothing) is **unsatisfiable by design** — #62 made `deep-grill` a path component and
`plugins/lk/README.md` documents the rename on purpose. Use the invocation-scoped grep above.

**Cosmetic, not worth a commit on its own:** `install/bundles.md`'s `ado-workflow` paragraph has
one over-long line from a rewrap (`…auto-close setting (the pull request's completion options
transition`). Tidy it next time that file is open.

---

## #53 — `install-skills` as its own plugin

**What shipped.** `plugins/install-skills/`, with the skill moved by `git mv` (exec bit preserved,
same blob SHA), and the load-bearing fix: `plugins/install-skills/skills/install ->
../../../install`, so all seven `../install/…` references stay byte-identical.

**How to exercise it.** The decisive test is **not** that the skill loads — it is that it reads
its templates **from the installed copy**.

```bash
# 1. refresh the cache properly
claude plugin uninstall install-skills --scope local
claude plugin install install-skills@liamklyneker-dev --scope local

# 2. did the symlinked dirs arrive DEREFERENCED as real directories?
ls -la ~/.claude/plugins/cache/liamklyneker-dev/install-skills/1.0.0/skills
#    _shared and install must be  drwx…  NOT  lrwx…  and not dangling

# 3. can the cache copy reach its templates?
cd ~/.claude/plugins/cache/liamklyneker-dev/install-skills/1.0.0/skills/install-skills
ls ../install/bundles.md ../install/adapter.template.md ../install/gates/

# 4. doctor FROM THE CACHE COPY, with --bundle (the flag that actually reads bundles.md)
bash scripts/doctor.sh --repo /Users/klyneker/liam-klyneker/skills --bundle prd-workflow
```

A `BUNDLE` error at step 4 means the symlink did not survive install — the silent failure this
issue exists to prevent. A bare `doctor` run never touches `install/`, so it proves less than it
looks like.

Then, in a **fresh** session in this repo, confirm `/install-skills:install-skills` resolves.

**Known defect, not fixed, deliberately.** `doctor.sh` derives
`canonical="$(cd "$script_dir/../.." && pwd -P)"`. That used to reach the repo root; it now
reaches `plugins/install-skills/skills`, which is exactly where the two symlinks sit — so every
template lookup still resolves, in the working tree *and* in a cache copy. But `$canonical` also
backs the FORK check at `doctor.sh:344` (`[ -d "$canonical/$name" ]`), which used to mean "a
top-level plain skill of this name exists" and now means something narrower. The
`plugin_provides` branch below it still catches shadowing, so nothing goes unreported. Reaching
back to the repo root would work here and produce garbage from a cache copy — the exact failure
class this issue exists to avoid. **Wants its own issue after merge**, along with `--help`'s
description of `--canonical` as "path to the canonical skills repo", which is no longer literally
true. To sanity-check the FORK path: drop a real directory named after a plugin-provided skill
into a scratch repo's `.claude/skills/` and confirm `FORK` still fires.

---

## #56 — the `grill` bundle

**What shipped.** A `grill` bundle owning `## Sources of truth`; the section removed from the
`prd-workflow` and `ado-workflow` bundles along with both apologetic paragraphs; `prd-qa` keeps
it. `grill` is the first bundle that is tracker-free but **not** adapter-free.

**How to exercise it — the interview is the test, not the file.** Reinstall first (see the habit
above), then against three throwaway repos (`git init`, one commit):

1. `/install-skills:install-skills install prd-workflow` → you must **never** be asked for a
   project explorer agent, a contract-boundary agent, or an access-policy source.
2. `install grill` → those three must be the **only** questions. Then open the created
   `.claude/project/adapter.md` and confirm **no `Tracker:` line** and **both** `### GitHub` and
   `### Azure DevOps` sub-sections still present.
3. In that same repo, `install ado-workflow` → it must **gap-fill and ask** which tracker, not
   stop on a contradiction and not read the absent line as `github`.
4. `install prd-qa` → `## Sources of truth` must **still** be asked for. Silently losing it would
   leave `triage-prd` with no explorer agents and no cross-repo routing.

Then confirm this repo's own `.claude/project/adapter.md` `## Sources of truth (recon + hard
gates)` still carries all three `None` bullets **plus** the two external sources (the three config
dirs; the plugin CLI). Only the heading's parenthetical was meant to move.

**Mechanical rung anyone can rerun:**

```bash
D=plugins/install-skills/skills/install-skills/scripts/doctor.sh
for b in prd-workflow ado-workflow prd-qa grill figma-tools; do bash $D --repo . --bundle $b --quiet; done
bash $D --repo . --bundle nonesuch --quiet    # must FAIL, exit 1 — proves a pass isn't a no-op
```

**Edge case.** Expect `UNFILLED` placeholder noise from the doctor run that ends `install grill` —
placeholders in the sections that bundle never asked about. `prd-qa` has had the identical
property all along; doctor's placeholder check is whole-file and bundle-blind. Not a regression.

---

## #57 — five versioned plugins

**What shipped.** `version: 1.0.0` on all five manifests, mirrored into all five catalog entries,
plus `keywords` and `category` on each.

**How to exercise it.**

```bash
for p in plugins/prd-workflow plugins/figma-tools plugins/ado-workflow plugins/lk plugins/install-skills; do
  claude plugin tag --dry-run "$p"; done
```

Five `✔ Dry run — would create tag <name>--v1.0.0`, each naming the catalog index it matched.
**`--dry-run` only. No tag exists and none should** — `git tag` is empty; tagging a release is not
part of this PRD.

Then `claude plugin list`. **This will look like a gap and is not one**:
`figma-tools@liamklyneker` and `prd-workflow@liamklyneker` still report `81af34d0d5e1`, because
those are cache copies pinned to an earlier commit and no reinstall was run (#61's job). Meanwhile
`prd-workflow@skills-dir` — the self-hosting symlink, reading live off the working tree — already
reports `1.0.0`. That contrast is the cleanest proof the version write took effect.

**Edge case worth doing once, because it proves the guard fires:** bump
`plugins/lk/.claude-plugin/plugin.json` to `1.0.1` without touching the catalog, run
`claude plugin tag --dry-run plugins/lk`, and confirm:

```
✘ Version mismatch: plugin.json says "1.0.1" but .claude-plugin/marketplace.json
  plugins[3].version says "1.0.0". plugin.json wins at install time…
```

Then revert. (`git checkout -- plugins/lk/.claude-plugin/plugin.json`.)

---

## #58 — bump-or-fail, the load-bearing half

**What shipped.** `check_version_bumps()` in `.github/scripts/validate_skills.py`, standard
library only; `fetch-depth: 0` and `VALIDATE_BASE_REF` in the workflow; and both now-false adapter
passages **rewritten, not deleted**.

**How to exercise it — prove it FAILS, not that it passes.** A bump check that never fires is
indistinguishable from no check, and it is the entire justification for adding versions.

```bash
python3 .github/scripts/validate_skills.py --base HEAD          # ✓ 5 unchanged, exit 0
printf '\n<!-- probe -->\n' >> plugins/lk/README.md
python3 .github/scripts/validate_skills.py --base HEAD          # ✗ exit 1, names lk, 1.0.0, the file
# now bump ONLY the manifest to 1.0.1 and re-run  → ✗ catalog-mismatch error
# mirror 1.0.1 into .claude-plugin/marketplace.json and re-run → ✓ "1 bumped (lk 1.0.0→1.0.1)"
git checkout -- plugins/lk/                                     # revert all of it
python3 .github/scripts/validate_skills.py                      # ⊘ skipped — no base ref, exit 0
```

The last line matters: the skip must be **visible in the log**, not a silent pass. Confirm the
same on the real `push: [main]` run after merge.

**CI posture to re-read before merging** (`.github/workflows/validate.yml`): SHA pin
`actions/checkout@3d3c42e5…` with its `# v7.0.1` comment, `permissions: contents: read`,
`persist-credentials: false`, trigger `pull_request` — **never** `pull_request_target`. The first
CI run on PR #63 is itself the first test of `fetch-depth: 0`; history is 117 KiB / 80 commits, so
expect no measurable change.

**⚠ The one decision waiting on you.** A change under `_shared/` or `install/` counts as changing
**every** plugin whose `skills/` symlinks it — because install dereferences the link into each
cache copy. So **one shared-doc edit demands five version bumps.** Demonstrated:

```bash
printf '\n' >> _shared/ui-manifests.md
python3 .github/scripts/validate_skills.py --base HEAD
#  ✗ 4 problems: prd-workflow, figma-tools, ado-workflow, install-skills each
#    "changed since … but version is still 1.0.0 … (changed: _shared/ui-manifests.md)"
git checkout -- _shared/ui-manifests.md
```

Defensible — silent staleness is unrecoverable, tedium is not — and the message names the shared
file so "why is `prd-workflow` changed?" answers itself. But this repo edits `_shared` often, and
#55 on this very branch did. **If you want it scoped differently, the change is confined to
`plugin_pathspecs()` plus one bullet in the adapter's `## Repo discipline`.** Settle it before
merge; it is much cheaper now than after the third `_shared` edit.

**Read the two rewritten adapter passages cold** and check the *why* survives — `## Commands`
should explain why the row was ever plain `validate` and that zero warnings is now the bar;
`## Repo discipline` should explain why omitting `version` was once correct and what replaced it.
If either reads as a bare new rule, the next reader restores the old one from history.

---

## #54 — the invocation policy

**What shipped.** `qa-prd-log`, `triage-prd` and `install-skills` carry
`disable-model-invocation: true`, and their descriptions dropped the trigger phrasing in favour of
naming what to type.

**How to exercise it.** Reinstall both plugins first (frontmatter changes need it), then in a
**fresh** session:

1. Type `/lk:qa-prd-log`, `/lk:triage-prd`, `/install-skills:install-skills` — **each must
   resolve.** This half was *not* verified during the run and is the reason this section exists:
   testing it headlessly would mean actually invoking skills that post PR comments, file issues,
   or write an adapter. `disable-model-invocation` is supposed to hide a skill from the model
   while leaving the slash command intact, so **a regression where it hides both would look
   exactly like success** in the probe below.
2. Then, *without typing any of them*, say each of these and confirm none auto-fires:
   - "found a bug, let me log it against this PR"
   - "can you triage the QA comments on this PRD's PR"
   - "the adapter looks half-filled, can you fix the skills wiring"
3. **The control that matters most:** ask for a Slack message draft, naming no skill. `how-i-write`
   must still load and the response must read in your voice. This is the one that would be
   silently wrong if the flag had been applied too broadly.

**Already measured, for reference.** A fresh session asked to list every skill it can invoke
matching those names returned `lk:how-i-write` and `lk:pinpoint` and said the other three were not
in its list — where the same probe before #54 had returned `install-skills:install-skills`.

**Note.** `/context` in a *long-running* session will still show the pre-change list; the loaded
skill set is snapshotted at session start. Always use a fresh session for this check.

---

## #59 — the ADRs

**What shipped.** `docs/adr/` with a README and four records: 0001 the versioning reversal, 0002
`lk`, 0003 the invocation policy, 0004 the `_shared/` standing difference plus the hard/soft
dependency rule.

**How to exercise it — this is a read-review.**

1. Read **ADR 0001 as the person who would re-reverse it.** The test: the omit-`version` call must
   read as *correct and well-reasoned*, and the reversal as a change of context (a public catalog)
   plus a new mitigation (the gate) — **not** as a correction of a mistake. If it reads as "they
   got it wrong", it has failed.
2. Check 0001's operational conclusion survives skimming: **never drop a `version` to silence a
   bump failure**, because that drops the check with it. That is the one sentence preventing the
   cheap wrong fix.
3. **Reproduce the invocation table in 0003 with a grep rather than reading it** — this is the
   part of the record most likely to be written from memory, and the first draft got the pre-PRD
   set wrong by two:

   ```bash
   for f in plugins/*/skills/*/SKILL.md; do
     grep -H -oE "disable-model-invocation: true|user-invocable: false" $f; done
   ```

   Expect **6 + 1 across 18 skills**: `grill`, `deep-grill`, `figma-to-spec`, `qa-prd-log`,
   `triage-prd`, `install-skills` on the flag, and `scoped-context` on the inverse
   `user-invocable: false`.
4. Confirm 0003 still says the drop test covers **four of six** user-invoked skills. `grill` and
   `deep-grill` write nothing anywhere, so nothing in the stated test explains their flag — what
   does is that they *seize the conversation*. The ADR names that gap and deliberately does **not**
   patch the rule. If someone later adds the third clause, that sentence is the tripwire saying a
   new record is due rather than an edit here.
5. Confirm 0002 does **not** anywhere assert that a bare `/grill` is unreachable — it must appear
   only as the corrected claim, with the probe.

**Edge case.** `docs/adr/README.md` is the template every future record copies. Two clauses are
hard to change later and worth agreeing to now: numbers are **never reused and gaps never
backfilled**, and superseding is **append-only** — the superseded body stays wrong on purpose.

---

## #60 — README, INSTALL, and the front doors

**What shipped.** `README.md`, `INSTALL.md`, `install/README.md`, plus the cache-key and
three-plugins claims in `CLAUDE.md` and the adapter's `## App facts`.

**How to exercise it.**

1. Read `README.md` top to bottom **as a stranger**, then `INSTALL.md`. The test: could you get
   all five plugins onto a machine from those two alone? Specifically — can you answer *which
   bundle do I install for the grills* without opening `bundles.md`?
2. Read `install/README.md` too; it was absorbed into this issue because nothing else owned it.
3. **Click every link.** The anchor to watch is **Trap 2** — its heading was renamed to
   `## Trap 2: version is the install cache key, and a forgotten bump is silent`, and **two**
   places link to it (§4's opening, §5's "Refreshing after an edit"). Also click "the estate
   record", which should land on `## The estate today` — now a pointer rather than a duplicated
   table.
4. **Read the rewritten Trap 2 as someone who might restore the old rule.** It should read as
   "the mechanism is real, the response changed" — not "that was a mistake". Same test as ADR
   0001, and the two should agree.
5. Confirm neither document claims this repo ships plain skills, **and** that neither deleted the
   symlink *route*: §4 live authoring must still describe it, and README's two-delivery-routes
   paragraph must still name it. The claim goes; the mechanism stays.

**Flagged, unowned, for a follow-up after merge:** `README.md`'s `## Agents` table omits
`ado-workflow:spec-worker` while reading as an inventory. Pre-dates this PRD.

---

## Known defects and follow-ups this branch surfaced

None of these block the merge. All want issues afterwards.

1. **`doctor.sh` reports a dangling symlink as a double-load.** It matches the link's *name*
   against what the plugins provide without checking that the link *resolves*. Right now it calls
   all eight dead links under `~/.claude` "loads twice". **This lands squarely on #61**, whose
   `## Verify` calls double-load detection "the check that matters here" — it currently cannot
   tell a live double-load from a dead link, which is the exact distinction the cutover turns on.
   Not cosmetic. Fix it in #61 or file it before the cutover runs.
2. **`doctor.sh`'s `$canonical` narrowing** — see #53 above.
3. **`plugins/lk/skills/deep-grill/SKILL.md`** ends its description `Invoke /deep-grill.` — the
   bare name, where `grill` says `/lk:grill`. Both `lk` skills since #62. **No child of #52 owns
   it**; #54's AC froze both grills.
4. **`README.md`'s `## Agents` table** omits `ado-workflow:spec-worker`.
5. **`plugins/ado-workflow/skills/references/`** is a directory under `skills/` carrying no
   `SKILL.md`. Harmless, but it makes `ls`-based skill counts wrong — count `SKILL.md` files
   instead. (It is why one count in this run came out 10 instead of 9.)

---

## After you merge

Do **not** merge until the above passes. Then #61 runs, and its ordering is not optional. Its own
body and its two comments have the detail; the short version:

1. `/plugin marketplace update liamklyneker` in each config — a registered marketplace caches its
   catalog, so a config that has had `liamklyneker` since before `lk` existed will not find it.
2. Install `lk` and `install-skills` at the scope that config takes: `~/.claude` → **project**,
   `~/.claude-teamsnap` → **local** (project scope would write a committed `.claude/settings.json`
   into an employer's repo), `~/.claude-schmiede` → **user**.
3. Verify in a **fresh** session per config, checking *which name it resolved under*.
4. Only then remove that config's symlinks. Remove the `liamklyneker-dev` marketplace and anything
   installed from it. Clean the stale SHA-keyed cache directories.
5. `.claude/skills/lk -> ../../plugins/lk` in this repo — and it must **never** coexist with an
   installed `lk@liamklyneker` here, or every skill loads twice.
6. Rewrite `docs/estate-inventory.md` from the **live directories**, not from intent.

Note that #61's "the window where both exist is a double-load" reasoning is weaker than written,
because the fifteen links are already dead. The *other* window — after the merge, before the
install, when the skill is simply gone — is the real one, and two configs are in it now.
