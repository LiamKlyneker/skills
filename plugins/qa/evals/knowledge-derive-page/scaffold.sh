#!/usr/bin/env bash
#
# Place this case's stub project in the run's working directory: the shared shelves page with no
# knowledge file, on `main`. `../plant-knowledge.sh` has the layout it reads.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

bash "$case_dir/../plant-knowledge.sh" "$case_dir" shelves-page \
  'shelves: the shelves page' || exit 1

set +x
echo "scaffold complete"
