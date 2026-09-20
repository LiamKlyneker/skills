#!/usr/bin/env bash
#
# Place the fixture workspace, the frozen brief and the fidelity-ledger contract in the
# run's working directory — the same workaround `to-task-ledger-verbatim` uses under
# `plugins/prd-workflow/evals/`; see that case's scaffold.sh for the full rationale
# (the sandbox's read scope, and why the runner discards this script's exit status).
#
# deep-grill lives in plugins/lk, so it reaches the shared contract through
# plugins/lk/skills/_shared rather than prd-workflow's copy of the same packaging
# symlink; the fixture-workspace half of the workaround is shared across every
# plugin's suite, so this still calls prd-workflow's scaffold-fixture.sh.
#
# This case has no `context.history_file` to replay: deep-grill is the first
# interactive hop, grilled straight from the frozen brief rather than resuming a
# frozen transcript.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec >"$PWD/scaffold.log" 2>&1
set -x

"$case_dir/../../../prd-workflow/evals/scaffold-fixture.sh" --dest "$PWD" || exit 1
mkdir -p "$PWD/apps/consumer/capture" || exit 1
cp "$case_dir/../fixtures/brief.md" "$PWD/apps/consumer/capture/brief.md" || exit 1
cp "$case_dir/../../skills/_shared/fidelity-ledger.md" "$PWD/fidelity-ledger.md" || exit 1

set +x
echo "scaffold complete"
