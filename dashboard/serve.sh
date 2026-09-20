#!/usr/bin/env bash
# Regenerate the catalog, serve the repo root, and open the dashboard in the browser.
# Ctrl-C stops the server.
#
# The root is served, not this directory: report links point at
# ../plugins/<plugin>/evals/results/<ts>/report.html, which is unreachable from a
# server rooted here.

set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
root="$(cd "$dir/.." && pwd -P)"
port="${1:-8765}"

python3 "$dir/build.py"

# Open after the server has bound; a plain `open` before it would race the bind.
(sleep 1 && open "http://localhost:$port/dashboard/") &
exec python3 -m http.server "$port" --directory "$root"
