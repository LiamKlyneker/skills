#!/usr/bin/env bash
#
# Place this case's hand-written stub project and the shared references `to-spec` reads in the
# run's working directory, as a git repository with one fixture commit.
#
# `cp -R fixture/.` copies the dotfile tree too, which puts `.claude/project/adapter.md` at
# the run's root. The shared files are ones the skill reaches as `../_shared/…`; a run's read
# scope stops at the plugin directory and that symlink points out of it, so they are placed
# here, and ignored so they stay out of the fixture commit.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
shared="$case_dir/../../skills/_shared"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1
for f in fidelity-ledger.md ado-workitem-authoring.md final-prints.md; do
  cp "$shared/$f" "$PWD/$f" || exit 1
done

printf '/spec.md\n/fidelity-ledger.md\n/ado-workitem-authoring.md\n/final-prints.md\n/scaffold.log\n' > "$PWD/.gitignore" || exit 1
git -C "$PWD" init -q || exit 1
git -C "$PWD" config user.email "fixture@example.invalid" || exit 1
git -C "$PWD" config user.name "fixture" || exit 1
git -C "$PWD" add -A || exit 1
git -C "$PWD" commit -q -m "fixture: scaffold snapshot" || exit 1

set +x
echo "scaffold complete"
