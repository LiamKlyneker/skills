#!/usr/bin/env bash
#
# Place the fixture workspace, its node_modules (for an offline `pnpm test` /
# `pnpm ts-lint`), the frozen issue and the fidelity-ledger contract in the run's
# working directory.
#
# `scaffold-fixture.sh` places only tracked files at HEAD — `node_modules` is
# untracked and pnpm's links inside it are relative, so it has to be copied in
# separately, from the same sibling checkout, at the same relative depth
# (workspace root and `apps/consumer`) the fixture repo has them at. `cp -a`
# preserves those links as relative symlinks that still resolve once both trees
# land at the matching depth under `$PWD` — measured at 7.4s for both dirs
# (183MB root + 44KB consumer) on the machine this case was authored on.
#
# `fidelity-ledger.md` is the contract `work-on-task` reaches for as
# `../_shared/…`; placed here for the same reason `to-task-ledger-verbatim`
# places it — see that case's scaffold.sh for the read-scope explanation.
#
# `git archive` strips `.git`, so the placed tree starts with no repository — and
# `work-on-task` ends on a commit. `git init` plus one fixture commit gives the run
# something to branch its own commit from, the way a real checked-out repo would;
# that fixture commit runs through this script, never through the agent, so a
# `tool_used` grader on the run's own `git commit` call never double-counts it.
# `node_modules` is gitignored before that commit so the fixture history and every
# `git status`/`git diff` the run runs afterward stay small.
#
# The runner discards this script's exit status, so everything it does is logged
# to `scaffold.log` beside the workspace and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

"$case_dir/../scaffold-fixture.sh" --dest "$PWD" || exit 1

# `/issue.md`, `/fidelity-ledger.md` and `capture/brief.md` are evaluation inputs, not
# app source — the issue itself says the brief is "local file; not committed", and the
# other two are this case's stand-ins for a `gh issue view` and the `../_shared/` symlink.
# Ignoring them keeps an unthinking `git add -A` in the run's own commit from sweeping
# scaffold artifacts into it.
printf 'node_modules/\n/issue.md\n/fidelity-ledger.md\napps/consumer/capture/brief.md\n' > "$PWD/.gitignore" || exit 1
git -C "$PWD" init -q || exit 1
git -C "$PWD" config user.email "fixture@example.invalid" || exit 1
git -C "$PWD" config user.name "fixture" || exit 1
git -C "$PWD" add -A || exit 1
git -C "$PWD" commit -q -m "fixture: scaffold snapshot" || exit 1

# Same sibling scaffold-fixture.sh resolves by default (repo-root/../skills-fixture),
# recomputed here because node_modules is untracked and git archive never places it.
sibling="$case_dir/../../../../../skills-fixture"
if [ -d "$sibling/node_modules" ]; then
  cp -a "$sibling/node_modules" "$PWD/node_modules" || exit 1
fi
if [ -d "$sibling/apps/consumer/node_modules" ]; then
  mkdir -p "$PWD/apps/consumer" || exit 1
  cp -a "$sibling/apps/consumer/node_modules" "$PWD/apps/consumer/node_modules" || exit 1
fi
# packages/ds is a workspace member too — its own node_modules holds the symlinks tsup
# needs to build it (react, cmdk, @radix-ui/react-popover, clsx, tailwind-merge, …).
if [ -d "$sibling/packages/ds/node_modules" ]; then
  mkdir -p "$PWD/packages/ds" || exit 1
  cp -a "$sibling/packages/ds/node_modules" "$PWD/packages/ds/node_modules" || exit 1
fi

cp "$case_dir/../fixtures/issue.md" "$PWD/issue.md" || exit 1
cp "$case_dir/../../skills/_shared/fidelity-ledger.md" "$PWD/fidelity-ledger.md" || exit 1

# The evidence gate (fidelity-ledger.md §6) reads the brief's full ledger before any code —
# the issue carries the same rows, but the gate names the brief as the source to catch a
# column the issue dropped. Same placement `to-task-ledger-verbatim` uses.
mkdir -p "$PWD/apps/consumer/capture" || exit 1
cp "$case_dir/../fixtures/brief.md" "$PWD/apps/consumer/capture/brief.md" || exit 1

set +x
echo "scaffold complete"
