# The `accounts.md` file

The format of a project's observed layer: which staging org the QA pass uses, and which page states
are known to exist there, each with the ids that prove it and the date it was last verified. It is
never derived from code, and it only grows.

This file is the only definition of the format. No skill restates a column list; each points here
(`../references/accounts-file.md`). No project edits the format. The page states it cites are
defined per page in that page's `KNOWLEDGE.md`, whose format is
[`knowledge-file.md`](knowledge-file.md).

## Where it lives

**One per project, in the project's Claude configuration directory beside the adapter**:
`<repo-root>/.claude/project/accounts.md`. The adapter's `## QA` section carries a row pointing at
it.

## Writers

**Three writers, and no others:**

| Skill | Writes |
|---|---|
| `qa:setup` | the empty skeleton below, when no `accounts.md` exists, and the adapter's pointer row. It never deletes from either |
| `qa:setup-states` | every observed row: the first `## Orgs` row, asked for once when the table holds no org for the environment, and each `## States` row it verifies on the target, with its re-verifications and stale marks |
| `qa:prove-branch` | a `## States` row **only** when the developer answers a gap during a run — an instance the developer names after a stop. It never writes a row from what it observes on its own |

**`qa:build-knowledge` never touches it.** That skill reads code and never looks at staging, so it
has nothing to write here.

## Shape

### The empty skeleton

`qa:setup` copies this verbatim:

```markdown
# Accounts

## Orgs

| Env | Org | Role | Session method | Added |
|---|---|---|---|---|

## States

| Env | Org | Page | State | Ids | Last verified | Origin |
|---|---|---|---|---|---|---|
```

### `## Orgs`

`Env | Org | Role | Session method | Added`

One row per org the pass uses on an environment.

| Column | Holds |
|---|---|
| `Env` | `staging` or `prod` |
| `Org` | the org's id on that environment |
| `Role` | the role the pass signs in as, by the label the adapter's *Credential environment variables* row uses |
| `Session method` | the adapter's *Session method* value, `api` or `manual` |
| `Added` | the date the row was written, `YYYY-MM-DD` |

### `## States`

`Env | Org | Page | State | Ids | Last verified | Origin`

One row per known instance of a page state.

| Column | Holds |
|---|---|
| `Env` | `staging` or `prod` |
| `Org` | the org id, matching an `## Orgs` row for the same `Env` |
| `Page` | the page's route, as its `KNOWLEDGE.md` `Route:` line writes it |
| `State` | the state id from that page's `KNOWLEDGE.md` (`S21`) |
| `Ids` | the ids that prove the state is there — an order number, a plan id — each named in user words: `order 4412 · plan 98` |
| `Last verified` | the date the state was last seen on the target, `YYYY-MM-DD`, or the stale mark below |
| `Origin` | where the row came from, from the vocabulary below |

**Origin vocabulary**, and only this:

| Origin | The row came from |
|---|---|
| `observed in run <short sha>` | an instance a `prove-branch` run at that SHA saw on the target |
| `setup-states <YYYY-MM-DD>` | `setup-states` found or verified the state on the target that day |
| `developer, <YYYY-MM-DD>` | a developer named the instance, that day |

## Only grows

Rows are never deleted. A rerun of `setup-states` re-verifies every row it is scoped to:

- **still visible** — `Last verified` takes today's date;
- **no longer visible** — the row stays and `Last verified` reads `stale <YYYY-MM-DD>`, the date of
  the rerun that could not see it.

**A stale row resolves no flow**: a reader treats it as no row for that state. A later
re-verification that sees the state again writes a plain date back. Staging data moves under the
file; the stale mark is what keeps a moved row from being trusted.

## `Env`

The `Env` column prepares for prod rows, which no skill writes yet. A future prod row permits
**read-only** flows only: no flow that starts from a prod row may create, change or delete data.
