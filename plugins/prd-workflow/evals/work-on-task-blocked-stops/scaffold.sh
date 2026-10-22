#!/usr/bin/env bash
#
# Place this case's hand-written stub project in the run's working directory, as a git
# repository with one fixture commit.
#
# `cp -R fixture/.` copies the dotfile tree too, which is what puts
# `.claude/project/adapter.md` at the run's root. `/issue.md` is an evaluation input, not
# project source, so it is ignored and stays out of the fixture commit.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1

printf '/issue.md\n/scaffold.log\n' > "$PWD/.gitignore" || exit 1
git -C "$PWD" init -q || exit 1
git -C "$PWD" config user.email "fixture@example.invalid" || exit 1
git -C "$PWD" config user.name "fixture" || exit 1
git -C "$PWD" add -A || exit 1
git -C "$PWD" commit -q -m "fixture: scaffold snapshot" || exit 1

set +x
echo "scaffold complete"
