#!/usr/bin/env bash
#
# Place this case's hand-written stub project, its frozen issue and the fidelity-ledger
# contract in the run's working directory.
#
# The stub is this case directory's own `fixture/`, not the shared fixture repository: a
# micro case needs no pnpm workspace, no `node_modules`, no build and no captures beyond the
# one PNG it ships, so there is nothing for `scaffold-fixture.sh` to place and nothing to
# wait for. `cp -R fixture/.` copies the dotfile tree too, which is what puts
# `.claude/project/adapter.md` and `.claude/briefs/plate-chip.md` at the run's root.
#
# `fidelity-ledger.md` is the contract `work-on-task` reaches for as `../_shared/…`; a run's
# read scope stops at the plugin directory and that symlink points out of it, so the file is
# placed here instead.
#
# `/issue.md` and `/fidelity-ledger.md` are evaluation inputs, not project source. Ignoring
# them keeps them out of the fixture commit, so the run starts on a repository holding the
# stub project alone.
#
# The run is expected to end without a commit of its own — the skill halts on the ledger's
# undecided off-grid fact — but `git init` plus one fixture commit still gives it the branch
# the adapter's `Branch pattern:` row names, cut from a real base, the way a checked-out repo
# would. That fixture commit runs through this script, never through the agent.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1
cp "$case_dir/../../skills/_shared/fidelity-ledger.md" "$PWD/fidelity-ledger.md" || exit 1

printf '/issue.md\n/fidelity-ledger.md\n' > "$PWD/.gitignore" || exit 1
git -C "$PWD" init -q || exit 1
git -C "$PWD" config user.email "fixture@example.invalid" || exit 1
git -C "$PWD" config user.name "fixture" || exit 1
git -C "$PWD" add -A || exit 1
git -C "$PWD" commit -q -m "fixture: scaffold snapshot" || exit 1

set +x
echo "scaffold complete"
