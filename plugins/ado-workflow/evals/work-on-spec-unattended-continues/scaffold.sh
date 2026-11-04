#!/usr/bin/env bash
#
# Place this case's hand-written stub project in the run's working directory, as a git
# repository on the spec branch, one loop-start commit ahead of `main`.
#
# `tracker/` stands in for Azure DevOps: work items, tags, states, comments, worker reports and
# the pull-request body as local files. It is ignored, so the loop's own
# `git reset --hard && git clean -fd` on a failed `[TASK]` leaves it alone, and so are the two
# files the run writes for the graders.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1

printf '/tracker/\n/spawned.txt\n/exit-status\n/scaffold.log\n' > "$PWD/.gitignore" || exit 1
git -C "$PWD" init -q -b main || exit 1
git -C "$PWD" config user.email "fixture@example.invalid" || exit 1
git -C "$PWD" config user.name "fixture" || exit 1
git -C "$PWD" add -A || exit 1
git -C "$PWD" commit -q -m "fixture: scaffold snapshot" || exit 1
git -C "$PWD" checkout -q -b spec/40-shelf-count || exit 1
git -C "$PWD" commit -q --allow-empty -m "spec AB#40: loop start" || exit 1

set +x
echo "scaffold complete"
