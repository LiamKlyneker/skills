#!/usr/bin/env bash
#
# scaffold-fixture.sh — place the eval fixture workspace in an eval run's working
# directory, for any plugin's suite.
#
# The fixture is a separate repository, `LiamKlyneker/skills-fixture`: a pnpm
# workspace whose `apps/consumer` carries the adapter and the design-system catalog a
# case reads. A sibling checkout beside this repo is the fast source; a shallow clone
# is the fallback for a machine that has no sibling.
#
# Both sources place the same bytes: the fixture's tracked files at HEAD, extracted
# with `git archive`. Untracked dirt and build output in a sibling checkout therefore
# never reach a case, so two machines scaffold the same workspace.
#
# Usage:
#   scaffold-fixture.sh [--dest <dir>] [--sibling <path>] [--repo-url <url>] [--dry-run]
#
#   --dest      where the workspace lands (default: $PWD, the run's working directory)
#   --sibling   local fixture checkout to prefer (default: <this repo>/../skills-fixture)
#   --repo-url  clone source when the sibling is absent
#   --dry-run   resolve and report the source, place nothing
#
# Prints `source: sibling <path>` or `source: clone <url>`, so a failed case can be
# read back to the fixture it actually ran against.
#
# Exit: 0 placed · 1 neither source usable · 2 usage error

set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
canonical="$(cd "$script_dir/../../.." && pwd -P)"

dest="$PWD"
sibling="$canonical/../skills-fixture"
repo_url="https://github.com/LiamKlyneker/skills-fixture.git"
dry_run=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dest)     dest="${2:-}"; shift 2 ;;
    --sibling)  sibling="${2:-}"; shift 2 ;;
    --repo-url) repo_url="${2:-}"; shift 2 ;;
    --dry-run)  dry_run=1; shift ;;
    -h|--help)  sed -n '2,26p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)          echo "scaffold-fixture.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

[ -n "$dest" ] || { echo "scaffold-fixture.sh: --dest needs a path" >&2; exit 2; }

# A sibling counts only when it is a git repository; a directory of loose files has no
# HEAD to archive, and copying it instead would reintroduce the machine-dependent
# scaffold this script exists to avoid.
if [ -d "$sibling" ] && git -C "$sibling" rev-parse --git-dir >/dev/null 2>&1; then
  sibling="$(cd "$sibling" && pwd -P)"
  source_kind="sibling"
  source_label="$sibling"
else
  source_kind="clone"
  source_label="$repo_url"
fi

echo "source: $source_kind $source_label"

if [ "$dry_run" -eq 1 ]; then
  echo "dry run: nothing placed"
  exit 0
fi

mkdir -p "$dest" || exit 1
dest="$(cd "$dest" && pwd -P)"

clone_dir=""
cleanup() { [ -n "$clone_dir" ] && rm -rf "$clone_dir"; }
trap cleanup EXIT

if [ "$source_kind" = "clone" ]; then
  clone_dir="$(mktemp -d)" || exit 1
  if ! git clone --depth 1 --quiet "$repo_url" "$clone_dir/fixture"; then
    echo "scaffold-fixture.sh: no sibling at $sibling and clone of $repo_url failed" >&2
    exit 1
  fi
  archive_from="$clone_dir/fixture"
else
  archive_from="$sibling"
fi

if ! git -C "$archive_from" archive HEAD | tar -x -C "$dest"; then
  echo "scaffold-fixture.sh: could not extract $archive_from into $dest" >&2
  exit 1
fi

echo "placed: $dest/apps/consumer"
