#!/usr/bin/env bash
#
# Place this case's stub project in the run's working directory: the shared shelves page with its
# prove-branch layer, this case's `accounts.md` and ticket, on a branch beside `main`.
# `../plant-prove.sh` has the layout it reads.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

bash "$case_dir/../plant-prove.sh" --no-knowledge "$case_dir" shelf-actions \
  'shelves: label shelf actions with the shelf name (#12)' \
  'shelves: reword the overdue loans banner (#12)' || exit 1

set +x
echo "scaffold complete"
