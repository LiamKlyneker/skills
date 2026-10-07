#!/usr/bin/env bash
#
# Place this case's stub project, its local `[SPEC]` file and the shared references
# `to-spec-tasks` reads in the run's working directory.
#
# `cp -R fixture/.` copies the dotfile tree too, which puts `.claude/project/adapter.md`, the
# brief and its screenshot at the run's root.
#
# The four `_shared` files are ones the skill reaches as `../_shared/…`; a run's read scope
# stops at the plugin directory and that symlink points out of it, so they are placed here.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
shared="$case_dir/../../skills/_shared"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1
for f in fidelity-ledger.md spec-splitting-seams.md ado-workitem-authoring.md final-prints.md; do
  cp "$shared/$f" "$PWD/$f" || exit 1
done

printf '/spec.md\n/fidelity-ledger.md\n/spec-splitting-seams.md\n/ado-workitem-authoring.md\n/final-prints.md\n/out/\n' > "$PWD/.gitignore" || exit 1
git -C "$PWD" init -q || exit 1
git -C "$PWD" config user.email "fixture@example.invalid" || exit 1
git -C "$PWD" config user.name "fixture" || exit 1
git -C "$PWD" add -A || exit 1
git -C "$PWD" commit -q -m "fixture: scaffold snapshot" || exit 1

set +x
echo "scaffold complete"
