#!/usr/bin/env bash
#
# Place the fixture workspace, plus the frozen brief chain that carries one planted leak, in the
# run's working directory — the same workaround `to-task-ledger-verbatim` uses under
# `plugins/prd-workflow/evals/`; see that case's scaffold.sh for the full rationale (the sandbox's
# read scope, and why the runner discards this script's exit status).
#
# report-leak lives in plugins/lk, alongside deep-grill, so this reaches the fixture workspace
# through prd-workflow's shared scaffold-fixture.sh the same way deep-grill-row-coverage does.
#
# The leak is planted at the issue hop only: the brief and the grill decision both keep the
# search band's magnifier at 16px in `--color-ink-muted`; the frozen `to-task --out` issue
# invents 20px in `--color-accent` for the same row. Nothing plants a leak at the brief or grill
# hop, and there is no branch diff yet — `work-on-task` never ran against this ticket.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

"$case_dir/../../../prd-workflow/evals/scaffold-fixture.sh" --dest "$PWD" || exit 1

mkdir -p "$PWD/apps/consumer/.claude/briefs/VTR-4471" || exit 1
cp "$case_dir/../fixtures/brief.md" "$PWD/apps/consumer/.claude/briefs/VTR-4471.md" || exit 1
cp "$case_dir/../fixtures/leak-case-grill.md" \
  "$PWD/apps/consumer/.claude/briefs/VTR-4471/grill.md" || exit 1

mkdir -p "$PWD/apps/consumer/capture" || exit 1
cp "$case_dir/../fixtures/leak-case-issue.md" \
  "$PWD/apps/consumer/capture/issue-VTR-4471.md" || exit 1

set +x
echo "scaffold complete"
