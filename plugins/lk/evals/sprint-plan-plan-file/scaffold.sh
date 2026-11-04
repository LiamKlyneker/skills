#!/usr/bin/env bash
#
# Place this case's projects directory in the run's working directory: two child repos,
# each a git repository with one fixture commit, and two sprint files beside them. The
# root itself stays out of git, as a projects directory is.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1

for repo in atelier-web atelier-api; do
  git -C "$PWD/$repo" init -q || exit 1
  git -C "$PWD/$repo" config user.email "fixture@example.invalid" || exit 1
  git -C "$PWD/$repo" config user.name "fixture" || exit 1
  git -C "$PWD/$repo" add -A || exit 1
  git -C "$PWD/$repo" commit -q -m "fixture: scaffold snapshot" || exit 1
done

set +x
echo "scaffold complete"
