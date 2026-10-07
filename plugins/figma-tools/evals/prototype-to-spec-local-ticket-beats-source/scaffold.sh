#!/usr/bin/env bash
#
# Place the hairline-token case's stub project and ticket in the run's working directory, then
# give its adapter a `Ticket source:` line naming a Jira site.
#
# The stub is borrowed rather than copied into this case: the ticket and the prototype are not
# what this case tests, and a second copy would drift from the first.
#
# The runner discards this script's exit status, so everything it does is logged to
# `scaffold.log` beside the stub and read back with `--keep-temp`.

set -uo pipefail

case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
stub_dir="$case_dir/../prototype-to-spec-hairline-token"
exec >"$PWD/scaffold.log" 2>&1
set -x

cp -R "$stub_dir/fixture/." "$PWD" || exit 1
cp "$stub_dir/ticket.md" "$PWD/ticket.md" || exit 1

adapter="$PWD/.claude/project/adapter.md"
grep -q '^- Tracker: `github`$' "$adapter" || exit 1
sed -i.bak '/^- Tracker: `github`$/a\
- Ticket source: `jira · site atelier-stub.atlassian.net`
' "$adapter" && rm "$adapter.bak" || exit 1
grep -q '^- Ticket source:' "$adapter" || exit 1

set +x
echo "scaffold complete"
