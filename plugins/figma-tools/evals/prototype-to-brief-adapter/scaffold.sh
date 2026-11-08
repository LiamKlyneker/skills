#!/usr/bin/env bash
#
# Place the fixture workspace and this case's ticket in the run's working directory, and
# swap the variant adapter in over the one a session reads.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the workspace and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

"$case_dir/../../../prd-workflow/evals/scaffold-fixture.sh" --dest "$PWD" || exit 1
cp "$case_dir/ticket.md" "$PWD/ticket.md" || exit 1

adapter_dir="$PWD/apps/consumer/.claude/project"
cp "$adapter_dir/adapter.variant.md" "$adapter_dir/adapter.md" || exit 1

set +x
echo "scaffold complete"
