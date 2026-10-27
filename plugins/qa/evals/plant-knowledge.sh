#!/usr/bin/env bash
#
# plant-knowledge.sh — place one `build-knowledge` case's stub project in the run's working
# directory: the shared shelves page with the case's own files over it, planted by
# `plant-branch.sh`.
#
# Usage: plant-knowledge.sh [--with-backend] <case-dir> <branch> <subject>...
#
#   stub-shelves-page/     the page every case shares, copied first
#   <case-dir>/fixture/    copied over the shared page; this is where a case plants its own
#                          `KNOWLEDGE.md` or bait
#   <case-dir>/branch/     optional; becomes the branch's first-commit overlay, as in
#                          `plant-branch.sh`
#   --with-backend         also copies stub-shelves-api/ to `backends/shelves-api/`, a cloned
#                          backend repo kept out of the project's history through
#                          `.git/info/exclude`
#
# Exit: 0 placed · 1 a step failed · 2 usage error

set -uo pipefail

with_backend=0
if [ "${1:-}" = "--with-backend" ]; then
  with_backend=1
  shift
fi
[ $# -ge 3 ] || { echo "usage: plant-knowledge.sh [--with-backend] <case-dir> <branch> <subject>..." >&2; exit 2; }

evals_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
case_dir="$1"
shift

staged="$(mktemp -d)" || exit 1
trap 'rm -rf "$staged"' EXIT

mkdir -p "$staged/fixture" || exit 1
cp -R "$evals_dir/stub-shelves-page/." "$staged/fixture" || exit 1
if [ -d "$case_dir/fixture" ]; then
  cp -R "$case_dir/fixture/." "$staged/fixture" || exit 1
fi
if [ -d "$case_dir/branch" ]; then
  cp -R "$case_dir/branch" "$staged/branch" || exit 1
fi

bash "$evals_dir/plant-branch.sh" "$staged" "$@" || exit 1

if [ "$with_backend" -eq 1 ]; then
  mkdir -p "$PWD/backends/shelves-api" || exit 1
  cp -R "$evals_dir/stub-shelves-api/." "$PWD/backends/shelves-api" || exit 1
  exclude="$(git -C "$PWD" rev-parse --git-path info/exclude)" || exit 1
  case "$exclude" in /*) ;; *) exclude="$PWD/$exclude" ;; esac
  printf '/backends/\n' >> "$exclude" || exit 1
fi

[ -z "$(git -C "$PWD" status --short)" ] || { git -C "$PWD" status --short; exit 1; }
echo "planted the shelves page$([ "$with_backend" -eq 1 ] && echo ' with backends/shelves-api')"
