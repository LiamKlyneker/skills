#!/usr/bin/env bash
#
# plant-branch.sh — place one qa case's stub project in the run's working directory as a git
# repository with a default branch and the branch under test.
#
# Usage: plant-branch.sh <case-dir> <branch> <subject>...
#
#   <case-dir>/fixture/    copied to the working directory, dotfiles included, and committed on
#                          `main` as `fixture: scaffold snapshot`
#   <case-dir>/branch/     optional; copied over the tree in the branch's first commit, so the
#                          branch's diff against `main` is this overlay
#   <case-dir>/scenarios/  optional; copied to `.qa-scenarios/` after the commits, excluded
#                          through `.git/info/exclude` the way `prove-branch` excludes it
#   <subject>...           one commit on <branch> per subject, each appending its subject to
#                          CHANGES.md; this is where a case plants its commit-subject keys
#
# `.stand-in/` holds what `gh` and the Azure DevOps MCP would return for the branch. It is
# ignored, so the tree stays clean, and `__HEAD__` and `__BRANCH__` in its files become the
# branch's head commit and name once the commits exist.
#
# Commit dates and author are fixed, so a fixture plants the same commit ids on every machine.
#
# Exit: 0 placed · 1 a step failed · 2 usage error

set -uo pipefail

[ $# -ge 3 ] || { echo "usage: plant-branch.sh <case-dir> <branch> <subject>..." >&2; exit 2; }

case_dir="$1"
branch="$2"
shift 2
dest="$PWD"

export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE="2026-10-01T12:00:00Z" GIT_COMMITTER_DATE="2026-10-01T12:00:00Z"

cp -R "$case_dir/fixture/." "$dest" || exit 1
printf '/.stand-in/\n/scaffold.log\n' > "$dest/.gitignore" || exit 1

git -C "$dest" init -q -b main || exit 1
git -C "$dest" config user.email "$GIT_AUTHOR_EMAIL" || exit 1
git -C "$dest" config user.name "$GIT_AUTHOR_NAME" || exit 1
git -C "$dest" add -A || exit 1
git -C "$dest" commit -q -m "fixture: scaffold snapshot" || exit 1
git -C "$dest" checkout -q -b "$branch" || exit 1

first=1
for subject in "$@"; do
  if [ "$first" -eq 1 ] && [ -d "$case_dir/branch" ]; then
    cp -R "$case_dir/branch/." "$dest" || exit 1
  fi
  first=0
  printf '%s\n' "$subject" >> "$dest/CHANGES.md" || exit 1
  git -C "$dest" add -A || exit 1
  git -C "$dest" commit -q -m "$subject" || exit 1
done

head_sha="$(git -C "$dest" rev-parse HEAD)" || exit 1
if [ -d "$dest/.stand-in" ]; then
  find "$dest/.stand-in" -type f -exec \
    perl -pi -e "s/__HEAD__/$head_sha/g; s{__BRANCH__}{$branch}g" {} + || exit 1
fi

if [ -d "$case_dir/scenarios" ]; then
  exclude="$(git -C "$dest" rev-parse --git-path info/exclude)" || exit 1
  case "$exclude" in /*) ;; *) exclude="$dest/$exclude" ;; esac
  printf '/.qa-scenarios/\n' >> "$exclude" || exit 1
  ( umask 077 && mkdir -p "$dest/.qa-scenarios" && cp -R "$case_dir/scenarios/." "$dest/.qa-scenarios" ) || exit 1
fi

[ -z "$(git -C "$dest" status --short)" ] || { git -C "$dest" status --short; exit 1; }
echo "planted: $branch at $head_sha"
