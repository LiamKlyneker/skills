#!/usr/bin/env bash
#
# Place this case's hand-written stub project and its ticket in the run's working directory.
#
# The stub is this case directory's own `fixture/`, not the shared fixture repository: a micro
# case's whole point is that it needs no pnpm workspace, no build and no captures, so there is
# nothing for `scaffold-fixture.sh` to place and nothing to wait for. `cp -R fixture/.` copies
# the dotfile tree too, which is what puts `.claude/project/adapter.md` at the run's root.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$case_dir/fixture/." "$PWD" || exit 1
cp "$case_dir/ticket.md" "$PWD/ticket.md" || exit 1

set +x
echo "scaffold complete"
