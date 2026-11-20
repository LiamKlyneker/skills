# The recipe file

The format of a recipe: how to make one kind of item on the screens of an app, where it is made,
and where it is seen. A recipe is how `qa:prove-branch` makes the data a flow starts from. It is
written in user words only, and a recipe is saved only after a drive made the item.

This file is the only definition of the format. No skill restates a field list; each points here
(`../references/recipe-file.md`). No project edits the format. The items a run made from recipes
are listed in the made-items file, whose format is [`made-items-file.md`](made-items-file.md). The
write rules a drive keeps are in ADR
[0029](../../../../docs/adr/0029-test-data-is-made-on-demand-from-recipes.md) and ADR
[0028](../../../../docs/adr/0028-setup-states-may-create-data-under-write-rules.md).

## Where it lives

**One file per kind of item, in the project's QA folder.** The adapter's `## QA` row that names the
folder is the authority. The default, when the row gives no other path, is `.claude/project/qa/`,
beside the adapter. A file is named for the item in kebab case: `shelf.md`, `loan-with-late-fee.md`.

Each repo keeps its own copy of a recipe. No store outside the repo exists. A recipe file in a
sibling repo that sits beside this one may be read when learning a recipe, and is never written.

The skill adds the QA folder to `.git/info/exclude` when it first writes there.

## Shape

A header and one table of options, in this order. Nothing else: no notes section and no other
heading.

```markdown
# <item, in user words>

Made in: <app> · <the screens the steps use, in user words> · starts at <URL>
Seen in: <app> · <how the item is opened there, in user words>
Role: <the role that makes the item, by the label the adapter's credential row uses>
Needs: <other items that must exist first, by recipe name, or `none`>
Returns: <a link, or the ids the item is found by>
Failed: <YYYY-MM-DD> at step <k> — only after a drive of the recipe failed

## Shared steps

1. <step in the words on the screen>
2. <step>

## Options

| Option | Steps | Last proved |
|---|---|---|
```

### The header lines

| Line | Holds |
|---|---|
| `Made in` | the app where the item is made, the screens its steps use, and **the URL where the steps start**. The developer gives that URL once, when the recipe is learned. There is no org concept: the URL carries whatever the app needs to scope the data |
| `Seen in` | the app where a user meets the item, and how the item is opened there: a link, a list row, a menu entry. It may name the same app as `Made in` |
| `Role` | the role that makes the item, by the label the adapter's credential row uses |
| `Needs` | the recipes whose items must exist before this one is made, or `none`. A chain is made in `Needs` order and shown whole at the gate |
| `Returns` | what the drive reads off the screen when the item exists: a link to it, or the ids that find it |
| `Failed` | optional: the date a drive of the recipe failed and the step it failed at. The next run learns a recipe that carries this line again, and the line goes when a drive proves the recipe learned again |

When a branch's diff touches a page folder that is one of a recipe's `Made in` screens, the branch
changes how the item is made. `Made in` and `Seen in` are the connection between two apps, at the
level of the item.

### `## Shared steps`

The numbered steps every option starts with. Each step is one action in the words on the screen:
the label of a button, the title of a section, the text a field shows. **A step never holds a
selector, a test id, a component name or a code word.** A name a step types starts with `qa-setup`.

### `## Options`

`Option | Steps | Last proved`

One row per option of the item: a variant that a flow can start from, such as a shelf with a
waitlist. An option row holds the steps that follow the shared steps, and `Last proved`, the date
`YYYY-MM-DD` of the drive that last made the item with that option.

- **An option no drive proved is not in the file.** A learned option waits in the gate and is
  written after the drive makes the item.
- **A recipe has no expiry.** It stays valid until a drive fails. A recipe that fails in a run gets
  no second attempt in that run; the run writes its `Failed` line, and the next run learns it again.

## What a recipe may and may not do

- **A walk in the app's own screens is a recipe too.** One mechanism makes all start data: an item
  made in an admin app, and a state reached by a walk in the app under test.
- **A recipe may create a user through the app's own sign-up screen**, under the write rules, when
  sign-up needs no inbox step. When sign-up needs an inbox step, the state is Unable to verify.
- **No recipe runs a seeder, an end-to-end command, a database query or a writing API.** A recipe
  is only what a person does in the app's screens.
- A recipe never changes or removes an item it did not create in the run, and never enters payment
  details.
