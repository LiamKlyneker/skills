#!/usr/bin/env bash
# Regenerate the catalog, serve the dashboard directory, and open it in the browser.
# Ctrl-C stops the server.

set -euo pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
port="${1:-8765}"

python3 "$dir/build.py"

# Open after the server has bound; a plain `open` before it would race the bind.
(sleep 1 && open "http://localhost:$port/") &
exec python3 -m http.server "$port" --directory "$dir"
