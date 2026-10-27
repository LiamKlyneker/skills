#!/usr/bin/env bash
#
# Place this case's stub project in the run's working directory: `main` holds the fixture
# snapshot, and the branch under test carries the commits below. `../plant-branch.sh` has the
# layout it reads.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

bash "$case_dir/../plant-branch.sh" "$case_dir" shelf-archive \
  'shelves: archive toggle on the shelf row' \
  'shelves: hide archived shelves from the header total' || exit 1

set +x
echo "scaffold complete"
