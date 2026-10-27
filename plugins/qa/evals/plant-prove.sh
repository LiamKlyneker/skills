#!/usr/bin/env bash
#
# plant-prove.sh — place one `prove-branch` knowledge case's stub project in the run's working
# directory: the shared shelves page, its knowledge file, the prove-branch layer and the case's own
# files, planted by `plant-branch.sh`.
#
# Usage: plant-prove.sh [--no-knowledge] <case-dir> <branch> <subject>...
#
#   stub-shelves-page/              the page every qa stub shares, copied first
#   stub-shelves-states/fixture/    the page's `KNOWLEDGE.md`, copied over the page
#   stub-shelves-states/scenarios/  the owner's saved session, planted as `.qa-scenarios/`
#   stub-shelves-prove/fixture/     the adapter with a `## QA` → Known accounts row, and the
#                                   `.stand-in/` files every case shares
#   stub-shelves-prove/branch/      the branch's overlay: a change under `app/shelves/`
#   <case-dir>/fixture/             copied last; a case plants its `accounts.md` and its
#                                   `.stand-in/tickets.json` here
#   --no-knowledge                  removes `app/shelves/KNOWLEDGE.md` before planting
#
# Exit: 0 placed · 1 a step failed · 2 usage error

set -uo pipefail

no_knowledge=0
if [ "${1:-}" = "--no-knowledge" ]; then
  no_knowledge=1
  shift
fi
[ $# -ge 3 ] || { echo "usage: plant-prove.sh [--no-knowledge] <case-dir> <branch> <subject>..." >&2; exit 2; }

evals_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
case_dir="$1"
shift

staged="$(mktemp -d)" || exit 1
trap 'rm -rf "$staged"' EXIT

mkdir -p "$staged/fixture" "$staged/scenarios" "$staged/branch" || exit 1
cp -R "$evals_dir/stub-shelves-page/." "$staged/fixture" || exit 1
cp -R "$evals_dir/stub-shelves-states/fixture/." "$staged/fixture" || exit 1
cp -R "$evals_dir/stub-shelves-states/scenarios/." "$staged/scenarios" || exit 1
cp -R "$evals_dir/stub-shelves-prove/fixture/." "$staged/fixture" || exit 1
cp -R "$evals_dir/stub-shelves-prove/branch/." "$staged/branch" || exit 1
if [ -d "$case_dir/fixture" ]; then
  cp -R "$case_dir/fixture/." "$staged/fixture" || exit 1
fi
if [ "$no_knowledge" -eq 1 ]; then
  rm -f "$staged/fixture/app/shelves/KNOWLEDGE.md" || exit 1
fi

bash "$evals_dir/plant-branch.sh" "$staged" "$@" || exit 1
echo "planted the shelves page with its prove-branch layer$([ "$no_knowledge" -eq 1 ] && echo ', without KNOWLEDGE.md')"
