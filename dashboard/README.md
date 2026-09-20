# Dashboard

A local, static page listing this repo's plugins, skills, agents, eval cases, and every
eval run recorded under `plugins/*/evals/results/`.

## Regenerate

```bash
python3 dashboard/build.py
```

It writes `dashboard/catalog.json`, which is gitignored: run results can carry consumer
material, so nothing derived from them is committed.

## View

```bash
cd dashboard && python3 -m http.server 8765
```

Then open <http://localhost:8765/>. Serve it over HTTP rather than opening the file
directly; browsers block the `catalog.json` fetch on a `file://` page.

## Facts only

The page renders values the eval runner or the source files wrote, and never derives a
verdict. A pass mark is the runner's own `passed` flag, shown beside the `threshold` the
run recorded. There are no trends, no health colours and no recomputed scores. A run with
`partial: true` is shown and flagged. A grader of type `llm` is marked as judgement, so it
is not read as hard evidence. Per-run detail is the run's own `report.html`, linked rather
than re-rendered.
