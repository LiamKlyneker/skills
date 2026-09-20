# Dashboard

A local, static page listing this repo's plugins, skills, agents, eval cases, and every
eval run recorded under `plugins/*/evals/results/`.

## Run

```bash
dashboard/serve.sh
```

It regenerates `dashboard/catalog.json`, serves the directory on port 8765 and opens the
page in the browser. Pass a port as the first argument to change it. Ctrl-C stops the
server.

`catalog.json` is gitignored: run results can carry consumer material, so nothing derived
from them is committed. Serve over HTTP rather than opening the file directly; browsers
block the `catalog.json` fetch on a `file://` page.

## Facts only

The page renders values the eval runner or the source files wrote, and never derives a
verdict. A pass mark is the runner's own `passed` flag, shown beside the `threshold` the
run recorded. There are no trends, no health colours and no recomputed scores. A run with
`partial: true` is shown and flagged. A grader of type `llm` is marked as judgement, so it
is not read as hard evidence. Per-run detail is the run's own `report.html`, linked rather
than re-rendered.
