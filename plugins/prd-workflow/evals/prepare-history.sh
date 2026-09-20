#!/usr/bin/env bash
#
# prepare-history.sh — place the frozen grill transcript in every eval case that
# replays it, for any plugin's suite.
#
# The transcript lives in the fixture repository, `LiamKlyneker/skills-fixture`, at
# `evals/grill-history.jsonl`. A case that replays it declares
# `context.history_file: ./grill-history.jsonl`, and the runner resolves that path
# **inside the case directory** and **before the scaffold script runs** — a path
# holding `..`, or an absolute path, is refused. So the copy has to be in the case
# directory already, and a scaffold script cannot put it there.
#
# The copies are gitignored. This script is the prep step that places them, and it is
# run once before a suite that carries such a case.
#
# A sibling checkout beside this repo is the fast source; a shallow clone is the
# fallback. Both place the fixture's tracked bytes at HEAD, extracted with
# `git archive`, so two machines get the same transcript.
#
# Usage:
#   prepare-history.sh [--suite <dir>] [--sibling <path>] [--repo-url <url>] [--dry-run]
#
#   --suite     an evals directory to prepare (default: every `plugins/*/evals`)
#   --sibling   local fixture checkout to prefer (default: <this repo>/../skills-fixture)
#   --repo-url  clone source when the sibling is absent
#   --dry-run   resolve and report the source and the destinations, place nothing
#
# Prints `source: sibling <path>` or `source: clone <url>`, then one line per case.
#
# Exit: 0 placed (or nothing to place) · 1 neither source usable · 2 usage error

set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
canonical="$(cd "$script_dir/../../.." && pwd -P)"

member="evals/grill-history.jsonl"
suite=""
sibling="$canonical/../skills-fixture"
repo_url="https://github.com/LiamKlyneker/skills-fixture.git"
dry_run=0

while [ $# -gt 0 ]; do
  case "$1" in
    --suite)    suite="${2:-}"; shift 2 ;;
    --sibling)  sibling="${2:-}"; shift 2 ;;
    --repo-url) repo_url="${2:-}"; shift 2 ;;
    --dry-run)  dry_run=1; shift ;;
    -h|--help)  sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)          echo "prepare-history.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

if [ -n "$suite" ]; then
  [ -d "$suite" ] || { echo "prepare-history.sh: no such suite directory '$suite'" >&2; exit 2; }
  suites=("$suite")
else
  suites=()
  for d in "$canonical"/plugins/*/evals; do
    [ -d "$d" ] && suites+=("$d")
  done
fi

# A case earns a copy by declaring `history_file`, and the name it declares is the name
# the copy takes — the runner reads that literal path, not this script's idea of one.
targets=()
for s in "${suites[@]}"; do
  for case_yaml in "$s"/*/case.yaml; do
    [ -f "$case_yaml" ] || continue
    declared="$(sed -n 's/^[[:space:]]*history_file:[[:space:]]*//p' "$case_yaml" | head -1 | tr -d '"'"'"' \r')"
    [ -n "$declared" ] || continue
    targets+=("$(dirname "$case_yaml")/${declared#./}")
  done
done

if [ "${#targets[@]}" -eq 0 ]; then
  echo "no case declares history_file — nothing to place"
  exit 0
fi

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
  for t in "${targets[@]}"; do echo "dry run: would place $t"; done
  exit 0
fi

clone_dir=""
cleanup() { [ -n "$clone_dir" ] && rm -rf "$clone_dir"; }
trap cleanup EXIT

if [ "$source_kind" = "clone" ]; then
  clone_dir="$(mktemp -d)" || exit 1
  if ! git clone --depth 1 --quiet "$repo_url" "$clone_dir/fixture"; then
    echo "prepare-history.sh: no sibling at $sibling and clone of $repo_url failed" >&2
    exit 1
  fi
  archive_from="$clone_dir/fixture"
else
  archive_from="$sibling"
fi

staging="$(mktemp -d)" || exit 1
trap 'cleanup; rm -rf "$staging"' EXIT

if ! git -C "$archive_from" archive HEAD "$member" | tar -x -C "$staging"; then
  echo "prepare-history.sh: could not extract $member from $archive_from" >&2
  exit 1
fi

for t in "${targets[@]}"; do
  mkdir -p "$(dirname "$t")" || exit 1
  cp "$staging/$member" "$t" || exit 1
  echo "placed: $t"
done
