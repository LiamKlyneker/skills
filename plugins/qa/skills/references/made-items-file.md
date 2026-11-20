# The made-items file

The format of the one file that lists what the QA skills made on a target: which item, which
options it holds, where it is, which role sees it, when it was made, who made it, and whether it is
still usable. It is how a run uses an item again, and how the receipt lists what a run wrote.

This file is the only definition of the format. No skill restates a column list; each points here
(`../references/made-items-file.md`). No project edits the format. The recipes that make the items
are defined in [`recipe-file.md`](recipe-file.md).

## Where it lives

**One per project, in the project's QA folder**, named `made-items.md`. The adapter's `## QA` row
that names the folder is the authority; the default is `.claude/project/qa/`, beside the adapter.
The skill adds the folder to `.git/info/exclude` when it first writes there.

## Shape

```markdown
# Made items

| Item | Options | Link or ids | Role | Made | Origin | Status |
|---|---|---|---|---|---|---|
```

One row per item.

| Column | Holds |
|---|---|
| `Item` | the recipe name of the item, as the recipe file is named: `shelf` |
| `Options` | the options of the recipe the item was made with, or `none` |
| `Link or ids` | the link to the item, or the ids that find it, each named in user words. The item's `qa-setup` name is recorded with it; a row with origin `developer` has none |
| `Role` | the role that sees the item, by the label the adapter's credential row uses |
| `Made` | the date the row was written, `YYYY-MM-DD` |
| `Origin` | where the item came from, from the vocabulary below |
| `Status` | whether a run may use the item, from the vocabulary below |

**Origin vocabulary**, and only this:

| Origin | The item came from |
|---|---|
| `run <short sha>` | an arrange drive at that SHA, in a `prove-branch` run or in `qa:setup-env` |
| `developer` | a link a developer gave, at the gate or in `qa:setup-env` |

**Status vocabulary**, and only this:

| Status | Meaning |
|---|---|
| `fresh` | no flow has changed the item since it was made |
| `used <YYYY-MM-DD>` | a flow changed the item on that date |
| `gone <YYYY-MM-DD>` | a run looked for the item on that date and it no longer existed |

## Rules

- **A run uses only a `fresh` row whose item still exists.** It opens the link before the flow
  starts. An item that is missing is marked `gone` and the run goes on to the next source.
- **An item a flow changed is marked `used` and never used again.** The driver already marks each
  sub-step that changes data, so the rule needs no judgement.
- **No row is ever deleted.** A row that no run can use keeps its `used` or `gone` status.
- The receipt lists every row the run wrote.
