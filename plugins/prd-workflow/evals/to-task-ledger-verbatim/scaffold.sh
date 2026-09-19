#!/usr/bin/env bash
#
# Place the fixture workspace, the frozen brief and the fidelity-ledger contract in the
# run's working directory.
#
# The brief lands where the grill this case replays read it from — `capture/brief.md`
# under the consumer app — so the paths in the replayed conversation and the path the
# prompt passes name the same file.
#
# `fidelity-ledger.md` is the contract `to-task` reaches for as `../_shared/…`. A run's
# read scope covers its working directory and the plugin under test, and the plugin
# reaches that file through the packaging symlink `skills/_shared`, which points out of
# the plugin — so the run cannot follow it and the skill stops on a missing contract.
# This places the same bytes, through the same symlink, somewhere the run can read; the
# prompt is what points the run at the copy.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the workspace and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

"$case_dir/../scaffold-fixture.sh" --dest "$PWD" || exit 1
mkdir -p "$PWD/apps/consumer/capture" || exit 1
cp "$case_dir/../fixtures/brief.md" "$PWD/apps/consumer/capture/brief.md" || exit 1
cp "$case_dir/../../skills/_shared/fidelity-ledger.md" "$PWD/fidelity-ledger.md" || exit 1

set +x
echo "scaffold complete"
