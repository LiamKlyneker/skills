# Dashboard

A local, static page listing this repo's plugins and skills, which skills have eval
cases in each tier (`micro`, `full`), and every eval run recorded under
`plugins/*/evals/results/`.

## Run

```bash
dashboard/serve.sh
```

It regenerates `dashboard/catalog.json`, serves the repo root on port 8765 and opens the
page in the browser. Pass a port as the first argument to change it. Ctrl-C stops the
server.

`catalog.json` is gitignored: run results can carry consumer material, so nothing derived
from them is committed. Serve over HTTP rather than opening the file directly; browsers
block the `catalog.json` fetch on a `file://` page.

## What it reads from a case

- **Skill:** the longest skill name the case name starts with (`<skill>-<behaviour>`),
  falling back to a tag that names a skill. A case matching neither is listed under
  "(no matching skill)".
- **Tier:** the `micro` or `full` tag. A case with neither is shown under "no tier tag".
- **Title:** the case's `summary:` line, falling back to its name.

## Facts only

The page renders values the eval runner or the source files wrote, and never derives a
verdict. A case's verdict is the runner's own `passed` flag. The runner records that flag
per attempt, so a run with several attempts has no case-level verdict and shows "no
verdict" beside its attempt count. A skill row's `2/3` counts the cases in that tier whose
latest run the runner marked passed. There are no trends, no health colours and no
recomputed scores. A run with `partial: true` is shown and flagged. Attempts from the
runner's `without` arm are the no-plugin baseline and are left out of the counts.

A grader of type `llm` is marked in purple as model judgement, so it is not read as hard
evidence. A `sidecar.json` beside a run's `aggregate-result.json` is shown in its own box
on that case as Jev's measurement: claim counts per bucket and the added and contradicted
claims. The page never merges those numbers into the runner's score or `passed` flag.
Per-run detail is the run's own `report.html`, linked rather than re-rendered.
